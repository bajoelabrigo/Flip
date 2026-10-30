#include "ShapeStyle.h"
#include "ShapePathEdit.h"

#include "Effect.h"

#include "ShapePath.h"

#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QHash>
#include <QJsonArray>
#include <QJsonDocument>
#include <QLocale>
#include <QMutex>
#include <QRegularExpression>
#include <QSaveFile>
#include <QSet>
#include <QStandardPaths>
#include <algorithm>
#include <optional>
#include <utility>

namespace drift {
namespace {

// The parts' share of shapeStyleHash (0.28), defined with the parts below.
quint64 shapePartsHash(const ShapeStyle &style);

struct KindName
{
    ShapeKind kind;
    const char *name;
};

// The first five names are what projects saved before the roster grew still contain, so they must
// not change.
constexpr KindName kKindNames[] = {
    {ShapeKind::Rectangle, "rectangle"},
    {ShapeKind::Square, "square"},
    {ShapeKind::Triangle, "triangle"},
    {ShapeKind::Pentagon, "pentagon"},
    {ShapeKind::Hexagon, "hexagon"},
    {ShapeKind::RoundedRectangle, "rounded-rectangle"},
    {ShapeKind::Ellipse, "ellipse"},
    {ShapeKind::RightTriangle, "right-triangle"},
    {ShapeKind::Diamond, "diamond"},
    {ShapeKind::Octagon, "octagon"},
    {ShapeKind::Parallelogram, "parallelogram"},
    {ShapeKind::Trapezoid, "trapezoid"},
    {ShapeKind::Arrow, "arrow"},
    {ShapeKind::DoubleArrow, "double-arrow"},
    {ShapeKind::BlockArrow, "block-arrow"},
    {ShapeKind::CurvedArrow, "curved-arrow"},
    {ShapeKind::Chevron, "chevron"},
    {ShapeKind::SpeechBubble, "speech-bubble"},
    {ShapeKind::SpeechBubbleRect, "speech-bubble-rect"},
    {ShapeKind::ThoughtBubble, "thought-bubble"},
    {ShapeKind::Callout, "callout"},
    {ShapeKind::Star, "star"},
    {ShapeKind::LightningBolt, "lightning-bolt"},
    {ShapeKind::Cloud, "cloud"},
    {ShapeKind::Heart, "heart"},
    {ShapeKind::Cross, "cross"},
    {ShapeKind::Burst, "burst"},
    {ShapeKind::Banner, "banner"},
    {ShapeKind::Custom, "custom"},
};

ShapeStyle makeStyle(ShapeKind kind, const QColor &fill, const QColor &fillSecondary)
{
    ShapeStyle style;
    style.kind = kind;
    style.layers = defaultShapeLayers(fill, fillSecondary);
    return style;
}

QList<ShapeCatalogEntry> buildCatalog()
{
    const QColor blue(0, 180, 255);
    const QColor blueDeep(0, 92, 220);
    const QColor orange(255, 120, 64);
    const QColor orangeDeep(220, 60, 40);
    const QColor yellow(255, 214, 10);
    const QColor yellowDeep(240, 140, 0);
    const QColor purple(160, 96, 255);
    const QColor purpleDeep(96, 40, 200);
    const QColor green(80, 220, 140);
    const QColor greenDeep(20, 150, 110);
    const QColor pink(255, 96, 150);
    const QColor pinkDeep(200, 30, 110);

    QList<ShapeCatalogEntry> catalog{
        {QStringLiteral("rectangle"), QCoreApplication::translate("ShapeStyle", "Rectangle"), QStringLiteral("basic"), 1.6,
         makeStyle(ShapeKind::Rectangle, blue, blueDeep)},
        {QStringLiteral("rounded-rectangle"), QCoreApplication::translate("ShapeStyle", "Rounded rectangle"),
         QStringLiteral("basic"), 1.6, makeStyle(ShapeKind::RoundedRectangle, blue, blueDeep)},
        {QStringLiteral("square"), QCoreApplication::translate("ShapeStyle", "Square"), QStringLiteral("basic"), 1.0,
         makeStyle(ShapeKind::Square, orange, orangeDeep)},
        // "ellipse" leads "circle" because the inspector's kind list keeps the first entry of each
        // ShapeKind, and "Ellipse" is the honest label for both.
        {QStringLiteral("ellipse"), QCoreApplication::translate("ShapeStyle", "Ellipse"), QStringLiteral("basic"), 1.6,
         makeStyle(ShapeKind::Ellipse, yellow, yellowDeep)},
        {QStringLiteral("circle"), QCoreApplication::translate("ShapeStyle", "Circle"), QStringLiteral("basic"), 1.0,
         makeStyle(ShapeKind::Ellipse, yellow, yellowDeep)},
        {QStringLiteral("triangle"), QCoreApplication::translate("ShapeStyle", "Triangle"), QStringLiteral("basic"), 1.0,
         makeStyle(ShapeKind::Triangle, yellow, yellowDeep)},
        {QStringLiteral("right-triangle"), QCoreApplication::translate("ShapeStyle", "Right triangle"), QStringLiteral("basic"),
         1.0, makeStyle(ShapeKind::RightTriangle, yellow, yellowDeep)},
        {QStringLiteral("diamond"), QCoreApplication::translate("ShapeStyle", "Diamond"), QStringLiteral("basic"), 1.0,
         makeStyle(ShapeKind::Diamond, blue, blueDeep)},
        {QStringLiteral("pentagon"), QCoreApplication::translate("ShapeStyle", "Pentagon"), QStringLiteral("basic"), 1.0,
         makeStyle(ShapeKind::Pentagon, purple, purpleDeep)},
        {QStringLiteral("hexagon"), QCoreApplication::translate("ShapeStyle", "Hexagon"), QStringLiteral("basic"), 1.0,
         makeStyle(ShapeKind::Hexagon, green, greenDeep)},
        {QStringLiteral("octagon"), QCoreApplication::translate("ShapeStyle", "Octagon"), QStringLiteral("basic"), 1.0,
         makeStyle(ShapeKind::Octagon, green, greenDeep)},
        {QStringLiteral("parallelogram"), QCoreApplication::translate("ShapeStyle", "Parallelogram"), QStringLiteral("basic"),
         1.6, makeStyle(ShapeKind::Parallelogram, blue, blueDeep)},
        {QStringLiteral("trapezoid"), QCoreApplication::translate("ShapeStyle", "Trapezoid"), QStringLiteral("basic"), 1.6,
         makeStyle(ShapeKind::Trapezoid, blue, blueDeep)},

        {QStringLiteral("arrow"), QCoreApplication::translate("ShapeStyle", "Arrow"), QStringLiteral("arrows"), 2.0,
         makeStyle(ShapeKind::Arrow, orange, orangeDeep)},
        {QStringLiteral("double-arrow"), QCoreApplication::translate("ShapeStyle", "Double arrow"), QStringLiteral("arrows"),
         2.0, makeStyle(ShapeKind::DoubleArrow, orange, orangeDeep)},
        {QStringLiteral("block-arrow"), QCoreApplication::translate("ShapeStyle", "Block arrow"), QStringLiteral("arrows"), 1.6,
         makeStyle(ShapeKind::BlockArrow, orange, orangeDeep)},
        {QStringLiteral("curved-arrow"), QCoreApplication::translate("ShapeStyle", "Curved arrow"), QStringLiteral("arrows"),
         1.3, makeStyle(ShapeKind::CurvedArrow, orange, orangeDeep)},
        {QStringLiteral("chevron"), QCoreApplication::translate("ShapeStyle", "Chevron"), QStringLiteral("arrows"), 1.4,
         makeStyle(ShapeKind::Chevron, orange, orangeDeep)},

        {QStringLiteral("speech-bubble"), QCoreApplication::translate("ShapeStyle", "Speech bubble"), QStringLiteral("bubbles"),
         1.4, makeStyle(ShapeKind::SpeechBubble, blue, blueDeep)},
        {QStringLiteral("speech-bubble-rect"), QCoreApplication::translate("ShapeStyle", "Rounded bubble"),
         QStringLiteral("bubbles"), 1.5, makeStyle(ShapeKind::SpeechBubbleRect, blue, blueDeep)},
        {QStringLiteral("thought-bubble"), QCoreApplication::translate("ShapeStyle", "Thought bubble"),
         QStringLiteral("bubbles"), 1.4, makeStyle(ShapeKind::ThoughtBubble, blue, blueDeep)},
        {QStringLiteral("callout"), QCoreApplication::translate("ShapeStyle", "Callout"), QStringLiteral("bubbles"), 1.5,
         makeStyle(ShapeKind::Callout, purple, purpleDeep)},

        {QStringLiteral("star"), QCoreApplication::translate("ShapeStyle", "Star"), QStringLiteral("fun"), 1.0,
         makeStyle(ShapeKind::Star, yellow, yellowDeep)},
        {QStringLiteral("burst"), QCoreApplication::translate("ShapeStyle", "Burst"), QStringLiteral("fun"), 1.0,
         makeStyle(ShapeKind::Burst, yellow, orangeDeep)},
        {QStringLiteral("lightning-bolt"), QCoreApplication::translate("ShapeStyle", "Lightning bolt"), QStringLiteral("fun"),
         0.6, makeStyle(ShapeKind::LightningBolt, yellow, orangeDeep)},
        {QStringLiteral("cloud"), QCoreApplication::translate("ShapeStyle", "Cloud"), QStringLiteral("fun"), 1.6,
         makeStyle(ShapeKind::Cloud, QColor(235, 245, 255), QColor(150, 190, 235))},
        {QStringLiteral("heart"), QCoreApplication::translate("ShapeStyle", "Heart"), QStringLiteral("fun"), 1.0,
         makeStyle(ShapeKind::Heart, pink, pinkDeep)},
        {QStringLiteral("cross"), QCoreApplication::translate("ShapeStyle", "Cross"), QStringLiteral("fun"), 1.0,
         makeStyle(ShapeKind::Cross, pink, pinkDeep)},
        {QStringLiteral("banner"), QCoreApplication::translate("ShapeStyle", "Banner"), QStringLiteral("fun"), 2.2,
         makeStyle(ShapeKind::Banner, purple, purpleDeep)},
    };

    // Per-kind geometry defaults. Everything not listed keeps the ShapeStyle defaults.
    for (ShapeCatalogEntry &entry : catalog) {
        switch (entry.style.kind) {
        case ShapeKind::RoundedRectangle:
        case ShapeKind::SpeechBubbleRect:
        case ShapeKind::Callout:
            entry.style.cornerRadius = 32.0;
            break;
        case ShapeKind::Burst:
            entry.style.points = 12;
            entry.style.innerRatio = 0.62;
            break;
        case ShapeKind::Cross:
            entry.style.thickness = 0.36;
            break;
        case ShapeKind::Chevron:
            entry.style.headSize = 0.3;
            break;
        case ShapeKind::CurvedArrow:
            entry.style.thickness = 0.35;
            break;
        default:
            break;
        }
    }

    return catalog;
}

} // namespace

QString shapeKindToString(ShapeKind kind)
{
    for (const KindName &entry : kKindNames) {
        if (entry.kind == kind)
            return QString::fromLatin1(entry.name);
    }
    return QStringLiteral("rectangle");
}

ShapeKind shapeKindFromString(const QString &kind)
{
    for (const KindName &entry : kKindNames) {
        if (kind == QLatin1String(entry.name))
            return entry.kind;
    }
    // Catalog ids are not all kind names ("circle" is an ellipse), and the UI addresses shapes by
    // id, so fall back to a catalog lookup before giving up.
    if (const ShapeCatalogEntry *entry = shapeCatalogEntry(kind))
        return entry->style.kind;
    return ShapeKind::Rectangle;
}

const QList<ShapeCatalogEntry> &shapeCatalog()
{
    static const QList<ShapeCatalogEntry> catalog = buildCatalog();
    return catalog;
}

namespace {

struct UserShapes
{
    QMutex mutex;
    // Live entries by catalog id, in display order.
    QList<const ShapeCatalogEntry *> ordered;
    QHash<QString, const ShapeCatalogEntry *> byId;
    QList<ShapeCategory> categories;
    bool loaded = false;
};

UserShapes &userShapes()
{
    static UserShapes shapes;
    return shapes;
}

// The name in the UI language: exact tag ("pt_BR"), then the language ("pt"), then English,
// Spanish, then anything.
QString localizedName(const QJsonObject &names, const QString &fallback)
{
    const QLocale locale;
    const QString full = locale.name();
    const QString lang = full.section(QLatin1Char('_'), 0, 0);
    for (const QString &key : {full, lang, QStringLiteral("en"), QStringLiteral("es")}) {
        const QString v = names.value(key).toString().trimmed();
        if (!v.isEmpty())
            return v;
    }
    for (auto it = names.constBegin(); it != names.constEnd(); ++it) {
        const QString v = it.value().toString().trimmed();
        if (!v.isEmpty())
            return v;
    }
    return fallback;
}

const QRegularExpression &userShapeIdPattern()
{
    static const QRegularExpression re(QStringLiteral("^[a-z0-9][a-z0-9._-]{0,63}$"));
    return re;
}

// The entry a shape file describes, or nullopt with *error set.
std::optional<ShapeCatalogEntry> parseUserShape(const QByteArray &bytes, QString *error,
                                                QString *categoryLabel = nullptr)
{
    const auto fail = [&](const QString &why) {
        if (error)
            *error = why;
        return std::optional<ShapeCatalogEntry>();
    };
    const QJsonDocument doc = QJsonDocument::fromJson(bytes);
    if (!doc.isObject())
        return fail(QStringLiteral("not a JSON object"));
    const QJsonObject o = doc.object();
    if (o.value(QStringLiteral("format")).toInt(1) != 1)
        return fail(QStringLiteral("unknown format"));
    const QString id = o.value(QStringLiteral("id")).toString();
    if (!userShapeIdPattern().match(id).hasMatch())
        return fail(QStringLiteral("bad id"));
    const QString d = o.value(QStringLiteral("path")).toString();
    QPainterPath parsed;
    if (d.size() > 64 * 1024 || !parseSvgPathData(d, &parsed))
        return fail(QStringLiteral("the outline does not parse"));
    const QRectF box = parsed.boundingRect();
    if (box.width() <= 0.0 || box.height() <= 0.0)
        return fail(QStringLiteral("the outline is empty"));

    ShapeCatalogEntry entry;
    entry.id = QString::fromLatin1(kUserShapePrefix) + id;
    entry.label = localizedName(o.value(QStringLiteral("names")).toObject(), id);
    entry.category = QStringLiteral("user-") + o.value(QStringLiteral("category")).toString(QStringLiteral("shapes"));
    entry.aspect = qBound(0.1, o.value(QStringLiteral("aspect")).toDouble(1.0), 10.0);
    const QColor fill(o.value(QStringLiteral("fill")).toString(QStringLiteral("#FF6096")));
    const QColor deep(o.value(QStringLiteral("fillDeep")).toString());
    entry.style.kind = ShapeKind::Custom;
    entry.style.layers = defaultShapeLayers(fill.isValid() ? fill : QColor(255, 96, 150),
                                            deep.isValid() ? deep : QColor(), Qt::white, 0.0);
    entry.style.customPath = d;
    entry.style.customEvenOdd = o.value(QStringLiteral("fillRule")).toString() == QLatin1String("evenodd");
    if (categoryLabel)
        *categoryLabel = localizedName(o.value(QStringLiteral("categoryNames")).toObject(),
                                       o.value(QStringLiteral("category")).toString());
    return entry;
}

void ensureUserShapesLoaded()
{
    UserShapes &shapes = userShapes();
    bool loaded = false;
    {
        QMutexLocker lock(&shapes.mutex);
        loaded = shapes.loaded;
    }
    if (!loaded)
        reloadUserShapes();
}

} // namespace

const ShapeCatalogEntry *shapeCatalogEntry(const QString &id)
{
    const QList<ShapeCatalogEntry> &catalog = shapeCatalog();
    const auto it = std::find_if(catalog.cbegin(), catalog.cend(),
                                 [&](const ShapeCatalogEntry &e) { return e.id == id; });
    if (it != catalog.cend())
        return &(*it);
    if (!id.startsWith(QLatin1String(kUserShapePrefix)))
        return nullptr;
    ensureUserShapesLoaded();
    UserShapes &shapes = userShapes();
    QMutexLocker lock(&shapes.mutex);
    return shapes.byId.value(id, nullptr);
}

QString userShapesDir()
{
    return QDir(QStandardPaths::writableLocation(QStandardPaths::AppDataLocation))
        .filePath(QStringLiteral("shapes"));
}

void reloadUserShapes()
{
    struct Loaded
    {
        ShapeCatalogEntry entry;
        QString categoryLabel;
    };
    QList<Loaded> found;
    const QDir dir(userShapesDir());
    const QFileInfoList files = dir.entryInfoList({QStringLiteral("*.json")}, QDir::Files, QDir::Name);
    for (const QFileInfo &info : files) {
        QFile file(info.absoluteFilePath());
        if (!file.open(QIODevice::ReadOnly) || file.size() > 256 * 1024)
            continue;
        QString label;
        if (auto entry = parseUserShape(file.readAll(), nullptr, &label))
            found.append({*entry, label});
    }
    std::stable_sort(found.begin(), found.end(), [](const Loaded &a, const Loaded &b) {
        if (a.entry.category != b.entry.category)
            return a.entry.category < b.entry.category;
        return QString::localeAwareCompare(a.entry.label, b.entry.label) < 0;
    });

    UserShapes &shapes = userShapes();
    QMutexLocker lock(&shapes.mutex);
    // Old entries are leaked on purpose: a render thread may still hold a pointer from
    // shapeCatalogEntry(), and a rescan only happens on start or after an install.
    shapes.ordered.clear();
    shapes.byId.clear();
    shapes.categories.clear();
    QSet<QString> seenCategories;
    for (const Loaded &row : std::as_const(found)) {
        const auto *entry = new ShapeCatalogEntry(row.entry);
        shapes.ordered.append(entry);
        shapes.byId.insert(entry->id, entry);
        if (!seenCategories.contains(entry->category)) {
            seenCategories.insert(entry->category);
            shapes.categories.append({entry->category, row.categoryLabel});
        }
    }
    shapes.loaded = true;
}

QList<ShapeCatalogEntry> userShapeCatalog()
{
    ensureUserShapesLoaded();
    UserShapes &shapes = userShapes();
    QMutexLocker lock(&shapes.mutex);
    QList<ShapeCatalogEntry> out;
    out.reserve(shapes.ordered.size());
    for (const ShapeCatalogEntry *entry : std::as_const(shapes.ordered))
        out.append(*entry);
    return out;
}

QList<ShapeCategory> userShapeCategories()
{
    ensureUserShapesLoaded();
    UserShapes &shapes = userShapes();
    QMutexLocker lock(&shapes.mutex);
    return shapes.categories;
}

QString installUserShapeFile(const QString &path, QString *error)
{
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly) || file.size() > 256 * 1024) {
        if (error)
            *error = QStringLiteral("cannot read the file");
        return {};
    }
    const QByteArray bytes = file.readAll();
    const auto entry = parseUserShape(bytes, error);
    if (!entry)
        return {};
    const QString id = entry->id.mid(int(qstrlen(kUserShapePrefix)));
    QDir().mkpath(userShapesDir());
    QSaveFile out(QDir(userShapesDir()).filePath(id + QStringLiteral(".json")));
    if (!out.open(QIODevice::WriteOnly) || out.write(bytes) != bytes.size() || !out.commit()) {
        if (error)
            *error = QStringLiteral("cannot write into the shapes folder");
        return {};
    }
    reloadUserShapes();
    return entry->id;
}

