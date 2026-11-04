#pragma once

#include "core/Clip.h"
#include "core/Track.h"

#include <QRectF>
#include <QSizeF>

namespace drift {

// Fits a scene template drawn on a fromW×fromH canvas into a toW×toH one: one uniform scale,
// centred, so a 1080×1920 template lands whole in a 720×1280 project and letterboxed in a 16:9
// one. Boxes, text sizes and shape corners scale with it; audio is left alone.
void scaleTemplateLayout(QList<Track> &tracks, int fromW, int fromH, int toW, int toH);

// A lower third drawn for one shape put in another (0.30, Jorge: a 16:9 one in a Short came out tiny in the
// middle): sized and placed by what it draws, not by its canvas. Its art (every clip's box at every key) is made
// as wide as most of the frame and its bottom set on the lower part of it, centred across.
void fitLowerThirdLayout(QList<Track> &tracks, int fromW, int fromH, int toW, int toH);

// Any overlay of the YouTube kit (0.30, Jorge: drawn for 16:9, tiny in a Short) put in a video of another shape,
// by what it draws: LowerThird as above; Keep holds its size against the short side and its place (a corner stays
// a corner, the middle the middle) inside the part of the frame a Short's captions and buttons leave free.
// Backdrops that cover the canvas go on covering it.
enum class OverlayFit { LowerThird, Keep };
void fitOverlayLayout(QList<Track> &tracks, int fromW, int fromH, int toW, int toH, OverlayFit fit);

// The part of a picture of mediaSize that fills a slot of slotSize without stretching, as a
// normalised source rect (Clip::sourceFrame): the middle, cut on the long side. `within` is the
// crop the picture already had (an asset's own sourceFrame).
QRectF coverSourceFrame(const QSizeF &mediaSize, const QSizeF &slotSize,
                        const QRectF &within = QRectF(0, 0, 1, 1));

} // namespace drift
