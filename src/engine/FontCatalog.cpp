#include "FontCatalog.h"

#include "GpuPackageParse.h"

#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QFontDatabase>
#include <QHash>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QMutex>
#include <QMutexLocker>
#include <QRawFont>
#include <QStandardPaths>

#include <algorithm>
#include <cstdlib>
#include <limits>

QList<int> FontFamilyEntry::weights() const
{
    QList<int> out;
    for (const FontFace &face : faces) {
        if (!face.italic && !out.contains(face.weight))
            out.append(face.weight);
    }
    std::sort(out.begin(), out.end());
    return out;
}

bool FontFamilyEntry::hasItalic() const
{
    for (const FontFace &face : faces) {
        if (face.italic)
            return true;
    }
    return false;
}

namespace {

QList<FontFamilyEntry> g_catalog;
QHash<QString, int> g_familyIndex; // lowercased family name -> index
QMutex g_mutex;
bool g_initialized = false;

FontFamilyEntry loadPackage(const QString &packageDir)
{
    FontFamilyEntry entry;

    QFile file(QDir(packageDir).filePath(QStringLiteral("family.json")));
    if (!file.open(QIODevice::ReadOnly))
        return entry;

    const QJsonObject root = QJsonDocument::fromJson(file.readAll()).object();
    if (root.isEmpty())
        return entry;

    entry.id = root.value(QStringLiteral("id")).toString();
    entry.family = root.value(QStringLiteral("family")).toString();
    entry.category = root.value(QStringLiteral("category")).toString();
    entry.license = root.value(QStringLiteral("license")).toString();
    entry.order = root.value(QStringLiteral("order")).toInt();
    entry.packageDir = packageDir;
    if (entry.family.isEmpty())
        return {};

    const QJsonArray faces = root.value(QStringLiteral("faces")).toArray();
    for (const QJsonValue &value : faces) {
        const QJsonObject object = value.toObject();
        const QString relative = object.value(QStringLiteral("file")).toString();
        const QString absolute = QDir(packageDir).filePath(relative);
        if (relative.isEmpty() || !QFile::exists(absolute))
            continue;

        const int id = QFontDatabase::addApplicationFont(absolute);
        if (id < 0) {
            qWarning("FontCatalog: Qt rejected %s", qPrintable(absolute));
            continue;
        }
        if (entry.qtFamily.isEmpty())
            entry.qtFamily = QFontDatabase::applicationFontFamilies(id).value(0);

        FontFace face;
        face.weight = qBound(100, object.value(QStringLiteral("weight")).toInt(400), 900);
        face.italic = object.value(QStringLiteral("italic")).toBool();
        face.styleName = object.value(QStringLiteral("styleName")).toString();
        face.file = absolute;
        entry.faces.append(face);
    }

    if (entry.faces.isEmpty() || entry.qtFamily.isEmpty())
        return {};

    std::sort(entry.faces.begin(), entry.faces.end(), [](const FontFace &a, const FontFace &b) {
        if (a.weight != b.weight)
            return a.weight < b.weight;
        return !a.italic && b.italic;
    });
    return entry;
}

void rebuildLocked(const QStringList &packageRoots)
{
    g_catalog.clear();
    g_familyIndex.clear();

    const QStringList roots = packageRoots.isEmpty()
        ? GpuPackageParse::defaultSearchPaths(QStringLiteral("DRIFT_FONTS_DIR"),
                                              QStringLiteral("fonts"), QStringLiteral("fonts"))
        : packageRoots;

    for (const QString &root : roots) {
        QDir dir(root);
        if (!dir.exists())
            continue;
        const QStringList packages = dir.entryList(QDir::Dirs | QDir::NoDotAndDotDot, QDir::Name);
        for (const QString &package : packages) {
            FontFamilyEntry entry = loadPackage(dir.filePath(package));
            if (entry.family.isEmpty())
                continue;
            // First root wins, so DRIFT_FONTS_DIR can shadow the shipped bundle.
            if (g_familyIndex.contains(entry.family.toLower()))
                continue;
            g_familyIndex.insert(entry.family.toLower(), g_catalog.size());
            g_catalog.append(entry);
        }
    }

    // Categories in fontCategories() order, then any the app has no label for.
    QHash<QString, int> rank;
    const QList<QPair<QString, QString>> categories = fontCategories();
    for (int i = 0; i < categories.size(); ++i)
        rank.insert(categories.at(i).first, i);
    std::sort(g_catalog.begin(), g_catalog.end(), [&rank](const FontFamilyEntry &a, const FontFamilyEntry &b) {
        const int ra = rank.value(a.category, int(rank.size()));
        const int rb = rank.value(b.category, int(rank.size()));
        if (ra != rb)
            return ra < rb;
        if (a.category != b.category)
            return a.category < b.category;
        if (a.order != b.order)
            return a.order < b.order;
        return a.family < b.family;
    });

    g_familyIndex.clear();
    for (int i = 0; i < g_catalog.size(); ++i)
        g_familyIndex.insert(g_catalog.at(i).family.toLower(), i);

    g_initialized = true;
}

void ensureLocked()
{
    if (!g_initialized)
        rebuildLocked({});
}

// CSS-style nearest weight: at or above 400 prefer the next heavier face, below 400 the next
// lighter one, and fall back to whatever is closest when the family runs out in that direction.
const FontFace *nearestFace(const FontFamilyEntry &entry, int weight, bool italic)
{
    const FontFace *best = nullptr;
    int bestScore = std::numeric_limits<int>::max();

    for (const FontFace &face : entry.faces) {
        if (face.italic != italic)
            continue;
        const int distance = std::abs(face.weight - weight);
        const bool wrongSide = weight >= 400 ? face.weight < weight : face.weight > weight;
        const int score = distance + (wrongSide ? 1000 : 0);
        if (score < bestScore) {
            bestScore = score;
            best = &face;
        }
    }
    return best;
}

} // namespace

