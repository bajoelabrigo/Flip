#pragma once

#include <QImage>
#include <QString>

#include <memory>

namespace drift {

// Frame interpolation with RIFE (Practical-RIFE 4.25, MIT, code and weights) on ONNX Runtime: the
// picture between two frames at any instant t in 0..1. Used for the AI transition (a morph from the
// last frame of one clip into the first of the next) and, later, smooth slow motion.
//
// The model comes as an addon of kind "interp-model" (or DRIFT_INTERP_MODEL_DIR): a folder with the
// vs-mlrt export of the "rife_v2" form and a constants.json naming it ({"model": "rife_v4.25.onnx"}).
// That graph takes one fp32 tensor "input" [1, 7, H, W] — frame A RGB, frame B RGB and a plane
// filled with t, all 0..1, planar — and returns "output" [1, 3, H, W] RGB. It pads internally, so
// any size works; frames are capped at kMaxSide on their long side to keep a pass interactive.
class FrameInterpolator
{
    struct Impl;

public:
    // Whether a model is on disk (cheap; does not load ONNX Runtime).
    static bool modelPresent();

    // Loads (or reuses) the model's session. nullptr with *error set when it cannot be used.
    // Blocks — never call this from the GUI thread.
    static std::shared_ptr<FrameInterpolator> load(QString *error);

    // The frame at `t` between `a` (t = 0) and `b` (t = 1), as RGB888 at a's size (b is scaled to
    // it). Null with *error set on failure.
    QImage interpolate(const QImage &a, const QImage &b, float t, QString *error);

    static constexpr int kMaxSide = 1920;

    ~FrameInterpolator();
    FrameInterpolator(const FrameInterpolator &) = delete;
    FrameInterpolator &operator=(const FrameInterpolator &) = delete;

private:
    FrameInterpolator();
    std::unique_ptr<Impl> d;
};

} // namespace drift
