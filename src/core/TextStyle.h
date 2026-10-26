#pragma once

#include "Keyframe.h"
#include "TextAnimator.h"
#include "TextShading.h"
#include "Time.h"

#include <QColor>
#include <QJsonObject>
#include <QList>
#include <QMap>
#include <QPair>
#include <QRectF>
#include <QString>
#include <QStringList>

#include <optional>

namespace drift {

enum class TextAlign { Left, Center, Right, Justify }; // Justify: wrapped lines fill the box, the last one starts left
enum class TextVAlign { Top, Middle, Bottom };

// Which words a style pack accents. The positional rules are time-independent, so the layout
// stays cacheable for the whole cue; Karaoke follows the word being spoken and re-lays-out as
// the playhead crosses each word.
enum class WordAccentRule { None, FirstWord, LastWord, EveryOther, EveryNth, LongestWord,
                            RandomStable, Karaoke, Keywords };

QString textAlignToString(TextAlign align);
TextAlign textAlignFromString(const QString &align);

QString textVAlignToString(TextVAlign valign);
TextVAlign textVAlignFromString(const QString &valign);

QString wordAccentRuleToString(WordAccentRule rule);
WordAccentRule wordAccentRuleFromString(const QString &rule);

// Words written between asterisks ("Dios es *fiel*") are accented whatever the rule, and drawn
// without the asterisks. A mark may sit inside opening and closing punctuation: "¡*Amén*!".
bool isMarkedWord(const QString &word);
QString stripWordMark(const QString &word);
bool hasWordMarks(const QString &text);
// The text as it reads, marks removed.
QString textWithoutWordMarks(const QString &text);
// A style whose accent shows something: marked words in a style with no accent look get
// the default accent colour, so a mark never does nothing.
TextStyle withWordMarkDefaults(const TextStyle &style);
// The Keywords rule: words that carry the meaning — numbers, and words of seven letters or more
// that are not common Spanish/English function words.
bool isKeyword(const QString &word);

// Rounded pill drawn behind a word. Used both for "every word" backgrounds and for the
// accent-only highlight a pack paints under its chosen words.
struct TextHighlight
{
    bool enabled = false;
    QColor color = QColor(230, 40, 40);
    double padding = 6.0; // px at pixelSize
    double radius = 4.0;
};

// The per-word override a style pack applies to the words its rule picks out. Everything left
// disabled falls through to the block style, so a pack only states what it changes.
struct WordAccent
{
    WordAccentRule rule = WordAccentRule::None;
    int n = 2;    // EveryNth stride
    int phase = 0; // index of the first accented word

    bool colorEnabled = false;
    QColor color = QColor(255, 214, 64);
    double sizeScale = 1.0; // relative to the block's pixelSize; changes the layout

    bool outlineEnabled = false;
    double outlineWidth = 0.0;
    QColor outlineColor = Qt::black;

    TextHighlight highlight;
};

// Un tramo del texto con su propio color, tamaño y negrita/cursiva (0.23): lo que el editor de
// Texto avanzado llama «las letras seleccionadas». Los desplazamientos son UTF-16 dentro del texto
// del bloque y la lista la deja ordenada, recortada al texto y sin solapes normalizedTextRuns().
struct TextRun
{
    int start = 0;
    int end = 0; // uno más allá del último

    bool colorEnabled = false;
    QColor color = QColor(255, 214, 64);
    bool sizeEnabled = false;
    double sizeScale = 1.0; // relativo al pixelSize del bloque; cambia el trazado
    bool boldEnabled = false;
    bool bold = true;
    bool italicEnabled = false;
    bool italic = true;
    bool underlineEnabled = false; // a line under these letters, in their colour
    bool underline = true;
    bool fontEnabled = false; // another font for these letters
    QString fontFamily;

