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

// Smooth morph (0.32, the cartoon packs): any two outlines blend, whatever their contours and vertex counts. Each
// contour is resampled by arc length to the same number of points, the start and direction of the second are
// chosen to sit closest to the first, and the blend is drawn back as a smooth curve (Catmull-Rom). A contour with
// no partner grows from (or shrinks into) the nearest point of the other outline, so a drop can split off a blob.
// t <= 0 and t >= 1 give a and b exactly.
//
// Options (0.32, docs/plan-vfx.md A and D): with cornerAngle > 0, a vertex where the outline turns by more than that
// many degrees is a corner (the tip of a flame tongue): it stays sharp in the blend, and when both contours have the
// same number of corners they pair up in order, each stretch between two corners resampled on its own, so a tip
// travels to its partner instead of sliding along the edge. fromCentre: a contour with no partner grows from (or
// shrinks into) its own centre (a hole opening inside smoke) instead of the nearest point of the other outline.
struct SmoothMorphOptions
{
    double cornerAngle = 0.0;
    bool fromCentre = false;
};
QString morphSvgPathsResampled(const QString &a, const QString &b, double t, const SmoothMorphOptions &options = {});
// The vertices of `contour` where its outline turns by more than `angleDeg` degrees (comparing the direction the
// curve arrives in with the one it leaves along), in vertex order. The ends of an open contour are not corners.
QList<int> pathContourCorners(const PathContour &contour, double angleDeg);

// The box the vertices and their handles span (which holds the whole curve).
QRectF pathContoursBounds(const QList<PathContour> &contours);

} // namespace drift