bool removeUserShape(const QString &catalogId)
{
    if (!catalogId.startsWith(QLatin1String(kUserShapePrefix)))
        return false;
    const QString id = catalogId.mid(int(qstrlen(kUserShapePrefix)));
    if (!userShapeIdPattern().match(id).hasMatch())
        return false;
    const bool removed = QFile::remove(QDir(userShapesDir()).filePath(id + QStringLiteral(".json")));
    if (removed)
        reloadUserShapes();
    return removed;
}

QList<ShapeCategory> shapeCategories()
{
    return {
        {QStringLiteral("basic"), QCoreApplication::translate("ShapeStyle", "Basic")},
        {QStringLiteral("arrows"), QCoreApplication::translate("ShapeStyle", "Arrows")},
        {QStringLiteral("bubbles"), QCoreApplication::translate("ShapeStyle", "Bubbles")},
        {QStringLiteral("fun"), QCoreApplication::translate("ShapeStyle", "Fun")},
    };
}

// ---------------------------------------------------------------------------------------------
// Layers

QList<TextShadingLayer> defaultShapeLayers(const QColor &fill, const QColor &fillDeep, const QColor &stroke,
                                           double strokeWidth)
{
    TextShadingLayer fillLayer = solidFillLayer(fill, QStringLiteral("fill"));
    fillLayer.paint.gradient.stops = {{0.0, fill}, {1.0, fillDeep.isValid() ? fillDeep : fill.darker(160)}};
    TextShadingLayer strokeLayer_ = strokeLayer(qMax(0.0, strokeWidth), stroke, QStringLiteral("stroke"));
    strokeLayer_.strokeAlign = StrokeAlign::Inside;
    strokeLayer_.enabled = strokeWidth > 0.0;
    return {fillLayer, strokeLayer_};
}