void reloadFontCatalog(const QStringList &packageRoots)
{
    QMutexLocker lock(&g_mutex);
    rebuildLocked(packageRoots);
}

const QList<FontFamilyEntry> &fontCatalog()
{
    QMutexLocker lock(&g_mutex);
    ensureLocked();
    return g_catalog;
}

const FontFamilyEntry *fontFamilyForName(const QString &family)
{
    QMutexLocker lock(&g_mutex);
    ensureLocked();
    const auto it = g_familyIndex.constFind(family.toLower());
    if (it == g_familyIndex.constEnd())
        return nullptr;
    return &g_catalog.at(it.value());
}

QList<QPair<QString, QString>> fontCategories()
{
    // The font packs' categories, then the older bundle's four, which the packs replaced.
    return {
        {QStringLiteral("mine"), QCoreApplication::translate("FontCatalog", "My fonts")},
        {QStringLiteral("sans"), QCoreApplication::translate("FontCatalog", "Clean")},
        {QStringLiteral("display"), QCoreApplication::translate("FontCatalog", "Bold & impact")},
        {QStringLiteral("serif"), QCoreApplication::translate("FontCatalog", "Elegant")},
        {QStringLiteral("handwriting"), QCoreApplication::translate("FontCatalog", "Handwritten")},
        {QStringLiteral("fun"), QCoreApplication::translate("FontCatalog", "Fun")},
        {QStringLiteral("retro"), QCoreApplication::translate("FontCatalog", "Retro")},
        {QStringLiteral("impact"), QCoreApplication::translate("FontCatalog", "High-Impact & Bold")},
        {QStringLiteral("clean"), QCoreApplication::translate("FontCatalog", "Clean & Minimal")},
        {QStringLiteral("editorial"), QCoreApplication::translate("FontCatalog", "Classy & Editorial")},
        {QStringLiteral("playful"), QCoreApplication::translate("FontCatalog", "Creative & Playful")},
    };
}

QString userFontsDir()
{
    const QString appData = QStandardPaths::writableLocation(QStandardPaths::AppDataLocation);
    return appData.isEmpty() ? QString() : QDir(appData).filePath(QStringLiteral("fonts"));
}

