#include "ShapePathEdit.h"

#include "ShapePath.h"

#include <QHash>
#include <QPainterPath>
#include <QRectF>

#include <QtMath>

#include <algorithm>
#include <cmath>
#include <limits>
#include <vector>

namespace drift {

namespace {

bool samePoint(const QPointF &a, const QPointF &b)
{
    return qAbs(a.x() - b.x()) < 1e-6 && qAbs(a.y() - b.y()) < 1e-6;
}

QString number(double v)
{
    QString s = QString::number(v, 'f', 3);
    while (s.contains(QLatin1Char('.')) && (s.endsWith(QLatin1Char('0')) || s.endsWith(QLatin1Char('.'))))
        s.chop(1);
    return s == QLatin1String("-0") ? QStringLiteral("0") : s;
}

QString pair(const QPointF &p)
{
    return number(p.x()) + QLatin1Char(' ') + number(p.y());
}

void finishContour(QList<PathContour> &out, PathContour &contour)
{
    if (contour.vertices.isEmpty())
        return;
    // QPainterPath closes a subpath with a line back to its start: that last vertex is the first.
    if (contour.vertices.size() > 1 && samePoint(contour.vertices.first().point, contour.vertices.last().point)) {
        contour.vertices.first().in = contour.vertices.last().in;
        contour.vertices.removeLast();
        contour.closed = true;
    }
    out.append(contour);
    contour = PathContour();
}

QPointF lerp(const QPointF &a, const QPointF &b, double t)
{
    return a + (b - a) * t;
}

} // namespace

QList<PathContour> pathContoursFromSvg(const QString &d)
{
    QList<PathContour> out;
    QPainterPath path;
    if (d.trimmed().isEmpty() || !parseSvgPathData(d, &path))
        return out;
    // A "Z" leaves no element of its own, so remember which subpaths the text closed.
    QList<bool> zClosed;
    {
        bool open = false;
        for (const QChar c : d) {
            if (c == QLatin1Char('M') || c == QLatin1Char('m')) {
                if (open)
                    zClosed.append(false);
                open = true;
            } else if ((c == QLatin1Char('Z') || c == QLatin1Char('z')) && open) {
                zClosed.append(true);
                open = false;
            }
        }
        if (open)
            zClosed.append(false);
    }
    PathContour contour;
    int subpath = -1;
    for (int i = 0; i < path.elementCount(); ++i) {
        const QPainterPath::Element e = path.elementAt(i);
        const QPointF p(e.x, e.y);
        switch (e.type) {
        case QPainterPath::MoveToElement:
            finishContour(out, contour);
            ++subpath;
            contour.closed = subpath < zClosed.size() && zClosed.at(subpath);
            contour.vertices.append({p, p, p});
            break;
        case QPainterPath::LineToElement:
            if (!contour.vertices.isEmpty() && samePoint(contour.vertices.last().point, p))
                break;
            contour.vertices.append({p, p, p});
            break;
        case QPainterPath::CurveToElement: {
            if (i + 2 >= path.elementCount() || contour.vertices.isEmpty())
                break;
            const QPainterPath::Element c2 = path.elementAt(i + 1);
            const QPainterPath::Element end = path.elementAt(i + 2);
            contour.vertices.last().out = p;
            contour.vertices.append({QPointF(end.x, end.y), QPointF(c2.x, c2.y), QPointF(end.x, end.y)});
            i += 2;
            break;
        }
        case QPainterPath::CurveToDataElement:
            break;
        }
    }
    finishContour(out, contour);
    return out;
}

QString svgFromPathContours(const QList<PathContour> &contours)
{
    QStringList parts;
    for (const PathContour &contour : contours) {
        const QList<PathVertex> &v = contour.vertices;
        if (v.isEmpty())
            continue;
        parts.append(QStringLiteral("M ") + pair(v.first().point));
        const int segments = contour.closed ? v.size() : v.size() - 1;
        for (int i = 0; i < segments; ++i) {
            const PathVertex &a = v.at(i);
            const PathVertex &b = v.at((i + 1) % v.size());
            if (samePoint(a.out, a.point) && samePoint(b.in, b.point)) {
                // The closing line is drawn by Z itself.
                if (!(contour.closed && i == segments - 1))
                    parts.append(QStringLiteral("L ") + pair(b.point));
            } else {
                parts.append(QStringLiteral("C ") + pair(a.out) + QLatin1Char(' ') + pair(b.in) + QLatin1Char(' ')
                             + pair(b.point));
            }
        }
        if (contour.closed)
            parts.append(QStringLiteral("Z"));
    }
    return parts.join(QLatin1Char(' '));
}

QString morphSvgPaths(const QString &a, const QString &b, double t)
{
    if (t <= 0.0 || a == b)
        return a;
    if (t >= 1.0)
        return b;
    const QList<PathContour> ca = pathContoursFromSvg(a);
    const QList<PathContour> cb = pathContoursFromSvg(b);
    bool match = !ca.isEmpty() && ca.size() == cb.size();
    for (int i = 0; match && i < ca.size(); ++i)
        match = ca.at(i).vertices.size() == cb.at(i).vertices.size() && ca.at(i).closed == cb.at(i).closed;
    if (!match)
        return a;
    QList<PathContour> mixed = ca;
    for (int i = 0; i < mixed.size(); ++i) {
        for (int k = 0; k < mixed[i].vertices.size(); ++k) {
            PathVertex &v = mixed[i].vertices[k];
            const PathVertex &w = cb.at(i).vertices.at(k);
            v.point = lerp(v.point, w.point, t);
            v.in = lerp(v.in, w.in, t);
            v.out = lerp(v.out, w.out, t);
        }
    }
    return svgFromPathContours(mixed);
}

QRectF pathContoursBounds(const QList<PathContour> &contours)
{
    QRectF box;
    bool first = true;
    for (const PathContour &contour : contours) {
        for (const PathVertex &v : contour.vertices) {
            for (const QPointF &p : {v.point, v.in, v.out}) {
                if (first) {
                    box = QRectF(p, QSizeF(0, 0));
                    first = false;
                } else {
                    box.setLeft(qMin(box.left(), p.x()));
                    box.setTop(qMin(box.top(), p.y()));
                    box.setRight(qMax(box.right(), p.x()));
                    box.setBottom(qMax(box.bottom(), p.y()));
                }
            }
        }
    }
    return box;
}

namespace {

QPointF cubicPoint(const QPointF &p0, const QPointF &c0, const QPointF &c1, const QPointF &p1, double t)
{
    const double u = 1.0 - t;
    return p0 * (u * u * u) + c0 * (3.0 * u * u * t) + c1 * (3.0 * u * t * t) + p1 * (t * t * t);
}

// A contour as a dense polyline (a closed one without repeating its first point).
// The contour as a polyline; `vertexAt`, when given, gets the index of each vertex's point in it.
std::vector<QPointF> flattenContour(const PathContour &contour, std::vector<int> *vertexAt = nullptr)
{
    std::vector<QPointF> out;
    const QList<PathVertex> &v = contour.vertices;
    if (vertexAt)
        vertexAt->assign(size_t(v.size()), 0);
    if (v.isEmpty())
        return out;
    out.push_back(v.first().point);
    const int segments = contour.closed ? int(v.size()) : int(v.size()) - 1;
    for (int i = 0; i < segments; ++i) {
        const PathVertex &a = v.at(i);
        const PathVertex &b = v.at((i + 1) % v.size());
        const bool straight = samePoint(a.out, a.point) && samePoint(b.in, b.point);
        const int steps = straight ? 1 : 16;
        for (int k = 1; k <= steps; ++k)
            out.push_back(straight ? b.point : cubicPoint(a.point, a.out, b.in, b.point, double(k) / steps));
        if (vertexAt && i + 1 < v.size())
            (*vertexAt)[size_t(i + 1)] = int(out.size()) - 1;
    }
    if (contour.closed && out.size() > 1)
        out.pop_back(); // back at the first point
    return out;
}

double polylineLength(const std::vector<QPointF> &pts, bool closed)
{
    double len = 0.0;
    for (size_t i = 1; i < pts.size(); ++i)
        len += std::hypot(pts[i].x() - pts[i - 1].x(), pts[i].y() - pts[i - 1].y());
    if (closed && pts.size() > 2)
        len += std::hypot(pts.front().x() - pts.back().x(), pts.front().y() - pts.back().y());
    return len;
}

// n points spread evenly by length (an open contour keeps both ends; a closed one starts at its first point).
std::vector<QPointF> resampleEven(const std::vector<QPointF> &pts, bool closed, int n)
{
    std::vector<QPointF> out;
    if (pts.empty())
        return out;
    std::vector<QPointF> loop = pts;
    if (closed)
        loop.push_back(pts.front());
    const double total = polylineLength(loop, false);
    if (total <= 1e-9 || loop.size() < 2) {
        out.assign(size_t(n), pts.front());
        return out;
    }
    const int divisions = closed ? n : n - 1;
    size_t seg = 1;
    double walked = 0.0;
    for (int i = 0; i < n; ++i) {
        const double target = total * i / divisions;
        while (seg < loop.size() - 1) {
            const double l = std::hypot(loop[seg].x() - loop[seg - 1].x(), loop[seg].y() - loop[seg - 1].y());
            if (walked + l >= target)
                break;
            walked += l;
            ++seg;
        }
        const QPointF a = loop[seg - 1], b = loop[seg];
        const double l = std::hypot(b.x() - a.x(), b.y() - a.y());
        const double q = l > 1e-12 ? qBound(0.0, (target - walked) / l, 1.0) : 0.0;
        out.push_back(a + (b - a) * q);
    }
    return out;
}

double signedArea(const std::vector<QPointF> &pts)
{
    double area = 0.0;
    for (size_t i = 0; i < pts.size(); ++i) {
        const QPointF &a = pts[i];
        const QPointF &b = pts[(i + 1) % pts.size()];
        area += a.x() * b.y() - b.x() * a.y();
    }
    return area / 2.0;
}

QPointF centroidOf(const std::vector<QPointF> &pts)
{
    QPointF sum;
    for (const QPointF &p : pts)
        sum += p;
    return pts.empty() ? QPointF() : sum / double(pts.size());
}

// Turns `b` (same count as `a`) to the start and direction that sit closest to `a`, point for point.
void alignTo(const std::vector<QPointF> &a, std::vector<QPointF> &b, bool closed)
{
    const size_t n = a.size();
    if (n < 2 || b.size() != n)
        return;
    const auto cost = [&](const std::vector<QPointF> &c, size_t shift) {
        double sum = 0.0;
        for (size_t i = 0; i < n; ++i) {
            const QPointF d = a[i] - c[(i + shift) % n];
            sum += d.x() * d.x() + d.y() * d.y();
        }
        return sum;
    };
    std::vector<QPointF> reversed(b.rbegin(), b.rend());
    if (!closed) {
        if (cost(reversed, 0) < cost(b, 0))
            b = reversed;
        return;
    }
    // A blob turning the other way round would cross over itself on the way.
    const double sa = signedArea(a), sb = signedArea(b);
    if (std::abs(sa) > 1e-9 && std::abs(sb) > 1e-9 && (sa > 0.0) != (sb > 0.0))
        b = reversed;
    size_t best = 0;
    double bestCost = std::numeric_limits<double>::max();
    for (size_t shift = 0; shift < n; ++shift) {
        const double c = cost(b, shift);
        if (c < bestCost) {
            bestCost = c;
            best = shift;
        }
    }
    std::vector<QPointF> turned(n);
    for (size_t i = 0; i < n; ++i)
        turned[i] = b[(i + best) % n];
    b = turned;
}

// The point of `outline` nearest `p` (p itself when there is no outline).
QPointF nearestOn(const std::vector<std::vector<QPointF>> &outline, const QPointF &p)
{
    QPointF best = p;
    double bestD = std::numeric_limits<double>::max();
    for (const std::vector<QPointF> &c : outline) {
        for (const QPointF &q : c) {
            const double d = (q.x() - p.x()) * (q.x() - p.x()) + (q.y() - p.y()) * (q.y() - p.y());
            if (d < bestD) {
                bestD = d;
                best = q;
            }
        }
    }
    return best;
}

// Points back to a smooth contour: each vertex gets Catmull-Rom handles, (next - previous) / 6; a corner (0.32) none,
// so it stays a sharp point.
PathContour smoothContour(const std::vector<QPointF> &pts, bool closed, const std::vector<bool> &corner = {})
{
    PathContour c;
    c.closed = closed;
    const int n = int(pts.size());
    for (int i = 0; i < n; ++i) {
        const QPointF prev = closed ? pts[size_t((i - 1 + n) % n)] : pts[size_t(qMax(0, i - 1))];
        const QPointF next = closed ? pts[size_t((i + 1) % n)] : pts[size_t(qMin(n - 1, i + 1))];
        const bool sharp = size_t(i) < corner.size() && corner[size_t(i)];
        const QPointF m = sharp ? QPointF() : (next - prev) / 6.0;
        c.vertices.append({pts[size_t(i)], pts[size_t(i)] - m, pts[size_t(i)] + m});
    }
    if (!closed && n > 0) {
        c.vertices.first().in = c.vertices.first().point;
        c.vertices.last().out = c.vertices.last().point;
    }
    return c;
}

// The flat index of each corner of `contour` (see pathContourCorners), in order.
std::vector<int> flatCorners(const PathContour &contour, const std::vector<int> &vertexAt, double angleDeg)
{
    std::vector<int> out;
    if (angleDeg <= 0.0)
        return out;
    for (const int v : pathContourCorners(contour, angleDeg))
        out.push_back(vertexAt[size_t(v)]);
    return out;
}

// The stretch of a closed polyline from flat index `from` round to `to` (both included).
std::vector<QPointF> stretchOf(const std::vector<QPointF> &pts, int from, int to)
{
    std::vector<QPointF> out;
    const int n = int(pts.size());
    if (n == 0)
        return out;
    int i = from;
    out.push_back(pts[size_t(i)]);
    while (i != to) {
        i = (i + 1) % n;
        out.push_back(pts[size_t(i)]);
    }
    return out;
}

// Turns a polyline round, its corner indices with it.
void reverseWithCorners(std::vector<QPointF> &pts, std::vector<int> &corners)
{
    const int last = int(pts.size()) - 1;
    std::reverse(pts.begin(), pts.end());
    std::reverse(corners.begin(), corners.end());
    for (int &c : corners)
        c = last - c;
}

// Each stretch resampled on its own to the same count in both outlines, its share of `n` the larger of its share of
// either outline's length; the first sample of every stretch but the open contour's first is a corner. `whole`: the
// last stretch keeps its end point (an open contour's end).
void resampleStretches(const std::vector<std::vector<QPointF>> &stA, const std::vector<std::vector<QPointF>> &stB, int n,
                       bool open, std::vector<QPointF> *pa, std::vector<QPointF> *pb, std::vector<bool> *corner)
{
    double totA = 0.0, totB = 0.0;
    for (size_t j = 0; j < stA.size(); ++j) {
        totA += polylineLength(stA[j], false);
        totB += polylineLength(stB[j], false);
    }
    pa->clear();
    pb->clear();
    corner->clear();
    for (size_t j = 0; j < stA.size(); ++j) {
        const double share = qMax(totA > 0.0 ? polylineLength(stA[j], false) / totA : 0.0,
                                  totB > 0.0 ? polylineLength(stB[j], false) / totB : 0.0);
        const int m = qMax(2, int(std::lround(share * n)) + 1);
        const std::vector<QPointF> ra = resampleEven(stA[j], false, m), rb = resampleEven(stB[j], false, m);
        const bool keepEnd = open && j + 1 == stA.size();
        for (int q = 0; q < (keepEnd ? m : m - 1); ++q) { // a stretch's end is the next one's corner
            pa->push_back(ra[size_t(q)]);
            pb->push_back(rb[size_t(q)]);
            corner->push_back(q == 0 && (!open || j > 0));
        }
    }
}

// Corner-paired resampling (0.32): both contours have the same corner count k > 0. The corners of `b` are matched to
// those of `a` in order (on a closed contour the same winding and the cyclic shift that brings them closest; an open
// one turned round when that fits better), and each stretch between two corners is resampled on its own, so a corner
// lands on a corner. Returns false when it cannot (the caller then resamples evenly).
bool resampleByCorners(const std::vector<QPointF> &fa, const std::vector<int> &ca, std::vector<QPointF> fb,
                       std::vector<int> cb, bool closed, int n, std::vector<QPointF> *pa, std::vector<QPointF> *pb,
                       std::vector<bool> *corner)
{
    const size_t k = ca.size();
    if (k == 0 || cb.size() != k || fa.size() < 2 || fb.size() < 2)
        return false;
    std::vector<std::vector<QPointF>> stA, stB;
    if (!closed) {
        const auto d2 = [](const QPointF &p, const QPointF &q) {
            return (p.x() - q.x()) * (p.x() - q.x()) + (p.y() - q.y()) * (p.y() - q.y());
        };
        if (d2(fa.front(), fb.back()) + d2(fa.back(), fb.front()) < d2(fa.front(), fb.front()) + d2(fa.back(), fb.back()))
            reverseWithCorners(fb, cb);
        std::vector<int> sa{0}, sb{0};
        sa.insert(sa.end(), ca.begin(), ca.end());
        sb.insert(sb.end(), cb.begin(), cb.end());
        sa.push_back(int(fa.size()) - 1);
        sb.push_back(int(fb.size()) - 1);
        for (size_t j = 0; j + 1 < sa.size(); ++j) {
            stA.emplace_back(fa.begin() + sa[j], fa.begin() + sa[j + 1] + 1);
            stB.emplace_back(fb.begin() + sb[j], fb.begin() + sb[j + 1] + 1);
        }
        resampleStretches(stA, stB, n, true, pa, pb, corner);
        return true;
    }
    const double areaA = signedArea(fa), areaB = signedArea(fb);
    if (std::abs(areaA) > 1e-9 && std::abs(areaB) > 1e-9 && (areaA > 0.0) != (areaB > 0.0))
        reverseWithCorners(fb, cb);
    size_t best = 0;
    double bestCost = std::numeric_limits<double>::max();
    for (size_t shift = 0; shift < k; ++shift) {
        double cost = 0.0;
        for (size_t j = 0; j < k; ++j) {
            const QPointF d = fa[size_t(ca[j])] - fb[size_t(cb[(j + shift) % k])];
            cost += d.x() * d.x() + d.y() * d.y();
        }
        if (cost < bestCost) {
            bestCost = cost;
            best = shift;
        }
    }
    std::vector<int> turned(k);
    for (size_t j = 0; j < k; ++j)
        turned[j] = cb[(j + best) % k];
    cb = turned;
    const int na = int(fa.size()), nb = int(fb.size());
    for (size_t j = 0; j < k; ++j) {
        if (k == 1) {
            // One corner: the stretch runs all the way round, back to it.
            stA.push_back(stretchOf(fa, ca[0], (ca[0] - 1 + na) % na));
            stA.back().push_back(fa[size_t(ca[0])]);
            stB.push_back(stretchOf(fb, cb[0], (cb[0] - 1 + nb) % nb));
            stB.back().push_back(fb[size_t(cb[0])]);
        } else {
            stA.push_back(stretchOf(fa, ca[j], ca[(j + 1) % k]));
            stB.push_back(stretchOf(fb, cb[j], cb[(j + 1) % k]));
        }
    }
    resampleStretches(stA, stB, n, false, pa, pb, corner);
    return true;
}

// The sample of `pts` nearest `p`.
size_t nearestIndex(const std::vector<QPointF> &pts, const QPointF &p)
{
    size_t best = 0;
    double bestD = std::numeric_limits<double>::max();
    for (size_t i = 0; i < pts.size(); ++i) {
        const double d = (pts[i].x() - p.x()) * (pts[i].x() - p.x()) + (pts[i].y() - p.y()) * (pts[i].y() - p.y());
        if (d < bestD) {
            bestD = d;
            best = i;
        }
    }
    return best;
}

} // namespace

QList<int> pathContourCorners(const PathContour &contour, double angleDeg)
{
    QList<int> corners;
    const QList<PathVertex> &v = contour.vertices;
    const int n = int(v.size());
    if (angleDeg <= 0.0 || n < (contour.closed ? 2 : 3))
        return corners;
    const double limit = qDegreesToRadians(qBound(0.0, angleDeg, 180.0));
    const auto length = [](const QPointF &p) { return std::hypot(p.x(), p.y()); };
    for (int i = 0; i < n; ++i) {
        if (!contour.closed && (i == 0 || i == n - 1))
            continue;
        const PathVertex &prev = v.at((i - 1 + n) % n);
        const PathVertex &here = v.at(i);
        const PathVertex &next = v.at((i + 1) % n);
        // The direction the curve arrives in (from the nearest distinct control point behind) and leaves along.
        QPointF in = here.point - here.in;
        if (length(in) < 1e-6)
            in = here.point - prev.out;
        if (length(in) < 1e-6)
            in = here.point - prev.point;
        QPointF out = here.out - here.point;
        if (length(out) < 1e-6)
            out = next.in - here.point;
        if (length(out) < 1e-6)
            out = next.point - here.point;
        const double li = length(in), lo = length(out);
        if (li < 1e-6 || lo < 1e-6)
            continue;
        const double cosA = qBound(-1.0, (in.x() * out.x() + in.y() * out.y()) / (li * lo), 1.0);
        if (std::acos(cosA) > limit)
            corners.append(i);
    }
    return corners;
}

QString morphSvgPathsResampled(const QString &a, const QString &b, double t, const SmoothMorphOptions &options)
{
    if (t <= 0.0 || a == b)
        return a;
    if (t >= 1.0)
        return b;
    const QList<PathContour> ca = pathContoursFromSvg(a);
    const QList<PathContour> cb = pathContoursFromSvg(b);
    if (ca.isEmpty() && cb.isEmpty())
        return t < 0.5 ? a : b;
    std::vector<std::vector<QPointF>> fa, fb;
    std::vector<std::vector<int>> cornersA, cornersB;
    for (const PathContour &c : ca) {
        std::vector<int> at;
        fa.push_back(flattenContour(c, &at));
        cornersA.push_back(flatCorners(c, at, options.cornerAngle));
    }
    for (const PathContour &c : cb) {
        std::vector<int> at;
        fb.push_back(flattenContour(c, &at));
        cornersB.push_back(flatCorners(c, at, options.cornerAngle));
    }
    const std::vector<int> noCorners;
    QList<PathContour> mixed;
    const int count = int(qMax(ca.size(), cb.size()));
    for (int i = 0; i < count; ++i) {
        const bool hasA = i < ca.size() && !fa[size_t(i)].empty();
        const bool hasB = i < cb.size() && !fb[size_t(i)].empty();
        if (!hasA && !hasB)
            continue;
        // A closed and an open contour meet as two closed ones.
        const bool closed = (hasA && ca.at(i).closed) || (hasB && cb.at(i).closed);
        const double lenA = hasA ? polylineLength(fa[size_t(i)], closed) : 0.0;
        const double lenB = hasB ? polylineLength(fb[size_t(i)], closed) : 0.0;
        // Coordinates are a 0..100 box: a point every ~2 units, enough for a round blob, bounded for speed.
        const int n = qBound(closed ? 12 : 6, int(std::ceil(qMax(lenA, lenB) / 2.0)), 160);
        const std::vector<int> &cA = hasA ? cornersA[size_t(i)] : noCorners;
        const std::vector<int> &cB = hasB ? cornersB[size_t(i)] : noCorners;
        std::vector<QPointF> pa, pb;
        std::vector<bool> corner;
        const bool paired = hasA && hasB && resampleByCorners(fa[size_t(i)], cA, fb[size_t(i)], cB, closed, n, &pa, &pb, &corner);
        if (!paired) {
            if (hasA)
                pa = resampleEven(fa[size_t(i)], closed, n);
            if (hasB)
                pb = resampleEven(fb[size_t(i)], closed, n);
            if (!hasA)
                pa.assign(size_t(n), options.fromCentre ? centroidOf(pb) : nearestOn(fa, centroidOf(pb)));
            else if (!hasB)
                pb.assign(size_t(n), options.fromCentre ? centroidOf(pa) : nearestOn(fb, centroidOf(pa)));
            else
                alignTo(pa, pb, closed);
            // Corners that do not pair (other counts): the nearer key's own, snapped onto their samples.
            corner.assign(size_t(n), false);
            const bool useA = hasA && (!hasB || t < 0.5);
            const std::vector<QPointF> &flat = useA ? fa[size_t(i)] : fb[size_t(i)];
            std::vector<QPointF> &samples = useA ? pa : pb;
            for (const int c : useA ? cA : cB) {
                const size_t at = nearestIndex(samples, flat[size_t(c)]);
                samples[at] = flat[size_t(c)];
                corner[at] = true;
            }
        }
        const size_t m = pa.size();
        std::vector<QPointF> blend(m);
        for (size_t k = 0; k < m; ++k)
            blend[k] = lerp(pa[k], pb[k], t);
        mixed.append(smoothContour(blend, closed, corner));
    }
    return svgFromPathContours(mixed);
}

} // namespace drift