QColor ShapeStyle::primaryColor() const
{
    // A layer of parts: the top shape part's colour.
    if (hasParts()) {
        std::vector<const ShapePart *> stack;
        for (auto it = parts.rbegin(); it != parts.rend(); ++it)
            stack.push_back(&*it);
        while (!stack.empty()) {
            const ShapePart *part = stack.back();
            stack.pop_back();
            if (!part->group)
                return part->shape.primaryColor();
            for (auto it = part->children.rbegin(); it != part->children.rend(); ++it)
                stack.push_back(&*it);
        }
    }
    if (const TextShadingLayer *fill = firstTextLayerOfKind(layers, TextLayerKind::Fill))
        return fill->paint.kind == TextPaintKind::Gradient && !fill->paint.gradient.stops.isEmpty()
                   ? fill->paint.gradient.stops.first().color
                   : fill->paint.color;
    return QColor(0, 180, 255);
}

void ShapeStyle::setPrimaryColor(const QColor &color)
{
    // Simple mode recolours a layer of parts as one shape: every part takes the colour.
    if (hasParts()) {
        std::vector<ShapePart *> stack;
        for (ShapePart &part : parts)
            stack.push_back(&part);
        while (!stack.empty()) {
            ShapePart *part = stack.back();
            stack.pop_back();
            if (!part->group)
                part->shape.setPrimaryColor(color);
            for (ShapePart &child : part->children)
                stack.push_back(&child);
        }
    }
    if (TextShadingLayer *fill = firstTextLayerOfKind(layers, TextLayerKind::Fill, false)) {
        fill->paint.color = color;
        if (!fill->paint.gradient.stops.isEmpty())
            fill->paint.gradient.stops.first().color = color;
        return;
    }
    layers.prepend(solidFillLayer(color, QStringLiteral("fill")));
}

