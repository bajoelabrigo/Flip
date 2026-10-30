#pragma once

#include <QJsonObject>
#include <QList>
#include <QMap>
#include <QString>
#include <QStringList>

#include <optional>

// Clip animation presets: JSON recipes (presets/clip-animations/*.json) for Video › Animation's
// In, Out and Combo galleries, the way Filmora and CapCut ship theirs. A preset is a set of
// curves over the slot's progress (0 → 1) for the clip's offset, scale, turn, turn in depth,
// opacity and blur, plus catalog effects whose parameters follow curves of their own (a zoom blur,
// an RGB split). In runs from away to in place, Out from in place to away, Combo is one motion
// that does both. Lengths are fractions of the clip's own box; blur is in pixels of a 1080 frame.

namespace drift {

struct ClipAnimSample;

enum class ClipAnimSlot { In, Out, Combo };
QString clipAnimSlotToString(ClipAnimSlot slot);
ClipAnimSlot clipAnimSlotFromString(const QString &slot);

// Easing of the segment that starts at a key.
enum class ClipAnimKeyEase { Linear, EaseIn, EaseOut, EaseInOut, Back, BackIn, Elastic, Bounce, Hold };

struct ClipAnimKey
{
    double t = 0.0; // progress 0..1
    double v = 0.0;
    ClipAnimKeyEase ease = ClipAnimKeyEase::EaseInOut;
};

struct ClipAnimTrack
{
    QList<ClipAnimKey> keys;

    bool isEmpty() const { return keys.isEmpty(); }
    double at(double progress, double fallback) const;
    double maxAbs() const;
};

struct ClipAnimPresetEffect
{
    QString effectId;                     // catalog folder name, e.g. "rgb_split"
    QMap<QString, ClipAnimTrack> params;  // uniform name → curve
    QMap<QString, double> fixed;          // uniform name → constant
};

struct ClipAnimationPreset
{
    QString id;
    QString label;
    QString category;
    QList<ClipAnimSlot> slotKinds;
    int order = 100;
    bool trending = false;
    double defaultSeconds = 0.6; // Combo: 0 = the whole clip

    ClipAnimTrack x, y;              // fraction of the box, + right / + down
    ClipAnimTrack scale;             // percent
    ClipAnimTrack scaleX, scaleY;    // percent, on top of scale
    ClipAnimTrack rotation;          // degrees, clockwise
    ClipAnimTrack rotationX;         // degrees, + tips the top edge away
    ClipAnimTrack rotationY;         // degrees, + swings the right edge away
    ClipAnimTrack opacity;           // percent
    ClipAnimTrack blur;              // px of a 1080 frame
    QList<ClipAnimPresetEffect> effects;

    bool supportsSlot(ClipAnimSlot slot) const { return slotKinds.contains(slot); }
    static std::optional<ClipAnimationPreset> fromJson(const QJsonObject &o, QString *error = nullptr);
};

class ClipAnimationPresetCatalog
{
public:
    static ClipAnimationPresetCatalog &instance();

    QList<ClipAnimationPreset> presets() const;
    QList<ClipAnimationPreset> presetsFor(ClipAnimSlot slot) const;
    std::optional<ClipAnimationPreset> presetForId(const QString &id) const;

    // Built-in resources, then $DRIFT_CLIP_ANIMATIONS (';' or ':'-separated dirs); later ids win.
    void reload();

private:
    ClipAnimationPresetCatalog() = default;
    void ensureLoaded() const;
    void loadDir(const QString &dir) const;

    mutable bool m_loaded = false;
    mutable QList<ClipAnimationPreset> m_presets;
};

// [[t, v, "ease"], …], [{"t","v","ease"}, …] or a bare number (constant); the Squash & Stretch
// animations (0.26) write their curves the same way.
ClipAnimTrack clipAnimTrackFromJson(const QJsonValue &v);

// Adds the preset's pose at `progress` to `sample`. `boxW` / `boxH` are the clip's box in render
// px; `shortSidePx` scales the 1080-frame blur.
void applyClipAnimationPreset(const ClipAnimationPreset &preset, double progress, double boxW, double boxH,
                              double shortSidePx, ClipAnimSample *sample);

} // namespace drift
