#pragma once

#include "engine/BodyLandmarker.h"
#include "core/Time.h"

#include <QList>
#include <QMap>
#include <QString>
#include <QVariant>

#include <memory>

namespace drift {

// A clip's body pose, baked once by Retouch › Body and replayed at composite time: the body
// counterpart of FaceTrack, with the same conventions. One person per frame (the most prominent);
// an invalid entry is a frame where no one was found.
struct PoseTrack
{
    int fps = 0;
    TimeUs startSrcUs = 0; // source time of frame 0, for diagnostics
    QList<BodyPose> frames;

    bool isEmpty() const { return frames.isEmpty(); }

    // `relativeUs` is source time from the start of the track (the caller has already subtracted
    // Clip::poseTrackSrcOffsetUs). Interpolates between the two frames around it, and is invalid
    // unless both are, so a person walking out of shot never leaves a half-way ghost pose.
    BodyPose sample(TimeUs relativeUs) const;
};

// A symmetric average over neighbouring frames, only across runs where the pose is continuously
// valid. Raw landmarks jitter a few pixels on a still body, and a warp anchored to them boils.
void smoothPoseTrack(PoseTrack *track, int radius = 3);

// One frame's pose as u_body* uniforms for a "requires": "pose" effect. Points stay in uv;
// u_bodyValid is 0 without a pose, which every body shader treats as pass-through, so an
// un-analysed clip renders untouched.
void applyPoseUniforms(QMap<QString, QVariant> *parameters, const BodyPose &pose);

// <AppDataLocation>/posetracks, created on demand. Mirrors faceTrackCacheDir().
QString poseTrackCacheDir();
QString newPoseTrackPath();

// Writes via a ".part" file and renames, so a cancelled bake never leaves a complete-looking file.
bool writePoseTrack(const QString &path, const PoseTrack &track, QString *errorOut);
bool readPoseTrack(const QString &path, PoseTrack *out, QString *errorOut);

// Parsed once and kept, keyed by path and modification time: the compositor calls this every
// frame. Null when the file is missing or malformed. Thread-safe.
std::shared_ptr<const PoseTrack> loadPoseTrackCached(const QString &path);

} // namespace drift