void ShapeStyle::setSolidFill(const QColor &color)
{
    const TextShadingLayer *stroke = firstTextLayerOfKind(layers, TextLayerKind::Stroke, false);
    layers = defaultShapeLayers(color, QColor(), stroke ? stroke->paint.color : QColor(Qt::white),
                                stroke && stroke->enabled ? stroke->width : 0.0);
}

void ShapeStyle::setStroke(double width, const QColor &color)
{
    TextShadingLayer *stroke = firstTextLayerOfKind(layers, TextLayerKind::Stroke, false);
    if (!stroke) {
        TextShadingLayer layer = strokeLayer(width, color, QStringLiteral("stroke"));
        layer.strokeAlign = StrokeAlign::Inside;
        layers.append(layer);
        stroke = &layers.last();
    }
    stroke->width = qMax(0.0, width);
    stroke->paint.color = color;
    stroke->enabled = width > 0.0;
}

// ---------------------------------------------------------------------------------------------
// Keyframes

namespace {

struct KnobField
{
    const char *key;
    const char *label;
    double ShapeStyle::*field;
    double min;
    double max;
};

// points is an int and handled apart from the doubles.
constexpr KnobField kKnobs[] = {
    {"cornerRadius", QT_TRANSLATE_NOOP("ShapeStyle", "Corner radius"), &ShapeStyle::cornerRadius, 0.0, 2000.0},
    {"innerRatio", QT_TRANSLATE_NOOP("ShapeStyle", "Inner radius"), &ShapeStyle::innerRatio, 0.05, 0.95},
    {"headSize", QT_TRANSLATE_NOOP("ShapeStyle", "Head size"), &ShapeStyle::headSize, 0.05, 0.9},
    {"thickness", QT_TRANSLATE_NOOP("ShapeStyle", "Thickness"), &ShapeStyle::thickness, 0.05, 1.0},
    {"tailX", QT_TRANSLATE_NOOP("ShapeStyle", "Tail position"), &ShapeStyle::tailX, 0.08, 0.92},
    {"tailSize", QT_TRANSLATE_NOOP("ShapeStyle", "Tail size"), &ShapeStyle::tailSize, 0.05, 0.5},
    {"trimStart", QT_TRANSLATE_NOOP("ShapeStyle", "Trim start"), &ShapeStyle::trimStart, 0.0, 100.0},
    {"trimEnd", QT_TRANSLATE_NOOP("ShapeStyle", "Trim end"), &ShapeStyle::trimEnd, 0.0, 100.0},
    {"trimOffset", QT_TRANSLATE_NOOP("ShapeStyle", "Trim offset"), &ShapeStyle::trimOffset, -36000.0, 36000.0},
    {"trimSegments", QT_TRANSLATE_NOOP("ShapeStyle", "Trim segments"), &ShapeStyle::trimSegments, 1.0, 64.0},
    {"trimReverse", QT_TRANSLATE_NOOP("ShapeStyle", "Reverse path direction"), &ShapeStyle::trimReverse, 0.0, 1.0},
    {"repeatCopies", QT_TRANSLATE_NOOP("ShapeStyle", "Copies"), &ShapeStyle::repeatCopies, 1.0, 200.0},
    {"repeatOffset", QT_TRANSLATE_NOOP("ShapeStyle", "Repeater offset"), &ShapeStyle::repeatOffset, -200.0, 200.0},
    {"repeatX", QT_TRANSLATE_NOOP("ShapeStyle", "Repeater position X"), &ShapeStyle::repeatX, -10000.0, 10000.0},
    {"repeatY", QT_TRANSLATE_NOOP("ShapeStyle", "Repeater position Y"), &ShapeStyle::repeatY, -10000.0, 10000.0},
    {"repeatScale", QT_TRANSLATE_NOOP("ShapeStyle", "Repeater scale"), &ShapeStyle::repeatScale, 0.0, 1000.0},
    {"repeatRotation", QT_TRANSLATE_NOOP("ShapeStyle", "Repeater rotation"), &ShapeStyle::repeatRotation, -36000.0, 36000.0},
    {"repeatStartOpacity", QT_TRANSLATE_NOOP("ShapeStyle", "Start opacity"), &ShapeStyle::repeatStartOpacity, 0.0, 100.0},
    {"repeatEndOpacity", QT_TRANSLATE_NOOP("ShapeStyle", "End opacity"), &ShapeStyle::repeatEndOpacity, 0.0, 100.0},
    {"wiggleSize", QT_TRANSLATE_NOOP("ShapeStyle", "Wiggle size"), &ShapeStyle::wiggleSize, 0.0, 1000.0},
    {"wiggleDetail", QT_TRANSLATE_NOOP("ShapeStyle", "Wiggle detail"), &ShapeStyle::wiggleDetail, 2.0, 500.0},
    {"wiggleSpeed", QT_TRANSLATE_NOOP("ShapeStyle", "Wiggles per second"), &ShapeStyle::wiggleSpeed, 0.0, 30.0},
    {"wiggleSeed", QT_TRANSLATE_NOOP("ShapeStyle", "Random seed"), &ShapeStyle::wiggleSeed, 0.0, 1000.0},
    {"mergeMode", QT_TRANSLATE_NOOP("ShapeStyle", "Merge paths"), &ShapeStyle::mergeMode, 0.0, 4.0},
    {"offsetPath", QT_TRANSLATE_NOOP("ShapeStyle", "Offset paths"), &ShapeStyle::offsetPath, -500.0, 500.0},
    {"zigzagSize", QT_TRANSLATE_NOOP("ShapeStyle", "Zig zag size"), &ShapeStyle::zigzagSize, 0.0, 500.0},
    {"zigzagRidges", QT_TRANSLATE_NOOP("ShapeStyle", "Ridges"), &ShapeStyle::zigzagRidges, 1.0, 200.0},
    {"zigzagSmooth", QT_TRANSLATE_NOOP("ShapeStyle", "Smooth points"), &ShapeStyle::zigzagSmooth, 0.0, 1.0},
    {"twistAngle", QT_TRANSLATE_NOOP("ShapeStyle", "Twist"), &ShapeStyle::twistAngle, -3600.0, 3600.0},
    {"puckerBloat", QT_TRANSLATE_NOOP("ShapeStyle", "Pucker & Bloat"), &ShapeStyle::puckerBloat, -100.0, 100.0},
};

const KnobField *knobFor(const QString &key)
{
    for (const KnobField &knob : kKnobs)
        if (key == QLatin1String(knob.key))
            return &knob;
    return nullptr;
}

} // namespace

