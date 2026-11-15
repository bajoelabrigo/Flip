#include "SceneTemplateTools.h"

#include "core/TextShading.h"

#include <QHash>
#include <QRegularExpression>
#include <QSet>
#include <QVariant>

#include <algorithm>
#include <cmath>
#include <limits>

namespace drift {

// --- Use with my photos ---------------------------------------------------------------------

QString shapeOfSize(int width, int height)
{
    if (width <= 0 || height <= 0)
        return {};
    const double ratio = double(width) / double(height);
    if (ratio > 1.08)
        return QStringLiteral("horizontal");
    if (ratio < 1.0 / 1.08)
        return QStringLiteral("vertical");
    return QStringLiteral("square");
}

QString majorityShape(int vertical, int horizontal, int square)
{
    if (vertical <= 0 && horizontal <= 0 && square <= 0)
        return {};
    if (vertical >= horizontal && vertical >= square)
        return QStringLiteral("vertical");
    if (square >= horizontal)
        return QStringLiteral("square");
    return QStringLiteral("horizontal");
}

QString photoCountBucket(int count)
{
    if (count <= 0)
        return QStringLiteral("0");
    if (count == 1)
        return QStringLiteral("1");
    if (count <= 3)
        return QStringLiteral("2-3");
    if (count <= 6)
        return QStringLiteral("4-6");
    return QStringLiteral("7+");
}

QString nextPhotoCountBucket(const QString &bucket)
{
    static const QStringList order{QStringLiteral("0"), QStringLiteral("1"), QStringLiteral("2-3"),
                                   QStringLiteral("4-6"), QStringLiteral("7+")};
    const int i = int(order.indexOf(bucket));
    return i >= 0 && i + 1 < order.size() ? order.at(i + 1) : QString();
}

double sceneTemplateMatchScore(int slotCount, const QString &templateShape, int mediaCount, const QString &mediaShape,
                               const QString &projectShape)
{
    if (slotCount <= 0)
        return -1.0;
    double score = 100.0;
    if (slotCount >= mediaCount)
        score -= 10.0 * (slotCount - mediaCount); // empty slotCount left over: the user has to find more
    else
        score -= 16.0 * (mediaCount - slotCount); // pictures left out
    if (!mediaShape.isEmpty() && templateShape == mediaShape)
        score += 30.0;
    // A project that already has a shape keeps it: a template of that shape needs no letterbox.
    if (!projectShape.isEmpty())
        score += templateShape == projectShape ? 25.0 : -15.0;
    return std::max(0.0, score);
}

// --- Fit the cuts to the beat ---------------------------------------------------------------

QList<TimeUs> steadyBeatGrid(TimeUs startUs, TimeUs endUs, double bpm)
{
    QList<TimeUs> beats;
    if (bpm <= 0.0 || endUs <= startUs)
        return beats;
    const double step = 60.0 / bpm * double(kUsPerSecond);
    for (int i = 0;; ++i) {
        const TimeUs at = startUs + TimeUs(std::llround(step * i));
        if (at >= endUs)
            break;
        beats.append(at);
    }
    return beats;
}

QList<TimeUs> snapCutsToBeats(const QList<TimeUs> &cuts, const QList<TimeUs> &beats, TimeUs startUs, TimeUs endUs,
                              TimeUs minGapUs)
{
    QList<TimeUs> out;
    out.reserve(cuts.size());
    TimeUs previous = startUs;
    const int n = int(cuts.size());
    for (int i = 0; i < n; ++i) {
        const TimeUs lo = previous + minGapUs;
        TimeUs hi = endUs - minGapUs * TimeUs(n - i);
        if (hi < lo)
            hi = lo; // too many cuts for the room: keep the order, give up the gap
        const TimeUs target = cuts.at(i);
        TimeUs best = 0;
        TimeUs bestDistance = std::numeric_limits<TimeUs>::max();
        for (const TimeUs beat : beats) {
            if (beat < lo || beat > hi)
                continue;
            const TimeUs distance = beat > target ? beat - target : target - beat;
            if (distance < bestDistance) {
                bestDistance = distance;
                best = beat;
            }
        }
        const TimeUs value = bestDistance != std::numeric_limits<TimeUs>::max() ? best : qBound(lo, target, hi);
        out.append(value);
        previous = value;
    }
    return out;
}

namespace {

bool isSlotMedia(const Clip &clip)
{
    return !clip.placeholderId.isEmpty() && (clip.type == ClipType::Image || clip.type == ClipType::Video);
}

void refitSource(Clip &clip, const std::function<TimeUs(const QString &)> &mediaDurationUs)
{
    if (clip.type != ClipType::Video) {
        clip.srcOut = clip.srcIn + clip.timelineDuration;
        return;
    }
    const TimeUs media = mediaDurationUs ? mediaDurationUs(clip.assetId) : 0;
    if (media <= 0) {
        clip.srcOut = clip.srcIn + clip.sourceSpanUs();
        return;
    }
    // As a slot is filled: at normal speed when the source is long enough, slowed to cover it if not.
    const TimeUs available = qMax<TimeUs>(1, media - clip.srcIn);
    if (available >= clip.timelineDuration) {
        clip.speed = 1.0;
        clip.srcOut = clip.srcIn + clip.timelineDuration;
    } else {
        clip.speed = qMax(0.1, double(available) / double(clip.timelineDuration));
        clip.srcOut = media;
    }
}

} // namespace

int retimeTemplateSlotsToBeats(QList<Track> &tracks, const QList<TimeUs> &beats, TimeUs minDurationUs,
                               const std::function<TimeUs(const QString &assetId)> &mediaDurationUs)
{
    constexpr TimeUs kMaxGapUs = 500'000; // further apart than this, two slotIndices are not one sequence
    int moved = 0;
    QHash<QString, QPair<TimeUs, TimeUs>> movedSpans; // clip id -> new start, duration
    for (Track &track : tracks) {
        QList<int> slotIndices;
        for (int c = 0; c < track.clips.size(); ++c) {
            if (isSlotMedia(track.clips.at(c)))
                slotIndices.append(c);
        }
        std::sort(slotIndices.begin(), slotIndices.end(), [&](int a, int b) {
            return track.clips.at(a).timelineStart < track.clips.at(b).timelineStart;
        });
        int first = 0;
        while (first < slotIndices.size()) {
            int last = first;
            while (last + 1 < slotIndices.size()) {
                const Clip &a = track.clips.at(slotIndices.at(last));
                const Clip &b = track.clips.at(slotIndices.at(last + 1));
                if (b.timelineStart <= a.timelineStart || b.timelineStart - a.timelineEnd() > kMaxGapUs)
                    break;
                ++last;
            }
            if (last > first) {
                QList<TimeUs> cuts;
                for (int k = first + 1; k <= last; ++k)
                    cuts.append(track.clips.at(slotIndices.at(k)).timelineStart);
                const TimeUs start = track.clips.at(slotIndices.at(first)).timelineStart;
                const TimeUs end = track.clips.at(slotIndices.at(last)).timelineEnd();
                const QList<TimeUs> snapped = snapCutsToBeats(cuts, beats, start, end, minDurationUs);
                for (int k = 0; k < cuts.size(); ++k) {
                    const TimeUs delta = snapped.at(k) - cuts.at(k);
                    if (delta == 0)
                        continue;
                    Clip &a = track.clips[slotIndices.at(first + k)];
                    Clip &b = track.clips[slotIndices.at(first + k + 1)];
                    a.timelineDuration += delta;
                    b.timelineStart += delta;
                    b.timelineDuration -= delta;
                    ++moved;
                }
                for (int k = first; k <= last; ++k) {
                    Clip &clip = track.clips[slotIndices.at(k)];
                    refitSource(clip, mediaDurationUs);
                    movedSpans.insert(clip.id, {clip.timelineStart, clip.timelineDuration});
                }
            }
            first = last + 1;
        }
        std::sort(track.clips.begin(), track.clips.end(),
                  [](const Clip &a, const Clip &b) { return a.timelineStart < b.timelineStart; });
    }
    if (moved == 0)
        return 0;
    // A mask or effect lane pinned to a slot covers it as before.
    for (Track &track : tracks) {
        for (Clip &clip : track.clips) {
            if (clip.linkedClipId.isEmpty() || clip.independentRange || !movedSpans.contains(clip.linkedClipId))
                continue;
            const auto span = movedSpans.value(clip.linkedClipId);
            clip.timelineStart = span.first;
            clip.timelineDuration = span.second;
            clip.srcOut = clip.srcIn + span.second;
        }
    }
    return moved;
}

// --- Text form --------------------------------------------------------------------------------

namespace {

// Lower case without accents ("Telefono" with its accent -> "telefono"), so the patterns stay ASCII.
QString folded(const QString &text)
{
    QString out;
    const QString decomposed = text.normalized(QString::NormalizationForm_D).toLower();
    out.reserve(decomposed.size());
    for (const QChar c : decomposed) {
        if (c.category() != QChar::Mark_NonSpacing)
            out.append(c);
    }
    return out;
}

// `text` is folded already; the pattern is ASCII.
bool matches(const QString &text, const char *pattern)
{
    return QRegularExpression(QLatin1String(pattern), QRegularExpression::UseUnicodePropertiesOption)
        .match(text)
        .hasMatch();
}

bool hasCurrencySign(const QString &text)
{
    for (const QChar c : text) {
        if (c.category() == QChar::Symbol_Currency)
            return true;
    }
    return false;
}

// Keywords an author (or the generator) puts in a slot's label, in Spanish and English.
QString kindFromLabel(const QString &rawLabel)
{
    const QString label = folded(rawLabel);
    if (label.isEmpty())
        return {};
    if (matches(label, "telefono|phone|whats ?app|celular|movil"))
        return QStringLiteral("phone");
    if (matches(label, "descuento|discount|oferta|promo"))
        return QStringLiteral("discount");
    if (matches(label, "precio|price|costo|cost"))
        return QStringLiteral("price");
    if (matches(label, "correo|e-?mail"))
        return QStringLiteral("email");
    if (matches(label, "\\bweb\\b|sitio|website|url|enlace|link"))
        return QStringLiteral("web");
    if (matches(label, "usuario|handle|redes|instagram|tiktok|@"))
        return QStringLiteral("handle");
    if (matches(label, "direccion|address|ubicacion|location"))
        return QStringLiteral("address");
    if (matches(label, "horario|\\bhora\\b|\\btime\\b|hours"))
        return QStringLiteral("time");
    if (matches(label, "fecha|\\bdate\\b|\\bdia\\b|\\bday\\b"))
        return QStringLiteral("date");
    if (matches(label, "negocio|business|empresa|marca|brand|tienda|store|company"))
        return QStringLiteral("business");
    if (matches(label, "llamada|cta|call to action|boton|button"))
        return QStringLiteral("cta");
    if (matches(label, "subtitulo|subtitle|tagline|eslogan|slogan"))
        return QStringLiteral("subtitle");
    if (matches(label, "titulo|title|nombre|name|headline"))
        return QStringLiteral("title");
    return {};
}

} // namespace

QString guessTemplateTextKind(const QString &rawText, const QString &label, bool largest)
{
    const QString text = folded(rawText.simplified());
    // The author's label wins when it says something the text itself does not.
    if (folded(label.simplified()) != text) {
        const QString fromLabel = kindFromLabel(label);
        if (!fromLabel.isEmpty())
            return fromLabel;
    }
    if (text.isEmpty())
        return largest ? QStringLiteral("title") : QStringLiteral("text");

    if (matches(text, "[\\w.+-]+@[\\w-]+\\.[\\w.]+"))
        return QStringLiteral("email");
    if (text.startsWith(QLatin1Char('@')))
        return QStringLiteral("handle");
    if (matches(text, "https?://|\\bwww\\.|\\.(com|net|org|pe|mx|co|es|io|app|shop|store)\\b"))
        return QStringLiteral("web");
    if (matches(text, "\\d{1,3}\\s?%|\\b(off|dto|descuento|discount|sale|rebaja)\\b"))
        return QStringLiteral("discount");
    if (hasCurrencySign(text)
        || matches(text, "\\bs/\\.?\\s*\\d|\\b(usd|pen|eur|mxn|cop|soles?|precio|price|desde|from)\\b\\s*\\d"))
        return QStringLiteral("price");

    int digits = 0;
    bool phoneChars = true;
    for (const QChar c : text) {
        if (c.isDigit())
            ++digits;
        else if (!(c.isSpace() || c == QLatin1Char('+') || c == QLatin1Char('-') || c == QLatin1Char('(')
                   || c == QLatin1Char(')') || c == QLatin1Char('.')))
            phoneChars = false;
    }
    if (digits >= 7 && (phoneChars || matches(text, "\\b(tel|telefono|phone|whatsapp|llama|call)\\b")))
        return QStringLiteral("phone");
    if (matches(text, "\\b\\d{1,2}[:h]\\d{2}\\b|\\b\\d{1,2}\\s?(am|pm)\\b"))
        return QStringLiteral("time");
    if (matches(text, "\\b\\d{1,2}[/.-]\\d{1,2}([/.-]\\d{2,4})?\\b|\\b(19|20)\\d{2}\\b"
                      "|\\b(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre"
                      "|diciembre|january|february|march|april|may|june|july|august|september|october|november"
                      "|december|lunes|martes|miercoles|jueves|viernes|sabado|domingo|monday|tuesday"
                      "|wednesday|thursday|friday|saturday|sunday)\\b"))
        return QStringLiteral("date");
    if (matches(text, "\\b(av\\.?|avenida|calle|jr\\.?|jiron|carrera|street|st\\.|ave\\.?|blvd|plaza)\\s"))
        return QStringLiteral("address");
    if (matches(text, "\\b(negocio|business|empresa|marca|brand|tienda|store|shop|company)\\b"))
        return QStringLiteral("business");
    if (matches(text, "\\b(compra|compralo|reserva|llama|escribenos|siguenos|visita|pide|ordena|"
                      "suscribete|desliza|buy|shop now|order|call|book|follow|visit|subscribe|swipe|link)\\b"))
        return QStringLiteral("cta");
    if (largest)
        return QStringLiteral("title");
    return text.size() > 60 ? QStringLiteral("text") : QStringLiteral("subtitle");
}

// --- Brand kit --------------------------------------------------------------------------------

QColor BrandKit::colorFor(const QString &role) const
{
    const auto at = [this](int i) { return i < colors.size() ? colors.at(i) : QColor(); };
    if (role == QLatin1String("primary"))
        return at(0);
    if (role == QLatin1String("secondary"))
        return at(1).isValid() ? at(1) : at(0);
    if (role == QLatin1String("accent"))
        return at(2).isValid() ? at(2) : (at(1).isValid() ? at(1) : at(0));
    if (role == QLatin1String("text"))
        return at(3);
    return {};
}

namespace {

bool paintFill(QList<TextShadingLayer> &layers, const QColor &color)
{
    TextShadingLayer *fill = firstTextLayerOfKind(layers, TextLayerKind::Fill);
    if (!fill)
        return false;
    QColor c = color;
    if (fill->paint.kind == TextPaintKind::Solid)
        c.setAlphaF(fill->paint.color.alphaF() * color.alphaF());
    fill->paint.kind = TextPaintKind::Solid;
    fill->paint.color = c;
    return true;
}

bool isText(const Clip &clip)
{
    return clip.type == ClipType::Text || clip.type == ClipType::Subtitle;
}

} // namespace

BrandApplyResult applyBrandKit(QList<Track> &tracks, const BrandKit &kit)
{
    BrandApplyResult result;
    if (kit.isEmpty())
        return result;
    bool marked = false;
    bool logoMarked = false;
    for (const Track &track : tracks) {
        for (const Clip &clip : track.clips) {
            if (clip.brandRole.isEmpty())
                continue;
            marked = true;
            logoMarked = logoMarked || clip.brandRole.compare(QLatin1String("logo"), Qt::CaseInsensitive) == 0;
        }
    }
    const auto addLogo = [&](const Clip &clip) {
        if (!clip.placeholderId.isEmpty() && !isText(clip) && !result.logoSlots.contains(clip.placeholderId))
            result.logoSlots.append(clip.placeholderId);
    };

    if (marked) {
        for (Track &track : tracks) {
            for (Clip &clip : track.clips) {
                const QString role = clip.brandRole.toLower();
                if (role.isEmpty())
                    continue;
                if (role == QLatin1String("logo")) {
                    if (!kit.logoPath.isEmpty())
                        addLogo(clip);
                    continue;
                }
                const QColor color = kit.colorFor(role);
                if (color.isValid()) {
                    const bool done = clip.type == ClipType::Shape ? paintFill(clip.shapeStyle.layers, color)
                                      : isText(clip)               ? paintFill(clip.textStyle.layers, color)
                                                                   : false;
                    result.recoloured += done ? 1 : 0;
                }
                if (isText(clip) && !kit.fontFamily.isEmpty() && clip.textStyle.fontFamily != kit.fontFamily) {
                    clip.textStyle.fontFamily = kit.fontFamily;
                    ++result.refonted;
                }
            }
        }
    }

    // Unmarked templates (and marked ones without a logo slot): a slot whose label says "logo".
    if (!logoMarked && !kit.logoPath.isEmpty()) {
        for (const Track &track : tracks) {
            for (const Clip &clip : track.clips) {
                if (clip.placeholderLabel.contains(QLatin1String("logo"), Qt::CaseInsensitive))
                    addLogo(clip);
            }
        }
    }

    // Unmarked: the brand font on the titles, the largest of the editable texts (all texts when
    // none is editable).
    if (!marked && !kit.fontFamily.isEmpty()) {
        bool anyEditable = false;
        for (const Track &track : tracks) {
            for (const Clip &clip : track.clips)
                anyEditable = anyEditable || (isText(clip) && !clip.placeholderId.isEmpty());
        }
        double largest = 0.0;
        for (const Track &track : tracks) {
            for (const Clip &clip : track.clips) {
                if (isText(clip) && (!anyEditable || !clip.placeholderId.isEmpty()))
                    largest = qMax(largest, clip.textStyle.pixelSize);
            }
        }
        for (Track &track : tracks) {
            for (Clip &clip : track.clips) {
                if (!isText(clip) || (anyEditable && clip.placeholderId.isEmpty()) || largest <= 0
                    || clip.textStyle.pixelSize < largest * 0.8 || clip.textStyle.fontFamily == kit.fontFamily)
                    continue;
                clip.textStyle.fontFamily = kit.fontFamily;
                ++result.refonted;
            }
        }
    }
    return result;
}

// --- Template colours ------------------------------------------------------------------------

namespace {

double colourDistance(const QColor &a, const QColor &b)
{
    const double dr = a.red() - b.red();
    const double dg = a.green() - b.green();
    const double db = a.blue() - b.blue();
    return std::sqrt(dr * dr + dg * dg + db * db);
}

// Walks every colour a clip paints with. `paint` gets a colour it may change (rgb only matters);
// `keyed` gets a set of channel tracks "<base>.r/.g/.b" (0..1) with the static colour they animate.
struct ColourVisitor
{
    std::function<void(QColor &)> paint;
    std::function<void(QMap<QString, KeyframeTrack<double>> &, const QString &, const QColor &)> keyed;

