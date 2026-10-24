#include "MotionTrackController.h"

#include "AppController.h"
#include "core/MotionTrack.h"
#include "engine/ClipReaderPool.h"
#include "engine/FaceTrack.h"
#include "engine/ObjectDetector.h"
#include "engine/RegionTracker.h"
#include "engine/StillImage.h"

#include <QCoreApplication>
#include <QMetaObject>
#include <QUuid>
#include <QtConcurrent>

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <functional>

namespace {

constexpr quint64 kMotionTrackStreamId = 0xA5'11'5C'A4'00'00'00'0Bull;
// Frames are decoded no bigger than this: the tracker works on a small grey copy anyway.
constexpr int kDecodeSide = 960;

using Sample = drift::MotionTrackSample;

double valueAt(const drift::KeyframeTrack<double> &track, drift::TimeUs relative, double fallback)
{
    return track.isEmpty() ? fallback : track.evaluateAt(relative);
}

// Where a clip sits on the canvas at a timeline time, in project pixels (the same defaults the
// compositor's layoutRectForClip uses: no keys means the whole canvas).
QRectF canvasRect(const drift::Clip &clip, drift::TimeUs timelineUs, int projectW, int projectH)
{
    const drift::TimeUs relative = timelineUs - clip.timelineStart;
    return QRectF(valueAt(clip.transformX, relative, 0.0), valueAt(clip.transformY, relative, 0.0),
                  valueAt(clip.transformW, relative, double(projectW)),
                  valueAt(clip.transformH, relative, double(projectH)));
}

QRectF normalizedToCanvas(const QRectF &n, const QRectF &video)
{
    return QRectF(video.x() + n.x() * video.width(), video.y() + n.y() * video.height(), n.width() * video.width(),
                  n.height() * video.height());
}

bool followsVideo(drift::ClipType type)
{
    return type == drift::ClipType::Video || type == drift::ClipType::Image;
}

bool canBeTracked(drift::ClipType type)
{
    switch (type) {
    case drift::ClipType::Text:
    case drift::ClipType::Image:
    case drift::ClipType::Video:
    case drift::ClipType::Shape:
    case drift::ClipType::Vector:
    case drift::ClipType::Composite:
        return true;
    default:
        return false;
    }
}

bool isText(const drift::Clip &clip)
{
    return clip.type == drift::ClipType::Text || clip.type == drift::ClipType::Subtitle;
}

// A scanned face as a rect normalized to the frame. The oval's half-axes are in width-normalized
// units (see applyFaceUniforms), so the height comes back to uv through the frame's aspect.
QRectF faceRect(const drift::FaceAnchors &face, double aspect)
{
    const double rx = qMax(0.01, face.faceRx);
    const double ry = qMax(0.01, face.faceRy > 0.0 ? face.faceRy : face.faceRx) * aspect;
    return QRectF(face.faceCenter.x() - rx, face.faceCenter.y() - ry, 2 * rx, 2 * ry);
}

QList<QRectF> faceRects(const QList<drift::FaceAnchors> &faces, double aspect)
{
    QList<QRectF> rects;
    for (const drift::FaceAnchors &f : faces)
        rects.append(f.valid ? faceRect(f, aspect) : QRectF());
    return rects;
}

// The face nearest a point (normalized), or -1.
int nearestFace(const QList<QRectF> &faces, const QPointF &point)
{
    int best = -1;
    double bestDistance = 0.0;
    for (int i = 0; i < faces.size(); ++i) {
        if (faces.at(i).isNull())
            continue;
        const QPointF d = faces.at(i).center() - point;
        const double distance = std::hypot(d.x(), d.y());
        if (best < 0 || distance < bestDistance) {
            best = i;
            bestDistance = distance;
        }
    }
    return best;
}

// Before a re-bake: the old path may lie outside the new stretch once the video moved, so the
// keys the last bake wrote are removed rather than left to mix in. Only those: keys the user set
// outside the tracked stretch stay (auditoria D12). A track from before 0.22.1 does not know its
// stretch, so it clears the whole animation as it always did, and returns how many keys that
// removed so the caller can say so (Undo brings them back).
int resetTrackedKeys(drift::Clip &clip)
{
    const bool scale = clip.motionTrack && clip.motionTrack->followScale;
    QList<drift::KeyframeTrack<double> *> tracks{&clip.transformX, &clip.transformY};
    if (scale) {
        tracks << &clip.transformW << &clip.transformH;
        if (clip.textStyle.keyframes.contains(QStringLiteral("pixelSize")))
            tracks << &clip.textStyle.keyframes[QStringLiteral("pixelSize")];
    }
    const drift::TimeUs from = clip.motionTrack ? clip.motionTrack->bakedFromUs : -1;
    const drift::TimeUs to = clip.motionTrack ? clip.motionTrack->bakedToUs : -1;
    int removed = 0;
    for (drift::KeyframeTrack<double> *keys : tracks) {
        for (const drift::TimeUs time : keys->keyframes().keys()) {
            if (from >= 0 && (time < from || time > to))
                continue;
            keys->removeKeyframe(time);
            ++removed;
        }
    }
    return from < 0 ? removed : 0;
}

// The bake's stretch, kept so the next re-bake knows which keys are the tracker's.
void rememberBake(drift::Clip &clip, const drift::MotionBakeResult &baked)
{
    if (clip.motionTrack && baked.ok) {
        clip.motionTrack->bakedFromUs = baked.fromUs;
        clip.motionTrack->bakedToUs = baked.toUs;
    }
}

// The detector's objects of `classId` in a frame, as rects normalized to it.
QList<QRectF> detectedOfClass(const QImage &frame, int classId)
{
    QList<QRectF> out;
    if (frame.isNull() || frame.width() <= 0 || frame.height() <= 0)
        return out;
    for (const drift::Detection &d : drift::ObjectDetector::instance().detect(frame)) {
        if (d.classId == classId)
            out.append(QRectF(d.box.x() / frame.width(), d.box.y() / frame.height(), d.box.width() / frame.width(),
                              d.box.height() / frame.height()));
    }
    return out;
}

// After the tracker lost the subject: the detected object of the same kind that is most likely it,
// near where it was lost (the radius grows the longer it has been gone) and about its size. Null
// when none qualifies, so a lost subject stays lost rather than taking another one's place.
QRectF reacquire(const QList<QRectF> &candidates, const QRectF &last, int lostFrames)
{
    QRectF best;
    double bestDistance = 0.0;
    const double reach = qMax(last.width(), last.height()) * (1.5 + 0.25 * lostFrames);
    for (const QRectF &c : candidates) {
        const double ratio = c.width() * c.height() / qMax(1e-9, last.width() * last.height());
        if (ratio < 0.4 || ratio > 2.5)
            continue;
        const QPointF d = c.center() - last.center();
        const double distance = std::hypot(d.x(), d.y());
        if (distance > reach)
            continue;
        if (best.isNull() || distance < bestDistance) {
            best = c;
            bestDistance = distance;
        }
    }
    return best;
}

// The object tracker over a video, outward from `t0` in each direction (`forward` starts with t0
// itself): its samples, or an error. Runs off the GUI thread; shared by an element that follows,
// Hide an object and a mask that follows. `stepDone` is called once per sample.
struct ObjectRun
{
    QList<Sample> samples;
    QString error;
};

ObjectRun runObjectTracking(const drift::Clip &video, const QRectF &region, drift::TimeUs t0,
                            const QList<drift::TimeUs> &forward, const QList<drift::TimeUs> &backward,
                            bool followScale, int classId, const QAtomicInt &cancel,
                            const std::function<void()> &stepDone)
{
    ObjectRun run;
    const bool still = video.type == drift::ClipType::Image;
    // A picked object of a known class is looked for again by the detector once lost.
    const bool redetect = classId >= 0 && drift::ObjectDetector::instance().available();
    const auto frameAt = [&](drift::TimeUs timelineUs) {
        return still ? drift::decodeStillImage(video.path, kDecodeSide, kDecodeSide)
                     : ClipReaderPool::instance().readVideoFrame(video.path, kMotionTrackStreamId,
                                                                 video.timelineToSourceUs(timelineUs), kDecodeSide,
                                                                 kDecodeSide, video.rotationCorrection);
    };
    const auto tr = [](const char *text) { return QCoreApplication::translate("MotionTrackController", text); };
    // Forward from the playhead, then backward from it again, each with its own tracker.
    for (int pass = 0; pass < 2; ++pass) {
        const QList<drift::TimeUs> &times = pass == 0 ? forward : backward;
        if (times.isEmpty())
            continue;
        drift::RegionTracker tracker;
        if (!tracker.start(frameAt(t0), region)) {
            run.error = tr("Could not read the video at the playhead");
            return run;
        }
        QRectF lastTrusted = region;
        int lostRun = 0;
        for (const drift::TimeUs t : times) {
            if (cancel.loadRelaxed() != 0) {
                run.error = tr("Tracking cancelled");
                return run;
            }
            Sample s;
            s.sourceUs = video.timelineToSourceUs(t);
            if (pass == 0 && t == t0) {
                s.rect = region;
                s.score = 1.0;
            } else {
                const QImage frame = frameAt(t);
                if (frame.isNull()) {
                    run.error = tr("Could not decode the video");
                    return run;
                }
                const drift::RegionTracker::Result r = tracker.step(frame, followScale);
                s.rect = r.rect;
                s.score = qBound(0.0, r.score, 1.0);
                s.state = r.lost ? Sample::State::Lost
                                 : (r.recovered ? Sample::State::Recovered : Sample::State::Tracked);
                if (r.lost) {
                    ++lostRun;
                    // The detector costs tens of milliseconds: on the first lost frame, then every
                    // fifth, which still picks the subject up within a fraction of a second.
                    if (redetect && lostRun % 5 == 1) {
                        const QRectF again = reacquire(detectedOfClass(frame, classId), lastTrusted, lostRun);
                        if (!again.isNull() && tracker.start(frame, again)) {
                            s.rect = again;
                            s.score = drift::RegionTracker::kRecoverScore;
                            s.state = Sample::State::Recovered;
                        }
                    }
                }
                if (s.state != Sample::State::Lost) {
                    lostRun = 0;
                    lastTrusted = s.rect;
                }
            }
            run.samples.append(s);
            stepDone();
        }
    }
    std::sort(run.samples.begin(), run.samples.end(),
              [](const Sample &a, const Sample &b) { return a.sourceUs < b.sourceUs; });
    return run;
}

// The timeline times a clip is followed over, outward from `t0`: forward starts with t0 itself.
void stepsAround(drift::TimeUs t0, drift::TimeUs start, drift::TimeUs end, drift::TimeUs step,
                 QList<drift::TimeUs> *forward, QList<drift::TimeUs> *backward)
{
    forward->clear();
    backward->clear();
    for (drift::TimeUs t = t0; t < end; t += step)
        forward->append(t);
    for (drift::TimeUs t = t0 - step; t >= start; t -= step)
        backward->append(t);
}

QString stateName(Sample::State state)
{
    switch (state) {
    case Sample::State::Lost:
        return QStringLiteral("lost");
    case Sample::State::Recovered:
        return QStringLiteral("recovered");
    default:
        return QStringLiteral("tracked");
    }
}

} // namespace

