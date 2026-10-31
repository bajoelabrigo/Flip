#pragma once

#include "ShapeStyle.h"

#include <QPainterPath>
#include <QRectF>
#include <QString>

namespace drift {

// Every shape fills `bounds` exactly, so a "square" or "circle" is a rectangle or ellipse in a
// square box rather than a path that forces its own aspect. Strokes are the painter's business:
// the path is the outline the layer stack paints around.
QPainterPath shapePath(const ShapeStyle &style, const QRectF &bounds);

// Any path serialized as an SVG "d" string, for QML's PathSvg; masks serialize drift::maskPath()
// through here for their assets-panel thumbnails.
QString painterPathToSvg(const QPainterPath &path);

// Parses an SVG path "d" string (M L H V C S Q T Z, absolute or relative; no arcs) into `out`,
// in the string's own coordinates. False, with `out` untouched, when it does not parse or is empty.
bool parseSvgPathData(const QString &d, QPainterPath *out);

// Regular n-gon inscribed in `bounds`, first vertex at the top. Shared with mask rendering.
// roundness (0.28): After Effects' Outer Roundness, 0..1; 1 turns the polygon into a circle.
QPainterPath regularPolygonPath(const QRectF &bounds, int sides, double rotationDeg, double roundness = 0.0);

// Heart filling `bounds`. Shared with mask rendering.
QPainterPath heartPath(const QRectF &bounds);

} // namespace drift
