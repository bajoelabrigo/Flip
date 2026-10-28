#include "SkiaTextPainter.h"

#include "EmojiCatalog.h"
#include "SkiaFontCollection.h"
#include "SkiaFonts.h"
#include "SkiaPath.h"
#include "SkiaShading.h"
#include "SkiaTextGeometry.h"
#include "SkiaTextEffects.h"
#include "SkiaVectorResources.h"
#include "core/ShapePath.h"
#include "core/TextAnimationPreset.h"

#include <QCache>
#include <QHash>
#include <QMutex>
#include <QMap>
#include <QMutexLocker>
#include <QPainterPath>
#include <QTransform>
#include <QtMath>

#include <algorithm>
#include <cmath>
#include <optional>

#include "include/core/SkBlendMode.h"
#include "include/core/SkBlurTypes.h"
#include "include/core/SkCanvas.h"
#include "include/core/SkColorFilter.h"
#include "include/core/SkContourMeasure.h"
#include "include/core/SkFont.h"
#include "include/core/SkFontMgr.h"
#include "include/core/SkImage.h"
#include "include/core/SkM44.h"
#include "include/core/SkMaskFilter.h"
#include "include/core/SkMatrix.h"
#include "include/core/SkPaint.h"
#include "include/core/SkPathBuilder.h"
#include "include/core/SkPathEffect.h"
#include "include/core/SkRRect.h"
#include "include/core/SkSamplingOptions.h"
#include "include/core/SkTextBlob.h"
#include "include/effects/SkGradient.h"
#include "include/effects/SkImageFilters.h"
#include "include/effects/SkShaderMaskFilter.h"

namespace drift::skia {

namespace {

SkRect toSkRect(const QRectF &r)
{
    return SkRect::MakeXYWH(float(r.x()), float(r.y()), float(r.width()), float(r.height()));
}

QRectF fromSkRect(const SkRect &r)
{
    return QRectF(r.left(), r.top(), r.width(), r.height());
}

// One laid-out piece with its geometry already in Skia form, so paint() only issues draws.
struct Piece
{
    SkPath glyphs;
    QRectF cellRect;
    QRectF inkRect;
    double baselineY = 0.0;
    int line = 0;
    int wordIndex = 0;
    bool accent = false;
    sk_sp<SkTextBlob> emoji; // colour-glyph cluster (no outline), drawn as glyphs in block coordinates
    bool runColorSet = false; // the stretch of text this piece belongs to brings its own colour
    QColor runColor;
    // 0.24: the stretch's own shading stack, background and transform, when it brings them.
    bool hasRun = false;
    drift::TextRun run;
    QPointF runCentre; // centre of the stretch's box, in output pixels
    double runOpacity = 1.0; // the letters' own opacity (0.24)
    bool runUnderline = false;
};

struct BlockGeometry
{
    QList<Piece> pieces;
};

QMutex g_geometryMutex;
QCache<quint64, std::shared_ptr<const BlockGeometry>> g_geometryCache(48);

// Glyph paths and colour-glyph blobs for a fragment set, built once per layout.
std::shared_ptr<const BlockGeometry> geometryFor(const text::FragmentSet &set)
{
    const quint64 key = set.key;
    {
        QMutexLocker lock(&g_geometryMutex);
        if (const auto *hit = g_geometryCache.object(key))
            return *hit;
    }
    auto geometry = std::make_shared<BlockGeometry>();
    geometry->pieces.reserve(set.frags.size());
    for (const text::StyledWord &word : set.frags) {
        Piece piece;
        piece.cellRect = word.cellRect;
        piece.inkRect = word.inkRect;
        piece.baselineY = word.baselineY;
        piece.line = word.line;
        piece.wordIndex = word.index;
        piece.accent = word.accent;
        piece.runColorSet = word.runColorSet;
        piece.runColor = word.runColor;
        piece.hasRun = word.hasRun;
        piece.run = word.run;
        piece.runOpacity = word.runOpacity;
        piece.runUnderline = word.runUnderline;
        if (word.geometry) {
            const text::PieceGeometry &geometry = *word.geometry;
            if (word.colour) {
                piece.emoji = SkTextBlob::MakeFromPosGlyphs(geometry.glyphs, geometry.positions, geometry.font);
            } else {
                piece.glyphs = geometry.path;
            }
        }
        geometry->pieces.append(piece);
    }
    QMutexLocker lock(&g_geometryMutex);
    g_geometryCache.insert(key, new std::shared_ptr<const BlockGeometry>(geometry));
    return geometry;
}

// The arc a bent single line sits on: chord = the line's extent, rise = textBendRise. Glyphs keep
// their advances along the arc and the slack the longer arc leaves is split between the ends.
struct Bend
{
    bool active = false;
    double left = 0, width = 0, baseline = 0;
    double radius = 0, sweep = 0, arcLen = 0;
    bool up = true;
    QPointF centre;

    // Text on a path (0.26): the outline the baseline follows, and where the line starts on it.
    sk_sp<SkContourMeasure> contour;
    double pathStart = 0.0;

