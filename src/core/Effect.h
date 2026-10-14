#pragma once

#include "Keyframe.h"
#include "Time.h"

#include <QJsonArray>
#include <QJsonObject>
#include <QList>
#include <QMap>
#include <QString>
#include <QVariant>

namespace drift {

// Marks an effect an effect template put on a clip, with what is needed to rebuild its pulses
// (intensity, decay, rhythm) or take the whole template off again. Every effect of one application
// carries the same `instance`; the tag rides along when hoisting moves the effects onto the clip's
// linked adjustment, where a list stored on the clip itself would be left behind.
struct EffectTemplateTag
{
    QString templateId;
    QString instance;
    // Index into the template's `layers`: which pulse rule this effect follows.
    int layer = -1;
    // "onset", "beat", "bar" or "clip".
    QString sync;
    // Pulse height relative to the template's (1 = as designed), and decay length likewise.
    double intensity = 1.0;
    double decay = 1.0;
    // Pulse times, relative to the start of the clip the template was applied to.
    QList<TimeUs> points;
    // The template also wrote a speed curve on that clip, to undo with the template.
    bool speedApplied = false;

    bool isValid() const { return !instance.isEmpty(); }
    bool operator==(const EffectTemplateTag &) const = default;
};

// Per-clip libavfilter effect with named parameters.
struct Effect
{
    QString name;
    QMap<QString, QVariant> parameters;

    // Params with a non-empty track are animated: the track wins over `parameters` at
    // render time. `parameters` still holds the last static value, so clearing a track
    // returns the param to a constant rather than to the catalog default.
    QMap<QString, KeyframeTrack<double>> paramKeyframes;

    // Id into the effect preset catalog (src/engine/EffectCatalog.h) this effect was
    // created from; UI-only bookkeeping so the inspector can show the right
    // label/sliders. Rendering uses catalog metadata in the engine layer.
    QString catalogId;

    // When false the effect stays on the clip (params/keyframes preserved) but is
    // skipped at render/mix time. Default true so older projects load as enabled.
    bool enabled = true;

    // Set when an effect template added this effect; empty otherwise.
    EffectTemplateTag templateTag;

    QString filterGraphString() const;

    // parameters[key], overridden by paramKeyframes[key] evaluated at clipTimeUs.
    QVariant valueAt(const QString &key, TimeUs clipTimeUs) const;

    // A copy with every animated param baked down to its value at clipTimeUs.
    Effect resolvedAt(TimeUs clipTimeUs) const;
};

QJsonObject keyframesToJson(const KeyframeTrack<double> &track);
// Also migrates the pre-tangent "interpolation" field older projects carry.
KeyframeTrack<double> keyframesFromJson(const QJsonObject &object);

QJsonArray effectsToJson(const QList<Effect> &effects);
QList<Effect> effectsFromJson(const QJsonArray &array);

// Moves every keyframe on `effects` off a clip of `fromDurationUs` and onto one of
// `toDurationUs`, keeping each key at the same fraction of the clip. This is what lets a stack
// copied from a two-second shot read the same way on a six-second one.
void rescaleEffectKeyframes(QList<Effect> &effects, TimeUs fromDurationUs, TimeUs toDurationUs);

} // namespace drift
