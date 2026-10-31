#include "SkiaShapePainter.h"

#include "SkiaPath.h"
#include "SkiaShading.h"
#include "core/ShapePath.h"
#include "core/ShapePathEdit.h"

#include <QtMath>

#include <cmath>

#include "include/core/SkCanvas.h"
#include "include/core/SkClipOp.h"
#include "include/core/SkPathBuilder.h"
#include "include/core/SkStrokeRec.h"
#include "include/effects/SkCornerPathEffect.h"
#include "include/core/SkPathMeasure.h"
#include "include/core/SkContourMeasure.h"
#include "include/effects/SkTrimPathEffect.h"
#include "include/pathops/SkPathOps.h"

namespace drift::skia {

namespace {

// The rect family rounds its own corners in shapePath(); every other kind gets the same radius
// as a corner path effect over its polygon. An ellipse has no corners to round.
bool nativeCornerKind(ShapeKind kind)
{
    switch (kind) {
    case ShapeKind::RoundedRectangle:
    case ShapeKind::SpeechBubbleRect:
    case ShapeKind::Callout:
    case ShapeKind::Ellipse:
        return true;
    default:
        return false;
    }
}

// How far a stroke layer reaches outside the outline, as a multiple of its width.
double strokeReachFactor(StrokeAlign align)
{
    switch (align) {
    case StrokeAlign::Center:
        return 0.5;
    case StrokeAlign::Outside:
        return 1.0;
    case StrokeAlign::Inside:
        return 0.0;
    }
    return 0.5;
}

double widestOutwardStroke(const ShapeStyle &style)
{
    double widest = 0.0;
    for (const TextShadingLayer &layer : style.layers) {
        if (layer.enabled && layer.kind == TextLayerKind::Stroke)
            widest = qMax(widest, layer.width * strokeReachFactor(layer.strokeAlign));
    }
    return widest;
}

// Wiggle Paths (0.26): every contour resampled each `detail` px, each sample pushed along its normal
// by a noise that is smooth both along the outline and in time (`phase` = seconds × wiggles/s),
// then joined through the midpoints so the result stays round rather than jagged.
SkPath wiggledPath(const SkPath &path, double size, double detail, double phase, double seed)
{
    if (size <= 0.0 || detail <= 0.0)
        return path;
    const double s1 = std::fmod(seed * 12.9898, 6.2831853);
    const double s2 = std::fmod(seed * 78.233, 6.2831853);
    const double s3 = std::fmod(seed * 37.719, 6.2831853);
    const double t = phase * 6.2831853;
    const auto noise = [&](double u) {
        return 0.5 * std::sin(u * 1.00 + s1 + t) + 0.3 * std::sin(u * 2.31 + s2 - 1.37 * t)
               + 0.2 * std::sin(u * 0.57 + s3 + 0.71 * t);
    };
    SkPathBuilder out;
    SkPathMeasure measure(path, false);
    do {
        const double length = measure.getLength();
        if (length <= 0.0)
            continue;
        const bool closed = measure.isClosed();
        const int count = qMax(4, int(std::ceil(length / detail)));
        std::vector<SkPoint> pts;
        pts.reserve(count + 1);
        const int last = closed ? count - 1 : count;
        for (int i = 0; i <= last; ++i) {
            SkPoint pos;
            SkVector tan;
            if (!measure.getPosTan(float(length * i / count), &pos, &tan))
                continue;
            // The ends of an open outline stay where they are, as AE keeps them pinned.
            const double push = (!closed && (i == 0 || i == last)) ? 0.0 : size * noise(i * 0.35);
            pts.push_back({float(pos.x() - tan.y() * push), float(pos.y() + tan.x() * push)});
        }
        if (pts.size() < 2)
            continue;
        if (closed) {
            const auto mid = [](const SkPoint &a, const SkPoint &b) {
                return SkPoint{(a.x() + b.x()) * 0.5f, (a.y() + b.y()) * 0.5f};
            };
            const size_t n = pts.size();
            out.moveTo(mid(pts[n - 1], pts[0]));
            for (size_t i = 0; i < n; ++i)
                out.quadTo(pts[i], mid(pts[i], pts[(i + 1) % n]));
            out.close();
        } else {
            out.moveTo(pts.front());
            for (size_t i = 1; i < pts.size(); ++i)
                out.lineTo(pts[i]);
        }
    } while (measure.nextContour());
    SkPath result = out.detach();
    result.setFillType(path.getFillType());
    return result;
}

// The path's contours as separate paths.
std::vector<SkPath> splitContours(const SkPath &path)
{
    std::vector<SkPath> out;
    SkPathBuilder current;
    bool open = false;
    SkPath::Iter iter(path, false);
    SkPoint pts[4];
    for (SkPath::Verb verb = iter.next(pts); verb != SkPath::kDone_Verb; verb = iter.next(pts)) {
        switch (verb) {
        case SkPath::kMove_Verb:
            if (open)
                out.push_back(current.detach());
            current.moveTo(pts[0]);
            open = true;
            break;
        case SkPath::kLine_Verb:
            current.lineTo(pts[1]);
            break;
        case SkPath::kQuad_Verb:
            current.quadTo(pts[1], pts[2]);
            break;
        case SkPath::kConic_Verb:
            current.conicTo(pts[1], pts[2], iter.conicWeight());
            break;
        case SkPath::kCubic_Verb:
            current.cubicTo(pts[1], pts[2], pts[3]);
            break;
        case SkPath::kClose_Verb:
            current.close();
            break;
        default:
            break;
        }
    }
    if (open)
        out.push_back(current.detach());
    return out;
}

// Merge Paths (0.26): each contour combined with the result so far, as After Effects' modes.
SkPath mergedPath(const SkPath &path, int mode)
{
    const std::vector<SkPath> parts = splitContours(path);
    if (parts.size() < 2 || mode <= 0)
        return path;
    const SkPathOp op = mode == 2 ? kDifference_SkPathOp : mode == 3 ? kIntersect_SkPathOp
                      : mode == 4 ? kXOR_SkPathOp : kUnion_SkPathOp;
    SkPath result = parts.front();
    for (size_t i = 1; i < parts.size(); ++i) {
        SkPath next;
        if (Op(result, parts[i], op, &next))
            result = next;
    }
    return result;
}

// Offset Paths (0.26): the outline grown (or shrunk) by `amount` px, with round joins.
SkPath offsetOutline(const SkPath &path, double amount)
{
    if (qAbs(amount) < 0.01)
        return path;
    SkStrokeRec rec(SkStrokeRec::kFill_InitStyle);
    rec.setStrokeStyle(float(qAbs(amount) * 2.0));
    rec.setStrokeParams(SkPaint::kRound_Cap, SkPaint::kRound_Join, 4.0f);
    SkPathBuilder ring;
    if (!rec.applyToPath(&ring, path))
        return path;
    SkPath result;
    if (!Op(path, ring.detach(), amount > 0 ? kUnion_SkPathOp : kDifference_SkPathOp, &result))
        return path;
    return result;
}

// Pucker & Bloat (0.26), as After Effects: `amount` (percent, -100..100) pulls every vertex towards
// the centre of the vertices and pushes its handles away (positive: bloat, petals swelling out), or
// the other way round (negative: pucker, points drawn out to spikes). Straight sides count as curves
// whose handles sit on their vertices, so a polygon turns into a flower as in AE.
SkPath puckerBloated(const SkPath &path, double amount)
{
    const float k = float(amount / 100.0);
    if (qAbs(k) < 1e-4)
        return path;
    struct Seg { bool move = false, close = false; SkPoint a, b, c, d; };
    std::vector<Seg> segs;
    double sx = 0.0, sy = 0.0;
    int n = 0;
    SkPoint last{0, 0};
    SkPath::Iter iter(path, false);
    SkPoint pts[4];
    const auto cubic = [&](SkPoint b, SkPoint c, SkPoint d) {
        Seg s;
        s.a = last; s.b = b; s.c = c; s.d = d;
        segs.push_back(s);
        last = d;
        sx += d.x(); sy += d.y(); ++n;
    };
    const auto quad = [&](SkPoint q, SkPoint d) {
        cubic(last + (q - last) * (2.0f / 3.0f), d + (q - d) * (2.0f / 3.0f), d);
    };
    for (SkPath::Verb verb = iter.next(pts); verb != SkPath::kDone_Verb; verb = iter.next(pts)) {
        switch (verb) {
        case SkPath::kMove_Verb: {
            Seg s;
            s.move = true;
            s.d = pts[0];
            segs.push_back(s);
            last = pts[0];
            sx += last.x(); sy += last.y(); ++n;
            break;
        }
        case SkPath::kLine_Verb:
            cubic(last, pts[1], pts[1]);
            break;
        case SkPath::kQuad_Verb:
            quad(pts[1], pts[2]);
            break;
        case SkPath::kConic_Verb: {
            SkPoint q[1 + 2 * 4];
            const int count = SkPath::ConvertConicToQuads(pts[0], pts[1], pts[2], iter.conicWeight(), q, 2);
            for (int i = 0; i < count; ++i)
                quad(q[1 + 2 * i], q[2 + 2 * i]);
            break;
        }
        case SkPath::kCubic_Verb:
            cubic(pts[1], pts[2], pts[3]);
            break;
        case SkPath::kClose_Verb: {
            Seg s;
            s.close = true;
            segs.push_back(s);
            break;
        }
        default:
            break;
        }
    }
    if (n == 0)
        return path;
    const SkPoint centre{float(sx / n), float(sy / n)};
    const auto vertex = [&](SkPoint p) { return p + (centre - p) * k; };
    const auto handle = [&](SkPoint p) { return p - (centre - p) * k; };
    SkPathBuilder out;
    for (const Seg &s : segs) {
        if (s.move)
            out.moveTo(vertex(s.d));
        else if (s.close)
            out.close();
        else
            out.cubicTo(handle(s.b), handle(s.c), vertex(s.d));
    }
    SkPath result = out.detach();
    result.setFillType(path.getFillType());
    return result;
}

// Zig Zag and Twist (0.26): every contour resampled, each point pushed alternately either side of
// the outline (zig zag), then turned about `centre` by twist × its distance from the centre over
// the farthest one.
SkPath zigzagTwisted(const SkPath &path, double size, int ridges, bool smooth, double twistDeg, SkPoint centre)
{
    const bool zig = size > 0.0;
    const bool twist = qAbs(twistDeg) > 1e-6;
    if (!zig && !twist)
        return path;
    double farthest = 1.0;
    {
        const SkRect b = path.getBounds();
        for (const SkPoint corner : {SkPoint{b.left(), b.top()}, SkPoint{b.right(), b.top()},
                                     SkPoint{b.right(), b.bottom()}, SkPoint{b.left(), b.bottom()}})
            farthest = qMax(farthest, double(SkPoint::Distance(corner, centre)));
    }
    SkPathBuilder out;
    SkPathMeasure measure(path, false);
    do {
        const double length = measure.getLength();
        if (length <= 0.0)
            continue;
        const bool closed = measure.isClosed();
        // Two points per ridge for the zig zag; dense enough to bend smoothly for a twist.
        const int count = zig ? qMax(2, ridges * 2) : qMax(16, int(std::ceil(length / 6.0)));
        std::vector<SkPoint> pts;
        const int last = closed ? count - 1 : count;
        for (int i = 0; i <= last; ++i) {
            SkPoint pos;
            SkVector tan;
            if (!measure.getPosTan(float(length * i / count), &pos, &tan))
                continue;
            if (zig) {
                const double side = (i % 2 == 0 ? 1.0 : -1.0) * size;
                pos = {float(pos.x() - tan.y() * side), float(pos.y() + tan.x() * side)};
            }
            if (twist) {
                const double dx = pos.x() - centre.x();
                const double dy = pos.y() - centre.y();
                const double a = qDegreesToRadians(twistDeg) * std::hypot(dx, dy) / farthest;
                pos = {float(centre.x() + dx * std::cos(a) - dy * std::sin(a)),
                       float(centre.y() + dx * std::sin(a) + dy * std::cos(a))};
            }
            pts.push_back(pos);
        }
        if (pts.size() < 2)
            continue;
        if (smooth || (!zig && twist)) {
            const auto mid = [](const SkPoint &a, const SkPoint &b) {
                return SkPoint{(a.x() + b.x()) * 0.5f, (a.y() + b.y()) * 0.5f};
            };
            const size_t n = pts.size();
            if (closed) {
                out.moveTo(mid(pts[n - 1], pts[0]));
                for (size_t i = 0; i < n; ++i)
                    out.quadTo(pts[i], mid(pts[i], pts[(i + 1) % n]));
                out.close();
            } else {
                out.moveTo(pts.front());
                for (size_t i = 1; i + 1 < n; ++i)
                    out.quadTo(pts[i], mid(pts[i], pts[i + 1]));
                out.lineTo(pts.back());
            }
        } else {
            out.moveTo(pts.front());
            for (size_t i = 1; i < pts.size(); ++i)
                out.lineTo(pts[i]);
            if (closed)
                out.close();
        }
    } while (measure.nextContour());
    SkPath result = out.detach();
    result.setFillType(path.getFillType());
    return result;
}

// Trim Paths (0.26): start and end in percent, the offset in degrees (once round = 360°), wrapping
// past the outline's end the way After Effects does.
SkPath trimmedPath(const SkPath &path, double startPct, double endPct, double offsetDeg, int segments, bool reverse)
{
    double a = qBound(0.0, startPct, 100.0) / 100.0;
    double b = qBound(0.0, endPct, 100.0) / 100.0;
    if (a > b)
        std::swap(a, b);
    double shift = offsetDeg / 360.0;
    if (reverse) {
        const double ra = 1.0 - b;
        b = 1.0 - a;
        a = ra;
        shift = -shift;
    }
    // Each contour on its own, as After Effects' default (Simultaneously).
    return trimEachContour(path, a + shift, b + shift, segments);
}

// Repeater (0.26): copy `index` (fractional with the offset) of a w × h box, in box px: moved,
// turned and scaled from its centre, each step compounding as in After Effects.
SkMatrix repeaterMatrix(const ShapeStyle &style, double index, double w, double h, double scale)
{
    SkMatrix m;
    m.setTranslate(float(-w / 2.0), float(-h / 2.0));
    // A floor above 0: Scale 0 with a negative offset (index < 0) gave pow(0, -n) = infinity.
    const double factor = std::pow(qMax(0.001, style.repeatScale / 100.0), index);
    m.postScale(float(factor), float(factor));
    m.postRotate(float(style.repeatRotation * index));
    m.postTranslate(float(w / 2.0 + style.repeatX * index * scale), float(h / 2.0 + style.repeatY * index * scale));
    return m;
}

// How far the repeater's copies reach outside the w × h box, in box px.
double repeaterReach(const ShapeStyle &style, double w, double h, double scale)
{
    if (!style.hasRepeater())
        return 0.0;
    const int copies = qBound(1, qRound(style.repeatCopies), 200);
    double reach = 0.0;
    for (int k = 0; k < copies; ++k) {
        const SkMatrix m = repeaterMatrix(style, k + style.repeatOffset, w, h, scale);
        for (const SkPoint corner : {SkPoint{0, 0}, SkPoint{float(w), 0}, SkPoint{float(w), float(h)}, SkPoint{0, float(h)}}) {
            const SkPoint p = m.mapPoint(corner);
            reach = qMax(reach, qMax(qMax(-double(p.x()), double(p.x()) - w), qMax(-double(p.y()), double(p.y()) - h)));
        }
    }
    return reach;
}

// After Effects' Taper and Wave (0.28): the stroke drawn as a filled outline whose width follows a profile along
// the path (thinner towards a tapered end, rising and falling with the wave). Each contour is walked in short steps
// and offset both ways along its normal; an open one becomes one band, a closed one a ring.
bool strokeHasProfile(const TextShadingLayer &layer)
{
    return layer.taperStartLength > 0.0 || layer.taperEndLength > 0.0 || layer.waveAmount > 0.0;
}

SkPath profiledStroke(const SkPath &path, double width, const TextShadingLayer &layer, double scale)
{
    SkPathBuilder out;
    out.setFillType(SkPathFillType::kEvenOdd);
    SkContourMeasureIter iter(path, false, 1.0f);
    const double ease = qBound(0.0, layer.taperEase / 100.0, 1.0);
    const auto shape = [ease](double t) {
        // 0..1 → 0..1, straight, or rounded off towards the full width with the ease.
        t = qBound(0.0, t, 1.0);
        const double smooth = 1.0 - (1.0 - t) * (1.0 - t);
        return t + (smooth - t) * ease;
    };
    while (sk_sp<SkContourMeasure> cm = iter.next()) {
        const double len = cm->length();
        if (len <= 0.0)
            continue;
        const double ts = layer.taperStartLength / 100.0, te = layer.taperEndLength / 100.0;
        const double ws = layer.taperStartWidth / 100.0, we = layer.taperEndWidth / 100.0;
        const double wave = qBound(0.0, layer.waveAmount / 100.0, 1.0);
        const double waveLen = qMax(1.0, layer.waveLength * scale);
        const double phase = qDegreesToRadians(layer.wavePhase);
        const int steps = qBound(8, int(std::ceil(len / 1.5)), 6000);
        std::vector<SkPoint> left, right;
        left.reserve(size_t(steps) + 1);
        right.reserve(size_t(steps) + 1);
        for (int i = 0; i <= steps; ++i) {
            const double d = len * i / steps;
            const double f = d / len;
            double k = 1.0;
            if (ts > 0.0 && f < ts)
                k = qMin(k, ws + (1.0 - ws) * shape(f / ts));
            if (te > 0.0 && f > 1.0 - te)
                k = qMin(k, we + (1.0 - we) * shape((1.0 - f) / te));
            if (wave > 0.0)
                k *= 1.0 - wave * 0.5 * (1.0 - std::cos(2.0 * M_PI * d / waveLen + phase));
            const double half = width * k / 2.0;
            SkPoint p;
            SkVector tan;
            if (!cm->getPosTan(float(d), &p, &tan))
                continue;
            const SkVector n{-tan.y(), tan.x()};
            left.push_back({p.x() + n.x() * float(half), p.y() + n.y() * float(half)});
            right.push_back({p.x() - n.x() * float(half), p.y() - n.y() * float(half)});
        }
        if (left.size() < 2)
            continue;
        if (cm->isClosed()) {
            out.addPolygon({left.data(), left.size()}, true);
            out.addPolygon({right.data(), right.size()}, true);
        } else {
            std::vector<SkPoint> band(left);
            band.insert(band.end(), right.rbegin(), right.rend());
            out.addPolygon({band.data(), band.size()}, true);
        }
    }
    return out.detach();
}

class ShapePainter final : public VectorPainter
{
public:
    ShapePainter(const ShapeStyle &style, int width, int height, double renderScale, double timeSec, double bleedPx)
        : m_style(style), m_scale(renderScale), m_timeSec(timeSec), m_bleed(bleedPx),
          m_size(qMax(1, qRound(width + bleedPx * 2.0)), qMax(1, qRound(height + bleedPx * 2.0)))
    {
        m_style.keyframes.clear();
        const bool cacheable = !style.isAnimated() && !shapeTimeDrivenPaint(style);
        m_key = cacheable ? (qHashMulti(shapeStyleHash(style), width, height, qRound(renderScale * 1000.0)) | 1) : 0;

        ShapeStyle scaled = m_style;
        scaled.cornerRadius = m_style.cornerRadius * m_scale;
        const SkPath outline = toSkPath(shapePath(scaled, QRectF(0, 0, width, height)));
        if (!nativeCornerKind(scaled.kind) && scaled.cornerRadius > 0.0) {
            SkPathBuilder rounded;
            SkStrokeRec rec(SkStrokeRec::kFill_InitStyle);
            if (SkCornerPathEffect::Make(float(scaled.cornerRadius))->filterPath(&rounded, outline, &rec))
                m_path = rounded.detach();
            else
                m_path = outline;
        } else {
            m_path = outline;
        }
        m_silhouetteStrokePx = widestOutwardStroke(style) * m_scale * 2.0;
        m_boxW = width;
        m_boxH = height;
        // After Effects' order down the stack: merge, offset, pucker & bloat, zig zag / twist, wiggle, trim.
        if (m_style.mergeMode >= 0.5)
            m_path = mergedPath(m_path, qRound(m_style.mergeMode));
        if (qAbs(m_style.offsetPath) >= 0.01)
            m_path = offsetOutline(m_path, m_style.offsetPath * m_scale);
        if (qAbs(m_style.puckerBloat) > 1e-6)
            m_path = puckerBloated(m_path, m_style.puckerBloat);
        if (m_style.zigzagSize > 0.0 || qAbs(m_style.twistAngle) > 1e-6)
            m_path = zigzagTwisted(m_path, m_style.zigzagSize * m_scale, qRound(m_style.zigzagRidges),
                                   m_style.zigzagSmooth >= 0.5, m_style.twistAngle,
                                   SkPoint{float(width / 2.0), float(height / 2.0)});
        if (m_style.hasWiggle())
            m_path = wiggledPath(m_path, m_style.wiggleSize * m_scale, m_style.wiggleDetail * m_scale,
                                 m_timeSec * m_style.wiggleSpeed, m_style.wiggleSeed);
        if (m_style.hasTrim() || !qFuzzyIsNull(m_style.trimOffset))
            m_path = trimmedPath(m_path, m_style.trimStart, m_style.trimEnd, m_style.trimOffset,
                                 qRound(m_style.trimSegments), m_style.trimReverse > 0.5);
    }