MotionTrackController::MotionTrackController(AppController *app, QObject *parent)
    : QObject(parent)
    , m_app(app)
{
    // A face track asked for on the way to following a face: carry on once the scan lands.
    connect(m_app->faces(), &FaceTrackingController::finished, this, [this](bool ok, const QString &) {
        if (!m_pendingBlur.isEmpty()) {
            const QVariantMap blur = m_pendingBlur;
            m_pendingBlur.clear();
            const QString clipId = blur.value(QStringLiteral("clipId")).toString();
            const QList<drift::Track> &tracks = m_app->m_project.tracks();
            for (int t = 0; ok && t < tracks.size(); ++t) {
                for (int c = 0; c < tracks.at(t).clips.size(); ++c) {
                    if (tracks.at(t).clips.at(c).id == clipId) {
                        blurFace(t, c, blur.value(QStringLiteral("style")).toString(),
                                 blur.value(QStringLiteral("faceSlot")).toInt());
                        return;
                    }
                }
            }
        }
        if (m_pendingFaceClipId.isEmpty())
            return;
        const QString overlayId = m_pendingFaceClipId;
        const QVariantMap options = m_pendingOptions;
        m_pendingFaceClipId.clear();
        if (!ok)
            return;
        const QList<drift::Track> &tracks = m_app->m_project.tracks();
        for (int t = 0; t < tracks.size(); ++t) {
            for (int c = 0; c < tracks.at(t).clips.size(); ++c) {
                if (tracks.at(t).clips.at(c).id == overlayId) {
                    trackWith(t, c, options);
                    return;
                }
            }
        }
    });
}

void MotionTrackController::setBusy(bool busy)
{
    if (m_busy == busy)
        return;
    m_busy = busy;
    emit busyChanged();
}

void MotionTrackController::bump()
{
    ++m_revision;
    emit revisionChanged();
}

// The topmost picture under the element at this time: tracks below it in the stack (track 0 is
// on top), skipping hidden, audio and adjustment tracks.
MotionTrackController::Source MotionTrackController::sourceUnder(int trackIndex, int clipIndex,
                                                                 drift::TimeUs atUs) const
{
    Source source;
    const QList<drift::Track> &tracks = m_app->m_project.tracks();
    for (int t = trackIndex + 1; t < tracks.size(); ++t) {
        const drift::Track &track = tracks.at(t);
        if (track.hidden || track.type == drift::TrackType::Audio || track.isAdjustment())
            continue;
        for (int c = 0; c < track.clips.size(); ++c) {
            const drift::Clip &clip = track.clips.at(c);
            if (followsVideo(clip.type) && clip.containsTime(atUs) && !clip.path.isEmpty()) {
                source.trackIndex = t;
                source.clipIndex = c;
                return source;
            }
        }
    }
    Q_UNUSED(clipIndex)
    return source;
}

MotionTrackController::Source MotionTrackController::pickSource(int trackIndex, int clipIndex,
                                                                drift::TimeUs atUs) const
{
    if (m_chooser.startsWith(QLatin1String("hide-")) && m_app->isValidClipIndex(trackIndex, clipIndex)) {
        const drift::Clip &clip = m_app->m_project.tracks().at(trackIndex).clips.at(clipIndex);
        if (followsVideo(clip.type) && !clip.path.isEmpty()) {
            Source self;
            self.trackIndex = trackIndex;
            self.clipIndex = clipIndex;
            return self;
        }
    }
    return sourceUnder(trackIndex, clipIndex, atUs);
}

const drift::Clip *MotionTrackController::followedVideo(const drift::Clip &follower, int trackIndex,
                                                        int clipIndex) const
{
    const QList<drift::Track> &tracks = m_app->m_project.tracks();
    if (follower.motionTrack && !follower.motionTrack->sourceClipId.isEmpty()) {
        for (const drift::Track &track : tracks) {
            for (const drift::Clip &clip : track.clips) {
                if (clip.id == follower.motionTrack->sourceClipId)
                    return &clip;
            }
        }
    }
    drift::TimeUs at = m_app->playheadUs();
    if (!follower.containsTime(at))
        at = follower.timelineStart;
    const Source source = sourceUnder(trackIndex, clipIndex, at);
    return source.trackIndex < 0 ? nullptr : &tracks.at(source.trackIndex).clips.at(source.clipIndex);
}

QVariantMap MotionTrackController::sourceFor(int trackIndex, int clipIndex) const
{
    QVariantMap out{{QStringLiteral("ok"), false}};
    if (!m_app->isValidClipIndex(trackIndex, clipIndex))
        return out;
    const drift::Clip &clip = m_app->m_project.tracks().at(trackIndex).clips.at(clipIndex);
    if (!canBeTracked(clip.type)) {
        out.insert(QStringLiteral("reason"), tr("This clip cannot follow anything"));
        return out;
    }
    // A text scales its letters with the target (its font size is keyed alongside the box).
    out.insert(QStringLiteral("canScale"), true);
    drift::TimeUs at = m_app->playheadUs();
    if (!clip.containsTime(at))
        at = clip.timelineStart;
    const Source source = sourceUnder(trackIndex, clipIndex, at);
    if (source.trackIndex < 0) {
        out.insert(QStringLiteral("reason"), tr("Put it over a video to follow something in it"));
        return out;
    }
    const drift::Clip &video = m_app->m_project.tracks().at(source.trackIndex).clips.at(source.clipIndex);
    out.insert(QStringLiteral("ok"), true);
    out.insert(QStringLiteral("source"), video.name);
    out.insert(QStringLiteral("hasFaces"), !video.faceTrackPath.isEmpty());
    return out;
}

QVariantMap MotionTrackController::info(int trackIndex, int clipIndex) const
{
    QVariantMap out{{QStringLiteral("has"), false}};
    if (!m_app->isValidClipIndex(trackIndex, clipIndex))
        return out;
    const drift::Clip &clip = m_app->m_project.tracks().at(trackIndex).clips.at(clipIndex);
    if (!clip.motionTrack || clip.motionTrack->isEmpty())
        return out;
    const drift::MotionTrack &mt = *clip.motionTrack;
    const drift::Clip *video = followedVideo(clip, trackIndex, clipIndex);
    out.insert(QStringLiteral("has"), true);
    out.insert(QStringLiteral("mode"), mt.mode);
    out.insert(QStringLiteral("faceSlot"), mt.faceSlot);
    out.insert(QStringLiteral("followScale"), mt.followScale);
    out.insert(QStringLiteral("keepDistance"), mt.keepDistance);
    out.insert(QStringLiteral("direction"), mt.direction);
    out.insert(QStringLiteral("samples"), int(mt.samples.size()));
    out.insert(QStringLiteral("lost"), mt.lostCount());
    out.insert(QStringLiteral("sourceMissing"), !video || video->id != mt.sourceClipId);
    out.insert(QStringLiteral("sourceChanged"), video && video->id == mt.sourceClipId && video->path != mt.sourcePath);
    return out;
}

