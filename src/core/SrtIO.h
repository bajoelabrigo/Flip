#pragma once

#include "SubtitleCue.h"

#include <QColor>
#include <QList>
#include <QString>

namespace drift {

// Parse SubRip (.srt) text into clip-local cues. Accepts HH:MM:SS,mmm or HH:MM:SS.mmm
// timestamps, UTF-8 (with or without BOM), and multi-line cue bodies. Invalid or empty
// input returns false and leaves *outCues untouched when provided.
bool parseSrt(const QString &content, QList<SubtitleCue> *outCues, QString *error = nullptr);
bool parseSrtFile(const QString &path, QList<SubtitleCue> *outCues, QString *error = nullptr);

// Serialize cues to SubRip text (UTF-8, comma milliseconds, blank line between cues).
QString writeSrt(const QList<SubtitleCue> &cues);
bool writeSrtFile(const QString &path, const QList<SubtitleCue> &cues, QString *error = nullptr);

// WebVTT (.vtt). Reading skips NOTE/STYLE/REGION blocks and cue identifiers, accepts
// hh:mm:ss.mmm and mm:ss.mmm timestamps, ignores cue settings (align:, line:, ...), strips
// inline tags (<b>, <c.x>, <v Name>, <00:00:01.000>) and decodes character references.
// Writing produces a plain cue list with &, < and > escaped.
bool parseWebVtt(const QString &content, QList<SubtitleCue> *outCues, QString *error = nullptr);
QString writeWebVtt(const QList<SubtitleCue> &cues);

// (Advanced) SubStation Alpha (.ass/.ssa). Reading takes the Dialogue lines of [Events] in the
// field order its Format line declares, drops override blocks {...} and drawings, and maps
// \N / \n to a newline and \h to a space. Writing produces a minimal script with one Default
// style; pass the project's size as the play resolution so players keep the text proportions.
bool parseAss(const QString &content, QList<SubtitleCue> *outCues, QString *error = nullptr);
// The look an .ass file carries (font, size at PlayResY, colours, outline, box): the captions' own
// style instead of a plain Arial. Unset fields keep the plain defaults.
struct AssStyleHint
{
    QString fontFamily;
    double pixelSize = 0.0;
    bool bold = false;
    bool italic = false;
    QColor primary = Qt::white;
    QColor outline = Qt::black;
    double outlineWidth = -1.0; // < 0: the default thin outline
    bool box = false;           // an opaque box behind the text (BorderStyle 3)
    QColor boxColor = QColor(0, 0, 0, 128);
};

QString writeAss(const QList<SubtitleCue> &cues, int playResX = 1920, int playResY = 1080,
                 const AssStyleHint *style = nullptr);

enum class SubtitleFormat { Srt, WebVtt, Ass };

// Format named by the file extension (.srt, .vtt, .ass, .ssa; any case). Anything else is SRT.
SubtitleFormat subtitleFormatForPath(const QString &path);

// Read or write a subtitle file in the format its extension names. A file with an unknown
// extension is read as whichever format its content looks like (SRT when unsure) and written
// as SRT.
bool parseSubtitleFile(const QString &path, QList<SubtitleCue> *outCues, QString *error = nullptr);

bool writeSubtitleFile(const QString &path, const QList<SubtitleCue> &cues, QString *error = nullptr,
                       int playResX = 1920, int playResY = 1080, const AssStyleHint *style = nullptr);

} // namespace drift
