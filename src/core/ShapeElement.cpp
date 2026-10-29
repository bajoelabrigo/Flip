#include "ShapeElement.h"

#include "ShapePathEdit.h"

#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QMutex>
#include <QMutexLocker>

#include <algorithm>

static void initShapeElementResources()
{
    Q_INIT_RESOURCE(drift_shape_elements);
}

namespace drift {

namespace {
QMutex g_elementMutex;
}

std::optional<ShapeElement> ShapeElement::fromJson(const QJsonObject &o, QString *error)
{
    ShapeElement e;
    e.id = o.value(QStringLiteral("id")).toString();
    if (e.id.isEmpty()) {
        if (error)
            *error = QStringLiteral("no id");
        return std::nullopt;
    }
    e.label = o.value(QStringLiteral("label")).toString(e.id);
    e.category = o.value(QStringLiteral("category")).toString(QStringLiteral("morph"));
    e.order = o.value(QStringLiteral("order")).toInt(100);
    e.seconds = std::max(0.1, o.value(QStringLiteral("duration")).toDouble(2.0));
    e.cover = o.value(QStringLiteral("fit")).toString() == QLatin1String("cover");
    e.size = std::clamp(o.value(QStringLiteral("size")).toDouble(0.4), 0.05, 4.0);
    for (const QJsonValue &lv : o.value(QStringLiteral("layers")).toArray()) {
        const QJsonObject lo = lv.toObject();
        ShapeElementLayer layer;
        layer.color = lo.value(QStringLiteral("color")).toInt(0);
        for (const QJsonValue &kv : lo.value(QStringLiteral("keys")).toArray()) {
            const QJsonObject ko = kv.toObject();
            const QString svg = ko.value(QStringLiteral("svg")).toString();
            if (!svg.isEmpty())
                layer.keys.append({std::clamp(ko.value(QStringLiteral("t")).toDouble(), 0.0, 1.0), svg});
        }
        std::stable_sort(layer.keys.begin(), layer.keys.end(),
                         [](const ShapeElementKey &a, const ShapeElementKey &b) { return a.t < b.t; });
        if (!layer.keys.isEmpty())
            e.layers.append(layer);
    }
    if (e.layers.isEmpty()) {
        if (error)
            *error = QStringLiteral("no layers");
        return std::nullopt;
    }
    return e;
}

QStringList ShapeElement::outlinesAt(double progress) const
{
    QStringList out;
    for (const ShapeElementLayer &layer : layers) {
        const QList<ShapeElementKey> &keys = layer.keys;
        if (progress <= keys.first().t || keys.size() == 1) {
            out.append(keys.first().svg);
            continue;
        }
        if (progress >= keys.last().t) {
            out.append(keys.last().svg);
            continue;
        }
        for (int i = 0; i + 1 < keys.size(); ++i) {
            if (progress > keys.at(i + 1).t)
                continue;
            const double span = keys.at(i + 1).t - keys.at(i).t;
            const double f = span > 1e-9 ? (progress - keys.at(i).t) / span : 1.0;
            out.append(morphSvgPaths(keys.at(i).svg, keys.at(i + 1).svg, f));
            break;
        }
    }
    return out;
}

ShapeElementCatalog &ShapeElementCatalog::instance()
{
    static ShapeElementCatalog catalog;
    return catalog;
}

void ShapeElementCatalog::ensureLoaded() const
{
    if (m_loaded)
        return;
    m_loaded = true;
    m_elements.clear();
    initShapeElementResources();
    const QDir dir(QStringLiteral(":/shape-elements"));
    for (const QFileInfo &info : dir.entryInfoList({QStringLiteral("*.json")}, QDir::Files, QDir::Name)) {
        QFile file(info.absoluteFilePath());
        if (!file.open(QIODevice::ReadOnly))
            continue;
        QString error;
        const std::optional<ShapeElement> e =
            ShapeElement::fromJson(QJsonDocument::fromJson(file.readAll()).object(), &error);
        if (!e) {
            qWarning("shape element %s: %s", qPrintable(info.fileName()), qPrintable(error));
            continue;
        }
        m_elements.append(*e);
    }
    std::stable_sort(m_elements.begin(), m_elements.end(),
                     [](const ShapeElement &a, const ShapeElement &b) { return a.order < b.order; });
}

QList<ShapeElement> ShapeElementCatalog::elements() const
{
    QMutexLocker lock(&g_elementMutex);
    ensureLoaded();
    return m_elements;
}

std::optional<ShapeElement> ShapeElementCatalog::elementForId(const QString &id) const
{
    QMutexLocker lock(&g_elementMutex);
    ensureLoaded();
    for (const ShapeElement &e : m_elements) {
        if (e.id == id)
            return e;
    }
    return std::nullopt;
}

} // namespace drift
