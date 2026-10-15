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

// The part of a picture of mediaSize that fills a slot of slotSize without stretching, as a
// normalised source rect (Clip::sourceFrame): the middle, cut on the long side. `within` is the
// crop the picture already had (an asset's own sourceFrame).
QRectF coverSourceFrame(const QSizeF &mediaSize, const QSizeF &slotSize,
                        const QRectF &within = QRectF(0, 0, 1, 1));

} // namespace drift