    void layers(QList<TextShadingLayer> &stack, QMap<QString, KeyframeTrack<double>> *keys)
    {
        for (TextShadingLayer &layer : stack) {
            if (!layer.enabled)
                continue;
            switch (layer.paint.kind) {
            case TextPaintKind::Solid:
            case TextPaintKind::Effect:
                if (keys)
                    keyed(*keys, QStringLiteral("layer.%1.color").arg(layer.id), layer.paint.color);
                paint(layer.paint.color);
                break;
            case TextPaintKind::Gradient:
                for (TextGradientStop &stop : layer.paint.gradient.stops)
                    paint(stop.color);
                break;
            case TextPaintKind::Texture:
                break;
            }
            if (layer.paint.kind == TextPaintKind::Effect) {
                for (auto it = layer.paint.effect.params.begin(); it != layer.paint.effect.params.end(); ++it) {
                    if (it->type == VectorSlotValue::Type::Color)
                        paint(it->color);
                }
            }
        }
    }

    void shape(ShapeStyle &style)
    {
        layers(style.layers, &style.keyframes);
        for (ShapePart &part : style.parts)
            shapePart(part);
    }

    void shapePart(ShapePart &part)
    {
        if (!part.visible)
            return;
        if (part.group) {
            for (ShapePart &child : part.children)
                shapePart(child);
        } else {
            shape(part.shape);
        }
    }

