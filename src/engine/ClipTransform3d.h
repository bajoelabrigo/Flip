#pragma once

#include <QMatrix4x4>
#include <QPolygonF>
#include <QRectF>
#include <QSizeF>

#include <cmath>

namespace drift {

// A clip's 3D pose on top of its 2D layout. All lengths are in the same pixels as the layout
// rect and the canvas. The eye sits `perspective` px in front of the canvas centre, so every clip
// is seen by one virtual camera; a shared scene camera can later replace the per-clip distance.
struct ClipPose3d
{
    double rotationX = 0.0; // degrees; + tips the top edge away from the viewer
    double rotationY = 0.0; // degrees; + swings the right edge away from the viewer
    double positionZ = 0.0; // px; + toward the viewer
    double perspective = 2000.0;
    // The anchor point relative to the rect centre (px), already turned by the in-plane spin: the
    // X/Y tilt pivots there, as After Effects (before 0.29 it always pivoted on the centre, so a
    // card with its anchor on an edge swung about its middle). The spin's own share of the anchor
    // is still Clip::anchorShift's move of the rect.
    QPointF pivot;

    bool isActive() const
    {
        return !qFuzzyIsNull(rotationX) || !qFuzzyIsNull(rotationY) || !qFuzzyIsNull(positionZ);
    }
};

inline constexpr double kDefaultClipPerspective = 2000.0;

// ClipPose3d::pivot for an anchor at (fx, fy) of a w × h box (fractions, 0.5 the centre) turned
// `rotationDeg` in its plane.
inline QPointF clipPivot(double fx, double fy, double w, double h, double rotationDeg)
{
    const double ax = (fx - 0.5) * w;
    const double ay = (fy - 0.5) * h;
    if (ax == 0.0 && ay == 0.0)
        return {};
    const double r = rotationDeg * 3.14159265358979323846 / 180.0;
    return {std::cos(r) * ax - std::sin(r) * ay, std::sin(r) * ax + std::cos(r) * ay};
}

// Nearest the eye a point may get, as a fraction of the perspective distance.
inline constexpr double kClipNearFraction = 0.02;

// Maps the unit quad [-1, 1]² onto the canvas in homogeneous canvas pixels (top-left origin):
// divide x, y by w to get the pixel. `rotation` is the existing in-plane spin (clockwise degrees)
// about the rect centre. Clip-space z is set so that GL clips anything nearer than a sliver in
// front of the eye, and nothing else.
QMatrix4x4 clipQuadToCanvas(const QRectF &rect, double rotation, bool flipH, bool flipV,
                            const ClipPose3d &pose, const QSizeF &canvas);

// The placement half of clipQuadToCanvas on its own: the unit quad [-1, 1]^2 into world space —
// canvas pixels about the canvas *centre*, y down, +z toward the viewer, with no projection and no
// perspective divide (w stays 1). This is the space a shared camera views, so
//
//     cameraViewProjection(camera, canvas) * clipQuadToWorld(...)
//
// is clipQuadToCanvas with one eye for the whole scene instead of the clip's own. `pose.perspective`
// is ignored here on purpose: the eye belongs to the camera, not to the clip. `canvas` is still
// needed, to put the world origin at the canvas centre.
QMatrix4x4 clipQuadToWorld(const QRectF &rect, double rotation, bool flipH, bool flipV,
                           const ClipPose3d &pose, const QSizeF &canvas);

// The same placement for an item of the rect's size laid out from (0, 0), without the flips and
// with z passed through untouched (a z = 0 point stays at z = 0, and the matrix stays invertible):
// what a QtQuick Matrix4x4 transform needs to overlay the clip.
QMatrix4x4 clipLocalToCanvas(const QRectF &rect, double rotation, const ClipPose3d &pose,
                             const QSizeF &canvas);

// clipLocalToCanvas in world space: an item of the rect's size laid out from (0, 0), placed about
// the canvas centre with no projection. What the preview overlay needs before the camera is applied.
QMatrix4x4 clipLocalToWorld(const QRectF &rect, double rotation, const ClipPose3d &pose,
                            const QSizeF &canvas);

// The flat placement of the unit quad: rect, in-plane rotation and flips, z = 0 and w = 1.
QMatrix4x4 flatQuadToCanvas(const QRectF &rect, double rotation, bool flipH, bool flipV);

// The four projected corners (top-left, top-right, bottom-right, bottom-left), in canvas pixels.
// Empty when any corner is at or behind the eye.
QPolygonF projectedClipQuad(const QRectF &rect, double rotation, const ClipPose3d &pose,
                            const QSizeF &canvas);

} // namespace drift
