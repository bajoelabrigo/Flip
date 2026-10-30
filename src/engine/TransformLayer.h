#pragma once

#include "core/Time.h"

#include <QList>
#include <QMatrix4x4>
#include <QPolygonF>
#include <QSize>
#include <QTransform>

namespace drift {

struct Clip;
class Project;

// A transform clip's box as a parent: the matrix taking a point of the canvas its children are
// laid out on to where the layer puts it, in the same (render) pixels. The box's natural size is
// the canvas, so a full-canvas box is the identity; a tilted box is one flat card seen through
// the clip's own perspective. `opacity` receives the clip's opacity, fades and animation opacity.
// `projectSize` is the canvas in project pixels; the render canvas is that times `renderScale`.
QTransform transformLayerMatrix(const Clip &clip, TimeUs timelineUs, const QSize &projectSize,
                                double renderScale, double *opacity = nullptr);

struct TransformParent
{
    QTransform matrix;       // outermost layer applied last
    double opacity = 1.0;    // product over every covering layer
    bool hasParent = false;  // false when the matrix is the identity, so nothing changes
};

// Per track of `project.tracks()`, what the transform layers over it do at `timelineUs`. Empty
// when the project has no transform layer, which callers take as "no parent anywhere". A hidden
// layer is bypassed; several transform clips live on one layer compose in list order.
QList<TransformParent> transformParentsAt(const Project &project, TimeUs timelineUs,
                                          double renderScale);

// After Effects' parenting (0.26). A clip's pose: the unit box centred on the origin → where the
// clip's laid-out box sits on the canvas (centre, turn, size; the anchor shift included), in
// project px, carried through its own parent so a chain composes. 2D: a parent's 3D tilt is not
// passed on. Evaluated at `timelineUs` even outside the clip's range, as AE does.
QTransform clipWorldPose(const Project &project, const Clip &clip, TimeUs timelineUs);

// What a clip's parent does to it at `timelineUs`: the parent's pose now against the one it had
// when the link was made (`Clip::parentRest`), in render px (`renderScale`). Identity, with
// `*active` false, for a clip without a parent, a parent that is gone or a cycle.
QTransform clipParentMatrix(const Project &project, const Clip &clip, TimeUs timelineUs,
                            double renderScale, bool *active = nullptr);

// The clip with that id anywhere on the project's timeline; null when none.
const Clip *findClipInProject(const Project &project, const QString &clipId);

// True when making `parentId` the parent of `childId` would close a loop.
bool parentLinkMakesCycle(const Project &project, const QString &childId, const QString &parentId);

// Moves the clip's own layout (position, size, turn, every key) by `delta` (project px), so that
// without the parent it sits where the parent had put it. Used to unlink or change the parent
// without a jump, as After Effects does. The anchor stays the fixed point.
void bakeMatrixIntoClipLayout(Clip &clip, const QTransform &delta, const QSize &projectSize);

// Links `clip` to `parent` (null unlinks) keeping its place at `timelineUs`: the old parent's
// motion is baked into the clip first, then the new parent's current pose becomes the rest.
void setClipParentKeepingPlace(const Project &project, Clip &clip, const Clip *parent, TimeUs timelineUs);

// A child's quad matrix (unit quad → homogeneous canvas pixels, see clipQuadToCanvas) carried
// through the parent `parent`. An affine parent passes the child's own depth through untouched;
// a projective one keeps both the child's near plane and the card's.
QMatrix4x4 parentedQuadToCanvas(const QTransform &parent, const QMatrix4x4 &quad);

// The unit quad's corners through `quad`, in canvas pixels (top-left, top-right, bottom-right,
// bottom-left); empty when any corner is at or behind the eye.
QPolygonF projectedQuad(const QMatrix4x4 &quad);

} // namespace drift