    void text(TextStyle &style)
    {
        layers(style.layers, &style.keyframes);
        if (style.boxEnabled) {
            paint(style.boxColor);
            if (style.boxBorderWidth > 0.0)
                paint(style.boxBorderColor);
        }
        if (style.wordHighlight.enabled)
            paint(style.wordHighlight.color);
        if (style.underlineEnabled)
            paint(style.underlineColor);
        if (style.accent.rule != WordAccentRule::None) {
            if (style.accent.colorEnabled)
                paint(style.accent.color);
            if (style.accent.outlineEnabled)
                paint(style.accent.outlineColor);
            if (style.accent.highlight.enabled)
                paint(style.accent.highlight.color);
        }
        for (TextRun &run : style.runs) {
            if (run.colorEnabled)
                paint(run.color);
            if (run.layersEnabled)
                layers(run.layers, nullptr);
            if (run.boxEnabled) {
                paint(run.boxColor);
                if (run.boxBorderWidth > 0.0)
                    paint(run.boxBorderColor);
            }
        }
    }

    // Effect colours are "#rrggbb" or "#rrggbbaa" strings (or a QColor), animated as channel tracks.
    void effects(QList<Effect> &list)
    {
        static const QRegularExpression hexColour(QStringLiteral("^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$"));
        for (Effect &effect : list) {
            if (!effect.enabled)
                continue;
            for (auto it = effect.parameters.begin(); it != effect.parameters.end(); ++it) {
                QColor colour;
                QString tail;
                const bool isColour = it->metaType() == QMetaType::fromType<QColor>();
                if (isColour) {
                    colour = it->value<QColor>();
                } else if (it->metaType() == QMetaType::fromType<QString>()) {
                    const QString value = it->toString();
                    if (!hexColour.match(value).hasMatch())
                        continue;
                    colour = QColor(value.left(7));
                    tail = value.mid(7);
                } else {
                    continue;
                }
                const QColor before = colour;
                paint(colour);
                if (colour.rgb() != before.rgb())
                    *it = isColour ? QVariant(colour) : QVariant(colour.name(QColor::HexRgb) + tail);
                if (effect.paramKeyframes.contains(it.key() + QLatin1String(".r")))
                    keyed(effect.paramKeyframes, it.key(), before);
            }
        }
    }