    SkMatrix matrixFor(double x0, double baselineY) const
    {
        if (contour) {
            const double length = contour->length();
            double d = (x0 - left) + pathStart;
            double beyond = 0.0; // an open outline carries on straight past its ends
            if (contour->isClosed()) {
                d = std::fmod(d, length);
                if (d < 0.0)
                    d += length;
            } else if (d < 0.0) {
                beyond = d;
                d = 0.0;
            } else if (d > length) {
                beyond = d - length;
                d = length;
            }
            SkPoint pos{0, 0};
            SkVector tan{1, 0};
            contour->getPosTan(float(d), &pos, &tan);
            pos += tan * float(beyond);
            SkMatrix m = SkMatrix::Translate(pos.x(), pos.y());
            m.preConcat(SkMatrix::RotateRad(std::atan2(tan.y(), tan.x())));
            m.preConcat(SkMatrix::Translate(float(-x0), float(-baselineY)));
            return m;
        }
        const double d = (x0 - left) + (arcLen - width) / 2.0;
        const double phi = -sweep / 2.0 + d / radius;
        QPointF pos;
        double rot;
        if (up) {
            pos = centre + QPointF(radius * std::sin(phi), -radius * std::cos(phi));
            rot = phi;
        } else {
            pos = centre + QPointF(radius * std::sin(phi), radius * std::cos(phi));
            rot = -phi;
        }
        SkMatrix m = SkMatrix::Translate(float(pos.x()), float(pos.y()));
        m.preConcat(SkMatrix::RotateRad(float(rot)));
        m.preConcat(SkMatrix::Translate(float(-x0), float(-baselineY)));
        return m;
    }
};

Bend bendFor(const QList<text::StyledWord> &words, const TextStyle &style, double renderScale, const QSizeF &box)
{
    Bend bend;
    // On an outline (0.26): the outline is drawn on 0..100 of the text box; the line keeps its
    // alignment along it (left at the start, centred in the middle) plus the offset.
    if (!style.pathSvg.isEmpty() && !words.isEmpty()) {
        double left = words.first().cellRect.left();
        double right = words.first().cellRect.right();
        for (const text::StyledWord &word : words) {
            if (word.line != words.first().line)
                return bend; // multi-line blocks stay straight
            left = qMin(left, word.cellRect.left());
            right = qMax(right, word.cellRect.right());
        }
        QPainterPath outline;
        if (!drift::parseSvgPathData(style.pathSvg, &outline) || outline.isEmpty())
            return bend;
        outline = QTransform::fromScale(box.width() / 100.0, box.height() / 100.0).map(outline);
        SkContourMeasureIter iter(toSkPath(outline), false);
        sk_sp<SkContourMeasure> contour = iter.next();
        if (!contour || contour->length() < 1.0f)
            return bend;
        const double length = contour->length();
        const double width = right - left;
        const double alignShare = style.align == TextAlign::Center ? 0.5 : style.align == TextAlign::Right ? 1.0 : 0.0;
        bend.active = true;
        bend.left = left;
        bend.width = width;
        bend.baseline = words.first().baselineY;
        bend.contour = std::move(contour);
        bend.pathStart = (length - width) * alignShare + style.pathOffset / 100.0 * length;
        return bend;
    }
    // Around a circle: the line's own length is the arc, a share of the whole circumference, and
    // the ring is centred on the line's box, starting at the top (letters outward; inward when
    // bent down). A whole ring keeps a letter's gap where the end meets the start.
    if (style.pathCircle > 0.5 && !words.isEmpty()) {
        double left = words.first().cellRect.left();
        double right = words.first().cellRect.right();
        double top = words.first().cellRect.top();
        double bottom = words.first().cellRect.bottom();
        for (const text::StyledWord &word : words) {
            if (word.line != words.first().line)
                return bend; // multi-line blocks stay straight
            left = qMin(left, word.cellRect.left());
            right = qMax(right, word.cellRect.right());
            top = qMin(top, word.cellRect.top());
            bottom = qMax(bottom, word.cellRect.bottom());
        }
        const double width = right - left;
        if (width < 1.0)
            return bend;
        const double share = qBound(0.1, style.pathCircle / 100.0, 1.0);
        const double gap = share > 0.95 ? (bottom - top) * 0.6 : 0.0;
        const double around = width + gap;
        bend.active = true;
        bend.up = style.pathBend >= 0.0;
        bend.left = left;
        bend.width = width;
        bend.baseline = words.first().baselineY;
        bend.radius = around / (6.283185307179586 * share);
        bend.sweep = 6.283185307179586 * share;
        bend.arcLen = around;
        bend.centre = QPointF(left + width / 2.0, (top + bottom) / 2.0);
        return bend;
    }
    const double rise = text::textBendRise(style) * renderScale;
    if (rise < 0.5 || words.isEmpty())
        return bend;
    for (const text::StyledWord &word : words) {
        if (word.line != words.first().line)
            return bend; // multi-line blocks stay straight
    }
    double left = words.first().cellRect.left();
    double right = words.first().cellRect.right();
    for (const text::StyledWord &word : words) {
        left = qMin(left, word.cellRect.left());
        right = qMax(right, word.cellRect.right());
    }
    const double width = right - left;
    if (width < 1.0)
        return bend;
    bend.active = true;
    bend.up = style.pathBend > 0.0;
    bend.left = left;
    bend.width = width;
    bend.baseline = words.first().baselineY;
    bend.radius = (width * width / 4.0 + rise * rise) / (2.0 * rise);
    bend.sweep = 2.0 * std::asin(qMin(1.0, width / (2.0 * bend.radius)));
    bend.arcLen = bend.radius * bend.sweep;
    const double mid = left + width / 2.0;
    bend.centre = bend.up ? QPointF(mid, bend.baseline + (bend.radius - rise))
                          : QPointF(mid, bend.baseline - (bend.radius - rise));
    return bend;
}

// Whether any enabled layer changes with time on its own (moving gradients, shader effects).
bool timeDrivenPaint(const TextStyle &style)
{
    for (const TextShadingLayer &layer : style.layers) {
        if (!layer.enabled)
            continue;
        if (layer.paint.kind == TextPaintKind::Gradient && !qFuzzyIsNull(layer.paint.gradient.offsetSpeed))
            return true;
        if (layer.paint.kind == TextPaintKind::Effect && textEffectIsAnimated(layer.paint.effect))
            return true;
    }
    return false;
}

double widestStroke(const TextStyle &style)
{
    double w = textStrokeWidth(style, false);
    if (style.accent.rule != WordAccentRule::None)
        w = qMax(w, textStrokeWidth(style, true));
    return w;
}

// A soft-edged reveal across `box`: opaque behind the front, clear ahead of it. `angleDeg` is the
// direction the front travels, `progress` how far it has come (0 = nothing shown).
sk_sp<SkShader> wipeShader(const QRectF &box, double angleDeg, double progress, double softness)
{
    const double rad = qDegreesToRadians(angleDeg);
    const QPointF dir(std::cos(rad), std::sin(rad));
    double lo = std::numeric_limits<double>::max(), hi = std::numeric_limits<double>::lowest();
    for (const QPointF &corner : {box.topLeft(), box.topRight(), box.bottomLeft(), box.bottomRight()}) {
        const double t = QPointF::dotProduct(corner, dir);
        lo = qMin(lo, t);
        hi = qMax(hi, t);
    }
    const double len = qMax(1.0, hi - lo);
    const double soft = qBound(0.0, softness, 1.0);
    const double front = qBound(0.0, progress, 1.0) * (1.0 + soft);
    const QPointF origin = dir * lo;
    const SkPoint pts[2] = {SkPoint::Make(float(origin.x()), float(origin.y())),
                            SkPoint::Make(float(origin.x() + dir.x() * len), float(origin.y() + dir.y() * len))};
    const SkColor4f colors[2] = {SkColors::kWhite, SkColors::kTransparent};
    const float pos[2] = {float(qBound(0.0, front - soft, 1.0)), float(qBound(0.0, front, 1.0))};
    const SkGradient::Colors stops{SkSpan<const SkColor4f>(colors, 2), SkSpan<const float>(pos, 2), SkTileMode::kClamp};
    return SkShaders::LinearGradient(pts, SkGradient{stops, SkGradient::Interpolation{}});
}

// The outline of a text background: a rounded box, or one of the bubbles of the Burbuja gallery
// fitted around `b` (the padded text). `em` is the font size in the same units, for the parts —
// a speech tail, cloud bumps, spikes — that should not grow with the amount of text.
QPainterPath bubblePath(const QRectF &b, const QString &shape, double radius, double em)
{
    QPainterPath p;
    p.setFillRule(Qt::WindingFill);
    const double w = b.width();
    const double h = b.height();
    const double r = qMin(radius, qMin(w, h) / 2.0);
    const auto tail = [&](double at, double reach) {
        // A triangle hanging under the bottom edge, its tip leaning left like a comic balloon.
        QPainterPath t;
        const double x = b.left() + w * at;
        const double half = qMax(em * 0.22, w * 0.05);
        t.moveTo(x - half, b.bottom() - 1.0);
        t.lineTo(x - half * 1.6, b.bottom() + reach);
        t.lineTo(x + half, b.bottom() - 1.0);
        t.closeSubpath();
        return t;
    };
    const auto polygon = [](const QList<QPointF> &points) {
        QPainterPath poly;
        poly.moveTo(points.first());
        for (int i = 1; i < points.size(); ++i)
            poly.lineTo(points.at(i));
        poly.closeSubpath();
        return poly;
    };
    // An ellipse that still contains the whole box: a box inscribed in an ellipse touches it at
    // the corners when the radii are the half sides times sqrt(2).
    const QRectF ellipse = b.adjusted(-w * 0.2071, -h * 0.2071, w * 0.2071, h * 0.2071);

    if (shape == QLatin1String("pill")) {
        p.addRoundedRect(b, h / 2.0, h / 2.0);
    } else if (shape == QLatin1String("speech")) {
        p.addRoundedRect(b, qMax(r, h * 0.3), qMax(r, h * 0.3));
        p = p.united(tail(0.22, em * 0.7));
    } else if (shape == QLatin1String("oval")) {
        p.addEllipse(ellipse);
        QPainterPath t;
        const double x = ellipse.left() + ellipse.width() * 0.3;
        const double y = ellipse.bottom() - ellipse.height() * 0.08;
        t.moveTo(x - em * 0.25, y - em * 0.1);
        t.lineTo(x - em * 0.55, y + em * 0.75);
        t.lineTo(x + em * 0.3, y - em * 0.05);
        t.closeSubpath();
        p = p.united(t);
    } else if (shape == QLatin1String("thought")) {
        p.addEllipse(ellipse);
        const double d1 = em * 0.42;
        const double d2 = em * 0.24;
        p.addEllipse(QRectF(ellipse.left() + ellipse.width() * 0.2 - d1 / 2, ellipse.bottom() + em * 0.05, d1, d1));
        p.addEllipse(QRectF(ellipse.left() + ellipse.width() * 0.1 - d2 / 2, ellipse.bottom() + em * 0.55, d2, d2));
    } else if (shape == QLatin1String("cloud")) {
        // Bumps along every edge around a solid core.
        p.addRoundedRect(b, h * 0.3, h * 0.3);
        const double bump = qMax(em * 0.55, h * 0.42);
        const int across = qMax(2, qRound(w / (bump * 1.3)));
        for (int i = 0; i <= across; ++i) {
            const double x = b.left() + w * i / across;
            const double d = bump * (i % 2 ? 1.0 : 1.18);
            p.addEllipse(QPointF(x, b.top()), d * 0.62, d * 0.55);
            p.addEllipse(QPointF(x, b.bottom()), d * 0.62, d * 0.55);
        }
        p.addEllipse(QPointF(b.left(), b.center().y()), bump * 0.6, h * 0.5);
        p.addEllipse(QPointF(b.right(), b.center().y()), bump * 0.6, h * 0.5);
        p = p.simplified();
    } else if (shape == QLatin1String("burst") || shape == QLatin1String("shout")) {
        // A starburst ("BOOM!") or a ragged shout: spikes around the containing ellipse.
        const bool burst = shape == QLatin1String("burst");
        const int spikes = burst ? 18 : 12;
        const QPointF c = b.center();
        const double rx = ellipse.width() / 2.0;
        const double ry = ellipse.height() / 2.0;
        const double reach = em * (burst ? 0.55 : 0.75);
        QList<QPointF> points;
        for (int i = 0; i < spikes * 2; ++i) {
            const double a = M_PI * 2.0 * i / (spikes * 2) - M_PI / 2.0;
            // Fixed pseudo-random lengths, so a shout is irregular but never flickers.
            const double jitter = burst ? 1.0 : 0.65 + 0.35 * std::fabs(std::sin(i * 12.9898) * 1.7);
            const double out = (i % 2 == 0) ? reach * jitter : -em * 0.05;
            points.append(QPointF(c.x() + std::cos(a) * (rx + out), c.y() + std::sin(a) * (ry + out)));
        }
        p = polygon(points);
    } else if (shape == QLatin1String("tag")) {
        const double point = h * 0.5;
        p = polygon({{b.left() - point, b.center().y()}, {b.left(), b.top()}, {b.right(), b.top()},
                     {b.right(), b.bottom()}, {b.left(), b.bottom()}});
        QPainterPath hole;
        const double d = qMax(4.0, h * 0.18);
        hole.addEllipse(QPointF(b.left() - point * 0.3, b.center().y()), d / 2, d / 2);
        p = p.subtracted(hole);
    } else if (shape == QLatin1String("ribbon")) {
        const double notch = h * 0.45;
        const double out = h * 0.55;
        p = polygon({{b.left() - out, b.top()}, {b.right() + out, b.top()},
                     {b.right() + out - notch, b.center().y()}, {b.right() + out, b.bottom()},
                     {b.left() - out, b.bottom()}, {b.left() - out + notch, b.center().y()}});
    } else if (shape == QLatin1String("arrow")) {
        const double head = h * 0.6;
        p = polygon({{b.left(), b.top()}, {b.right(), b.top()}, {b.right() + head, b.center().y()},
                     {b.right(), b.bottom()}, {b.left(), b.bottom()}});
    } else if (shape == QLatin1String("note")) {
        const double fold = qMin(h, w) * 0.35;
        p = polygon({{b.left(), b.top()}, {b.right() - fold, b.top()}, {b.right(), b.top() + fold},
                     {b.right(), b.bottom()}, {b.left(), b.bottom()}});
    } else if (shape == QLatin1String("ticket")) {
        p.addRoundedRect(b, qMax(r, em * 0.12), qMax(r, em * 0.12));
        QPainterPath bites;
        const double d = h * 0.32;
        bites.addEllipse(QPointF(b.left(), b.center().y()), d, d);
        bites.addEllipse(QPointF(b.right(), b.center().y()), d, d);
        p = p.subtracted(bites);
    } else if (shape == QLatin1String("brush") || shape == QLatin1String("torn")) {
        // A paint stroke wobbles; torn paper zigzags. Both follow a fixed pattern.
        const bool brush = shape == QLatin1String("brush");
        const double amp = brush ? h * 0.08 : h * 0.07;
        const double step = brush ? em * 0.9 : em * 0.35;
        const int n = qMax(4, qRound(w / step));
        QList<QPointF> points;
        for (int i = 0; i <= n; ++i) {
            const double x = b.left() + w * i / n;
            const double wave = brush ? std::sin(i * 1.3) * amp : (i % 2 ? amp : -amp);
            points.append(QPointF(x, b.top() + wave));
        }
        points.append(QPointF(b.right() + (brush ? em * 0.35 : 0.0), b.center().y()));
        for (int i = n; i >= 0; --i) {
            const double x = b.left() + w * i / n;
            const double wave = brush ? std::sin(i * 1.7 + 1.0) * amp : (i % 2 ? -amp : amp);
            points.append(QPointF(x, b.bottom() + wave));
        }
        points.append(QPointF(b.left() - (brush ? em * 0.35 : 0.0), b.center().y()));
        p = polygon(points);
    } else if (shape == QLatin1String("heart")) {
        // A heart large enough that the text sits in its widest band.
        const QRectF hb = b.adjusted(-w * 0.28, -h * 0.75, w * 0.28, h * 1.35);
        const double x = hb.left();
        const double y = hb.top();
        const double hw = hb.width();
        const double hh = hb.height();
        p.moveTo(x + hw * 0.5, y + hh * 0.25);
        p.cubicTo(x + hw * 0.5, y, x, y, x, y + hh * 0.3);
        p.cubicTo(x, y + hh * 0.55, x + hw * 0.3, y + hh * 0.75, x + hw * 0.5, y + hh);
        p.cubicTo(x + hw * 0.7, y + hh * 0.75, x + hw, y + hh * 0.55, x + hw, y + hh * 0.3);
        p.cubicTo(x + hw, y, x + hw * 0.5, y, x + hw * 0.5, y + hh * 0.25);
        p.closeSubpath();
    } else {
        p.addRoundedRect(b, r, r);
    }
    return p;
}

QColor withAlpha(const QColor &c, double factor)
{
    QColor out = c;
    out.setAlphaF(qBound(0.0, c.alphaF() * factor, 1.0));
    return out;
}

// A fragment turned in depth about its anchor (already at the origin), seen from `distance`.
SkMatrix perspectiveTurn(double rotationXDeg, double rotationYDeg, double distance)
{
    SkM44 persp;
    persp.setRC(3, 2, float(-1.0 / qMax(1.0, distance)));
    const SkM44 m = persp * SkM44::Rotate({1, 0, 0}, float(qDegreesToRadians(rotationXDeg)))
                    * SkM44::Rotate({0, 1, 0}, float(qDegreesToRadians(rotationYDeg)));
    return m.asM33();
}

SkPath polygonPath(std::initializer_list<SkPoint> points)
{
    SkPathBuilder b;
    bool first = true;
    for (const SkPoint &p : points) {
        if (first)
            b.moveTo(p);
        else
            b.lineTo(p);
        first = false;
    }
    b.close();
    return b.detach();
}

// A bar halfWidth wide and 2 * halfLength long through the origin, turned by deg.
SkPath rotatedBar(float halfWidth, float halfLength, float deg)
{
    const float c = float(qCos(qDegreesToRadians(double(deg))));
    const float sn = float(qSin(qDegreesToRadians(double(deg))));
    const auto at = [&](float x, float y) { return SkPoint::Make(x * c - y * sn, x * sn + y * c); };
    return polygonPath({at(-halfWidth, -halfLength), at(halfWidth, -halfLength), at(halfWidth, halfLength),
                        at(-halfWidth, halfLength)});
}

// A star with `points` tips, outer radius r, inner radius r * inner, first tip straight up.
SkPath starPath(double r, int points, double inner)
{
    SkPathBuilder b;
    for (int i = 0; i < points * 2; ++i) {
        const double rad = (i % 2 ? r * inner : r);
        const double a = -M_PI / 2.0 + M_PI * i / points;
        const SkPoint p = SkPoint::Make(float(std::cos(a) * rad), float(std::sin(a) * rad));
        if (i == 0)
            b.moveTo(p);
        else
            b.lineTo(p);
    }
    b.close();
    return b.detach();
}

SkPath heartPath(double r)
{
    SkPathBuilder b;
    const float s = float(r);
    b.moveTo(0, 0.95f * s);
    b.cubicTo(-1.25f * s, 0.05f * s, -0.8f * s, -1.05f * s, 0, -0.42f * s);
    b.cubicTo(0.8f * s, -1.05f * s, 1.25f * s, 0.05f * s, 0, 0.95f * s);
    b.close();
    return b.detach();
}

// Symbols drawn as paths, so a glyph caret or particle works without any emoji font:
// "shape:bolt", "shape:diamond"… Centred on the origin, `r` = half the height.
std::optional<SkPath> vectorSymbol(const QString &glyph, double r)
{
    if (!glyph.startsWith(QLatin1String("shape:")))
        return std::nullopt;
    const QString name = glyph.mid(6);
    const float s = float(r);
    if (name == QLatin1String("bolt"))
        return polygonPath({{0.25f * s, -s}, {-0.55f * s, 0.12f * s}, {-0.02f * s, 0.12f * s}, {-0.25f * s, s},
                            {0.55f * s, -0.15f * s}, {0.03f * s, -0.15f * s}});
    if (name == QLatin1String("diamond"))
        return polygonPath({{-0.7f * s, -0.35f * s}, {-0.35f * s, -0.8f * s}, {0.35f * s, -0.8f * s},
                            {0.7f * s, -0.35f * s}, {0, s}});
    if (name == QLatin1String("heart"))
        return heartPath(r);
    if (name == QLatin1String("star"))
        return starPath(r, 5, 0.45);
    if (name == QLatin1String("sparkle"))
        return starPath(r, 4, 0.22);
    if (name == QLatin1String("burst"))
        return starPath(r, 8, 0.5);
    if (name == QLatin1String("arrow"))
        return polygonPath({{-s, -0.3f * s}, {0.1f * s, -0.3f * s}, {0.1f * s, -0.75f * s}, {s, 0},
                            {0.1f * s, 0.75f * s}, {0.1f * s, 0.3f * s}, {-s, 0.3f * s}});
    if (name == QLatin1String("play") || name == QLatin1String("triangle"))
        return polygonPath({{-0.6f * s, -0.8f * s}, {0.8f * s, 0}, {-0.6f * s, 0.8f * s}});
    if (name == QLatin1String("chevron"))
        return polygonPath({{-0.6f * s, -0.9f * s}, {-0.1f * s, -0.9f * s}, {0.7f * s, 0}, {-0.1f * s, 0.9f * s},
                            {-0.6f * s, 0.9f * s}, {0.2f * s, 0}});
    if (name == QLatin1String("check"))
        return polygonPath({{-0.9f * s, 0}, {-0.6f * s, -0.3f * s}, {-0.25f * s, 0.1f * s}, {0.6f * s, -0.8f * s},
                            {0.9f * s, -0.5f * s}, {-0.25f * s, 0.7f * s}});
    if (name == QLatin1String("plus") || name == QLatin1String("cross"))
        return polygonPath({{-0.25f * s, -s}, {0.25f * s, -s}, {0.25f * s, -0.25f * s}, {s, -0.25f * s},
                            {s, 0.25f * s}, {0.25f * s, 0.25f * s}, {0.25f * s, s}, {-0.25f * s, s},
                            {-0.25f * s, 0.25f * s}, {-s, 0.25f * s}, {-s, -0.25f * s}, {-0.25f * s, -0.25f * s}});
    if (name == QLatin1String("hash")) {
        SkPathBuilder b;
        b.addRect(SkRect::MakeLTRB(-0.45f * s, -s, -0.2f * s, s));
        b.addRect(SkRect::MakeLTRB(0.2f * s, -s, 0.45f * s, s));
        b.addRect(SkRect::MakeLTRB(-0.9f * s, -0.5f * s, 0.9f * s, -0.25f * s));
        b.addRect(SkRect::MakeLTRB(-0.9f * s, 0.25f * s, 0.9f * s, 0.5f * s));
        return b.detach();
    }
    if (name == QLatin1String("slash"))
        return polygonPath({{0.35f * s, -s}, {0.65f * s, -s}, {-0.35f * s, s}, {-0.65f * s, s}});
    if (name == QLatin1String("asterisk")) {
        SkPathBuilder b;
        for (int i = 0; i < 3; ++i) {
            b.addPath(rotatedBar(0.14f * s, s, float(i * 60)));
        }
        return b.detach();
    }
    if (name == QLatin1String("circle"))
        return SkPath::Circle(0, 0, s * 0.8f);
    if (name == QLatin1String("square"))
        return SkPath::Rect(SkRect::MakeLTRB(-0.75f * s, -0.75f * s, 0.75f * s, 0.75f * s));
    if (name == QLatin1String("moon")) {
        QPainterPath a, c;
        a.addEllipse(QPointF(0, 0), r * 0.85, r * 0.85);
        c.addEllipse(QPointF(r * 0.4, -r * 0.25), r * 0.7, r * 0.7);
        return toSkPath(a.subtracted(c));
    }
    if (name == QLatin1String("note")) {
        QPainterPath p;
        p.addEllipse(QPointF(-r * 0.35, r * 0.55), r * 0.38, r * 0.3);
        p.addRect(QRectF(-r * 0.05, -r, r * 0.16, r * 1.5));
        p.addRect(QRectF(-r * 0.05, -r, r * 0.6, r * 0.22));
        return toSkPath(p.simplified());
    }
    if (name == QLatin1String("flower")) {
        QPainterPath p;
        for (int i = 0; i < 5; ++i) {
            const double a = -M_PI / 2.0 + 2.0 * M_PI * i / 5.0;
            p.addEllipse(QPointF(std::cos(a) * r * 0.5, std::sin(a) * r * 0.5), r * 0.42, r * 0.42);
        }
        return toSkPath(p.simplified());
    }
    if (name == QLatin1String("drop")) {
        SkPathBuilder b;
        b.moveTo(0, -s);
        b.cubicTo(0.35f * s, -0.4f * s, 0.75f * s, 0, 0.75f * s, 0.3f * s);
        b.cubicTo(0.75f * s, 0.75f * s, 0.4f * s, s, 0, s);
        b.cubicTo(-0.4f * s, s, -0.75f * s, 0.75f * s, -0.75f * s, 0.3f * s);
        b.cubicTo(-0.75f * s, 0, -0.35f * s, -0.4f * s, 0, -s);
        b.close();
        return b.detach();
    }
    if (name == QLatin1String("snow")) {
        SkPathBuilder b;
        for (int i = 0; i < 3; ++i) {
            b.addPath(rotatedBar(0.08f * s, s, float(i * 60)));
        }
        return b.detach();
    }
    return std::nullopt;
}

// A text glyph (emoji or symbol) as a blob centred on the origin. The emoji addon's face when it
// carries the glyph, else whatever the platform falls back to for that character.
sk_sp<SkTypeface> glyphFace(const QString &text, const QString &styleFamily)
{
    const SkUnichar first = SkUnichar(text.toUcs4().value(0));
    std::lock_guard<std::recursive_mutex> lock(textLayoutMutex());
    sk_sp<SkTypeface> face;
    const QString emoji = emojiFontFamily();
    if (!emoji.isEmpty()) {
        face = registeredTypeface(emoji);
        if (face && face->unicharToGlyph(first) == 0)
            face = nullptr;
    }
    if (!face) {
        face = registeredTypeface(styleFamily);
        if (face && face->unicharToGlyph(first) == 0)
            face = nullptr;
    }
    if (!face) {
        if (const sk_sp<SkFontMgr> mgr = systemFontMgr())
            face = mgr->matchFamilyStyleCharacter(nullptr, SkFontStyle(), nullptr, 0, first);
    }
    return face;
}

QMutex g_glyphMutex;
QCache<QString, sk_sp<SkTextBlob>> g_glyphCache(256);

// The blob for a glyph at a size quantised to a quarter pixel; particles ask for it every frame.
sk_sp<SkTextBlob> glyphBlob(const QString &glyph, double sizePx, const QString &styleFamily)
{
    QString text = glyph;
    text.remove(QChar(0xFE0F));
    if (text.isEmpty() || sizePx <= 0.0)
        return nullptr;
    const int quarter = qMax(1, qRound(sizePx * 4.0));
    const QString key = text + QLatin1Char('\x1f') + styleFamily + QLatin1Char('\x1f') + QString::number(quarter);
    {
        QMutexLocker lock(&g_glyphMutex);
        if (const sk_sp<SkTextBlob> *hit = g_glyphCache.object(key))
            return *hit;
    }
    sk_sp<SkTextBlob> blob;
    if (const sk_sp<SkTypeface> face = glyphFace(text, styleFamily)) {
        const SkFont font(face, quarter / 4.0f);
        const QByteArray utf8 = text.toUtf8();
        const size_t bytes = size_t(utf8.size());
        const int count = int(font.textToGlyphs(utf8.constData(), bytes, SkTextEncoding::kUTF8, {}));
        if (count > 0) {
            SkRect bounds;
            font.measureText(utf8.constData(), bytes, SkTextEncoding::kUTF8, &bounds);
            SkTextBlobBuilder builder;
            const auto &run = builder.allocRun(font, count, -bounds.centerX(), -bounds.centerY());
            font.textToGlyphs(utf8.constData(), bytes, SkTextEncoding::kUTF8, {run.glyphs, size_t(count)});
            blob = builder.make();
        }
    }
    QMutexLocker lock(&g_glyphMutex);
    g_glyphCache.insert(key, new sk_sp<SkTextBlob>(blob));
    return blob;
}

// One symbol (vector or text glyph) centred on the origin, `size` tall.
void drawSymbol(SkCanvas &canvas, const QString &glyph, double size, const SkPaint &paint, const QString &family)
{
    if (const std::optional<SkPath> path = vectorSymbol(glyph, size * 0.5)) {
        canvas.drawPath(*path, paint);
        return;
    }
    if (const sk_sp<SkTextBlob> blob = glyphBlob(glyph, size, family)) {
        // Colour emoji keep their own colours; the paint carries only the alpha and blend.
        canvas.drawTextBlob(blob, 0, 0, paint);
    }
}

class AnimatedTextPainter final : public VectorPainter
{
public:
    AnimatedTextPainter(QSize size, quint64 key, const TextPaintRequest &request,
                        std::shared_ptr<const BlockGeometry> geometry, const Bend &bend, double bleedPx)
        : m_size(size), m_key(key == 0 ? 0 : (key | 1)), m_style(request.style), m_scale(request.renderScale),
          m_set(request.set), m_geometry(std::move(geometry)), m_frame(request.frame), m_bend(bend),
          m_bleed(bleedPx), m_timeSec(request.timeSec), m_grouping(request.anchorGrouping),
          m_alignment(request.anchorAlignment)
    {
        m_style.keyframes.clear();
        prepare();
    }

