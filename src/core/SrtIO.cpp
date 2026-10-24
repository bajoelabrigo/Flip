#include "SrtIO.h"

#include "Time.h"

#include <QCoreApplication>
#include <QFile>
#include <QFileInfo>
#include <QRegularExpression>
#include <QStringList>

#include <utility>

namespace drift {
namespace {

QString formatSrtTimestamp(TimeUs us)
{
    if (us < 0)
        us = 0;
    const qint64 totalMs = us / kUsPerMs;
    const qint64 hours = totalMs / 3'600'000;
    const qint64 minutes = (totalMs / 60'000) % 60;
    const qint64 seconds = (totalMs / 1'000) % 60;
    const qint64 millis = totalMs % 1'000;
    return QStringLiteral("%1:%2:%3,%4")
        .arg(hours, 2, 10, QLatin1Char('0'))
        .arg(minutes, 2, 10, QLatin1Char('0'))
        .arg(seconds, 2, 10, QLatin1Char('0'))
        .arg(millis, 3, 10, QLatin1Char('0'));
}

bool parseSrtTimestamp(QStringView token, TimeUs *outUs)
{
    static const QRegularExpression re(
        QStringLiteral(R"(^\s*(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})\s*$)"));
    const auto match = re.matchView(token);
    if (!match.hasMatch())
        return false;

    const qint64 hours = match.captured(1).toLongLong();
    const qint64 minutes = match.captured(2).toLongLong();
    const qint64 seconds = match.captured(3).toLongLong();
    QString msStr = match.captured(4);
    while (msStr.size() < 3)
        msStr.append(QLatin1Char('0'));
    if (msStr.size() > 3)
        msStr = msStr.left(3);
    const qint64 millis = msStr.toLongLong();
    if (minutes >= 60 || seconds >= 60 || millis >= 1000)
        return false;

    *outUs = ((hours * 3600 + minutes * 60 + seconds) * kUsPerSecond) + (millis * kUsPerMs);
    return true;
}

QString normalizeNewlines(QString text)
{
    text.replace(QLatin1String("\r\n"), QLatin1String("\n"));
    text.replace(QLatin1Char('\r'), QLatin1Char('\n'));
    if (text.startsWith(QChar(0xFEFF)))
        text.remove(0, 1);
    return text;
}

bool isIndexLine(const QString &line)
{
    if (line.isEmpty())
        return false;
    for (const QChar ch : line) {
        if (!ch.isDigit())
            return false;
    }
    return true;
}

QString decodeSubtitleBytes(const QByteArray &bytes)
{
    // Prefer UTF-8 (with or without BOM); fall back to Latin-1 for older files.
    QString content = QString::fromUtf8(bytes);
    if (content.contains(QChar::ReplacementCharacter))
        content = QString::fromLatin1(bytes);
    return content;
}

bool writeTextFile(const QString &path, const QString &text, QString *error)
{
    QFile file(path);
    if (!file.open(QIODevice::WriteOnly | QIODevice::Truncate)) {
        if (error)
            *error = QCoreApplication::translate("SrtIO", "Could not write subtitle file");
        return false;
    }

    const QByteArray bytes = text.toUtf8();
    if (file.write(bytes) != bytes.size()) {
        if (error)
            *error = QCoreApplication::translate("SrtIO", "Could not write subtitle file");
        return false;
    }
    return true;
}

// Milliseconds from a fraction written with 1-3 digits: ".5" and ".50" are 500 ms, ".05" 50 ms.
qint64 fractionToMillis(QString digits)
{
    while (digits.size() < 3)
        digits.append(QLatin1Char('0'));
    return digits.left(3).toLongLong();
}

// The cues a writer emits: sorted, empty zero-length ones dropped, end after start.
QList<SubtitleCue> cuesForWriting(const QList<SubtitleCue> &cues)
{
    QList<SubtitleCue> sorted = cues;
    sortSubtitleCues(sorted);
    QList<SubtitleCue> out;
    out.reserve(sorted.size());
    for (SubtitleCue cue : sorted) {
        if (cue.endUs <= cue.startUs && cue.text.trimmed().isEmpty())
            continue;
        if (cue.startUs < 0)
            cue.startUs = 0;
        if (cue.endUs <= cue.startUs)
            cue.endUs = cue.startUs + kUsPerMs;
        out.append(cue);
    }
    return out;
}

bool finishParsedCues(QList<SubtitleCue> &cues, QList<SubtitleCue> *outCues, QString *error)
{
    if (cues.isEmpty()) {
        if (error)
            *error = QCoreApplication::translate("SrtIO", "No subtitle cues found");
        return false;
    }
    sortSubtitleCues(cues);
    *outCues = std::move(cues);
    return true;
}

// ---- WebVTT ----

bool parseVttTimestamp(QStringView token, TimeUs *outUs)
{
    static const QRegularExpression re(
        QStringLiteral(R"(^(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{1,3})$)"));
    const auto match = re.matchView(token);
    if (!match.hasMatch())
        return false;

    const qint64 hours = match.captured(1).isEmpty() ? 0 : match.captured(1).toLongLong();
    const qint64 minutes = match.captured(2).toLongLong();
    const qint64 seconds = match.captured(3).toLongLong();
    const qint64 millis = fractionToMillis(match.captured(4));
    if (minutes >= 60 || seconds >= 60)
        return false;

    *outUs = ((hours * 3600 + minutes * 60 + seconds) * kUsPerSecond) + (millis * kUsPerMs);
    return true;
}

QString formatVttTimestamp(TimeUs us)
{
    // SRT's layout with a dot before the milliseconds.
    QString stamp = formatSrtTimestamp(us);
    stamp[stamp.size() - 4] = QLatin1Char('.');
    return stamp;
}

QString decodeCharacterReferences(const QString &text)
{
    static const QRegularExpression re(QStringLiteral(R"(&(#[xX][0-9a-fA-F]+|#\d+|[a-zA-Z]+);)"));
    QString out;
    out.reserve(text.size());
    qsizetype last = 0;
    auto it = re.globalMatch(text);
    while (it.hasNext()) {
        const auto match = it.next();
        out += QStringView(text).mid(last, match.capturedStart() - last);
        last = match.capturedEnd();

        const QString name = match.captured(1);
        char32_t code = 0;
        if (name.startsWith(QLatin1String("#x"), Qt::CaseInsensitive))
            code = char32_t(name.mid(2).toUInt(nullptr, 16));
        else if (name.startsWith(QLatin1Char('#')))
            code = char32_t(name.mid(1).toUInt());
        else if (name == QLatin1String("amp"))
            code = '&';
        else if (name == QLatin1String("lt"))
            code = '<';
        else if (name == QLatin1String("gt"))
            code = '>';
        else if (name == QLatin1String("quot"))
            code = '"';
        else if (name == QLatin1String("apos"))
            code = '\'';
        else if (name == QLatin1String("nbsp"))
            code = 0xA0;
        else if (name == QLatin1String("lrm"))
            code = 0x200E;
        else if (name == QLatin1String("rlm"))
            code = 0x200F;

        if (code == 0 || code > 0x10FFFF)
            out += match.captured(0);
        else
            out += QString::fromUcs4(&code, 1);
    }
    out += QStringView(text).mid(last);
    return out;
}

QString vttCueText(const QStringList &lines)
{
    static const QRegularExpression tagRe(QStringLiteral(R"(<[^>]*>)"));
    QStringList body;
    for (const QString &line : lines) {
        QString clean = line;
        clean.remove(tagRe);
        body.append(decodeCharacterReferences(clean));
    }
    while (!body.isEmpty() && body.first().trimmed().isEmpty())
        body.removeFirst();
    while (!body.isEmpty() && body.last().trimmed().isEmpty())
        body.removeLast();
    return body.join(QLatin1Char('\n'));
}

bool startsWithKeyword(const QString &line, QLatin1String keyword)
{
    if (!line.startsWith(keyword))
        return false;
    if (line.size() == keyword.size())
        return true;
    const QChar next = line.at(keyword.size());
    return next == QLatin1Char(' ') || next == QLatin1Char('\t');
}

// ---- (Advanced) SubStation Alpha ----

bool parseAssTimestamp(QStringView token, TimeUs *outUs)
{
    static const QRegularExpression re(
        QStringLiteral(R"(^\s*(\d+):(\d{1,2}):(\d{1,2})[.:](\d{1,3})\s*$)"));
    const auto match = re.matchView(token);
    if (!match.hasMatch())
        return false;

    const qint64 hours = match.captured(1).toLongLong();
    const qint64 minutes = match.captured(2).toLongLong();
    const qint64 seconds = match.captured(3).toLongLong();
    const qint64 millis = fractionToMillis(match.captured(4));
    if (minutes >= 60 || seconds >= 60)
        return false;

    *outUs = ((hours * 3600 + minutes * 60 + seconds) * kUsPerSecond) + (millis * kUsPerMs);
    return true;
}

QString formatAssTimestamp(qint64 centis)
{
    const qint64 hours = centis / 360'000;
    const qint64 minutes = (centis / 6'000) % 60;
    const qint64 seconds = (centis / 100) % 60;
    const qint64 cs = centis % 100;
    return QStringLiteral("%1:%2:%3.%4")
        .arg(hours)
        .arg(minutes, 2, 10, QLatin1Char('0'))
        .arg(seconds, 2, 10, QLatin1Char('0'))
        .arg(cs, 2, 10, QLatin1Char('0'));
}

// Plain text of a Dialogue Text field, or an empty string for a vector drawing.
QString assPlainText(const QString &field)
{
    static const QRegularExpression overrideRe(QStringLiteral(R"((?<!\\)\{[^}]*\})"));
    static const QRegularExpression drawingRe(QStringLiteral(R"(\\p\s*[1-9])"));

    QString text;
    qsizetype last = 0;
    bool drawing = false;
    auto it = overrideRe.globalMatch(field);
    while (it.hasNext()) {
        const auto match = it.next();
        if (!drawing)
            text += QStringView(field).mid(last, match.capturedStart() - last);
        last = match.capturedEnd();
        const QString block = match.captured(0);
        if (drawingRe.match(block).hasMatch())
            drawing = true;
        else if (block.contains(QLatin1String("\\p0")))
            drawing = false;
    }
    if (!drawing)
        text += QStringView(field).mid(last);

    text.replace(QLatin1String("\\N"), QLatin1String("\n"));
    text.replace(QLatin1String("\\n"), QLatin1String("\n"));
    text.replace(QLatin1String("\\h"), QLatin1String(" "));
    text.replace(QLatin1String("\\{"), QLatin1String("{"));
    text.replace(QLatin1String("\\}"), QLatin1String("}"));

    QStringList lines = text.split(QLatin1Char('\n'));
    while (!lines.isEmpty() && lines.first().trimmed().isEmpty())
        lines.removeFirst();
    while (!lines.isEmpty() && lines.last().trimmed().isEmpty())
        lines.removeLast();
    return lines.join(QLatin1Char('\n'));
}

} // namespace

bool parseSrt(const QString &content, QList<SubtitleCue> *outCues, QString *error)
{
    if (!outCues) {
        if (error)
            *error = QCoreApplication::translate("SrtIO", "Missing output");
        return false;
    }

    const QString text = normalizeNewlines(content).trimmed();
    if (text.isEmpty()) {
        if (error)
            *error = QCoreApplication::translate("SrtIO", "Subtitle file is empty");
        return false;
    }

    static const QRegularExpression timingRe(
        QStringLiteral(R"(^\s*(.+?)\s*-->\s*(.+?)\s*(?:X1:.*)?$)"));

    QList<SubtitleCue> cues;
    const QStringList blocks = text.split(QStringLiteral("\n\n"), Qt::SkipEmptyParts);
    for (const QString &rawBlock : blocks) {
        QStringList lines = rawBlock.split(QLatin1Char('\n'));
        while (!lines.isEmpty() && lines.first().trimmed().isEmpty())
            lines.removeFirst();
        while (!lines.isEmpty() && lines.last().trimmed().isEmpty())
            lines.removeLast();
        if (lines.isEmpty())
            continue;

        int timingLine = 0;
        if (isIndexLine(lines.first().trimmed()) && lines.size() >= 2)
            timingLine = 1;

        const auto match = timingRe.match(lines.at(timingLine).trimmed());
        if (!match.hasMatch()) {
            if (error)
                *error = QCoreApplication::translate("SrtIO", "Invalid subtitle timing line");
            return false;
        }

        TimeUs startUs = 0;
        TimeUs endUs = 0;
        if (!parseSrtTimestamp(match.capturedView(1), &startUs)
            || !parseSrtTimestamp(match.capturedView(2), &endUs)) {
            if (error)
                *error = QCoreApplication::translate("SrtIO", "Invalid subtitle timestamp");
            return false;
        }
        if (endUs <= startUs)
            endUs = startUs + kUsPerMs;

        QStringList body;
        for (int i = timingLine + 1; i < lines.size(); ++i)
            body.append(lines.at(i));
        // Keep intentional blank lines inside a cue, but trim the whole body.
        while (!body.isEmpty() && body.first().trimmed().isEmpty())
            body.removeFirst();
        while (!body.isEmpty() && body.last().trimmed().isEmpty())
            body.removeLast();

        SubtitleCue cue;
        cue.startUs = startUs;
        cue.endUs = endUs;
        cue.text = body.join(QLatin1Char('\n'));
        cues.append(cue);
    }

    if (cues.isEmpty()) {
        if (error)
            *error = QCoreApplication::translate("SrtIO", "No subtitle cues found");
        return false;
    }

    sortSubtitleCues(cues);
    *outCues = std::move(cues);
    return true;
}

bool parseSrtFile(const QString &path, QList<SubtitleCue> *outCues, QString *error)
{
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly)) {
        if (error)
            *error = QCoreApplication::translate("SrtIO", "Could not open subtitle file");
        return false;
    }

    return parseSrt(decodeSubtitleBytes(file.readAll()), outCues, error);
}

QString writeSrt(const QList<SubtitleCue> &cues)
{
    QList<SubtitleCue> sorted = cues;
    sortSubtitleCues(sorted);

    QString out;
    int index = 1;
    for (const SubtitleCue &cue : sorted) {
        if (cue.endUs <= cue.startUs && cue.text.trimmed().isEmpty())
            continue;
        TimeUs endUs = cue.endUs;
        if (endUs <= cue.startUs)
            endUs = cue.startUs + kUsPerMs;

        out += QString::number(index++);
        out += QLatin1Char('\n');
        out += formatSrtTimestamp(cue.startUs);
        out += QStringLiteral(" --> ");
        out += formatSrtTimestamp(endUs);
        out += QLatin1Char('\n');
        out += cue.text;
        out += QStringLiteral("\n\n");
    }
    return out;
}

bool writeSrtFile(const QString &path, const QList<SubtitleCue> &cues, QString *error)
{
    QFile file(path);
    if (!file.open(QIODevice::WriteOnly | QIODevice::Truncate)) {
        if (error)
            *error = QCoreApplication::translate("SrtIO", "Could not write subtitle file");
        return false;
    }

    const QByteArray bytes = writeSrt(cues).toUtf8();
    if (file.write(bytes) != bytes.size()) {
        if (error)
            *error = QCoreApplication::translate("SrtIO", "Could not write subtitle file");
        return false;
    }
    return true;
}

bool parseWebVtt(const QString &content, QList<SubtitleCue> *outCues, QString *error)
{
    if (!outCues) {
        if (error)
            *error = QCoreApplication::translate("SrtIO", "Missing output");
        return false;
    }

    const QString text = normalizeNewlines(content);
    if (text.trimmed().isEmpty()) {
        if (error)
            *error = QCoreApplication::translate("SrtIO", "Subtitle file is empty");
        return false;
    }

    // Blocks are runs of lines separated by blank lines.
    QList<QStringList> blocks;
    QStringList current;
    for (const QString &line : text.split(QLatin1Char('\n'))) {
        if (line.trimmed().isEmpty()) {
            if (!current.isEmpty())
                blocks.append(current);
            current.clear();
        } else {
            current.append(line);
        }
    }
    if (!current.isEmpty())
        blocks.append(current);

    static const QRegularExpression timingRe(QStringLiteral(R"(^\s*(\S+?)\s*-->\s*(\S+))"));

    QList<SubtitleCue> cues;
    for (int b = 0; b < blocks.size(); ++b) {
        QStringList lines = blocks.at(b);
        if (b == 0 && lines.first().trimmed().startsWith(QLatin1String("WEBVTT"))) {
            // The header and its metadata lines ("Kind: captions"); a cue glued to it still counts.
            while (!lines.isEmpty() && !lines.first().contains(QLatin1String("-->")))
                lines.removeFirst();
            if (lines.isEmpty())
                continue;
        }

        const QString head = lines.first().trimmed();
        if (!head.contains(QLatin1String("-->"))
            && (startsWithKeyword(head, QLatin1String("NOTE"))
                || startsWithKeyword(head, QLatin1String("STYLE"))
                || startsWithKeyword(head, QLatin1String("REGION"))))
            continue;

        int timingLine = -1;
        if (head.contains(QLatin1String("-->")))
            timingLine = 0;
        else if (lines.size() >= 2 && lines.at(1).contains(QLatin1String("-->")))
            timingLine = 1; // Cue identifier first.
        if (timingLine < 0)
            continue;

        const auto match = timingRe.match(lines.at(timingLine));
        TimeUs startUs = 0;
        TimeUs endUs = 0;
        if (!match.hasMatch() || !parseVttTimestamp(match.capturedView(1), &startUs)
            || !parseVttTimestamp(match.capturedView(2), &endUs)) {
            if (error)
                *error = QCoreApplication::translate("SrtIO", "Invalid subtitle timestamp");
            return false;
        }
        if (endUs <= startUs)
            endUs = startUs + kUsPerMs;

        SubtitleCue cue;
        cue.startUs = startUs;
        cue.endUs = endUs;
        cue.text = vttCueText(lines.mid(timingLine + 1));
        cues.append(cue);
    }

    return finishParsedCues(cues, outCues, error);
}

QString writeWebVtt(const QList<SubtitleCue> &cues)
{
    QString out = QStringLiteral("WEBVTT\n\n");
    for (const SubtitleCue &cue : cuesForWriting(cues)) {
        QString body = cue.text;
        body.replace(QLatin1Char('&'), QLatin1String("&amp;"));
        body.replace(QLatin1Char('<'), QLatin1String("&lt;"));
        body.replace(QLatin1Char('>'), QLatin1String("&gt;"));
        // A blank line ends a WebVTT cue, so empty lines inside the text are dropped.
        QStringList lines;
        for (const QString &line : body.split(QLatin1Char('\n'))) {
            if (!line.trimmed().isEmpty())
                lines.append(line);
        }

        out += formatVttTimestamp(cue.startUs);
        out += QStringLiteral(" --> ");
        out += formatVttTimestamp(cue.endUs);
        out += QLatin1Char('\n');
        if (!lines.isEmpty()) {
            out += lines.join(QLatin1Char('\n'));
            out += QLatin1Char('\n');
        }
        out += QLatin1Char('\n');
    }
    return out;
}

bool parseAss(const QString &content, QList<SubtitleCue> *outCues, QString *error)
{
    if (!outCues) {
        if (error)
            *error = QCoreApplication::translate("SrtIO", "Missing output");
        return false;
    }

    const QString text = normalizeNewlines(content);
    if (text.trimmed().isEmpty()) {
        if (error)
            *error = QCoreApplication::translate("SrtIO", "Subtitle file is empty");
        return false;
    }

    // The ASS default; an SSA file names "Marked" instead of "Layer", which changes nothing here.
    QStringList format = {QStringLiteral("layer"),   QStringLiteral("start"),
                          QStringLiteral("end"),     QStringLiteral("style"),
                          QStringLiteral("name"),    QStringLiteral("marginl"),
                          QStringLiteral("marginr"), QStringLiteral("marginv"),
                          QStringLiteral("effect"),  QStringLiteral("text")};

    QList<SubtitleCue> cues;
    bool inEvents = false;
    for (const QString &rawLine : text.split(QLatin1Char('\n'))) {
        const QString line = rawLine.trimmed();
        if (line.startsWith(QLatin1Char('[')) && line.endsWith(QLatin1Char(']'))) {
            inEvents = line.compare(QLatin1String("[Events]"), Qt::CaseInsensitive) == 0;
            continue;
        }
        if (!inEvents)
            continue;

        const qsizetype colon = line.indexOf(QLatin1Char(':'));
        if (colon <= 0)
            continue;
        const QString key = line.left(colon).trimmed();
        const QString value = line.mid(colon + 1);

        if (key.compare(QLatin1String("Format"), Qt::CaseInsensitive) == 0) {
            format.clear();
            for (const QString &field : value.split(QLatin1Char(',')))
                format.append(field.trimmed().toLower());
            continue;
        }
        if (key.compare(QLatin1String("Dialogue"), Qt::CaseInsensitive) != 0)
            continue;

        const qsizetype startIndex = format.indexOf(QStringLiteral("start"));
        const qsizetype endIndex = format.indexOf(QStringLiteral("end"));
        const qsizetype textIndex = format.indexOf(QStringLiteral("text"));
        if (startIndex < 0 || endIndex < 0 || textIndex < 0)
            continue;

        // The last field takes the rest of the line: the text may contain commas.
        QStringList fields;
        qsizetype from = 0;
        while (fields.size() < format.size() - 1) {
            const qsizetype comma = value.indexOf(QLatin1Char(','), from);
            if (comma < 0)
                break;
            fields.append(value.mid(from, comma - from));
            from = comma + 1;
        }
        fields.append(value.mid(from));
        if (fields.size() < format.size())
            continue;

        TimeUs startUs = 0;
        TimeUs endUs = 0;
        if (!parseAssTimestamp(fields.at(startIndex), &startUs)
            || !parseAssTimestamp(fields.at(endIndex), &endUs)) {
            if (error)
                *error = QCoreApplication::translate("SrtIO", "Invalid subtitle timestamp");
            return false;
        }
        if (endUs <= startUs)
            endUs = startUs + kUsPerMs;

        const QString body = assPlainText(fields.at(textIndex)).trimmed();
        if (body.isEmpty())
            continue;

        SubtitleCue cue;
        cue.startUs = startUs;
        cue.endUs = endUs;
        cue.text = body;
        cues.append(cue);
    }

    return finishParsedCues(cues, outCues, error);
}

QString writeAss(const QList<SubtitleCue> &cues, int playResX, int playResY)
{
    if (playResX <= 0 || playResY <= 0) {
        playResX = 1920;
        playResY = 1080;
    }
    const int shortSide = qMin(playResX, playResY);
    const int fontSize = qMax(8, qRound(shortSide * 0.06));
    const int marginH = qMax(10, qRound(playResX * 0.04));
    const int marginV = qMax(10, qRound(playResY * 0.06));

    QString out;
    out += QStringLiteral("[Script Info]\n"
                          "; Flip Studio\n"
                          "ScriptType: v4.00+\n"
                          "WrapStyle: 0\n"
                          "ScaledBorderAndShadow: yes\n");
    out += QStringLiteral("PlayResX: %1\nPlayResY: %2\n\n").arg(playResX).arg(playResY);
    out += QStringLiteral(
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n");
    out += QStringLiteral("Style: Default,Arial,%1,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,"
                          "0,0,0,0,100,100,0,0,1,%2,0,2,%3,%3,%4,1\n\n")
               .arg(fontSize)
               .arg(qMax(1, qRound(fontSize / 20.0)))
               .arg(marginH)
               .arg(marginV);
    out += QStringLiteral("[Events]\n"
                          "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, "
                          "Effect, Text\n");

    for (const SubtitleCue &cue : cuesForWriting(cues)) {
        const qint64 startCs = cue.startUs / (kUsPerMs * 10);
        qint64 endCs = cue.endUs / (kUsPerMs * 10);
        if (endCs <= startCs)
            endCs = startCs + 1;

        QString body = cue.text;
        body.replace(QLatin1Char('{'), QLatin1String("\\{"));
        body.replace(QLatin1Char('}'), QLatin1String("\\}"));
        body.replace(QLatin1Char('\n'), QLatin1String("\\N"));

        out += QStringLiteral("Dialogue: 0,");
        out += formatAssTimestamp(startCs);
        out += QLatin1Char(',');
        out += formatAssTimestamp(endCs);
        out += QStringLiteral(",Default,,0,0,0,,");
        out += body;
        out += QLatin1Char('\n');
    }
    return out;
}

SubtitleFormat subtitleFormatForPath(const QString &path)
{
    const QString suffix = QFileInfo(path).suffix().toLower();
    if (suffix == QLatin1String("vtt"))
        return SubtitleFormat::WebVtt;
    if (suffix == QLatin1String("ass") || suffix == QLatin1String("ssa"))
        return SubtitleFormat::Ass;
    return SubtitleFormat::Srt;
}

bool parseSubtitleFile(const QString &path, QList<SubtitleCue> *outCues, QString *error)
{
    const QString suffix = QFileInfo(path).suffix().toLower();
    if (suffix == QLatin1String("srt"))
        return parseSrtFile(path, outCues, error);

    QFile file(path);
    if (!file.open(QIODevice::ReadOnly)) {
        if (error)
            *error = QCoreApplication::translate("SrtIO", "Could not open subtitle file");
        return false;
    }
    const QString content = decodeSubtitleBytes(file.readAll());

    SubtitleFormat format = subtitleFormatForPath(path);
    if (suffix != QLatin1String("vtt") && suffix != QLatin1String("ass")
        && suffix != QLatin1String("ssa")) {
        // Unknown extension: go by what the text looks like.
        const QString head = normalizeNewlines(content).trimmed();
        if (head.startsWith(QLatin1String("WEBVTT")))
            format = SubtitleFormat::WebVtt;
        else if (head.startsWith(QLatin1String("[Script Info]"), Qt::CaseInsensitive)
                 || head.contains(QLatin1String("[Events]"), Qt::CaseInsensitive))
            format = SubtitleFormat::Ass;
    }

    switch (format) {
    case SubtitleFormat::WebVtt:
        return parseWebVtt(content, outCues, error);
    case SubtitleFormat::Ass:
        return parseAss(content, outCues, error);
    case SubtitleFormat::Srt:
        break;
    }
    return parseSrt(content, outCues, error);
}

bool writeSubtitleFile(const QString &path, const QList<SubtitleCue> &cues, QString *error,
                       int playResX, int playResY)
{
    switch (subtitleFormatForPath(path)) {
    case SubtitleFormat::WebVtt:
        return writeTextFile(path, writeWebVtt(cues), error);
    case SubtitleFormat::Ass:
        return writeTextFile(path, writeAss(cues, playResX, playResY), error);
    case SubtitleFormat::Srt:
        break;
    }
    return writeSrtFile(path, cues, error);
}

} // namespace drift
