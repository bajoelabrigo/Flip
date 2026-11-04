#include "TtsController.h"

#include "AppController.h"
#include "JobRegistry.h"
#include "VoiceLibrary.h"
#include "engine/AddonRegistry.h"
#include "engine/AudioFileWriter.h"
#include "engine/OrtRuntime.h"
#include "engine/SpeechAudio.h"
#include "core/ZipArchive.h"

#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QLocale>
#include <QPointer>
#include <QRegularExpression>
#include <QSettings>
#include <QUuid>

#include <soundtouch/SoundTouch.h>

#include <algorithm>
#include <map>
#include <memory>
#include <optional>

namespace {

QString slugFor(const QString &text)
{
    QString slug;
    for (const QChar c : text.toLower()) {
        if (c.isLetterOrNumber())
            slug.append(c);
        else if (!slug.isEmpty() && !slug.endsWith(QLatin1Char('-')))
            slug.append(QLatin1Char('-'));
        if (slug.size() >= 24)
            break;
    }
    while (slug.endsWith(QLatin1Char('-')))
        slug.chop(1);
    return slug.isEmpty() ? QStringLiteral("speech") : slug;
}

QString speechPath(const QString &text)
{
    return QDir(drift::generatedAudioDir())
        .filePath(QStringLiteral("tts-chatterbox-%1-%2.flac")
                      .arg(slugFor(text), QUuid::createUuid().toString(QUuid::Id128).left(8)));
}

QString jobError(const QJsonObject &job)
{
    const QJsonObject error = job.value(QStringLiteral("error")).toObject();
    return error.value(QStringLiteral("code")).toString() == QLatin1String("cancelled")
               ? QString()
               : error.value(QStringLiteral("message")).toString();
}

struct CueSpeech
{
    QString path;
    QString text;
    drift::TimeUs startUs = 0;
    double cueSeconds = 0.0;
    double speechSeconds = 0.0;
};

} // namespace

TtsController::TtsController(AppController *app, QObject *parent)
    : QObject(parent)
    , m_app(app)
{
    m_poll.setInterval(150);
    connect(&m_poll, &QTimer::timeout, this, &TtsController::pollJob);
    refreshAvailability();
}

void TtsController::refreshAvailability()
{
    const bool now = !drift::resolveChatterboxModelDir().isEmpty() && drift::ort::available();
    if (now == m_available)
        return;
    m_available = now;
    emit availableChanged();
}

QString TtsController::lastVoice() const
{
    return QSettings().value(QStringLiteral("tts/voice"), QStringLiteral("default")).toString();
}

QString TtsController::lastLanguage() const
{
    // Until one is chosen, the interface's language when the voice speaks it (it started in
    // English for everyone).
    QSettings settings;
    if (settings.contains(QStringLiteral("tts/language")))
        return settings.value(QStringLiteral("tts/language")).toString();
    QString ui = settings.value(QStringLiteral("ui/language")).toString();
    if (ui.isEmpty())
        ui = QLocale::system().name();
    QString code = ui.section(QLatin1Char('_'), 0, 0).section(QLatin1Char('-'), 0, 0).toLower();
    if (code == QLatin1String("nb") || code == QLatin1String("nn"))
        code = QStringLiteral("no");
    return drift::ChatterboxTts::supportedLanguages().contains(code) ? code : QStringLiteral("en");
}

double TtsController::lastExaggeration() const
{
    return QSettings().value(QStringLiteral("tts/exaggeration"), 0.5).toDouble();
}

void TtsController::remember(const QString &voiceId, const QString &lang, double exaggeration)
{
    QSettings settings;
    settings.setValue(QStringLiteral("tts/voice"), voiceId);
    settings.setValue(QStringLiteral("tts/language"), lang);
    settings.setValue(QStringLiteral("tts/exaggeration"), exaggeration);
    emit lastUsedChanged();
}

QVariantList TtsController::languageOptions() const
{
    QVariantList out;
    for (const QString &code : drift::ChatterboxTts::supportedLanguages()) {
        // Each language in its own name (español, français…), as the language chooser shows them:
        // languageToString is English only, so a Spanish interface listed "Spanish".
        QString label = QLocale(code).nativeLanguageName();
        // One Spanish, one Portuguese, one English for the model: not «español de España» (0.30).
        if (code == QLatin1String("es"))
            label = QStringLiteral("Español");
        else if (code == QLatin1String("pt"))
            label = QStringLiteral("Português");
        else if (code == QLatin1String("en"))
            label = QStringLiteral("English");
        if (label.isEmpty())
            label = QLocale::languageToString(QLocale(code).language());
        if (!label.isEmpty())
            label[0] = label.at(0).toUpper();
        out.append(QVariantMap{{QStringLiteral("code"), code}, {QStringLiteral("label"), label}});
    }
    return out;
}

bool TtsController::ensureLoaded(QString *err)
{
    if (m_loaded.load())
        return true;
    m_loading.store(true);
    const bool ok = m_engine.load(err);
    m_loaded.store(ok);
    m_loading.store(false);
    return ok;
}

void TtsController::setStatus(const QString &status)
{
    if (m_status == status)
        return;
    m_status = status;
    emit statusChanged();
}

void TtsController::pollJob()
{
    if (m_shownLoaded != m_loaded.load() || m_shownLoading != m_loading.load()) {
        m_shownLoaded = m_loaded.load();
        m_shownLoading = m_loading.load();
        emit loadStateChanged();
    }
    if (!m_jobId.isEmpty()) {
        const QJsonObject job = m_app->m_jobs->job(m_jobId);
        const double progress = job.value(QStringLiteral("progress")).toDouble();
        if (!qFuzzyCompare(1.0 + progress, 1.0 + m_progress)) {
            m_progress = progress;
            emit progressChanged();
        }
        const QString status = job.value(QStringLiteral("status")).toString();
        if (!status.isEmpty())
            setStatus(status);
    }
    if (m_jobId.isEmpty() && m_loadJobId.isEmpty() && !m_loading.load())
        m_poll.stop();
}