    QSize size() const override { return m_size; }
    quint64 cacheKey() const override { return m_key; }

    void paint(SkCanvas &canvas) const override
    {
        canvas.translate(float(m_bleed), float(m_bleed));
        SkPaint fill;
        fill.setAntiAlias(true);

        if (m_style.boxEnabled && !m_set->ink.isEmpty())
            drawBackground(canvas);
        drawParticles(canvas, true);

        // Pills follow the straight cell geometry, which a bent line no longer has.
        if (!m_bend.active) {
            for (int i = 0; i < m_pieces.size(); ++i) {
                if (!visible(i))
                    continue;
                const Piece &piece = m_pieces.at(i);
                const TextHighlight *highlight = text::highlightFor(m_style, piece.accent);
                if (!highlight)
                    continue;
                const double pad = highlight->padding * m_scale;
                const float r = float(highlight->radius * m_scale);
                fill.setColor(toSkColor(withAlpha(highlight->color, props(i).opacity)));
                canvas.save();
                canvas.concat(m_matrices.at(i));
                canvas.drawRoundRect(toSkRect(piece.cellRect.adjusted(-pad, -pad, pad, pad)), r, r, fill);
                canvas.restore();
            }
        }

        // Fully opaque fragments are drawn layer by layer, so every stroke sits under every fill.
        // A fragment mid-fade is drawn on its own translucent layer instead, so the stroke and
        // fill fade as one and the stroke never shows through the glyph.
        QList<int> solid, fading;
        for (int i = 0; i < m_pieces.size(); ++i) {
            if (!visible(i))
                continue;
            (opacityOf(i) >= 0.999 ? solid : fading).append(i);
        }
        // The stretches asking for a background get it behind their letters (0.24).
        drawRunBackgrounds(canvas, solid);
        drawLayers(canvas, solid);
        for (int i : fading) {
            SkPaint alpha;
            alpha.setAlphaf(float(opacityOf(i)));
            canvas.saveLayer(nullptr, &alpha);
            drawRunBackgrounds(canvas, {i});
            drawLayers(canvas, {i});
            canvas.restore();
        }

        drawUnderline(canvas);
        drawStrike(canvas);
        drawCaret(canvas);
        drawParticles(canvas, false);

        if (m_frame.block.wipeProgress >= 0.0) {
            SkPaint mask;
            mask.setBlendMode(SkBlendMode::kDstIn);
            mask.setShader(wipeShader(m_set->ink, m_frame.block.wipeAngle, m_frame.block.wipeProgress,
                                      m_frame.block.wipeSoftness));
            canvas.drawPaint(mask);
        }
    }

private:
    const textanim::FragmentProps &props(int i) const
    {
        static const textanim::FragmentProps kIdentity;
        return i < m_frame.props.size() ? m_frame.props.at(i) : kIdentity;
    }

