#include "engine/TransformLayer.h"

#include "core/Clip.h"
#include "core/ClipAnimation.h"
#include "core/Project.h"
#include "core/TimelineOps.h"
#include "engine/ClipTransform3d.h"

#include <QVector4D>

#include <algorithm>
#include <cmath>

namespace drift {

namespace {

double valueAt(const KeyframeTrack<double> &track, TimeUs relative, double fallback)
{
    return track.isEmpty() ? fallback : track.evaluateAt(relative);
}

// Column-vector 3x3 (rows of `m`) as a row-vector QTransform.
QTransform fromColumns(const double m[3][3])
{
    return QTransform(m[0][0], m[1][0], m[2][0], m[0][1], m[1][1], m[2][1], m[0][2], m[1][2],
                      m[2][2]);
}

bool fuzzyIdentity(const QTransform &t)
{
    constexpr double eps = 1e-9;
    return qAbs(t.m11() - 1.0) < eps && qAbs(t.m22() - 1.0) < eps && qAbs(t.m33() - 1.0) < eps
           && qAbs(t.m12()) < eps && qAbs(t.m13()) < eps && qAbs(t.m21()) < eps
           && qAbs(t.m23()) < eps && qAbs(t.m31()) < 1e-6 && qAbs(t.m32()) < 1e-6;
}

} // namespace

QTransform transformLayerMatrix(const Clip &clip, TimeUs timelineUs, const QSize &projectSize,
                                double renderScale, double *opacity)
{
    const TimeUs relative = timelineUs - clip.timelineStart;
    const double rw = projectSize.width() * renderScale;
    const double rh = projectSize.height() * renderScale;
    QRectF box(valueAt(clip.transformX, relative, 0.0) * renderScale,
               valueAt(clip.transformY, relative, 0.0) * renderScale,
               valueAt(clip.transformW, relative, projectSize.width()) * renderScale,
               valueAt(clip.transformH, relative, projectSize.height()) * renderScale);
    double rotation = valueAt(clip.rotation, relative, 0.0);
    double alpha = qBound(0.0, valueAt(clip.opacity, relative, 1.0), 1.0)
                   * clip.fadeMultiplier(timelineUs);

    if (clipAnimationActive(clip.animIn) || clipAnimationActive(clip.animOut) || clipAnimationActive(clip.animCombo)) {
        const ClipAnimSample body =
            evaluateClipAnimation(clip.timelineStart, clip.timelineDuration, clip.animIn,
                                  clip.animOut, timelineUs, box.width(), box.height(), clip.animCombo);
        alpha *= body.opacity;
        box.translate(body.dx, body.dy);
        const double sx = body.scale * body.scaleX;
        const double sy = body.scale * body.scaleY;
        if (!qFuzzyCompare(sx, 1.0) || !qFuzzyCompare(sy, 1.0)) {
            const QPointF centre = box.center();
            box.setSize(QSizeF(box.width() * sx, box.height() * sy));
            box.moveCenter(centre);
        }
        rotation += body.rotationDeg;
    }
    if (opacity)
        *opacity = alpha;
    if (rw <= 0.0 || rh <= 0.0)
        return {};

    const double fx = clip.flipH ? -1.0 : 1.0;
    const double fy = clip.flipV ? -1.0 : 1.0;

    ClipPose3d pose;
    if (clip.layer3d) {
        pose.rotationX = valueAt(clip.rotationX, relative, 0.0);
        pose.rotationY = valueAt(clip.rotationY, relative, 0.0);
        pose.positionZ = valueAt(clip.positionZ, relative, 0.0) * renderScale;
        pose.perspective = valueAt(clip.perspective, relative, kDefaultClipPerspective) * renderScale;
    }
    if (!pose.isActive()) {
        QTransform t;
        t.translate(box.center().x(), box.center().y());
        t.rotate(rotation);
        t.scale(fx * box.width() / rw, fy * box.height() / rh);
        t.translate(-rw / 2.0, -rh / 2.0);
        return t;
    }

    // The card's own local pixels → canvas, reduced to the z = 0 plane it lies in.
    const QMatrix4x4 local = clipLocalToCanvas(box, rotation, pose, QSizeF(rw, rh));
    const int idx[3] = {0, 1, 3};
    double a[3][3];
    for (int r = 0; r < 3; ++r) {
        for (int c = 0; c < 3; ++c)
            a[r][c] = local(idx[r], idx[c]);
    }
    // Canvas → card-local: flip about the canvas centre, then shrink the canvas onto the box.
    const double sx = box.width() / rw;
    const double sy = box.height() / rh;
    const double toLocal[3][3] = {{fx * sx, 0.0, clip.flipH ? rw * sx : 0.0},
                                  {0.0, fy * sy, clip.flipV ? rh * sy : 0.0},
                                  {0.0, 0.0, 1.0}};
    double m[3][3];
    for (int r = 0; r < 3; ++r) {
        for (int c = 0; c < 3; ++c) {
            m[r][c] = 0.0;
            for (int k = 0; k < 3; ++k)
                m[r][c] += a[r][k] * toLocal[k][c];
        }
    }
    return fromColumns(m);
}

QList<TransformParent> transformParentsAt(const Project &project, TimeUs timelineUs,
                                          double renderScale)
{
    const QList<Track> &tracks = project.tracks();
    bool anyLayer = false;
    for (const Track &track : tracks)
        anyLayer = anyLayer || track.isTransformLayer();
    if (!anyLayer)
        return {};

    const QSize projectSize(project.width(), project.height());
    QList<TransformParent> parents(tracks.size());
    QList<bool> touched(tracks.size(), false);
    for (int layer = 0; layer < tracks.size(); ++layer) {
        const Track &track = tracks.at(layer);
        if (!track.isTransformLayer() || track.hidden)
            continue;
        const int end = transformSpanEndIndex(tracks, layer);
        if (end < 0)
            continue;

        QTransform matrix;
        double opacity = 1.0;
        bool active = false;
        for (const Clip &clip : track.clips) {
            if (clip.adjustmentKind != AdjustmentKind::Transform || !clip.containsTime(timelineUs))
                continue;
            double clipOpacity = 1.0;
            matrix = matrix * transformLayerMatrix(clip, timelineUs, projectSize, renderScale,
                                                   &clipOpacity);
            opacity *= clipOpacity;
            active = true;
        }
        if (!active)
            continue;

        // Layers are visited outermost first, so each one applies inside those before it.
        for (int i = layer + 1; i < tracks.size(); ++i) {
            if (transformLayersCovering(tracks, i).contains(layer)) {
                parents[i].matrix = matrix * parents[i].matrix;
                parents[i].opacity *= opacity;
                touched[i] = true;
            }
        }
    }
    for (int i = 0; i < parents.size(); ++i)
        parents[i].hasParent = touched.at(i) && !fuzzyIdentity(parents.at(i).matrix);
    return parents;
}

const Clip *findClipInProject(const Project &project, const QString &clipId)
{
    if (clipId.isEmpty())
        return nullptr;
    for (const Track &track : project.tracks()) {
        for (const Clip &clip : track.clips) {
            if (clip.id == clipId)
                return &clip;
        }
    }
    return nullptr;
}

bool parentLinkMakesCycle(const Project &project, const QString &childId, const QString &parentId)
{
    QString cursor = parentId;
    for (int guard = 0; guard < 256 && !cursor.isEmpty(); ++guard) {
        if (cursor == childId)
            return true;
        const Clip *clip = findClipInProject(project, cursor);
        if (!clip)
            return false;
        cursor = clip->parentId;
    }
    return !cursor.isEmpty();
}

namespace {

QTransform ownPose(const Clip &clip, TimeUs timelineUs, const QSize &projectSize)
{
    const TimeUs relative = timelineUs - clip.timelineStart;
    const double w = valueAt(clip.transformW, relative, projectSize.width());
    const double h = valueAt(clip.transformH, relative, projectSize.height());
    double x = valueAt(clip.transformX, relative, 0.0);
    double y = valueAt(clip.transformY, relative, 0.0);
    const double rotation = valueAt(clip.rotation, relative, 0.0);
    if (!clip.anchorX.isEmpty() || !clip.anchorY.isEmpty()) {
        const QPointF shift = clip.anchorShift(relative, w, h, rotation);
        x += shift.x();
        y += shift.y();
    }
    QTransform t;
    t.translate(x + w / 2.0, y + h / 2.0);
    t.rotate(rotation);
    t.scale(qAbs(w) > 1e-6 ? w : 1e-6, qAbs(h) > 1e-6 ? h : 1e-6);
    return t;
}

// The parent's effect on `clip` in project px; `depth` stops a cycle that slipped into a file.
QTransform parentDelta(const Project &project, const Clip &clip, TimeUs timelineUs, int depth, bool *active);

QTransform worldPose(const Project &project, const Clip &clip, TimeUs timelineUs, int depth)
{
    const QTransform own = ownPose(clip, timelineUs, QSize(project.width(), project.height()));
    bool active = false;
    const QTransform delta = parentDelta(project, clip, timelineUs, depth, &active);
    return active ? own * delta : own;
}

QTransform parentDelta(const Project &project, const Clip &clip, TimeUs timelineUs, int depth, bool *active)
{
    *active = false;
    if (clip.parentId.isEmpty() || depth > 32)
        return {};
    const Clip *parent = findClipInProject(project, clip.parentId);
    if (!parent || parent == &clip)
        return {};
    bool invertible = false;
    const QTransform restInverse = clip.parentRest.inverted(&invertible);
    if (!invertible)
        return {};
    const QTransform delta = restInverse * worldPose(project, *parent, timelineUs, depth + 1);
    *active = !fuzzyIdentity(delta);
    return delta;
}

} // namespace

QTransform clipWorldPose(const Project &project, const Clip &clip, TimeUs timelineUs)
{
    return worldPose(project, clip, timelineUs, 0);
}

QTransform clipParentMatrix(const Project &project, const Clip &clip, TimeUs timelineUs,
                            double renderScale, bool *active)
{
    bool on = false;
    if (!clip.parentId.isEmpty() && !parentLinkMakesCycle(project, clip.id, clip.parentId)) {
        QTransform delta = parentDelta(project, clip, timelineUs, 0, &on);
        if (on && renderScale != 1.0 && renderScale > 0.0) {
            // Project px → render px: the same motion seen on a canvas `renderScale` times larger.
            delta = QTransform::fromScale(1.0 / renderScale, 1.0 / renderScale) * delta
                    * QTransform::fromScale(renderScale, renderScale);
        }
        if (active)
            *active = on;
        return on ? delta : QTransform();
    }
    if (active)
        *active = false;
    return {};
}

void bakeMatrixIntoClipLayout(Clip &clip, const QTransform &delta, const QSize &projectSize)
{
    if (fuzzyIdentity(delta))
        return;
    const double sx = std::hypot(delta.m11(), delta.m12());
    const double sy = std::hypot(delta.m21(), delta.m22());
    const double turn = std::atan2(delta.m12(), delta.m11()) * 180.0 / 3.14159265358979323846;
    const bool translationOnly = qAbs(sx - 1.0) < 1e-9 && qAbs(sy - 1.0) < 1e-9 && qAbs(turn) < 1e-9;

    // Every moment a layout value is pinned. A pure move only touches X and Y at their own keys;
    // a turn or a scale mixes them, so each is written wherever any of them has a key.
    QList<TimeUs> times;
    const auto addTimes = [&times](const KeyframeTrack<double> &track) {
        for (auto it = track.keyframes().constBegin(); it != track.keyframes().constEnd(); ++it) {
            if (!times.contains(it.key()))
                times.append(it.key());
        }
    };
    for (const KeyframeTrack<double> *track : {&clip.transformX, &clip.transformY, &clip.transformW,
                                               &clip.transformH, &clip.anchorX, &clip.anchorY})
        addTimes(*track);
    if (times.isEmpty())
        times.append(0);
    std::sort(times.begin(), times.end());

    struct Pose { double x, y, w, h; };
    QList<Pose> poses;
    for (const TimeUs t : times) {
        const double w = valueAt(clip.transformW, t, projectSize.width());
        const double h = valueAt(clip.transformH, t, projectSize.height());
        const double fx = valueAt(clip.anchorX, t, 0.5);
        const double fy = valueAt(clip.anchorY, t, 0.5);
        // The anchor's place on the canvas is x + fx·w whatever the turn (see Clip::anchorShift).
        const QPointF pivot = delta.map(QPointF(valueAt(clip.transformX, t, 0.0) + fx * w,
                                                valueAt(clip.transformY, t, 0.0) + fy * h));
        const double nw = w * sx;
        const double nh = h * sy;
        poses.append({pivot.x() - fx * nw, pivot.y() - fy * nh, nw, nh});
    }
    const auto write = [&](KeyframeTrack<double> &track, double Pose::*field, bool always) {
        if (!always && !track.isEmpty()) {
            for (int i = 0; i < times.size(); ++i) {
                if (track.keyframes().contains(times.at(i)))
                    track.setKeyframe(times.at(i), poses.at(i).*field);
            }
            return;
        }
        const bool wasEmpty = track.isEmpty();
        for (int i = 0; i < times.size(); ++i) {
            if (wasEmpty && times.size() == 1)
                track.setKeyframe(0, poses.at(i).*field);
            else
                track.setKeyframe(times.at(i), poses.at(i).*field);
        }
    };
    write(clip.transformX, &Pose::x, !translationOnly || clip.transformX.isEmpty());
    write(clip.transformY, &Pose::y, !translationOnly || clip.transformY.isEmpty());
    if (!translationOnly) {
        write(clip.transformW, &Pose::w, true);
        write(clip.transformH, &Pose::h, true);
    }
    if (qAbs(turn) > 1e-9) {
        if (clip.rotation.isEmpty()) {
            clip.rotation.setKeyframe(0, turn);
        } else {
            QMap<TimeUs, Keyframe<double>> keys = clip.rotation.keyframes();
            for (auto it = keys.begin(); it != keys.end(); ++it)
                clip.rotation.setKeyframe(it.key(), it.value().value + turn);
        }
    }
}

void setClipParentKeepingPlace(const Project &project, Clip &clip, const Clip *parent, TimeUs timelineUs)
{
    bool active = false;
    const QTransform delta = clipParentMatrix(project, clip, timelineUs, 1.0, &active);
    if (active)
        bakeMatrixIntoClipLayout(clip, delta, QSize(project.width(), project.height()));
    if (!parent || parent->id == clip.id || parentLinkMakesCycle(project, clip.id, parent->id)) {
        clip.parentId.clear();
        clip.parentRest = QTransform();
        return;
    }
    clip.parentId = parent->id;
    clip.parentRest = clipWorldPose(project, *parent, timelineUs);
}

QMatrix4x4 parentedQuadToCanvas(const QTransform &parent, const QMatrix4x4 &quad)
{
    const double a = parent.m11(), b = parent.m21(), c = parent.m31();
    const double d = parent.m12(), e = parent.m22(), f = parent.m32();
    const double g = parent.m13(), h = parent.m23(), i = parent.m33();
    if (parent.isAffine() && qFuzzyCompare(i, 1.0)) {
        const QMatrix4x4 lift(float(a), float(b), 0.f, float(c),
                              float(d), float(e), 0.f, float(f),
                              0.f, 0.f, 1.f, 0.f,
                              0.f, 0.f, 0.f, 1.f);
        return lift * quad;
    }
    // z is rebuilt from the two w's: z = w' - 2n·w + 2n², so GL's -w' <= z <= w' reads as
    // w >= n (the child's own near plane) and w' >= n(w - n) (the card's).
    const double n = kClipNearFraction;
    const QMatrix4x4 lift(float(a), float(b), 0.f, float(c),
                          float(d), float(e), 0.f, float(f),
                          float(g), float(h), 0.f, float(i - 2.0 * n),
                          float(g), float(h), 0.f, float(i));
    QMatrix4x4 out = lift * quad;
    out(2, 3) += float(2.0 * n * n);
    return out;
}

QPolygonF projectedQuad(const QMatrix4x4 &quad)
{
    QPolygonF out;
    for (const QPointF corner : {QPointF(-1, -1), QPointF(1, -1), QPointF(1, 1), QPointF(-1, 1)}) {
        const QVector4D p = quad.map(QVector4D(float(corner.x()), float(corner.y()), 0.f, 1.f));
        if (p.w() <= 1e-6f)
            return {};
        out << QPointF(p.x() / p.w(), p.y() / p.w());
    }
    return out;
}

} // namespace drift
