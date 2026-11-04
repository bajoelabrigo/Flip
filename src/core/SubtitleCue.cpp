#include "SubtitleCue.h"

#include <QCoreApplication>
#include <QLibrary>
#include <QRegularExpression>
#include <QSet>

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
// Thai is written without spaces between words. Windows 10 and later ship ICU (icu.dll), whose
// dictionary word breaker finds them; without it a Thai run stays one unit, as before.
QStringList splitThaiWords(const QString &token)
{
    using Open = void *(*)(int, const char *, const char16_t *, int32_t, int *);
    using Step = int32_t (*)(void *);
    using Close = void (*)(void *);
    static Open open = nullptr;
    static Step first = nullptr;
    static Step next = nullptr;
    static Close close = nullptr;
    static const bool loaded = [] {
#ifdef Q_OS_WIN
        QLibrary icu(QStringLiteral("icu"));
        if (!icu.load())
            return false;
        open = reinterpret_cast<Open>(icu.resolve("ubrk_open"));
        first = reinterpret_cast<Step>(icu.resolve("ubrk_first"));
        next = reinterpret_cast<Step>(icu.resolve("ubrk_next"));
        close = reinterpret_cast<Close>(icu.resolve("ubrk_close"));
        return open && first && next && close;
#else
        return false;
#endif
    }();
    if (!loaded)
        return {token};
    int status = 0;
    void *breaker = open(1 /* UBRK_WORD */, "th", reinterpret_cast<const char16_t *>(token.utf16()),
                         int32_t(token.size()), &status);
    if (!breaker || status > 0)
        return {token};
    QStringList words;
    int32_t from = first(breaker);
    for (int32_t to = next(breaker); to != -1; to = next(breaker)) {
        const QString piece = token.mid(from, to - from);
        // Spaces and punctuation stay with the word before them, as the other tokens do.
        if (!words.isEmpty() && (piece.trimmed().isEmpty() || !piece.at(0).isLetterOrNumber()))
            words.last() += piece;
        else
            words.append(piece);
        from = to;
    }
    close(breaker);
    return words.isEmpty() ? QStringList{token} : words;
}

