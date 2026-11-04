#include "PositionPath.h"

#include <QPointF>

#include <algorithm>
#include <cmath>

namespace drift {

namespace {

QList<TimeUs> unionTimes(const Clip &clip)
{
    QList<TimeUs> times = clip.transformX.keyframes().keys();
    for (const TimeUs t : clip.transformY.keyframes().keys()) {
        if (!times.contains(t))
            times.append(t);
    }
    std::sort(times.begin(), times.end());
    return times;
}

QPointF bezier2(const QPointF &a, const QPointF &b, const QPointF &c, const QPointF &d, double s)
{
    return QPointF(cubicBezier(a.x(), b.x(), c.x(), d.x(), s), cubicBezier(a.y(), b.y(), c.y(), d.y(), s));
}

// The timing as joined Position reads it: flat handles stay an ease, anything else goes straight
// (a value slope means nothing along the path).
void timingFromValue(Keyframe<double> &key)
{
    if (!qFuzzyIsNull(key.inDy) || !qFuzzyIsNull(key.outDy)) {
        key.inDx = key.inDy = key.outDx = key.outDy = 0.0;
    }
}

} // namespace

bool positionAnimated(const Clip &clip)
{
    return clip.transformX.keyframes().size() >= 2 || clip.transformY.keyframes().size() >= 2;
}

void syncJoinedPosition(Clip &clip)
{
    if (!clip.positionJoined) {
        // Keys pasted from a joined clip read as plain X and Y here.
        for (KeyframeTrack<double> *track : {&clip.transformX, &clip.transformY}) {
            QList<TimeUs> stale;
            for (auto it = track->keyframes().constBegin(); it != track->keyframes().constEnd(); ++it) {
                if (it->spatial)
                    stale.append(it.key());
            }
            for (const TimeUs t : stale) {
                Keyframe<double> *key = track->keyframeRef(t);
                key->spatial = false;
                key->spIn = key->spOut = key->pathDistance = 0.0;
                key->pathArc.fill(0.0f);
            }
        }
        return;
    }
    KeyframeTrack<double> &xs = clip.transformX;
    KeyframeTrack<double> &ys = clip.transformY;
    const QList<TimeUs> times = unionTimes(clip);
    if (times.isEmpty())
        return;

    // One set of keys: the axis that lacks one takes what it plays there now, and the timing and
    // the handles' mode come from X's key (Y's where only Y has one).
    QList<QPointF> points;
    for (const TimeUs t : times) {
        const bool hasX = xs.keyframes().contains(t);
        const bool hasY = ys.keyframes().contains(t);
        if (!hasX)
            xs.setKeyframe(t, xs.isEmpty() ? 0.0 : xs.evaluateKeys(t));
        if (!hasY)
            ys.setKeyframe(t, ys.isEmpty() ? 0.0 : ys.evaluateKeys(t));
        Keyframe<double> *kx = xs.keyframeRef(t);
        Keyframe<double> *ky = ys.keyframeRef(t);
        const Keyframe<double> &master = (hasX || !hasY) ? *kx : *ky;
        Keyframe<double> *other = (hasX || !hasY) ? ky : kx;
        if (!master.spatial) {
            // A key just put there by a value edit: its handles start as Auto Bezier.
            Keyframe<double> *m = (hasX || !hasY) ? kx : ky;
            m->spatial = true;
            m->spatialAuto = true;
            timingFromValue(*m);
        }
        other->inDx = master.inDx;
        other->inDy = master.inDy;
        other->outDx = master.outDx;
        other->outDy = master.outDy;
        other->corner = master.corner;
        other->hold = master.hold;
        other->spatialAuto = master.spatialAuto;
        if (!other->spatial) {
            other->spatial = true;
            other->spIn = other->spOut = 0.0;
        }
        points.append(QPointF(kx->value, ky->value));
    }

    // Auto Bezier: through a key the path runs parallel to the line between its neighbours, each
    // handle a third of the way to its own neighbour; the ends point straight at the next handle.
    const int n = times.size();
    for (int i = 0; i < n; ++i) {
        Keyframe<double> *kx = xs.keyframeRef(times.at(i));
        Keyframe<double> *ky = ys.keyframeRef(times.at(i));
        if (!kx->spatialAuto)
            continue;
        kx->spIn = kx->spOut = ky->spIn = ky->spOut = 0.0;
        if (i == 0 || i == n - 1)
            continue;
        const QPointF dir = points.at(i + 1) - points.at(i - 1);
        const double len = std::hypot(dir.x(), dir.y());
        if (len < 1e-9)
            continue;
        const QPointF unit = dir / len;
        const QPointF toPrev = points.at(i) - points.at(i - 1);
        const QPointF toNext = points.at(i + 1) - points.at(i);
        const double inLen = std::hypot(toPrev.x(), toPrev.y()) / 3.0;
        const double outLen = std::hypot(toNext.x(), toNext.y()) / 3.0;
        kx->spIn = -unit.x() * inLen;
        ky->spIn = -unit.y() * inLen;
        kx->spOut = unit.x() * outLen;
        ky->spOut = unit.y() * outLen;
    }

    // The distance along the path to each key, and the curve's parameter at each eighth of every
    // segment's length, so the clip covers equal stretches in equal times.
    double along = 0.0;
    for (int i = 0; i < n; ++i) {
        Keyframe<double> *kx = xs.keyframeRef(times.at(i));
        Keyframe<double> *ky = ys.keyframeRef(times.at(i));
        kx->pathDistance = ky->pathDistance = along;
        kx->pathArc.fill(0.0f);
        ky->pathArc.fill(0.0f);
        if (i == n - 1)
            break;
        const Keyframe<double> &nx = xs.keyframes()[times.at(i + 1)];
        const Keyframe<double> &ny = ys.keyframes()[times.at(i + 1)];
        const QPointF a = points.at(i);
        const QPointF d = points.at(i + 1);
        const QPointF b = a + QPointF(kx->spOut, ky->spOut);
        const QPointF c = d + QPointF(nx.spIn, ny.spIn);
        constexpr int kSteps = 96;
        std::array<double, kSteps + 1> cumulative{};
        QPointF last = a;
        for (int k = 1; k <= kSteps; ++k) {
            const QPointF p = bezier2(a, b, c, d, double(k) / kSteps);
            cumulative[k] = cumulative[k - 1] + std::hypot(p.x() - last.x(), p.y() - last.y());
            last = p;
        }
        const double length = cumulative[kSteps];
        if (length > 1e-9) {
            int k = 0;
            for (int e = 0; e <= 8; ++e) {
                const double want = length * e / 8.0;
                while (k < kSteps && cumulative[k + 1] < want)
                    ++k;
                const double span = cumulative[qMin(k + 1, kSteps)] - cumulative[k];
                const double frac = span > 1e-12 ? (want - cumulative[k]) / span : 0.0;
                const float s = float(qBound(0.0, (k + frac) / kSteps, 1.0));
                kx->pathArc[e] = ky->pathArc[e] = s;
            }
            kx->pathArc[8] = ky->pathArc[8] = 1.0f;
        }
        along += length;
    }
}

void joinPosition(Clip &clip)
{
    if (clip.positionJoined)
        return;
    clip.positionJoined = true;
    clip.positionSeparated = false;
    for (KeyframeTrack<double> *track : {&clip.transformX, &clip.transformY}) {
        for (const TimeUs t : track->keyframes().keys()) {
            Keyframe<double> *key = track->keyframeRef(t);
            // A key that was joined before keeps its path handles (a straight corner stays one:
            // separating and joining again rounded every bounce, test #8); a new one starts as
            // Auto Bezier (the default of spatialAuto).
            key->spatial = true;
            timingFromValue(*key);
        }
    }
    syncJoinedPosition(clip);
}

void separatePosition(Clip &clip)
{
    if (!clip.positionJoined) {
        clip.positionSeparated = true;
        return;
    }
    clip.positionJoined = false;
    clip.positionSeparated = true;
    // The spatial handles as value ones over a third of each segment: the same path while the
    // timing is even, which is what the separate tracks can say.
    for (KeyframeTrack<double> *track : {&clip.transformX, &clip.transformY}) {
        const QList<TimeUs> times = track->keyframes().keys();
        for (int i = 0; i < times.size(); ++i) {
            Keyframe<double> *key = track->keyframeRef(times.at(i));
            const double toPrev = i > 0 ? double(times.at(i) - times.at(i - 1)) : 0.0;
            const double toNext = i + 1 < times.size() ? double(times.at(i + 1) - times.at(i)) : 0.0;
            key->inDx = -toPrev / 3.0;
            key->outDx = toNext / 3.0;
            key->inDy = toPrev > 0 ? key->spIn : 0.0;
            key->outDy = toNext > 0 ? key->spOut : 0.0;
            if (qFuzzyIsNull(key->inDy) && qFuzzyIsNull(key->outDy))
                key->inDx = key->outDx = 0.0;
            // The path handles are kept (unused while separate) for joining again.
            key->spatial = false;
            key->pathDistance = 0.0;
            key->pathArc.fill(0.0f);
        }
    }
}

double pathDistanceAt(const Clip &clip, TimeUs relative)
{
    const QMap<TimeUs, Keyframe<double>> &keys = clip.transformX.keyframes();
    if (keys.isEmpty())
        return 0.0;
    auto it = keys.lowerBound(relative);
    if (it == keys.end())
        return std::prev(it)->pathDistance;
    if (it.key() == relative || it == keys.begin())
        return it->pathDistance;
    const auto prev = std::prev(it);
    if (prev->hold)
        return prev->pathDistance;
    const double t0 = double(prev.key());
    const double t1 = double(it.key());
    const double d0 = prev->pathDistance;
    const double d1 = it->pathDistance;
    const double time = double(relative);
    if (qFuzzyIsNull(prev->outDx) && qFuzzyIsNull(prev->outDy) && qFuzzyIsNull(it->inDx) && qFuzzyIsNull(it->inDy))
        return d0 + (d1 - d0) * (time - t0) / (t1 - t0);
    const double x1 = qBound(t0, t0 + prev->outDx, t1);
    const double x2 = qBound(t0, t1 + it->inDx, t1);
    const double s = bezierParameterForX(t0, x1, x2, t1, time);
    return cubicBezier(d0, d0 + prev->outDy, d1 + it->inDy, d1, s);
}

} // namespace drift