QStringList shapeKeyframeProperties(const ShapeStyle &style)
{
    QStringList out;
    for (const KnobField &knob : kKnobs)
        out.append(QLatin1String(knob.key));
    out.append(QStringLiteral("points"));
    if (style.kind == ShapeKind::Custom)
        out.append(QLatin1String(kShapePathKey));
    for (const TextShadingLayer &layer : style.layers) {
        for (const QString &field : shadingLayerKeyframeFields(layer))
            out.append(QStringLiteral("layer.%1.%2").arg(layer.id, field));
    }
    return out;
}

QString shapeKeyframeCanonicalKey(const QString &key, const ShapeStyle &style)
{
    if (knobFor(key) || key == QLatin1String("points") || key == QLatin1String(kShapePathKey))
        return key;
    LayerKeyPath path;
    if (!parseLayerKey(key, &path))
        return {};
    const TextShadingLayer *layer = findTextLayer(style.layers, path.layerId);
    if (!layer)
        return {};
    double probe = 0.0;
    return shadingLayerScalar(*layer, path.field, &probe) ? key : QString();
}

QString shapeKeyframeLabel(const QString &key, const ShapeStyle &style)
{
    if (const KnobField *knob = knobFor(key))
        return QCoreApplication::translate("ShapeStyle", knob->label);
    if (key == QLatin1String("points"))
        return QCoreApplication::translate("ShapeStyle", "Points");
    if (key == QLatin1String(kShapePathKey))
        return QCoreApplication::translate("ShapeStyle", "Path");
    return shadingLayerKeyframeLabel(style.layers, key);
}

bool shapeStyleScalar(const ShapeStyle &style, const QString &key, double *out)
{
    if (const KnobField *knob = knobFor(key)) {
        *out = style.*(knob->field);
        return true;
    }
    if (key == QLatin1String("points")) {
        *out = style.points;
        return true;
    }
    LayerKeyPath path;
    if (!parseLayerKey(key, &path))
        return false;
    const TextShadingLayer *layer = findTextLayer(style.layers, path.layerId);
    return layer && shadingLayerScalar(*layer, path.field, out);
}

bool setShapeStyleScalar(ShapeStyle &style, const QString &key, double value)
{
    if (const KnobField *knob = knobFor(key)) {
        style.*(knob->field) = qBound(knob->min, value, knob->max);
        return true;
    }
    if (key == QLatin1String("points")) {
        style.points = qBound(3, qRound(value), 60);
        return true;
    }
    LayerKeyPath path;
    if (!parseLayerKey(key, &path))
        return false;
    TextShadingLayer *layer = findTextLayer(style.layers, path.layerId);
    return layer && setShadingLayerScalar(*layer, path.field, value);
}

bool ShapeStyle::isAnimated() const
{
    for (auto it = keyframes.constBegin(); it != keyframes.constEnd(); ++it) {
        if (!it->isEmpty() && it->enabled())
            return true;
    }
    return std::any_of(parts.begin(), parts.end(), [](const ShapePart &part) { return part.isAnimated(); });
}

ShapeStyle ShapeStyle::resolvedAt(TimeUs clipTimeUs) const
{
    ShapeStyle out = *this;
    for (auto it = keyframes.constBegin(); it != keyframes.constEnd(); ++it) {
        if (it.key() == QLatin1String(kShapePathKey))
            continue;
        if (!it->isEmpty())
            setShapeStyleScalar(out, it.key(), it->evaluateAt(clipTimeUs));
    }
    if (kind == ShapeKind::Custom)
        out.customPath = shapePathAt(*this, clipTimeUs);
    for (ShapePart &part : out.parts)
        part = part.resolvedAt(clipTimeUs);
    return out;
}

QString shapePathAt(const ShapeStyle &style, TimeUs clipTimeUs)
{
    const auto it = style.keyframes.constFind(QLatin1String(kShapePathKey));
    if (it == style.keyframes.constEnd() || it->isEmpty() || style.pathShapes.isEmpty())
        return style.customPath;
    const QMap<TimeUs, Keyframe<double>> &keys = it->keyframes();
    const auto outline = [&style](double index) {
        const int i = qRound(index);
        return i >= 0 && i < style.pathShapes.size() ? style.pathShapes.at(i) : style.customPath;
    };
    // Switched off: the first key's outline throughout, as every other property does.
    if (!it->enabled() || clipTimeUs <= keys.firstKey())
        return outline(keys.first().value);
    if (clipTimeUs >= keys.lastKey())
        return outline(keys.last().value);
    auto next = keys.upperBound(clipTimeUs);
    auto prev = std::prev(next);
    const double v0 = prev->value;
    const double v1 = next->value;
    if (prev->hold || qFuzzyCompare(v0 + 1.0, v1 + 1.0))
        return outline(v0);
    const double t = qBound(0.0, (it->evaluateAt(clipTimeUs) - v0) / (v1 - v0), 1.0);
    return morphSvgPaths(outline(v0), outline(v1), t);
}