void TtsController::endJob()
{
    m_jobId.clear();
    m_running = false;
    m_progress = 0.0;
    emit runningChanged();
    emit progressChanged();
    pollJob();
}

void TtsController::warmUp()
{
    if (!m_available || m_loaded.load() || m_loading.load() || !m_loadJobId.isEmpty())
        return;
    m_loading.store(true);
    const QPointer<TtsController> self(this);
    m_loadJobId = m_app->m_jobs->start(
        QStringLiteral("tts-load"), QStringLiteral("chatterbox"), JobRegistry::Lane::Model,
        [this](JobContext &ctx) {
            ctx.progress(0.0, tr("Loading voice model…"));
            QString err;
            if (!ensureLoaded(&err))
                return ctx.fail(QStringLiteral("internal"), err);
            ctx.succeed({});
        },
        [self](const QJsonObject &job) {
            if (!self)
                return QJsonObject{};
            self->m_loadJobId.clear();
            self->pollJob();
            if (!job.value(QStringLiteral("ok")).toBool())
                emit self->finished(false, jobError(job));
            return QJsonObject{};
        });
    m_poll.start();
    pollJob();
}

void TtsController::cancel()
{
    if (!m_jobId.isEmpty())
        m_app->m_jobs->cancel(m_jobId);
}

double TtsController::lastSpeed() const
{
    return QSettings().value(QStringLiteral("tts/speed"), 1.0).toDouble();
}

double TtsController::lastPitch() const
{
    return QSettings().value(QStringLiteral("tts/pitch"), 1.0).toDouble();
}

namespace {
// A sentence ends in a short breath; a blank line, a longer one (seconds, at normal speed).
constexpr double kSentenceGap = 0.12;
constexpr double kParagraphGap = 0.45;
} // namespace

QList<QPair<QString, double>> TtsController::splitScript(const QString &text)
{
    // [pausa 1s], [pause 0.5], [pausa]: a silence there (half a second when no length is given).
    static const QRegularExpression pauseRe(QStringLiteral("\\[(?:pausa|pause)\\s*([0-9]+(?:[.,][0-9]+)?)?\\s*s?\\]"),
                                            QRegularExpression::CaseInsensitiveOption);
    static const QRegularExpression paragraphRe(QStringLiteral("\\n\\s*\\n"));
    static const QRegularExpression sentenceEndRe(QStringLiteral("(?<=[.!?…。！？])\\s+"));
    QList<QPair<QString, double>> out;
    const auto addChunk = [&](const QString &chunk) {
        const QStringList paragraphs = chunk.split(paragraphRe);
        for (int p = 0; p < paragraphs.size(); ++p) {
            QString paragraph = paragraphs.at(p);
            paragraph.replace(QLatin1Char('\n'), QLatin1Char(' '));
            for (const QString &piece : paragraph.split(sentenceEndRe, Qt::SkipEmptyParts)) {
                const QString sentence = piece.simplified();
                if (!sentence.isEmpty())
                    out.append({sentence, kSentenceGap});
            }
            if (!out.isEmpty() && p + 1 < paragraphs.size())
                out.last().second = kParagraphGap;
        }
    };
    qsizetype at = 0;
    for (auto it = pauseRe.globalMatch(text); it.hasNext();) {
        const QRegularExpressionMatch m = it.next();
        addChunk(text.mid(at, m.capturedStart() - at));
        QString length = m.captured(1);
        length.replace(QLatin1Char(','), QLatin1Char('.'));
        const double seconds = length.isEmpty() ? 0.5 : length.toDouble();
        if (!out.isEmpty())
            out.last().second = qBound(0.0, seconds, 10.0);
        at = m.capturedEnd();
    }
    addChunk(text.mid(at));
    if (!out.isEmpty())
        out.last().second = 0.0;
    return out;
}

QList<QPair<QString, QString>> TtsController::dialogueParts(const QString &text)
{
    // «Ana: Hola», «LUIS: ¿qué tal?»: a short name, then a colon. A time («10:30») or a link is not.
    static const QRegularExpression speakerRe(QStringLiteral("^\\s*([^:\\n\\d][^:\\n]{0,23}?)\\s*:\\s+(.*)$"));
    QList<QPair<QString, QString>> parts;
    QString speaker;
    QString body;
    const auto flush = [&] {
        if (!body.trimmed().isEmpty())
            parts.append({speaker, body.trimmed()});
        body.clear();
    };
    for (const QString &line : text.split(QLatin1Char('\n'))) {
        const QRegularExpressionMatch m = speakerRe.match(line);
        if (m.hasMatch() && !m.captured(1).contains(QLatin1String("//"))) {
            flush();
            speaker = m.captured(1).trimmed();
            body = m.captured(2);
        } else {
            body += QLatin1Char('\n') + line;
        }
    }
    flush();
    return parts;
}

QStringList TtsController::scriptSpeakers(const QString &text) const
{
    QStringList out;
    for (const auto &part : dialogueParts(text)) {
        if (!part.first.isEmpty() && !out.contains(part.first, Qt::CaseInsensitive))
            out.append(part.first);
    }
    return out;
}

