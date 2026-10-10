#include "TextStyleCatalog.h"

#include "GpuPackageParse.h"
#include "core/TextStyle.h"

#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QRectF>

#include <algorithm>

namespace {

struct Pack
{
    QString id;
    int order = 0;
    QList<QPair<QString, QString>> categories;
    QList<drift::TextPreset> presets;
};

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
        const QJsonObject object = value.toObject();
        const QString id = object.value(QStringLiteral("id")).toString();
        if (!id.isEmpty())
            pack.categories.append({id, object.value(QStringLiteral("label")).toString(id)});
    }

    for (const QJsonValue &value : root.value(QStringLiteral("styles")).toArray()) {
        const QJsonObject object = value.toObject();
        const QString id = object.value(QStringLiteral("id")).toString();
        const QJsonObject style = object.value(QStringLiteral("style")).toObject();
        if (id.isEmpty() || style.isEmpty())
            continue;
        QList<drift::TextTemplatePart> parts;
        for (const QJsonValue &partValue : object.value(QStringLiteral("parts")).toArray()) {
            const QJsonObject part = partValue.toObject();
            const QJsonArray rect = part.value(QStringLiteral("rect")).toArray();
            if (rect.size() != 4 || part.value(QStringLiteral("text")).toString().isEmpty())
                continue;
            drift::TextTemplatePart p;
            p.style = drift::textStyleFromJson(part.value(QStringLiteral("style")).toObject(style));
            p.text = part.value(QStringLiteral("text")).toString();
            p.rect = QRectF(rect.at(0).toDouble(), rect.at(1).toDouble(), rect.at(2).toDouble(), rect.at(3).toDouble());
            p.delaySeconds = qMax(0.0, part.value(QStringLiteral("delay")).toDouble());
            parts.append(p);
        }
        drift::TextPreset preset;
        preset.id = QStringLiteral("pack:%1/%2").arg(pack.id, id);
        preset.label = object.value(QStringLiteral("label")).toString(id);
        preset.style = drift::textStyleFromJson(style);
        preset.style.packId = preset.id;
        preset.sampleText = object.value(QStringLiteral("sampleText")).toString(preset.label);
        preset.category = object.value(QStringLiteral("category")).toString();
        preset.parts = parts;
        pack.presets.append(preset);
    }
    if (pack.presets.isEmpty())
        return false;
    *out = pack;
    return true;
}

} // namespace

void reloadTextStyleCatalog(const QStringList &packageRoots)
{
    const QStringList roots = packageRoots.isEmpty()
        ? GpuPackageParse::defaultSearchPaths(QStringLiteral("DRIFT_TEXT_STYLES_DIR"),
                                              QStringLiteral("text-styles"), QStringLiteral("text-styles"))
        : packageRoots;

    QList<Pack> packs;
    for (const QString &root : roots) {
        const QDir dir(root);
        if (!dir.exists())
            continue;
        for (const QString &name : dir.entryList(QDir::Dirs | QDir::NoDotAndDotDot, QDir::Name)) {
            Pack pack;
            if (!loadPack(dir.filePath(name), &pack))
                continue;
            // First root wins, so DRIFT_TEXT_STYLES_DIR shadows an installed addon.
            const bool duplicate = std::any_of(packs.cbegin(), packs.cend(),
                                               [&](const Pack &p) { return p.id == pack.id; });
            if (!duplicate)
                packs.append(pack);
        }
    }
    std::stable_sort(packs.begin(), packs.end(), [](const Pack &a, const Pack &b) { return a.order < b.order; });

    QList<drift::TextPreset> presets;
    QList<QPair<QString, QString>> categories;
    for (const Pack &pack : std::as_const(packs)) {
        presets.append(pack.presets);
        for (const auto &category : pack.categories) {
            const bool seen = std::any_of(categories.cbegin(), categories.cend(),
                                          [&](const auto &c) { return c.first == category.first; });
            if (!seen)
                categories.append(category);
        }
    }
    drift::setAddonTextPresets(presets, categories);
}
