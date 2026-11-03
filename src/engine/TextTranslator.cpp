#include "engine/TextTranslator.h"

#include "engine/GpuPackageParse.h"
#include "engine/OrtSupport.h"

#include <QDir>
#include <QFile>
#include <QHash>
#include <QMutex>
#include <QMutexLocker>
#include <QRegularExpression>
#include <QTextStream>

#include <onnxruntime_cxx_api.h>

#include <algorithm>
#include <array>

namespace drift {

namespace {

using drift::ort::ortPath;
using drift::ort::sessionNames;

constexpr int64_t kPad = 1;
constexpr int64_t kEos = 2;
constexpr int64_t kUnk = 3;
constexpr int kMaxSourceTokens = 200;

QString discoverRoot()
{
    const QStringList roots = GpuPackageParse::defaultSearchPaths(
        QStringLiteral("DRIFT_TRANSLATE_MODEL_DIR"), QStringLiteral("models/translate"),
        QStringLiteral("translate-model"));
    for (const QString &root : roots) {
        const QDir dir(root);
        if (QFile::exists(dir.filePath(QStringLiteral("encoder.onnx")))
            && QFile::exists(dir.filePath(QStringLiteral("decoder.onnx")))
            && QFile::exists(dir.filePath(QStringLiteral("vocab.txt")))
            && QFile::exists(dir.filePath(QStringLiteral("merges.txt"))))
            return root;
    }
    return {};
}

QMutex g_mutex;
std::weak_ptr<TextTranslator> g_loaded;

// The characters of a string, surrogate pairs kept together.
QStringList characters(const QString &s)
{
    QStringList out;
    for (int i = 0; i < s.size(); ++i) {
        if (s.at(i).isHighSurrogate() && i + 1 < s.size()) {
            out.append(s.mid(i, 2));
            ++i;
        } else {
            out.append(s.at(i));
        }
    }
    return out;
}

bool readLines(const QString &path, QStringList *lines, QString *error)
{
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        if (error)
            *error = QStringLiteral("Cannot read %1").arg(path);
        return false;
    }
    QTextStream in(&file);
    in.setEncoding(QStringConverter::Utf8);
    while (!in.atEnd())
        lines->append(in.readLine());
    return true;
}

} // namespace

struct TextTranslator::Impl
{
    std::unique_ptr<Ort::Session> encoder;
    std::unique_ptr<Ort::Session> decoder;
    std::vector<std::string> encoderInputs;
    std::vector<std::string> decoderInputs;
    QHash<QString, int64_t> vocab;
    QStringList pieces;
    // "a\x01b" -> rank
    QHash<QString, int> ranks;
    QMutex runMutex;

    QStringList bpe(const QString &word) const;
    std::vector<int64_t> encode(const QString &text) const;
    QString decode(const std::vector<int64_t> &ids) const;
    QString translateOne(const QString &text, int64_t sourceToken, int64_t targetToken, QString *error);
};

QStringList TextTranslator::Impl::bpe(const QString &word) const
{
    QStringList syms = characters(word);
    while (syms.size() > 1) {
        int bestRank = -1;
        int at = -1;
        for (int i = 0; i + 1 < syms.size(); ++i) {
            const auto hit = ranks.constFind(syms.at(i) + QChar(1) + syms.at(i + 1));
            if (hit != ranks.constEnd() && (bestRank < 0 || hit.value() < bestRank)) {
                bestRank = hit.value();
                at = i;
            }
        }
        if (at < 0)
            break;
        syms[at] = syms.at(at) + syms.at(at + 1);
        syms.removeAt(at + 1);
    }
    return syms;
}

std::vector<int64_t> TextTranslator::Impl::encode(const QString &text) const
{
    std::vector<int64_t> ids;
    const QString normalized = text.normalized(QString::NormalizationForm_KC);
    const QStringList words = normalized.split(QRegularExpression(QStringLiteral("\\s+")), Qt::SkipEmptyParts);
    for (const QString &word : words) {
        for (const QString &piece : bpe(QStringLiteral("▁") + word)) {
            const int64_t id = vocab.value(piece, kUnk);
            // Consecutive unknowns collapse into one, as the tokenizer's fuse_unk does.
            if (id == kUnk && !ids.empty() && ids.back() == kUnk)
                continue;
            ids.push_back(id);
        }
        if (int(ids.size()) >= kMaxSourceTokens)
            break;
    }
    if (int(ids.size()) > kMaxSourceTokens)
        ids.resize(size_t(kMaxSourceTokens));
    return ids;
}