std::vector<float> TtsController::retuned(const std::vector<float> &pcm, double speed, double pitch)
{
    speed = qBound(0.5, speed, 2.0);
    pitch = qBound(0.5, pitch, 2.0);
    if (pcm.empty() || (qFuzzyCompare(speed, 1.0) && qFuzzyCompare(pitch, 1.0)))
        return pcm;
    soundtouch::SoundTouch shifter;
    shifter.setSampleRate(drift::ChatterboxTts::kSampleRate);
    shifter.setChannels(1);
    shifter.setTempo(speed);
    shifter.setPitch(pitch);
    // As the clip pitch effect: quickseek is audible on voice, and pitch shifting resamples.
    shifter.setSetting(SETTING_USE_QUICKSEEK, 0);
    shifter.setSetting(SETTING_USE_AA_FILTER, 1);
    shifter.putSamples(pcm.data(), static_cast<uint>(pcm.size()));
    shifter.flush();
    std::vector<float> out;
    out.reserve(static_cast<size_t>(double(pcm.size()) / speed) + 4096);
    std::vector<float> buffer(4096);
    for (;;) {
        const uint got = shifter.receiveSamples(buffer.data(), static_cast<uint>(buffer.size()));
        if (got == 0)
            break;
        out.insert(out.end(), buffer.begin(), buffer.begin() + got);
    }
    return out;
}

double TtsController::gapAfter(const Line &line, double speed)
{
    // A typed pause is a length of its own; the breaths between sentences follow the speed.
    return qFuzzyCompare(line.pauseAfter, kSentenceGap) || qFuzzyCompare(line.pauseAfter, kParagraphGap)
               ? line.pauseAfter / qBound(0.5, speed, 2.0)
               : line.pauseAfter;
}

QList<drift::SubtitleCue> TtsController::takeCues(const QList<Line> &lines, double speed, int lineWidth)
{
    // The script's own words at the times each sentence is said: no listening needed (it heard
    // «Hoy vamos» as «Toy vamos»). A long sentence is split at words into lines of about
    // lineWidth letters, each timed by its share of the letters.
    QList<drift::SubtitleCue> cues;
    double at = 0.0;
    for (int i = 0; i < lines.size(); ++i) {
        const Line &line = lines.at(i);
        const QString text = line.text.simplified();
        if (line.seconds > 0.0 && !text.isEmpty()) {
            QStringList pieces;
            QString current;
            for (const QString &word : text.split(QLatin1Char(' '), Qt::SkipEmptyParts)) {
                if (!current.isEmpty() && current.size() + 1 + word.size() > qMax(8, lineWidth)) {
                    pieces << current;
                    current.clear();
                }
                current = current.isEmpty() ? word : current + QLatin1Char(' ') + word;
            }
            if (!current.isEmpty())
                pieces << current;
            qsizetype letters = 0;
            for (const QString &piece : std::as_const(pieces))
                letters += piece.size();
            double start = at;
            for (const QString &piece : std::as_const(pieces)) {
                const double length = line.seconds * double(piece.size()) / double(qMax<qsizetype>(1, letters));
                drift::SubtitleCue cue;
                cue.startUs = drift::secondsToUs(start);
                cue.endUs = drift::secondsToUs(start + length);
                cue.text = piece;
                cues.append(cue);
                start += length;
            }
        }
        at += line.seconds;
        if (i + 1 < lines.size())
            at += gapAfter(line, speed);
    }
    return cues;
}

TtsController::TakeFiles TtsController::writeTake(const QList<Line> &lines, double speed, double pitch,
                                                  const QString &script)
{
    TakeFiles files;
    const int rate = drift::ChatterboxTts::kSampleRate;
    std::vector<float> whole;
    const QString stem = QUuid::createUuid().toString(QUuid::Id128).left(8);
    for (int i = 0; i < lines.size(); ++i) {
        const Line &line = lines.at(i);
        const std::vector<float> spoken = line.pcm ? retuned(*line.pcm, speed, pitch) : std::vector<float>{};
        const QString path = QDir(drift::generatedAudioDir())
                                 .filePath(QStringLiteral("tts-line-%1-%2.flac").arg(stem).arg(i + 1));
        if (!spoken.empty() && !VoiceLibrary::writeFlac24k(path, spoken, &files.error))
            return files;
        files.linePaths.append(spoken.empty() ? QString() : path);
        files.lineSeconds.append(double(spoken.size()) / rate);
        whole.insert(whole.end(), spoken.begin(), spoken.end());
        const double gap = gapAfter(line, speed);
        if (i + 1 < lines.size())
            whole.insert(whole.end(), static_cast<size_t>(gap * rate), 0.0f);
    }
    if (whole.empty()) {
        files.error = tr("No speech was produced");
        return files;
    }
    files.path = speechPath(script);
    if (!VoiceLibrary::writeFlac24k(files.path, whole, &files.error)) {
        files.path.clear();
        return files;
    }
    files.seconds = double(whole.size()) / rate;
    return files;
}

void TtsController::clearTakeFiles(bool keepTake)
{
    for (const Line &line : std::as_const(m_lines)) {
        if (!line.path.isEmpty())
            QFile::remove(line.path);
    }
    if (!keepTake && !m_takePath.isEmpty())
        QFile::remove(m_takePath);
}

void TtsController::adoptTake(const QList<Line> &lines, const TakeFiles &files)
{
    clearTakeFiles(false);
    m_lines = lines;
    for (int i = 0; i < m_lines.size(); ++i) {
        m_lines[i].path = files.linePaths.value(i);
        m_lines[i].seconds = files.lineSeconds.value(i);
    }
    m_takePath = files.path;
    m_takeSeconds = files.seconds;
    emit takeChanged();
}

QVariantList TtsController::sentences() const
{
    QVariantList out;
    for (const Line &line : m_lines)
        out.append(QVariantMap{{QStringLiteral("text"), line.text},
                               {QStringLiteral("url"), line.path.isEmpty() ? QUrl() : QUrl::fromLocalFile(line.path)},
                               {QStringLiteral("seconds"), line.seconds}});
    return out;
}

