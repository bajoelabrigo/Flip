#include "MaskApplier.h"

#include "core/ShapePath.h"

#include <QFont>
#include <QLinearGradient>
#include <QPainter>
#include <QPainterPath>
#include <QtMath>

#include <cmath>

namespace drift {

QPainterPath maskPath(const Mask &mask, int canvasWidth, int canvasHeight)
{
    const QPointF center(mask.x * canvasWidth, mask.y * canvasHeight);
    // Expand grows (or shrinks) the outline by the same distance on every side, measured on the
    // frame's shorter side so a square stays square on a wide frame.
    const double grow = mask.expand * qMin(canvasWidth, canvasHeight);
    const double halfW = qMax(1.0, mask.w * canvasWidth * 0.5 + grow);
    const double halfH = qMax(1.0, mask.h * canvasHeight * 0.5 + grow);
    // The mask's own rect. Star and heart used to be forced into a square of qMin(halfW, halfH),
    // which quietly threw away whichever of the width and height sliders was larger; both
    // generators handle a non-square box, so both sliders now mean something.
    const QRectF bounds(center.x() - halfW, center.y() - halfH, halfW * 2.0, halfH * 2.0);

    switch (mask.shape) {
    case drift::MaskShape::Rectangle: {
        QPainterPath path;
        path.addRect(bounds);
        return path;
    }
    case drift::MaskShape::Ellipse: {
        QPainterPath path;
        path.addEllipse(center, halfW, halfH);
        return path;
    }
    case drift::MaskShape::Star:
        // Rotation is deliberately not passed through: maskAlphaMap rotates every parametric
        // shape about its centre below, and baking it in here as well turned a star twice as far
        // as the slider said.
        return drift::regularPolygonPath(bounds, 5, 0.0);
    case drift::MaskShape::Heart:
        return drift::heartPath(bounds);
    case drift::MaskShape::Bars: {
        const double barH = halfH;
        QPainterPath path;
        path.addRect(QRectF(0, 0, canvasWidth, barH));
        path.addRect(QRectF(0, canvasHeight - barH, canvasWidth, barH));
        return path;
    }
    case drift::MaskShape::Freeform: {
        QPainterPath path;
        if (mask.points.isEmpty())
            return path;
        if (!qFuzzyIsNull(grow)) {
            // Each vertex pushed away from (or towards) the middle of them all by the expand.
            QPointF middle;
            for (const QPointF &p : mask.points)
                middle += QPointF(p.x() * canvasWidth, p.y() * canvasHeight);
            middle /= double(mask.points.size());
            Mask grown = mask;
            grown.expand = 0.0;
            for (QPointF &p : grown.points) {
                const QPointF at(p.x() * canvasWidth, p.y() * canvasHeight);
                const QPointF d = at - middle;
                const double len = std::hypot(d.x(), d.y());
                const double k = len > 0.0 ? qMax(0.0, len + grow) / len : 1.0;
                const QPointF moved = middle + d * k;
                p = QPointF(moved.x() / canvasWidth, moved.y() / canvasHeight);
            }
            return maskPath(grown, canvasWidth, canvasHeight);
        }
        // Pen: a closed Catmull-Rom curve through every vertex, as cubic Beziers.
        if (mask.smooth && mask.points.size() >= 3) {
            const int n = mask.points.size();
            const auto at = [&](int i) {
                const QPointF &p = mask.points.at(((i % n) + n) % n);
                return QPointF(p.x() * canvasWidth, p.y() * canvasHeight);
            };
            path.moveTo(at(0));
            for (int i = 0; i < n; ++i) {
                const QPointF p0 = at(i - 1), p1 = at(i), p2 = at(i + 1), p3 = at(i + 2);
                path.cubicTo(p1 + (p2 - p0) / 6.0, p2 - (p3 - p1) / 6.0, p2);
            }
            path.closeSubpath();
            return path;
        }
        for (int i = 0; i < mask.points.size(); ++i) {
            const QPointF pt(mask.points.at(i).x() * canvasWidth, mask.points.at(i).y() * canvasHeight);
            if (i == 0)
                path.moveTo(pt);
            else
                path.lineTo(pt);
        }
        path.closeSubpath();
        return path;
    }
    case drift::MaskShape::Text: {
        // The words' outline in a heavy font, scaled to fill the mask's rect. Rotation is applied
        // by maskAlphaMap like every parametric shape.
        QPainterPath glyphs;
        if (mask.text.trimmed().isEmpty())
            return glyphs;
        QFont font(QStringLiteral("Arial Black"));
        font.setStyleHint(QFont::SansSerif);
        font.setWeight(QFont::Black);
        font.setPixelSize(200);
        const QStringList lines = mask.text.split(QLatin1Char('\n'));
        for (int i = 0; i < lines.size(); ++i)
            glyphs.addText(0.0, 200.0 * 1.1 * i, font, lines.at(i));
        const QRectF box = glyphs.boundingRect();
        if (box.width() <= 0.0 || box.height() <= 0.0)
            return {};
        QTransform fit;
        fit.translate(bounds.left(), bounds.top());
        fit.scale(bounds.width() / box.width(), bounds.height() / box.height());
        fit.translate(-box.left(), -box.top());
        return fit.map(glyphs);
    }
    case drift::MaskShape::Path: {
        // A library shape: its 0..100 outline stretched onto the mask's rect.
        QPainterPath unit;
        if (mask.pathData.isEmpty() || !drift::parseSvgPathData(mask.pathData, &unit))
            return {};
        QTransform fit;
        fit.translate(bounds.left(), bounds.top());
        fit.scale(bounds.width() / 100.0, bounds.height() / 100.0);
        QPainterPath mapped = fit.map(unit);
        mapped.setFillRule(mask.pathEvenOdd ? Qt::OddEvenFill : Qt::WindingFill);
        return mapped;
    }
    case drift::MaskShape::Media:
        // Raster, not parametric: the coverage map is decoded per frame in FrameCompositor and
        // rides on GpuLayer::maskMedia. There is no path to rasterize.
        break;
    case drift::MaskShape::LinearGradient: {
        // A ramp has no outline; maskAlphaMap paints it. The path is the band's full-coverage
        // side, for thumbnails and outlines.
        const double band = qMax(1.0, mask.h * canvasHeight);
        QPainterPath path;
        const double far = double(canvasWidth + canvasHeight) * 2.0;
        path.addRect(QRectF(center.x() - far, center.y() - far, far * 2.0, far - band / 2.0 + grow));
        return path;
    }
    case drift::MaskShape::None:
        break;
    }
    return {};
}

} // namespace drift