void setShapePathAt(ShapeStyle &style, TimeUs clipTimeUs, const QString &svg, TimeUs toleranceUs)
{
    auto it = style.keyframes.find(QLatin1String(kShapePathKey));
    if (it == style.keyframes.end() || it->isEmpty()) {
        style.customPath = svg;
        return;
    }
    const TimeUs near = it->nearestKeyframe(clipTimeUs, toleranceUs);
    if (near >= 0) {
        const int index = qRound(it->keyframes().value(near).value);
        if (index >= 0 && index < style.pathShapes.size()) {
            style.pathShapes[index] = svg;
            return;
        }
    }
    style.pathShapes.append(svg);
    it->setKeyframe(clipTimeUs, double(style.pathShapes.size() - 1));
    it->setStopwatch(true);
}

void setShapePathAnimated(ShapeStyle &style, bool on, TimeUs clipTimeUs)
{
    if (on) {
        if (style.keyframes.contains(QLatin1String(kShapePathKey))
            && !style.keyframes.value(QLatin1String(kShapePathKey)).isEmpty())
            return;
        style.pathShapes = {style.customPath};
        KeyframeTrack<double> track;
        track.setKeyframe(qMax<TimeUs>(0, clipTimeUs), 0.0);
        track.setStopwatch(true);
        style.keyframes.insert(QLatin1String(kShapePathKey), track);
        return;
    }
    style.customPath = shapePathAt(style, clipTimeUs);
    style.keyframes.remove(QLatin1String(kShapePathKey));
    style.pathShapes.clear();
}

quint64 shapeStyleHash(const ShapeStyle &style)
{
    return qHashMulti(0, static_cast<int>(style.kind), textLayersHash(style.layers), style.cornerRadius, style.points,
                      style.innerRatio, style.headSize, style.thickness, style.tailX, style.tailSize,
                      style.customPath, style.customEvenOdd)
           ^ qHashMulti(1, style.trimStart, style.trimEnd, style.trimOffset, style.trimSegments, style.trimReverse, style.repeatCopies, style.repeatOffset,
                        style.repeatX, style.repeatY, style.repeatScale, style.repeatRotation,
                        style.repeatStartOpacity, style.repeatEndOpacity)
           ^ qHashMulti(2, style.wiggleSize, style.wiggleDetail, style.wiggleSpeed, style.wiggleSeed)
           ^ qHashMulti(3, style.mergeMode, style.offsetPath, style.zigzagSize, style.zigzagRidges,
                        style.zigzagSmooth, style.twistAngle, style.puckerBloat)
           ^ qHash(style.pathShapes) ^ shapePartsHash(style);
}

bool shapeTimeDrivenPaint(const ShapeStyle &style)
{
    for (const ShapePart &part : style.parts) {
        if (part.group) {
            ShapeStyle holder;
            holder.layers.clear();
            holder.parts = part.children;
            if (shapeTimeDrivenPaint(holder))
                return true;
        } else if (shapeTimeDrivenPaint(part.shape)) {
            return true;
        }
    }
    // A wiggle that moves redraws every frame.
    if (style.hasWiggle() && style.wiggleSpeed > 0.0)
        return true;
    for (const TextShadingLayer &layer : style.layers) {
        if (!layer.enabled)
            continue;
        if (layer.paint.kind == TextPaintKind::Gradient && !qFuzzyIsNull(layer.paint.gradient.offsetSpeed))
            return true;
        if (layer.paint.kind == TextPaintKind::Effect) {
            const TextEffectSpec *spec = textShaderEffectSpec(layer.paint.effect.id);
            if (spec && spec->timeDriven)
                return true;
        }
    }
    return false;
}

// ---------------------------------------------------------------------------------------------
// JSON

QJsonObject shapeStyleToJson(const ShapeStyle &s)
{
    QJsonArray layers;
    for (const TextShadingLayer &layer : s.layers)
        layers.append(textShadingLayerToJson(layer));
    QJsonObject o{
        {QStringLiteral("kind"), shapeKindToString(s.kind)},
        {QStringLiteral("layers"), layers},
        {QStringLiteral("cornerRadius"), s.cornerRadius},
        {QStringLiteral("points"), s.points},
        {QStringLiteral("innerRatio"), s.innerRatio},
        {QStringLiteral("headSize"), s.headSize},
        {QStringLiteral("thickness"), s.thickness},
        {QStringLiteral("tailX"), s.tailX},
        {QStringLiteral("tailSize"), s.tailSize},
    };
    // The shape operators (0.26) are written only away from their defaults, so a shape without
    // them saves as it always did.
    {
        const ShapeStyle defaults;
        for (const KnobField &knob : kKnobs) {
            const double value = s.*(knob.field);
            if (value != defaults.*(knob.field) && !o.contains(QLatin1String(knob.key)))
                o.insert(QLatin1String(knob.key), value);
        }
    }
    if (s.kind == ShapeKind::Custom) {
        o.insert(QStringLiteral("customPath"), s.customPath);
        if (s.customEvenOdd)
            o.insert(QStringLiteral("customEvenOdd"), true);
    }
    if (!s.pathShapes.isEmpty())
        o.insert(QStringLiteral("pathShapes"), QJsonArray::fromStringList(s.pathShapes));
    QJsonObject keyframesJson;
    for (auto it = s.keyframes.constBegin(); it != s.keyframes.constEnd(); ++it) {
        if (!it->isEmpty())
            keyframesJson.insert(it.key(), keyframesToJson(it.value()));
    }
    if (!keyframesJson.isEmpty())
        o.insert(QStringLiteral("keyframes"), keyframesJson);
    // Contents (0.28): written only when the layer has parts, so a plain shape saves as before.
    if (s.hasParts()) {
        QJsonArray parts;
        for (const ShapePart &part : s.parts)
            parts.append(shapePartToJson(part));
        o.insert(QStringLiteral("parts"), parts);
        o.insert(QStringLiteral("partsRef"), QJsonArray{s.partsRefWidth, s.partsRefHeight});
    }
    return o;
}