void TtsController::startTakeJob(const QString &label, std::function<void(JobContext &)> work,
                                 std::function<void()> done)
{
    m_running = true;
    m_progress = 0.0;
    emit runningChanged();
    emit progressChanged();
    setStatus(label);
    const QPointer<TtsController> self(this);
    m_jobId = m_app->m_jobs->start(QStringLiteral("tts"), QStringLiteral("chatterbox"), JobRegistry::Lane::Model,
                                   std::move(work), [self, done](const QJsonObject &job) {
                                       if (!self)
                                           return QJsonObject{};
                                       self->endJob();
                                       if (!job.value(QStringLiteral("ok")).toBool()) {
                                           const QString message = jobError(job);
                                           self->setStatus(message.isEmpty() ? tr("Cancelled") : message);
                                           emit self->finished(false, self->m_status);
                                           return QJsonObject{};
                                       }
                                       done();
                                       return QJsonObject{};
                                   });
    m_poll.start();
}

void TtsController::generate(const QString &text, const QString &voiceId, const QString &lang,
                             double exaggeration, double speed, double pitch, const QVariantMap &speakerVoices)
{
    const QString script = text.trimmed();
    if (m_running || script.isEmpty())
        return;
    if (!m_available) {
        emit finished(false, tr("Install the voice model first"));
        return;
    }
    remember(voiceId, lang, exaggeration);
    QSettings settings;
    settings.setValue(QStringLiteral("tts/speed"), speed);
    settings.setValue(QStringLiteral("tts/pitch"), pitch);
    emit lastUsedChanged();
    auto lines = std::make_shared<QList<Line>>();
    const bool dialogue = scriptSpeakers(script).size() > 0;
    for (const auto &part : dialogueParts(script)) {
        // The speaker's voice, matched without caring for case («ANA» is «Ana»).
        QString voice;
        for (auto it = speakerVoices.cbegin(); it != speakerVoices.cend() && !part.first.isEmpty(); ++it) {
            if (it.key().compare(part.first, Qt::CaseInsensitive) == 0)
                voice = it.value().toString();
        }
        const auto sentences = splitScript(part.second);
        for (int i = 0; i < sentences.size(); ++i) {
            // A turn of the dialogue ends in a longer breath than a sentence.
            const double after = dialogue && i + 1 == sentences.size() ? kParagraphGap : sentences.at(i).second;
            lines->append({sentences.at(i).first, after, voice, {}, {}, 0.0});
        }
    }
    if (lines->isEmpty())
        return;
    lines->last().pauseAfter = 0.0;
    // «Generate again» with the same script is another reading (the first one stays the usual).
    m_scriptTries = script == m_lastTriedScript ? m_scriptTries + 1 : 0;
    m_lastTriedScript = script;
    const unsigned variant = m_scriptTries == 0 ? 0u : unsigned(m_scriptTries) * 104729u;
    auto files = std::make_shared<TakeFiles>();
    const QPointer<TtsController> self(this);
    startTakeJob(
        tr("Queued"),
        [this, lines, files, voiceId, lang, exaggeration, speed, pitch, script, variant](JobContext &ctx) {
            QString err;
            ctx.progress(0.0, tr("Loading voice model…"));
            if (!ensureLoaded(&err))
                return ctx.fail(QStringLiteral("internal"), err);
            if (ctx.cancelled())
                return;
            ctx.progress(0.02, tr("Preparing voice…"));
            // Each voice of the take prepared once (a dialogue has several).
            std::map<QString, drift::VoiceConditioning> voices;
            const int count = static_cast<int>(lines->size());
            for (int i = 0; i < count; ++i) {
                Line &line = (*lines)[i];
                const QString id = line.voiceId.isEmpty() ? voiceId : line.voiceId;
                if (voices.find(id) == voices.end()) {
                    const auto prepared = m_voices->conditioning(id, &err);
                    if (!prepared)
                        return ctx.fail(QStringLiteral("internal"), err);
                    voices.emplace(id, *prepared);
                }
                std::vector<float> pcm = m_engine.synthesize(
                    line.text, lang, voices.at(id), static_cast<float>(exaggeration),
                    [&ctx, i, count](double p) {
                        ctx.progress(0.04 + 0.92 * (i + p) / count,
                                     tr("Speaking sentence %1 of %2…").arg(i + 1).arg(count));
                        return !ctx.cancelled();
                    },
                    &err, variant == 0 ? 0u : variant + unsigned(i));
                if (ctx.cancelled())
                    return;
                if (pcm.empty())
                    return ctx.fail(QStringLiteral("internal"),
                                    tr("Sentence %1 could not be spoken: %2").arg(i + 1)
                                        .arg(err.isEmpty() ? tr("No speech was produced") : err));
                line.pcm = std::make_shared<const std::vector<float>>(std::move(pcm));
            }
            ctx.progress(0.97, tr("Putting the take together…"));
            *files = writeTake(*lines, speed, pitch, script);
            if (files->path.isEmpty())
                return ctx.fail(QStringLiteral("internal"), files->error);
            ctx.succeed({});
        },
        [self, lines, files, voiceId, lang, exaggeration, speed, pitch, script]() {
            self->m_takeScript = script;
            self->m_takeVoice = voiceId;
            self->m_takeLang = lang;
            self->m_takeExaggeration = exaggeration;
            self->m_takeSpeed = speed;
            self->m_takePitch = pitch;
            self->adoptTake(*lines, *files);
            self->setStatus(tr("Listen to it, then add it to the timeline"));
            emit self->finished(true, self->m_status);
        });
}