    // La pila de sombreado entera de estas letras (relleno, trazo, sombra, resplandor, extrusión):
    // así un estilo preestablecido o un look se aplica solo a lo sombreado (0.24).
    bool layersEnabled = false;
    QList<TextShadingLayer> layers;
    // Un fondo detrás de estas letras (uno por línea si el tramo se parte en dos).
    bool boxEnabled = false;
    QColor boxColor = QColor(0, 0, 0, 128);
    double boxPadding = 6.0;   // px al pixelSize del bloque
    double boxRadius = 4.0;
    double boxBorderWidth = 0.0;
    QColor boxBorderColor = QColor(255, 255, 255);
    // Mueve, escala y gira estas letras alrededor del centro de su propia caja. No cambia el
    // trazado del resto (como Filmora): los desplazamientos van en px al pixelSize del bloque.
    bool transformEnabled = false;
    double offsetX = 0.0;
    double offsetY = 0.0;
    double transformScale = 1.0;
    double rotation = 0.0; // grados

    int length() const { return qMax(0, end - start); }
    bool contains(int at) const { return at >= start && at < end; }
};

// Los tramos ordenados, recortados al texto y sin solapes: donde dos se pisan gana el último.
QList<TextRun> normalizedTextRuns(const QList<TextRun> &runs, int textLength);
// Los tramos después de cambiar el texto de `before` a `after`: lo que va detrás de lo escrito o
// borrado se corre con ello, así cada color sigue en sus letras.
QList<TextRun> shiftTextRunsForEdit(const QList<TextRun> &runs, const QString &before, const QString &after);
// What the text bar does to the letters [start, end) (Texto avanzado, like a word processor): the
// fields `patch` turns on (its *Enabled flags) go onto every letter there, and whatever else those
// letters already had (another colour, bold…) stays. Letters outside keep their runs untouched.
QList<TextRun> patchTextRuns(const QList<TextRun> &runs, int textLength, int start, int end, const TextRun &patch);
// El tramo que cubre ese desplazamiento, o nullptr si ninguno.
const TextRun *textRunAt(const QList<TextRun> &runs, int at);

struct TextStyle
{
    // Tramos con estilo propio (0.23). Vacío: todo el bloque usa este estilo.
    QList<TextRun> runs;
    QString packId; // last applied style pack; cleared once the style is hand-edited
    QString fontFamily = QStringLiteral("Inter");
    // At project height. A real number since 0.22.1, so a keyed zoom grows smoothly instead of
    // a pixel at a time, and the preview and the export lay out the same size.
    double pixelSize = 64.0;
    int fontWeight = 700; // 100..900
    bool italic = false;

    // The look: an ordered shading stack, layers[0] drawn first. A fresh style is one solid
    // white fill. `lookId` names the Looks-gallery recipe the stack came from (cleared on a hand
    // edit) and `lookParams` its slider values, so the look stays regenerable.
    QList<TextShadingLayer> layers = {solidFillLayer(Qt::white)};
    QString lookId;
    QMap<QString, VectorSlotValue> lookParams;

    // Bends a single-line block along an arc: -100..100, the rise at the middle as a fraction of
    // two em (positive arches upward). Multi-line blocks ignore it.
    double pathBend = 0.0;
    // Text around a circle (0.22.1): 0 = off; else how much of the circle the line wraps, in percent
    // (100 = all the way round, as a round logo). The bend's sign still says outward (+) or inward.
    double pathCircle = 0.0;

    TextAlign align = TextAlign::Center;
    TextVAlign valign = TextVAlign::Middle;
    bool wordWrap = true;
    double lineHeight = 1.2; // multiple of the font's natural line spacing
    double letterSpacing = 0.0; // px at pixelSize
    double wordSpacing = 0.0;   // px added to every space between words (0.22.1)
    // "none", "upper", "lower" or "title": applied when the text is laid out, so the typed words
    // are kept and switching back restores them.
    QString textCase = QStringLiteral("none");
    // Animated counter (0.17): the first number in the text counts up (or down) from counterFrom to
    // itself over the clip, easing out and landing at 85 % of its length ("$1.000.000", "10K",
    // "100 días"). Separators and decimals keep the text's own format.
    bool counter = false;
    double counterFrom = 0.0;
    // Seconds the count takes from the clip's start (0.18, for templates that time a flash to the
    // landing); 0 keeps the 85 % of the clip.
    double counterSeconds = 0.0;