namespace {

QImage blurAlpha(const QImage &alpha, int radius)
{
    if (radius <= 0 || alpha.isNull())
        return alpha;

    QImage out = alpha;
    const int passes = qBound(1, radius / 2, 8);
    for (int pass = 0; pass < passes; ++pass) {
        QImage blurred(out.size(), QImage::Format_Grayscale8);
        for (int y = 0; y < out.height(); ++y) {
            auto *line = blurred.scanLine(y);
            for (int x = 0; x < out.width(); ++x) {
                int sum = 0;
                int count = 0;
                for (int dy = -radius; dy <= radius; ++dy) {
                    const int sy = qBound(0, y + dy, out.height() - 1);
                    for (int dx = -radius; dx <= radius; ++dx) {
                        const int sx = qBound(0, x + dx, out.width() - 1);
                        sum += qGray(out.pixel(sx, sy));
                        ++count;
                    }
                }
                line[x] = static_cast<uchar>(sum / qMax(1, count));
            }
        }
        out = blurred;
    }
    return out;
}

// Multiply the frame's alpha by a coverage map. Shared by both applyMask overloads, which differ
// only in how they arrive at the map.
QImage applyAlphaMap(const QImage &frame, const QImage &alpha, int canvasWidth, int canvasHeight)
{
    QImage rgba = frame.convertToFormat(QImage::Format_RGBA8888);
    if (rgba.size() != alpha.size())
        rgba = rgba.scaled(canvasWidth, canvasHeight, Qt::IgnoreAspectRatio, Qt::SmoothTransformation);

    QImage out(rgba.size(), QImage::Format_RGBA8888);
    for (int y = 0; y < rgba.height(); ++y) {
        const QRgb *src = reinterpret_cast<const QRgb *>(rgba.constScanLine(y));
        QRgb *dst = reinterpret_cast<QRgb *>(out.scanLine(y));
        const uchar *alphaLine = alpha.constScanLine(y);
        for (int x = 0; x < rgba.width(); ++x) {
            const int a = qAlpha(src[x]) * alphaLine[x] / 255;
            dst[x] = qRgba(qRed(src[x]), qGreen(src[x]), qBlue(src[x]), a);
        }
    }
    return out;
}

// Coverage times a mask's opacity (1 leaves it as it is).
QImage scaledByOpacity(QImage alpha, double opacity)
{
    const double k = qBound(0.0, opacity, 1.0);
    if (k >= 1.0 || alpha.isNull())
        return alpha;
    for (int y = 0; y < alpha.height(); ++y) {
        uchar *row = alpha.scanLine(y);
        for (int x = 0; x < alpha.width(); ++x)
            row[x] = static_cast<uchar>(std::lround(row[x] * k));
    }
    return alpha;
}

} // namespace

