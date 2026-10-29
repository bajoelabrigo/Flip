#pragma once

#include "ClipAnimationPreset.h"

#include <QJsonObject>
#include <QList>
#include <QMap>
#include <QString>

#include <optional>

// Squash & Stretch animations (0.26, Jorge): rubbery cartoon motion in the manner of the
// Squash & Stretch Pro script for After Effects, designed by us (presets/squash-animations/*.json).
// Applying one writes keyframes on the clip, so they can be edited as any others: position (a
// fraction of the canvas), rotation (degrees), opacity (percent) and the "squash.deform" effect's
// zoom, stretch, groundWidth, farWidth, shear, bend and bulge (percent). The curves run over the
// animation's progress (0 → 1).
namespace drift {

enum class SquashPlace { Start, End, Playhead };

struct SquashAnimation
{
    QString id;
    QString label;
    // in, out, moves, jumps, highlights, rotations, wiggles, glitch
    QString category;
    int order = 100;
    double seconds = 1.0;
    // Where it lands: the clip's start (In), its end (Out) or the playhead (the rest).
    SquashPlace place = SquashPlace::Playhead;
    // The edge that stays put while it squashes, in % from the top (100 = the bottom).
    double ground = 100.0;
    // "x", "y", "rotation", "opacity" and the deformer's channels
    QMap<QString, ClipAnimTrack> tracks;

    static std::optional<SquashAnimation> fromJson(const QJsonObject &o, QString *error = nullptr);
};

class SquashAnimationCatalog
{
public:
    static SquashAnimationCatalog &instance();

    QList<SquashAnimation> animations() const;
    std::optional<SquashAnimation> animationForId(const QString &id) const;

private:
    SquashAnimationCatalog() = default;
    void ensureLoaded() const;

    mutable bool m_loaded = false;
    mutable QList<SquashAnimation> m_animations;
};

} // namespace drift