    bool boxEnabled = false; // filled background behind the whole block
    QColor boxColor = QColor(0, 0, 0, 128);
    double boxPadding = 8.0;
    double boxRadius = 0.0;
    // CapCut's background controls. "block" is one box around everything, "line" one per line.
    // `boxShape` is "rect" or a bubble (textBubbleShapes()). The paddings are unset (< 0) until
    // edited and fall back to boxPadding, so older projects and a keyframed boxPadding still size
    // the box as before.
    QString boxStyle = QStringLiteral("block");
    QString boxShape = QStringLiteral("rect");
    double boxPaddingX = -1.0; // px at pixelSize
    double boxPaddingY = -1.0;
    double boxOffsetX = 0.0;
    double boxOffsetY = 0.0;
    QColor boxBorderColor = QColor(0, 0, 0);
    double boxBorderWidth = 0.0;
    double boxPadX() const { return boxPaddingX >= 0.0 ? boxPaddingX : boxPadding; }
    double boxPadY() const { return boxPaddingY >= 0.0 ? boxPaddingY : boxPadding; }

    TextHighlight wordHighlight; // pill behind every word

    bool underlineEnabled = false;
    QColor underlineColor = QColor(230, 40, 40);
    double underlineWidth = 6.0;
    double underlineOffset = 4.0; // below the baseline
    bool strikeEnabled = false;   // a line through the middle of the letters, in the text's colour (0.22.1)

    WordAccent accent;

    // In / Out / Loop motion (presets or inline animators) evaluated per fragment.
    TextAnimationSet animation;

    // Animated scalars keyed by textKeyframeProperties() names ("pixelSize", "layer.shadow.blur",
    // …), key times relative to the clip's start. A non-empty, enabled track wins over the scalar
    // at render time; the scalar keeps the last static value, so clearing a track returns the
    // property to a constant. Mirrors Mask::keyframes.
    QMap<QString, KeyframeTrack<double>> keyframes;

    bool isAnimated() const; // has enabled keyframe tracks
    bool hasFragmentAnimation() const { return animation.isActive(); }
    // A copy with every keyframed property baked down to its value at clipTimeUs. The renderers
    // only ever see plain numbers; `keyframes` is kept on the copy so callers can still tell an
    // animated style from a static one (cache keys).
    TextStyle resolvedAt(TimeUs clipTimeUs) const;