void TtsController::regenerateSentence(int index, const QString &voiceId, const QString &lang, double exaggeration)
{
    if (m_running || index < 0 || index >= m_lines.size())
        return;
    auto lines = std::make_shared<QList<Line>>(m_lines);
    auto files = std::make_shared<TakeFiles>();
    const double speed = m_takeSpeed;
    const double pitch = m_takePitch;
    const QString script = m_takeScript;
    const QPointer<TtsController> self(this);
    startTakeJob(
        tr("Speaking sentence %1 again…").arg(index + 1),
        [this, lines, files, index, voiceId, lang, exaggeration, speed, pitch, script](JobContext &ctx) {
            QString err;
            if (!ensureLoaded(&err))
                return ctx.fail(QStringLiteral("internal"), err);
            const auto voice = m_voices->conditioning(voiceId, &err);
            if (!voice)
                return ctx.fail(QStringLiteral("internal"), err);
            Line &line = (*lines)[index];
            const auto own = line.voiceId.isEmpty() ? std::optional<drift::VoiceConditioning>()
                                                    : m_voices->conditioning(line.voiceId, &err);
            // Another reading each time: the same words with variant 0 come back the same.
            line.redo += 1;
            std::vector<float> pcm = m_engine.synthesize(
                line.text, lang, own ? *own : *voice, static_cast<float>(exaggeration),
                [&ctx, index](double p) {
                    ctx.progress(0.05 + 0.9 * p, tr("Speaking sentence %1 again…").arg(index + 1));
                    return !ctx.cancelled();
                },
                &err, unsigned(line.redo) * 7919u + unsigned(index) + 1u);
            if (ctx.cancelled())
                return;
            if (pcm.empty())
                return ctx.fail(QStringLiteral("internal"), err.isEmpty() ? tr("No speech was produced") : err);
            line.pcm = std::make_shared<const std::vector<float>>(std::move(pcm));
            *files = writeTake(*lines, speed, pitch, script);
            if (files->path.isEmpty())
                return ctx.fail(QStringLiteral("internal"), files->error);
            ctx.succeed({});
        },
        [self, lines, files, index]() {
            self->adoptTake(*lines, *files);
            self->setStatus(tr("Sentence %1 spoken again").arg(index + 1));
            emit self->finished(true, self->m_status);
        });
}

void TtsController::retune(double speed, double pitch)
{
    if (m_running || m_lines.isEmpty()
        || (qFuzzyCompare(speed, m_takeSpeed) && qFuzzyCompare(pitch, m_takePitch)))
        return;
    QSettings settings;
    settings.setValue(QStringLiteral("tts/speed"), speed);
    settings.setValue(QStringLiteral("tts/pitch"), pitch);
    emit lastUsedChanged();
    auto lines = std::make_shared<QList<Line>>(m_lines);
    auto files = std::make_shared<TakeFiles>();
    const QString script = m_takeScript;
    const QPointer<TtsController> self(this);
    startTakeJob(
        tr("Changing speed and pitch…"),
        [lines, files, speed, pitch, script](JobContext &ctx) {
            *files = writeTake(*lines, speed, pitch, script);
            if (files->path.isEmpty())
                return ctx.fail(QStringLiteral("internal"), files->error);
            ctx.succeed({});
        },
        [self, lines, files, speed, pitch]() {
            self->m_takeSpeed = speed;
            self->m_takePitch = pitch;
            self->adoptTake(*lines, *files);
            self->setStatus(tr("Listen to it, then add it to the timeline"));
            emit self->finished(true, self->m_status);
        });
}

void TtsController::insertTake(bool captions)
{
    if (m_running || m_takePath.isEmpty())
        return;
    const QJsonObject generator{{QStringLiteral("engine"), QStringLiteral("chatterbox")},
                                {QStringLiteral("voice"), m_voices->nameFor(m_takeVoice)},
                                {QStringLiteral("voiceId"), m_takeVoice},
                                {QStringLiteral("lang"), m_takeLang},
                                {QStringLiteral("exaggeration"), m_takeExaggeration},
                                {QStringLiteral("speed"), m_takeSpeed},
                                {QStringLiteral("pitch"), m_takePitch},
                                {QStringLiteral("text"), m_takeScript}};
    QString clipId;
    const QPair<int, int> old = m_replaceClipId.isEmpty() ? qMakePair(-1, -1)
                                                          : m_app->m_mcpController->locateClip(m_replaceClipId);
    if (old.first >= 0 && captions) {
        // The old voice's captions go with it (they stacked a second subtitle track): those made
        // for it cover exactly its stretch.
        const drift::Clip &voice = m_app->m_project.tracks().at(old.first).clips.at(old.second);
        const drift::TimeUs start = voice.timelineStart;
        const drift::TimeUs length = voice.timelineDuration;
        const drift::Project before = m_app->m_project;
        bool removed = false;
        for (drift::Track &track : m_app->m_project.tracks()) {
            if (track.type != drift::TrackType::Subtitle)
                continue;
            removed = track.clips.removeIf([start, length](const drift::Clip &c) {
                          return c.type == drift::ClipType::Subtitle && c.timelineStart == start
                                 && c.timelineDuration == length;
                      }) > 0
                      || removed;
        }
        if (removed)
            m_app->pushProjectEdit(before, tr("Replace voice"));
    }
    if (old.first >= 0) {
        const AppController::GeneratedAudioImport imported =
            m_app->importGeneratedAudio(m_takePath, generator, false, 0.0, -1);
        if (!imported.ok || !m_app->swapClipAudio(m_replaceClipId, imported.assetId)) {
            setStatus(imported.ok ? tr("Could not replace the voice") : imported.error);
            emit finished(false, m_status);
            return;
        }
        clipId = m_replaceClipId;
    } else {
        const AppController::GeneratedAudioImport imported = m_app->importGeneratedAudio(
            m_takePath, generator, true, m_insertAtSeconds >= 0.0 ? m_insertAtSeconds : m_app->playheadSeconds(), -1);
        if (!imported.ok) {
            setStatus(imported.error);
            emit finished(false, imported.error);
            return;
        }
        clipId = imported.clipId;
    }
    const QString lang = m_takeLang;
    const QList<drift::SubtitleCue> scriptCues = captions ? takeCues(m_lines, m_takeSpeed, m_app->subtitleLineWidth())
                                                          : QList<drift::SubtitleCue>();
    // The take is the project's now: only the sentence files go.
    clearTakeFiles(true);
    m_lines.clear();
    m_takePath.clear();
    m_takeSeconds = 0.0;
    m_replaceClipId.clear();
    m_insertAtSeconds = -1.0;
    emit takeChanged();
    setStatus(old.first >= 0 ? tr("Voice replaced on the timeline") : tr("Speech added to the timeline"));
    emit finished(true, m_status);
    if (captions && !clipId.isEmpty()) {
        const QPair<int, int> at = m_app->m_mcpController->locateClip(clipId);
        if (at.first >= 0 && !scriptCues.isEmpty()) {
            const drift::Clip &voice = m_app->m_project.tracks().at(at.first).clips.at(at.second);
            m_app->finalizeGeneratedSubtitles(voice.timelineStart, voice.timelineDuration, scriptCues);
        } else if (at.first >= 0) {
            m_app->generateSubtitlesForClip(at.first, at.second, lang);
        }
    }
}