    QSize size() const override { return m_size; }
    quint64 cacheKey() const override { return m_key; }

    void paint(SkCanvas &canvas) const override
    {
        canvas.translate(float(m_bleed), float(m_bleed));
        if (m_path.isEmpty())
            return;
        const SkRect bounds = m_path.getBounds();
        const QRectF box(bounds.left(), bounds.top(), bounds.width(), bounds.height());
        if (!m_style.hasRepeater()) {
            drawLayers(canvas, box);
            return;
        }
        // The last copy first, so the original sits on top (After Effects' "Below" composite).
        const int copies = qBound(1, qRound(m_style.repeatCopies), 200);
        for (int k = copies - 1; k >= 0; --k) {
            const double f = copies > 1 ? double(k) / double(copies - 1) : 0.0;
            const double alpha = qBound(0.0, (m_style.repeatStartOpacity + (m_style.repeatEndOpacity - m_style.repeatStartOpacity) * f) / 100.0, 1.0);
            if (alpha <= 0.0)
                continue;
            canvas.save();
            canvas.concat(repeaterMatrix(m_style, k + m_style.repeatOffset, m_boxW, m_boxH, m_scale));
            if (alpha < 1.0)
                canvas.saveLayerAlphaf(nullptr, float(alpha));
            drawLayers(canvas, box);
            if (alpha < 1.0)
                canvas.restore();
            canvas.restore();
        }
    }

private:
    void drawLayers(SkCanvas &canvas, const QRectF &box) const
    {
        for (const TextShadingLayer &layer : m_style.layers) {
            if (!layer.enabled || layer.opacity <= 0.0)
                continue;
            const ShadingLayerGroup group = beginShadingLayer(canvas, layer, m_scale);
            canvas.save();
            canvas.translate(float(layer.offsetX * m_scale), float(layer.offsetY * m_scale));
            drawLayer(canvas, layer, box);
            canvas.restore();
            endShadingLayer(canvas, group);
        }
    }