QStringList importUserFonts(const QStringList &files, QString *error)
{
    const QString root = userFontsDir();
    if (root.isEmpty()) {
        if (error)
            *error = QStringLiteral("no writable data folder");
        return {};
    }
    QStringList families;
    QStringList rejected;
    for (const QString &path : files) {
        const QRawFont raw(path, 12);
        if (!raw.isValid() || raw.familyName().isEmpty()) {
            rejected.append(QFileInfo(path).fileName());
            continue;
        }
        const QString family = raw.familyName();
        QString slug;
        for (const QChar c : family.toLower())
            if (c.isLetterOrNumber())
                slug.append(c);
        // One folder per family, in the same family.json layout the font packs use, so the
        // catalog reads an imported font exactly like an installed one.
        const QDir dir(QDir(root).filePath(QStringLiteral("mine-") + (slug.isEmpty() ? QStringLiteral("font") : slug)));
        if (!QDir().mkpath(dir.path())) {
            rejected.append(QFileInfo(path).fileName());
            continue;
        }
        const QString fileName = QFileInfo(path).fileName();
        const QString dest = dir.filePath(fileName);
        if (QFileInfo(dest) != QFileInfo(path)) {
            QFile::remove(dest);
            if (!QFile::copy(path, dest)) {
                rejected.append(fileName);
                continue;
            }
        }

        QFile jsonFile(dir.filePath(QStringLiteral("family.json")));
        QJsonObject json;
        if (jsonFile.open(QIODevice::ReadOnly)) {
            json = QJsonDocument::fromJson(jsonFile.readAll()).object();
            jsonFile.close();
        }
        QJsonArray faces;
        for (const QJsonValue &face : json.value(QStringLiteral("faces")).toArray())
            if (face.toObject().value(QStringLiteral("file")).toString() != fileName)
                faces.append(face);
        faces.append(QJsonObject{
            {QStringLiteral("file"), fileName},
            {QStringLiteral("weight"), qBound(100, int(raw.weight()), 900)},
            {QStringLiteral("italic"), raw.style() != QFont::StyleNormal},
            {QStringLiteral("styleName"), raw.styleName()},
        });
        json.insert(QStringLiteral("id"), QStringLiteral("mine-") + slug);
        json.insert(QStringLiteral("family"), family);
        json.insert(QStringLiteral("category"), QStringLiteral("mine"));
        json.insert(QStringLiteral("license"), QStringLiteral("user"));
        json.insert(QStringLiteral("faces"), faces);
        if (!jsonFile.open(QIODevice::WriteOnly | QIODevice::Truncate)) {
            rejected.append(fileName);
            continue;
        }
        jsonFile.write(QJsonDocument(json).toJson());
        if (!families.contains(family))
            families.append(family);
    }
    if (error && !rejected.isEmpty())
        *error = rejected.join(QStringLiteral(", "));
    if (!families.isEmpty())
        reloadFontCatalog();
    return families;
}

QFont fontForStyle(const drift::TextStyle &style, int pixelSizePx)
{
    const int px = qMax(4, pixelSizePx);
    const FontFamilyEntry *entry = fontFamilyForName(style.fontFamily);

    if (!entry) { // not in the bundle — let the system font database resolve it
        QFont font(style.fontFamily);
        font.setPixelSize(px);
        font.setWeight(QFont::Weight(qBound(100, style.fontWeight, 900)));
        font.setItalic(style.italic);
        return font;
    }

    const FontFace *face = nearestFace(*entry, style.fontWeight, style.italic);
    if (!face && style.italic) // family ships no italic; use the upright face
        face = nearestFace(*entry, style.fontWeight, false);
    if (!face)
        face = &entry->faces.first();

    QFont font(entry->qtFamily);
    // usWeightClass is unreliable in these files (Montserrat/Inter Thin both report 250), so the
    // style name is what actually pins the face; the weight is a hint for backends that ignore it.
    font.setStyleName(face->styleName);
    font.setWeight(QFont::Weight(face->weight));
    font.setItalic(face->italic);
    font.setPixelSize(px);
    return font;
}