QVariantList MotionTrackController::faceTargets(int trackIndex, int clipIndex) const
{
    QVariantList out;
    if (!m_app->isValidClipIndex(trackIndex, clipIndex))
        return out;
    const drift::Project &project = m_app->m_project;
    const drift::Clip &clip = project.tracks().at(trackIndex).clips.at(clipIndex);
    drift::TimeUs at = m_app->playheadUs();
    if (!clip.containsTime(at))
        return out;
    const bool hiding = m_chooser.startsWith(QLatin1String("hide-"));
    const Source own = pickSource(trackIndex, clipIndex, at);
    const drift::Clip *video = hiding ? (own.trackIndex < 0 ? nullptr : &project.tracks().at(own.trackIndex).clips.at(own.clipIndex))
                                      : followedVideo(clip, trackIndex, clipIndex);
    if (!video || video->faceTrackPath.isEmpty() || !video->containsTime(at))
        return out;
    const std::shared_ptr<const drift::FaceTrack> faces = drift::loadFaceTrackCached(video->faceTrackPath);
    if (!faces || faces->isEmpty())
        return out;
    const QRectF videoRect = canvasRect(*video, at, project.width(), project.height());
    if (videoRect.height() <= 0.0)
        return out;
    const QList<QRectF> rects = faceRects(
        faces->sampleAll(video->timelineToSourceUs(at) - video->faceTrackSrcOffsetUs), videoRect.width() / videoRect.height());
    int selected = clip.motionTrack && clip.motionTrack->mode == QLatin1String("face") ? clip.motionTrack->faceSlot : -1;
    if (hiding) {
        // What Hide a face takes with nothing picked: the face nearest the middle of the frame.
        selected = nearestFace(rects, QPointF(0.5, 0.5));
    } else if (selected < 0 || selected >= rects.size() || rects.at(selected).isNull()) {
        const QRectF element = canvasRect(clip, at, project.width(), project.height());
        selected = nearestFace(rects, QPointF((element.center().x() - videoRect.x()) / videoRect.width(),
                                              (element.center().y() - videoRect.y()) / videoRect.height()));
    }
    for (int i = 0; i < rects.size(); ++i) {
        if (rects.at(i).isNull())
            continue;
        const QRectF r = normalizedToCanvas(rects.at(i), videoRect);
        out.append(QVariantMap{{QStringLiteral("slot"), i}, {QStringLiteral("x"), r.x()}, {QStringLiteral("y"), r.y()},
                               {QStringLiteral("w"), r.width()}, {QStringLiteral("h"), r.height()},
                               {QStringLiteral("selected"), i == selected}});
    }
    return out;
}

QVariantMap MotionTrackController::targetAt(int trackIndex, int clipIndex) const
{
    QVariantMap out{{QStringLiteral("ok"), false}};
    if (!m_app->isValidClipIndex(trackIndex, clipIndex))
        return out;
    const drift::Project &project = m_app->m_project;
    const drift::Clip &clip = project.tracks().at(trackIndex).clips.at(clipIndex);
    if (!clip.motionTrack || clip.motionTrack->isEmpty())
        return out;
    const drift::TimeUs at = m_app->playheadUs();
    const drift::Clip *video = followedVideo(clip, trackIndex, clipIndex);
    if (!video || video->id != clip.motionTrack->sourceClipId || !video->containsTime(at) || !clip.containsTime(at))
        return out;
    const QList<Sample> &samples = clip.motionTrack->samples;
    const drift::TimeUs sourceUs = video->timelineToSourceUs(at);
    const auto it = std::lower_bound(samples.cbegin(), samples.cend(), sourceUs,
                                     [](const Sample &s, drift::TimeUs t) { return s.sourceUs < t; });
    // The nearer of the two samples around the playhead, if it is within a couple of frames.
    const Sample *best = nullptr;
    for (auto candidate : {it, it == samples.cbegin() ? samples.cend() : it - 1}) {
        if (candidate == samples.cend())
            continue;
        if (!best || std::llabs(candidate->sourceUs - sourceUs) < std::llabs(best->sourceUs - sourceUs))
            best = &*candidate;
    }
    const drift::TimeUs frame = drift::kUsPerSecond / qMax(1, project.fps());
    if (!best || std::llabs(best->sourceUs - sourceUs) > 2 * frame * qMax(1.0, std::abs(video->effectiveSpeed())))
        return out;
    const QRectF r = normalizedToCanvas(best->rect, canvasRect(*video, at, project.width(), project.height()));
    out.insert(QStringLiteral("ok"), true);
    out.insert(QStringLiteral("x"), r.x());
    out.insert(QStringLiteral("y"), r.y());
    out.insert(QStringLiteral("w"), r.width());
    out.insert(QStringLiteral("h"), r.height());
    out.insert(QStringLiteral("state"), stateName(best->state));
    return out;
}

void MotionTrackController::setChooser(const QString &chooser)
{
    if (m_chooser == chooser)
        return;
    m_chooser = chooser;
    emit chooserChanged();
}

void MotionTrackController::setPick(const QVariantMap &pick)
{
    if (m_pick == pick)
        return;
    m_pick = pick;
    emit pickChanged();
}

QVariantMap MotionTrackController::regionFromCanvas(int trackIndex, int clipIndex, double x, double y, double w,
                                                    double h) const
{
    QVariantMap out{{QStringLiteral("ok"), false}};
    if (!m_app->isValidClipIndex(trackIndex, clipIndex) || w <= 0.0 || h <= 0.0)
        return out;
    const drift::Project &project = m_app->m_project;
    const drift::Clip &clip = project.tracks().at(trackIndex).clips.at(clipIndex);
    const drift::TimeUs at = m_app->playheadUs();
    const Source source = pickSource(trackIndex, clipIndex, clip.containsTime(at) ? at : clip.timelineStart);
    if (source.trackIndex < 0)
        return out;
    const QRectF v = canvasRect(project.tracks().at(source.trackIndex).clips.at(source.clipIndex), at,
                                project.width(), project.height());
    if (v.width() <= 0.0 || v.height() <= 0.0)
        return out;
    const QRectF n = QRectF((x - v.x()) / v.width(), (y - v.y()) / v.height(), w / v.width(), h / v.height())
                         .intersected(QRectF(0, 0, 1, 1));
    if (n.isEmpty())
        return out;
    out.insert(QStringLiteral("ok"), true);
    out.insert(QStringLiteral("x"), n.x());
    out.insert(QStringLiteral("y"), n.y());
    out.insert(QStringLiteral("w"), n.width());
    out.insert(QStringLiteral("h"), n.height());
    return out;
}

bool MotionTrackController::objectModelReady() const
{
    return drift::ObjectDetector::modelPresent();
}

void MotionTrackController::clearObjectTargets()
{
    ++m_objectGeneration;
    m_detectingObjects = false;
    m_objectTargets.clear();
    emit objectTargetsChanged();
}