    void drawLayer(SkCanvas &canvas, const TextShadingLayer &layer, const QRectF &box) const
    {
        SkPaint paint;
        paint.setAntiAlias(true);
        switch (layer.kind) {
        case TextLayerKind::Fill:
            applyShadingPaint(paint, layer.paint, box, m_timeSec, 1.0);
            paint.setPathEffect(fillPathEffectFor(layer, m_scale));
            canvas.drawPath(m_path, paint);
            break;
        case TextLayerKind::Stroke: {
            const double width = layer.width * m_scale;
            if (width <= 0.0)
                break;
            applyShadingPaint(paint, layer.paint, box, m_timeSec, 1.0);
            paint.setStyle(SkPaint::kStroke_Style);
            paint.setStrokeJoin(skStrokeJoin(layer.join));
            paint.setStrokeCap(skStrokeCap(layer.cap));
            paint.setStrokeMiter(float(layer.miterLimit));
            paint.setPathEffect(strokePathEffectFor(layer, width, m_scale));
            const SkPath stroked = strokedPathFor(layer, m_path);
            if (strokeHasProfile(layer)) {
                // Taper / Wave: the outline filled; inside or outside keeps one side of a twice-as-wide band.
                paint.setStyle(SkPaint::kFill_Style);
                paint.setPathEffect(nullptr);
                const bool centred = layer.strokeAlign == StrokeAlign::Center;
                const SkPath band = profiledStroke(stroked, centred ? width : width * 2.0, layer, m_scale);
                if (centred) {
                    canvas.drawPath(band, paint);
                    break;
                }
                canvas.save();
                canvas.clipPath(m_path, layer.strokeAlign == StrokeAlign::Inside ? SkClipOp::kIntersect : SkClipOp::kDifference,
                                true);
                canvas.drawPath(band, paint);
                canvas.restore();
                break;
            }
            if (layer.strokeAlign == StrokeAlign::Center) {
                paint.setStrokeWidth(float(width));
                canvas.drawPath(stroked, paint);
                break;
            }
            // A centred stroke of twice the width, clipped to one side of the outline, is the
            // half that grows purely outward or purely inward.
            paint.setStrokeWidth(float(width * 2.0));
            canvas.save();
            canvas.clipPath(m_path, layer.strokeAlign == StrokeAlign::Inside ? SkClipOp::kIntersect : SkClipOp::kDifference,
                            true);
            canvas.drawPath(stroked, paint);
            canvas.restore();
            break;
        }
        case TextLayerKind::Shadow:
        case TextLayerKind::Glow:
            // Silhouettes: the outline grown by the widest outward stroke, in the layer's colour.
            paint.setColor(toSkColor(layer.paint.color));
            canvas.drawPath(m_path, paint);
            if (m_silhouetteStrokePx > 0.0) {
                paint.setStyle(SkPaint::kStroke_Style);
                paint.setStrokeWidth(float(m_silhouetteStrokePx));
                paint.setStrokeJoin(SkPaint::kRound_Join);
                canvas.drawPath(m_path, paint);
            }
            break;
        case TextLayerKind::Extrude: {
            const int steps = qMax(1, layer.extrudeSteps);
            const double rad = qDegreesToRadians(layer.extrudeAngle);
            const double depth = layer.width * m_scale;
            for (int k = steps; k >= 1; --k) {
                const double f = double(k) / steps;
                paint.setColor(toSkColor(layer.paint.color.darker(100 + int(layer.extrudeDarken * 100.0 * f))));
                canvas.save();
                canvas.translate(float(std::cos(rad) * depth * f), float(std::sin(rad) * depth * f));
                canvas.drawPath(m_path, paint);
                canvas.restore();
            }
            break;
        }
        }
    }