    // What a piece fades by: the animator's, times the letters' own opacity (0.24).
    double opacityOf(int i) const
    {
        const double own = i < m_pieces.size() ? m_pieces.at(i).runOpacity : 1.0;
        return props(i).opacity * own;
    }

    bool visible(int i) const
    {
        const textanim::FragmentProps &p = props(i);
        return !p.hidden && p.opacity > 0.001;
    }

    // The point a fragment scales and rotates about, per the anchor grouping.
    QPointF anchorFor(int i) const
    {
        const Piece &piece = m_pieces.at(i);
        QRectF box = piece.cellRect;
        switch (m_grouping) {
        case TextAnchorGrouping::Character:
            break;
        case TextAnchorGrouping::Word:
            for (const Piece &other : m_pieces)
                if (other.wordIndex == piece.wordIndex && other.line == piece.line)
                    box = box.united(other.cellRect);
            break;
        case TextAnchorGrouping::Line:
            for (const Piece &other : m_pieces)
                if (other.line == piece.line)
                    box = box.united(other.cellRect);
            break;
        case TextAnchorGrouping::All:
            box = m_set->ink;
            break;
        }
        return QPointF(box.center().x() + box.width() * 0.5 * m_alignment.x(),
                       piece.baselineY + box.height() * 0.5 * m_alignment.y());
    }

    void prepare()
    {
        m_pieces = m_geometry->pieces;
        // Where each transformed stretch's box is: the letters turn about its centre. Stretches
        // side by side with the same transform are one box (the letters picked at once, split
        // only because some of them already had a colour or a font).
        const auto sameTransform = [](const drift::TextRun &a, const drift::TextRun &b) {
            return qFuzzyCompare(a.offsetX + 1.0, b.offsetX + 1.0) && qFuzzyCompare(a.offsetY + 1.0, b.offsetY + 1.0)
                   && qFuzzyCompare(a.transformScale, b.transformScale)
                   && qFuzzyCompare(a.rotation + 1.0, b.rotation + 1.0);
        };
        QList<int> order;
        for (int i = 0; i < m_pieces.size(); ++i)
            if (m_pieces.at(i).hasRun && m_pieces.at(i).run.transformEnabled)
                order.append(i);
        std::stable_sort(order.begin(), order.end(),
                         [&](int a, int b) { return m_pieces.at(a).run.start < m_pieces.at(b).run.start; });
        QList<QList<int>> boxes;
        for (int i : order) {
            const drift::TextRun &run = m_pieces.at(i).run;
            bool joined = false;
            if (!boxes.isEmpty()) {
                const drift::TextRun &last = m_pieces.at(boxes.last().last()).run;
                const bool touching = (last.start == run.start && last.end == run.end) || last.end == run.start;
                if (touching && sameTransform(last, run)) {
                    boxes.last().append(i);
                    joined = true;
                }
            }
            if (!joined)
                boxes.append(QList<int>{i});
        }
        for (const QList<int> &box : std::as_const(boxes)) {
            QRectF rect;
            for (int i : box)
                rect = rect.isNull() ? m_pieces.at(i).cellRect : rect.united(m_pieces.at(i).cellRect);
            for (int i : box)
                m_pieces[i].runCentre = rect.center();
        }
        m_matrices.reserve(m_pieces.size());
        for (int i = 0; i < m_pieces.size(); ++i) {
            const Piece &piece = m_pieces.at(i);
            const textanim::FragmentProps &p = props(i);
            const QPointF anchor = anchorFor(i);
            SkMatrix m = m_bend.active ? m_bend.matrixFor(piece.cellRect.left(), piece.baselineY) : SkMatrix::I();
            SkMatrix anim = SkMatrix::Translate(float(anchor.x() + p.dx), float(anchor.y() + p.dy));
            anim.preConcat(SkMatrix::RotateDeg(float(p.rotation)));
            anim.preConcat(SkMatrix::Skew(float(std::tan(qDegreesToRadians(p.skew))), 0.0f));
            if (!qFuzzyIsNull(p.rotationX) || !qFuzzyIsNull(p.rotationY))
                anim.preConcat(perspectiveTurn(p.rotationX, p.rotationY, m_style.pixelSize * m_scale * 5.0));
            anim.preConcat(SkMatrix::Scale(float(p.scaleX), float(p.scaleY)));
            anim.preConcat(SkMatrix::Translate(float(-anchor.x()), float(-anchor.y())));
            m.preConcat(anim);
            m_matrices.append(m);
        }
        m_strokeWidthPx = widestStroke(m_style) * m_scale;
        // A stretch with its own stack grows its shadow and glow by its own stroke (0.24).
        m_pieceStrokePx.resize(m_pieces.size());
        for (int i = 0; i < m_pieces.size(); ++i) {
            const Piece &piece = m_pieces.at(i);
            if (piece.hasRun && piece.run.layersEnabled && !piece.run.layers.isEmpty()) {
                TextStyle own = m_style;
                own.layers = piece.run.layers;
                m_pieceStrokePx[i] = widestStroke(own) * m_scale;
            } else {
                m_pieceStrokePx[i] = m_strokeWidthPx;
            }
        }
    }

