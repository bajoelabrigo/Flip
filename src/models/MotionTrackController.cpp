#include "MotionTrackController.h"

#include "AppController.h"
#include "engine/ClipReaderPool.h"
#include "engine/FaceTrack.h"
#include "engine/RegionTracker.h"
#include "engine/StillImage.h"

#include <QMetaObject>
#include <QtConcurrent>

#include <algorithm>
#include <cmath>
#include <cstdlib>

namespace {

constexpr quint64 kMotionTrackStreamId = 0xA5'11'5C'A4'00'00'00'0Bull;
// Frames are decoded no bigger than this: the tracker works on a small grey copy anyway.
constexpr int kDecodeSide = 960;
// A key every this many frames: smooth enough to follow, few enough to retouch.
constexpr int kKeyEvery = 2;

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

struct Sample
{
    drift::TimeUs timelineUs = 0;
    QRectF rect; // normalized to the source frame
    bool lost = true;
};

} // namespace

MotionTrackController::MotionTrackController(AppController *app, QObject *parent)
    : QObject(parent)
    , m_app(app)
{
    // A face track asked for on the way to following a face: carry on once the scan lands.
    connect(m_app->faces(), &FaceTrackingController::finished, this, [this](bool ok, const QString &) {
        if (m_pendingFaceClipId.isEmpty())
            return;
        const QString overlayId = m_pendingFaceClipId;
        m_pendingFaceClipId.clear();
        if (!ok)
            return;
        const QList<drift::Track> &tracks = m_app->m_project.tracks();
        for (int t = 0; t < tracks.size(); ++t) {
            for (int c = 0; c < tracks.at(t).clips.size(); ++c) {
                if (tracks.at(t).clips.at(c).id == overlayId) {
                    track(t, c, QStringLiteral("face"), m_pendingFollowScale);
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
    out.insert(QStringLiteral("canScale"), clip.type != drift::ClipType::Text);
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
    m_app->pushProjectEdit(before, tr("Remove tracking"));
    m_app->finishEdit(tr("Remove tracking"));
    m_app->setLastMessage(tr("Tracking removed"), QStringLiteral("success"));
}

void MotionTrackController::track(int trackIndex, int clipIndex, const QString &mode, bool followScale)
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
    const bool faceMode = mode == QLatin1String("face");
    followScale = followScale && overlay.type != drift::ClipType::Text;

    if (faceMode && video.faceTrackPath.isEmpty()) {
        // Scan the faces first, then come back here (see the constructor).
        m_pendingFaceClipId = overlay.id;
        m_pendingFollowScale = followScale;
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
    const QRectF region((overlayRect0.x() - videoRect0.x()) / videoRect0.width(),
                        (overlayRect0.y() - videoRect0.y()) / videoRect0.height(),
                        overlayRect0.width() / videoRect0.width(), overlayRect0.height() / videoRect0.height());
    if (!faceMode && !region.intersects(QRectF(0, 0, 1, 1))) {
        m_app->setLastMessage(tr("Move the element over what it should follow"), QStringLiteral("warning"));
        return;
    }

    QList<drift::TimeUs> forward;
    for (drift::TimeUs t = t0; t < rangeEnd; t += step)
        forward.append(t);
    QList<drift::TimeUs> backward;
    for (drift::TimeUs t = t0 - step; t >= rangeStart; t -= step)
        backward.append(t);
    const int total = forward.size() + backward.size();

    m_app->setPlaying(false);
    m_cancel.storeRelaxed(0);
    m_progress = 0.0;
    emit progressChanged();
    m_status = tr("Getting ready…");
    emit statusChanged();
    setBusy(true);

    const QString overlayId = overlay.id;
    (void)QtConcurrent::run([this, video, region, faceMode, followScale, forward, backward, total, overlayId,
                             overlayRect0, projectW, projectH, t0]() {
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
        const auto frameAt = [&](drift::TimeUs timelineUs) {
            return still ? drift::decodeStillImage(video.path, kDecodeSide, kDecodeSide)
                         : ClipReaderPool::instance().readVideoFrame(video.path, kMotionTrackStreamId,
                                                                     video.timelineToSourceUs(timelineUs),
                                                                     kDecodeSide, kDecodeSide,
                                                                     video.rotationCorrection);
        };

        QList<Sample> samples;
        int done = 0;
        if (faceMode) {
            const std::shared_ptr<const drift::FaceTrack> faces = drift::loadFaceTrackCached(video.faceTrackPath);
            if (!faces || faces->isEmpty()) {
                fail(tr("The video has no scanned faces"));
                return;
            }
            QList<drift::TimeUs> all = backward;
            std::reverse(all.begin(), all.end());
            all += forward;
            for (const drift::TimeUs t : all) {
                const drift::FaceAnchors face =
                    faces->sample(video.timelineToSourceUs(t) - video.faceTrackSrcOffsetUs, 0);
                Sample s;
                s.timelineUs = t;
                s.lost = !face.valid;
                if (face.valid) {
                    const double rx = qMax(0.01, face.faceRx);
                    s.rect = QRectF(face.faceCenter.x() - rx, face.faceCenter.y() - rx, 2 * rx, 2 * rx);
                }
                samples.append(s);
            }
        } else {
            // Forward from the playhead, then backward from it again, each with its own tracker.
            for (int pass = 0; pass < 2; ++pass) {
                const QList<drift::TimeUs> &times = pass == 0 ? forward : backward;
                drift::RegionTracker tracker;
                if (!tracker.start(frameAt(t0), region)) {
                    fail(tr("Could not read the video at the playhead"));
                    return;
                }
                QList<Sample> pass_;
                for (const drift::TimeUs t : times) {
                    if (m_cancel.loadRelaxed() != 0) {
                        fail(tr("Tracking cancelled"));
                        return;
                    }
                    Sample s;
                    s.timelineUs = t;
                    if (pass == 0 && t == t0) {
                        s.rect = region;
                        s.lost = false;
                    } else {
                        const QImage frame = frameAt(t);
                        if (frame.isNull()) {
                            fail(tr("Could not decode the video"));
                            return;
                        }
                        const drift::RegionTracker::Result r = tracker.step(frame, followScale);
                        s.rect = r.rect;
                        s.lost = r.lost;
                    }
                    pass_.append(s);
                    ++done;
                    progress(double(done) / qMax(1, total), tr("Following frame %1 of %2…").arg(done).arg(total));
                }
                if (pass == 1)
                    std::reverse(pass_.begin(), pass_.end());
                samples = pass == 0 ? pass_ : pass_ + samples;
            }
        }

        QMetaObject::invokeMethod(this, [this, samples, overlayId, video, overlayRect0, followScale, projectW,
                                         projectH, t0]() {
            setBusy(false);
            // Resolved by id: the timeline may have changed while the job ran.
            int trackIndex = -1, clipIndex = -1;
            const QList<drift::Track> &tracks = m_app->m_project.tracks();
            for (int t = 0; t < tracks.size() && trackIndex < 0; ++t) {
                for (int c = 0; c < tracks.at(t).clips.size(); ++c) {
                    if (tracks.at(t).clips.at(c).id == overlayId) {
                        trackIndex = t;
                        clipIndex = c;
                        break;
                    }
                }
            }
            if (trackIndex < 0) {
                emit finished(false, QString());
                return;
            }

            // The reference: the tracked rect at the playhead, against the element there.
            const Sample *ref = nullptr;
            for (const Sample &s : samples) {
                if (!s.lost && (!ref || std::llabs(s.timelineUs - t0) < std::llabs(ref->timelineUs - t0)))
                    ref = &s;
            }
            if (!ref) {
                const QString message = tr("Nothing to follow was found");
                m_status = message;
                emit statusChanged();
                m_app->setLastMessage(message, QStringLiteral("warning"));
                emit finished(false, message);
                return;
            }
            const auto toCanvas = [&](const QRectF &n, drift::TimeUs t) {
                const QRectF v = canvasRect(video, t, projectW, projectH);
                return QRectF(v.x() + n.x() * v.width(), v.y() + n.y() * v.height(), n.width() * v.width(),
                              n.height() * v.height());
            };
            const QRectF ref0 = toCanvas(ref->rect, ref->timelineUs);
            const QPointF offset = overlayRect0.center() - ref0.center();

            // Centre and size per trusted sample, then a short moving average to take out the
            // sub-pixel shimmer of the match.
            struct Point { drift::TimeUs t; QPointF centre; double k; };
            QList<Point> points;
            for (const Sample &s : samples) {
                if (s.lost)
                    continue;
                const QRectF c = toCanvas(s.rect, s.timelineUs);
                const double k = followScale ? c.width() / qMax(1e-6, ref0.width()) : 1.0;
                points.append({s.timelineUs, c.center() + offset * k, k});
            }
            QList<Point> smooth = points;
            for (int i = 0; i < points.size(); ++i) {
                QPointF sum;
                double ks = 0.0;
                int n = 0;
                for (int j = qMax(0, i - 2); j <= qMin(int(points.size()) - 1, i + 2); ++j) {
                    sum += points.at(j).centre;
                    ks += points.at(j).k;
                    ++n;
                }
                smooth[i].centre = sum / n;
                smooth[i].k = ks / n;
            }

            const drift::Project before = m_app->m_project;
            drift::Clip &clip = m_app->m_project.tracks()[trackIndex].clips[clipIndex];
            const drift::TimeUs first = smooth.first().t - clip.timelineStart;
            const drift::TimeUs last = smooth.last().t - clip.timelineStart;
            const auto clearRange = [&](drift::KeyframeTrack<double> &track) {
                for (const drift::TimeUs time : track.keyframes().keys()) {
                    if (time >= first && time <= last)
                        track.removeKeyframe(time);
                }
            };
            clearRange(clip.transformX);
            clearRange(clip.transformY);
            if (followScale) {
                clearRange(clip.transformW);
                clearRange(clip.transformH);
            }
            int keys = 0;
            for (int i = 0; i < smooth.size(); ++i) {
                if (i % kKeyEvery != 0 && i != smooth.size() - 1)
                    continue;
                const Point &p = smooth.at(i);
                const double w = overlayRect0.width() * p.k;
                const double h = overlayRect0.height() * p.k;
                const drift::TimeUs rel = p.t - clip.timelineStart;
                clip.transformX.setKeyframe(rel, p.centre.x() - w * 0.5);
                clip.transformY.setKeyframe(rel, p.centre.y() - h * 0.5);
                if (followScale) {
                    clip.transformW.setKeyframe(rel, w);
                    clip.transformH.setKeyframe(rel, h);
                }
                ++keys;
            }
            m_app->pushProjectEdit(before, tr("Motion tracking"));
            m_app->finishEdit(tr("Motion tracking"));
            const int lost = int(samples.size() - points.size());
            const QString message = lost > 0
                ? tr("Tracking done — lost the subject in %1 of %2 frames").arg(lost).arg(samples.size())
                : tr("Tracking done");
            m_progress = 1.0;
            emit progressChanged();
            m_status = message;
            emit statusChanged();
            m_app->setLastMessage(message, lost > samples.size() / 3 ? QStringLiteral("warning")
                                                                    : QStringLiteral("success"));
            emit finished(true, message);
            Q_UNUSED(keys)
        }, Qt::QueuedConnection);
    });
}
