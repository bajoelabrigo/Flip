#pragma once

#include "core/BlendMode.h"
#include "core/TextShading.h"

#include <QRectF>

#include "include/core/SkBlendMode.h"
#include "include/core/SkPaint.h"
#include "include/core/SkPathEffect.h"
#include "include/core/SkRefCnt.h"

class SkCanvas;

// The shading stack in Skia form, shared by the text and shape painters so a stroke, a shadow
// blur or a gradient reads the same on both. Skia-including header: only Skia*.cpp may include it.

namespace drift::skia {

SkBlendMode toSkBlendMode(BlendMode mode);

// A stroke layer's Line Cap and Line Join (0.26).
inline SkPaint::Cap skStrokeCap(StrokeCap cap)
{
    return cap == StrokeCap::Butt ? SkPaint::kButt_Cap : cap == StrokeCap::Square ? SkPaint::kSquare_Cap
                                                                                  : SkPaint::kRound_Cap;
}
inline SkPaint::Join skStrokeJoin(StrokeJoin join)
{
    return join == StrokeJoin::Miter ? SkPaint::kMiter_Join : join == StrokeJoin::Bevel ? SkPaint::kBevel_Join
                                                                                        : SkPaint::kRound_Join;
}

// The layer's own paint source — solid, gradient over `box`, texture or shader effect — into
// `paint`, with `alpha` folded into the colour. A texture or effect that fails to build falls
// back to the tint. `progress` feeds progress-driven effects (a text wipe); -1 when there is none.
void applyShadingPaint(SkPaint &paint, const TextPaint &source, const QRectF &box, double timeSec, double alpha,
                       double progress = -1.0);

// Dash → sketch, composed inner-to-outer so the dash runs along the (already trimmed) outline and the
// jitter is applied last. Null when none applies. `strokeWidthPx` scales the dash pattern and
// offset; `scale` the sketch lengths. The write-on trim is strokedPathFor's.
sk_sp<SkPathEffect> strokePathEffectFor(const TextShadingLayer &layer, double strokeWidthPx, double scale);
// After Effects' Trim Paths with "Trim Multiple Shapes: Simultaneously" (its default, 0.26): each
// contour is cut from `start` to `end` (fractions of its own length; past 1 wraps round to its
// start), so every letter of a text draws on at once instead of one after the other.
// With `segments` > 1 each contour is cut into that many equal stretches, all trimmed alike.
SkPath trimEachContour(const SkPath &path, double start, double end, int segments = 1);
// The outline a stroke layer draws: trimmed by its write-on, else as it is.
SkPath strokedPathFor(const TextShadingLayer &layer, const SkPath &path);
// The sketch jitter on a fill outline; null when off.
sk_sp<SkPathEffect> fillPathEffectFor(const TextShadingLayer &layer, double scale);

// Wraps the layer's draws in a saveLayer when its opacity, blend, knockout, spread or blur asks
// for one. Blur is left out for strokes and extrudes, which draw sharp. Every begin is matched by
// an end, which restores only when a layer was pushed.
struct ShadingLayerGroup
{
    bool pushed = false;
};
ShadingLayerGroup beginShadingLayer(SkCanvas &canvas, const TextShadingLayer &layer, double scale);
void endShadingLayer(SkCanvas &canvas, const ShadingLayerGroup &group);

} // namespace drift::skia