    // The front-most enabled fill of a stack: the one a colour override (the legacy accent, or a
    // stretch's own colour) paints.
    static bool isPrimaryFillIn(const QList<TextShadingLayer> &stack, const TextShadingLayer &layer)
    {
        const TextShadingLayer *primary = firstTextLayerOfKind(stack, TextLayerKind::Fill, true);
        return primary && layer.id == primary->id;
    }

    // The stack a piece paints with: its stretch's own, when it brings one, or the block's.
    const QList<TextShadingLayer> &stackOf(const Piece &piece) const
    {
        return piece.hasRun && piece.run.layersEnabled && !piece.run.layers.isEmpty() ? piece.run.layers
                                                                                       : m_style.layers;
    }

    bool isPrimaryFill(const TextShadingLayer &layer) const
    {
        return isPrimaryFillIn(m_style.layers, layer);
    }

    bool inScope(const TextShadingLayer &layer, const Piece &piece) const
    {
        switch (layer.scope) {
        case TextLayerScope::All:
            return true;
        case TextLayerScope::Base:
            return !piece.accent;
        case TextLayerScope::Accent:
            return piece.accent;
        }
        return true;
    }

    // Where a gradient maps for this piece.
    QRectF paintBoxFor(TextGradientSpace space, int i) const
    {
        const Piece &piece = m_pieces.at(i);
        switch (space) {
        case TextGradientSpace::Block:
            return m_set->ink;
        case TextGradientSpace::Glyph:
            return piece.inkRect;
        case TextGradientSpace::Line: {
            QRectF box;
            for (const Piece &other : m_pieces)
                if (other.line == piece.line)
                    box = box.isNull() ? other.inkRect : box.united(other.inkRect);
            return box;
        }
        case TextGradientSpace::Word: {
            QRectF box;
            for (const Piece &other : m_pieces)
                if (other.wordIndex == piece.wordIndex)
                    box = box.isNull() ? other.inkRect : box.united(other.inkRect);
            return box;
        }
        case TextGradientSpace::AccentRun: {
            // The contiguous run of accented words this piece belongs to; a plain piece maps to
            // the whole block.
            if (!piece.accent)
                return m_set->ink;
            int lo = i, hi = i;
            while (lo > 0 && m_pieces.at(lo - 1).accent && m_pieces.at(lo - 1).line == piece.line)
                --lo;
            while (hi + 1 < m_pieces.size() && m_pieces.at(hi + 1).accent && m_pieces.at(hi + 1).line == piece.line)
                ++hi;
            QRectF box;
            for (int k = lo; k <= hi; ++k)
                box = box.isNull() ? m_pieces.at(k).inkRect : box.united(m_pieces.at(k).inkRect);
            return box;
        }
        }
        return m_set->ink;
    }

    // The paint for one piece of one layer: the layer's own paint, or the animator's / accent's
    // colour override.
    void layerPaint(SkPaint &paint, const TextShadingLayer &layer, int i, double alpha) const
    {
        const Piece &piece = m_pieces.at(i);
        const textanim::FragmentProps &p = props(i);
        paint.setShader(nullptr);
        paint.setColorFilter(nullptr);
        std::optional<QColor> override;
        if (layer.kind == TextLayerKind::Fill) {
            if (p.fillColor)
                override = *p.fillColor;
            else if (piece.runColorSet && isPrimaryFillIn(stackOf(piece), layer))
                override = piece.runColor;
            else if (piece.accent && m_style.accent.colorEnabled && isPrimaryFill(layer))
                override = m_style.accent.color;
            alpha *= p.fillOpacity;
        } else if (layer.kind == TextLayerKind::Stroke) {
            if (p.strokeColor)
                override = *p.strokeColor;
            else if (piece.accent && m_style.accent.outlineEnabled)
                override = m_style.accent.outlineColor;
            alpha *= p.strokeOpacity;
        }
        if (override) {
            paint.setColor(toSkColor(withAlpha(*override, alpha)));
            return;
        }
        const TextPaint &tp = layer.paint;
        const QRectF box = paintBoxFor(tp.kind == TextPaintKind::Gradient ? tp.gradient.space : TextGradientSpace::Block, i);
        applyShadingPaint(paint, tp, box, m_timeSec, alpha, m_frame.block.wipeProgress);
    }

    void applyFragmentWipe(SkPaint &paint, int i) const
    {
        const textanim::FragmentProps &p = props(i);
        if (p.wipeProgress < 0.0)
            return;
        paint.setMaskFilter(SkShaderMaskFilter::Make(
            wipeShader(m_pieces.at(i).cellRect, p.wipeAngle, p.wipeProgress, p.wipeSoftness)));
    }

    // One layer of the stack over the given pieces. Pieces are bucketed by their own blur so
    // a handful of transitional fragments do not force a filter over the whole block.
    // The style's layers in order, except that an Inside stroke goes on last: it is clipped to the
    // glyph, so under a fill (where new strokes are put) it would never show (auditoría D2).
    // The animated halo (FragmentProps::glowPx) behind the letters, in the style's glow colour or
    // the letters' own. Drawn first, so the style's layers sit on it.
    void drawAnimatedGlow(SkCanvas &canvas, const QList<int> &pieces) const
    {
        QColor colour;
        for (const TextShadingLayer &layer : m_style.layers) {
            if (layer.enabled && layer.kind == TextLayerKind::Glow) {
                colour = layer.paint.color;
                break;
            }
        }
        if (!colour.isValid())
            colour = m_style.primaryColor();
        for (int i : pieces) {
            const double radius = props(i).glowPx;
            const Piece &piece = m_pieces.at(i);
            if (radius <= 0.25 || piece.emoji)
                continue;
            canvas.save();
            canvas.concat(m_matrices.at(i));
            SkPaint halo;
            halo.setAntiAlias(true);
            halo.setColor(toSkColor(colour));
            halo.setMaskFilter(SkMaskFilter::MakeBlur(kNormal_SkBlurStyle, float(radius * 0.5)));
            // Twice: one soft pass is too faint to read as a glow on a busy picture.
            canvas.drawPath(piece.glyphs, halo);
            canvas.drawPath(piece.glyphs, halo);
            canvas.restore();
        }
    }

    // The background a stretch asks for (0.24): one rounded box per piece, which gives one per line
    // when the stretch wraps.
    void drawRunBackgrounds(SkCanvas &canvas, const QList<int> &pieces) const
    {
        for (int i : pieces) {
            const Piece &piece = m_pieces.at(i);
            if (!piece.hasRun || !piece.run.boxEnabled)
                continue;
            const drift::TextRun &run = piece.run;
            // cellRect is already in output pixels (as the highlight pills use it).
            const double pad = run.boxPadding * m_scale;
            const QRectF scaled = piece.cellRect.adjusted(-pad, -pad * 0.5, pad, pad * 0.5);
            canvas.save();
            canvas.concat(m_matrices.at(i));
            applyRunTransform(canvas, piece);
            SkPaint paint;
            paint.setAntiAlias(true);
            paint.setColor(toSkColor(run.boxColor));
            const float radius = float(run.boxRadius * m_scale);
            canvas.drawRoundRect(toSkRect(scaled), radius, radius, paint);
            if (run.boxBorderWidth > 0.0) {
                SkPaint border;
                border.setAntiAlias(true);
                border.setStyle(SkPaint::kStroke_Style);
                border.setStrokeWidth(float(run.boxBorderWidth * m_scale));
                border.setColor(toSkColor(run.boxBorderColor));
                canvas.drawRoundRect(toSkRect(scaled), radius, radius, border);
            }
            canvas.restore();
        }
    }

    void drawStack(SkCanvas &canvas, const QList<TextShadingLayer> &stack, const QList<int> &pieces) const
    {
        const auto inside = [](const TextShadingLayer &layer) {
            return layer.kind == TextLayerKind::Stroke && layer.strokeAlign == StrokeAlign::Inside;
        };
        for (const TextShadingLayer &layer : stack) {
            if (!inside(layer))
                drawLayer(canvas, layer, pieces, 1.0);
        }
        for (const TextShadingLayer &layer : stack) {
            if (inside(layer))
                drawLayer(canvas, layer, pieces, 1.0);
        }
    }

    void drawLayers(SkCanvas &canvas, const QList<int> &pieces) const
    {
        drawAnimatedGlow(canvas, pieces);
        // The pieces with no stack of their own paint with the block's, as always.
        QList<int> blockPieces;
        // One group per stretch that brings its own stack, in reading order (a stretch's shadow can
        // fall over the letter next to it, as in Filmora).
        QList<QPair<QPair<int, int>, QList<int>>> runGroups;
        for (int i : pieces) {
            const Piece &piece = m_pieces.at(i);
            if (!piece.hasRun || !piece.run.layersEnabled || piece.run.layers.isEmpty()) {
                blockPieces.append(i);
                continue;
            }
            const QPair<int, int> key(piece.run.start, piece.run.end);
            bool found = false;
            for (auto &group : runGroups) {
                if (group.first == key) {
                    group.second.append(i);
                    found = true;
                    break;
                }
            }
            if (!found)
                runGroups.append({key, QList<int>{i}});
        }
        drawStack(canvas, m_style.layers, blockPieces);
        for (const auto &group : runGroups)
            drawStack(canvas, m_pieces.at(group.second.first()).run.layers, group.second);
    }