void TtsController::discardTake()
{
    if (m_running)
        return;
    clearTakeFiles(false);
    m_lines.clear();
    m_takePath.clear();
    m_takeSeconds = 0.0;
    m_replaceClipId.clear();
    m_insertAtSeconds = -1.0;
    emit takeChanged();
}

void TtsController::speakTextClip(int trackIndex, int clipIndex)
{
    if (m_running || !m_app->isValidClipIndex(trackIndex, clipIndex))
        return;
    const drift::Clip &clip = m_app->m_project.tracks().at(trackIndex).clips.at(clipIndex);
    const QString text = clip.textContent.trimmed();
    if (text.isEmpty())
        return;
    const double at = drift::usToSeconds(clip.timelineStart);
    discardTake();
    m_insertAtSeconds = at;
    m_draftScript = text;
    emit panelStateChanged();
    emit editRequested(QVariantMap{{QStringLiteral("text"), text},
                                   {QStringLiteral("voice"), lastVoice()},
                                   {QStringLiteral("lang"), lastLanguage()},
                                   {QStringLiteral("exaggeration"), lastExaggeration()},
                                   {QStringLiteral("speed"), lastSpeed()},
                                   {QStringLiteral("pitch"), lastPitch()}});
}

QString TtsController::clipScript(int trackIndex, int clipIndex) const
{
    if (!m_app->isValidClipIndex(trackIndex, clipIndex))
        return {};
    const drift::Clip &clip = m_app->m_project.tracks().at(trackIndex).clips.at(clipIndex);
    const drift::MediaAsset *asset = m_app->m_project.asset(clip.assetId);
    if (!asset || asset->generator.value(QStringLiteral("engine")).toString() != QLatin1String("chatterbox"))
        return {};
    return asset->generator.value(QStringLiteral("text")).toString();
}

void TtsController::editClipScript(int trackIndex, int clipIndex)
{
    const QString text = clipScript(trackIndex, clipIndex);
    if (text.isEmpty() || m_running)
        return;
    const drift::Clip &clip = m_app->m_project.tracks().at(trackIndex).clips.at(clipIndex);
    const QJsonObject g = m_app->m_project.asset(clip.assetId)->generator;
    discardTake();
    m_replaceClipId = clip.id;
    m_draftScript = text;
    // Remembered as the last used too, so a Voz tab that opens only now shows them.
    remember(g.value(QStringLiteral("voiceId")).toString(lastVoice()), g.value(QStringLiteral("lang")).toString(lastLanguage()),
             g.value(QStringLiteral("exaggeration")).toDouble(lastExaggeration()));
    QSettings settings;
    settings.setValue(QStringLiteral("tts/speed"), g.value(QStringLiteral("speed")).toDouble(1.0));
    settings.setValue(QStringLiteral("tts/pitch"), g.value(QStringLiteral("pitch")).toDouble(1.0));
    emit lastUsedChanged();
    emit panelStateChanged();
    emit takeChanged();
    emit editRequested(QVariantMap{{QStringLiteral("text"), text},
                                   {QStringLiteral("voice"), g.value(QStringLiteral("voiceId")).toString(lastVoice())},
                                   {QStringLiteral("lang"), g.value(QStringLiteral("lang")).toString(lastLanguage())},
                                   {QStringLiteral("exaggeration"), g.value(QStringLiteral("exaggeration")).toDouble(lastExaggeration())},
                                   {QStringLiteral("speed"), g.value(QStringLiteral("speed")).toDouble(1.0)},
                                   {QStringLiteral("pitch"), g.value(QStringLiteral("pitch")).toDouble(1.0)}});
}

