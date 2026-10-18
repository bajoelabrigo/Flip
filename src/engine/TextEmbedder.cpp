#include "engine/TextEmbedder.h"

#include "engine/GpuPackageParse.h"
#include "engine/OrtSupport.h"

#include <QDir>
#include <QFile>
#include <QHash>
#include <QMutex>
#include <QMutexLocker>
#include <QRegularExpression>
#include <QStringList>
#include <QTextStream>

#include <onnxruntime_cxx_api.h>

#include <algorithm>
#include <array>
#include <cmath>

namespace drift {

namespace {

using drift::ort::ortPath;
using drift::ort::sessionNames;

constexpr int kBos = 0;
constexpr int kEos = 2;
constexpr int kUnk = 3;
constexpr int kMaxTokens = 128;

QString discoverRoot()
{
    const QStringList roots = GpuPackageParse::defaultSearchPaths(
        QStringLiteral("DRIFT_TEXTEMBED_MODEL_DIR"), QStringLiteral("models/textembed"),
        QStringLiteral("text-embed-model"));
    for (const QString &root : roots) {
        const QDir dir(root);
        if (QFile::exists(dir.filePath(QStringLiteral("model.onnx")))
            && QFile::exists(dir.filePath(QStringLiteral("vocab.txt"))))
            return root;
    }
    return {};
}

QMutex g_mutex;
std::weak_ptr<TextEmbedder> g_loaded;

} // namespace

struct TextEmbedder::Impl
{
    std::unique_ptr<Ort::Session> session;
    std::vector<std::string> inputNames;
    std::string outputName;
    // piece -> (id, score); pieces are compared as UTF-32 code point sequences.
    QHash<QString, QPair<int, float>> vocab;
    int maxPieceLength = 1;
    float unknownScore = -100.0f;
    QMutex runMutex;

    bool loadVocab(const QString &path, QString *error);
    std::vector<int64_t> tokenize(const QString &text) const;
};

bool TextEmbedder::Impl::loadVocab(const QString &path, QString *error)
{
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        if (error)
            *error = QStringLiteral("Cannot read %1").arg(path);
        return false;
    }
    QTextStream in(&file);
    in.setEncoding(QStringConverter::Utf8);
    int id = 0;
    float minScore = 0.0f;
    vocab.reserve(260000);
    while (!in.atEnd()) {
        const QString line = in.readLine();
        const int tab = line.lastIndexOf(QLatin1Char('\t'));
        if (tab > 0) {
            const QString piece = line.left(tab);
            const float score = line.mid(tab + 1).toFloat();
            if (!vocab.contains(piece))
                vocab.insert(piece, qMakePair(id, score));
            maxPieceLength = std::max(maxPieceLength, int(piece.toUcs4().size()));
            minScore = std::min(minScore, score);
        }
        ++id;
    }
    unknownScore = minScore - 10.0f;
    if (vocab.size() < 1000) {
        if (error)
            *error = QStringLiteral("%1 is not a SentencePiece vocabulary").arg(path);
        return false;
    }
    return true;
}

std::vector<int64_t> TextEmbedder::Impl::tokenize(const QString &text) const
{
    std::vector<int64_t> ids{kBos};
    const QString normalized = text.normalized(QString::NormalizationForm_KC);
    const QStringList words = normalized.split(QRegularExpression(QStringLiteral("\\s+")), Qt::SkipEmptyParts);
    for (const QString &word : words) {
        const QList<uint> w = (QStringLiteral("▁") + word).toUcs4();
        const int n = int(w.size());
        std::vector<double> best(size_t(n) + 1, -1e30);
        std::vector<std::pair<int, int>> back(size_t(n) + 1, {-1, kUnk});
        best[0] = 0.0;
        for (int i = 1; i <= n; ++i) {
            for (int j = std::max(0, i - maxPieceLength); j < i; ++j) {
                if (best[size_t(j)] <= -1e29)
                    continue;
                const QString piece = QString::fromUcs4(reinterpret_cast<const char32_t *>(w.constData() + j), i - j);
                const auto hit = vocab.constFind(piece);
                double score;
                int pid;
                if (hit != vocab.constEnd()) {
                    score = best[size_t(j)] + hit->second;
                    pid = hit->first;
                } else if (i - j == 1) {
                    score = best[size_t(j)] + unknownScore;
                    pid = kUnk;
                } else {
                    continue;
                }
                if (score > best[size_t(i)]) {
                    best[size_t(i)] = score;
                    back[size_t(i)] = {j, pid};
                }
            }
        }
        std::vector<int64_t> pieces;
        for (int i = n; i > 0 && back[size_t(i)].first >= 0; i = back[size_t(i)].first)
            pieces.push_back(back[size_t(i)].second);
        std::reverse(pieces.begin(), pieces.end());
        for (const int64_t pid : pieces) {
            // Consecutive unknowns collapse into one, as SentencePiece does.
            if (pid == kUnk && !ids.empty() && ids.back() == kUnk)
                continue;
            ids.push_back(pid);
        }
        if (int(ids.size()) >= kMaxTokens - 1)
            break;
    }
    if (int(ids.size()) > kMaxTokens - 1)
        ids.resize(size_t(kMaxTokens - 1));
    ids.push_back(kEos);
    return ids;
}