void MotionTrackController::detectObjects(int trackIndex, int clipIndex)
{
    clearObjectTargets();
    if (!m_app->isValidClipIndex(trackIndex, clipIndex))
        return;
    if (!drift::ObjectDetector::modelPresent()) {
        m_app->setLastMessage(tr("Object detection needs the “Object tracking” extra"), QStringLiteral("warning"));
        return;
    }
    const drift::Project &project = m_app->m_project;
    const drift::Clip &clip = project.tracks().at(trackIndex).clips.at(clipIndex);
    const drift::TimeUs at = m_app->playheadUs();
    if (!clip.containsTime(at))
        return;
    const Source source = pickSource(trackIndex, clipIndex, at);
    if (source.trackIndex < 0)
        return;
    const drift::Clip video = project.tracks().at(source.trackIndex).clips.at(source.clipIndex);
    const QRectF videoRect = canvasRect(video, at, project.width(), project.height());
    const int generation = m_objectGeneration;
    m_detectingObjects = true;
    emit objectTargetsChanged();
    (void)QtConcurrent::run([this, video, videoRect, at, generation]() {
        const QImage frame = video.type == drift::ClipType::Image
            ? drift::decodeStillImage(video.path, kDecodeSide, kDecodeSide)
            : ClipReaderPool::instance().readVideoFrame(video.path, kMotionTrackStreamId, video.timelineToSourceUs(at),
                                                        kDecodeSide, kDecodeSide, video.rotationCorrection);
        QList<drift::Detection> found;
        if (!frame.isNull())
            found = drift::ObjectDetector::instance().detect(frame);
        QVariantList targets;
        for (const drift::Detection &d : found) {
            const QRectF n(d.box.x() / frame.width(), d.box.y() / frame.height(), d.box.width() / frame.width(),
                           d.box.height() / frame.height());
            const QRectF r = normalizedToCanvas(n, videoRect);
            targets.append(QVariantMap{
                {QStringLiteral("x"), r.x()}, {QStringLiteral("y"), r.y()},
                {QStringLiteral("w"), r.width()}, {QStringLiteral("h"), r.height()},
                {QStringLiteral("region"), QVariantMap{{QStringLiteral("x"), n.x()}, {QStringLiteral("y"), n.y()},
                                                       {QStringLiteral("w"), n.width()},
                                                       {QStringLiteral("h"), n.height()}}},
                {QStringLiteral("classId"), d.classId}, {QStringLiteral("score"), d.score}});
        }
        QMetaObject::invokeMethod(this, [this, targets, generation]() {
            if (generation != m_objectGeneration)
                return;
            m_detectingObjects = false;
            m_objectTargets = targets;
            emit objectTargetsChanged();
            if (targets.isEmpty())
                m_app->setLastMessage(tr("No objects found here: draw a box around what to follow"),
                                      QStringLiteral("warning"));
        }, Qt::QueuedConnection);
    });
}

void MotionTrackController::blurFace(int trackIndex, int clipIndex, const QString &style, int faceSlot)
{
    if (m_busy || !m_app->isValidClipIndex(trackIndex, clipIndex))
        return;
    m_app->m_project.ensureTrackIds();
    const drift::Project &project = m_app->m_project;
    const drift::Clip video = project.tracks().at(trackIndex).clips.at(clipIndex);
    if (!followsVideo(video.type) || video.path.isEmpty()) {
        m_app->setLastMessage(tr("Select a video or a photo to hide a face in it"), QStringLiteral("warning"));
        return;
    }
    if (video.faceTrackPath.isEmpty()) {
        m_pendingBlur = QVariantMap{{QStringLiteral("clipId"), video.id}, {QStringLiteral("style"), style},
                                    {QStringLiteral("faceSlot"), faceSlot}};
        m_app->setLastMessage(tr("Scanning the faces in the video first…"));
        m_app->faces()->detect(trackIndex, clipIndex);
        return;
    }
    const std::shared_ptr<const drift::FaceTrack> faces = drift::loadFaceTrackCached(video.faceTrackPath);
    if (!faces || faces->isEmpty()) {
        m_app->setLastMessage(tr("No face was found in this clip"), QStringLiteral("warning"));
        return;
    }
    const int projectW = project.width();
    const int projectH = project.height();
    const int fps = qMax(1, project.fps());
    const drift::TimeUs step = drift::kUsPerSecond / fps;
    const drift::TimeUs start = video.timelineStart;
    const drift::TimeUs end = video.timelineStart + video.timelineDuration;
    const auto rectsAt = [&](drift::TimeUs t, double aspect) {
        return faceRects(faces->sampleAll(video.timelineToSourceUs(t) - video.faceTrackSrcOffsetUs), aspect);
    };

    // The face to hide: the one asked for, else the one nearest the middle of the frame at the
    // playhead (or at the start, when the playhead is off the clip).
    drift::TimeUs t0 = m_app->playheadUs();
    if (!video.containsTime(t0))
        t0 = start;
    const QRectF v0 = canvasRect(video, t0, projectW, projectH);
    if (v0.width() <= 0.0 || v0.height() <= 0.0)
        return;
    const QList<QRectF> first = rectsAt(t0, v0.width() / v0.height());
    int slot = faceSlot >= 0 && faceSlot < first.size() && !first.at(faceSlot).isNull()
        ? faceSlot
        : nearestFace(first, QPointF(0.5, 0.5));
    if (slot < 0) {
        m_app->setLastMessage(tr("There is no face at the playhead: move to a frame where the face shows"),
                              QStringLiteral("warning"));
        return;
    }

    // The oval in canvas-normalized terms (a standalone layer's mask is measured on the canvas),
    // followed outward from the anchor in both directions with the same person kept.
    struct Key { drift::TimeUs t; QRectF r; };
    QList<Key> keys;
    for (int pass = 0; pass < 2; ++pass) {
        int current = slot;
        QRectF last = first.at(slot);
        for (drift::TimeUs t = pass == 0 ? t0 : t0 - step; pass == 0 ? t < end : t >= start;
             t += pass == 0 ? step : -step) {
            const QRectF v = canvasRect(video, t, projectW, projectH);
            if (v.width() <= 0.0 || v.height() <= 0.0)
                continue;
            const QList<QRectF> rects = rectsAt(t, v.width() / v.height());
            const int picked = drift::followFaceSlot(rects, last, current);
            if (picked < 0)
                continue; // lost: the mask glides between the frames the face was found in
            current = picked;
            last = rects.at(picked);
            const QRectF c = normalizedToCanvas(last, v);
            // A little larger than the oval of the face, so hair and jaw are covered too.
            keys.append({t, QRectF((c.center().x()) / projectW, (c.center().y()) / projectH,
                                   c.width() * 1.35 / projectW, c.height() * 1.35 / projectH)});
        }
    }
    if (keys.isEmpty()) {
        m_app->setLastMessage(tr("No face was found in this clip"), QStringLiteral("warning"));
        return;
    }
    QList<HideKey> hideKeys;
    double faceWidth = 0.0;
    for (const Key &k : keys) {
        hideKeys.append({k.t, k.r});
        faceWidth += k.r.width() * projectW / 1.35;
    }
    addHideLayer(trackIndex, video, hideKeys, style, faceWidth / keys.size() / 8.0,
                 style == QLatin1String("blur") ? tr("Blurred face") : tr("Pixelated face"), tr("Hide face"),
                 tr("Face hidden: its layer is above the clip, where it can be trimmed or removed"));
}

void MotionTrackController::addHideLayer(int trackIndex, const drift::Clip &video, QList<HideKey> keys,
                                         const QString &style, double blockPx, const QString &name,
                                         const QString &undoText, const QString &message)
{
    if (keys.isEmpty())
        return;
    const QString effectId = style == QLatin1String("blur") ? QStringLiteral("builtin.effects.gaussian_blur")
                                                            : QStringLiteral("stylize.pixelate");
    std::optional<drift::Effect> effect = m_app->effectWithDefaults(effectId);
    if (!effect)
        return;
    if (style == QLatin1String("blur")) {
        effect->parameters.insert(QStringLiteral("u_blurRadius"), 40.0);
    } else {
        // Blocks sized to what is hidden, about eight across it: small blocks still let a face be
        // recognised, and a fixed size meant a different look on every video.
        const double block = qBound(14.0, blockPx, 64.0);
        effect->parameters.insert(QStringLiteral("width"), block);
        effect->parameters.insert(QStringLiteral("height"), block);
    }
    std::sort(keys.begin(), keys.end(), [](const HideKey &a, const HideKey &b) { return a.t < b.t; });
    const drift::TimeUs start = video.timelineStart;

    drift::Clip layer;
    layer.id = QUuid::createUuid().toString(QUuid::WithoutBraces);
    layer.type = drift::ClipType::Adjustment;
    layer.adjustmentKind = drift::AdjustmentKind::VideoEffects;
    layer.name = name;
    layer.timelineStart = start;
    layer.timelineDuration = video.timelineDuration;
    layer.srcIn = 0;
    layer.srcOut = video.timelineDuration;
    layer.effects.append(*effect);
    layer.masksLimitEffects = true;
    layer.mask.shape = drift::MaskShape::Ellipse;
    layer.mask.feather = 14.0;
    layer.mask.x = keys.first().r.x();
    layer.mask.y = keys.first().r.y();
    layer.mask.w = keys.first().r.width();
    layer.mask.h = keys.first().r.height();
    // A key every other frame, averaged over its neighbours (a symmetric window, so the ends stay
    // on the target): smooth, and few enough to retouch.
    for (int i = 0; i < keys.size(); ++i) {
        if (i % 2 != 0 && i != keys.size() - 1)
            continue;
        QPointF centre;
        QSizeF size(0.0, 0.0); // not QSizeF(): that is (-1, -1), an invalid size that would skew the sum
        int n = 0;
        const int half = qMin(2, qMin(i, int(keys.size()) - 1 - i));
        for (int j = i - half; j <= i + half; ++j) {
            centre += QPointF(keys.at(j).r.x(), keys.at(j).r.y());
            size += keys.at(j).r.size();
            ++n;
        }
        const drift::TimeUs rel = keys.at(i).t - start;
        layer.mask.keyframes[QStringLiteral("x")].setKeyframe(rel, centre.x() / n);
        layer.mask.keyframes[QStringLiteral("y")].setKeyframe(rel, centre.y() / n);
        layer.mask.keyframes[QStringLiteral("w")].setKeyframe(rel, size.width() / n);
        layer.mask.keyframes[QStringLiteral("h")].setKeyframe(rel, size.height() / n);
    }

    const drift::Project before = m_app->m_project;
    drift::Track layerTrack;
    layerTrack.type = drift::TrackType::Adjustment;
    layerTrack.id = QUuid::createUuid().toString(QUuid::WithoutBraces);
    layerTrack.clips.append(layer);
    // Right above the video (track 0 is on top), so it hides on that clip and what is under it,
    // never on what was stacked over it.
    m_app->m_project.tracks().insert(trackIndex, layerTrack);
    m_app->pushProjectEdit(before, undoText);
    m_app->finishEdit(undoText);
    m_app->selectClip(trackIndex, 0);
    m_app->setLastMessage(message, QStringLiteral("success"));
    bump();
}