bool TtsController::saveClipVoice(int trackIndex, int clipIndex, const QUrl &url) const
{
    if (!m_app->isValidClipIndex(trackIndex, clipIndex) || !url.isLocalFile())
        return false;
    const drift::Clip &clip = m_app->m_project.tracks().at(trackIndex).clips.at(clipIndex);
    const drift::MediaAsset *asset = m_app->m_project.asset(clip.assetId);
    if (!asset)
        return false;
    const QString target = url.toLocalFile();
    const QString suffix = QFileInfo(target).suffix().toLower();
    if (suffix == QLatin1String("wav") || suffix == QLatin1String("mp3")) {
        // WAV or MP3, as people share a voice (0.30 tests E59): decoded and written anew. The voices
        // are mono at 24 kHz (Chatterbox) or less, so that is what is kept.
        constexpr int kRate = 24000;
        const std::vector<float> pcm = drift::readMono(asset->path, 0, -1, kRate);
        if (pcm.empty())
            return false;
        drift::AudioFileWriter writer;
        QString error;
        if (!writer.open(target, kRate, 1, &error))
            return false;
        constexpr int kBlock = 1 << 15;
        for (size_t off = 0; off < pcm.size(); off += kBlock) {
            const int n = int(std::min<size_t>(kBlock, pcm.size() - off));
            if (!writer.writeFrames(pcm.data() + off, n, &error)) {
                writer.abort();
                return false;
            }
        }
        return writer.finish(&error);
    }
    if (QFile::exists(target))
        QFile::remove(target);
    return QFile::copy(asset->path, target);
}

int TtsController::duckMusicUnder(int trackIndex, int clipIndex)
{
    if (!m_app->isValidClipIndex(trackIndex, clipIndex))
        return 0;
    const drift::Clip voice = m_app->m_project.tracks().at(trackIndex).clips.at(clipIndex);
    QList<QPair<int, int>> music;
    const QList<drift::Track> &tracks = m_app->m_project.tracks();
    for (int t = 0; t < tracks.size(); ++t) {
        if (t == trackIndex || tracks.at(t).type != drift::TrackType::Audio)
            continue;
        for (int c = 0; c < tracks.at(t).clips.size(); ++c) {
            const drift::Clip &other = tracks.at(t).clips.at(c);
            if (other.timelineStart >= voice.timelineEnd() || other.timelineEnd() <= voice.timelineStart)
                continue;
            // Only the music: another voice from a script, or a recorded voiceover, is speech too and
            // stays as loud (0.30 tests E57: the other voice went down with the music, «2 clips»).
            const drift::MediaAsset *asset = m_app->m_project.asset(other.assetId);
            const bool speech = asset
                                && (asset->generator.contains(QStringLiteral("text"))
                                    || QFileInfo(asset->path).fileName().startsWith(QLatin1String("voiceover-")));
            if (!speech)
                music.append({t, c});
        }
    }
    int lowered = 0;
    for (const auto &at : std::as_const(music)) {
        const QJsonObject r = m_app->m_mcpController->duckUnder(at.first, at.second, trackIndex, {voice.id}, 0.3, 0.12, 0.25);
        if (!r.contains(QStringLiteral("error")))
            ++lowered;
    }
    m_app->setLastMessage(lowered > 0 ? tr("The music goes down under the voice (%n clip(s))", nullptr, lowered)
                                      : tr("There is no music under this voice"),
                          lowered > 0 ? QStringLiteral("success") : QStringLiteral("info"));
    return lowered;
}

QString TtsController::readScriptFile(const QUrl &url) const
{
    const QString path = url.isLocalFile() ? url.toLocalFile() : url.toString();
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly))
        return {};
    const QString suffix = QFileInfo(path).suffix();
    if (suffix.compare(QLatin1String("md"), Qt::CaseInsensitive) == 0
        || suffix.compare(QLatin1String("markdown"), Qt::CaseInsensitive) == 0) {
        // Markdown: what is read is the words, not the marks. A heading is the script's title and is
        // left out (it was read aloud as a line, «# Diálogo»: 0.30 tests E55); bullets, quotes,
        // emphasis, code and link marks go, the words stay.
        static const QRegularExpression bulletRe(QStringLiteral("^\\s*(?:[-*+]|\\d+[.)]|>)\\s+"));
        static const QRegularExpression emphasisRe(QStringLiteral("(\\*\\*|__|\\*|_|`)(.+?)\\1"));
        static const QRegularExpression linkRe(QStringLiteral("!?\\[([^\\]]*)\\]\\([^)]*\\)"));
        static const QRegularExpression ruleRe(QStringLiteral("^\\s*(?:[-*_]\\s*){3,}$"));
        QStringList lines;
        for (QString line : QString::fromUtf8(file.readAll()).split(QLatin1Char('\n'))) {
            line = line.trimmed();
            if (line.startsWith(QLatin1Char('#')) || ruleRe.match(line).hasMatch())
                continue;
            line.remove(bulletRe);
            line.replace(linkRe, QStringLiteral("\\1"));
            for (int pass = 0; pass < 3; ++pass)
                line.replace(emphasisRe, QStringLiteral("\\2"));
            lines.append(line);
        }
        return lines.join(QLatin1Char('\n')).trimmed();
    }
    if (suffix.compare(QLatin1String("docx"), Qt::CaseInsensitive) != 0)
        return QString::fromUtf8(file.readAll()).trimmed();
    // A Word document: the text of each paragraph of word/document.xml, one per line.
    QString err;
    for (const drift::zip::Entry &entry : drift::zip::readEntries(file, &err)) {
        if (entry.path != QLatin1String("word/document.xml"))
            continue;
        QByteArray xml;
        if (!drift::zip::extractEntry(file, entry, xml))
            return {};
        static const QRegularExpression paragraphRe(QStringLiteral("<w:p[ >].*?</w:p>"),
                                                    QRegularExpression::DotMatchesEverythingOption);
        static const QRegularExpression runRe(QStringLiteral("<w:t(?: [^>]*)?>(.*?)</w:t>"),
                                              QRegularExpression::DotMatchesEverythingOption);
        QStringList paragraphs;
        const QString doc = QString::fromUtf8(xml);
        for (auto p = paragraphRe.globalMatch(doc); p.hasNext();) {
            const QString body = p.next().captured(0);
            QString line;
            for (auto r = runRe.globalMatch(body); r.hasNext();)
                line += r.next().captured(1);
            line.replace(QStringLiteral("&lt;"), QStringLiteral("<"))
                .replace(QStringLiteral("&gt;"), QStringLiteral(">"))
                .replace(QStringLiteral("&quot;"), QStringLiteral("\""))
                .replace(QStringLiteral("&apos;"), QStringLiteral("'"))
                .replace(QStringLiteral("&amp;"), QStringLiteral("&"));
            paragraphs.append(line);
        }
        return paragraphs.join(QStringLiteral("\n")).trimmed();
    }
    return {};
}

