#pragma once

#include "Time.h"

#include <QJsonObject>
#include <QList>
#include <QRectF>
#include <QString>

#include <optional>

namespace drift {

struct Clip;

// What motion tracking found, kept on the clip that follows (a text, sticker, picture…) so the
// result can be baked again without analysing the video: when Scale or Distance is switched, or
// when the followed video is moved, trimmed or sped up after tracking. The baked keyframes stay the
// clip's real animation, so preview and export need nothing else.
//
// Samples are in the followed video's source time and in coordinates normalized to its source
// frame (0..1), which is what survives edits to the timeline.
struct MotionTrackSample
{
    enum class State : quint8 { Tracked, Lost, Recovered };

    TimeUs sourceUs = 0;
    QRectF rect;        // normalized to the source frame; the last trusted one while lost
    double score = 0.0; // confidence, 0..1
    State state = State::Tracked;
};

struct MotionTrack
{
    static constexpr int kVersion = 1;

    QString mode;             // "object" or "face"
    QString sourceClipId;     // the followed video clip
    QString sourcePath;       // its file at tracking time: a replaced file invalidates the samples
    int faceSlot = -1;        // face mode: which of the scanned faces
    QString direction = QStringLiteral("both"); // "both", "forward" or "backward" from the anchor
    bool followScale = false;
    // CapCut's "Distance": keep the element where it was against the target (on) or put its centre
    // on the target's (off).
    bool keepDistance = true;
    TimeUs anchorSourceUs = 0; // where tracking started, in the video's source time
    QRectF anchorTarget;       // the target there, normalized
    QRectF anchorElement;      // the element there, canvas pixels
    // A text's font size there: with followScale a text grows and shrinks its letters, not only
    // its box (resizing a text box rewraps the words, it does not scale them). 0 for anything else.
    double anchorPixelSize = 0.0;
    QList<MotionTrackSample> samples; // in source-time order

    bool isEmpty() const { return samples.isEmpty(); }
    int lostCount() const;
};

QJsonObject motionTrackToJson(const MotionTrack &track);
std::optional<MotionTrack> motionTrackFromJson(const QJsonObject &object);

struct MotionBakeResult
{
    int keys = 0;     // keyframes written per animated property
    int samples = 0;  // samples inside both clips
    int lost = 0;     // of those, not trusted
    bool ok = false;  // false when no trusted sample falls where the two clips overlap
};

// Writes `follower`'s position (and, with followScale, size) keyframes from `track`, mapping each
// sample through `video`'s current timing and layout. Replaces the keys over the tracked stretch
// only; anything animated before or after it is kept.
MotionBakeResult bakeMotionTrack(const MotionTrack &track, const Clip &video, Clip *follower, int projectW,
                                 int projectH);

// Face mode, frame by frame: which scanned face is the one being followed. `faces` holds one rect
// per slot (a null rect where the slot has no face this frame), `last` the followed face's last
// trusted rect. Keeps `current` while it stays near; takes another slot when that one is where the
// followed face was and `current` is gone or jumped (the scan swapped two people's slots); -1 when
// nothing is close enough, so the face is lost rather than swapped for someone else.
int followFaceSlot(const QList<QRectF> &faces, const QRectF &last, int current);

} // namespace drift
