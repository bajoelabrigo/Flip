#include "BodyController.h"

#include "AppController.h"
#include "core/Mask.h"
#include "core/TimelineOps.h"
#include "engine/BodyLandmarker.h"
#include "engine/ClipReaderPool.h"
#include "engine/EffectCatalog.h"
#include "engine/MatteWriter.h"
#include "engine/PoseTrack.h"
#include "engine/StillImage.h"

#include <QColor>
#include <QFile>
#include <QMetaObject>
#include <QUuid>
#include <QtConcurrent>

namespace {

// Its own decode cursor: sharing 0x0B with the cutout scrub and the motion tracker made each reseek
// the other on every frame when they ran together.
constexpr quint64 kBodyStreamId = 0xA5'11'5C'A4'00'00'00'0Cull;
const QString kHairEffectId = QStringLiteral("hair.color");

bool locateClip(const drift::Project &project, const QString &clipId, int *trackOut, int *clipOut)
{
    for (int t = 0; t < project.tracks().size(); ++t) {
        const drift::Track &track = project.tracks().at(t);
        for (int c = 0; c < track.clips.size(); ++c) {
            if (track.clips.at(c).id == clipId) {
                *trackOut = t;
                *clipOut = c;
                return true;
            }
        }
    }
    return false;
}

// The hair-colour adjustment pinned to a clip: a video-effects adjustment on one of its lanes
// carrying hair.color and the hair matte.
drift::ClipRef hairAdjustmentFor(const drift::Project &project, int trackIndex, const QString &clipId)
{
    for (const int laneIndex : drift::adjustmentLaneIndexes(project, trackIndex)) {
        const drift::Track &lane = project.tracks().at(laneIndex);
        for (int c = 0; c < lane.clips.size(); ++c) {
            const drift::Clip &adjustment = lane.clips.at(c);
            if (adjustment.adjustmentKind != drift::AdjustmentKind::VideoEffects
                || adjustment.linkedClipId != clipId)
                continue;
            for (const drift::Effect &effect : adjustment.effects) {
                if (effect.catalogId == kHairEffectId)
                    return {laneIndex, c};
            }
        }
    }
    return {};
}

int effectIndex(const drift::Clip &adjustment, const QString &catalogId)
{
    for (int i = 0; i < adjustment.effects.size(); ++i) {
        if (adjustment.effects.at(i).catalogId == catalogId)
            return i;
    }
    return -1;
}

} // namespace

BodyController::BodyController(AppController *app, QObject *parent)
    : QObject(parent)
    , m_app(app)
{
}

bool BodyController::available()
{
    return drift::BodyLandmarker::modelPresent();
}

void BodyController::cancel()
{
    if (m_running)
        m_cancel.storeRelaxed(1);
}

bool BodyController::begin(const QString &job, const QString &message)
{
    if (m_running) {
        m_app->setLastMessage(tr("Body analysis already in progress"), QStringLiteral("warning"));
        return false;
    }
    // Same reason as the face scan: playback would drive the decode pool from a second thread.
    m_app->setPlaying(false);
    m_cancel.storeRelaxed(0);
    m_progress = 0.0;
    emit progressChanged();
    m_status = tr("Getting ready…");
    emit statusChanged();
    m_job = job;
    m_running = true;
    emit runningChanged();
    m_app->setLastMessage(message);
    return true;
}

void BodyController::clearBody(int trackIndex, int clipIndex)
{
    const drift::ClipRef source = m_app->sourceClipRef(trackIndex, clipIndex);
    if (source.trackIndex < 0)
        return;
    drift::Clip &clip = m_app->m_project.tracks()[source.trackIndex].clips[source.clipIndex];
    if (clip.poseTrackPath.isEmpty())
        return;
    // The sidecar stays on disk so undo can bring it back.
    const drift::Project before = m_app->m_project;
    clip.poseTrackPath.clear();
    clip.poseTrackSrcOffsetUs = 0;
    m_app->pushProjectEdit(before, tr("Clear body analysis"));
    m_app->finishEdit(tr("Clear body analysis"));
}