    void drawLayer(SkCanvas &canvas, const TextShadingLayer &layer, const QList<int> &pieces, double alpha) const
    {
        if (!layer.enabled || layer.opacity <= 0.0 || pieces.isEmpty())
            return;
        QList<int> scoped;
        for (int i : pieces)
            if (inScope(layer, m_pieces.at(i)))
                scoped.append(i);
        if (scoped.isEmpty())
            return;

        const ShadingLayerGroup group = beginShadingLayer(canvas, layer, m_scale);
        canvas.translate(float(layer.offsetX * m_scale), float(layer.offsetY * m_scale));

        // Bucket by the animator's per-fragment blur (quantised to half a pixel).
        QMap<int, QList<int>> buckets;
        for (int i : scoped)
            buckets[qRound(props(i).blurPx * 2.0)].append(i);
        for (auto it = buckets.constBegin(); it != buckets.constEnd(); ++it) {
            const double sigma = it.key() / 2.0;
            if (sigma > 0.0) {
                SkPaint bp;
                bp.setImageFilter(SkImageFilters::Blur(float(sigma), float(sigma), nullptr));
                canvas.saveLayer(nullptr, &bp);
            }
            for (int i : it.value())
                drawPiece(canvas, layer, i, alpha);
            if (sigma > 0.0)
                canvas.restore();
        }

        canvas.translate(float(-layer.offsetX * m_scale), float(-layer.offsetY * m_scale));
        endShadingLayer(canvas, group);
    }

    void drawPiece(SkCanvas &canvas, const TextShadingLayer &layer, int i, double alpha) const
    {
        const Piece &piece = m_pieces.at(i);
        const textanim::FragmentProps &p = props(i);
        canvas.save();
        canvas.concat(m_matrices.at(i));
        applyRunTransform(canvas, piece);
        SkPaint paint;
        paint.setAntiAlias(true);
        switch (layer.kind) {
        case TextLayerKind::Fill:
            layerPaint(paint, layer, i, alpha);
            applyFragmentWipe(paint, i);
            if (piece.emoji) {
                drawEmoji(canvas, piece, paint.getMaskFilter() ? &paint : nullptr);
            } else {
                paint.setPathEffect(fillPathEffectFor(layer, m_scale));
                canvas.drawPath(piece.glyphs, paint);
            }
            break;
        case TextLayerKind::Stroke: {
            double width = (piece.accent && m_style.accent.outlineEnabled ? m_style.accent.outlineWidth : layer.width)
                           + p.strokeWidthDelta / m_scale;
            width = qMax(0.0, width) * m_scale;
            if (width <= 0.0)
                break;
            layerPaint(paint, layer, i, alpha);
            applyFragmentWipe(paint, i);
            if (piece.emoji) {
                // The bitmap's alpha, dilated by the stroke width and tinted: the same ring an
                // outlined glyph gets.
                SkPaint ring;
                ring.setAlphaf(paint.getAlphaf());
                ring.setImageFilter(SkImageFilters::ColorFilter(
                    SkColorFilters::Blend(paint.getColor() | 0xFF000000, SkBlendMode::kSrcIn),
                    SkImageFilters::Dilate(float(width), float(width), nullptr)));
                drawEmoji(canvas, piece, &ring);
                break;
            }
            paint.setStyle(SkPaint::kStroke_Style);
            // A centred stroke of twice the width grows entirely outward when the fill is drawn
            // over it, which is what the legacy outline did; Inside clips the same stroke to the
            // glyph instead.
            paint.setStrokeWidth(float(layer.strokeAlign != StrokeAlign::Center ? width * 2.0 : width));
            paint.setStrokeJoin(SkPaint::kRound_Join);
            paint.setStrokeCap(SkPaint::kRound_Cap);
            paint.setPathEffect(strokePathEffectFor(layer, width, m_scale));
            if (layer.strokeAlign == StrokeAlign::Inside) {
                canvas.save();
                canvas.clipPath(piece.glyphs, SkClipOp::kIntersect, true);
                canvas.drawPath(piece.glyphs, paint);
                canvas.restore();
            } else {
                canvas.drawPath(piece.glyphs, paint);
            }
            break;
        }
        case TextLayerKind::Shadow:
        case TextLayerKind::Glow: {
            // Shadows and glows are silhouettes: the glyph grown by the stroke, in the layer's colour.
            const double strokePx = i < m_pieceStrokePx.size() ? m_pieceStrokePx.at(i) : m_strokeWidthPx;
            paint.setColor(toSkColor(withAlpha(layer.paint.color, alpha)));
            applyFragmentWipe(paint, i);
            if (piece.emoji) {
                SkPaint silhouette;
                sk_sp<SkImageFilter> dilate =
                    strokePx > 0.0 ? SkImageFilters::Dilate(float(strokePx), float(strokePx), nullptr)
                                          : nullptr;
                silhouette.setImageFilter(SkImageFilters::ColorFilter(
                    SkColorFilters::Blend(toSkColor(layer.paint.color), SkBlendMode::kSrcIn), std::move(dilate)));
                silhouette.setAlphaf(float(alpha));
                drawEmoji(canvas, piece, &silhouette);
                break;
            }
            canvas.drawPath(piece.glyphs, paint);
            if (strokePx > 0.0) {
                paint.setStyle(SkPaint::kStroke_Style);
                paint.setStrokeWidth(float(strokePx * 2.0));
                paint.setStrokeJoin(SkPaint::kRound_Join);
                canvas.drawPath(piece.glyphs, paint);
            }
            break;
        }
        case TextLayerKind::Extrude: {
            if (piece.emoji)
                break;
            const int steps = qMax(1, layer.extrudeSteps);
            const double rad = qDegreesToRadians(layer.extrudeAngle);
            const double depth = layer.width * m_scale;
            for (int k = steps; k >= 1; --k) {
                const double f = double(k) / steps;
                QColor c = layer.paint.color.darker(100 + int(layer.extrudeDarken * 100.0 * f));
                paint.setColor(toSkColor(withAlpha(c, alpha)));
                canvas.save();
                canvas.translate(float(std::cos(rad) * depth * f), float(std::sin(rad) * depth * f));
                canvas.drawPath(piece.glyphs, paint);
                canvas.restore();
            }
            break;
        }
        }
        canvas.restore();
    }

    // A stretch's own transform, about the centre of its box (0.24). It moves these letters (and
    // their background) and nothing else: the rest of the block keeps its layout. The offset moves
    // the turned box; it is not turned or scaled with it.
    void applyRunTransform(SkCanvas &canvas, const Piece &piece) const
    {
        if (!piece.hasRun || !piece.run.transformEnabled)
            return;
        const float cx = float(piece.runCentre.x());
        const float cy = float(piece.runCentre.y());
        canvas.translate(float(piece.run.offsetX * m_scale) + cx, float(piece.run.offsetY * m_scale) + cy);
        canvas.rotate(float(piece.run.rotation));
        canvas.scale(float(piece.run.transformScale), float(piece.run.transformScale));
        canvas.translate(-cx, -cy);
    }

    void drawEmoji(SkCanvas &canvas, const Piece &piece, const SkPaint *paint) const
    {
        canvas.drawTextBlob(piece.emoji, 0, 0, paint ? *paint : SkPaint());
    }

    // The box behind the text: one around the block, or one per line ("line"), padded, shifted
    // and shaped (a bubble) as the style says, with an optional border.
    void drawBackground(SkCanvas &canvas) const
    {
        const double padX = m_style.boxPadX() * m_scale;
        const double padY = m_style.boxPadY() * m_scale;
        const QPointF shift(m_style.boxOffsetX * m_scale, m_style.boxOffsetY * m_scale);
        const double em = m_style.pixelSize * m_scale;
        QList<QRectF> boxes;
        if (m_style.boxStyle == QLatin1String("line") && !m_bend.active) {
            QMap<int, QRectF> lines;
            for (const Piece &piece : m_pieces) {
                QRectF &line = lines[piece.line];
                line = line.isNull() ? piece.cellRect : line.united(piece.cellRect);
            }
            for (const QRectF &line : std::as_const(lines))
                boxes.append(line);
        }
        if (boxes.isEmpty())
            boxes.append(m_set->ink);

        QPainterPath outline;
        outline.setFillRule(Qt::WindingFill);
        for (const QRectF &box : std::as_const(boxes)) {
            const QRectF padded = box.adjusted(-padX, -padY, padX, padY).translated(shift);
            outline.addPath(bubblePath(padded, m_style.boxShape, m_style.boxRadius * m_scale, em));
        }
        const SkPath path = toSkPath(outline);
        SkPaint fill;
        fill.setAntiAlias(true);
        fill.setColor(toSkColor(m_style.boxColor));
        canvas.drawPath(path, fill);
        if (m_style.boxBorderWidth > 0.0) {
            SkPaint border;
            border.setAntiAlias(true);
            border.setStyle(SkPaint::kStroke_Style);
            border.setStrokeJoin(SkPaint::kRound_Join);
            border.setStrokeWidth(float(m_style.boxBorderWidth * m_scale));
            border.setColor(toSkColor(m_style.boxBorderColor));
            canvas.drawPath(path, border);
        }
    }

    // A line through the letters at about half their x-height, in the text's own colour, as thick
    // as a regular stroke of the font would be.
    void drawStrike(SkCanvas &canvas) const
    {
        if (m_bend.active || !m_style.strikeEnabled)
            return;
        const double thickness = qMax(1.0, m_style.pixelSize * 0.065) * m_scale;
        const double rise = m_style.pixelSize * 0.3 * m_scale;
        QHash<int, QRectF> perLine;
        for (int i = 0; i < m_pieces.size(); ++i) {
            if (!visible(i))
                continue;
            const Piece &piece = m_pieces.at(i);
            const textanim::FragmentProps &p = props(i);
            const QRectF rule(piece.cellRect.left() + p.dx, piece.baselineY + p.dy - rise - thickness * 0.5,
                              piece.cellRect.width(), thickness);
            const auto it = perLine.find(piece.line);
            if (it == perLine.end())
                perLine.insert(piece.line, rule);
            else
                *it = it->united(rule);
        }
        SkPaint fill;
        fill.setAntiAlias(true);
        fill.setColor(toSkColor(m_style.primaryColor()));
        for (const QRectF &rule : std::as_const(perLine))
            canvas.drawRect(toSkRect(rule), fill);
    }

