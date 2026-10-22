#include "MotionTrackController.h"

#include "AppController.h"
#include "core/MotionTrack.h"
#include "engine/ClipReaderPool.h"
#include "engine/FaceTrack.h"
#include "engine/ObjectDetector.h"
#include "engine/RegionTracker.h"
#include "engine/StillImage.h"

#include <QMetaObject>
#include <QUuid>
#include <QtConcurrent>

#include <algorithm>
#include <cmath>
#include <cstdlib>

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

// A re-bake owns the element's position (and, with Scale, size) animation: the old path may lie
// outside the new stretch once the video moved, so it is cleared rather than left to mix in.
void resetTrackedKeys(drift::Clip &clip)
{
    clip.transformX = drift::KeyframeTrack<double>{};
    clip.transformY = drift::KeyframeTrack<double>{};
    if (clip.motionTrack && clip.motionTrack->followScale) {
        clip.transformW = drift::KeyframeTrack<double>{};
        clip.transformH = drift::KeyframeTrack<double>{};
        clip.textStyle.keyframes.remove(QStringLiteral("pixelSize"));
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
    const drift::Clip *video = followedVideo(clip, trackIndex, clipIndex);
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
    if (selected < 0 || selected >= rects.size() || rects.at(selected).isNull()) {
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
    const Source source = sourceUnder(trackIndex, clipIndex, clip.containsTime(at) ? at : clip.timelineStart);
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
    const Source source = sourceUnder(trackIndex, clipIndex, at);
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
    const QString effectId = style == QLatin1String("blur") ? QStringLiteral("builtin.effects.gaussian_blur")
                                                            : QStringLiteral("stylize.pixelate");
    std::optional<drift::Effect> effect = m_app->effectWithDefaults(effectId);
    if (!effect)
        return;
    if (style == QLatin1String("blur"))
        effect->parameters.insert(QStringLiteral("u_blurRadius"), 40.0);

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
    std::sort(keys.begin(), keys.end(), [](const Key &a, const Key &b) { return a.t < b.t; });

    if (style != QLatin1String("blur")) {
        // Blocks sized to the face, about eight across it: small blocks still let a face be
        // recognised, and a fixed size meant a different look on every video.
        double faceWidth = 0.0;
        for (const Key &k : keys)
            faceWidth += k.r.width() * projectW / 1.35;
        const double block = qBound(14.0, faceWidth / keys.size() / 8.0, 64.0);
        effect->parameters.insert(QStringLiteral("width"), block);
        effect->parameters.insert(QStringLiteral("height"), block);
    }

    drift::Clip layer;
    layer.id = QUuid::createUuid().toString(QUuid::WithoutBraces);
    layer.type = drift::ClipType::Adjustment;
    layer.adjustmentKind = drift::AdjustmentKind::VideoEffects;
    layer.name = style == QLatin1String("blur") ? tr("Blurred face") : tr("Pixelated face");
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
    // A key every other frame, averaged over its neighbours: smooth, and few enough to retouch.
    for (int i = 0; i < keys.size(); ++i) {
        if (i % 2 != 0 && i != keys.size() - 1)
            continue;
        QPointF centre;
        QSizeF size;
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
    // Right above the video (track 0 is on top), so it hides the face on that clip and what is
    // under it, never on what was stacked over it.
    m_app->m_project.tracks().insert(trackIndex, layerTrack);
    m_app->pushProjectEdit(before, tr("Hide face"));
    m_app->finishEdit(tr("Hide face"));
    m_app->selectClip(trackIndex, 0);
    m_app->setLastMessage(tr("Face hidden: its layer is above the clip, where it can be trimmed or removed"),
                          QStringLiteral("success"));
    bump();
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
    resetTrackedKeys(clip);
    const drift::MotionBakeResult baked = drift::bakeMotionTrack(*clip.motionTrack, videoCopy, &clip,
                                                                 m_app->m_project.width(), m_app->m_project.height());
    if (!baked.ok) {
        m_app->m_project = before;
        m_app->setLastMessage(tr("The element and the tracked part of the video no longer overlap"),
                              QStringLiteral("warning"));
        return false;
    }
    m_app->pushProjectEdit(before, undoText);
    m_app->finishEdit(undoText);
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
    resetTrackedKeys(clip);
    const drift::MotionBakeResult baked = drift::bakeMotionTrack(*clip.motionTrack, videoCopy, &clip,
                                                                 m_app->m_project.width(), m_app->m_project.height());
    if (!baked.ok) {
        m_app->m_project = before;
        return false;
    }
    m_app->pushProjectEdit(before, tr("Tracking settings"));
    m_app->finishEdit(tr("Tracking settings"));
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

        const bool still = video.type == drift::ClipType::Image;
        // A picked object of a known class is looked for again by the detector once lost.
        const bool redetect = classId >= 0 && drift::ObjectDetector::instance().available();
        const auto frameAt = [&](drift::TimeUs timelineUs) {
            return still ? drift::decodeStillImage(video.path, kDecodeSide, kDecodeSide)
                         : ClipReaderPool::instance().readVideoFrame(video.path, kMotionTrackStreamId,
                                                                     video.timelineToSourceUs(timelineUs),
                                                                     kDecodeSide, kDecodeSide,
                                                                     video.rotationCorrection);
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
            // Forward from the playhead, then backward from it again, each with its own tracker.
            for (int pass = 0; pass < 2; ++pass) {
                const QList<drift::TimeUs> &times = pass == 0 ? forward : backward;
                if (times.isEmpty())
                    continue;
                drift::RegionTracker tracker;
                if (!tracker.start(frameAt(t0), region)) {
                    fail(tr("Could not read the video at the playhead"));
                    return;
                }
                QRectF lastTrusted = region;
                int lostRun = 0;
                for (const drift::TimeUs t : times) {
                    if (m_cancel.loadRelaxed() != 0) {
                        fail(tr("Tracking cancelled"));
                        return;
                    }
                    Sample s;
                    s.sourceUs = video.timelineToSourceUs(t);
                    if (pass == 0 && t == t0) {
                        s.rect = region;
                        s.score = 1.0;
                    } else {
                        const QImage frame = frameAt(t);
                        if (frame.isNull()) {
                            fail(tr("Could not decode the video"));
                            return;
                        }
                        const drift::RegionTracker::Result r = tracker.step(frame, followScale);
                        s.rect = r.rect;
                        s.score = qBound(0.0, r.score, 1.0);
                        s.state = r.lost ? Sample::State::Lost
                                         : (r.recovered ? Sample::State::Recovered : Sample::State::Tracked);
                        if (r.lost) {
                            ++lostRun;
                            // The detector costs tens of milliseconds: on the first lost frame, then
                            // every fifth, which still picks the subject up within a fraction of a second.
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
                    samples.append(s);
                    ++done;
                    progress(double(done) / qMax(1, total), tr("Following frame %1 of %2…").arg(done).arg(total));
                }
            }
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
            clip.motionTrack = result;
            const drift::MotionBakeResult baked =
                drift::bakeMotionTrack(result, videoCopy, &clip, m_app->m_project.width(), m_app->m_project.height());
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
