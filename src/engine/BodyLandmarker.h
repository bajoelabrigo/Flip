#pragma once

#include <QImage>
#include <QList>
#include <QPointF>
#include <QString>

#include <memory>

namespace drift {

// MediaPipe BlazePose's 33 body points, in the model's own order. Only the ones the body warps and
// the hair crop read have names here.
namespace body {
constexpr int kPointCount = 33;
constexpr int kNose = 0;
constexpr int kShoulderLeft = 11;
constexpr int kShoulderRight = 12;
constexpr int kElbowLeft = 13;
constexpr int kElbowRight = 14;
constexpr int kWristLeft = 15;
constexpr int kWristRight = 16;
constexpr int kHipLeft = 23;
constexpr int kHipRight = 24;
constexpr int kKneeLeft = 25;
constexpr int kKneeRight = 26;
constexpr int kAnkleLeft = 27;
constexpr int kAnkleRight = 28;
} // namespace body

// One person's pose in one frame. Points are uv (0..1 across the frame), so a pose survives the
// project being rendered at another size.
struct BodyPose
{
    bool valid = false;
    double score = 0.0;
    QList<QPointF> points;    // body::kPointCount, uv
    QList<float> visibility;  // body::kPointCount, 0..1
    // The square the landmark model looked at, in uv of the frame width (size) and uv (centre).
    // Kept so the next frame can start from it, the way MediaPipe tracks without its detector.
    QPointF roiCenter;
    double roiSize = 0.0;
};

// MediaPipe Pose Landmarker (BlazePose GHUM, "full") and Selfie Multiclass on ONNX Runtime, the
// two models of the Retouch › Body and Hair pages. Both are Apache-2.0.
//
// The pose detector that normally finds the person does not convert to ONNX, so the landmark
// model finds them itself: it looks at the whole frame first, and then three more times at the
// square its own auxiliary points describe (hip centre and body scale, MediaPipe's ROI). Later
// frames start from the previous frame's square, and fall back to the whole frame when the person
// is lost. Validated on photos before it was written; see docs/retoque-cuerpo-cabello.md.
//
// All work is synchronous on the calling thread; callers run it off the GUI thread.
class BodyLandmarker
{
    struct Impl;

public:
    static BodyLandmarker &instance();

    // Cheap file-existence check that constructs no ONNX session. This is what UI gating must use.
    static bool modelPresent();

    // Loads both sessions on first use. False if the models are missing or failed to load (see
    // lastError()). Blocks — never call this from the GUI thread.
    bool available();
    QString lastError() const;

    // The most prominent person in the frame. `hint` is the previous frame's pose.
    BodyPose detect(const QImage &frame, const BodyPose *hint = nullptr);

    // Soft hair coverage (Grayscale8, frame size, 0..255). The segmenter looks at the person's
    // square when `pose` is valid — the hair is then large in its input — and at the whole frame
    // otherwise.
    QImage hairCoverage(const QImage &frame, const BodyPose &pose);

    BodyLandmarker(const BodyLandmarker &) = delete;
    BodyLandmarker &operator=(const BodyLandmarker &) = delete;

private:
    BodyLandmarker();
    ~BodyLandmarker();

    std::unique_ptr<Impl> d;
};

} // namespace drift