void BodyController::analyzeBody(int trackIndex, int clipIndex)
{
    // Asked from the effect adjustment's inspector as often as from the clip: the pose belongs on
    // the clip the adjustment is pinned to.
    const drift::ClipRef source = m_app->sourceClipRef(trackIndex, clipIndex);
    if (source.trackIndex < 0)
        return;
    const drift::Clip clip = m_app->m_project.tracks().at(source.trackIndex).clips.at(source.clipIndex);
    if (clip.type != drift::ClipType::Video && clip.type != drift::ClipType::Image) {
        m_app->setLastMessage(tr("Select a video or image clip"), QStringLiteral("warning"));
        return;
    }
    if (clip.path.isEmpty() || clip.srcOut <= clip.srcIn) {
        m_app->setLastMessage(tr("This clip has no picture to analyse"), QStringLiteral("warning"));
        return;
    }
    if (!begin(QStringLiteral("body"), tr("Analysing the body…")))
        return;

    const QString path = clip.path;
    // A still is one frame however long it stays on screen; PoseTrack::sample clamps to it.
    const bool still = clip.type == drift::ClipType::Image;
    const drift::TimeUs srcIn = still ? 0 : clip.srcIn;
    const drift::TimeUs srcOut = still ? 1 : clip.srcOut;
    const int fps = qMax(1, m_app->m_project.fps());
    const int canvasW = m_app->m_project.width();
    const int canvasH = m_app->m_project.height();
    const QString clipId = clip.id;
    const int rotationCorrection = clip.rotationCorrection;

    (void)QtConcurrent::run([this, path, still, srcIn, srcOut, fps, canvasW, canvasH, clipId,
                             rotationCorrection]() {
        auto setProgress = [this](double fraction, const QString &status) {
            QMetaObject::invokeMethod(this, [this, fraction, status]() {
                m_progress = fraction;
                emit progressChanged();
                if (status != m_status) {
                    m_status = status;
                    emit statusChanged();
                }
            }, Qt::QueuedConnection);
        };
        auto finish = [this, clipId, srcIn](bool ok, const QString &message, const QString &trackPath) {
            QMetaObject::invokeMethod(this, [this, ok, message, trackPath, clipId, srcIn]() {
                m_running = false;
                m_job.clear();
                emit runningChanged();
                m_progress = ok ? 1.0 : 0.0;
                emit progressChanged();
                m_status = ok ? tr("Done") : message;
                emit statusChanged();
                if (!ok) {
                    m_app->setLastMessage(message, QStringLiteral("error"));
                    emit finished(false, message);
                    return;
                }
                finalizeBody(clipId, trackPath, srcIn);
                m_app->setLastMessage(message);
                emit finished(true, message);
            }, Qt::QueuedConnection);
        };

        drift::BodyLandmarker &landmarker = drift::BodyLandmarker::instance();
        if (!landmarker.available()) {
            finish(false, landmarker.lastError(), {});
            return;
        }
        const drift::TimeUs step = drift::kUsPerSecond / fps;
        const int totalFrames = int((srcOut - srcIn + step - 1) / step);
        if (totalFrames <= 0) {
            finish(false, tr("Clip is too short to analyse"), {});
            return;
        }

        drift::PoseTrack poseTrack;
        poseTrack.fps = fps;
        poseTrack.startSrcUs = srcIn;
        poseTrack.frames.reserve(totalFrames);
        drift::BodyPose previous;
        int framesWithBody = 0;
        for (int i = 0; i < totalFrames; ++i) {
            if (m_cancel.loadRelaxed() != 0) {
                finish(false, tr("Body analysis cancelled"), {});
                return;
            }
            const drift::TimeUs sourceUs = srcIn + drift::TimeUs(i) * step;
            const QImage frame = still
                ? drift::decodeStillImage(path, canvasW, canvasH)
                : ClipReaderPool::instance().readVideoFrame(path, kBodyStreamId, sourceUs, canvasW,
                                                            canvasH, rotationCorrection);
            if (frame.isNull()) {
                finish(false, tr("Could not decode frame %1").arg(i), {});
                return;
            }
            const drift::BodyPose pose = landmarker.detect(frame, previous.valid ? &previous : nullptr);
            previous = pose;
            poseTrack.frames.append(pose);
            if (pose.valid)
                ++framesWithBody;
            setProgress(double(i + 1) / totalFrames,
                        tr("Analysing frame %1 of %2…").arg(i + 1).arg(totalFrames));
        }
        if (framesWithBody == 0) {
            finish(false, tr("No person found in this clip"), {});
            return;
        }
        drift::smoothPoseTrack(&poseTrack);

        const QString trackPath = drift::newPoseTrackPath();
        QString error;
        if (trackPath.isEmpty() || !drift::writePoseTrack(trackPath, poseTrack, &error)) {
            finish(false, error.isEmpty() ? tr("Could not write the body analysis") : error, {});
            return;
        }
        finish(true,
               framesWithBody < totalFrames
                   ? tr("Body analysis complete — a person was visible in %1 of %2 frames")
                         .arg(framesWithBody)
                         .arg(totalFrames)
                   : tr("Body analysis complete"),
               trackPath);
    });
}

