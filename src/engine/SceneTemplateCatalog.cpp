#include "SceneTemplateCatalog.h"

#include "GpuPackageParse.h"

#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLocale>
#include <QSet>

#include <algorithm>
#include <optional>

namespace {

QList<SceneTemplateEntry> g_catalog;
bool g_loaded = false;

QString labelForCategory(const QString &slug)
{
    if (slug == QLatin1String("reels"))
        return QCoreApplication::translate("SceneTemplateCatalog", "Photo reels");
    if (slug == QLatin1String("intro"))
        return QCoreApplication::translate("SceneTemplateCatalog", "Intros and titles");
    if (slug == QLatin1String("text"))
        return QCoreApplication::translate("SceneTemplateCatalog", "Text");
    if (slug == QLatin1String("collage"))
        return QCoreApplication::translate("SceneTemplateCatalog", "Collages");
    if (slug == QLatin1String("beforeafter"))
        return QCoreApplication::translate("SceneTemplateCatalog", "Before and after");
    if (slug == QLatin1String("product"))
        return QCoreApplication::translate("SceneTemplateCatalog", "Products");
    if (slug == QLatin1String("celebration"))
        return QCoreApplication::translate("SceneTemplateCatalog", "Celebrations");
    if (slug == QLatin1String("countdown"))
        return QCoreApplication::translate("SceneTemplateCatalog", "Countdowns");
    if (slug == QLatin1String("outro"))
        return QCoreApplication::translate("SceneTemplateCatalog", "Endings");
    if (slug.isEmpty())
        return QCoreApplication::translate("SceneTemplateCatalog", "Other");
    QString label = slug;
    label[0] = label.at(0).toUpper();
    return label;
}

// The package's own name in the UI language: "es_CO", then "es", then displayName.
QString localizedName(const QJsonObject &root)
{
    const QJsonObject names = root.value(QStringLiteral("names")).toObject();
    const QString locale = QLocale().name();
    for (const QString &key : {locale, locale.section(QLatin1Char('_'), 0, 0)}) {
        const QString name = names.value(key).toString().trimmed();
        if (!name.isEmpty())
            return name;
    }
    return root.value(QStringLiteral("displayName")).toString().trimmed();
}

std::optional<SceneTemplateEntry> loadManifest(const QString &packageDir, QString *errorOut)
{
    QFile file(QDir(packageDir).filePath(QStringLiteral("template.json")));
    if (!file.open(QIODevice::ReadOnly)) {
        *errorOut = QStringLiteral("cannot read template.json");
        return std::nullopt;
    }
    QJsonParseError parseError;
    const QJsonDocument doc = QJsonDocument::fromJson(file.readAll(), &parseError);
    if (!doc.isObject()) {
        *errorOut = parseError.errorString();
        return std::nullopt;
    }
    const QJsonObject root = doc.object();

    SceneTemplateEntry entry;
    entry.id = root.value(QStringLiteral("id")).toString().trimmed();
    if (entry.id.isEmpty()) {
        *errorOut = QStringLiteral("missing id");
        return std::nullopt;
    }
    entry.projectPath = QDir(packageDir).filePath(QStringLiteral("project.json"));
    if (!QFileInfo::exists(entry.projectPath)) {
        *errorOut = QStringLiteral("missing project.json");
        return std::nullopt;
    }
    entry.displayName = localizedName(root);
    if (entry.displayName.isEmpty())
        entry.displayName = entry.id;
    entry.category = root.value(QStringLiteral("category")).toString().trimmed();
    entry.order = root.value(QStringLiteral("order")).toInt(0);
    entry.width = qMax(16, root.value(QStringLiteral("width")).toInt(1080));
    entry.height = qMax(16, root.value(QStringLiteral("height")).toInt(1920));
    entry.durationUs = drift::secondsToUs(qMax(0.0, root.value(QStringLiteral("durationSec")).toDouble()));
    entry.slotCount = qMax(0, root.value(QStringLiteral("slots")).toInt());
    entry.textCount = qMax(0, root.value(QStringLiteral("texts")).toInt());
    entry.premium = root.value(QStringLiteral("premium")).toBool(false);
    for (const QJsonValue &tag : root.value(QStringLiteral("tags")).toArray())
        entry.tags.append(tag.toString());
    entry.packageDir = packageDir;
    entry.thumbnailPath = GpuPackageParse::resolvePackageAsset(packageDir, QStringLiteral("thumbnail.png"));
    const QString preview = QDir(packageDir).filePath(QStringLiteral("preview.mp4"));
    if (QFileInfo::exists(preview))
        entry.previewPath = preview;
    return entry;
}

QList<SceneTemplateEntry> scanDirectories(const QStringList &rootDirs)
{
    QList<SceneTemplateEntry> loaded;
    QSet<QString> seenIds;
    for (const QString &root : rootDirs) {
        if (root.isEmpty())
            continue;
        const QDir dir(root);
        if (!dir.exists())
            continue;
        for (const QFileInfo &info : dir.entryInfoList(QDir::Dirs | QDir::NoDotAndDotDot, QDir::Name)) {
            const QString packageDir = info.absoluteFilePath();
            if (!QFileInfo::exists(QDir(packageDir).filePath(QStringLiteral("template.json"))))
                continue;
            QString error;
            const std::optional<SceneTemplateEntry> entry = loadManifest(packageDir, &error);
            if (!entry) {
                qWarning("SceneTemplateCatalog: skip %s: %s", qPrintable(packageDir), qPrintable(error));
                continue;
            }
            // An installed copy (Stock, addons) comes first in the roots and wins.
            if (seenIds.contains(entry->id))
                continue;
            seenIds.insert(entry->id);
            loaded.append(*entry);
        }
    }
    std::sort(loaded.begin(), loaded.end(), [](const SceneTemplateEntry &a, const SceneTemplateEntry &b) {
        if (a.order != b.order)
            return a.order < b.order;
        return a.id < b.id;
    });
    return loaded;
}

void ensureLoaded()
{
    if (!g_loaded)
        reloadSceneTemplateCatalog();
}

} // namespace

QStringList defaultSceneTemplateSearchPaths()
{
    return GpuPackageParse::defaultSearchPaths(QStringLiteral("DRIFT_SCENE_TEMPLATES_DIR"),
                                               QStringLiteral("scene-templates"),
                                               QStringLiteral("scene-templates"));
}

void reloadSceneTemplateCatalog(const QStringList &packageRoots)
{
    g_catalog = scanDirectories(packageRoots.isEmpty() ? defaultSceneTemplateSearchPaths() : packageRoots);
    g_loaded = true;
}

const QList<SceneTemplateEntry> &sceneTemplateCatalog()
{
    ensureLoaded();
    return g_catalog;
}

const SceneTemplateEntry *sceneTemplateForId(const QString &id)
{
    ensureLoaded();
    for (const SceneTemplateEntry &entry : g_catalog) {
        if (entry.id == id)
            return &entry;
    }
    return nullptr;
}

QList<QPair<QString, QString>> sceneTemplateCategories()
{
    ensureLoaded();
    QList<QPair<QString, QString>> categories;
    QSet<QString> seen;
    for (const SceneTemplateEntry &entry : g_catalog) {
        if (seen.contains(entry.category))
            continue;
        seen.insert(entry.category);
        categories.append({entry.category, labelForCategory(entry.category)});
    }
    return categories;
}

QString sceneTemplateCategoryLabel(const QString &categoryId)
{
    return labelForCategory(categoryId);
}
