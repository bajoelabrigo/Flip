#pragma once

#include <QImage>
#include <QRectF>
#include <QVector>

namespace drift {

// Follows a rectangle of a video from frame to frame, the way CapCut's and Filmora's motion
// tracking do: the user frames something, and every next frame finds where that patch went.
//
// Zero-mean normalized cross-correlation of a small grey template over a window around the last
// position, with a sub-pixel peak and, when asked, a scale search. The template drifts slowly
// toward what it last matched, so a subject that turns or changes light is still followed, and a
// match too weak to trust holds the last position instead of jumping onto the background.
//
// Frames and rects are in normalized frame coordinates (0..1 on both axes), so the caller can
// decode at any size. Pure CPU and deterministic, so it is tested without a GPU.
class RegionTracker
{
public:
    struct Result
    {
        QRectF rect;        // normalized; the last trusted position while lost
        double score = 0.0; // correlation of the match, -1..1
        bool lost = false;
        // Found again by a search over the whole frame after being lost.
        bool recovered = false;
    };

    // A match below this is not trusted: the rect holds and the result says lost.
    static constexpr double kLostScore = 0.35;
    // Once lost, the subject is looked for over the whole frame with the template as it was
    // framed. A match counts only above this score and clearly ahead of the next best place, so a
    // look-alike (the other car, the other player) is not taken for it.
    static constexpr double kRecoverScore = 0.6;
    static constexpr double kRecoverMargin = 0.08;

    // Returns false when the region is empty or outside the frame.
    bool start(const QImage &frame, const QRectF &region);
    Result step(const QImage &frame, bool followScale);

    bool started() const { return m_started; }

private:
    struct Gray
    {
        int w = 0;
        int h = 0;
        QVector<float> px;
        float at(int x, int y) const { return px[y * w + x]; }
    };

    Gray analysisFrame(const QImage &frame) const;
    // The template-sized patch of `frame` centred on (cx, cy) at `scale` times the template, in
    // analysis pixels, bilinearly sampled.
    Gray patch(const Gray &frame, double cx, double cy, double scale) const;
    double correlate(const Gray &frame, const Gray &templ, int x0, int y0) const;
    // The whole-frame search for a lost subject; true when it was found unambiguously.
    bool recover(const Gray &frame);
    struct Peak
    {
        double score;
        int x; // top-left of the template, analysis pixels
        int y;
    };
    // `templ` correlated over the whole frame on a coarse grid, the best few refined; best first.
    QVector<Peak> wholeFrameSearch(const Gray &frame, const Gray &templ) const;
    Gray scaledOriginal(double scale) const;

    bool m_started = false;
    int m_analysisW = 0; // analysis frame size, fixed at start so positions stay comparable
    int m_analysisH = 0;
    Gray m_template;     // grey patch at the tracked scale 1.0
    Gray m_original;     // the patch as framed, never blended: what a lost subject is searched for
    int m_lostFrames = 0;
    // Something else in the first frame looks like the subject (twins, two of the same car): a lost
    // subject is then only picked up again near where it was lost.
    bool m_lookAlike = false;
    double m_cx = 0.0;   // centre in analysis pixels
    double m_cy = 0.0;
    double m_scale = 1.0;
    double m_baseW = 0.0; // region size at start, normalized
    double m_baseH = 0.0;
};

} // namespace drift