void TtsController::voiceoverFromSubtitles(int trackIndex, int clipIndex, const QString &voiceId,
                                           const QString &lang, double exaggeration)
{
    if (m_running)
        return;
    if (!m_available) {
        emit finished(false, tr("Install the voice model first"));
        return;
    }
    if (!m_app->isValidClipIndex(trackIndex, clipIndex)
        || m_app->m_project.tracks().at(trackIndex).clips.at(clipIndex).type != drift::ClipType::Subtitle) {
        emit finished(false, tr("Select a subtitle clip first"));
        return;
    }
    const drift::Clip &clip = m_app->m_project.tracks().at(trackIndex).clips.at(clipIndex);
    const drift::TimeUs clipStartUs = clip.timelineStart;
    auto lines = std::make_shared<QList<CueSpeech>>();
    for (const drift::SubtitleCue &cue : clip.subtitleCues) {
        const QString text = cue.text.simplified();
        if (text.isEmpty())
            continue;
        lines->append({speechPath(text), text, cue.startUs, drift::usToSeconds(cue.endUs - cue.startUs), 0.0});
    }
    if (lines->isEmpty()) {
        emit finished(false, tr("This subtitle clip has no text to speak"));
        return;
    }
    remember(voiceId, lang, exaggeration);
    const QString voiceName = m_voices->nameFor(voiceId);
    m_running = true;
    m_progress = 0.0;
    emit runningChanged();
    emit progressChanged();
    setStatus(tr("Queued"));
    const QPointer<TtsController> self(this);
    m_jobId = m_app->m_jobs->start(
        QStringLiteral("tts"), QStringLiteral("chatterbox"), JobRegistry::Lane::Model,
        [this, lines, voiceId, lang, exaggeration](JobContext &ctx) {
            QString err;
            ctx.progress(0.0, tr("Loading voice model…"));
            if (!ensureLoaded(&err))
                return ctx.fail(QStringLiteral("internal"), err);
            if (ctx.cancelled())
                return;
            ctx.progress(0.02, tr("Preparing voice…"));
            const auto voice = m_voices->conditioning(voiceId, &err);
            if (!voice)
                return ctx.fail(QStringLiteral("internal"), err);
            const int count = static_cast<int>(lines->size());
            for (int i = 0; i < count; ++i) {
                CueSpeech &line = (*lines)[i];
                const std::vector<float> pcm = m_engine.synthesize(
                    line.text, lang, *voice, static_cast<float>(exaggeration),
                    [&ctx, i, count](double p) {
                        ctx.progress(0.05 + 0.95 * (i + p) / count,
                                     tr("Speaking line %1 of %2…").arg(i + 1).arg(count));
                        return !ctx.cancelled();
                    },
                    &err);
                if (ctx.cancelled())
                    return;
                if (pcm.empty())
                    return ctx.fail(QStringLiteral("internal"),
                                    err.isEmpty() ? tr("No speech was produced") : err);
                if (!VoiceLibrary::writeFlac24k(line.path, pcm, &err))
                    return ctx.fail(QStringLiteral("internal"), err);
                line.speechSeconds = static_cast<double>(pcm.size()) / drift::ChatterboxTts::kSampleRate;
            }
            ctx.succeed({});
        },
        [self, lines, lang, exaggeration, voiceName, clipStartUs](const QJsonObject &job) {
            if (!self)
                return QJsonObject{};
            self->endJob();
            if (!job.value(QStringLiteral("ok")).toBool()) {
                for (const CueSpeech &line : std::as_const(*lines))
                    QFile::remove(line.path);
                const QString message = jobError(job);
                self->setStatus(message.isEmpty() ? tr("Cancelled") : message);
                emit self->finished(false, self->m_status);
                return QJsonObject{};
            }
            QList<AppController::GeneratedAudioPlacement> placements;
            int longer = 0;
            int lost = 0;
            for (const CueSpeech &line : std::as_const(*lines)) {
                const QJsonObject generator{{QStringLiteral("engine"), QStringLiteral("chatterbox")},
                                            {QStringLiteral("voice"), voiceName},
                                            {QStringLiteral("lang"), lang},
                                            {QStringLiteral("exaggeration"), exaggeration},
                                            {QStringLiteral("text"), line.text}};
                if (!self->m_app->importGeneratedAudio(line.path, generator, false, 0.0, -1).ok) {
                    ++lost;
                    continue;
                }
                placements.append({line.path, drift::usToSeconds(clipStartUs + line.startUs)});
                if (line.speechSeconds > line.cueSeconds)
                    ++longer;
            }
            const int placed = self->m_app->placeGeneratedAudioOnNewTracks(placements, tr("Generate voiceover"));
            if (placed == 0) {
                self->setStatus(tr("Could not add the voiceover"));
                emit self->finished(false, self->m_status);
                return QJsonObject{};
            }
            QString message = tr("Generated %n line(s)", nullptr, placed);
            if (longer > 0)
                message += tr("; %n ran longer than their captions", nullptr, longer);
            // A line that could not be added is said, not skipped in silence (0.30).
            if (lost > 0)
                message += tr("; %n could not be added", nullptr, lost);
            self->setStatus(message);
            emit self->finished(true, message);
            return QJsonObject{};
        });
    m_poll.start();
}