namespace {

// The flat look projects before format 8 wrote: one fill (none / solid / two-stop linear or
// radial gradient) under one stroke. Disabled layers are still created so toggling one back on
// restores the old colour or width. The old stroke was inset by half its width so it stayed
// inside the layout rect, which is what Inside reproduces.
QList<TextShadingLayer> legacyShapeLayersFromJson(const QJsonObject &o)
{
    const auto color = [&](const char *key, const QColor &fallback) {
        return QColor(o.value(QLatin1String(key)).toString(fallback.name(QColor::HexArgb)));
    };
    const QColor fill = color("fill", QColor(0, 180, 255));
    const QColor secondary = color("fillSecondary", QColor(122, 0, 255));
    const QString fillKind = o.value(QStringLiteral("fillKind")).toString(QStringLiteral("solid"));
    const QString strokeStyle = o.value(QStringLiteral("strokeStyle")).toString(QStringLiteral("solid"));

    QList<TextShadingLayer> layers = defaultShapeLayers(fill, secondary, color("stroke", Qt::white),
                                                        o.value(QStringLiteral("strokeWidth")).toDouble(4.0));
    TextShadingLayer &fillLayer = layers[0];
    TextShadingLayer &strokeLayer_ = layers[1];
    fillLayer.paint.gradient.angle = o.value(QStringLiteral("gradientAngle")).toDouble(90.0);
    if (fillKind == QLatin1String("none")) {
        fillLayer.enabled = false;
    } else if (fillKind == QLatin1String("linear") || fillKind == QLatin1String("radial")) {
        fillLayer.paint.kind = TextPaintKind::Gradient;
        fillLayer.paint.gradient.kind = fillKind == QLatin1String("radial") ? TextGradientKind::Radial
                                                                            : TextGradientKind::Linear;
    }
    if (strokeStyle == QLatin1String("none"))
        strokeLayer_.enabled = false;
    else
        strokeLayer_.dash = strokeDashFromString(strokeStyle);
    return layers;
}

} // namespace

ShapeStyle shapeStyleFromJson(const QJsonObject &o)
{
    ShapeStyle s;
    if (o.isEmpty())
        return s;
    s.kind = shapeKindFromString(o.value(QStringLiteral("kind")).toString());
    if (o.contains(QStringLiteral("layers"))) {
        s.layers.clear();
        for (const QJsonValue &v : o.value(QStringLiteral("layers")).toArray())
            s.layers.append(textShadingLayerFromJson(v.toObject()));
        for (TextShadingLayer &layer : s.layers) {
            if (layer.id.isEmpty())
                layer.id = mintTextLayerId(s.layers);
        }
    } else {
        s.layers = legacyShapeLayersFromJson(o);
    }
    // Geometry knobs default to the struct value, so a project saved before shapes gained them
    // still loads.
    s.cornerRadius = o.value(QStringLiteral("cornerRadius")).toDouble(s.cornerRadius);
    s.points = o.value(QStringLiteral("points")).toInt(s.points);
    s.innerRatio = o.value(QStringLiteral("innerRatio")).toDouble(s.innerRatio);
    s.headSize = o.value(QStringLiteral("headSize")).toDouble(s.headSize);
    s.thickness = o.value(QStringLiteral("thickness")).toDouble(s.thickness);
    s.tailX = o.value(QStringLiteral("tailX")).toDouble(s.tailX);
    s.tailSize = o.value(QStringLiteral("tailSize")).toDouble(s.tailSize);
    for (const KnobField &knob : kKnobs) {
        if (o.contains(QLatin1String(knob.key)))
            s.*(knob.field) = qBound(knob.min, o.value(QLatin1String(knob.key)).toDouble(), knob.max);
    }
    s.customPath = o.value(QStringLiteral("customPath")).toString();
    s.customEvenOdd = o.value(QStringLiteral("customEvenOdd")).toBool(false);
    // A custom kind without an outline would draw nothing; a rectangle is the honest fallback.
    if (s.kind == ShapeKind::Custom && s.customPath.isEmpty())
        s.kind = ShapeKind::Rectangle;
    for (const QJsonValue &v : o.value(QStringLiteral("pathShapes")).toArray())
        s.pathShapes.append(v.toString());
    const QJsonObject keyframesJson = o.value(QStringLiteral("keyframes")).toObject();
    for (auto it = keyframesJson.constBegin(); it != keyframesJson.constEnd(); ++it) {
        const QString canonical = shapeKeyframeCanonicalKey(it.key(), s);
        if (!canonical.isEmpty())
            s.keyframes.insert(canonical, keyframesFromJson(it.value().toObject()));
    }
    for (const QJsonValue &v : o.value(QStringLiteral("parts")).toArray())
        s.parts.push_back(shapePartFromJson(v.toObject()));
    if (s.hasParts()) {
        const QJsonArray ref = o.value(QStringLiteral("partsRef")).toArray();
        s.partsRefWidth = qMax(1.0, ref.at(0).toDouble(100.0));
        s.partsRefHeight = qMax(1.0, ref.at(1).toDouble(100.0));
    }
    return s;
}

// ---------------------------------------------------------------------------------------------
// Contents: parts (0.28)

namespace {

struct PartField
{
    const char *key;
    double ShapePartTransform::*field;
    double min;
    double max;
};

constexpr PartField kPartFields[] = {
    {"anchorX", &ShapePartTransform::anchorX, -100000.0, 100000.0},
    {"anchorY", &ShapePartTransform::anchorY, -100000.0, 100000.0},
    {"x", &ShapePartTransform::x, -100000.0, 100000.0},
    {"y", &ShapePartTransform::y, -100000.0, 100000.0},
    {"scaleX", &ShapePartTransform::scaleX, -10000.0, 10000.0},
    {"scaleY", &ShapePartTransform::scaleY, -10000.0, 10000.0},
    {"skew", &ShapePartTransform::skew, -85.0, 85.0},
    {"skewAxis", &ShapePartTransform::skewAxis, -36000.0, 36000.0},
    {"rotation", &ShapePartTransform::rotation, -360000.0, 360000.0},
    {"opacity", &ShapePartTransform::opacity, 0.0, 100.0},
};

const PartField *partFieldFor(const QString &key)
{
    for (const PartField &f : kPartFields) {
        if (key == QLatin1String(f.key))
            return &f;
    }
    return nullptr;
}

quint64 shapePartHash(const ShapePart &part)
{
    const ShapePartTransform &t = part.transform;
    quint64 h = qHashMulti(7, part.id, part.visible, static_cast<int>(part.blend), part.group, part.width, part.height)
                ^ qHashMulti(8, t.anchorX, t.anchorY, t.x, t.y, t.scaleX, t.scaleY, t.skew, t.skewAxis, t.rotation,
                             t.opacity);
    if (part.group) {
        for (const ShapePart &child : part.children)
            h = h * 31 + shapePartHash(child);
    } else {
        h ^= shapeStyleHash(part.shape) * 1099511628211ULL;
    }
    return h;
}

quint64 shapePartsHash(const ShapeStyle &style)
{
    if (!style.hasParts())
        return 0;
    quint64 h = qHashMulti(9, style.partsRefWidth, style.partsRefHeight);
    for (const ShapePart &part : style.parts)
        h = h * 31 + shapePartHash(part);
    return h;
}

void collectPartIds(const std::vector<ShapePart> &parts, QSet<QString> &ids)
{
    for (const ShapePart &part : parts) {
        ids.insert(part.id);
        collectPartIds(part.children, ids);
    }
}

QJsonObject partTransformToJson(const ShapePartTransform &t)
{
    QJsonObject o;
    const ShapePartTransform defaults;
    for (const PartField &f : kPartFields) {
        if (t.*(f.field) != defaults.*(f.field))
            o.insert(QLatin1String(f.key), t.*(f.field));
    }
    return o;
}

} // namespace

