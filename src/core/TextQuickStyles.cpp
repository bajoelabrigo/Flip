#include "TextQuickStyles.h"

#include <QCoreApplication>

#include <functional>

namespace drift {

namespace {

// Every width below is a fraction of the font size, so a recipe reads the same at 40 px and 200 px.
using Layers = QList<TextShadingLayer>;
using Builder = std::function<Layers(double em)>;

TextShadingLayer fill(const QColor &color)
{
    return solidFillLayer(color, QStringLiteral("fill"));
}

TextShadingLayer gradientFill(const QList<TextGradientStop> &stops, double angle)
{
    TextShadingLayer layer = solidFillLayer(stops.first().color, QStringLiteral("fill"));
    layer.paint.kind = TextPaintKind::Gradient;
    layer.paint.gradient.stops = stops;
    layer.paint.gradient.angle = angle;
    return layer;
}

TextShadingLayer stroke(double width, const QColor &color, const QString &id = QStringLiteral("stroke"))
{
    return strokeLayer(width, color, id);
}

TextShadingLayer shadow(const QColor &color, double dx, double dy, double blur, double opacity)
{
    return shadowLayer(color, dx, dy, blur, opacity, QStringLiteral("shadow"));
}

TextShadingLayer glow(const QColor &color, double radius, double opacity, const QString &id = QStringLiteral("glow"))
{
    return glowLayer(color, radius, opacity, id);
}

TextShadingLayer extrude(double depth, const QColor &color)
{
    TextShadingLayer layer;
    layer.id = QStringLiteral("extrude");
    layer.kind = TextLayerKind::Extrude;
    layer.paint.color = color;
    layer.width = depth;
    layer.extrudeSteps = 10;
    layer.extrudeAngle = 45.0;
    layer.extrudeDarken = 0.25;
    return layer;
}

// A white core with a coloured halo, the way a neon tube reads on video.
Builder neon(const QColor &tube)
{
    return [tube](double em) {
        return Layers{glow(tube, em * 0.8, 0.55, QStringLiteral("glow2")), glow(tube, em * 0.3, 0.95),
                      stroke(em * 0.035, tube), fill(QColor(255, 255, 255))};
    };
}

Builder outlined(const QColor &text, const QColor &line, double width)
{
    return [=](double em) { return Layers{stroke(em * width, line), fill(text)}; };
}

Builder solid3d(const QColor &face, const QColor &side, const QColor &line = QColor())
{
    return [=](double em) {
        Layers layers{extrude(em * 0.16, side)};
        if (line.isValid())
            layers.append(stroke(em * 0.045, line));
        layers.append(fill(face));
        return layers;
    };
}

struct QuickStyle
{
    const char *id;
    const char *label;
    const char *category;
    Builder build;
};

const QList<QuickStyle> &quickStyles()
{
    static const QList<QuickStyle> styles = {
        // Básicos: the row under the text box.
        {"q-white", QT_TRANSLATE_NOOP("TextQuickStyles", "White"), "basic",
         [](double) { return Layers{fill(Qt::white)}; }},
        {"q-outline", QT_TRANSLATE_NOOP("TextQuickStyles", "Black outline"), "basic",
         outlined(Qt::white, Qt::black, 0.07)},
        {"q-outline-thick", QT_TRANSLATE_NOOP("TextQuickStyles", "Thick outline"), "basic",
         outlined(Qt::white, Qt::black, 0.13)},
        {"q-black-white", QT_TRANSLATE_NOOP("TextQuickStyles", "Black on white"), "basic",
         outlined(QColor(17, 17, 17), Qt::white, 0.09)},
        {"q-yellow", QT_TRANSLATE_NOOP("TextQuickStyles", "Yellow"), "basic",
         outlined(QColor(255, 230, 0), Qt::black, 0.08)},
        {"q-red", QT_TRANSLATE_NOOP("TextQuickStyles", "Red"), "basic",
         outlined(QColor(255, 45, 45), Qt::white, 0.08)},
        {"q-shadow", QT_TRANSLATE_NOOP("TextQuickStyles", "Soft shadow"), "basic",
         [](double em) { return Layers{shadow(Qt::black, 0, em * 0.05, em * 0.12, 0.7), fill(Qt::white)}; }},
        {"q-sticker", QT_TRANSLATE_NOOP("TextQuickStyles", "Sticker"), "basic",
         [](double em) {
             return Layers{shadow(Qt::black, 0, em * 0.04, em * 0.1, 0.45),
                           stroke(em * 0.17, Qt::white, QStringLiteral("stroke2")), stroke(em * 0.06, Qt::black),
                           fill(Qt::white)};
         }},
        {"q-cyan", QT_TRANSLATE_NOOP("TextQuickStyles", "Cyan"), "basic",
         outlined(QColor(35, 224, 255), QColor(11, 42, 111), 0.08)},
        {"q-pink", QT_TRANSLATE_NOOP("TextQuickStyles", "Pink"), "basic",
         outlined(QColor(255, 95, 162), Qt::white, 0.08)},
        {"q-green", QT_TRANSLATE_NOOP("TextQuickStyles", "Green"), "basic",
         outlined(QColor(57, 231, 95), Qt::black, 0.08)},
        {"q-orange", QT_TRANSLATE_NOOP("TextQuickStyles", "Orange"), "basic",
         outlined(QColor(255, 138, 0), Qt::black, 0.12)},
        {"q-purple", QT_TRANSLATE_NOOP("TextQuickStyles", "Purple"), "basic",
         outlined(QColor(155, 92, 255), Qt::white, 0.08)},
        {"q-hollow", QT_TRANSLATE_NOOP("TextQuickStyles", "Hollow"), "basic",
         [](double em) { return Layers{stroke(em * 0.05, Qt::white), fill(QColor(0, 0, 0, 0))}; }},

        // Neón
        {"n-pink", QT_TRANSLATE_NOOP("TextQuickStyles", "Pink neon"), "neon", neon(QColor(255, 47, 208))},
        {"n-cyan", QT_TRANSLATE_NOOP("TextQuickStyles", "Cyan neon"), "neon", neon(QColor(0, 229, 255))},
        {"n-green", QT_TRANSLATE_NOOP("TextQuickStyles", "Green neon"), "neon", neon(QColor(57, 255, 20))},
        {"n-yellow", QT_TRANSLATE_NOOP("TextQuickStyles", "Yellow neon"), "neon", neon(QColor(255, 220, 0))},
        {"n-purple", QT_TRANSLATE_NOOP("TextQuickStyles", "Purple neon"), "neon", neon(QColor(176, 38, 255))},
        {"n-red", QT_TRANSLATE_NOOP("TextQuickStyles", "Red neon"), "neon", neon(QColor(255, 30, 60))},
        {"n-blue", QT_TRANSLATE_NOOP("TextQuickStyles", "Blue neon"), "neon", neon(QColor(47, 123, 255))},
        {"n-warm", QT_TRANSLATE_NOOP("TextQuickStyles", "Warm light"), "neon", neon(QColor(255, 170, 60))},

        // Degradado
        {"g-sunset", QT_TRANSLATE_NOOP("TextQuickStyles", "Sunset"), "gradient",
         [](double em) {
             return Layers{shadow(Qt::black, 0, em * 0.04, em * 0.1, 0.5),
                           gradientFill({{0.0, QColor(255, 212, 0)}, {1.0, QColor(255, 61, 127)}}, 90)};
         }},
        {"g-ocean", QT_TRANSLATE_NOOP("TextQuickStyles", "Ocean"), "gradient",
         [](double em) {
             return Layers{stroke(em * 0.05, QColor(8, 24, 70)),
                           gradientFill({{0.0, QColor(63, 242, 255)}, {1.0, QColor(47, 91, 255)}}, 90)};
         }},
        {"g-fire", QT_TRANSLATE_NOOP("TextQuickStyles", "Fire"), "gradient",
         [](double em) {
             return Layers{stroke(em * 0.06, QColor(58, 0, 0)),
                           gradientFill({{0.0, QColor(255, 240, 77)}, {0.5, QColor(255, 122, 0)},
                                         {1.0, QColor(224, 0, 0)}}, 90)};
         }},
        {"g-candy", QT_TRANSLATE_NOOP("TextQuickStyles", "Candy"), "gradient",
         [](double em) {
             return Layers{stroke(em * 0.07, Qt::white),
                           gradientFill({{0.0, QColor(255, 154, 232)}, {1.0, QColor(155, 92, 255)}}, 0)};
         }},
        {"g-gold", QT_TRANSLATE_NOOP("TextQuickStyles", "Gold"), "gradient",
         [](double em) {
             return Layers{shadow(Qt::black, 0, em * 0.05, em * 0.08, 0.6), stroke(em * 0.05, QColor(59, 37, 0)),
                           gradientFill({{0.0, QColor(255, 243, 168)}, {0.5, QColor(224, 168, 0)},
                                         {1.0, QColor(138, 90, 0)}}, 90)};
         }},
        {"g-mint", QT_TRANSLATE_NOOP("TextQuickStyles", "Mint"), "gradient",
         [](double em) {
             return Layers{stroke(em * 0.05, QColor(0, 70, 60)),
                           gradientFill({{0.0, QColor(182, 255, 224)}, {1.0, QColor(0, 194, 168)}}, 90)};
         }},
        {"g-rainbow", QT_TRANSLATE_NOOP("TextQuickStyles", "Rainbow"), "gradient",
         [](double em) {
             return Layers{stroke(em * 0.06, Qt::white),
                           gradientFill({{0.0, QColor(255, 59, 59)}, {0.2, QColor(255, 165, 0)},
                                         {0.4, QColor(255, 230, 0)}, {0.6, QColor(57, 231, 95)},
                                         {0.8, QColor(47, 123, 255)}, {1.0, QColor(155, 92, 255)}}, 0)};
         }},
        {"g-chrome", QT_TRANSLATE_NOOP("TextQuickStyles", "Chrome"), "gradient",
         [](double em) {
             return Layers{stroke(em * 0.04, QColor(34, 34, 34)),
                           gradientFill({{0.0, Qt::white}, {0.45, QColor(154, 163, 173)},
                                         {0.55, QColor(70, 78, 88)}, {1.0, QColor(230, 233, 238)}}, 90)};
         }},

        // 3D
        {"d-white", QT_TRANSLATE_NOOP("TextQuickStyles", "White 3D"), "3d",
         solid3d(Qt::white, QColor(20, 20, 20), QColor(20, 20, 20))},
        {"d-yellow", QT_TRANSLATE_NOOP("TextQuickStyles", "Yellow 3D"), "3d",
         solid3d(QColor(255, 230, 0), QColor(215, 38, 30))},
        {"d-pink", QT_TRANSLATE_NOOP("TextQuickStyles", "Pink 3D"), "3d",
         solid3d(QColor(255, 123, 198), QColor(122, 31, 122))},
        {"d-cyan", QT_TRANSLATE_NOOP("TextQuickStyles", "Cyan 3D"), "3d",
         solid3d(QColor(111, 243, 255), QColor(26, 60, 158))},
        {"d-retro", QT_TRANSLATE_NOOP("TextQuickStyles", "Retro"), "3d",
         solid3d(QColor(255, 176, 0), QColor(90, 42, 0), QColor(90, 42, 0))},
        {"d-red", QT_TRANSLATE_NOOP("TextQuickStyles", "Red 3D"), "3d",
         solid3d(QColor(255, 59, 59), QColor(92, 0, 0), Qt::white)},

        // Sombra y contorno
        {"s-hard", QT_TRANSLATE_NOOP("TextQuickStyles", "Hard shadow"), "shadow",
         [](double em) {
             return Layers{shadow(Qt::black, em * 0.08, em * 0.08, 0, 1.0), stroke(em * 0.05, Qt::black),
                           fill(Qt::white)};
         }},
        {"s-long", QT_TRANSLATE_NOOP("TextQuickStyles", "Long shadow"), "shadow",
         [](double em) {
             return Layers{shadow(Qt::black, em * 0.15, em * 0.15, 0, 0.9), fill(QColor(255, 230, 0))};
         }},
        {"s-soft", QT_TRANSLATE_NOOP("TextQuickStyles", "Diffuse shadow"), "shadow",
         [](double em) { return Layers{shadow(Qt::black, 0, em * 0.04, em * 0.3, 0.85), fill(Qt::white)}; }},
        {"s-pop", QT_TRANSLATE_NOOP("TextQuickStyles", "Pop"), "shadow",
         [](double em) {
             return Layers{shadow(QColor(255, 45, 122), em * 0.1, em * 0.1, 0, 1.0), stroke(em * 0.06, Qt::black),
                           fill(QColor(255, 230, 0))};
         }},
        {"s-double", QT_TRANSLATE_NOOP("TextQuickStyles", "Double outline"), "shadow",
         [](double em) {
             return Layers{stroke(em * 0.17, QColor(255, 45, 122), QStringLiteral("stroke2")),
                           stroke(em * 0.07, Qt::black), fill(Qt::white)};
         }},
        {"s-halo", QT_TRANSLATE_NOOP("TextQuickStyles", "Dark halo"), "shadow",
         [](double em) { return Layers{glow(Qt::black, em * 0.25, 0.85), fill(Qt::white)}; }},
    };
    return styles;
}

struct Bubble
{
    const char *id;
    const char *label;
    const char *category;
    const char *shape;
    QColor box;
    QColor text;
    QColor border = QColor();
    double borderWidth = 0.0; // of the font size
    double radius = 0.0;      // of the font size
};

const QList<Bubble> &bubbles()
{
    static const QList<Bubble> list = {
        {"none", QT_TRANSLATE_NOOP("TextQuickStyles", "None"), "", "rect", QColor(), QColor()},

        // Cómic
        {"b-speech", QT_TRANSLATE_NOOP("TextQuickStyles", "Speech"), "comic", "speech", Qt::white,
         QColor(17, 17, 17), QColor(17, 17, 17), 0.07},
        {"b-oval", QT_TRANSLATE_NOOP("TextQuickStyles", "Balloon"), "comic", "oval", Qt::white,
         QColor(17, 17, 17), QColor(17, 17, 17), 0.07},
        {"b-thought", QT_TRANSLATE_NOOP("TextQuickStyles", "Thought"), "comic", "thought", Qt::white,
         QColor(17, 17, 17), QColor(17, 17, 17), 0.06},
        {"b-boom", QT_TRANSLATE_NOOP("TextQuickStyles", "Boom!"), "comic", "burst", QColor(255, 230, 0),
         QColor(227, 0, 27), QColor(227, 0, 27), 0.08},
        {"b-shout", QT_TRANSLATE_NOOP("TextQuickStyles", "Shout"), "comic", "shout", Qt::white,
         QColor(17, 17, 17), QColor(17, 17, 17), 0.07},
        {"b-pow", QT_TRANSLATE_NOOP("TextQuickStyles", "Pow!"), "comic", "burst", QColor(255, 59, 59),
         Qt::white, QColor(17, 17, 17), 0.07},
        {"b-cloud", QT_TRANSLATE_NOOP("TextQuickStyles", "Cloud"), "comic", "cloud", Qt::white,
         QColor(17, 17, 17), QColor(17, 17, 17), 0.05},

        // Etiquetas
        {"b-pill-black", QT_TRANSLATE_NOOP("TextQuickStyles", "Black pill"), "labels", "pill",
         QColor(0, 0, 0, 230), Qt::white},
        {"b-pill-white", QT_TRANSLATE_NOOP("TextQuickStyles", "White pill"), "labels", "pill", Qt::white,
         QColor(17, 17, 17)},
        {"b-pill-yellow", QT_TRANSLATE_NOOP("TextQuickStyles", "Yellow pill"), "labels", "pill",
         QColor(255, 230, 0), QColor(17, 17, 17)},
        {"b-box-black", QT_TRANSLATE_NOOP("TextQuickStyles", "Caption box"), "labels", "rect",
         QColor(0, 0, 0, 204), Qt::white, QColor(), 0.0, 0.1},
        {"b-box-red", QT_TRANSLATE_NOOP("TextQuickStyles", "Red box"), "labels", "rect", QColor(255, 45, 45),
         Qt::white, QColor(), 0.0, 0.12},
        {"b-tag-red", QT_TRANSLATE_NOOP("TextQuickStyles", "Tag"), "labels", "tag", QColor(255, 59, 59), Qt::white},
        {"b-tag-kraft", QT_TRANSLATE_NOOP("TextQuickStyles", "Kraft tag"), "labels", "tag", QColor(201, 160, 106),
         QColor(59, 37, 16), QColor(107, 74, 34), 0.04},
        {"b-ribbon-red", QT_TRANSLATE_NOOP("TextQuickStyles", "Red ribbon"), "labels", "ribbon",
         QColor(227, 0, 27), Qt::white},
        {"b-ribbon-blue", QT_TRANSLATE_NOOP("TextQuickStyles", "Blue ribbon"), "labels", "ribbon",
         QColor(47, 91, 255), Qt::white},
        {"b-arrow", QT_TRANSLATE_NOOP("TextQuickStyles", "Arrow"), "labels", "arrow", QColor(255, 230, 0),
         QColor(17, 17, 17)},
        {"b-ticket", QT_TRANSLATE_NOOP("TextQuickStyles", "Ticket"), "labels", "ticket", QColor(255, 138, 0),
         Qt::white},
        {"b-note-yellow", QT_TRANSLATE_NOOP("TextQuickStyles", "Sticky note"), "labels", "note",
         QColor(255, 242, 122), QColor(51, 51, 51)},
        {"b-note-pink", QT_TRANSLATE_NOOP("TextQuickStyles", "Pink note"), "labels", "note", QColor(255, 179, 217),
         QColor(90, 26, 58)},

        // Pincel y papel
        {"b-brush-pink", QT_TRANSLATE_NOOP("TextQuickStyles", "Pink brush"), "brush", "brush",
         QColor(255, 95, 162), Qt::white},
        {"b-brush-yellow", QT_TRANSLATE_NOOP("TextQuickStyles", "Yellow brush"), "brush", "brush",
         QColor(255, 230, 0), QColor(17, 17, 17)},
        {"b-brush-blue", QT_TRANSLATE_NOOP("TextQuickStyles", "Blue brush"), "brush", "brush",
         QColor(47, 123, 255), Qt::white},
        {"b-brush-black", QT_TRANSLATE_NOOP("TextQuickStyles", "Black brush"), "brush", "brush",
         QColor(17, 17, 17), Qt::white},
        {"b-torn-white", QT_TRANSLATE_NOOP("TextQuickStyles", "Paper"), "brush", "torn", QColor(246, 241, 231),
         QColor(34, 34, 34)},
        {"b-torn-kraft", QT_TRANSLATE_NOOP("TextQuickStyles", "Kraft paper"), "brush", "torn",
         QColor(201, 160, 106), QColor(43, 26, 8)},

        // Lindos
        {"b-heart", QT_TRANSLATE_NOOP("TextQuickStyles", "Heart"), "cute", "heart", QColor(255, 95, 162), Qt::white},
        {"b-cloud-pastel", QT_TRANSLATE_NOOP("TextQuickStyles", "Pastel cloud"), "cute", "cloud",
         QColor(191, 227, 255), QColor(42, 74, 122), Qt::white, 0.06},
        {"b-speech-lilac", QT_TRANSLATE_NOOP("TextQuickStyles", "Lilac speech"), "cute", "speech",
         QColor(205, 180, 255), QColor(59, 26, 107)},
        {"b-pill-mint", QT_TRANSLATE_NOOP("TextQuickStyles", "Mint pill"), "cute", "pill", QColor(182, 255, 224),
         QColor(11, 90, 71)},
        {"b-oval-pink", QT_TRANSLATE_NOOP("TextQuickStyles", "Pink balloon"), "cute", "oval",
         QColor(255, 209, 232), QColor(138, 31, 85), QColor(255, 95, 162), 0.05},
    };
    return list;
}

QString translated(const char *text)
{
    return QCoreApplication::translate("TextQuickStyles", text);
}

} // namespace

QList<TextGalleryEntry> textQuickStyles()
{
    QList<TextGalleryEntry> out;
    for (const QuickStyle &s : quickStyles())
        out.append({QLatin1String(s.id), translated(s.label), QLatin1String(s.category)});
    return out;
}

QList<QPair<QString, QString>> textQuickStyleCategories()
{
    return {{QStringLiteral("basic"), translated(QT_TRANSLATE_NOOP("TextQuickStyles", "Basic"))},
            {QStringLiteral("neon"), translated(QT_TRANSLATE_NOOP("TextQuickStyles", "Neon"))},
            {QStringLiteral("gradient"), translated(QT_TRANSLATE_NOOP("TextQuickStyles", "Gradient"))},
            {QStringLiteral("3d"), translated(QT_TRANSLATE_NOOP("TextQuickStyles", "3D"))},
            {QStringLiteral("shadow"), translated(QT_TRANSLATE_NOOP("TextQuickStyles", "Shadow and outline"))}};
}

bool applyTextQuickStyle(TextStyle &style, const QString &id)
{
    // The gallery's "no style" card: every effect off, the text keeps its colour.
    if (id == QLatin1String("q-plain")) {
        const QColor color = style.primaryColor();
        style.layers = {solidFillLayer(color.alpha() > 0 ? color : QColor(Qt::white), QStringLiteral("fill"))};
        style.lookId.clear();
        style.lookParams.clear();
        style.packId.clear();
        for (auto it = style.keyframes.begin(); it != style.keyframes.end();) {
            if (it.key().startsWith(QLatin1String("layer.")))
                it = style.keyframes.erase(it);
            else
                ++it;
        }
        return true;
    }
    for (const QuickStyle &s : quickStyles()) {
        if (id != QLatin1String(s.id))
            continue;
        style.layers = s.build(qMax(1, style.pixelSize));
        // The look gallery's recipe and the style pack no longer describe these layers.
        style.lookId.clear();
        style.lookParams.clear();
        style.packId.clear();
        // Keyframes on layers that no longer exist would be dropped by the renderer anyway.
        for (auto it = style.keyframes.begin(); it != style.keyframes.end();) {
            if (it.key().startsWith(QLatin1String("layer.")))
                it = style.keyframes.erase(it);
            else
                ++it;
        }
        return true;
    }
    return false;
}

QList<TextGalleryEntry> textBubbles()
{
    QList<TextGalleryEntry> out;
    for (const Bubble &b : bubbles())
        out.append({QLatin1String(b.id), translated(b.label), QLatin1String(b.category)});
    return out;
}

QList<QPair<QString, QString>> textBubbleCategories()
{
    return {{QStringLiteral("comic"), translated(QT_TRANSLATE_NOOP("TextQuickStyles", "Comic"))},
            {QStringLiteral("labels"), translated(QT_TRANSLATE_NOOP("TextQuickStyles", "Labels"))},
            {QStringLiteral("brush"), translated(QT_TRANSLATE_NOOP("TextQuickStyles", "Brush and paper"))},
            {QStringLiteral("cute"), translated(QT_TRANSLATE_NOOP("TextQuickStyles", "Cute"))}};
}

bool applyTextBubble(TextStyle &style, const QString &id)
{
    for (const Bubble &b : bubbles()) {
        if (id != QLatin1String(b.id))
            continue;
        if (id == QLatin1String("none")) {
            style.boxEnabled = false;
            style.boxShape = QStringLiteral("rect");
            return true;
        }
        const double em = qMax(1, style.pixelSize);
        style.boxEnabled = true;
        style.boxStyle = QStringLiteral("block");
        style.boxShape = QLatin1String(b.shape);
        style.boxColor = b.box;
        style.boxRadius = em * b.radius;
        style.boxPaddingX = em * 0.45;
        style.boxPaddingY = em * 0.28;
        style.boxOffsetX = 0.0;
        style.boxOffsetY = 0.0;
        style.boxBorderWidth = b.border.isValid() ? em * b.borderWidth : 0.0;
        if (b.border.isValid())
            style.boxBorderColor = b.border;
        // A plain fill in a colour that reads on the bubble; outlines and glows meant for bare
        // text over video only muddy it.
        style.layers = {solidFillLayer(b.text, QStringLiteral("fill"))};
        style.lookId.clear();
        style.lookParams.clear();
        style.packId.clear();
        for (auto it = style.keyframes.begin(); it != style.keyframes.end();) {
            if (it.key().startsWith(QLatin1String("layer.")))
                it = style.keyframes.erase(it);
            else
                ++it;
        }
        return true;
    }
    return false;
}

} // namespace drift