void BodyController::finalizeBody(const QString &clipId, const QString &trackPath,
                                  drift::TimeUs srcOffsetUs)
{
    int trackIndex = -1;
    int clipIndex = -1;
    if (!locateClip(m_app->m_project, clipId, &trackIndex, &clipIndex)) {
        QFile::remove(trackPath);
        m_app->setLastMessage(tr("That clip no longer exists"), QStringLiteral("warning"));
        return;
    }
    const drift::Project before = m_app->m_project;
    drift::Clip &clip = m_app->m_project.tracks()[trackIndex].clips[clipIndex];
    clip.poseTrackPath = trackPath;
    clip.poseTrackSrcOffsetUs = srcOffsetUs;
    m_app->pushProjectEdit(before, tr("Analyse body"));
    m_app->finishEdit(tr("Analyse body"));
    m_app->emitPreviewFrame();
}

QVariantMap BodyController::hairColor(int trackIndex, int clipIndex) const
{
    const drift::ClipRef source = m_app->sourceClipRef(trackIndex, clipIndex);
    if (source.trackIndex < 0)
        return {};
    const drift::Clip &clip = m_app->m_project.tracks().at(source.trackIndex).clips.at(source.clipIndex);
    const drift::ClipRef hair = hairAdjustmentFor(m_app->m_project, source.trackIndex, clip.id);
    if (hair.trackIndex < 0)
        return {};
    const drift::Clip &adjustment = m_app->m_project.tracks().at(hair.trackIndex).clips.at(hair.clipIndex);
    const int index = effectIndex(adjustment, kHairEffectId);
    const drift::Effect &effect = adjustment.effects.at(index);
    return {
        {QStringLiteral("trackIndex"), hair.trackIndex},
        {QStringLiteral("clipIndex"), hair.clipIndex},
        {QStringLiteral("shade"), effect.parameters.value(QStringLiteral("shade")).toString()},
        {QStringLiteral("strength"), effect.parameters.value(QStringLiteral("strength")).toDouble()},
    };
}

void BodyController::removeHairColor(int trackIndex, int clipIndex)
{
    const drift::ClipRef source = m_app->sourceClipRef(trackIndex, clipIndex);
    if (source.trackIndex < 0)
        return;
    const QString clipId = m_app->m_project.tracks().at(source.trackIndex).clips.at(source.clipIndex).id;
    const drift::ClipRef hair = hairAdjustmentFor(m_app->m_project, source.trackIndex, clipId);
    if (hair.trackIndex < 0)
        return;
    const drift::Project before = m_app->m_project;
    m_app->m_project.tracks()[hair.trackIndex].clips.removeAt(hair.clipIndex);
    m_app->pushProjectEdit(before, tr("Remove hair colour"));
    m_app->finishEdit(tr("Remove hair colour"));
    int t = -1;
    int c = -1;
    if (locateClip(m_app->m_project, clipId, &t, &c))
        m_app->selectClip(t, c);
}

