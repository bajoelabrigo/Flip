#include "ShapePathEdit.h"

#include "ShapePath.h"

#include <QHash>
#include <QPainterPath>
#include <QRectF>

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

} // namespace drift