namespace drift {

QImage maskAlphaMap(const Mask &mask, int canvasWidth, int canvasHeight)
{
    if (!mask.contributes() || mask.shape == MaskShape::Media || canvasWidth <= 0
        || canvasHeight <= 0)
        return {};

    QImage alpha(canvasWidth, canvasHeight, QImage::Format_Grayscale8);
    alpha.fill(mask.invert ? 255 : 0);

    QPainter mp(&alpha);
    mp.setRenderHint(QPainter::Antialiasing);
    mp.setBrush(mask.invert ? Qt::black : Qt::white);
    mp.setPen(Qt::NoPen);

    if (mask.shape == MaskShape::LinearGradient) {
        // Full coverage before the band, none after it, a straight ramp across it; the line is
        // moved along its normal by expand and turned about (x, y) by rotation.
        const QPointF center(mask.x * canvasWidth, mask.y * canvasHeight);
        const double band = qMax(1.0, mask.h * canvasHeight);
        const double grow = mask.expand * qMin(canvasWidth, canvasHeight);
        mp.translate(center);
        mp.rotate(mask.rotation);
        QLinearGradient ramp(0.0, -band / 2.0 + grow, 0.0, band / 2.0 + grow);
        ramp.setColorAt(0.0, mask.invert ? Qt::black : Qt::white);
        ramp.setColorAt(1.0, mask.invert ? Qt::white : Qt::black);
        const double far = double(canvasWidth + canvasHeight) * 2.0;
        mp.fillRect(QRectF(-far, -far, far * 2.0, far * 2.0), ramp);
        mp.end();
        return scaledByOpacity(alpha, mask.opacity);
    }

    QPainterPath path = maskPath(mask, canvasWidth, canvasHeight);
    if (!path.isEmpty()) {
        const QPointF center(mask.x * canvasWidth, mask.y * canvasHeight);
        if (!qFuzzyIsNull(mask.rotation) && mask.shape != MaskShape::Bars && mask.shape != MaskShape::Freeform) {
            QTransform transform;
            transform.translate(center.x(), center.y());
            transform.rotate(mask.rotation);
            transform.translate(-center.x(), -center.y());
            path = transform.map(path);
        }
        mp.drawPath(path);
    }
    mp.end();

    if (mask.feather > 0.0)
        alpha = blurAlpha(alpha, qMax(1, static_cast<int>(mask.feather)));

    return scaledByOpacity(alpha, mask.opacity);
}

QImage maskAlphaMap(const QList<Mask> &masks, int canvasWidth, int canvasHeight)
{
    if (canvasWidth <= 0 || canvasHeight <= 0)
        return {};

    QImage accum;
    for (const Mask &mask : masks) {
        // Media coverage is decoded per frame by the compositor, which is the only place that
        // knows the frame time; there is nothing to rasterize here.
        if (!mask.contributes() || mask.shape == MaskShape::Media)
            continue;

        const QImage coverage = maskAlphaMap(mask, canvasWidth, canvasHeight);
        if (coverage.isNull())
            continue;

        // The first contributing entry seeds the accumulator whatever its op says — starting
        // from black would let a lone Subtract or Intersect blank the clip.
        if (accum.isNull()) {
            accum = coverage;
            continue;
        }

        for (int y = 0; y < accum.height(); ++y) {
            uchar *dst = accum.scanLine(y);
            const uchar *src = coverage.constScanLine(y);
            for (int x = 0; x < accum.width(); ++x) {
                // src is already scaled by the entry's opacity o. Intersect keeps what the entry
                // does not cover in proportion to 1 - o, so a half-opacity Intersect only
                // half-limits: a * (1 - o + o*c).
                switch (mask.op) {
                case MaskOp::Subtract:
                    dst[x] = static_cast<uchar>(dst[x] * (255 - src[x]) / 255);
                    break;
                case MaskOp::Intersect: {
                    const int keep = int(std::lround((1.0 - qBound(0.0, mask.opacity, 1.0)) * 255.0));
                    dst[x] = static_cast<uchar>(dst[x] * qMin(255, src[x] + keep) / 255);
                    break;
                }
                case MaskOp::Add:
                    dst[x] = qMax(dst[x], src[x]);
                    break;
                }
            }
        }
    }
    return accum;
}

QImage applyMask(const QImage &frame, const Mask &mask, int canvasWidth, int canvasHeight)
{
    if (!mask.contributes() || mask.shape == MaskShape::Media || frame.isNull())
        return frame;

    const QImage alpha = maskAlphaMap(mask, canvasWidth, canvasHeight);
    if (alpha.isNull())
        return frame;

    return applyAlphaMap(frame, alpha, canvasWidth, canvasHeight);
}

QImage applyMask(const QImage &frame, const QList<Mask> &masks, int canvasWidth, int canvasHeight)
{
    if (frame.isNull() || masksAreInert(masks))
        return frame;

    const QImage alpha = maskAlphaMap(masks, canvasWidth, canvasHeight);
    if (alpha.isNull())
        return frame;

    return applyAlphaMap(frame, alpha, canvasWidth, canvasHeight);
}

} // namespace drift
