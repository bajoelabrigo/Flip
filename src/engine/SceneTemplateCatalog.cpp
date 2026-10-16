#include "SceneTemplateCatalog.h"

#include "GpuPackageParse.h"
#include "core/ZipArchive.h"

#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLocale>
#include <QRegularExpression>
#include <QSet>
#include <QStandardPaths>

#include <algorithm>
#include <optional>

namespace {

QList<SceneTemplateEntry> g_catalog;
bool g_loaded = false;

QString labelForCategory(const QString &slug)
{
    if (slug == QLatin1String("mine"))
        return QCoreApplication::translate("SceneTemplateCatalog", "My templates");
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
    if (slug == QLatin1String("seasonal"))
        return QCoreApplication::translate("SceneTemplateCatalog", "Special dates");
    if (slug == QLatin1String("business"))
        return QCoreApplication::translate("SceneTemplateCatalog", "Business");
    if (slug == QLatin1String("slideshow"))
        return QCoreApplication::translate("SceneTemplateCatalog", "Photo slideshows");
    if (slug == QLatin1String("lowerthird"))
        return QCoreApplication::translate("SceneTemplateCatalog", "Lower thirds");
    if (slug == QLatin1String("transition"))
        return QCoreApplication::translate("SceneTemplateCatalog", "Transitions and separators");
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
    entry.origin = root.value(QStringLiteral("origin")).toString();
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

QString userSceneTemplatesDir()
{
    const QString appData = QStandardPaths::writableLocation(QStandardPaths::AppDataLocation);
    return appData.isEmpty() ? QString() : QDir(appData).filePath(QStringLiteral("scene-templates"));
}

QStringList defaultSceneTemplateSearchPaths()
{
    QStringList roots = GpuPackageParse::defaultSearchPaths(QStringLiteral("DRIFT_SCENE_TEMPLATES_DIR"),
                                                            QStringLiteral("scene-templates"),
                                                            QStringLiteral("scene-templates"));
    // What came from Stock goes ahead of the bundled packages: an update has to win.
    const QString user = userSceneTemplatesDir();
    if (!user.isEmpty()) {
        roots.removeAll(user);
        roots.insert(qEnvironmentVariableIsSet("DRIFT_SCENE_TEMPLATES_DIR") ? 1 : 0, user);
    }
    return roots;
}

QString installSceneTemplatePackage(const QString &zipPath, QString *error)
{
    const auto fail = [error](const QString &message) {
        if (error)
            *error = message;
        return QString();
    };
    QFile zip(zipPath);
    if (!zip.open(QIODevice::ReadOnly))
        return fail(zip.errorString());
    QString zipError;
    const QList<drift::zip::Entry> entries = drift::zip::readEntries(zip, &zipError);
    if (entries.isEmpty())
        return fail(zipError.isEmpty() ? QStringLiteral("the package is empty") : zipError);

    // template.json at the root, or inside a single top folder.
    QString prefix;
    bool found = false;
    for (const drift::zip::Entry &entry : entries) {
        if (entry.isDir)
            continue;
        if (entry.path == QLatin1String("template.json")) {
            prefix.clear();
            found = true;
            break;
        }
        if (entry.path.endsWith(QLatin1String("/template.json")) && entry.path.count(QLatin1Char('/')) == 1) {
            prefix = entry.path.left(entry.path.size() - int(qstrlen("template.json")));
            found = true;
        }
    }
    if (!found)
        return fail(QStringLiteral("not a template package (no template.json)"));

    QByteArray manifestBytes;
    for (const drift::zip::Entry &entry : entries) {
        if (entry.path == prefix + QLatin1String("template.json")) {
            drift::zip::extractEntry(zip, entry, manifestBytes);
            break;
        }
    }
    const QString id = QJsonDocument::fromJson(manifestBytes).object().value(QStringLiteral("id")).toString().trimmed();
    static const QRegularExpression safeId(QStringLiteral("^[a-z0-9][a-z0-9._-]{0,63}$"));
    if (!safeId.match(id).hasMatch())
        return fail(QStringLiteral("the package has no usable id"));

    const QString root = userSceneTemplatesDir();
    if (root.isEmpty() || !QDir().mkpath(root))
        return fail(QStringLiteral("cannot create the templates folder"));
    const QString dest = QDir(root).filePath(id);
    const QString staging = dest + QStringLiteral(".partial");
    QDir(staging).removeRecursively();
    for (const drift::zip::Entry &entry : entries) {
        if (entry.isDir || !entry.path.startsWith(prefix))
            continue;
        QByteArray bytes;
        if (!drift::zip::extractEntry(zip, entry, bytes)) {
            QDir(staging).removeRecursively();
            return fail(QStringLiteral("cannot extract %1").arg(entry.path));
        }
        const QString target = QDir(staging).filePath(entry.path.mid(prefix.size()));
        QFile out(target);
        if (!QDir().mkpath(QFileInfo(target).absolutePath()) || !out.open(QIODevice::WriteOnly | QIODevice::Truncate)
            || out.write(bytes) != bytes.size()) {
            QDir(staging).removeRecursively();
            return fail(QStringLiteral("cannot write %1").arg(target));
        }
    }
    QString manifestError;
    if (!loadManifest(staging, &manifestError)) {
        QDir(staging).removeRecursively();
        return fail(manifestError);
    }
    QDir(dest).removeRecursively();
    if (!QDir().rename(staging, dest)) {
        QDir(staging).removeRecursively();
        return fail(QStringLiteral("cannot move the template into place"));
    }
    reloadSceneTemplateCatalog();
    return id;
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