QString TextTranslator::Impl::decode(const std::vector<int64_t> &ids) const
{
    QString out;
    for (const int64_t id : ids) {
        if (id <= kUnk || id >= pieces.size())
            continue;
        const QString &piece = pieces.at(int(id));
        if (piece.startsWith(QLatin1String("__")) && piece.endsWith(QLatin1String("__")))
            continue;
        out += piece;
    }
    return out.replace(QStringLiteral("▁"), QStringLiteral(" ")).trimmed();
}

QString TextTranslator::Impl::translateOne(const QString &text, int64_t sourceToken, int64_t targetToken, QString *error)
{
    std::vector<int64_t> source{sourceToken};
    const std::vector<int64_t> body = encode(text);
    if (body.empty())
        return {};
    source.insert(source.end(), body.begin(), body.end());
    source.push_back(kEos);
    const int64_t n = int64_t(source.size());
    std::vector<int64_t> mask(size_t(n), 1);
    const std::array<int64_t, 2> shape{1, n};

    std::vector<Ort::Value> encoderOut;
    {
        std::vector<Ort::Value> inputs;
        std::vector<const char *> names;
        for (const std::string &name : encoderInputs) {
            std::vector<int64_t> *data = name == "attention_mask" ? &mask : &source;
            inputs.push_back(Ort::Value::CreateTensor<int64_t>(drift::ort::cpuMemory(), data->data(), data->size(),
                                                               shape.data(), shape.size()));
            names.push_back(name.c_str());
        }
        const char *outName = "last_hidden_state";
        encoderOut = encoder->Run(Ort::RunOptions{nullptr}, names.data(), inputs.data(), inputs.size(), &outName, 1);
    }
    const std::vector<int64_t> hiddenShape = encoderOut.front().GetTensorTypeAndShapeInfo().GetShape();
    if (hiddenShape.size() != 3) {
        if (error)
            *error = QStringLiteral("The translation model returned an unexpected shape");
        return {};
    }
    const float *hidden = encoderOut.front().GetTensorData<float>();
    std::vector<float> hiddenCopy(hidden, hidden + hiddenShape[0] * hiddenShape[1] * hiddenShape[2]);

    std::vector<int64_t> out{kEos, targetToken};
    const int maxSteps = std::min(200, int(n) * 3 + 10);
    for (int step = 0; step < maxSteps; ++step) {
        const std::array<int64_t, 2> decShape{1, int64_t(out.size())};
        std::vector<Ort::Value> inputs;
        std::vector<const char *> names;
        for (const std::string &name : decoderInputs) {
            if (name == "encoder_attention_mask") {
                inputs.push_back(Ort::Value::CreateTensor<int64_t>(drift::ort::cpuMemory(), mask.data(), mask.size(),
                                                                   shape.data(), shape.size()));
            } else if (name == "encoder_hidden_states") {
                inputs.push_back(Ort::Value::CreateTensor<float>(drift::ort::cpuMemory(), hiddenCopy.data(),
                                                                 hiddenCopy.size(), hiddenShape.data(),
                                                                 hiddenShape.size()));
            } else {
                inputs.push_back(Ort::Value::CreateTensor<int64_t>(drift::ort::cpuMemory(), out.data(), out.size(),
                                                                   decShape.data(), decShape.size()));
            }
            names.push_back(name.c_str());
        }
        const char *outName = "logits";
        std::vector<Ort::Value> result =
            decoder->Run(Ort::RunOptions{nullptr}, names.data(), inputs.data(), inputs.size(), &outName, 1);
        const std::vector<int64_t> logitShape = result.front().GetTensorTypeAndShapeInfo().GetShape();
        const int64_t vocabSize = logitShape.back();
        const float *logits = result.front().GetTensorData<float>() + (int64_t(out.size()) - 1) * vocabSize;
        int64_t best = kEos;
        float bestScore = -1e30f;
        for (int64_t v = 0; v < vocabSize; ++v) {
            if (v == kPad || v == kUnk)
                continue;
            if (logits[v] > bestScore) {
                bestScore = logits[v];
                best = v;
            }
        }
        out.push_back(best);
        if (best == kEos)
            break;
    }
    return decode(out);
}

TextTranslator::TextTranslator()
    : d(std::make_unique<Impl>())
{
}

TextTranslator::~TextTranslator() = default;

bool TextTranslator::modelPresent()
{
    return !discoverRoot().isEmpty();
}