void BodyController::colorHair(int trackIndex, int clipIndex, const QString &shade)
{
    const drift::ClipRef source = m_app->sourceClipRef(trackIndex, clipIndex);
    if (source.trackIndex < 0)
        return;
    const drift::Clip clip = m_app->m_project.tracks().at(source.trackIndex).clips.at(source.clipIndex);
    const QString hex = QColor(shade).isValid() ? QColor(shade).name() : QStringLiteral("#8a4a2a");

    // Already coloured: only the shade changes, no second scan.
    const drift::ClipRef existing = hairAdjustmentFor(m_app->m_project, source.trackIndex, clip.id);
    if (existing.trackIndex >= 0) {
        const drift::Project before = m_app->m_project;
        drift::Clip &adjustment = m_app->m_project.tracks()[existing.trackIndex].clips[existing.clipIndex];
        adjustment.effects[effectIndex(adjustment, kHairEffectId)].parameters.insert(QStringLiteral("shade"), hex);
        m_app->pushProjectEdit(before, tr("Hair colour"));
        m_app->finishEdit(tr("Hair colour"));
        return;
    }

    if (clip.type != drift::ClipType::Video && clip.type != drift::ClipType::Image) {
        m_app->setLastMessage(tr("Select a video or image clip"), QStringLiteral("warning"));
        return;
    }
    const bool still = clip.type == drift::ClipType::Image;
    if (clip.path.isEmpty() || (!still && clip.srcOut <= clip.srcIn)) {
        m_app->setLastMessage(tr("This clip has no picture to analyse"), QStringLiteral("warning"));
        return;
    }
    if (!effectDefForId(kHairEffectId)) {
        m_app->setLastMessage(tr("The hair colour effect is missing"), QStringLiteral("error"));
        return;
    }
    if (!begin(QStringLiteral("hair"), tr("Finding the hair…")))
        return;

    const QString path = clip.path;
    // Like a cutout, the matte covers as long as a photo is on screen.
    const drift::TimeUs srcIn = clip.srcIn;
    const drift::TimeUs srcOut = still ? clip.srcIn + clip.timelineDuration : clip.srcOut;
    const int fps = qMax(1, m_app->m_project.fps());
    const int canvasW = m_app->m_project.width();
    const int canvasH = m_app->m_project.height();
    const QString clipId = clip.id;
    const int rotationCorrection = clip.rotationCorrection;

    (void)QtConcurrent::run([this, path, still, srcIn, srcOut, fps, canvasW, canvasH, clipId,
                             rotationCorrection, hex]() {
        auto setProgress = [this](double fraction, const QString &status) {
            QMetaObject::invokeMethod(this, [this, fraction, status]() {
                m_progress = fraction;
                emit progressChanged();
                if (status != m_status) {
                    m_status = status;
                    emit statusChanged();
                }
            }, Qt::QueuedConnection);
        };
        auto finish = [this, clipId, srcIn, hex](bool ok, const QString &message, const QString &mattePath) {
            QMetaObject::invokeMethod(this, [this, ok, message, mattePath, clipId, srcIn, hex]() {
                m_running = false;
                m_job.clear();
                emit runningChanged();
                m_progress = ok ? 1.0 : 0.0;
                emit progressChanged();
                m_status = ok ? tr("Done") : message;
                emit statusChanged();
                if (!ok) {
                    m_app->setLastMessage(message, QStringLiteral("error"));
                    emit finished(false, message);
                    return;
                }
                finalizeHair(clipId, mattePath, srcIn, hex);
                m_app->setLastMessage(message);
                emit finished(true, message);
            }, Qt::QueuedConnection);
        };

        drift::BodyLandmarker &landmarker = drift::BodyLandmarker::instance();
        if (!landmarker.available()) {
            finish(false, landmarker.lastError(), {});
            return;
        }
        const drift::TimeUs step = drift::kUsPerSecond / fps;
        const int totalFrames = int((srcOut - srcIn + step - 1) / step);
        if (totalFrames <= 0) {
            finish(false, tr("Clip is too short to analyse"), {});
            return;
        }
        const QString mattePath = drift::newMattePath();
        if (mattePath.isEmpty()) {
            finish(false, tr("Could not create a hair matte file"), {});
            return;
        }

        drift::MatteWriter writer;
        bool writerOpen = false;
        QString error;
        drift::BodyPose previous;
        QImage stillCoverage;
        int framesWithHair = 0;
        for (int i = 0; i < totalFrames; ++i) {
            if (m_cancel.loadRelaxed() != 0) {
                writer.abort();
                finish(false, tr("Hair analysis cancelled"), {});
                return;
            }
            QImage coverage = stillCoverage;
            QImage frame;
            if (coverage.isNull()) {
                const drift::TimeUs sourceUs = srcIn + drift::TimeUs(i) * step;
                frame = still ? drift::decodeStillImage(path, canvasW, canvasH)
                              : ClipReaderPool::instance().readVideoFrame(
                                    path, kBodyStreamId, sourceUs, canvasW, canvasH, rotationCorrection);
                if (frame.isNull()) {
                    writer.abort();
                    finish(false, tr("Could not decode frame %1").arg(i), {});
                    return;
                }
                // The pose places the square the segmenter looks at, and follows the person.
                const drift::BodyPose pose = landmarker.detect(frame, previous.valid ? &previous : nullptr);
                previous = pose;
                coverage = landmarker.hairCoverage(frame, pose);
                if (coverage.isNull()) {
                    writer.abort();
                    finish(false, landmarker.lastError(), {});
                    return;
                }
                if (still)
                    stillCoverage = coverage;
            }
            if (!writerOpen) {
                if (!writer.open(mattePath, coverage.size(), fps, 1, &error)) {
                    finish(false, error, {});
                    return;
                }
                writerOpen = true;
            }
            if (!writer.writeFrame(coverage, &error)) {
                writer.abort();
                finish(false, error, {});
                return;
            }
            if (i == 0 || !still) {
                // Counted on a coarse grid: a frame "has hair" when a few hundred pixels do.
                int lit = 0;
                for (int y = 0; y < coverage.height() && lit < 200; y += 4) {
                    const uchar *row = coverage.constScanLine(y);
                    for (int x = 0; x < coverage.width(); x += 4)
                        lit += row[x] > 127 ? 1 : 0;
                }
                if (lit >= 20)
                    ++framesWithHair;
            }
            setProgress(double(i + 1) / totalFrames,
                        tr("Analysing frame %1 of %2…").arg(i + 1).arg(totalFrames));
        }
        if (!writer.finish(&error)) {
            writer.abort();
            finish(false, error, {});
            return;
        }
        if (framesWithHair == 0) {
            QFile::remove(mattePath);
            finish(false, tr("No hair found in this clip"), {});
            return;
        }
        finish(true, tr("Hair colour applied"), mattePath);
    });
}

