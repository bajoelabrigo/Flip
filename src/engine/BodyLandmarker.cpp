#include "engine/BodyLandmarker.h"

#include "engine/GpuPackageParse.h"
#include "engine/OrtSupport.h"

#include <QDir>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>

#include <onnxruntime_cxx_api.h>

#include <algorithm>
#include <array>
#include <cmath>

namespace drift {
namespace {

using drift::ort::cstrs;
using drift::ort::ortPath;
using drift::ort::sessionNames;

constexpr char kPoseFile[] = "pose_landmarks.onnx";
constexpr char kSegmenterFile[] = "selfie_multiclass.onnx";

// The landmark model returns 39 points: the 33 of the body, then six auxiliary ones. 33 is the
// hip centre and 34 a point at the body's own scale; MediaPipe derives its next ROI from them.
constexpr int kOutputPoints = 39;
constexpr int kAuxCenter = 33;
constexpr int kAuxScale = 34;
constexpr int kValuesPerPoint = 5; // x, y, z, visibility, presence
constexpr int kHairClass = 1;      // background, hair, body skin, face skin, clothes, others
constexpr int kSegmenterClasses = 6;

QString resolveBodyModelDir()
{
    const QStringList roots = GpuPackageParse::defaultSearchPaths(
        QStringLiteral("DRIFT_BODY_MODEL_DIR"), QStringLiteral("models/body"),
        QStringLiteral("body-model"));
    // A directory only counts when every piece is there: a half-downloaded folder must not look
    // installed.
    for (const QString &root : roots) {
        const QDir dir(root);
        if (QFile::exists(dir.filePath(QLatin1String(kPoseFile)))
            && QFile::exists(dir.filePath(QLatin1String(kSegmenterFile)))) {
            return root;
        }
    }
    return {};
}

float sigmoid(float x)
{
    return 1.0f / (1.0f + std::exp(-x));
}

// A square of the frame, `size` pixels on a side around (cx, cy), resampled to n×n RGB in 0..1
// (NHWC). Outside the frame is black, as in the validation: the model was checked that way.
std::vector<float> squareInput(const QImage &rgb, double cx, double cy, double size, int n)
{
    std::vector<float> input(size_t(n) * n * 3, 0.0f);
    const double scale = size / n;
    const double x0 = cx - size / 2.0;
    const double y0 = cy - size / 2.0;
    const int w = rgb.width();
    const int h = rgb.height();
    for (int y = 0; y < n; ++y) {
        const double sy = y0 + (y + 0.5) * scale - 0.5;
        if (sy < -0.5 || sy > h - 0.5)
            continue;
        const int iy = std::clamp(int(std::floor(sy)), 0, h - 1);
        const int iy1 = std::min(iy + 1, h - 1);
        const double fy = std::clamp(sy - iy, 0.0, 1.0);
        const uchar *row0 = rgb.constScanLine(iy);
        const uchar *row1 = rgb.constScanLine(iy1);
        for (int x = 0; x < n; ++x) {
            const double sx = x0 + (x + 0.5) * scale - 0.5;
            if (sx < -0.5 || sx > w - 0.5)
                continue;
            const int ix = std::clamp(int(std::floor(sx)), 0, w - 1);
            const int ix1 = std::min(ix + 1, w - 1);
            const double fx = std::clamp(sx - ix, 0.0, 1.0);
            float *out = &input[(size_t(y) * n + x) * 3];
            for (int c = 0; c < 3; ++c) {
                const double top = row0[ix * 3 + c] * (1 - fx) + row0[ix1 * 3 + c] * fx;
                const double bottom = row1[ix * 3 + c] * (1 - fx) + row1[ix1 * 3 + c] * fx;
                out[c] = float((top * (1 - fy) + bottom * fy) / 255.0);
            }
        }
    }
    return input;
}

struct Pass
{
    bool ok = false;
    double presence = 0.0;
    std::array<QPointF, kOutputPoints> points; // frame pixels
    std::array<float, kOutputPoints> visibility{};
    double cx = 0.0;
    double cy = 0.0;
    double size = 0.0;
};

} // namespace

struct BodyLandmarker::Impl
{
    bool loaded = false;
    bool loadAttempted = false;
    QString error;

