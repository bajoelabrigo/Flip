#pragma once

#include "FadeShape.h"
#include "Time.h"

#include <QJsonObject>
#include <QList>
#include <QMap>
#include <QString>

namespace drift {

// CapCut-style body intro/outro for a whole clip (video/image/shape/text).
// Fade is one kind among slide/zoom/pop — same duration + style (curve) as the rest.
enum class ClipAnimKind {
    None,
    Fade,
    SlideUp,
    SlideDown,
    SlideLeft,
    SlideRight,
    ZoomIn,
    ZoomOut,
    Pop,
    SpinCW,
    SpinCCW,
    Bounce,
    Preset // ClipAnimation::presetId names a preset of presets/clip-animations
};

// Legacy ease names kept for project JSON compatibility. New UI uses FadeCurve.
enum class ClipAnimEase { Linear, EaseOut, EaseInOut, Back };

struct ClipAnimation
{
    ClipAnimKind kind = ClipAnimKind::None;
    QString presetId;           // kind == Preset
    TimeUs durationUs = 500000; // 0.5s; a Combo of 0 lasts the whole clip
    ClipAnimEase ease = ClipAnimEase::EaseOut; // legacy
    FadeCurve curve = FadeCurve::Smooth;
    FadeShape shape; // when curve == Custom
};

// A catalog effect a preset adds to the clip for this frame, with its parameters already sampled.
struct ClipAnimSampleEffect
{
    QString effectId;
    QMap<QString, double> params;
};

struct ClipAnimSample
{
    double opacity = 1.0;
    double dx = 0.0;
    double dy = 0.0;
    double scale = 1.0;
    double rotationDeg = 0.0;
    // Presets only: non-uniform scale, turn in depth, blur (render px) and effects.
    double scaleX = 1.0;
    double scaleY = 1.0;
    double rotationX = 0.0;
    double rotationY = 0.0;
    double blurPx = 0.0;
    QList<ClipAnimSampleEffect> effects;
};

QString clipAnimKindToString(ClipAnimKind kind);
ClipAnimKind clipAnimKindFromString(const QString &kind);

QString clipAnimEaseToString(ClipAnimEase ease);
ClipAnimEase clipAnimEaseFromString(const QString &ease);

FadeCurve clipAnimEaseToCurve(ClipAnimEase ease);
ClipAnimEase clipAnimCurveToEase(FadeCurve curve);

QJsonObject clipAnimationToJson(const ClipAnimation &anim);
ClipAnimation clipAnimationFromJson(const QJsonObject &object);

// Settled sample for the clip at `timelineUs`. `layoutW`/`layoutH` are canvas pixels
// (already render-scaled) so slide travel matches what the user sees.
// Fade kind is a no-op here — opacity comes from Clip::fadeMultiplier.
// `animCombo` is the one motion that both brings the clip in and takes it out (Combo).
ClipAnimSample evaluateClipAnimation(TimeUs timelineStart, TimeUs timelineDuration,
                                     const ClipAnimation &animIn, const ClipAnimation &animOut,
                                     TimeUs timelineUs, double layoutW, double layoutH,
                                     const ClipAnimation &animCombo = {});

inline bool clipAnimationActive(const ClipAnimation &anim)
{
    return anim.kind != ClipAnimKind::None && (anim.kind != ClipAnimKind::Preset || !anim.presetId.isEmpty());
}

} // namespace drift