QString TextTranslator::languageCode(const QString &appCode)
{
    // The app offers DeepL's codes; the model has one per language (100 of them).
    static const QHash<QString, QString> special = {
        {QStringLiteral("pt-br"), QStringLiteral("pt")}, {QStringLiteral("pt-pt"), QStringLiteral("pt")},
        {QStringLiteral("en-us"), QStringLiteral("en")}, {QStringLiteral("en-gb"), QStringLiteral("en")},
        {QStringLiteral("nb"), QStringLiteral("no")},    {QStringLiteral("zh-hans"), QStringLiteral("zh")},
        {QStringLiteral("zh-hant"), QStringLiteral("zh")},
    };
    const QString code = appCode.trimmed().toLower().replace(QLatin1Char('_'), QLatin1Char('-'));
    if (special.contains(code))
        return special.value(code);
    return code.section(QLatin1Char('-'), 0, 0);
}

std::shared_ptr<TextTranslator> TextTranslator::load(QString *error)
{
    QMutexLocker lock(&g_mutex);
    if (std::shared_ptr<TextTranslator> live = g_loaded.lock())
        return live;
    const QString root = discoverRoot();
    if (root.isEmpty()) {
        if (error)
            *error = QStringLiteral("The offline translation model is not installed. Install the Offline translation extra.");
        return nullptr;
    }
    if (!drift::ort::ensureLoaded(error))
        return nullptr;

    std::shared_ptr<TextTranslator> out(new TextTranslator());
    const QDir dir(root);
    QStringList merges;
    if (!readLines(dir.filePath(QStringLiteral("vocab.txt")), &out->d->pieces, error)
        || !readLines(dir.filePath(QStringLiteral("merges.txt")), &merges, error))
        return nullptr;
    out->d->vocab.reserve(out->d->pieces.size());
    for (int i = 0; i < out->d->pieces.size(); ++i) {
        if (!out->d->vocab.contains(out->d->pieces.at(i)))
            out->d->vocab.insert(out->d->pieces.at(i), i);
    }
    out->d->ranks.reserve(merges.size());
    for (int i = 0; i < merges.size(); ++i) {
        const int space = merges.at(i).indexOf(QLatin1Char(' '));
        if (space > 0)
            out->d->ranks.insert(merges.at(i).left(space) + QChar(1) + merges.at(i).mid(space + 1), i);
    }
    if (out->d->vocab.size() < 1000 || out->d->ranks.size() < 1000) {
        if (error)
            *error = QStringLiteral("%1 has no usable vocabulary").arg(root);
        return nullptr;
    }

    Ort::Env &env = drift::ort::env();
    QString loadError;
    // int8 graphs only have CPU kernels for some ops; the CPU provider is the safe home for them.
    const bool built = drift::ort::buildSessions(env, "translate", false, &loadError, [&](Ort::SessionOptions &opts) {
        out->d->encoder = std::make_unique<Ort::Session>(env, ortPath(dir.filePath(QStringLiteral("encoder.onnx"))).c_str(), opts);
        out->d->decoder = std::make_unique<Ort::Session>(env, ortPath(dir.filePath(QStringLiteral("decoder.onnx"))).c_str(), opts);
    });
    if (!built || !out->d->encoder || !out->d->decoder) {
        if (error)
            *error = QStringLiteral("Failed to load the offline translation model: ") + loadError;
        return nullptr;
    }
    out->d->encoderInputs = sessionNames(*out->d->encoder, true);
    out->d->decoderInputs = sessionNames(*out->d->decoder, true);
    qInfo("[translate] loaded %s (%lld pieces, %lld merges)", qUtf8Printable(root), qlonglong(out->d->vocab.size()),
          qlonglong(out->d->ranks.size()));
    g_loaded = out;
    return out;
}

QStringList TextTranslator::translate(const QStringList &texts, const QString &source, const QString &target,
                                      QString *error)
{
    const QString src = languageCode(source.isEmpty() ? QStringLiteral("es") : source);
    const QString tgt = languageCode(target);
    // "auto" (the captions' language detected per clip) or one the model lacks reads as Spanish.
    int64_t srcToken = d->vocab.value(QStringLiteral("__%1__").arg(src), -1);
    if (srcToken < 0)
        srcToken = d->vocab.value(QStringLiteral("__es__"), -1);
    const int64_t tgtToken = d->vocab.value(QStringLiteral("__%1__").arg(tgt), -1);
    if (srcToken < 0 || tgtToken < 0) {
        if (error)
            *error = QStringLiteral("The offline translation does not know that language");
        return {};
    }
    QMutexLocker lock(&d->runMutex);
    QStringList out;
    try {
        for (const QString &text : texts) {
            QString one = d->translateOne(text, srcToken, tgtToken, error);
            if (one.isEmpty() && error && !error->isEmpty())
                return {};
            out.append(one);
        }
    } catch (const Ort::Exception &e) {
        if (error)
            *error = QStringLiteral("Offline translation failed: %1").arg(QString::fromUtf8(e.what()));
        return {};
    }
    return out;
}

} // namespace drift