void MotionTrackController::hideObject(int trackIndex, int clipIndex, const QString &style, const QVariantMap &region,
                                       int classId)
{
    if (m_busy) {
        m_app->setLastMessage(tr("Tracking already in progress"), QStringLiteral("warning"));
        return;
    }
    if (!m_app->isValidClipIndex(trackIndex, clipIndex))
        return;
    const drift::Project &project = m_app->m_project;
    const drift::Clip video = project.tracks().at(trackIndex).clips.at(clipIndex);
    if (!followsVideo(video.type) || video.path.isEmpty()) {
        m_app->setLastMessage(tr("Select a video or a photo to hide something in it"), QStringLiteral("warning"));
        return;
    }
    const QRectF picked(region.value(QStringLiteral("x")).toDouble(), region.value(QStringLiteral("y")).toDouble(),
                        region.value(QStringLiteral("w")).toDouble(), region.value(QStringLiteral("h")).toDouble());
    if (picked.width() <= 0.0 || picked.height() <= 0.0) {
        m_app->setLastMessage(tr("Pick an object on the preview, or draw a box around it, first"),
                              QStringLiteral("warning"));
        return;
    }
    drift::TimeUs t0 = m_app->playheadUs();
    if (!video.containsTime(t0))
        t0 = video.timelineStart;
    const int fps = qMax(1, project.fps());
    const drift::TimeUs step = drift::kUsPerSecond / fps;
    QList<drift::TimeUs> forward, backward;
    stepsAround(t0, video.timelineStart, video.timelineStart + video.timelineDuration, step, &forward, &backward);
    const int total = forward.size() + backward.size();
    const int projectW = project.width();
    const int projectH = project.height();

    m_app->setPlaying(false);
    m_cancel.storeRelaxed(0);
    m_progress = 0.0;
    emit progressChanged();
    m_status = tr("Getting ready…");
    emit statusChanged();
    setBusy(true);
    const QString videoId = video.id;
    (void)QtConcurrent::run([this, video, picked, t0, forward, backward, total, classId, style, videoId, projectW,
                             projectH]() {
        int done = 0;
        const ObjectRun run = runObjectTracking(video, picked, t0, forward, backward, true, classId, m_cancel, [&]() {
            ++done;
            const double fraction = double(done) / qMax(1, total);
            const QString status = tr("Following frame %1 of %2…").arg(done).arg(total);
            QMetaObject::invokeMethod(this, [this, fraction, status]() {
                m_progress = fraction;
                emit progressChanged();
                m_status = status;
                emit statusChanged();
            }, Qt::QueuedConnection);
        });
        QMetaObject::invokeMethod(this, [this, run, style, videoId, projectW, projectH]() {
            setBusy(false);
            if (!run.error.isEmpty()) {
                m_status = run.error;
                emit statusChanged();
                m_app->setLastMessage(run.error, QStringLiteral("error"));
                emit finished(false, run.error);
                return;
            }
            int trackIndex = -1;
            const drift::Clip *video = nullptr;
            const QList<drift::Track> &tracks = m_app->m_project.tracks();
            for (int t = 0; t < tracks.size() && !video; ++t) {
                for (const drift::Clip &c : tracks.at(t).clips) {
                    if (c.id == videoId) {
                        trackIndex = t;
                        video = &c;
                        break;
                    }
                }
            }
            if (!video) {
                emit finished(false, QString());
                return;
            }
            const drift::Clip videoCopy = *video;
            QList<HideKey> keys;
            double width = 0.0;
            for (const Sample &s : run.samples) {
                if (s.state == Sample::State::Lost)
                    continue;
                const drift::TimeUs t = videoCopy.timelineStart + videoCopy.sourceUsToClipLocalUs(s.sourceUs);
                const QRectF c = normalizedToCanvas(s.rect, canvasRect(videoCopy, t, projectW, projectH));
                // A little larger than the box, so the oval covers its corners.
                keys.append({t, QRectF(c.center().x() / projectW, c.center().y() / projectH,
                                       c.width() * 1.2 / projectW, c.height() * 1.2 / projectH)});
                width += c.width();
            }
            if (keys.isEmpty()) {
                const QString message = tr("Nothing to follow was found");
                m_app->setLastMessage(message, QStringLiteral("warning"));
                emit finished(false, message);
                return;
            }
            addHideLayer(trackIndex, videoCopy, keys, style, width / keys.size() / 8.0,
                         style == QLatin1String("blur") ? tr("Blurred object") : tr("Pixelated object"),
                         tr("Hide object"),
                         tr("Object hidden: its layer is above the clip, where it can be trimmed or removed"));
            m_progress = 1.0;
            emit progressChanged();
            emit finished(true, QString());
        }, Qt::QueuedConnection);
    });
}

MotionTrackController::MaskTarget MotionTrackController::maskTarget(int trackIndex, int clipIndex,
                                                                    drift::TimeUs atUs) const
{
    MaskTarget target;
    if (!m_app->isValidClipIndex(trackIndex, clipIndex))
        return target;
    const QList<drift::Track> &tracks = m_app->m_project.tracks();
    const drift::Track &track = tracks.at(trackIndex);
    const drift::Clip &clip = track.clips.at(clipIndex);
    if (clip.type != drift::ClipType::Adjustment || !clip.mask.contributes() || clip.mask.isMedia()) {
        target.reason = tr("Select a mask to make it follow what it covers");
        return target;
    }
    const auto at = [&](const QString &id) {
        for (int t = 0; t < tracks.size(); ++t) {
            for (int c = 0; c < tracks.at(t).clips.size(); ++c) {
                if (tracks.at(t).clips.at(c).id == id) {
                    target.videoTrack = t;
                    target.videoClip = c;
                    return true;
                }
            }
        }
        return false;
    };
    // Pinned to a clip, or on a lane of a track: measured on that clip's frame.
    if (!clip.linkedClipId.isEmpty()) {
        at(clip.linkedClipId);
    } else if (track.isAdjustmentLane()) {
        for (int t = 0; t < tracks.size() && target.videoTrack < 0; ++t) {
            if (tracks.at(t).id != track.parentTrackId)
                continue;
            for (int c = 0; c < tracks.at(t).clips.size(); ++c) {
                if (tracks.at(t).clips.at(c).containsTime(atUs)) {
                    target.videoTrack = t;
                    target.videoClip = c;
                    break;
                }
            }
        }
    } else {
        // A standalone layer: measured on the canvas, over whatever picture is under it.
        const Source source = sourceUnder(trackIndex, clipIndex, atUs);
        target.videoTrack = source.trackIndex;
        target.videoClip = source.clipIndex;
        target.canvasSpace = true;
    }
    if (target.videoTrack < 0) {
        target.reason = tr("Put the mask over a video to follow something in it");
        return target;
    }
    const drift::Clip &video = tracks.at(target.videoTrack).clips.at(target.videoClip);
    if (!followsVideo(video.type) || video.path.isEmpty()) {
        target.reason = tr("Put the mask over a video to follow something in it");
        return target;
    }
    target.ok = true;
    return target;
}

QVariantMap MotionTrackController::maskFollowSource(int trackIndex, int clipIndex) const
{
    drift::TimeUs at = m_app->playheadUs();
    if (m_app->isValidClipIndex(trackIndex, clipIndex)) {
        const drift::Clip &clip = m_app->m_project.tracks().at(trackIndex).clips.at(clipIndex);
        if (!clip.containsTime(at))
            at = clip.timelineStart;
    }
    const MaskTarget target = maskTarget(trackIndex, clipIndex, at);
    return QVariantMap{{QStringLiteral("ok"), target.ok}, {QStringLiteral("reason"), target.reason}};
}