    std::unique_ptr<Ort::Session> pose, segmenter;
    std::vector<std::string> poseIn, poseOut, segIn, segOut;
    int poseSize = 256;
    int segSize = 256;
    double presenceThreshold = 0.5;
    double roiScale = 1.25;
    double hairCropScale = 1.15;

    bool ensureLoaded();
    Pass runPose(const QImage &rgb, double cx, double cy, double size);
    // MediaPipe's next ROI: centred on the hip centre, twice the body scale, with a margin.
    static void roiFromPass(const Pass &pass, double roiScale, double frameLong, double *cx,
                            double *cy, double *size);
};

bool BodyLandmarker::Impl::ensureLoaded()
{
    if (loadAttempted)
        return loaded;

    const QString modelDir = resolveBodyModelDir();
    if (modelDir.isEmpty()) {
        // Not latched: the model arrives as an addon that can be installed while the app runs.
        error = QStringLiteral("Body model not found. Install the body retouch addon, place it in "
                               "models/body, or set DRIFT_BODY_MODEL_DIR.");
        return false;
    }
    if (!drift::ort::ensureLoaded(&error))
        return false;
    loadAttempted = true;

    const QDir dir(modelDir);
    QFile constants(dir.filePath(QStringLiteral("constants.json")));
    if (constants.open(QIODevice::ReadOnly)) {
        const QJsonObject obj = QJsonDocument::fromJson(constants.readAll()).object();
        poseSize = obj.value(QStringLiteral("pose_input_size")).toInt(poseSize);
        segSize = obj.value(QStringLiteral("segmenter_input_size")).toInt(segSize);
        presenceThreshold = obj.value(QStringLiteral("presence_threshold")).toDouble(presenceThreshold);
        roiScale = obj.value(QStringLiteral("roi_scale")).toDouble(roiScale);
        hairCropScale = obj.value(QStringLiteral("hair_crop_scale")).toDouble(hairCropScale);
    }

    Ort::Env &ortEnv = drift::ort::env();
    QString buildError;
    const bool built = drift::ort::buildSessions(
        ortEnv, "body", false, &buildError, [&](Ort::SessionOptions &opts) {
            pose = std::make_unique<Ort::Session>(
                ortEnv, ortPath(dir.filePath(QLatin1String(kPoseFile))).c_str(), opts);
            segmenter = std::make_unique<Ort::Session>(
                ortEnv, ortPath(dir.filePath(QLatin1String(kSegmenterFile))).c_str(), opts);
        });
    if (!built) {
        error = QStringLiteral("Failed to load body model: ") + buildError;
        pose.reset();
        segmenter.reset();
        return false;
    }
    poseIn = sessionNames(*pose, true);
    poseOut = sessionNames(*pose, false);
    segIn = sessionNames(*segmenter, true);
    segOut = sessionNames(*segmenter, false);
    loaded = true;
    return true;
}

Pass BodyLandmarker::Impl::runPose(const QImage &rgb, double cx, double cy, double size)
{
    Pass pass;
    pass.cx = cx;
    pass.cy = cy;
    pass.size = size;
    const int n = poseSize;
    std::vector<float> input = squareInput(rgb, cx, cy, size, n);

    std::vector<Ort::Value> results;
    try {
        const std::array<int64_t, 4> shape{1, n, n, 3};
        Ort::Value tensor = Ort::Value::CreateTensor<float>(drift::ort::cpuMemory(), input.data(),
                                                            input.size(), shape.data(), shape.size());
        const auto inNames = cstrs(poseIn);
        const auto outNames = cstrs(poseOut);
        results = pose->Run(Ort::RunOptions{nullptr}, inNames.data(), &tensor, 1, outNames.data(),
                            outNames.size());
    } catch (const Ort::Exception &e) {
        error = QStringLiteral("Body landmarking failed: ") + QString::fromUtf8(e.what());
        return pass;
    }

    // Told apart by size rather than by name: tf2onnx names them Identity, Identity_1, … and the
    // order is not something a re-export promises to keep.
    const float *landmarks = nullptr;
    const float *presence = nullptr;
    for (Ort::Value &value : results) {
        const auto count = value.GetTensorTypeAndShapeInfo().GetElementCount();
        if (count == size_t(kOutputPoints * kValuesPerPoint))
            landmarks = value.GetTensorData<float>();
        else if (count == 1)
            presence = value.GetTensorData<float>();
    }
    if (!landmarks || !presence) {
        error = QStringLiteral("Body landmark model returned unexpected outputs");
        return pass;
    }

    // Already a probability in this export (1.0 on a person, 0.02 on none); the visibilities are
    // logits.
    pass.presence = presence[0];
    const double scale = size / n;
    for (int i = 0; i < kOutputPoints; ++i) {
        const float *p = landmarks + i * kValuesPerPoint;
        pass.points[i] = QPointF(cx - size / 2.0 + p[0] * scale, cy - size / 2.0 + p[1] * scale);
        pass.visibility[i] = sigmoid(p[3]);
    }
    pass.ok = true;
    return pass;
}

void BodyLandmarker::Impl::roiFromPass(const Pass &pass, double roiScale, double frameLong,
                                       double *cx, double *cy, double *size)
{
    const QPointF c = pass.points[kAuxCenter];
    const QPointF s = pass.points[kAuxScale];
    const double radius = std::hypot(s.x() - c.x(), s.y() - c.y());
    *cx = c.x();
    *cy = c.y();
    // Kept within sane bounds: a wild pass must not collapse the square to nothing or blow it up.
    *size = std::clamp(2.0 * radius * roiScale, frameLong * 0.08, frameLong * 3.0);
}

BodyLandmarker::BodyLandmarker()
    : d(std::make_unique<Impl>())
{
}

BodyLandmarker::~BodyLandmarker() = default;

BodyLandmarker &BodyLandmarker::instance()
{
    // Leaked on purpose, like the other ONNX models: destroying sessions during exit, after the
    // GPU driver has started its own teardown, aborts the process.
    static BodyLandmarker *s = new BodyLandmarker;
    return *s;
}

bool BodyLandmarker::modelPresent()
{
    return !resolveBodyModelDir().isEmpty();
}

bool BodyLandmarker::available()
{
    return d->ensureLoaded();
}

QString BodyLandmarker::lastError() const
{
    return d->error;
}

BodyPose BodyLandmarker::detect(const QImage &frame, const BodyPose *hint)
{
    BodyPose out;
    if (!d->ensureLoaded() || frame.isNull())
        return out;

    const QImage rgb = frame.convertToFormat(QImage::Format_RGB888);
    const double w = rgb.width();
    const double h = rgb.height();
    const double frameLong = std::max(w, h);

    auto refine = [&](Pass pass, int times) {
        for (int i = 0; i < times && pass.ok && pass.presence >= d->presenceThreshold; ++i) {
            double cx = 0, cy = 0, size = 0;
            Impl::roiFromPass(pass, d->roiScale, frameLong, &cx, &cy, &size);
            const Pass next = d->runPose(rgb, cx, cy, size);
            if (!next.ok)
                break;
            pass = next;
        }
        return pass;
    };

    Pass pass;
    if (hint && hint->valid && hint->roiSize > 0) {
        // Tracking: start from where the person was, one look to follow them.
        pass = refine(d->runPose(rgb, hint->roiCenter.x() * w, hint->roiCenter.y() * h,
                                 hint->roiSize * w),
                      1);
    }
    if (!pass.ok || pass.presence < d->presenceThreshold) {
        // No hint, or the person was lost: the whole frame, then three refinements.
        pass = refine(d->runPose(rgb, w / 2.0, h / 2.0, frameLong), 3);
    }
    if (!pass.ok || pass.presence < d->presenceThreshold)
        return out;

    out.valid = true;
    out.score = pass.presence;
    out.points.reserve(body::kPointCount);
    out.visibility.reserve(body::kPointCount);
    for (int i = 0; i < body::kPointCount; ++i) {
        out.points.append(QPointF(pass.points[i].x() / w, pass.points[i].y() / h));
        out.visibility.append(pass.visibility[i]);
    }
    // The square this pose came from, for the next frame and for the hair crop.
    out.roiCenter = QPointF(pass.cx / w, pass.cy / h);
    out.roiSize = pass.size / w;
    return out;
}

QImage BodyLandmarker::hairCoverage(const QImage &frame, const BodyPose &pose)
{
    QImage coverage;
    if (!d->ensureLoaded() || frame.isNull())
        return coverage;

    const QImage rgb = frame.convertToFormat(QImage::Format_RGB888);
    const int w = rgb.width();
    const int h = rgb.height();
    const int n = d->segSize;

    // The person's square, a little wider so long hair fits; the whole frame (stretched to a
    // square) when no one was found. The validation showed the square is what makes the hair big
    // enough in a 256×256 input to come out clean.
    const bool squared = pose.valid && pose.roiSize > 0;
    const double cx = squared ? pose.roiCenter.x() * w : w / 2.0;
    const double cy = squared ? pose.roiCenter.y() * h : h / 2.0;
    const double size = squared ? pose.roiSize * w * d->hairCropScale : 0.0;

    std::vector<float> input;
    if (squared) {
        input = squareInput(rgb, cx, cy, size, n);
    } else {
        const QImage small = rgb.scaled(n, n, Qt::IgnoreAspectRatio, Qt::SmoothTransformation);
        input.resize(size_t(n) * n * 3);
        for (int y = 0; y < n; ++y) {
            const uchar *row = small.constScanLine(y);
            for (int x = 0; x < n * 3; ++x)
                input[size_t(y) * n * 3 + x] = row[x] / 255.0f;
        }
    }

    std::vector<Ort::Value> results;
    try {
        const std::array<int64_t, 4> shape{1, n, n, 3};
        Ort::Value tensor = Ort::Value::CreateTensor<float>(drift::ort::cpuMemory(), input.data(),
                                                            input.size(), shape.data(), shape.size());
        const auto inNames = cstrs(d->segIn);
        const auto outNames = cstrs(d->segOut);
        results = d->segmenter->Run(Ort::RunOptions{nullptr}, inNames.data(), &tensor, 1,
                                    outNames.data(), outNames.size());
    } catch (const Ort::Exception &e) {
        d->error = QStringLiteral("Hair segmentation failed: ") + QString::fromUtf8(e.what());
        return coverage;
    }
    if (results.empty()
        || results.front().GetTensorTypeAndShapeInfo().GetElementCount()
               != size_t(n) * n * kSegmenterClasses) {
        d->error = QStringLiteral("Hair segmentation model returned unexpected outputs");
        return coverage;
    }

    // Logits per class; the hair probability is the softmax of class 1. Pushed through a ramp so
    // the edge stays soft without a grey haze over everything the model was unsure about.
    const float *logits = results.front().GetTensorData<float>();
    std::vector<float> hair(size_t(n) * n);
    for (size_t i = 0; i < hair.size(); ++i) {
        const float *l = logits + i * kSegmenterClasses;
        const float top = *std::max_element(l, l + kSegmenterClasses);
        float sum = 0.0f;
        for (int c = 0; c < kSegmenterClasses; ++c)
            sum += std::exp(l[c] - top);
        const float p = std::exp(l[kHairClass] - top) / sum;
        hair[i] = std::clamp((p - 0.3f) / 0.4f, 0.0f, 1.0f);
    }

    // Back onto the frame, bilinearly.
    coverage = QImage(w, h, QImage::Format_Grayscale8);
    coverage.fill(0);
    auto at = [&](int x, int y) { return hair[size_t(std::clamp(y, 0, n - 1)) * n + std::clamp(x, 0, n - 1)]; };
    for (int y = 0; y < h; ++y) {
        uchar *row = coverage.scanLine(y);
        const double v = squared ? (y + 0.5 - (cy - size / 2.0)) / size * n - 0.5
                                 : (y + 0.5) / h * n - 0.5;
        if (v < -0.5 || v > n - 0.5)
            continue;
        const int iy = int(std::floor(v));
        const float fy = float(v - iy);
        for (int x = 0; x < w; ++x) {
            const double u = squared ? (x + 0.5 - (cx - size / 2.0)) / size * n - 0.5
                                     : (x + 0.5) / w * n - 0.5;
            if (u < -0.5 || u > n - 0.5)
                continue;
            const int ix = int(std::floor(u));
            const float fx = float(u - ix);
            const float top = at(ix, iy) * (1 - fx) + at(ix + 1, iy) * fx;
            const float bottom = at(ix, iy + 1) * (1 - fx) + at(ix + 1, iy + 1) * fx;
            row[x] = uchar(std::lround((top * (1 - fy) + bottom * fy) * 255.0f));
        }
    }
    return coverage;
}

} // namespace drift
