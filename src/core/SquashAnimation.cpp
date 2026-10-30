#include "SquashAnimation.h"

#include <QDir>
#include <QFile>
#include <QJsonDocument>
#include <QMutex>
#include <QMutexLocker>

#include <algorithm>

static void initSquashAnimationResources()
{
    Q_INIT_RESOURCE(drift_squash_animations);
}

namespace drift {

namespace {

QMutex g_squashMutex;

const char *const kSquashProps[] = {"x",           "y",        "rotation", "opacity", "zoom", "stretch",
                                    "groundWidth", "farWidth", "shear",    "bend",    "bulge"};

} // namespace

std::optional<SquashAnimation> SquashAnimation::fromJson(const QJsonObject &o, QString *error)
{
    SquashAnimation anim;
    anim.id = o.value(QStringLiteral("id")).toString();
    if (anim.id.isEmpty()) {
        if (error)
            *error = QStringLiteral("no id");
        return std::nullopt;
    }
    anim.label = o.value(QStringLiteral("label")).toString(anim.id);
    anim.category = o.value(QStringLiteral("category")).toString(QStringLiteral("moves"));
    anim.order = o.value(QStringLiteral("order")).toInt(100);
    anim.seconds = std::max(0.05, o.value(QStringLiteral("duration")).toDouble(1.0));
    const QString place = o.value(QStringLiteral("place")).toString();
    anim.place = place == QLatin1String("start") ? SquashPlace::Start
               : place == QLatin1String("end")   ? SquashPlace::End
                                                 : SquashPlace::Playhead;
    anim.ground = std::clamp(o.value(QStringLiteral("ground")).toDouble(100.0), 0.0, 100.0);
    const QJsonObject keys = o.value(QStringLiteral("keys")).toObject();
    for (const char *prop : kSquashProps) {
        const QString name = QLatin1String(prop);
        if (!keys.contains(name))
            continue;
        const ClipAnimTrack track = clipAnimTrackFromJson(keys.value(name));
        if (!track.isEmpty())
            anim.tracks.insert(name, track);
    }
    if (anim.tracks.isEmpty()) {
        if (error)
            *error = QStringLiteral("no curves");
        return std::nullopt;
    }
    return anim;
}

SquashAnimationCatalog &SquashAnimationCatalog::instance()
{
    static SquashAnimationCatalog catalog;
    return catalog;
}

void SquashAnimationCatalog::ensureLoaded() const
{
    if (m_loaded)
        return;
    m_loaded = true;
    m_animations.clear();
    initSquashAnimationResources();
    const QDir dir(QStringLiteral(":/squash-animations"));
    for (const QFileInfo &info : dir.entryInfoList({QStringLiteral("*.json")}, QDir::Files, QDir::Name)) {
        QFile file(info.absoluteFilePath());
        if (!file.open(QIODevice::ReadOnly))
            continue;
        QString error;
        const std::optional<SquashAnimation> anim =
            SquashAnimation::fromJson(QJsonDocument::fromJson(file.readAll()).object(), &error);
        if (!anim) {
            qWarning("squash animation %s: %s", qPrintable(info.fileName()), qPrintable(error));
            continue;
        }
        m_animations.append(*anim);
    }
    std::stable_sort(m_animations.begin(), m_animations.end(),
                     [](const SquashAnimation &a, const SquashAnimation &b) { return a.order < b.order; });
}

QList<SquashAnimation> SquashAnimationCatalog::animations() const
{
    QMutexLocker lock(&g_squashMutex);
    ensureLoaded();
    return m_animations;
}

std::optional<SquashAnimation> SquashAnimationCatalog::animationForId(const QString &id) const
{
    QMutexLocker lock(&g_squashMutex);
    ensureLoaded();
    for (const SquashAnimation &anim : m_animations) {
        if (anim.id == id)
            return anim;
    }
    return std::nullopt;
}

} // namespace drift