void MotionTrackController::maskFollow(int trackIndex, int clipIndex, bool followScale)
{
    if (m_busy) {
        m_app->setLastMessage(tr("Tracking already in progress"), QStringLiteral("warning"));
        return;
    }
    if (!m_app->isValidClipIndex(trackIndex, clipIndex))
        return;
    const drift::Project &project = m_app->m_project;
    const drift::Clip maskClip = project.tracks().at(trackIndex).clips.at(clipIndex);
    drift::TimeUs t0 = m_app->playheadUs();
    if (!maskClip.containsTime(t0))
        t0 = maskClip.timelineStart;
    const MaskTarget target = maskTarget(trackIndex, clipIndex, t0);
    if (!target.ok) {
        m_app->setLastMessage(target.reason, QStringLiteral("warning"));
        return;
    }
    const drift::Clip video = project.tracks().at(target.videoTrack).clips.at(target.videoClip);
    const int projectW = project.width();
    const int projectH = project.height();

    // The mask at the playhead, as a box of the video's frame.
    const drift::Mask now = maskClip.mask.isAnimated() ? maskClip.mask.resolvedAt(t0 - maskClip.timelineStart)
                                                       : maskClip.mask;
    QRectF region(now.x - now.w / 2, now.y - now.h / 2, now.w, now.h);
    if (target.canvasSpace) {
        const QRectF v = canvasRect(video, t0, projectW, projectH);
        if (v.width() <= 0.0 || v.height() <= 0.0)
            return;
        const QRectF c(region.x() * projectW, region.y() * projectH, region.width() * projectW,
                       region.height() * projectH);
        region = QRectF((c.x() - v.x()) / v.width(), (c.y() - v.y()) / v.height(), c.width() / v.width(),
                        c.height() / v.height());
    }
    region = region.intersected(QRectF(0, 0, 1, 1));
    if (region.isEmpty()) {
        m_app->setLastMessage(tr("Move the mask over what it should follow"), QStringLiteral("warning"));
        return;
    }

    const drift::TimeUs rangeStart = qMax(maskClip.timelineStart, video.timelineStart);
    const drift::TimeUs rangeEnd = qMin(maskClip.timelineStart + maskClip.timelineDuration,
                                        video.timelineStart + video.timelineDuration);
    const drift::TimeUs step = drift::kUsPerSecond / qMax(1, project.fps());
    QList<drift::TimeUs> forward, backward;
    stepsAround(t0, rangeStart, rangeEnd, step, &forward, &backward);
    const int total = forward.size() + backward.size();
    const bool canvasSpace = target.canvasSpace;
    // Scale is measured against the mask and its target at the playhead, where it was placed.
    const QSizeF baseSize(now.w, now.h);

    m_app->setPlaying(false);
    m_cancel.storeRelaxed(0);
    m_progress = 0.0;
    emit progressChanged();
    m_status = tr("Getting ready…");
    emit statusChanged();
    setBusy(true);
    const QString maskId = maskClip.id;
    const QString videoId = video.id;
    (void)QtConcurrent::run([this, video, region, t0, forward, backward, total, followScale, maskId, videoId,
                             canvasSpace, projectW, projectH, baseSize]() {
        int done = 0;
        const ObjectRun run = runObjectTracking(video, region, t0, forward, backward, followScale, -1, m_cancel, [&]() {
            ++done;
            const double fraction = double(done) / qMax(1, total);
            const QString status = tr("Following frame %1 of %2…").arg(done).arg(total);
            QMetaObject::invokeMethod(this, [this, fraction, status]() {
                m_progress = fraction;
                emit progressChanged();
                m_status = status;
                emit statusChanged();
            }, Qt::QueuedConnection);
        });
        QMetaObject::invokeMethod(this, [this, run, followScale, maskId, videoId, canvasSpace, projectW, projectH,
                                         baseSize, t0]() {
            setBusy(false);
            if (!run.error.isEmpty()) {
                m_status = run.error;
                emit statusChanged();
                m_app->setLastMessage(run.error, QStringLiteral("error"));
                emit finished(false, run.error);
                return;
            }
            int maskTrack = -1, maskIndex = -1;
            const drift::Clip *video = nullptr;
            const QList<drift::Track> &tracks = m_app->m_project.tracks();
            for (int t = 0; t < tracks.size(); ++t) {
                for (int c = 0; c < tracks.at(t).clips.size(); ++c) {
                    const drift::Clip &clip = tracks.at(t).clips.at(c);
                    if (clip.id == maskId) {
                        maskTrack = t;
                        maskIndex = c;
                    }
                    if (clip.id == videoId)
                        video = &clip;
                }
            }
            if (maskTrack < 0 || !video) {
                emit finished(false, QString());
                return;
            }
            const drift::Clip videoCopy = *video;
            struct Point { drift::TimeUs t; QRectF r; };
            QList<Point> points;
            for (const Sample &s : run.samples) {
                if (s.state == Sample::State::Lost)
                    continue;
                const drift::TimeUs t = videoCopy.timelineStart + videoCopy.sourceUsToClipLocalUs(s.sourceUs);
                QRectF r = s.rect; // the video's frame: a lane mask's own space
                if (canvasSpace) {
                    const QRectF c = normalizedToCanvas(s.rect, canvasRect(videoCopy, t, projectW, projectH));
                    r = QRectF(c.x() / projectW, c.y() / projectH, c.width() / projectW, c.height() / projectH);
                }
                points.append({t, r});
            }
            if (points.isEmpty()) {
                const QString message = tr("Nothing to follow was found");
                m_app->setLastMessage(message, QStringLiteral("warning"));
                emit finished(false, message);
                return;
            }
            std::sort(points.begin(), points.end(), [](const Point &a, const Point &b) { return a.t < b.t; });
            const drift::Project before = m_app->m_project;
            drift::Clip &maskClip = m_app->m_project.tracks()[maskTrack].clips[maskIndex];
            drift::Mask &mask = maskClip.mask;
            mask.keyframes.remove(QStringLiteral("x"));
            mask.keyframes.remove(QStringLiteral("y"));
            if (followScale) {
                mask.keyframes.remove(QStringLiteral("w"));
                mask.keyframes.remove(QStringLiteral("h"));
            }
            // The mask keeps its own size and shape; its centre (and with scale, its size) follows. The
            // size scales by the target's width against its width at the playhead.
            const Point *ref = &points.first();
            for (const Point &p : points) {
                if (std::llabs(p.t - t0) < std::llabs(ref->t - t0))
                    ref = &p;
            }
            const QRectF first = ref->r;
            const QSizeF base = baseSize;
            for (int i = 0; i < points.size(); ++i) {
                if (i % 2 != 0 && i != points.size() - 1)
                    continue;
                const int half = qMin(2, qMin(i, int(points.size()) - 1 - i));
                QPointF centre;
                double k = 0.0;
                for (int j = i - half; j <= i + half; ++j) {
                    centre += points.at(j).r.center();
                    k += points.at(j).r.width() / qMax(1e-6, first.width());
                }
                centre /= (2 * half + 1);
                k /= (2 * half + 1);
                const drift::TimeUs rel = points.at(i).t - maskClip.timelineStart;
                mask.keyframes[QStringLiteral("x")].setKeyframe(rel, centre.x());
                mask.keyframes[QStringLiteral("y")].setKeyframe(rel, centre.y());
                if (followScale) {
                    mask.keyframes[QStringLiteral("w")].setKeyframe(rel, base.width() * k);
                    mask.keyframes[QStringLiteral("h")].setKeyframe(rel, base.height() * k);
                }
            }
            m_app->pushProjectEdit(before, tr("Mask follows"));
            m_app->finishEdit(tr("Mask follows"));
            const int lost = int(run.samples.size() - points.size());
            const QString message = lost > 0
                ? tr("Tracking done — lost the subject in %1 of %2 frames").arg(lost).arg(run.samples.size())
                : tr("Tracking done");
            m_progress = 1.0;
            emit progressChanged();
            m_status = message;
            emit statusChanged();
            m_app->setLastMessage(message, QStringLiteral("success"));
            bump();
            emit finished(true, message);
        }, Qt::QueuedConnection);
    });
}

void MotionTrackController::cancel()
{
    m_cancel.storeRelaxed(1);
    m_pendingFaceClipId.clear();
}

