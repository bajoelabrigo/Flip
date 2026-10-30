#pragma once

#include <QList>
#include <QPointF>
#include <QRectF>
#include <QString>

namespace drift {

// After Effects' path editing (0.26): a custom shape's outline as vertices with their Bézier
// handles, the form the pen draws, the preview edits and two path keys morph between.
//
// Coordinates are those of ShapeStyle::customPath, a 0..100 × 0..100 box. A handle equal to its
// vertex is no handle (a corner, a straight segment on that side).
struct PathVertex
{
    QPointF point;
    QPointF in;  // the handle the curve arrives along
    QPointF out; // the handle it leaves along
};

struct PathContour
{
    QList<PathVertex> vertices;
    bool closed = false;
};

// Any outline parseSvgPathData reads (M L H V C S Q T Z, absolute or relative) as contours.
// Quadratics become the equivalent cubics; a contour ending where it began is closed.
QList<PathContour> pathContoursFromSvg(const QString &d);
// Back to "M … C … Z", straight segments as L, numbers to three decimals.
QString svgFromPathContours(const QList<PathContour> &contours);

// Two outlines with the same contours and vertex counts blend point by point at `t` (0 = a,
// 1 = b); any other pair holds `a` until `t` reaches 1, as a path key without a match would.
QString morphSvgPaths(const QString &a, const QString &b, double t);

// The box the vertices and their handles span (which holds the whole curve).
QRectF pathContoursBounds(const QList<PathContour> &contours);

} // namespace drift