QStringList tokenizeWords(const QString &text)
{
    // Chinese and Japanese write without spaces: each ideograph or kana is its own unit, so a
    // caption can break between them (a whole sentence was one «word» and never wrapped).
    static const QRegularExpression re(QStringLiteral(
        R"((\s*(?:[\p{Han}\p{Hiragana}\p{Katakana}]|[^\s\p{Han}\p{Hiragana}\p{Katakana}]+)))"));
    QStringList tokens;
    auto it = re.globalMatch(text);
    static const QRegularExpression thai(QStringLiteral(R"(\p{Thai})"));
    while (it.hasNext()) {
        const QString token = it.next().captured(1);
        if (token.contains(thai)) {
            const QString lead = token.left(token.size() - token.trimmed().size()); // the space before
            QStringList words = splitThaiWords(token.trimmed());
            words.first().prepend(lead);
            tokens.append(words);
        } else {
            tokens.append(token);
        }
    }
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
        QList<TimedWord> words = wordsFromCue(cue);
        // A segment's first word carries no leading space; joined after the previous segment's
        // last word it would glue to it ("noches,que").
        if (!all.isEmpty() && !words.isEmpty() && !words.first().word.isEmpty()
            && !words.first().word.front().isSpace())
            words.first().word.prepend(QLatin1Char(' '));
        all += words;
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

void shiftSubtitleCue(SubtitleCue &cue, TimeUs delta)
{
    cue.startUs += delta;
    cue.endUs += delta;
    for (TimeUs &end : cue.wordEndsUs)
        end += delta;
}

int activeWordIndexAt(const SubtitleCue &cue, TimeUs localUs)
{
    if (cue.endUs <= cue.startUs || localUs < cue.startUs)
        return -1;
    const QList<TimedWord> words = wordsFromCue(cue);
    // A word added after alignment at the end (the caption's emoji) still lets the timings drive
    // the words before it; fewer words than timings (one removed, or the text rewritten) does not.
    bool timed = !cue.wordEndsUs.isEmpty() && cue.wordEndsUs.size() <= words.size()
                 && words.size() - cue.wordEndsUs.size() <= 1;
    for (int i = 0; timed && i < cue.wordEndsUs.size(); ++i) {
        const TimeUs end = cue.wordEndsUs.at(i);
        timed = end > cue.startUs && end <= cue.endUs + kUsPerSecond / 10
                && (i == 0 || end >= cue.wordEndsUs.at(i - 1));
    }
    if (!timed)
        return activeWordIndexAt(cue.text, cue.startUs, cue.endUs, localUs);
    for (int i = 0; i < cue.wordEndsUs.size(); ++i) {
        if (localUs < cue.wordEndsUs.at(i))
            return i;
    }
    return words.size() - 1;
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

namespace {
// Letters a word takes on a line: an ideograph or kana is as wide as two Latin letters.
int displayWidth(const QString &word)
{
    int width = 0;
    for (const QChar c : word) {
        if (c.category() == QChar::Mark_NonSpacing)
            continue; // Thai vowel and tone marks sit on the letter: no width of their own
        const QChar::Script script = c.script();
        width += (script == QChar::Script_Han || script == QChar::Script_Hiragana
                  || script == QChar::Script_Katakana) ? 2 : 1;
    }
    return width;
}
} // namespace

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
        cue.text = text.trimmed(); // the line breaks are the ones packing put in
        for (const TimedWord &w : subtitle) {
            if (!w.word.trimmed().isEmpty())
                cue.wordEndsUs.append(w.endUs);
        }
        if (!cue.text.isEmpty() && cue.endUs > cue.startUs)
            packed.append(cue);
        subtitle.clear();
        lineLen = 0;
        lineCount = 1;
        wordCount = 0;
    };

    for (TimedWord timing : words) {
        // A break inside a word's text is not ours: only the packing below splits lines (a second
        // line used to be flattened back into one, so two-line captions never came out).
        timing.word.replace(QLatin1Char('\n'), QLatin1Char(' '));
        const bool longPause = timing.startUs - lastStart > kLongPauseUs;
        const bool hasRoom = lineLen + displayWidth(timing.word) <= maxLineWidth;
        const bool wordCapHit = maxWordsPerCue > 0 && wordCount >= maxWordsPerCue;

        if (lineLen > 0 && hasRoom && !longPause && !wordCapHit) {
            lineLen += displayWidth(timing.word);
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
            lineLen = displayWidth(timing.word.trimmed());
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

namespace {
QString wordKey(const QString &word)
{
    QString key;
    for (const QChar c : word) {
        if (c.isLetterOrNumber())
            key.append(c.toLower());
    }
    return key;
}
} // namespace

QList<TimeUs> realignWordEnds(const QString &oldText, const QList<TimeUs> &oldEnds, const QString &newText)
{
    const QStringList a = oldText.split(QLatin1Char(' '), Qt::SkipEmptyParts);
    const QStringList b = newText.split(QLatin1Char(' '), Qt::SkipEmptyParts);
    if (oldEnds.size() != a.size() || a.isEmpty() || b.isEmpty())
        return {};
    // Longest common run of words (by letters, case and punctuation aside): a kept word keeps its
    // timing; a new word takes the end of the old words it replaced, or of the word before it.
    const int n = a.size();
    const int m = b.size();
    QList<QList<int>> lcs(n + 1, QList<int>(m + 1, 0));
    for (int i = n - 1; i >= 0; --i) {
        for (int j = m - 1; j >= 0; --j)
            lcs[i][j] = wordKey(a.at(i)) == wordKey(b.at(j)) ? lcs[i + 1][j + 1] + 1 : qMax(lcs[i + 1][j], lcs[i][j + 1]);
    }
    QList<TimeUs> out;
    int i = 0;
    int j = 0;
    TimeUs last = -1; // the end of the last old word passed
    while (j < m) {
        if (i < n && wordKey(a.at(i)) == wordKey(b.at(j))) {
            last = oldEnds.at(i);
            out.append(last);
            ++i;
            ++j;
        } else if (i < n && lcs[i + 1][j + 1] == lcs[i][j]) {
            // One word for another (a name fixed): it takes the replaced word's timing.
            last = oldEnds.at(i);
            out.append(last);
            ++i;
            ++j;
        } else if (i < n && lcs[i + 1][j] >= lcs[i][j + 1]) {
            last = oldEnds.at(i); // an old word gone (or being replaced)
            ++i;
        } else {
            // A new word: it ends where the old words it replaced did, else with the next old one.
            out.append(last >= 0 ? last : oldEnds.at(qMin(i, n - 1)));
            ++j;
        }
    }
    // Never going back in time.
    for (int k = 1; k < out.size(); ++k)
        out[k] = qMax(out.at(k), out.at(k - 1));
    return out;
}

QString cleanSubtitleText(const QString &text, bool capitalize)
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
    for (int i = 0; capitalize && i < out.size(); ++i) {
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
        // A caption only starts with a capital where a sentence starts: the first one, or after
        // one that ended a sentence. "...que el Rey de Reyes los / bendiga grandemente" stays
        // lower-case.
        bool sentenceStart = out.isEmpty();
        if (!sentenceStart) {
            const QString previous = out.last().text.trimmed();
            const QChar last = previous.isEmpty() ? QChar() : previous.back();
            sentenceStart = last == QLatin1Char('.') || last == QLatin1Char('?') || last == QLatin1Char('!')
                            || last == QChar(0x2026);
        }
        // The aligned word timings lose the hesitations' too, so the karaoke keeps following the
        // voice (left as they were, there were more timings than words and it fell back to an even
        // spread).
        const QStringList words = cue.text.split(QLatin1Char(' '), Qt::SkipEmptyParts);
        QList<TimeUs> ends;
        if (cue.wordEndsUs.size() == words.size()) {
            for (int i = 0; i < words.size(); ++i) {
                if (!isHesitation(words.at(i)))
                    ends.append(cue.wordEndsUs.at(i));
            }
        }
        const QString before = cue.text;
        cue.text = cleanSubtitleText(cue.text, sentenceStart);
        if (!ends.isEmpty() && cue.text.split(QLatin1Char(' '), Qt::SkipEmptyParts).size() == ends.size())
            cue.wordEndsUs = ends;
        else if (cue.text != before)
            cue.wordEndsUs = realignWordEnds(before, cue.wordEndsUs, cue.text);
        if (!cue.text.isEmpty())
            out.append(cue);
    }
    return out;
}

QString maskProfanity(const QString &text)
{
    // Stems: a word that starts with one is masked ("put" also takes "puta", "putos").
    static const QStringList kStems = {
        QStringLiteral("mierd"), QStringLiteral("put"), QStringLiteral("puñet"), QStringLiteral("cabron"),
        QStringLiteral("carajo"), QStringLiteral("coño"), QStringLiteral("joder"), QStringLiteral("jodid"),
        QStringLiteral("pendej"), QStringLiteral("verga"), QStringLiteral("chinga"), QStringLiteral("cojon"),
        QStringLiteral("gilipoll"), QStringLiteral("culer"), QStringLiteral("huevon"),
        QStringLiteral("marica"), QStringLiteral("malparid"), QStringLiteral("hijueput"), QStringLiteral("csm"),
        QStringLiteral("fuck"), QStringLiteral("shit"), QStringLiteral("bitch"), QStringLiteral("asshole"),
        QStringLiteral("bastard"), QStringLiteral("dick"), QStringLiteral("pussy"), QStringLiteral("cunt"),
        QStringLiteral("motherfuck"), QStringLiteral("bullshit"), QStringLiteral("damn"),
    };
    // Words that start like one but are not swearing.
    static const QStringList kInnocent = {
        QStringLiteral("put"), QStringLiteral("puts"), QStringLiteral("putt"), QStringLiteral("putting"), QStringLiteral("output"),
        QStringLiteral("dickens"), QStringLiteral("putin"), QStringLiteral("damnation"),
    };
    QString out;
    QString word;
    auto flush = [&]() {
        if (word.isEmpty())
            return;
        // Matched as written («coño») and without accents («cabrón» → «cabron»).
        const QString lower = word.toLower();
        const QString key = word.normalized(QString::NormalizationForm_D)
                                .remove(QRegularExpression(QStringLiteral("[\\x{0300}-\\x{036f}]")))
                                .toLower();
        bool bad = false;
        if (!kInnocent.contains(key)) {
            for (const QString &stem : kStems) {
                if (lower.startsWith(stem) || key.startsWith(stem)) {
                    bad = true;
                    break;
                }
            }
        }
        out += bad ? word.left(1) + QString(word.size() - 1, QLatin1Char('*')) : word;
        word.clear();
    };
    for (const QChar c : text) {
        if (c.isLetter()) {
            word += c;
        } else {
            flush();
            out += c;
        }
    }
    flush();
    return out;
}

QString captionWithEmoji(const QString &text)
{
    // (stem, emoji): a stem matches the start of an accent-free, lower-case word; a stem ending
    // in a space must be the whole word ("fe ", "sol "). Earlier rows win.
    static const QList<QPair<QString, QString>> kStems = {
        {QStringLiteral("dios"), QStringLiteral("🙏")},
        {QStringLiteral("senor"), QStringLiteral("🙏")},
        {QStringLiteral("jesus"), QStringLiteral("✝️")},
        {QStringLiteral("cristo"), QStringLiteral("✝️")},
        {QStringLiteral("cruz"), QStringLiteral("✝️")},
        {QStringLiteral("biblia"), QStringLiteral("📖")},
        {QStringLiteral("palabra de dios"), QStringLiteral("📖")},
        {QStringLiteral("orac"), QStringLiteral("🙏")},
        {QStringLiteral("orar"), QStringLiteral("🙏")},
        {QStringLiteral("oremos"), QStringLiteral("🙏")},
        {QStringLiteral("bendic"), QStringLiteral("🙌")},
        {QStringLiteral("bendig"), QStringLiteral("🙌")},
        {QStringLiteral("aleluya"), QStringLiteral("🙌")},
        {QStringLiteral("amen"), QStringLiteral("🙏")},
        {QStringLiteral("iglesia"), QStringLiteral("⛪")},
        {QStringLiteral("espiritu"), QStringLiteral("🕊️")},
        {QStringLiteral("paz"), QStringLiteral("🕊️")},
        {QStringLiteral("fe "), QStringLiteral("✨")},
        {QStringLiteral("milagro"), QStringLiteral("✨")},
        {QStringLiteral("cielo"), QStringLiteral("☁️")},
        {QStringLiteral("gloria"), QStringLiteral("✨")},
        {QStringLiteral("gracias"), QStringLiteral("🙏")},
        {QStringLiteral("amor"), QStringLiteral("❤️")},
        {QStringLiteral("corazon"), QStringLiteral("❤️")},
        {QStringLiteral("te quiero"), QStringLiteral("❤️")},
        {QStringLiteral("familia"), QStringLiteral("👨‍👩‍👧")},
        {QStringLiteral("hijo"), QStringLiteral("👶")},
        {QStringLiteral("bebe"), QStringLiteral("👶")},
        {QStringLiteral("mama"), QStringLiteral("👩")},
        {QStringLiteral("papa"), QStringLiteral("👨")},
        {QStringLiteral("fuego"), QStringLiteral("🔥")},
        {QStringLiteral("increible"), QStringLiteral("🤯")},
        {QStringLiteral("wow"), QStringLiteral("😮")},
        {QStringLiteral("sorpresa"), QStringLiteral("😮")},
        {QStringLiteral("risa"), QStringLiteral("😂")},
        {QStringLiteral("jaja"), QStringLiteral("😂")},
        {QStringLiteral("chiste"), QStringLiteral("😂")},
        {QStringLiteral("feliz"), QStringLiteral("😊")},
        {QStringLiteral("alegr"), QStringLiteral("😄")},
        {QStringLiteral("triste"), QStringLiteral("😢")},
        {QStringLiteral("llor"), QStringLiteral("😢")},
        {QStringLiteral("miedo"), QStringLiteral("😱")},
        {QStringLiteral("dinero"), QStringLiteral("💰")},
        {QStringLiteral("plata "), QStringLiteral("💰")},
        {QStringLiteral("precio"), QStringLiteral("💲")},
        {QStringLiteral("oferta"), QStringLiteral("🏷️")},
        {QStringLiteral("gratis"), QStringLiteral("🎁")},
        {QStringLiteral("regalo"), QStringLiteral("🎁")},
        {QStringLiteral("fiesta"), QStringLiteral("🎉")},
        {QStringLiteral("celebr"), QStringLiteral("🎉")},
        {QStringLiteral("cumpleanos"), QStringLiteral("🎂")},
        {QStringLiteral("musica"), QStringLiteral("🎵")},
        {QStringLiteral("cancion"), QStringLiteral("🎶")},
        {QStringLiteral("canta"), QStringLiteral("🎤")},
        {QStringLiteral("idea"), QStringLiteral("💡")},
        {QStringLiteral("tiempo"), QStringLiteral("⏰")},
        {QStringLiteral("hora"), QStringLiteral("⏰")},
        {QStringLiteral("mundo"), QStringLiteral("🌎")},
        {QStringLiteral("sol "), QStringLiteral("☀️")},
        {QStringLiteral("agua"), QStringLiteral("💧")},
        {QStringLiteral("luz"), QStringLiteral("✨")},
        {QStringLiteral("exito"), QStringLiteral("🏆")},
        {QStringLiteral("ganar"), QStringLiteral("🏆")}, {QStringLiteral("ganamos"), QStringLiteral("🏆")},
        {QStringLiteral("trabajo"), QStringLiteral("💼")},
        {QStringLiteral("fuerza"), QStringLiteral("💪")},
        {QStringLiteral("fuerte"), QStringLiteral("💪")},
        {QStringLiteral("comida"), QStringLiteral("🍽️")},
        {QStringLiteral("casa"), QStringLiteral("🏠")},
        {QStringLiteral("viaje"), QStringLiteral("✈️")},
        {QStringLiteral("telefono"), QStringLiteral("📱")},
        {QStringLiteral("celular"), QStringLiteral("📱")},
        {QStringLiteral("video"), QStringLiteral("🎬")},
        {QStringLiteral("foto"), QStringLiteral("📸")},
        {QStringLiteral("mira"), QStringLiteral("👀")},
        {QStringLiteral("atencion"), QStringLiteral("👀")},
        {QStringLiteral("escucha"), QStringLiteral("👂")},
        {QStringLiteral("importante"), QStringLiteral("⚠️")},
        {QStringLiteral("cuidado"), QStringLiteral("⚠️")},
        {QStringLiteral("nuevo"), QStringLiteral("✨")},
        {QStringLiteral("primero"), QStringLiteral("🥇")},
        {QStringLiteral("rapido"), QStringLiteral("⚡")},
        {QStringLiteral("estudi"), QStringLiteral("📚")},
        {QStringLiteral("libro"), QStringLiteral("📚")},
        {QStringLiteral("escuela"), QStringLiteral("🏫")},
        {QStringLiteral("god"), QStringLiteral("🙏")},
        {QStringLiteral("pray"), QStringLiteral("🙏")},
        {QStringLiteral("bless"), QStringLiteral("🙌")},
        {QStringLiteral("church"), QStringLiteral("⛪")},
        {QStringLiteral("love"), QStringLiteral("❤️")},
        {QStringLiteral("heart"), QStringLiteral("❤️")},
        {QStringLiteral("fire"), QStringLiteral("🔥")},
        {QStringLiteral("money"), QStringLiteral("💰")},
        {QStringLiteral("party"), QStringLiteral("🎉")},
        {QStringLiteral("music"), QStringLiteral("🎵")},
        {QStringLiteral("happy"), QStringLiteral("😊")},
        {QStringLiteral("funny"), QStringLiteral("😂")},
        {QStringLiteral("sad"), QStringLiteral("😢")},
        {QStringLiteral("amazing"), QStringLiteral("🤯")},
        {QStringLiteral("idea"), QStringLiteral("💡")},
        {QStringLiteral("time"), QStringLiteral("⏰")},
        {QStringLiteral("world"), QStringLiteral("🌎")},
        {QStringLiteral("win "), QStringLiteral("🏆")}, {QStringLiteral("winner"), QStringLiteral("🏆")},
        {QStringLiteral("strong"), QStringLiteral("💪")},
        {QStringLiteral("food"), QStringLiteral("🍽️")},
        {QStringLiteral("home"), QStringLiteral("🏠")},
        {QStringLiteral("look"), QStringLiteral("👀")},
        {QStringLiteral("thank"), QStringLiteral("🙏")},
    };
    if (text.trimmed().isEmpty())
        return text;
    // Already has one: a caption the user decorated, or one this already ran on.
    for (const QChar c : text) {
        // Supplementary-plane emoji, or the arrows/symbols/dingbats blocks (☀ ❤ ✝ ✨ ⚡ …).
        if (c.isSurrogate() || (c.unicode() >= 0x2190 && c.unicode() <= 0x2BFF))
            return text;
    }
    QString folded = text.normalized(QString::NormalizationForm_KD);
    QString plain;
    for (const QChar c : std::as_const(folded)) {
        if (c.category() == QChar::Mark_NonSpacing)
            continue;
        plain.append(c.isLetterOrNumber() ? c.toLower() : QLatin1Char(' '));
    }
    const QString padded = QLatin1Char(' ') + plain.simplified() + QLatin1Char(' ');
    for (const auto &[stem, emoji] : kStems) {
        if (padded.contains(QLatin1Char(' ') + stem))
            return text.trimmed() + QLatin1Char(' ') + emoji;
    }
    return text;
}

QString highlightCaptionKeyword(const QString &text)
{
    // Words that carry no meaning of their own, accent-free and lower-case.
    static const QSet<QString> kFiller = [] {
        QSet<QString> set;
        for (const char *w : {
                 // es
                 "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al", "a", "en", "y", "o",
                 "que", "con", "por", "para", "como", "pero", "mas", "muy", "ya", "se", "su", "sus", "mi", "mis",
                 "tu", "tus", "lo", "le", "les", "me", "te", "nos", "es", "son", "fue", "era", "esta", "estan",
                 "este", "esto", "estos", "estas", "ese", "esa", "eso", "esos", "esas", "aqui", "alli", "asi",
                 "tambien", "porque", "cuando", "donde", "hay", "ser", "estar", "tener", "tiene", "tengo",
                 "hacer", "hace", "vamos", "voy", "va", "van", "hoy", "ahora", "entonces", "despues", "antes",
                 "todo", "todos", "toda", "todas", "algo", "nada", "cada", "otro", "otra", "otros", "sobre",
                 "entre", "hasta", "desde", "sin", "solo", "bien", "mucho", "mucha", "muchos", "poco", "puede",
                 "pueden", "hola", "bueno", "pues", "primero", "luego", "listo", "simple", "forma", "manera",
                 // en
                 "the", "an", "and", "or", "of", "to", "in", "on", "at", "for", "with", "is", "are", "was",
                 "were", "be", "been", "it", "this", "that", "these", "those", "you", "we", "they", "he",
                 "she", "his", "her", "our", "your", "their", "my", "me", "us", "them", "so", "but", "if",
                 "then", "just", "very", "really", "here", "there", "what", "when", "where", "which", "who",
                 "how", "about", "from", "into", "have", "has", "had", "will", "would", "can", "could",
                 "going", "gonna", "get", "got", "now", "today", "all", "some", "any", "more", "much", "also",
                 // pt
                 "os", "as", "um", "uma", "do", "da", "dos", "das", "no", "na", "nos", "nas", "em", "e", "com",
                 "nao", "sim", "voce", "isso", "isto", "aquilo", "aqui", "tambem", "muito", "agora",
                 // fr
                 "le", "les", "des", "du", "et", "ou", "est", "sont", "avec", "pour", "dans", "sur", "pas",
                 "vous", "nous", "ils", "elle", "cette", "ces", "tres", "aussi", "mais", "donc",
                 // it
                 "il", "lo", "gli", "di", "che", "con", "per", "non", "sono", "questo", "questa", "molto",
                 "anche", "ma", "perche"}) {
            set.insert(QString::fromLatin1(w));
        }
        return set;
    }();
    if (text.contains(QLatin1Char('*')))
        return text;
    static const QRegularExpression kWord(QStringLiteral(R"(([$€£]?\d[\d.,]*\s?%?|[\p{L}\p{M}][\p{L}\p{M}'’-]*))"));
    struct Candidate { int start; int length; int score; };
    QList<Candidate> words;
    for (auto it = kWord.globalMatch(text); it.hasNext();) {
        const QRegularExpressionMatch m = it.next();
        const QString w = m.captured(0).trimmed();
        int score = 0;
        if (w.front().isDigit() || w.front() == QLatin1Char('$') || w.front() == QChar(0x20AC)
            || w.front() == QChar(0x00A3)) {
            score = 1000; // «100 %», «$5», «3»: the number is what a viewer keeps
        } else {
            QString key;
            for (const QChar c : w.normalized(QString::NormalizationForm_KD)) {
                if (c.category() != QChar::Mark_NonSpacing)
                    key.append(c.toLower());
            }
            if (!kFiller.contains(key) && w.size() >= 4)
                score = int(w.size());
        }
        words.append({int(m.capturedStart(0)), int(w.size()), score});
    }
    if (words.size() < 3)
        return text;
    const Candidate *best = nullptr;
    for (const Candidate &c : std::as_const(words)) {
        if (c.score > 0 && (!best || c.score > best->score))
            best = &c;
    }
    if (!best)
        return text;
    QString out = text;
    out.insert(best->start + best->length, QLatin1Char('*'));
    out.insert(best->start, QLatin1Char('*'));
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