void MotionTrackController::clear(int trackIndex, int clipIndex)
{
    if (!m_app->isValidClipIndex(trackIndex, clipIndex))
        return;
    const drift::Project before = m_app->m_project;
    drift::Clip &clip = m_app->m_project.tracks()[trackIndex].clips[clipIndex];
    drift::TimeUs at = m_app->playheadUs();
    if (!clip.containsTime(at))
        at = clip.timelineStart;
    const QRectF rect = canvasRect(clip, at, m_app->m_project.width(), m_app->m_project.height());
    const auto hold = [](drift::KeyframeTrack<double> &track, double value) {
        track = drift::KeyframeTrack<double>{};
        track.setKeyframe(0, value);
    };
    hold(clip.transformX, rect.x());
    hold(clip.transformY, rect.y());
    hold(clip.transformW, rect.width());
    hold(clip.transformH, rect.height());
    if (clip.motionTrack && clip.motionTrack->followScale && isText(clip)
        && clip.textStyle.keyframes.contains(QStringLiteral("pixelSize"))) {
        const drift::KeyframeTrack<double> size = clip.textStyle.keyframes.value(QStringLiteral("pixelSize"));
        if (!size.isEmpty())
            clip.textStyle.pixelSize = int(std::lround(size.evaluateAt(at - clip.timelineStart)));
        clip.textStyle.keyframes.remove(QStringLiteral("pixelSize"));
    }
    clip.motionTrack.reset();
    m_app->pushProjectEdit(before, tr("Remove tracking"));
    m_app->finishEdit(tr("Remove tracking"));
    m_app->setLastMessage(tr("Tracking removed"), QStringLiteral("success"));
    bump();
}

// A tracking made before 0.22.1 does not know which keys it wrote, so its re-bake replaced the
// whole position animation: say so instead of losing the user's keys in silence.
void MotionTrackController::warnIfKeysReplaced(int removed)
{
    if (removed <= 0)
        return;
    m_app->setLastMessage(tr("The position keyframes of this element were replaced by the new tracking. "
                             "Undo (Ctrl+Z) brings them back."),
                          QStringLiteral("warning"));
}

bool MotionTrackController::rebake(int trackIndex, int clipIndex, const QString &undoText)
{
    drift::Clip &clip = m_app->m_project.tracks()[trackIndex].clips[clipIndex];
    const drift::Clip *video = followedVideo(clip, trackIndex, clipIndex);
    if (!video || video->id != clip.motionTrack->sourceClipId) {
        m_app->setLastMessage(tr("The video it followed is no longer in the project"), QStringLiteral("warning"));
        return false;
    }
    const drift::Project before = m_app->m_project;
    const drift::Clip videoCopy = *video;
    const int removed = resetTrackedKeys(clip);
    const drift::MotionBakeResult baked = drift::bakeMotionTrack(*clip.motionTrack, videoCopy, &clip,
                                                                 m_app->m_project.width(), m_app->m_project.height());
    if (!baked.ok) {
        m_app->m_project = before;
        m_app->setLastMessage(tr("The element and the tracked part of the video no longer overlap"),
                              QStringLiteral("warning"));
        return false;
    }
    rememberBake(clip, baked);
    m_app->pushProjectEdit(before, undoText);
    m_app->finishEdit(undoText);
    warnIfKeysReplaced(removed);
    bump();
    return true;
}

bool MotionTrackController::setOption(int trackIndex, int clipIndex, const QString &key, const QVariant &value)
{
    if (m_busy || !m_app->isValidClipIndex(trackIndex, clipIndex))
        return false;
    if (key != QLatin1String("followScale") && key != QLatin1String("keepDistance"))
        return false;
    const drift::Clip &current = m_app->m_project.tracks().at(trackIndex).clips.at(clipIndex);
    if (!current.motionTrack || current.motionTrack->isEmpty())
        return false;
    const drift::Clip *video = followedVideo(current, trackIndex, clipIndex);
    if (!video || video->id != current.motionTrack->sourceClipId) {
        m_app->setLastMessage(tr("The video it followed is no longer in the project"), QStringLiteral("warning"));
        return false;
    }
    const drift::Clip videoCopy = *video;
    const drift::Project before = m_app->m_project;
    drift::Clip &clip = m_app->m_project.tracks()[trackIndex].clips[clipIndex];
    if (key == QLatin1String("followScale")) {
        clip.motionTrack->followScale = value.toBool();
        // Scale switched off: back to the element's size at the anchor, keyed once.
        if (!value.toBool()) {
            const QRectF anchor = clip.motionTrack->anchorElement;
            clip.transformW = drift::KeyframeTrack<double>{};
            clip.transformW.setKeyframe(0, anchor.width());
            clip.transformH = drift::KeyframeTrack<double>{};
            clip.transformH.setKeyframe(0, anchor.height());
            if (isText(clip) && clip.motionTrack->anchorPixelSize > 0.0) {
                clip.textStyle.keyframes.remove(QStringLiteral("pixelSize"));
                clip.textStyle.pixelSize = int(std::lround(clip.motionTrack->anchorPixelSize));
            }
        }
    } else {
        clip.motionTrack->keepDistance = value.toBool();
    }
    const int removed = resetTrackedKeys(clip);
    const drift::MotionBakeResult baked = drift::bakeMotionTrack(*clip.motionTrack, videoCopy, &clip,
                                                                 m_app->m_project.width(), m_app->m_project.height());
    if (!baked.ok) {
        m_app->m_project = before;
        return false;
    }
    rememberBake(clip, baked);
    m_app->pushProjectEdit(before, tr("Tracking settings"));
    m_app->finishEdit(tr("Tracking settings"));
    warnIfKeysReplaced(removed);
    bump();
    return true;
}

bool MotionTrackController::realign(int trackIndex, int clipIndex)
{
    if (m_busy || !m_app->isValidClipIndex(trackIndex, clipIndex))
        return false;
    const drift::Clip &clip = m_app->m_project.tracks().at(trackIndex).clips.at(clipIndex);
    if (!clip.motionTrack || clip.motionTrack->isEmpty())
        return false;
    return rebake(trackIndex, clipIndex, tr("Realign tracking"));
}

void MotionTrackController::track(int trackIndex, int clipIndex, const QString &mode, bool followScale)
{
    trackWith(trackIndex, clipIndex, QVariantMap{{QStringLiteral("mode"), mode},
                                                 {QStringLiteral("followScale"), followScale}});
}