    // The colour of the text as a user thinks of it: the front-most enabled fill's solid colour
    // (or first gradient stop). Setting it edits that fill.
    QColor primaryColor() const;
    void setPrimaryColor(const QColor &color);
};

// `text` in the style's case ("upper", "lower", "title"; anything else leaves it as typed).
QString applyTextCase(const QString &text, const QString &textCase);
// The animated counter's text at `progress` (0..1 of the clip): the first number in `text` replaced
// by its value counting from `from`, in the text's own format, reaching it at `land` (0..1) of the
// clip. A number written with leading zeros ("05:00") keeps its width. `text` unchanged if it has none.
QString counterTextAt(const QString &text, double from, double progress, double land = 0.85);
// The background shapes a text box can take besides "rect", in gallery order.
QStringList textBubbleShapes();

// Convenience accessors the layout and painters use so nobody spells out layer lookups.
QColor textFillColor(const TextStyle &style, bool accent);
double textStrokeWidth(const TextStyle &style, bool accent);
QColor textStrokeColor(const TextStyle &style, bool accent);
// Sets the front-most fill to a solid colour (importers).
void setSolidFill(TextStyle &style, const QColor &color);

// The scalars a text style can animate, in inspector order: the flat ones then one group per
// layer. Keys are canonical ("layer.<id>.<field>").
QStringList textKeyframeProperties(const TextStyle &style);
// Canonical spelling of a keyframe key: the key itself when valid on this style, the layer path
// for a legacy alias ("outlineWidth" → "layer.stroke.width"), or empty when unknown.
QString textKeyframeCanonicalKey(const QString &key, const TextStyle &style);
// Human label for a key ("Shadow · Blur").
QString textKeyframeLabel(const QString &key, const TextStyle &style);
// The scalar a keyframe property reads/writes on the style; colour channels are 0..1. False for
// an unknown key. Legacy aliases are accepted.
bool textStyleScalar(const TextStyle &style, const QString &key, double *out);
bool setTextStyleScalar(TextStyle &style, const QString &key, double value);
// Grows or shrinks the whole look by `factor`, not only the letters: the size, the spacing, every
// layer's stroke width, blur, spread and offset, the box and pill paddings, radii and borders, the
// underline, and the keyframes of all of those. A template put on another canvas and a text
// scaled from its corner keep their proportions (auditoria D7, D14).
void scaleTextStyle(TextStyle &style, double factor);

// One text of a combined template: its look, its words, where it sits (fractions of the canvas)
// and how long after the template's start it comes in.
struct TextTemplatePart
{
    TextStyle style;
    QString text;
    QRectF rect;
    double delaySeconds = 0.0;
};

struct TextPreset
{
    QString id;
    QString label;
    TextStyle style;
    // Short phrase shown on picker thumbnails — chosen to demo the pack's look
    // (accents, wrap, weight) rather than a meaningless filler line.
    QString sampleText;
    // Add-on packs only: the pack category it is listed under.
    QString category;
    // Add-on packs only: a combined template (a title with its subtitle, a name with its role…)
    // adds one text clip per part, placed and timed together. Empty for a plain style.
    QList<TextTemplatePart> parts;
    // User library only: the Stock item it was installed from ("tend-a-limpio-blanco"), so a
    // second download refreshes it instead of adding a copy, and Titles › Trending finds it.
    QString stockId;
};

// Built-in style packs only. User-saved presets live in TextPresetStore; textPresetForId()
// resolves both, which is what keeps the preview provider and applyTextPreset kind-agnostic.
const QList<TextPreset> &textPresets();
// By value: a user preset lives in a mutable library that the GUI thread edits while the
// preview provider resolves ids on the image-loading thread.
std::optional<TextPreset> textPresetForId(const QString &id);
std::optional<TextStyle> textStyleForPresetId(const QString &id);
// `preset`'s look put on a text that already has `current`: the template brings the look, and
// what the user did to this text stays (Jorge, 2026-10-24: a template used to wipe the motion).
// Kept from `current`: each In / Out / Loop slot the user set (the template's own fills the empty
// ones), the counter, a case the template does not set, and every keyframe track that still names
// a property of the new style. `dropped`, when given, gets the keyframe tracks that could not
// stay (a layer the template does not have).
TextStyle textStyleWithPresetLook(const TextStyle &current, const TextStyle &preset,
                                  QStringList *dropped = nullptr);

// Styles from installed text-style add-ons, ids "pack:<pack>/<style>". The engine's catalog
// (TextStyleCatalog) reads the packs and hands them over here, so textPresetForId resolves them
// like built-in ones. Categories are id + label, in display order.
bool isAddonTextPresetId(const QString &id);
void setAddonTextPresets(const QList<TextPreset> &presets, const QList<QPair<QString, QString>> &categories);
QList<TextPreset> addonTextPresets();
QList<QPair<QString, QString>> addonTextPresetCategories();

// Shared with the project file format, which is why these live here rather than in Project.cpp:
// the user preset store writes the same style objects and must inherit the same key migrations.
QJsonObject textHighlightToJson(const TextHighlight &h);
TextHighlight textHighlightFromJson(const QJsonObject &o, const TextHighlight &fallback);
QJsonObject wordAccentToJson(const WordAccent &a);
WordAccent wordAccentFromJson(const QJsonObject &o);
QJsonObject textStyleToJson(const TextStyle &s);
// Reads both the v7 layered form and the flat v6 form (migrated into layers and preset slots).
TextStyle textStyleFromJson(const QJsonObject &o);

} // namespace drift