    void drawUnderline(SkCanvas &canvas) const
    {
        drawRunUnderlines(canvas);
        if (m_bend.active || !m_style.underlineEnabled || m_style.underlineWidth <= 0.0)
            return;
        QHash<int, QRectF> perLine;
        for (int i = 0; i < m_pieces.size(); ++i) {
            if (!visible(i))
                continue;
            const Piece &piece = m_pieces.at(i);
            const textanim::FragmentProps &p = props(i);
            const QRectF rule(piece.cellRect.left() + p.dx, piece.baselineY + p.dy + m_style.underlineOffset * m_scale,
                              piece.cellRect.width(), m_style.underlineWidth * m_scale);
            const auto it = perLine.find(piece.line);
            if (it == perLine.end())
                perLine.insert(piece.line, rule);
            else
                *it = it->united(rule);
        }
        SkPaint fill;
        fill.setAntiAlias(true);
        fill.setColor(toSkColor(m_style.underlineColor));
        const float r = float(m_style.underlineWidth * m_scale * 0.5);
        for (const QRectF &rule : std::as_const(perLine))
            canvas.drawRoundRect(toSkRect(rule), r, r, fill);
    }

    // Letters underlined on their own (Texto avanzado's U): a thin rule under each piece, in the
    // piece's colour, like a word processor. Neighbouring pieces touch, so a run reads as one line.
    void drawRunUnderlines(SkCanvas &canvas) const
    {
        if (m_bend.active)
            return;
        const double width = qMax(1.0, m_style.pixelSize * 0.06) * m_scale;
        const double offset = qMax(1.0, m_style.pixelSize * 0.08) * m_scale;
        for (int i = 0; i < m_pieces.size(); ++i) {
            const Piece &piece = m_pieces.at(i);
            if (!piece.runUnderline || !visible(i))
                continue;
            const textanim::FragmentProps &p = props(i);
            const QRectF rule(piece.cellRect.left() + p.dx, piece.baselineY + p.dy + offset,
                              piece.cellRect.width(), width);
            SkPaint fill;
            fill.setAntiAlias(true);
            fill.setColor(toSkColor(piece.runColorSet ? piece.runColor : m_style.primaryColor()));
            canvas.drawRect(toSkRect(rule), fill);
        }
    }

    void drawCaret(SkCanvas &canvas) const
    {
        const textanim::CaretState &caret = m_frame.caret;
        if (!caret.visible || m_pieces.isEmpty())
            return;
        double x, baseline;
        if (caret.afterFragment >= 0 && caret.afterFragment < m_pieces.size()) {
            const Piece &piece = m_pieces.at(caret.afterFragment);
            x = piece.cellRect.right() + props(caret.afterFragment).dx;
            baseline = piece.baselineY + props(caret.afterFragment).dy;
        } else {
            const Piece &piece = m_pieces.first();
            x = piece.cellRect.left() + props(0).dx;
            baseline = piece.baselineY + props(0).dy;
        }
        if (caret.shape == TextCaret::Shape::Glyph) {
            const double size = caret.heightPx;
            SkPaint paint;
            paint.setAntiAlias(true);
            paint.setColor(toSkColor(caret.color));
            canvas.save();
            canvas.translate(float(x + caret.gapPx + size * 0.5), float(baseline - size * 0.35 + caret.bobPx));
            canvas.rotate(float(caret.swayDeg));
            drawSymbol(canvas, caret.glyph, size, paint, m_style.fontFamily);
            canvas.restore();
            return;
        }
        QRectF rect;
        switch (caret.shape) {
        case TextCaret::Shape::Bar:
            rect = QRectF(x, baseline - caret.heightPx * 0.8, qMax(1.0, caret.widthPx), caret.heightPx);
            break;
        case TextCaret::Shape::Underscore:
            rect = QRectF(x, baseline - caret.heightPx * 0.08, caret.heightPx * 0.6, qMax(1.0, caret.heightPx * 0.08));
            break;
        case TextCaret::Shape::Block:
            rect = QRectF(x, baseline - caret.heightPx * 0.8, caret.heightPx * 0.6, caret.heightPx);
            break;
        }
        SkPaint fill;
        fill.setAntiAlias(true);
        fill.setColor(toSkColor(withAlpha(caret.color, caret.shape == TextCaret::Shape::Block ? 0.5 : 1.0)));
        canvas.drawRect(toSkRect(rect), fill);
    }

    // The frame's live particles of one depth (behind the text, or over it).
    void drawParticles(SkCanvas &canvas, bool behind) const
    {
        if (m_frame.particles.isEmpty() || m_pieces.isEmpty())
            return;
        const QPointF blockCentre = m_set->ink.center();
        for (const textanim::ParticleState &p : m_frame.particles) {
            if (p.look < 0 || p.look >= m_frame.particleLooks.size() || p.alpha <= 0.002 || p.sizePx <= 0.05)
                continue;
            const TextParticleSpec &look = m_frame.particleLooks.at(p.look);
            if (look.behind != behind)
                continue;
            const QPointF anchor = p.fragment >= 0 && p.fragment < m_pieces.size()
                                       ? m_pieces.at(p.fragment).cellRect.center()
                                       : blockCentre;
            canvas.save();
            canvas.translate(float(anchor.x() + p.x), float(anchor.y() + p.y));
            SkPaint paint;
            paint.setAntiAlias(true);
            paint.setColor(toSkColor(withAlpha(p.color, p.alpha)));
            if (look.additive)
                paint.setBlendMode(SkBlendMode::kPlus);
            if (look.glow > 0.0) {
                SkPaint halo = paint;
                halo.setMaskFilter(SkMaskFilter::MakeBlur(kNormal_SkBlurStyle, float(qMax(0.5, p.sizePx * look.glow))));
                drawParticleShape(canvas, look, p, halo, 1.6);
            }
            drawParticleShape(canvas, look, p, paint, 1.0);
            canvas.restore();
        }
    }

    void drawParticleShape(SkCanvas &canvas, const TextParticleSpec &look, const textanim::ParticleState &p,
                           const SkPaint &base, double grow) const
    {
        const float r = float(p.sizePx * 0.5 * grow);
        SkPaint paint = base;
        switch (look.shape) {
        case TextParticleSpec::Shape::Dot:
            canvas.drawCircle(0, 0, r, paint);
            break;
        case TextParticleSpec::Shape::Star:
            canvas.rotate(float(p.rotation));
            canvas.drawPath(starPath(r, 5, 0.45), paint);
            break;
        case TextParticleSpec::Shape::Flare:
            canvas.rotate(float(p.rotation * 0.25));
            canvas.drawPath(starPath(r, 4, 0.16), paint);
            break;
        case TextParticleSpec::Shape::Spark: {
            // A streak along the direction of travel, longer the faster it goes.
            const float length = float(qBound(double(r) * 2.0, p.speedPx * 0.05, double(r) * 12.0));
            canvas.rotate(float(p.heading));
            paint.setStyle(SkPaint::kStroke_Style);
            paint.setStrokeCap(SkPaint::kRound_Cap);
            paint.setStrokeWidth(qMax(0.6f, r * 0.7f));
            canvas.drawLine(-length, 0, 0, 0, paint);
            break;
        }
        case TextParticleSpec::Shape::Ring:
            paint.setStyle(SkPaint::kStroke_Style);
            paint.setStrokeWidth(qMax(0.6f, r * 0.18f));
            canvas.drawCircle(0, 0, r, paint);
            break;
        case TextParticleSpec::Shape::Square:
            canvas.rotate(float(p.rotation));
            canvas.drawRect(SkRect::MakeLTRB(-r, -r, r, r), paint);
            break;
        case TextParticleSpec::Shape::Triangle:
            canvas.rotate(float(p.rotation));
            canvas.drawPath(polygonPath({{0, -r}, {r * 0.87f, r * 0.5f}, {-r * 0.87f, r * 0.5f}}), paint);
            break;
        case TextParticleSpec::Shape::Heart:
            canvas.rotate(float(std::sin(qDegreesToRadians(p.rotation)) * 20.0));
            canvas.drawPath(heartPath(r), paint);
            break;
        case TextParticleSpec::Shape::Confetti:
            // A paper strip tumbling: its height swings through zero as it flips.
            canvas.rotate(float(p.rotation));
            canvas.scale(1.0f, float(qMax(0.15, std::abs(std::cos(qDegreesToRadians(p.rotation * 2.0))))));
            canvas.drawRect(SkRect::MakeLTRB(-r, -r * 0.45f, r, r * 0.45f), paint);
            break;
        case TextParticleSpec::Shape::Smoke: {
            // A soft puff: the colour at the centre fading to nothing at the edge.
            const SkColor4f c = paint.getColor4f();
            const SkColor4f stops[] = {c, {c.fR, c.fG, c.fB, c.fA * 0.45f}, {c.fR, c.fG, c.fB, 0.0f}};
            const float pos[] = {0.0f, 0.5f, 1.0f};
            const SkGradient::Colors colors{SkSpan<const SkColor4f>(stops, 3), SkSpan<const float>(pos, 3),
                                            SkTileMode::kClamp};
            paint.setShader(SkShaders::RadialGradient(SkPoint::Make(0, 0), r,
                                                      SkGradient{colors, SkGradient::Interpolation{}}, nullptr));
            paint.setColor4f({1, 1, 1, 1});
            paint.setMaskFilter(nullptr);
            canvas.drawCircle(0, 0, r, paint);
            break;
        }
        case TextParticleSpec::Shape::Glyph:
            canvas.rotate(float(p.rotation));
            drawSymbol(canvas, look.glyph, r * 2.0, paint, m_style.fontFamily);
            break;
        }
    }

