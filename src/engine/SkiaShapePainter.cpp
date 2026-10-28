#include "SkiaShapePainter.h"

#include "SkiaPath.h"
#include "SkiaShading.h"
#include "core/ShapePath.h"

#include <QtMath>

#include <cmath>

#include "include/core/SkCanvas.h"
#include "include/core/SkClipOp.h"
#include "include/core/SkPathBuilder.h"
#include "include/core/SkStrokeRec.h"
#include "include/effects/SkCornerPathEffect.h"
#include "include/core/SkPathMeasure.h"
#include "include/effects/SkTrimPathEffect.h"

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

// Trim Paths (0.26): start and end in percent, the offset in degrees (once round = 360°), wrapping
// past the outline's end the way After Effects does.
SkPath trimmedPath(const SkPath &path, double startPct, double endPct, double offsetDeg)
{
    double a = qBound(0.0, startPct, 100.0) / 100.0;
    double b = qBound(0.0, endPct, 100.0) / 100.0;
    if (a > b)
        std::swap(a, b);
    if (b - a <= 1e-6)
        return {};
    const double shift = offsetDeg / 360.0;
    a += shift;
    b += shift;
    const double whole = std::floor(a);
    a -= whole;
    b -= whole;
    sk_sp<SkPathEffect> effect = b <= 1.0 + 1e-9
                                     ? SkTrimPathEffect::Make(float(a), float(qMin(1.0, b)))
                                     : SkTrimPathEffect::Make(float(b - 1.0), float(a), SkTrimPathEffect::Mode::kInverted);
    if (!effect)
        return path;
    SkPathBuilder trimmed;
    SkStrokeRec rec(SkStrokeRec::kHairline_InitStyle);
    if (!effect->filterPath(&trimmed, path, &rec))
        return path;
    SkPath result = trimmed.detach();
    result.setFillType(path.getFillType());
    return result;
}

// Repeater (0.26): copy `index` (fractional with the offset) of a w × h box, in box px: moved,
// turned and scaled from its centre, each step compounding as in After Effects.
SkMatrix repeaterMatrix(const ShapeStyle &style, double index, double w, double h, double scale)
{
    SkMatrix m;
    m.setTranslate(float(-w / 2.0), float(-h / 2.0));
    const double factor = std::pow(qMax(0.0, style.repeatScale) / 100.0, index);
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
        if (m_style.hasWiggle())
            m_path = wiggledPath(m_path, m_style.wiggleSize * m_scale, m_style.wiggleDetail * m_scale,
                                 m_timeSec * m_style.wiggleSpeed, m_style.wiggleSeed);
        if (m_style.hasTrim() || !qFuzzyIsNull(m_style.trimOffset))
            m_path = trimmedPath(m_path, m_style.trimStart, m_style.trimEnd, m_style.trimOffset);
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
            paint.setStrokeJoin(SkPaint::kRound_Join);
            paint.setStrokeCap(SkPaint::kRound_Cap);
            paint.setPathEffect(strokePathEffectFor(layer, width, m_scale));
            if (layer.strokeAlign == StrokeAlign::Center) {
                paint.setStrokeWidth(float(width));
                canvas.drawPath(m_path, paint);
                break;
            }
            // A centred stroke of twice the width, clipped to one side of the outline, is the
            // half that grows purely outward or purely inward.
            paint.setStrokeWidth(float(width * 2.0));
            canvas.save();
            canvas.clipPath(m_path, layer.strokeAlign == StrokeAlign::Inside ? SkClipOp::kIntersect : SkClipOp::kDifference,
                            true);
            canvas.drawPath(m_path, paint);
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

ShapePainterResult makeShapePainter(const ShapePaintRequest &request)
{
    ShapePainterResult result;
    const int w = qMax(1, qRound(request.layoutRect.width()));
    const int h = qMax(1, qRound(request.layoutRect.height()));
    // A wiggle pushes the outline out by its size; the repeater's copies can land well outside the
    // box, capped so a runaway repeater cannot ask for a texture the GPU will not hold.
    const double operators = request.style.wiggleSize * request.renderScale
                             + qMin(4096.0, repeaterReach(request.style, w, h, request.renderScale));
    const double bleed = std::ceil(shapeBleedFor(request.style) * request.renderScale + operators);
    auto painter = std::make_shared<ShapePainter>(request.style, w, h, request.renderScale, request.timeSec, bleed);
    result.rect = QRectF(request.layoutRect.x() - bleed, request.layoutRect.y() - bleed, painter->size().width(),
                         painter->size().height());
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