TextEmbedder::TextEmbedder()
    : d(std::make_unique<Impl>())
{
}

TextEmbedder::~TextEmbedder() = default;

bool TextEmbedder::modelPresent()
{
    return !discoverRoot().isEmpty();
}

std::shared_ptr<TextEmbedder> TextEmbedder::load(QString *error)
{
    QMutexLocker lock(&g_mutex);
    if (std::shared_ptr<TextEmbedder> live = g_loaded.lock())
        return live;
    const QString root = discoverRoot();
    if (root.isEmpty()) {
        if (error)
            *error = QStringLiteral("The AI text model is not installed. Install the AI text extra.");
        return nullptr;
    }
    if (!drift::ort::ensureLoaded(error))
        return nullptr;

    std::shared_ptr<TextEmbedder> out(new TextEmbedder());
    if (!out->d->loadVocab(QDir(root).filePath(QStringLiteral("vocab.txt")), error))
        return nullptr;

    Ort::Env &env = drift::ort::env();
    QString loadError;
    const QString modelPath = QDir(root).filePath(QStringLiteral("model.onnx"));
    // int8 graphs only have CPU kernels for some ops; the CPU provider is the safe home for them.
    const bool built = drift::ort::buildSessions(env, "textembed", false, &loadError,
                                                 [&](Ort::SessionOptions &opts) {
        out->d->session = std::make_unique<Ort::Session>(env, ortPath(modelPath).c_str(), opts);
    });
    if (!built || !out->d->session) {
        if (error)
            *error = QStringLiteral("Failed to load the AI text model: ") + loadError;
        return nullptr;
    }
    out->d->inputNames = sessionNames(*out->d->session, true);
    const std::vector<std::string> outs = sessionNames(*out->d->session, false);
    if (outs.empty() || out->d->inputNames.empty()) {
        if (error)
            *error = QStringLiteral("%1 has no inputs or outputs").arg(modelPath);
        return nullptr;
    }
    out->d->outputName = outs.front();
    qInfo("[textembed] loaded %s (%lld pieces)", qUtf8Printable(modelPath), qlonglong(out->d->vocab.size()));
    g_loaded = out;
    return out;
}

std::vector<float> TextEmbedder::embed(const QString &text, QString *error)
{
    const std::vector<int64_t> ids = d->tokenize(text);
    const int64_t n = int64_t(ids.size());
    std::vector<int64_t> inputIds = ids;
    std::vector<int64_t> mask(size_t(n), 1);
    std::vector<int64_t> types(size_t(n), 0);
    const std::array<int64_t, 2> shape{1, n};

    QMutexLocker lock(&d->runMutex);
    try {
        std::vector<Ort::Value> inputs;
        std::vector<const char *> names;
        for (const std::string &name : d->inputNames) {
            std::vector<int64_t> *data = name == "attention_mask" ? &mask
                                       : name == "token_type_ids" ? &types
                                                                  : &inputIds;
            inputs.push_back(Ort::Value::CreateTensor<int64_t>(drift::ort::cpuMemory(), data->data(),
                                                               data->size(), shape.data(), shape.size()));
            names.push_back(name.c_str());
        }
        const char *outName = d->outputName.c_str();
        std::vector<Ort::Value> result = d->session->Run(Ort::RunOptions{nullptr}, names.data(), inputs.data(),
                                                         inputs.size(), &outName, 1);
        const std::vector<int64_t> outShape = result.front().GetTensorTypeAndShapeInfo().GetShape();
        if (outShape.size() != 3 || outShape[1] != n) {
            if (error)
                *error = QStringLiteral("The AI text model returned an unexpected shape");
            return {};
        }
        const int64_t dim = outShape[2];
        const float *data = result.front().GetTensorData<float>();
        std::vector<float> pooled(size_t(dim), 0.0f);
        for (int64_t t = 0; t < n; ++t) {
            for (int64_t k = 0; k < dim; ++k)
                pooled[size_t(k)] += data[t * dim + k];
        }
        double norm = 0.0;
        for (float &v : pooled) {
            v /= float(n);
            norm += double(v) * double(v);
        }
        norm = std::sqrt(norm);
        if (norm > 0.0) {
            for (float &v : pooled)
                v = float(v / norm);
        }
        return pooled;
    } catch (const Ort::Exception &e) {
        if (error)
            *error = QStringLiteral("AI text failed: ") + QString::fromUtf8(e.what());
        return {};
    }
}

float TextEmbedder::cosine(const std::vector<float> &a, const std::vector<float> &b)
{
    if (a.size() != b.size() || a.empty())
        return -1.0f;
    double dot = 0.0;
    for (size_t i = 0; i < a.size(); ++i)
        dot += double(a[i]) * double(b[i]);
    return float(dot);
}

} // namespace drift
