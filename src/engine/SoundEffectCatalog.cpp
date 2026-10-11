#include "SoundEffectCatalog.h"

#include "GpuPackageParse.h"

#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QMutex>
#include <QMutexLocker>

#include <algorithm>

namespace {

struct Pack
{
    QString id;
    int order = 0;
    QList<SoundEffectCategory> categories;
    QList<SoundEffectEntry> sounds;
};

QMutex g_mutex;
QList<Pack> g_packs;
bool g_initialized = false;

bool loadPack(const QString &dir, Pack *out)
{
    QFile file(QDir(dir).filePath(QStringLiteral("pack.json")));
    if (!file.open(QIODevice::ReadOnly))
        return false;
    const QJsonObject root = QJsonDocument::fromJson(file.readAll()).object();
    Pack pack;
    pack.id = root.value(QStringLiteral("id")).toString();
    pack.order = root.value(QStringLiteral("order")).toInt();
    if (pack.id.isEmpty())
        return false;
    for (const QJsonValue &value : root.value(QStringLiteral("categories")).toArray()) {
        const QJsonObject o = value.toObject();
        const QString id = o.value(QStringLiteral("id")).toString();
        if (!id.isEmpty())
            pack.categories.append({id, o.value(QStringLiteral("label")).toString(id)});
    }
    for (const QJsonValue &value : root.value(QStringLiteral("sounds")).toArray()) {
        const QJsonObject o = value.toObject();
        const QString id = o.value(QStringLiteral("id")).toString();
        const QString path = QDir(dir).filePath(o.value(QStringLiteral("file")).toString());
        if (id.isEmpty() || !QFileInfo::exists(path))
            continue;
        SoundEffectEntry entry;
        entry.id = pack.id + QLatin1Char('/') + id;
        entry.label = o.value(QStringLiteral("label")).toString(id);
        entry.category = o.value(QStringLiteral("category")).toString();
        entry.path = path;
        entry.duration = o.value(QStringLiteral("duration")).toDouble();
        pack.sounds.append(entry);
    }
    if (pack.sounds.isEmpty())
        return false;
    *out = pack;
    return true;
}

void rebuildLocked(const QStringList &packageRoots)
{
    g_packs.clear();
    g_initialized = true;
    const QStringList roots = packageRoots.isEmpty()
        ? GpuPackageParse::defaultSearchPaths(QStringLiteral("DRIFT_SOUND_EFFECTS_DIR"),
                                              QStringLiteral("sound-effects"), QStringLiteral("sound-effects"))
        : packageRoots;
    for (const QString &root : roots) {
        const QDir dir(root);
        if (!dir.exists())
            continue;
        for (const QString &name : dir.entryList(QDir::Dirs | QDir::NoDotAndDotDot, QDir::Name)) {
            Pack pack;
            if (!loadPack(dir.filePath(name), &pack))
                continue;
            const bool duplicate = std::any_of(g_packs.cbegin(), g_packs.cend(),
                                               [&](const Pack &p) { return p.id == pack.id; });
            if (!duplicate)
                g_packs.append(pack);
        }
    }
    std::stable_sort(g_packs.begin(), g_packs.end(), [](const Pack &a, const Pack &b) { return a.order < b.order; });
}

void ensureLocked()
{
    if (!g_initialized)
        rebuildLocked({});
}

} // namespace

QList<SoundEffectEntry> soundEffects()
{
    QMutexLocker lock(&g_mutex);
    ensureLocked();
    QList<SoundEffectEntry> out;
    for (const Pack &pack : std::as_const(g_packs))
        out.append(pack.sounds);
    return out;
}

QList<SoundEffectCategory> soundEffectCategories()
{
    QMutexLocker lock(&g_mutex);
    ensureLocked();
    QList<SoundEffectCategory> out;
    for (const Pack &pack : std::as_const(g_packs)) {
        for (const SoundEffectCategory &c : pack.categories) {
            const bool seen = std::any_of(out.cbegin(), out.cend(), [&](const SoundEffectCategory &x) { return x.id == c.id; });
            if (!seen)
                out.append(c);
        }
    }
    return out;
}

void reloadSoundEffectCatalog(const QStringList &packageRoots)
{
    QMutexLocker lock(&g_mutex);
    rebuildLocked(packageRoots);
}