bool ShapePart::isAnimated() const
{
    for (auto it = keyframes.constBegin(); it != keyframes.constEnd(); ++it) {
        if (!it->isEmpty() && it->enabled())
            return true;
    }
    if (group)
        return std::any_of(children.begin(), children.end(), [](const ShapePart &c) { return c.isAnimated(); });
    return shape.isAnimated();
}

ShapePart ShapePart::resolvedAt(TimeUs clipTimeUs) const
{
    ShapePart out = *this;
    for (auto it = keyframes.constBegin(); it != keyframes.constEnd(); ++it) {
        if (!it->isEmpty())
            setShapePartScalar(out, it.key(), it->evaluateAt(clipTimeUs));
    }
    out.keyframes.clear();
    if (group) {
        for (ShapePart &child : out.children)
            child = child.resolvedAt(clipTimeUs);
    } else {
        out.shape = shape.resolvedAt(clipTimeUs);
        out.shape.keyframes.clear();
    }
    return out;
}

QStringList shapePartKeyframeFields(const ShapePart &part)
{
    QStringList out;
    for (const PartField &f : kPartFields)
        out.append(QLatin1String(f.key));
    if (!part.group)
        out << QStringLiteral("width") << QStringLiteral("height");
    return out;
}

bool shapePartScalar(const ShapePart &part, const QString &field, double *out)
{
    if (const PartField *f = partFieldFor(field)) {
        *out = part.transform.*(f->field);
        return true;
    }
    if (part.group)
        return false;
    if (field == QLatin1String("width")) {
        *out = part.width;
        return true;
    }
    if (field == QLatin1String("height")) {
        *out = part.height;
        return true;
    }
    return false;
}

bool setShapePartScalar(ShapePart &part, const QString &field, double value)
{
    if (const PartField *f = partFieldFor(field)) {
        part.transform.*(f->field) = qBound(f->min, value, f->max);
        return true;
    }
    if (part.group)
        return false;
    if (field == QLatin1String("width")) {
        part.width = qBound(0.0, value, 100000.0);
        return true;
    }
    if (field == QLatin1String("height")) {
        part.height = qBound(0.0, value, 100000.0);
        return true;
    }
    return false;
}

ShapePart *findShapePart(std::vector<ShapePart> &parts, const QString &id)
{
    for (ShapePart &part : parts) {
        if (part.id == id)
            return &part;
        if (ShapePart *inner = findShapePart(part.children, id))
            return inner;
    }
    return nullptr;
}

const ShapePart *findShapePart(const std::vector<ShapePart> &parts, const QString &id)
{
    return findShapePart(const_cast<std::vector<ShapePart> &>(parts), id);
}

QString mintShapePartId(const ShapeStyle &style)
{
    QSet<QString> used;
    collectPartIds(style.parts, used);
    for (int n = 1;; ++n) {
        const QString id = QStringLiteral("p%1").arg(n);
        if (!used.contains(id))
            return id;
    }
}

ShapeStyle shapeWithParts(const ShapeStyle &style, double boxWidth, double boxHeight, const QString &partName)
{
    if (style.hasParts())
        return style;
    ShapeStyle out = style;
    ShapePart part;
    part.id = QStringLiteral("p1");
    part.name = partName;
    part.width = qMax(1.0, boxWidth);
    part.height = qMax(1.0, boxHeight);
    part.shape = style; // its keys come along: they animate the part as they animated the layer
    out.keyframes.clear();
    out.pathShapes.clear();
    out.parts.push_back(std::move(part));
    out.partsRefWidth = qMax(1.0, boxWidth);
    out.partsRefHeight = qMax(1.0, boxHeight);
    return out;
}

QJsonObject shapePartToJson(const ShapePart &part)
{
    QJsonObject o{
        {QStringLiteral("id"), part.id},
        {QStringLiteral("name"), part.name},
    };
    if (!part.visible)
        o.insert(QStringLiteral("visible"), false);
    if (part.blend != BlendMode::Normal)
        o.insert(QStringLiteral("blend"), blendModeToString(part.blend));
    const QJsonObject transform = partTransformToJson(part.transform);
    if (!transform.isEmpty())
        o.insert(QStringLiteral("transform"), transform);
    if (part.group) {
        o.insert(QStringLiteral("group"), true);
        QJsonArray children;
        for (const ShapePart &child : part.children)
            children.append(shapePartToJson(child));
        o.insert(QStringLiteral("children"), children);
    } else {
        o.insert(QStringLiteral("width"), part.width);
        o.insert(QStringLiteral("height"), part.height);
        o.insert(QStringLiteral("shape"), shapeStyleToJson(part.shape));
    }
    QJsonObject keyframesJson;
    for (auto it = part.keyframes.constBegin(); it != part.keyframes.constEnd(); ++it) {
        if (!it->isEmpty())
            keyframesJson.insert(it.key(), keyframesToJson(it.value()));
    }
    if (!keyframesJson.isEmpty())
        o.insert(QStringLiteral("keyframes"), keyframesJson);
    return o;
}

ShapePart shapePartFromJson(const QJsonObject &o)
{
    ShapePart part;
    part.id = o.value(QStringLiteral("id")).toString();
    part.name = o.value(QStringLiteral("name")).toString();
    part.visible = o.value(QStringLiteral("visible")).toBool(true);
    part.blend = blendModeFromString(o.value(QStringLiteral("blend")).toString());
    const QJsonObject transform = o.value(QStringLiteral("transform")).toObject();
    for (const PartField &f : kPartFields) {
        if (transform.contains(QLatin1String(f.key)))
            part.transform.*(f.field) = qBound(f.min, transform.value(QLatin1String(f.key)).toDouble(), f.max);
    }
    part.group = o.value(QStringLiteral("group")).toBool(false);
    if (part.group) {
        for (const QJsonValue &v : o.value(QStringLiteral("children")).toArray())
            part.children.push_back(shapePartFromJson(v.toObject()));
    } else {
        part.width = qBound(0.0, o.value(QStringLiteral("width")).toDouble(100.0), 100000.0);
        part.height = qBound(0.0, o.value(QStringLiteral("height")).toDouble(100.0), 100000.0);
        part.shape = shapeStyleFromJson(o.value(QStringLiteral("shape")).toObject());
        part.shape.parts.clear(); // a part is one shape; groups hold the nesting
    }
    const QJsonObject keyframesJson = o.value(QStringLiteral("keyframes")).toObject();
    const QStringList fields = shapePartKeyframeFields(part);
    for (auto it = keyframesJson.constBegin(); it != keyframesJson.constEnd(); ++it) {
        if (fields.contains(it.key()))
            part.keyframes.insert(it.key(), keyframesFromJson(it.value().toObject()));
    }
    return part;
}

} // namespace drift
