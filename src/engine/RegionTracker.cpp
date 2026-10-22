#include "RegionTracker.h"

#include <QtGlobal>

#include <algorithm>
#include <utility>
#include <cmath>

namespace drift {

namespace {

// Longest side of the template in analysis pixels. Big enough to hold texture, small enough that a
// full-window search stays a few milliseconds per frame.
constexpr double kTemplateSide = 40.0;
// How far the subject may move between two frames, as a fraction of the template's longest side.
constexpr double kSearchReach = 0.9;
// How much of the last match the template takes on each confident frame.
constexpr float kTemplateBlend = 0.12f;
constexpr double kBlendScore = 0.7;
// How much a peak a whole search reach away is marked down against one at the last position.
constexpr double kDistancePenalty = 0.08;

float bilinear(const QVector<float> &px, int w, int h, double x, double y)
{
    x = qBound(0.0, x, double(w - 1));
    y = qBound(0.0, y, double(h - 1));
    const int x0 = int(x);
    const int y0 = int(y);
    const int x1 = qMin(x0 + 1, w - 1);
    const int y1 = qMin(y0 + 1, h - 1);
    const float fx = float(x - x0);
    const float fy = float(y - y0);
    const float a = px[y0 * w + x0] * (1.f - fx) + px[y0 * w + x1] * fx;
    const float b = px[y1 * w + x0] * (1.f - fx) + px[y1 * w + x1] * fx;
    return a * (1.f - fy) + b * fy;
}

} // namespace

RegionTracker::Gray RegionTracker::analysisFrame(const QImage &frame) const
{
    const QImage grey = frame.scaled(m_analysisW, m_analysisH, Qt::IgnoreAspectRatio, Qt::SmoothTransformation)
                            .convertToFormat(QImage::Format_Grayscale8);
    Gray out;
    out.w = grey.width();
    out.h = grey.height();
    out.px.resize(out.w * out.h);
    for (int y = 0; y < out.h; ++y) {
        const uchar *line = grey.constScanLine(y);
        for (int x = 0; x < out.w; ++x)
            out.px[y * out.w + x] = float(line[x]);
    }
    return out;
}

RegionTracker::Gray RegionTracker::patch(const Gray &frame, double cx, double cy, double scale) const
{
    Gray out;
    out.w = m_template.w;
    out.h = m_template.h;
    out.px.resize(out.w * out.h);
    const double left = cx - out.w * scale * 0.5;
    const double top = cy - out.h * scale * 0.5;
    for (int y = 0; y < out.h; ++y) {
        for (int x = 0; x < out.w; ++x)
            out.px[y * out.w + x] =
                bilinear(frame.px, frame.w, frame.h, left + (x + 0.5) * scale - 0.5, top + (y + 0.5) * scale - 0.5);
    }
    return out;
}

// Zero-mean normalized cross-correlation of `templ` placed with its top-left at (x0, y0).
double RegionTracker::correlate(const Gray &frame, const Gray &templ, int x0, int y0) const
{
    const int n = templ.w * templ.h;
    double sumF = 0.0;
    double sumT = 0.0;
    for (int y = 0; y < templ.h; ++y) {
        const float *f = frame.px.constData() + (y0 + y) * frame.w + x0;
        const float *t = templ.px.constData() + y * templ.w;
        for (int x = 0; x < templ.w; ++x) {
            sumF += f[x];
            sumT += t[x];
        }
    }
    const double meanF = sumF / n;
    const double meanT = sumT / n;
    double num = 0.0;
    double varF = 0.0;
    double varT = 0.0;
    for (int y = 0; y < templ.h; ++y) {
        const float *f = frame.px.constData() + (y0 + y) * frame.w + x0;
        const float *t = templ.px.constData() + y * templ.w;
        for (int x = 0; x < templ.w; ++x) {
            const double df = f[x] - meanF;
            const double dt = t[x] - meanT;
            num += df * dt;
            varF += df * df;
            varT += dt * dt;
        }
    }
    // A flat patch (sky, a wall) correlates with nothing; call it no match rather than divide by 0.
    if (varF < 1e-6 || varT < 1e-6)
        return 0.0;
    return num / std::sqrt(varF * varT);
}

namespace {

// Zero-mean normalized cross-correlation of two patches of the same size.
double similarity(const QVector<float> &a, const QVector<float> &b)
{
    const int n = int(qMin(a.size(), b.size()));
    if (n == 0)
        return 0.0;
    double meanA = 0.0;
    double meanB = 0.0;
    for (int i = 0; i < n; ++i) {
        meanA += a[i];
        meanB += b[i];
    }
    meanA /= n;
    meanB /= n;
    double num = 0.0;
    double varA = 0.0;
    double varB = 0.0;
    for (int i = 0; i < n; ++i) {
        const double da = a[i] - meanA;
        const double db = b[i] - meanB;
        num += da * db;
        varA += da * da;
        varB += db * db;
    }
    if (varA < 1e-6 || varB < 1e-6)
        return 0.0;
    return num / std::sqrt(varA * varB);
}

} // namespace

bool RegionTracker::start(const QImage &frame, const QRectF &region)
{
    m_started = false;
    const QRectF r = region.intersected(QRectF(0, 0, 1, 1));
    if (frame.isNull() || r.width() <= 0.0 || r.height() <= 0.0)
        return false;

    // The analysis size puts the region's longest side at about kTemplateSide pixels, so a small
    // subject is examined closely and a large one coarsely, at the same cost.
    const double aspect = double(frame.width()) / double(qMax(1, frame.height()));
    const double longest = qMax(r.width(), r.height() / aspect);
    m_analysisW = qBound(64, int(std::lround(kTemplateSide / longest)), qMax(64, frame.width()));
    m_analysisH = qMax(16, int(std::lround(m_analysisW / aspect)));

    const Gray grey = analysisFrame(frame);
    m_template.w = qMax(4, int(std::lround(r.width() * m_analysisW)));
    m_template.h = qMax(4, int(std::lround(r.height() * m_analysisH)));
    m_cx = r.center().x() * m_analysisW;
    m_cy = r.center().y() * m_analysisH;
    m_scale = 1.0;
    m_baseW = r.width();
    m_baseH = r.height();
    m_template = patch(grey, m_cx, m_cy, 1.0);
    m_original = m_template;
    m_lostFrames = 0;
    // Is the subject one of a kind in this frame? Anything far from it that matches nearly as well
    // makes the scene ambiguous for a later recovery.
    m_lookAlike = false;
    const double apart = qMax(m_template.w, m_template.h) * 0.75;
    for (const Peak &p : wholeFrameSearch(grey, m_template)) {
        if (p.score < kRecoverScore - kRecoverMargin)
            break;
        if (std::hypot(p.x + m_template.w * 0.5 - m_cx, p.y + m_template.h * 0.5 - m_cy) >= apart) {
            m_lookAlike = true;
            break;
        }
    }
    m_started = true;
    return true;
}

RegionTracker::Gray RegionTracker::scaledOriginal(double scale) const
{
    Gray templ;
    templ.w = qMax(4, int(std::lround(m_original.w * scale)));
    templ.h = qMax(4, int(std::lround(m_original.h * scale)));
    templ.px.resize(templ.w * templ.h);
    for (int y = 0; y < templ.h; ++y) {
        for (int x = 0; x < templ.w; ++x)
            templ.px[y * templ.w + x] = bilinear(m_original.px, m_original.w, m_original.h,
                                                 (x + 0.5) * m_original.w / templ.w - 0.5,
                                                 (y + 0.5) * m_original.h / templ.h - 0.5);
    }
    return templ;
}

QVector<RegionTracker::Peak> RegionTracker::wholeFrameSearch(const Gray &frame, const Gray &templ) const
{
    QVector<Peak> peaks;
    if (templ.w >= frame.w || templ.h >= frame.h)
        return peaks;
    // Every third position, then the best few refined: a textured peak is wider than that.
    for (int y = 0; y <= frame.h - templ.h; y += 3) {
        for (int x = 0; x <= frame.w - templ.w; x += 3)
            peaks.append({correlate(frame, templ, x, y), x, y});
    }
    std::sort(peaks.begin(), peaks.end(), [](const Peak &a, const Peak &b) { return a.score > b.score; });
    for (int k = 0; k < qMin(6, int(peaks.size())); ++k) {
        Peak &peak = peaks[k];
        const Peak coarse = peak;
        for (int y = qMax(0, coarse.y - 2); y <= qMin(frame.h - templ.h, coarse.y + 2); ++y) {
            for (int x = qMax(0, coarse.x - 2); x <= qMin(frame.w - templ.w, coarse.x + 2); ++x) {
                const double s = correlate(frame, templ, x, y);
                if (s > peak.score)
                    peak = {s, x, y};
            }
        }
    }
    std::sort(peaks.begin(), peaks.end(), [](const Peak &a, const Peak &b) { return a.score > b.score; });
    return peaks;
}

bool RegionTracker::recover(const Gray &frame)
{
    const Gray templ = scaledOriginal(m_scale);
    const QVector<Peak> peaks = wholeFrameSearch(frame, templ);
    if (peaks.isEmpty() || peaks.first().score < kRecoverScore)
        return false;
    const Peak best = peaks.first();
    // The runner-up has to be somewhere else (not the same peak's shoulder) and clearly lower.
    const double apart = qMax(templ.w, templ.h) * 0.75;
    for (const Peak &p : peaks) {
        if (std::hypot(p.x - best.x, p.y - best.y) < apart)
            continue;
        if (p.score > best.score - kRecoverMargin)
            return false;
        break; // sorted: the first one far enough away is the runner-up
    }
    const double bx = best.x + templ.w * 0.5;
    const double by = best.y + templ.h * 0.5;
    if (m_lookAlike) {
        // With a twin around, only near where it went: a few search reaches, growing slowly.
        const double reach = qMax(6.0, qMax(templ.w, templ.h) * kSearchReach);
        const double radius = reach * qMin(4.0, 2.0 + 0.25 * m_lostFrames);
        if (std::hypot(bx - m_cx, by - m_cy) > radius)
            return false;
    }
    m_cx = bx;
    m_cy = by;
    // Start again from the framed look: what was blended in while drifting off is not trusted.
    m_template = m_original;
    return true;
}

RegionTracker::Result RegionTracker::step(const QImage &frame, bool followScale)
{
    Result result;
    const auto currentRect = [this]() {
        const double w = m_baseW * m_scale;
        const double h = m_baseH * m_scale;
        return QRectF(m_cx / m_analysisW - w * 0.5, m_cy / m_analysisH - h * 0.5, w, h);
    };
    if (!m_started || frame.isNull()) {
        result.rect = m_started ? currentRect() : QRectF();
        result.lost = true;
        return result;
    }

    const Gray grey = analysisFrame(frame);
    const double scales[] = {1.0 / 1.04, 1.0, 1.04};
    const int reach = qMax(6, int(std::lround(qMax(m_template.w, m_template.h) * m_scale * kSearchReach)));

    double bestScore = -2.0;
    double bestX = m_cx;
    double bestY = m_cy;
    double bestScale = m_scale;
    for (const double s : scales) {
        if (!followScale && s != 1.0)
            continue;
        const double scale = m_scale * s;
        // The template resampled to this scale, so the correlation compares like with like.
        Gray templ;
        templ.w = qMax(4, int(std::lround(m_template.w * scale)));
        templ.h = qMax(4, int(std::lround(m_template.h * scale)));
        if (templ.w >= grey.w || templ.h >= grey.h)
            continue;
        templ.px.resize(templ.w * templ.h);
        for (int y = 0; y < templ.h; ++y) {
            for (int x = 0; x < templ.w; ++x)
                templ.px[y * templ.w + x] = bilinear(m_template.px, m_template.w, m_template.h,
                                                     (x + 0.5) * m_template.w / templ.w - 0.5,
                                                     (y + 0.5) * m_template.h / templ.h - 0.5);
        }

        const int cx0 = int(std::lround(m_cx - templ.w * 0.5));
        const int cy0 = int(std::lround(m_cy - templ.h * 0.5));
        const int xMin = qMax(0, cx0 - reach);
        const int xMax = qMin(grey.w - templ.w, cx0 + reach);
        const int yMin = qMax(0, cy0 - reach);
        const int yMax = qMin(grey.h - templ.h, cy0 + reach);
        if (xMin > xMax || yMin > yMax)
            continue;

        // Coarse to fine: every other position over the whole window, then every position around
        // the best of those. A textured patch's correlation peak is wider than two pixels, so the
        // coarse pass cannot step over it, and the search costs about a quarter.
        const int cols = xMax - xMin + 1;
        QVector<double> scores(cols * (yMax - yMin + 1), -2.0);
        double local = -2.0;
        double localRanked = -3.0;
        int lx = xMin;
        int ly = yMin;
        // Between two near-equal peaks the nearer one wins: a subject moves continuously, and on a
        // repeating pattern the far peak is the same stripe one repeat over.
        const auto ranked = [&](double score, int x, int y) {
            const double dist = std::hypot(x - cx0, y - cy0) / reach;
            return score - kDistancePenalty * dist;
        };
        const auto visit = [&](int x, int y) {
            double &slot = scores[(y - yMin) * cols + x - xMin];
            if (slot > -2.0)
                return;
            slot = correlate(grey, templ, x, y);
            const double r = ranked(slot, x, y);
            if (r > localRanked) {
                localRanked = r;
                local = slot;
                lx = x;
                ly = y;
            }
        };
        // The best few coarse positions are all refined: on a repeating pattern (stripes, a
        // checked shirt) the coarse grid can sample a neighbouring repeat higher than the true
        // peak it straddles.
        struct Coarse { double score; int x; int y; };
        QVector<Coarse> coarse;
        for (int y = yMin; y <= yMax; y += 2) {
            for (int x = xMin; x <= xMax; x += 2) {
                visit(x, y);
                coarse.append({ranked(scores[(y - yMin) * cols + x - xMin], x, y), x, y});
            }
        }
        const int keep = qMin(8, int(coarse.size()));
        std::partial_sort(coarse.begin(), coarse.begin() + keep, coarse.end(),
                          [](const Coarse &a, const Coarse &b) { return a.score > b.score; });
        for (int k = 0; k < keep; ++k) {
            for (int y = qMax(yMin, coarse[k].y - 2); y <= qMin(yMax, coarse[k].y + 2); ++y) {
                for (int x = qMax(xMin, coarse[k].x - 2); x <= qMin(xMax, coarse[k].x + 2); ++x)
                    visit(x, y);
            }
        }
        // Sub-pixel peak: a parabola through the best score and its two neighbours on each axis.
        const auto at = [&](int x, int y) {
            double &slot = scores[(y - yMin) * cols + x - xMin];
            if (slot <= -2.0)
                slot = correlate(grey, templ, x, y);
            return slot;
        };
        double dx = 0.0;
        double dy = 0.0;
        if (lx > xMin && lx < xMax) {
            const double l = at(lx - 1, ly), c = at(lx, ly), r = at(lx + 1, ly);
            const double d = l - 2 * c + r;
            if (d < 0)
                dx = qBound(-0.5, 0.5 * (l - r) / d, 0.5);
        }
        if (ly > yMin && ly < yMax) {
            const double u = at(lx, ly - 1), c = at(lx, ly), b = at(lx, ly + 1);
            const double d = u - 2 * c + b;
            if (d < 0)
                dy = qBound(-0.5, 0.5 * (u - b) / d, 0.5);
        }
        // A scale step has to beat staying put by a margin, or noise walks the size away.
        const double margin = s == 1.0 ? 0.0 : 0.01;
        if (local - margin > bestScore) {
            bestScore = local - margin;
            bestX = lx + dx + templ.w * 0.5;
            bestY = ly + dy + templ.h * 0.5;
            bestScale = scale;
        }
    }

    result.score = bestScore;
    // Still the framed subject there? The blended template can drift onto the background a little
    // at a time and keep matching it well; the framed look cannot.
    double framed = 1.0;
    if (bestScore >= kLostScore)
        framed = similarity(patch(grey, bestX, bestY, bestScale).px, m_original.px);
    if (bestScore < kLostScore || framed < kDriftScore) {
        // The whole-frame search costs a few local ones: every other lost frame is enough to pick
        // the subject up again within a frame or two of its return.
        ++m_lostFrames;
        if (m_lostFrames % 2 == 1 && recover(grey)) {
            m_lostFrames = 0;
            result.lost = false;
            result.recovered = true;
            result.score = kRecoverScore;
            result.rect = currentRect();
            return result;
        }
        result.lost = true;
        result.rect = currentRect();
        return result;
    }
    m_lostFrames = 0;
    m_cx = bestX;
    m_cy = bestY;
    m_scale = bestScale;
    if (bestScore >= kBlendScore && framed >= kLearnScore) {
        const Gray seen = patch(grey, m_cx, m_cy, m_scale);
        for (int i = 0; i < m_template.px.size(); ++i)
            m_template.px[i] = m_template.px[i] * (1.f - kTemplateBlend) + seen.px[i] * kTemplateBlend;
    }
    result.rect = currentRect();
    return result;
}

} // namespace drift
