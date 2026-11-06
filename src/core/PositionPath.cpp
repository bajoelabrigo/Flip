#include "PositionPath.h"

#include "Bezier.h"

#include <QPointF>

#include <algorithm>
#include <array>
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
    // Each axis keeps playing what it played joined (0.30.2, Jorge: an eased Position turned into a
    // straight line on separating). A straight stretch of path converts exactly: the distance
    // tangents scaled by how much of the distance this axis covers. A curved one is fitted: for a
    // few handle reaches in time, the handles' values that best match what played (least squares
    // over the stretch), keeping the closest.
    const QList<TimeUs> times = unionTimes(clip);
    const int n = times.size();
    if (n == 0)
        return;
    QList<Keyframe<double>> bx, by;
    for (const TimeUs t : times) {
        bx.append(clip.transformX.keyframes().value(t));
        by.append(clip.transformY.keyframes().value(t));
    }
    constexpr int kSamples = 16;
    // What each axis played joined, kSamples inside every segment, before the keys stop being spatial.
    QList<std::array<double, kSamples>> playedX(qMax(0, n - 1)), playedY(qMax(0, n - 1));
    for (int i = 0; i + 1 < n; ++i) {
        for (int k = 0; k < kSamples; ++k) {
            const TimeUs t = times.at(i) + (times.at(i + 1) - times.at(i)) * (k + 1) / (kSamples + 1);
            playedX[i][k] = clip.transformX.evaluateKeys(t);
            playedY[i][k] = clip.transformY.evaluateKeys(t);
        }
    }
    for (KeyframeTrack<double> *track : {&clip.transformX, &clip.transformY}) {
        const bool isX = track == &clip.transformX;
        const QList<Keyframe<double>> &before = isX ? bx : by;
        const QList<std::array<double, kSamples>> &played = isX ? playedX : playedY;
        for (int i = 0; i < n; ++i) {
            Keyframe<double> *key = track->keyframeRef(times.at(i));
            if (!key)
                continue;
            key->inDx = key->inDy = key->outDx = key->outDy = 0.0;
            // The path handles are kept (unused while separate) for joining again.
            key->spatial = false;
            key->pathDistance = 0.0;
            key->pathArc.fill(0.0f);
        }
        for (int i = 0; i + 1 < n; ++i) {
            const Keyframe<double> &a = before.at(i);
            const Keyframe<double> &b = before.at(i + 1);
            if (a.hold)
                continue;
            const double t0 = double(times.at(i));
            const double t1 = double(times.at(i + 1));
            const double span = t1 - t0;
            if (span <= 0.0)
                continue;
            Keyframe<double> *k0 = track->keyframeRef(times.at(i));
            Keyframe<double> *k1 = track->keyframeRef(times.at(i + 1));
            const double v0 = a.value;
            const double v1 = b.value;
            const bool straightPath = qFuzzyIsNull(bx.at(i).spOut) && qFuzzyIsNull(by.at(i).spOut)
                                      && qFuzzyIsNull(bx.at(i + 1).spIn) && qFuzzyIsNull(by.at(i + 1).spIn);
            const double dd = b.pathDistance - a.pathDistance;
            if (straightPath) {
                // Along a line this axis moves the same share of the distance all the way.
                const double share = std::abs(dd) > 1e-9 ? (v1 - v0) / dd : 0.0;
                k0->outDx = a.outDx;
                k0->outDy = a.outDy * share;
                k1->inDx = b.inDx;
                k1->inDy = b.inDy * share;
                continue;
            }
            const auto weights = [](double s) {
                const double u = 1.0 - s;
                return std::array<double, 4>{u * u * u, 3.0 * u * u * s, 3.0 * u * s * s, s * s * s};
            };
            QList<double> outReach{a.outDx > 0 ? a.outDx / span : 1.0 / 3.0};
            QList<double> inReach{b.inDx < 0 ? -b.inDx / span : 1.0 / 3.0};
            for (int r = 1; r <= 9; ++r) {
                outReach.append(r / 10.0);
                inReach.append(r / 10.0);
            }
            double bestErr = -1.0, bestX1 = 0, bestX2 = 0, bestY1 = 0, bestY2 = 0;
            for (const double ro : outReach) {
                for (const double ri : inReach) {
                    const double x1 = t0 + ro * span;
                    const double x2 = t1 - ri * span;
                    // Normal equations of y1, y2 over the samples.
                    double s11 = 0, s12 = 0, s22 = 0, r1 = 0, r2 = 0;
                    std::array<std::array<double, 4>, kSamples> ws;
                    for (int k = 0; k < kSamples; ++k) {
                        const double t = t0 + span * (k + 1) / (kSamples + 1);
                        ws[k] = weights(bezierParameterForX(t0, x1, x2, t1, t));
                        const double rest = played[i][k] - ws[k][0] * v0 - ws[k][3] * v1;
                        s11 += ws[k][1] * ws[k][1];
                        s12 += ws[k][1] * ws[k][2];
                        s22 += ws[k][2] * ws[k][2];
                        r1 += ws[k][1] * rest;
                        r2 += ws[k][2] * rest;
                    }
                    const double det = s11 * s22 - s12 * s12;
                    if (std::abs(det) < 1e-12)
                        continue;
                    const double y1 = (r1 * s22 - r2 * s12) / det;
                    const double y2 = (s11 * r2 - s12 * r1) / det;
                    double err = 0.0;
                    for (int k = 0; k < kSamples; ++k) {
                        const double v = ws[k][0] * v0 + ws[k][1] * y1 + ws[k][2] * y2 + ws[k][3] * v1;
                        err = qMax(err, std::abs(v - played[i][k]));
                    }
                    if (bestErr < 0.0 || err < bestErr) {
                        bestErr = err;
                        bestX1 = x1;
                        bestX2 = x2;
                        bestY1 = y1;
                        bestY2 = y2;
                    }
                }
            }
            if (bestErr < 0.0)
                continue;
            k0->outDx = bestX1 - t0;
            k0->outDy = bestY1 - v0;
            k1->inDx = bestX2 - t1;
            k1->inDy = bestY2 - v1;
        }
        // A key where this axis turns (a bounce's floor) leaves at another slope than it arrives: a
        // corner, so dragging one handle does not bend the other.
        for (int i = 1; i + 1 < n; ++i) {
            Keyframe<double> *key = track->keyframeRef(times.at(i));
            if (!key || qFuzzyIsNull(key->inDx) || qFuzzyIsNull(key->outDx))
                continue;
            const double in = key->inDy / key->inDx;
            const double out = key->outDy / key->outDx;
            if (std::abs(in - out) > 1e-3 * qMax(1e-9, qMax(std::abs(in), std::abs(out))))
                key->corner = true;
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
