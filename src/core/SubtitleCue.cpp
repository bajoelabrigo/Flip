#include "SubtitleCue.h"

#include <QCoreApplication>
#include <QRegularExpression>

#include <algorithm>
#include <cmath>

namespace drift {

QString subtitleClipName(const QList<SubtitleCue> &cues)
{
    if (cues.isEmpty())
        return QCoreApplication::translate("SubtitleCue", "Subtitles");
    return QCoreApplication::translate("SubtitleCue", "Subtitles (%1)").arg(cues.size());
}

namespace {

struct TimedWord
{
    TimeUs startUs = 0;
    TimeUs endUs = 0;
    QString word; // may include a leading space (Whisper-style)
};

// Split "Hello world. How are you?" into ["Hello", " world.", " How", " are", " you?"] so
// joining reproduces the original spacing/punctuation.
QStringList tokenizeWords(const QString &text)
{
    static const QRegularExpression re(QStringLiteral(R"((\s*\S+))"));
    QStringList tokens;
    auto it = re.globalMatch(text);
    while (it.hasNext())
        tokens.append(it.next().captured(1));
    return tokens;
}

QList<TimedWord> wordsFromCue(const SubtitleCue &cue)
{
    const QString text = cue.text;
    const QStringList tokens = tokenizeWords(text);
    QList<TimedWord> words;
    if (tokens.isEmpty())
        return words;

    int totalWeight = 0;
    QList<int> weights;
    weights.reserve(tokens.size());
    for (const QString &tok : tokens) {
        const int w = std::max(1, static_cast<int>(tok.trimmed().size()));
        weights.append(w);
        totalWeight += w;
    }

    const TimeUs span = std::max<TimeUs>(1, cue.endUs - cue.startUs);
    TimeUs cursor = cue.startUs;
    for (int i = 0; i < tokens.size(); ++i) {
        TimedWord tw;
        tw.word = tokens.at(i);
        tw.startUs = cursor;
        if (i + 1 == tokens.size()) {
            tw.endUs = cue.endUs;
        } else {
            const TimeUs dur =
                static_cast<TimeUs>((static_cast<double>(weights.at(i)) / totalWeight) * span);
            tw.endUs = std::min(cue.endUs, cursor + std::max<TimeUs>(1, dur));
        }
        if (tw.endUs <= tw.startUs)
            tw.endUs = tw.startUs + 1;
        cursor = tw.endUs;
        words.append(tw);
    }
    if (!words.isEmpty())
        words.last().endUs = cue.endUs;
    return words;
}

QList<TimedWord> flattenWords(const QList<SubtitleCue> &cues)
{
    QList<TimedWord> all;
    for (const SubtitleCue &cue : cues) {
        const QString trimmed = cue.text.trimmed();
        if (trimmed.isEmpty() || cue.endUs <= cue.startUs)
            continue;
        all += wordsFromCue(cue);
    }
    return all;
}

} // namespace

int activeWordIndexAt(const QString &text, TimeUs startUs, TimeUs endUs, TimeUs localUs)
{
    if (endUs <= startUs || localUs < startUs)
        return -1;

    SubtitleCue cue;
    cue.startUs = startUs;
    cue.endUs = endUs;
    cue.text = text;
    const QList<TimedWord> words = wordsFromCue(cue);
    for (int i = 0; i < words.size(); ++i) {
        if (localUs < words.at(i).endUs)
            return i;
    }
    // Past the last word's end (rounding, or the window overrunning the text): keep it lit.
    return words.isEmpty() ? -1 : words.size() - 1;
}

const SubtitleCue *activeSubtitleCueAt(const QList<SubtitleCue> &cues, TimeUs localUs)
{
    for (const SubtitleCue &cue : cues) {
        if (localUs >= cue.startUs && localUs < cue.endUs)
            return &cue;
    }
    return nullptr;
}

int subtitleCueIndexAt(const QList<SubtitleCue> &cues, TimeUs localUs)
{
    for (int i = 0; i < cues.size(); ++i) {
        const SubtitleCue &cue = cues.at(i);
        if (localUs >= cue.startUs && localUs < cue.endUs)
            return i;
    }
    return -1;
}

void sortSubtitleCues(QList<SubtitleCue> &cues)
{
    std::sort(cues.begin(), cues.end(), [](const SubtitleCue &a, const SubtitleCue &b) {
        if (a.startUs != b.startUs)
            return a.startUs < b.startUs;
        return a.endUs < b.endUs;
    });
}

QList<SubtitleCue> packSubtitleCues(const QList<SubtitleCue> &cues, int maxLineWidth,
                                    int maxLineCount, int maxWordsPerCue)
{
    if (cues.isEmpty())
        return {};

    // Mirror openai-whisper SubtitlesWriter: packing only applies when both limits are set.
    if (maxLineWidth <= 0 || maxLineCount <= 0)
        return cues;

    const QList<TimedWord> words = flattenWords(cues);
    if (words.isEmpty())
        return {};

    constexpr TimeUs kLongPauseUs = 3 * kUsPerSecond;

    QList<SubtitleCue> packed;
    QList<TimedWord> subtitle;
    int lineLen = 0;
    int lineCount = 1;
    int wordCount = 0;
    TimeUs lastStart = words.first().startUs;

    auto flush = [&]() {
        if (subtitle.isEmpty())
            return;
        SubtitleCue cue;
        cue.startUs = subtitle.first().startUs;
        cue.endUs = subtitle.last().endUs;
        QString text;
        for (const TimedWord &w : subtitle)
            text += w.word;
        cue.text = text.trimmed().replace(QLatin1Char('\n'), QLatin1Char(' '));
        if (!cue.text.isEmpty() && cue.endUs > cue.startUs)
            packed.append(cue);
        subtitle.clear();
        lineLen = 0;
        lineCount = 1;
        wordCount = 0;
    };

    for (TimedWord timing : words) {
        const bool longPause = timing.startUs - lastStart > kLongPauseUs;
        const bool hasRoom = lineLen + timing.word.size() <= maxLineWidth;
        const bool wordCapHit = maxWordsPerCue > 0 && wordCount >= maxWordsPerCue;

        if (lineLen > 0 && hasRoom && !longPause && !wordCapHit) {
            lineLen += timing.word.size();
            subtitle.append(timing);
            ++wordCount;
        } else {
            timing.word = timing.word.trimmed();
            if (!subtitle.isEmpty() && (longPause || wordCapHit || lineCount >= maxLineCount)) {
                flush();
            } else if (lineLen > 0) {
                ++lineCount;
                timing.word = QLatin1Char('\n') + timing.word;
            }
            lineLen = timing.word.trimmed().size();
            subtitle.append(timing);
            ++wordCount;
        }
        lastStart = timing.startUs;

        // Natural breaks: a sentence ends the caption, and a clause does once the line is half
        // full, so a caption reads as a phrase instead of stopping wherever the width ran out.
        const QString word = timing.word.trimmed();
        if (!word.isEmpty() && maxWordsPerCue != 1) {
            const QChar last = word.back();
            const bool sentenceEnd = last == QLatin1Char('.') || last == QLatin1Char('?')
                                     || last == QLatin1Char('!') || last == QChar(0x2026);
            const bool clauseEnd = last == QLatin1Char(',') || last == QLatin1Char(';')
                                   || last == QLatin1Char(':');
            if (sentenceEnd || (clauseEnd && lineCount == maxLineCount && lineLen * 2 >= maxLineWidth))
                flush();
        }
    }
    flush();

    sortSubtitleCues(packed);
    return packed;
}

namespace {

// Hesitations only: sounds, never words ("este", "o sea" are real Spanish and stay).
bool isHesitation(const QString &word)
{
    static const QStringList kHesitations = {
        QStringLiteral("eh"), QStringLiteral("ehh"), QStringLiteral("ehm"), QStringLiteral("em"),
        QStringLiteral("emm"), QStringLiteral("mm"), QStringLiteral("mmm"), QStringLiteral("hmm"),
        QStringLiteral("uh"), QStringLiteral("um"), QStringLiteral("umm"), QStringLiteral("ah"),
        QStringLiteral("ahh"), QStringLiteral("eeh"), QStringLiteral("mmh"),
    };
    QString bare;
    for (const QChar c : word)
        if (c.isLetter())
            bare.append(c.toLower());
    return !bare.isEmpty() && kHesitations.contains(bare);
}

} // namespace

QString cleanSubtitleText(const QString &text)
{
    const QStringList words = text.split(QLatin1Char(' '), Qt::SkipEmptyParts);
    QStringList kept;
    QString opening; // "¿" / "¡" a dropped hesitation opened with, for the next word
    for (const QString &word : words) {
        if (!isHesitation(word)) {
            kept.append(opening + word);
            opening.clear();
            continue;
        }
        for (const QChar c : word) {
            if (c.isLetter())
                break;
            if (c == QChar(0x00BF) || c == QChar(0x00A1))
                opening.append(c);
        }
        // "eh," before a word: keep a sentence end the hesitation carried.
        const QChar last = word.back();
        if (!kept.isEmpty() && (last == QLatin1Char('.') || last == QLatin1Char('?') || last == QLatin1Char('!'))
            && !kept.last().back().isPunct())
            kept.last().append(last);
    }
    QString out = kept.join(QLatin1Char(' ')).trimmed();
    // Leading punctuation a removed hesitation left behind (", y entonces").
    while (!out.isEmpty() && (out.front() == QLatin1Char(',') || out.front() == QLatin1Char(';')))
        out = out.mid(1).trimmed();
    // Capitalise the first letter, past any opening ¿ ¡ « " (.
    for (int i = 0; i < out.size(); ++i) {
        if (out.at(i).isLetter()) {
            out[i] = out.at(i).toUpper();
            break;
        }
        if (!out.at(i).isPunct() && !out.at(i).isSpace())
            break;
    }
    return out;
}

QList<SubtitleCue> cleanSubtitleCues(const QList<SubtitleCue> &cues)
{
    QList<SubtitleCue> out;
    for (SubtitleCue cue : cues) {
        cue.text = cleanSubtitleText(cue.text);
        if (!cue.text.isEmpty())
            out.append(cue);
    }
    return out;
}

QString applySubtitleReplacements(const QString &text, const QList<QPair<QString, QString>> &pairs)
{
    QString out = text;
    for (const auto &pair : pairs) {
        if (pair.first.trimmed().isEmpty())
            continue;
        // Whole words, any case: "jesus" fixes "Jesus" and "JESUS" but not "jesusito".
        const QRegularExpression re(QStringLiteral("(?<![\\p{L}\\p{N}])%1(?![\\p{L}\\p{N}])")
                                        .arg(QRegularExpression::escape(pair.first.trimmed())),
                                    QRegularExpression::CaseInsensitiveOption
                                        | QRegularExpression::UseUnicodePropertiesOption);
        out.replace(re, pair.second);
    }
    return out;
}

} // namespace drift