    QSize m_size;
    quint64 m_key;
    TextStyle m_style;
    double m_scale;
    std::shared_ptr<const text::FragmentSet> m_set;
    std::shared_ptr<const BlockGeometry> m_geometry;
    textanim::Frame m_frame;
    Bend m_bend;
    double m_bleed;
    double m_timeSec;
    TextAnchorGrouping m_grouping;
    QPointF m_alignment;
    QList<Piece> m_pieces;
    QList<SkMatrix> m_matrices;
    double m_strokeWidthPx = 0.0;
    QVector<double> m_pieceStrokePx;
};

// Selection, preedit underline and caret over a laid-out block; see TextEditPaintRequest.
class TextEditPainter final : public VectorPainter
{
public:
    TextEditPainter(QSize size, double bleed, const TextEditPaintRequest &request, QList<QRectF> selection,
                    QList<QRectF> preedit, QRectF caret, double emPx)
        : m_size(size), m_bleed(bleed), m_request(request), m_selection(std::move(selection)),
          m_preedit(std::move(preedit)), m_caret(caret), m_emPx(emPx)
    {
        m_request.set.reset();
    }

    QSize size() const override { return m_size; }
    quint64 cacheKey() const override { return 0; }

    void paint(SkCanvas &canvas) const override
    {
        canvas.translate(float(m_bleed), float(m_bleed));
        const double scale = m_request.renderScale;
        SkPaint paint;
        paint.setAntiAlias(true);

        QColor selectionColor = m_request.selectionColor;
        if (!selectionColor.isValid())
            selectionColor = QColor(0x3D, 0x7C, 0xFF, 89);
        paint.setColor(toSkColor(selectionColor));
        for (const QRectF &rect : m_selection)
            canvas.drawRect(toSkRect(rect), paint);

        QColor caretColor = m_request.caretColor.isValid() ? m_request.caretColor : QColor(Qt::white);
        if (!m_preedit.isEmpty()) {
            const double thickness = qMax(1.5, qMax(2.0 * scale, 0.04 * m_emPx) * 0.5);
            paint.setColor(toSkColor(caretColor));
            for (const QRectF &rect : m_preedit)
                canvas.drawRect(toSkRect(QRectF(rect.left(), rect.bottom() - thickness * 2.0, rect.width(), thickness)),
                                paint);
        }

        if (m_request.cursor >= 0 && m_caret.height() > 0.0) {
            // Never thinner than a device pixel and a half, whatever the preview scale.
            const double width = qMax(1.5, qMax(2.0 * scale, 0.06 * m_emPx));
            const QRectF bar(m_caret.x() - width * 0.5, m_caret.y(), width, m_caret.height());
            paint.setColor(SkColorSetARGB(160, 0, 0, 0));
            canvas.drawRect(toSkRect(bar.adjusted(-1.0, -1.0, 1.0, 1.0)), paint);
            paint.setColor(toSkColor(caretColor));
            canvas.drawRect(toSkRect(bar), paint);
        }
    }

private:
    QSize m_size;
    double m_bleed;
    TextEditPaintRequest m_request;
    QList<QRectF> m_selection;
    QList<QRectF> m_preedit;
    QRectF m_caret;
    double m_emPx;
};

} // namespace

TextPainterResult makeTextEditPainter(const TextEditPaintRequest &request)
{
    if (!request.set || !request.set->paragraph || request.layoutRect.width() < 1.0 || request.layoutRect.height() < 1.0)
        return {};
    const text::FragmentSet &set = *request.set;
    QList<QRectF> selection;
    if (request.selStart >= 0 && request.selEnd >= 0 && request.selStart != request.selEnd)
        selection = text::selectionRects(set, request.selStart, request.selEnd);
    QList<QRectF> preedit;
    if (request.preeditStart >= 0 && request.preeditLength > 0)
        preedit = text::selectionRects(set, request.preeditStart, request.preeditStart + request.preeditLength);
    const QRectF caret = request.cursor >= 0 ? text::caretRect(set, request.cursor) : QRectF();

    // The decorations may sit outside the layout rect (an overflowing line, a caret at its edge),
    // so the image grows to hold them.
    const QRectF box(0.0, 0.0, request.layoutRect.width(), request.layoutRect.height());
    QRectF reach = box;
    for (const QRectF &rect : selection)
        reach = reach.united(rect);
    for (const QRectF &rect : preedit)
        reach = reach.united(rect);
    if (!caret.isNull() || caret.height() > 0.0)
        reach = reach.united(caret);
    const double emPx = set.paragraph->emPx;
    const double bleed = std::ceil(qMax(qMax(-reach.left(), reach.right() - box.width()),
                                        qMax(-reach.top(), reach.bottom() - box.height()))
                                   + qMax(2.0 * request.renderScale, 0.06 * emPx) + 3.0);
    const int imageW = qMax(1, qRound(box.width() + bleed * 2.0));
    const int imageH = qMax(1, qRound(box.height() + bleed * 2.0));

    TextPainterResult result;
    result.rect = QRectF(request.layoutRect.x() - bleed, request.layoutRect.y() - bleed, imageW, imageH);
    result.painter = std::make_shared<TextEditPainter>(QSize(imageW, imageH), bleed, request, std::move(selection),
                                                       std::move(preedit), caret, emPx);
    return result;
}

TextPainterResult makeTextPainter(const TextPaintRequest &request)
{
    if (!request.set || request.set->frags.isEmpty() || request.layoutRect.width() < 1.0
        || request.layoutRect.height() < 1.0)
        return {};
    const TextStyle &style = request.style;
    const double scale = request.renderScale;

    // The static bleed plus how far the animators can throw a fragment: the image size must not
    // depend on time, or the hold-phase cache key would.
    double maxCell = 0.0;
    int lines = 1;
    for (const text::StyledWord &w : request.set->frags) {
        maxCell = qMax(maxCell, qMax(w.cellRect.width(), w.cellRect.height()));
        lines = qMax(lines, w.line + 1);
    }
    const textanim::Bounds &env = request.envelope;
    // A turn in depth brings the near edge closer, a quarter bigger at most at the distance used.
    const double rotationPad = (env.maxRotationDeg > 0.0 ? maxCell * 0.5 : 0.0)
                               + (env.maxRotation3dDeg > 0.0 ? maxCell * 0.25 : 0.0);
    const double envelope = qMax(env.maxDx, env.maxDy) + env.maxBlurPx * 2.0 + (env.maxScale - 1.0) * maxCell * 0.5
                            + rotationPad + env.maxTrackingPx * lines * 0.5 + env.maxParticlePx;
    const Bend bend = bendFor(request.set->frags, style, scale, request.layoutRect.size());
    // Around a circle the letters reach a diameter beyond the line, plus a letter's height; on an
    // outline, as far as the outline leaves the box (and what an open end carries on), plus that.
    double circleReach = 0.0;
    if (bend.contour) {
        QPainterPath outline;
        drift::parseSvgPathData(style.pathSvg, &outline);
        const QRectF b = QTransform::fromScale(request.layoutRect.width() / 100.0, request.layoutRect.height() / 100.0)
                             .map(outline)
                             .boundingRect();
        const double out = qMax(qMax(-b.left(), -b.top()), qMax(b.right() - request.layoutRect.width(),
                                                                 b.bottom() - request.layoutRect.height()));
        circleReach = qMax(0.0, out) + maxCell + (bend.contour->isClosed() ? 0.0 : bend.width);
    } else if (style.pathCircle > 0.5 && bend.active) {
        circleReach = 2.0 * bend.radius + maxCell;
    }
    const double bleed = std::ceil(text::bleedFor(style) * scale + envelope + circleReach) + 2.0;
    const int imageW = qMax(1, qRound(request.layoutRect.width() + bleed * 2.0));
    const int imageH = qMax(1, qRound(request.layoutRect.height() + bleed * 2.0));

    TextPainterResult result;
    result.rect = QRectF(request.layoutRect.x() - bleed, request.layoutRect.y() - bleed, imageW, imageH);
    result.block = request.frame.block;

    std::shared_ptr<const BlockGeometry> geometry = geometryFor(*request.set);

    const bool cacheable = request.frame.isStatic && !style.isAnimated() && !timeDrivenPaint(style) && !style.counter;
    const quint64 key = cacheable ? qHashMulti(request.set->key, text::styleHash(style), imageW, imageH,
                                               qRound(scale * 1000.0), request.frame.poseHash)
                                  : 0;
    result.painter = std::make_shared<AnimatedTextPainter>(QSize(imageW, imageH), key, request, std::move(geometry),
                                                           bend, bleed);
    return result;
}

TextPainterResult makeTextPainter(const Clip &clip, const QString &text, const QRectF &layoutRect,
                                  double renderScale, int activeWordIndex, TimeUs clipTimeUs)
{
    if (text.isEmpty())
        return {};
    const TimeUs window = clip.timelineDuration > 0 ? clip.timelineDuration : secondsToUs(3.0);
    const TimeUs t = clipTimeUs < 0 ? window / 2 : clipTimeUs;
    TextPaintRequest request;
    request.style = clip.textStyle.isAnimated() ? clip.textStyle.resolvedAt(t) : clip.textStyle;
    const ResolvedTextAnimation anim = resolveTextAnimation(request.style.animation);
    // An animated counter shows its number at this point of the clip.
    const double land = request.style.counterSeconds > 0.0
                            ? std::min(1.0, secondsToUs(request.style.counterSeconds) / double(window))
                            : 0.85;
    const QString shown = request.style.counter
                              ? drift::counterTextAt(text, request.style.counterFrom, double(t) / double(window), land)
                              : text;
    request.set = text::fragmentsFor(shown, request.style, layoutRect.width(), layoutRect.height(), renderScale,
                                     activeWordIndex, text::splitFor(anim.resolved, request.style));
    if (!request.set || request.set->frags.isEmpty())
        return {};
    const textanim::EvalContext ctx =
        text::evalContextFor(request.style, layoutRect, renderScale, 0, window, t, activeWordIndex);
    request.frame = textanim::evaluateTextAnimation(anim.set, anim.resolved, request.set->infos, request.set->domains, ctx);
    request.envelope = textanim::animationBounds(anim.resolved, ctx, &anim.set.caret);
    request.layoutRect = layoutRect;
    request.renderScale = renderScale;
    request.timeSec = usToSeconds(t);
    request.anchorGrouping = anim.set.anchorGrouping;
    request.anchorAlignment = anim.set.anchorAlignment;
    return makeTextPainter(request);
}

void clearTextGeometryCache()
{
    QMutexLocker lock(&g_geometryMutex);
    g_geometryCache.clear();
    clearTextEffectCaches();
}

} // namespace drift::skia