void MotionTrackController::trackWith(int trackIndex, int clipIndex, const QVariantMap &options)
{
    if (m_busy) {
        m_app->setLastMessage(tr("Tracking already in progress"), QStringLiteral("warning"));
        return;
    }
    const QVariantMap check = sourceFor(trackIndex, clipIndex);
    if (!check.value(QStringLiteral("ok")).toBool()) {
        m_app->setLastMessage(check.value(QStringLiteral("reason")).toString(), QStringLiteral("warning"));
        return;
    }

    const drift::Project &project = m_app->m_project;
    const drift::Clip overlay = project.tracks().at(trackIndex).clips.at(clipIndex);
    drift::TimeUs t0 = m_app->playheadUs();
    if (!overlay.containsTime(t0))
        t0 = overlay.timelineStart;
    const Source source = sourceUnder(trackIndex, clipIndex, t0);
    const drift::Clip video = project.tracks().at(source.trackIndex).clips.at(source.clipIndex);
    const bool faceMode = options.value(QStringLiteral("mode")).toString() == QLatin1String("face");
    const bool followScale = options.value(QStringLiteral("followScale")).toBool();
    const bool keepDistance = options.value(QStringLiteral("keepDistance"), true).toBool();
    QString direction = options.value(QStringLiteral("direction"), QStringLiteral("both")).toString();
    if (direction != QLatin1String("forward") && direction != QLatin1String("backward"))
        direction = QStringLiteral("both");
    const int requestedSlot = options.value(QStringLiteral("faceSlot"), -1).toInt();
    const QVariantMap picked = options.value(QStringLiteral("region")).toMap();
    const QRectF pickedRegion = picked.isEmpty()
        ? QRectF()
        : QRectF(picked.value(QStringLiteral("x")).toDouble(), picked.value(QStringLiteral("y")).toDouble(),
                 picked.value(QStringLiteral("w")).toDouble(), picked.value(QStringLiteral("h")).toDouble());
    const int classId = options.value(QStringLiteral("classId"), -1).toInt();

    if (faceMode && video.faceTrackPath.isEmpty()) {
        // Scan the faces first, then come back here (see the constructor).
        m_pendingFaceClipId = overlay.id;
        m_pendingOptions = options;
        m_app->setLastMessage(tr("Scanning the faces in the video first…"));
        m_app->faces()->detect(source.trackIndex, source.clipIndex);
        return;
    }

    const drift::TimeUs rangeStart = qMax(overlay.timelineStart, video.timelineStart);
    const drift::TimeUs rangeEnd =
        qMin(overlay.timelineStart + overlay.timelineDuration, video.timelineStart + video.timelineDuration);
    const int fps = qMax(1, project.fps());
    const drift::TimeUs step = drift::kUsPerSecond / fps;
    if (rangeEnd - rangeStart < step) {
        m_app->setLastMessage(tr("The element and the video barely overlap"), QStringLiteral("warning"));
        return;
    }

    // Everything the job needs, resolved here: the timeline may be edited while it runs.
    const int projectW = project.width();
    const int projectH = project.height();
    const QRectF overlayRect0 = canvasRect(overlay, t0, projectW, projectH);
    const QRectF videoRect0 = canvasRect(video, t0, projectW, projectH);
    if (videoRect0.width() <= 0 || videoRect0.height() <= 0)
        return;
    // What to follow: the box picked or drawn on the preview, else whatever the element covers.
    const QRectF region = pickedRegion.width() > 0.0 && pickedRegion.height() > 0.0
        ? pickedRegion
        : QRectF((overlayRect0.x() - videoRect0.x()) / videoRect0.width(),
                 (overlayRect0.y() - videoRect0.y()) / videoRect0.height(),
                 overlayRect0.width() / videoRect0.width(), overlayRect0.height() / videoRect0.height());
    if (!faceMode && !region.intersects(QRectF(0, 0, 1, 1))) {
        m_app->setLastMessage(tr("Move the element over what it should follow"), QStringLiteral("warning"));
        return;
    }
    double pixelSize0 = 0.0;
    if (isText(overlay)) {
        const drift::KeyframeTrack<double> size = overlay.textStyle.keyframes.value(QStringLiteral("pixelSize"));
        pixelSize0 = size.isEmpty() ? overlay.textStyle.pixelSize : size.evaluateAt(t0 - overlay.timelineStart);
    }

    QList<drift::TimeUs> forward{t0};
    if (direction != QLatin1String("backward")) {
        for (drift::TimeUs t = t0 + step; t < rangeEnd; t += step)
            forward.append(t);
    }
    QList<drift::TimeUs> backward;
    if (direction != QLatin1String("forward")) {
        for (drift::TimeUs t = t0 - step; t >= rangeStart; t -= step)
            backward.append(t);
    }
    const int total = forward.size() + backward.size();
    const double aspect = videoRect0.width() / videoRect0.height();
    const QPointF elementCentre((overlayRect0.center().x() - videoRect0.x()) / videoRect0.width(),
                                (overlayRect0.center().y() - videoRect0.y()) / videoRect0.height());

    m_app->setPlaying(false);
    m_cancel.storeRelaxed(0);
    m_progress = 0.0;
    emit progressChanged();
    m_status = tr("Getting ready…");
    emit statusChanged();
    setBusy(true);

    const QString overlayId = overlay.id;
    (void)QtConcurrent::run([this, video, region, faceMode, followScale, keepDistance, direction, requestedSlot,
                             forward, backward, total, overlayId, overlayRect0, pixelSize0, aspect, elementCentre,
                             classId, t0]() {
        const auto progress = [this](double fraction, const QString &status) {
            QMetaObject::invokeMethod(this, [this, fraction, status]() {
                m_progress = fraction;
                emit progressChanged();
                if (status != m_status) {
                    m_status = status;
                    emit statusChanged();
                }
            }, Qt::QueuedConnection);
        };
        const auto fail = [this](const QString &message) {
            QMetaObject::invokeMethod(this, [this, message]() {
                setBusy(false);
                m_status = message;
                emit statusChanged();
                m_app->setLastMessage(message, QStringLiteral("error"));
                emit finished(false, message);
            }, Qt::QueuedConnection);
        };

        QList<Sample> samples;
        QRectF anchorTarget = region;
        int slot = -1;
        int done = 0;
        if (faceMode) {
            const std::shared_ptr<const drift::FaceTrack> faces = drift::loadFaceTrackCached(video.faceTrackPath);
            if (!faces || faces->isEmpty()) {
                fail(tr("The video has no scanned faces"));
                return;
            }
            const auto rectsAt = [&](drift::TimeUs t) {
                return faceRects(faces->sampleAll(video.timelineToSourceUs(t) - video.faceTrackSrcOffsetUs), aspect);
            };
            const QList<QRectF> first = rectsAt(t0);
            slot = requestedSlot >= 0 && requestedSlot < first.size() && !first.at(requestedSlot).isNull()
                ? requestedSlot
                : nearestFace(first, elementCentre);
            if (slot < 0) {
                fail(tr("There is no face at the playhead: move to a frame where the face shows"));
                return;
            }
            anchorTarget = first.at(slot);
            // Outward from the anchor in each direction, keeping to the same person.
            for (int pass = 0; pass < 2; ++pass) {
                const QList<drift::TimeUs> &times = pass == 0 ? forward : backward;
                int current = slot;
                QRectF last = anchorTarget;
                bool wasLost = false;
                QList<Sample> pass_;
                for (const drift::TimeUs t : times) {
                    if (m_cancel.loadRelaxed() != 0) {
                        fail(tr("Tracking cancelled"));
                        return;
                    }
                    const QList<QRectF> rects = rectsAt(t);
                    const int picked = drift::followFaceSlot(rects, last, current);
                    Sample s;
                    s.sourceUs = video.timelineToSourceUs(t);
                    if (picked < 0) {
                        s.rect = last;
                        s.state = Sample::State::Lost;
                        wasLost = true;
                    } else {
                        current = picked;
                        last = rects.at(picked);
                        s.rect = last;
                        s.score = 1.0;
                        s.state = wasLost ? Sample::State::Recovered : Sample::State::Tracked;
                        wasLost = false;
                    }
                    pass_.append(s);
                    ++done;
                    if (done % 8 == 0)
                        progress(double(done) / qMax(1, total), tr("Following frame %1 of %2…").arg(done).arg(total));
                }
                samples += pass_;
            }
        } else {
            const ObjectRun run = runObjectTracking(video, region, t0, forward, backward, followScale, classId, m_cancel,
                                                    [&]() {
                                                        ++done;
                                                        progress(double(done) / qMax(1, total),
                                                                 tr("Following frame %1 of %2…").arg(done).arg(total));
                                                    });
            if (!run.error.isEmpty()) {
                fail(run.error);
                return;
            }
            samples = run.samples;
        }
        std::sort(samples.begin(), samples.end(), [](const Sample &a, const Sample &b) { return a.sourceUs < b.sourceUs; });

        drift::MotionTrack result;
        result.mode = faceMode ? QStringLiteral("face") : QStringLiteral("object");
        result.sourceClipId = video.id;
        result.sourcePath = video.path;
        result.faceSlot = slot;
        result.direction = direction;
        result.followScale = followScale;
        result.keepDistance = keepDistance;
        result.anchorSourceUs = video.timelineToSourceUs(t0);
        result.anchorTarget = anchorTarget;
        result.anchorElement = overlayRect0;
        result.anchorPixelSize = pixelSize0;
        result.samples = samples;

        QMetaObject::invokeMethod(this, [this, result, overlayId]() {
            setBusy(false);
            // Resolved by id: the timeline may have changed while the job ran.
            int trackIndex = -1, clipIndex = -1;
            const drift::Clip *video = nullptr;
            const QList<drift::Track> &tracks = m_app->m_project.tracks();
            for (int t = 0; t < tracks.size(); ++t) {
                for (int c = 0; c < tracks.at(t).clips.size(); ++c) {
                    const drift::Clip &clip = tracks.at(t).clips.at(c);
                    if (clip.id == overlayId) {
                        trackIndex = t;
                        clipIndex = c;
                    }
                    if (clip.id == result.sourceClipId)
                        video = &clip;
                }
            }
            if (trackIndex < 0 || !video) {
                emit finished(false, QString());
                return;
            }
            const drift::Clip videoCopy = *video;
            const drift::Project before = m_app->m_project;
            drift::Clip &clip = m_app->m_project.tracks()[trackIndex].clips[clipIndex];
            // Tracking again: the previous run's keys go, only those it wrote when it knows them.
            if (clip.motionTrack && clip.motionTrack->bakedFromUs >= 0)
                resetTrackedKeys(clip);
            clip.motionTrack = result;
            const drift::MotionBakeResult baked =
                drift::bakeMotionTrack(result, videoCopy, &clip, m_app->m_project.width(), m_app->m_project.height());
            rememberBake(clip, baked);
            if (!baked.ok) {
                m_app->m_project = before;
                const QString message = tr("Nothing to follow was found");
                m_status = message;
                emit statusChanged();
                m_app->setLastMessage(message, QStringLiteral("warning"));
                emit finished(false, message);
                return;
            }
            m_app->pushProjectEdit(before, tr("Motion tracking"));
            m_app->finishEdit(tr("Motion tracking"));
            const QString message = baked.lost > 0
                ? tr("Tracking done — lost the subject in %1 of %2 frames").arg(baked.lost).arg(baked.samples)
                : tr("Tracking done");
            m_progress = 1.0;
            emit progressChanged();
            m_status = message;
            emit statusChanged();
            m_app->setLastMessage(message, baked.lost > baked.samples / 3 ? QStringLiteral("warning")
                                                                          : QStringLiteral("success"));
            bump();
            emit finished(true, message);
        }, Qt::QueuedConnection);
    });
}