    void clip(Clip &c)
    {
        if (c.type == ClipType::Shape)
            shape(c.shapeStyle);
        else if (c.type == ClipType::Text || c.type == ClipType::Subtitle)
            text(c.textStyle);
        effects(c.effects);
    }

    void tracks(QList<Track> &list)
    {
        for (Track &track : list) {
            for (Clip &c : track.clips)
                clip(c);
        }
    }
};

// The times any of the three channel tracks has a key at.
QList<TimeUs> channelKeyTimes(const QMap<QString, KeyframeTrack<double>> &keys, const QString &base)
{
    QSet<TimeUs> times;
    for (const char *suffix : {".r", ".g", ".b"}) {
        const auto it = keys.constFind(base + QLatin1String(suffix));
        if (it == keys.constEnd() || it->isEmpty())
            continue;
        for (auto k = it->keyframes().constBegin(); k != it->keyframes().constEnd(); ++k)
            times.insert(k.key());
    }
    QList<TimeUs> out(times.begin(), times.end());
    std::sort(out.begin(), out.end());
    return out;
}

QColor channelColourAt(const QMap<QString, KeyframeTrack<double>> &keys, const QString &base, const QColor &fallback,
                       TimeUs at)
{
    const auto channel = [&](const char *suffix, double value) {
        const auto it = keys.constFind(base + QLatin1String(suffix));
        if (it == keys.constEnd() || it->isEmpty())
            return value;
        const auto key = it->keyframes().constFind(at);
        return key != it->keyframes().constEnd() ? key->value : double(it->evaluateKeys(at));
    };
    QColor c;
    c.setRgbF(float(qBound(0.0, channel(".r", fallback.redF()), 1.0)),
              float(qBound(0.0, channel(".g", fallback.greenF()), 1.0)),
              float(qBound(0.0, channel(".b", fallback.blueF()), 1.0)));
    c.setAlphaF(fallback.alphaF());
    return c;
}

} // namespace

QList<TemplateColour> templateColours(const QList<const QList<Track> *> &lists, int maxCount)
{
    QHash<QRgb, int> counts;
    const auto count = [&](const QColor &c) {
        if (c.isValid() && c.alphaF() >= 0.05)
            counts[c.rgb() | 0xff000000u] += 1;
    };
    ColourVisitor visitor;
    visitor.paint = [&](QColor &c) { count(c); };
    visitor.keyed = [&](QMap<QString, KeyframeTrack<double>> &keys, const QString &base, const QColor &fallback) {
        for (const TimeUs at : channelKeyTimes(keys, base))
            count(channelColourAt(keys, base, fallback, at));
    };
    for (const QList<Track> *list : lists) {
        if (!list)
            continue;
        // The visitor only reads here; a copy keeps the caller's tracks const.
        QList<Track> copy = *list;
        visitor.tracks(copy);
    }

    QList<QPair<QRgb, int>> sorted;
    for (auto it = counts.constBegin(); it != counts.constEnd(); ++it)
        sorted.append({it.key(), it.value()});
    std::sort(sorted.begin(), sorted.end(), [](const auto &a, const auto &b) {
        return a.second != b.second ? a.second > b.second : a.first < b.first;
    });
    QList<TemplateColour> groups;
    for (const auto &entry : sorted) {
        const QColor c = QColor::fromRgb(entry.first);
        bool merged = false;
        for (TemplateColour &group : groups) {
            if (colourDistance(group.color, c) < kTemplateColourMerge) {
                group.uses += entry.second;
                merged = true;
                break;
            }
        }
        if (!merged)
            groups.append({c, entry.second});
    }
    std::stable_sort(groups.begin(), groups.end(),
                     [](const TemplateColour &a, const TemplateColour &b) { return a.uses > b.uses; });
    if (maxCount > 0 && groups.size() > maxCount)
        groups.resize(maxCount);
    return groups;
}

int replaceTemplateColour(const QList<QList<Track> *> &lists, const QColor &from, const QColor &to)
{
    if (!from.isValid() || !to.isValid())
        return 0;
    int changed = 0;
    const auto matches = [&](const QColor &c) {
        return c.isValid() && c.alphaF() >= 0.05 && colourDistance(c, from) < kTemplateColourMerge;
    };
    ColourVisitor visitor;
    visitor.paint = [&](QColor &c) {
        if (!matches(c))
            return;
        c = QColor(to.red(), to.green(), to.blue(), c.alpha());
        ++changed;
    };
    visitor.keyed = [&](QMap<QString, KeyframeTrack<double>> &keys, const QString &base, const QColor &fallback) {
        // `fallback` may already be the new colour (the visitor painted it first): the keys are
        // matched on their own values.
        for (const TimeUs at : channelKeyTimes(keys, base)) {
            if (!matches(channelColourAt(keys, base, fallback, at)))
                continue;
            const double values[3] = {to.redF(), to.greenF(), to.blueF()};
            const char *suffixes[3] = {".r", ".g", ".b"};
            for (int i = 0; i < 3; ++i) {
                auto it = keys.find(base + QLatin1String(suffixes[i]));
                if (it == keys.end())
                    continue;
                if (Keyframe<double> *key = it->keyframeRef(at))
                    key->value = values[i];
            }
            ++changed;
        }
    };
    for (QList<Track> *list : lists) {
        if (list)
            visitor.tracks(*list);
    }
    return changed;
}

} // namespace drift
