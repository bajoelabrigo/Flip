#include "engine/FrameInterpolator.h"

#include "engine/GpuPackageParse.h"
#include "engine/OrtSupport.h"

#include <QDir>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QMutex>
#include <QMutexLocker>

#include <onnxruntime_cxx_api.h>

#include <algorithm>
#include <array>
#include <vector>

namespace drift {

namespace {

using drift::ort::ortPath;
using drift::ort::sessionNames;

// The model's .onnx in the first root that has one: constants.json "model", else the only .onnx.
QString discoverModel()
{
    const QStringList roots = GpuPackageParse::defaultSearchPaths(
        QStringLiteral("DRIFT_INTERP_MODEL_DIR"), QStringLiteral("models/interp"),
        QStringLiteral("interp-model"));
    for (const QString &root : roots) {
        const QDir dir(root);
        QFile constants(dir.filePath(QStringLiteral("constants.json")));
        if (constants.open(QIODevice::ReadOnly)) {
            const QString name = QJsonDocument::fromJson(constants.readAll())
                                     .object()
                                     .value(QStringLiteral("model"))
                                     .toString();
            if (!name.isEmpty() && QFile::exists(dir.filePath(name)))
                return dir.filePath(name);
        }
        const QStringList onnx = dir.entryList({QStringLiteral("*.onnx")}, QDir::Files, QDir::Name);
        if (onnx.size() == 1)
            return dir.filePath(onnx.first());
    }
    return {};
}

QMutex g_mutex;
std::weak_ptr<FrameInterpolator> g_loaded;

// The frame as planar RGB floats in 0..1 into `out` at `offset` planes.
void toPlanes(const QImage &rgb, std::vector<float> &out, size_t offset)
{
    const int w = rgb.width();
    const int h = rgb.height();
    const size_t plane = size_t(w) * size_t(h);
    float *r = out.data() + offset * plane;
    float *g = r + plane;
    float *b = g + plane;
    for (int y = 0; y < h; ++y) {
        const uchar *line = rgb.constScanLine(y);
        for (int x = 0; x < w; ++x) {
            const size_t i = size_t(y) * size_t(w) + size_t(x);
            r[i] = line[3 * x] / 255.0f;
            g[i] = line[3 * x + 1] / 255.0f;
            b[i] = line[3 * x + 2] / 255.0f;
        }
    }
}

} // namespace

struct FrameInterpolator::Impl
{
    std::unique_ptr<Ort::Session> session;
    std::string inputName;
    std::string outputName;
    QMutex runMutex;
};

FrameInterpolator::FrameInterpolator()
    : d(std::make_unique<Impl>())
{
}

FrameInterpolator::~FrameInterpolator() = default;

bool FrameInterpolator::modelPresent()
{
    return !discoverModel().isEmpty();
}

std::shared_ptr<FrameInterpolator> FrameInterpolator::load(QString *error)
{
    QMutexLocker lock(&g_mutex);
    if (std::shared_ptr<FrameInterpolator> live = g_loaded.lock())
        return live;

    const QString path = discoverModel();
    if (path.isEmpty()) {
        if (error)
            *error = QStringLiteral("The frame interpolation model is not installed. Install the "
                                    "AI transitions extra.");
        return nullptr;
    }
    if (!drift::ort::ensureLoaded(error))
        return nullptr;

    std::shared_ptr<FrameInterpolator> out(new FrameInterpolator());
    Ort::Env &env = drift::ort::env();
    QString loadError;
    const bool built = drift::ort::buildSessions(env, "interp", false, &loadError,
                                                 [&](Ort::SessionOptions &opts) {
        out->d->session = std::make_unique<Ort::Session>(env, ortPath(path).c_str(), opts);
    });
    if (!built || !out->d->session) {
        if (error)
            *error = QStringLiteral("Failed to load the frame interpolation model: ") + loadError;
        return nullptr;
    }

    const std::vector<std::string> ins = sessionNames(*out->d->session, true);
    const std::vector<std::string> outs = sessionNames(*out->d->session, false);
    if (ins.size() != 1 || outs.empty()) {
        if (error)
            *error = QStringLiteral("%1 is not a RIFE \"rife_v2\" export (it must take one input).")
                         .arg(path);
        return nullptr;
    }
    out->d->inputName = ins.front();
    out->d->outputName = outs.front();
    qInfo("[interp] loaded %s", qUtf8Printable(path));
    g_loaded = out;
    return out;
}

QImage FrameInterpolator::interpolate(const QImage &a, const QImage &b, float t, QString *error)
{
    if (a.isNull() || b.isNull()) {
        if (error)
            *error = QStringLiteral("Missing frame to interpolate from");
        return {};
    }
    QSize size = a.size();
    if (std::max(size.width(), size.height()) > kMaxSide)
        size.scale(kMaxSide, kMaxSide, Qt::KeepAspectRatio);
    // Even sides: the result goes to an H.264 encoder.
    size = QSize(std::max(2, size.width() & ~1), std::max(2, size.height() & ~1));

    const QImage ra = a.convertToFormat(QImage::Format_RGB888)
                          .scaled(size, Qt::IgnoreAspectRatio, Qt::SmoothTransformation);
    const QImage rb = b.convertToFormat(QImage::Format_RGB888)
                          .scaled(size, Qt::IgnoreAspectRatio, Qt::SmoothTransformation);

    const int w = size.width();
    const int h = size.height();
    const size_t plane = size_t(w) * size_t(h);
    std::vector<float> input(plane * 7);
    toPlanes(ra, input, 0);
    toPlanes(rb, input, 3);
    std::fill(input.begin() + std::ptrdiff_t(plane * 6), input.end(), std::clamp(t, 0.0f, 1.0f));

    const std::array<int64_t, 4> shape{1, 7, h, w};
    QMutexLocker lock(&d->runMutex);
    try {
        Ort::Value tensor = Ort::Value::CreateTensor<float>(drift::ort::cpuMemory(), input.data(),
                                                            input.size(), shape.data(), shape.size());
        const char *inName = d->inputName.c_str();
        const char *outName = d->outputName.c_str();
        std::vector<Ort::Value> result =
            d->session->Run(Ort::RunOptions{nullptr}, &inName, &tensor, 1, &outName, 1);
        if (result.empty() || !result.front().IsTensor()) {
            if (error)
                *error = QStringLiteral("The interpolation model returned nothing");
            return {};
        }
        const std::vector<int64_t> outShape = result.front().GetTensorTypeAndShapeInfo().GetShape();
        if (outShape.size() != 4 || outShape[1] != 3) {
            if (error)
                *error = QStringLiteral("The interpolation model returned an unexpected shape");
            return {};
        }
        const int oh = int(outShape[2]);
        const int ow = int(outShape[3]);
        const float *data = result.front().GetTensorData<float>();
        const size_t oplane = size_t(ow) * size_t(oh);
        QImage frame(ow, oh, QImage::Format_RGB888);
        for (int y = 0; y < oh; ++y) {
            uchar *line = frame.scanLine(y);
            for (int x = 0; x < ow; ++x) {
                const size_t i = size_t(y) * size_t(ow) + size_t(x);
                for (int c = 0; c < 3; ++c)
                    line[3 * x + c] = uchar(std::clamp(data[c * oplane + i] * 255.0f + 0.5f, 0.0f, 255.0f));
            }
        }
        // A graph that pads may hand back the padded size; keep the frame's own.
        return frame.size() == size ? frame : frame.copy(0, 0, std::min(ow, w), std::min(oh, h))
                                                   .scaled(size, Qt::IgnoreAspectRatio, Qt::SmoothTransformation);
    } catch (const Ort::Exception &e) {
        if (error)
            *error = QStringLiteral("Frame interpolation failed: ") + QString::fromUtf8(e.what());
        return {};
    }
}

} // namespace drift