    ShapeStyle m_style;
    double m_scale;
    double m_timeSec;
    double m_bleed;
    QSize m_size;
    quint64 m_key = 0;
    SkPath m_path;
    double m_silhouetteStrokePx = 0.0;
    double m_boxW = 0.0;
    double m_boxH = 0.0;
};

} // namespace

double shapeBleedFor(const ShapeStyle &style)
{
    const double silhouette = widestOutwardStroke(style);
    double widest = 0.0;
    for (const TextShadingLayer &layer : style.layers) {
        if (!layer.enabled)
            continue;
        // A blur's kernel runs to three sigma (sigma ≈ blur·scale), so that is the margin it needs.
        double reach = qMax(std::abs(layer.offsetX), std::abs(layer.offsetY)) + layer.blur * 3.0 + qMax(0.0, layer.spread)
                       + layer.sketchDeviation;
        switch (layer.kind) {
        case TextLayerKind::Stroke:
            reach += layer.width * strokeReachFactor(layer.strokeAlign);
            break;
        case TextLayerKind::Extrude:
            reach += layer.width;
            break;
        case TextLayerKind::Shadow:
        case TextLayerKind::Glow:
            reach += silhouette;
            break;
        case TextLayerKind::Fill:
            break;
        }
        widest = qMax(widest, reach);
    }
    return widest + 2.0;
}

namespace {

// The margin a plain shape of w × h canvas px needs around its box for its strokes, shadows and
// operators.
double painterBleed(const ShapeStyle &style, int w, int h, double renderScale)
{
    // A wiggle pushes the outline out by its size; the repeater's copies can land well outside the
    // box, capped so a runaway repeater cannot ask for a texture the GPU will not hold.
    double operators = (style.wiggleSize + qMax(0.0, style.offsetPath) + style.zigzagSize) * renderScale
                       + qMin(4096.0, repeaterReach(style, w, h, renderScale));
    // A custom outline edited past its box (a vertex or handle dragged out, a morph between keys)
    // is still drawn whole.
    if (style.kind == ShapeKind::Custom) {
        const QRectF b = pathContoursBounds(pathContoursFromSvg(style.customPath));
        if (!b.isNull()) {
            const double over = qMax(qMax(-b.left() * w, (b.right() - 100.0) * w),
                                     qMax(-b.top() * h, (b.bottom() - 100.0) * h)) / 100.0;
            operators += qMin(4096.0, qMax(0.0, over));
        }
    }
    return std::ceil(shapeBleedFor(style) * renderScale + operators);
}

// After Effects' «Transform: Group» as a matrix, part units in, parent units out: anchor, scale,
// skew along its axis, rotation, position.
SkMatrix partMatrix(const ShapePartTransform &t)
{
    SkMatrix m = SkMatrix::Translate(float(t.x), float(t.y));
    m.preRotate(float(t.rotation));
    if (qAbs(t.skew) > 1e-6) {
        // Positive skew leans the top to the right, as italic type.
        m.preRotate(float(t.skewAxis));
        m.preSkew(float(-std::tan(qDegreesToRadians(t.skew))), 0.0f);
        m.preRotate(float(-t.skewAxis));
    }
    m.preScale(float(t.scaleX / 100.0), float(t.scaleY / 100.0));
    m.preTranslate(float(-t.anchorX), float(-t.anchorY));
    return m;
}

// After Effects' Wiggle Transform (0.28): smooth pseudo-noise (a few sines at odd ratios, their phases from the
// seed) in -1..1 per channel, the same for the same seed and time, so preview and export agree.
double wiggleNoise(double t, double seed, int channel)
{
    const double s = seed * 12.9898 + channel * 78.233;
    const double p1 = std::fmod(std::sin(s) * 43758.5453, 1.0) * 6.2832;
    const double p2 = std::fmod(std::sin(s + 1.7) * 24634.6345, 1.0) * 6.2832;
    const double p3 = std::fmod(std::sin(s + 3.1) * 11891.2117, 1.0) * 6.2832;
    return (std::sin(t * 1.0 + p1) * 0.55 + std::sin(t * 2.31 + p2) * 0.30 + std::sin(t * 4.73 + p3) * 0.15);
}

ShapePartTransform wiggledTransform(const ShapePartTransform &t, double timeSec)
{
    if (!t.wiggles())
        return t;
    ShapePartTransform w = t;
    const double phase = timeSec * qMax(0.0, t.wiggleSpeed) * 2.0 * M_PI / 2.31;
    w.x += t.wigglePosition * wiggleNoise(phase, t.wiggleSeed, 0);
    w.y += t.wigglePosition * wiggleNoise(phase, t.wiggleSeed, 1);
    w.rotation += t.wiggleRotation * wiggleNoise(phase, t.wiggleSeed, 2);
    const double k = 1.0 + t.wiggleScale / 100.0 * wiggleNoise(phase, t.wiggleSeed, 3);
    w.scaleX *= k;
    w.scaleY *= k;
    return w;
}

// One part, placed: a shape part's own painter and where its image lands, or a group's children.
struct PartNode
{
    bool group = false;
    float alpha = 1.0f;
    SkBlendMode blend = SkBlendMode::kSrcOver;
    std::shared_ptr<const ShapePainter> painter;
    SkMatrix toCanvas; // the painter's image px into the layer's canvas px
    std::vector<PartNode> children; // top first, as the parts
};

void buildPartNodes(const std::vector<ShapePart> &parts, const SkMatrix &parent, double timeSec,
                    std::vector<PartNode> &out, SkRect &bounds)
{
    for (const ShapePart &part : parts) {
        if (!part.visible || part.transform.opacity <= 0.0)
            continue;
        PartNode node;
        node.group = part.group;
        node.alpha = float(qBound(0.0, part.transform.opacity / 100.0, 1.0));
        node.blend = toSkBlendMode(part.blend);
        SkMatrix m = parent;
        m.preConcat(partMatrix(wiggledTransform(part.transform, timeSec)));
        if (part.group) {
            buildPartNodes(part.children, m, timeSec, node.children, bounds);
            if (node.children.empty())
                continue;
            out.push_back(std::move(node));
            continue;
        }
        if (part.width <= 0.0 || part.height <= 0.0)
            continue;
        // Drawn at the scale it lands at, so strokes and edges stay sharp however far it is scaled.
        const double det = std::abs(double(m.getScaleX()) * m.getScaleY() - double(m.getSkewX()) * m.getSkewY());
        const double r = qBound(0.01, std::sqrt(det), 64.0);
        const int pw = qBound(1, qRound(part.width * r), 16384);
        const int ph = qBound(1, qRound(part.height * r), 16384);
        ShapeStyle shape = part.shape;
        shape.parts.clear();
        const double bleed = painterBleed(shape, pw, ph, r);
        node.painter = std::make_shared<ShapePainter>(shape, pw, ph, r, timeSec, bleed);
        node.toCanvas = m;
        node.toCanvas.preTranslate(float(-part.width / 2.0), float(-part.height / 2.0));
        node.toCanvas.preScale(float(part.width / pw), float(part.height / ph));
        node.toCanvas.preTranslate(float(-bleed), float(-bleed));
        const QSize size = node.painter->size();
        bounds.join(node.toCanvas.mapRect(SkRect::MakeWH(float(size.width()), float(size.height()))));
        out.push_back(std::move(node));
    }
}

void paintPartNodes(SkCanvas &canvas, const std::vector<PartNode> &nodes)
{
    // The bottom part first, so the first one in the list ends on top.
    for (auto it = nodes.rbegin(); it != nodes.rend(); ++it) {
        const PartNode &node = *it;
        const bool layered = node.alpha < 1.0f || node.blend != SkBlendMode::kSrcOver;
        canvas.save();
        if (layered) {
            SkPaint paint;
            paint.setAlphaf(node.alpha);
            paint.setBlendMode(node.blend);
            canvas.saveLayer(nullptr, &paint);
        }
        if (node.group) {
            paintPartNodes(canvas, node.children);
        } else {
            canvas.concat(node.toCanvas);
            node.painter->paint(canvas);
        }
        if (layered)
            canvas.restore();
        canvas.restore();
    }
}

// A layer of parts (0.28): each part drawn by its own ShapePainter, placed by its transform and
// its groups' within the layer's box.
class ContentsPainter final : public VectorPainter
{
public:
    ContentsPainter(const ShapeStyle &style, int width, int height, double renderScale, double timeSec)
    {
        const double refW = style.partsRefWidth > 0.0 ? style.partsRefWidth : width / qMax(renderScale, 1e-6);
        const double refH = style.partsRefHeight > 0.0 ? style.partsRefHeight : height / qMax(renderScale, 1e-6);
        SkMatrix layer = SkMatrix::Translate(float(width / 2.0), float(height / 2.0));
        layer.preScale(float(width / refW), float(height / refH));
        SkRect bounds = SkRect::MakeEmpty();
        buildPartNodes(style.parts, layer, timeSec, m_nodes, bounds);
        if (bounds.isEmpty())
            bounds = SkRect::MakeWH(float(width), float(height));
        // Capped so a part flung far away cannot ask for a texture the GPU will not hold.
        if (!bounds.intersect(SkRect::MakeLTRB(-8192.0f, -8192.0f, float(width) + 8192.0f, float(height) + 8192.0f)))
            bounds = SkRect::MakeWH(float(width), float(height));
        m_origin = QPointF(std::floor(bounds.left()), std::floor(bounds.top()));
        m_size = QSize(qMax(1, int(std::ceil(bounds.right() - m_origin.x()))),
                       qMax(1, int(std::ceil(bounds.bottom() - m_origin.y()))));
        const bool cacheable = !style.isAnimated() && !shapeTimeDrivenPaint(style);
        m_key = cacheable ? (qHashMulti(shapeStyleHash(style), width, height, qRound(renderScale * 1000.0), 28) | 1) : 0;
    }