void BodyController::finalizeHair(const QString &clipId, const QString &mattePath,
                                  drift::TimeUs srcOffsetUs, const QString &shade)
{
    int trackIndex = -1;
    int clipIndex = -1;
    if (!locateClip(m_app->m_project, clipId, &trackIndex, &clipIndex)) {
        QFile::remove(mattePath);
        m_app->setLastMessage(tr("That clip no longer exists"), QStringLiteral("warning"));
        return;
    }
    const EffectPresetEntry *def = effectDefForId(kHairEffectId);
    if (!def) {
        QFile::remove(mattePath);
        return;
    }

    m_app->m_project.ensureTrackIds();
    const drift::Project before = m_app->m_project;
    const drift::Clip host = m_app->m_project.tracks().at(trackIndex).clips.at(clipIndex);

    drift::Effect effect;
    effect.name = def->filterName;
    effect.catalogId = def->meta.id;
    for (auto it = def->fixedParams.constBegin(); it != def->fixedParams.constEnd(); ++it)
        effect.parameters.insert(it.key(), it.value());
    for (const drift::EffectParamSpec &p : def->meta.parameters)
        p.insertDefault(effect.parameters);
    effect.parameters.insert(QStringLiteral("shade"), shade);

    // Its own adjustment, pinned to the clip and masked by the hair: the colour lands on the hair
    // only, shows on the timeline as one row, and deleting that row takes it all back.
    drift::Clip adjustment;
    adjustment.id = QUuid::createUuid().toString(QUuid::WithoutBraces);
    adjustment.type = drift::ClipType::Adjustment;
    adjustment.adjustmentKind = drift::AdjustmentKind::VideoEffects;
    adjustment.linkedClipId = host.id;
    adjustment.timelineStart = host.timelineStart;
    adjustment.timelineDuration = host.timelineDuration;
    adjustment.srcIn = 0;
    adjustment.srcOut = host.timelineDuration;
    adjustment.name = tr("Hair colour");
    drift::Mask matte = drift::fullFrameMediaMask(mattePath, srcOffsetUs);
    matte.name = tr("Hair");
    adjustment.mask = matte;
    adjustment.effects.append(effect);

    const int laneIndex = drift::ensureAdjustmentLane(m_app->m_project, trackIndex,
                                                      drift::AdjustmentKind::VideoEffects,
                                                      adjustment.timelineStart,
                                                      adjustment.timelineDuration);
    if (laneIndex < 0) {
        QFile::remove(mattePath);
        m_app->setLastMessage(tr("This clip cannot take an adjustment"), QStringLiteral("warning"));
        return;
    }
    m_app->m_project.tracks()[laneIndex].clips.append(adjustment);
    m_app->pushProjectEdit(before, tr("Hair colour"));
    m_app->finishEdit(tr("Hair colour"));

    // The lane insert moved indices. The clip stays selected, so the next swatch is one click.
    int t = -1;
    int c = -1;
    if (locateClip(m_app->m_project, clipId, &t, &c))
        m_app->selectClip(t, c);
}