    QSize size() const override { return m_size; }
    quint64 cacheKey() const override { return m_key; }
    QPointF origin() const { return m_origin; }

    void paint(SkCanvas &canvas) const override
    {
        canvas.translate(float(-m_origin.x()), float(-m_origin.y()));
        paintPartNodes(canvas, m_nodes);
    }

private:
    std::vector<PartNode> m_nodes;
    QPointF m_origin;
    QSize m_size;
    quint64 m_key = 0;
};

} // namespace

ShapePainterResult makeShapePainter(const ShapePaintRequest &request)
{
    ShapePainterResult result;
    const int w = qMax(1, qRound(request.layoutRect.width()));
    const int h = qMax(1, qRound(request.layoutRect.height()));
    // The image is drawn at whole pixels, but it lands on the layout box as it is (fractions and all): a shape
    // that grows or shrinks (a pop, a zoom) stays centred instead of shaking by the rounding of its size each
    // frame (Jorge, 2026-10-30: «logos y fotos tiemblan»). The stretch is under half a pixel.
    const double sx = request.layoutRect.width() > 0.0 ? request.layoutRect.width() / w : 1.0;
    const double sy = request.layoutRect.height() > 0.0 ? request.layoutRect.height() / h : 1.0;
    if (request.style.hasParts()) {
        auto painter = std::make_shared<ContentsPainter>(request.style, w, h, request.renderScale, request.timeSec);
        result.rect = QRectF(request.layoutRect.x() + painter->origin().x() * sx,
                             request.layoutRect.y() + painter->origin().y() * sy, painter->size().width() * sx,
                             painter->size().height() * sy);
        result.painter = std::move(painter);
        return result;
    }
    const double bleed = painterBleed(request.style, w, h, request.renderScale);
    auto painter = std::make_shared<ShapePainter>(request.style, w, h, request.renderScale, request.timeSec, bleed);
    result.rect = QRectF(request.layoutRect.x() - bleed * sx, request.layoutRect.y() - bleed * sy,
                         painter->size().width() * sx, painter->size().height() * sy);
    result.painter = std::move(painter);
    return result;
}

ShapePainterResult makeShapePainter(const ShapeStyle &style, int width, int height, double renderScale, double timeSec)
{
    ShapePaintRequest request;
    request.style = style;
    request.layoutRect = QRectF(0, 0, width, height);
    request.renderScale = renderScale;
    request.timeSec = timeSec;
    return makeShapePainter(request);
}

} // namespace drift::skia
