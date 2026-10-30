#include "ClipAnimationPreset.h"

#include "CatalogText.h"
#include "ClipAnimation.h"

#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QJsonArray>
#include <QJsonDocument>
#include <QMutex>
#include <QMutexLocker>
#include <QRegularExpression>
#include <QtMath>

#include <algorithm>
#include <cmath>
#include <iterator>

static void initClipAnimationResources()
{
    Q_INIT_RESOURCE(drift_clip_animations);
}

namespace drift {

namespace {

QMutex g_catalogMutex;

const char *const kSlotNames[] = {"in", "out", "combo"};
const char *const kEaseNames[] = {"linear", "easeIn", "easeOut", "easeInOut", "back", "backIn", "elastic", "bounce",
                                  "hold"};

ClipAnimKeyEase easeFromString(const QString &s, ClipAnimKeyEase fallback)
{
    for (size_t i = 0; i < std::size(kEaseNames); ++i)
        if (s == QLatin1String(kEaseNames[i]))
            return static_cast<ClipAnimKeyEase>(i);
    return fallback;
}

double bounceOut(double u)
{
    constexpr double n = 7.5625;
    constexpr double d = 2.75;
    if (u < 1.0 / d)
        return n * u * u;
    if (u < 2.0 / d) {
        u -= 1.5 / d;
        return n * u * u + 0.75;
    }
    if (u < 2.5 / d) {
        u -= 2.25 / d;
        return n * u * u + 0.9375;
    }
    u -= 2.625 / d;
    return n * u * u + 0.984375;
}

double eased(ClipAnimKeyEase ease, double u)
{
    u = std::clamp(u, 0.0, 1.0);
    constexpr double c1 = 1.70158;
    constexpr double c3 = c1 + 1.0;
    switch (ease) {
    case ClipAnimKeyEase::Linear:
        return u;
    case ClipAnimKeyEase::EaseIn:
        return u * u * u;
    case ClipAnimKeyEase::EaseOut:
        return 1.0 - std::pow(1.0 - u, 3.0);
    case ClipAnimKeyEase::EaseInOut:
        return u < 0.5 ? 4.0 * u * u * u : 1.0 - std::pow(-2.0 * u + 2.0, 3.0) / 2.0;
    case ClipAnimKeyEase::Back:
        return 1.0 + c3 * std::pow(u - 1.0, 3.0) + c1 * std::pow(u - 1.0, 2.0);
    case ClipAnimKeyEase::BackIn:
        return c3 * u * u * u - c1 * u * u;
    case ClipAnimKeyEase::Elastic:
        if (u <= 0.0 || u >= 1.0)
            return u;
        return std::pow(2.0, -10.0 * u) * std::sin((10.0 * u - 0.75) * (2.0 * M_PI / 3.0)) + 1.0;
    case ClipAnimKeyEase::Bounce:
        return bounceOut(u);
    case ClipAnimKeyEase::Hold:
        return u >= 1.0 ? 1.0 : 0.0;
    }
    return u;
}

// [[t, v, "ease"], …], [{"t","v","ease"}, …] or a bare number (constant).
ClipAnimTrack trackFromJson(const QJsonValue &v)
{
    ClipAnimTrack track;
    if (v.isDouble()) {
        track.keys.append({0.0, v.toDouble(), ClipAnimKeyEase::Linear});
        return track;
    }
    for (const QJsonValue &item : v.toArray()) {
        ClipAnimKey key;
        if (item.isArray()) {
            const QJsonArray a = item.toArray();
            if (a.size() < 2)
                continue;
            key.t = a.at(0).toDouble();
            key.v = a.at(1).toDouble();
            key.ease = easeFromString(a.at(2).toString(), ClipAnimKeyEase::EaseInOut);
        } else if (item.isObject()) {
            const QJsonObject o = item.toObject();
            key.t = o.value(QStringLiteral("t")).toDouble();
            key.v = o.value(QStringLiteral("v")).toDouble();
            key.ease = easeFromString(o.value(QStringLiteral("ease")).toString(), ClipAnimKeyEase::EaseInOut);
        } else {
            continue;
        }
        key.t = std::clamp(key.t, 0.0, 1.0);
        track.keys.append(key);
    }
    std::stable_sort(track.keys.begin(), track.keys.end(),
                     [](const ClipAnimKey &a, const ClipAnimKey &b) { return a.t < b.t; });
    return track;
}

void addTrack(const ClipAnimTrack &track, double progress, double fallback, double *value)
{
    if (!track.isEmpty())
        *value = track.at(progress, fallback);
}

} // namespace

QString clipAnimSlotToString(ClipAnimSlot slot)
{
    const size_t i = static_cast<size_t>(slot);
    return QLatin1String(i < std::size(kSlotNames) ? kSlotNames[i] : kSlotNames[0]);
}

ClipAnimSlot clipAnimSlotFromString(const QString &slot)
{
    for (size_t i = 0; i < std::size(kSlotNames); ++i)
        if (slot == QLatin1String(kSlotNames[i]))
            return static_cast<ClipAnimSlot>(i);
    return ClipAnimSlot::In;
}

ClipAnimTrack clipAnimTrackFromJson(const QJsonValue &v)
{
    return trackFromJson(v);
}

double ClipAnimTrack::at(double progress, double fallback) const
{
    if (keys.isEmpty())
        return fallback;
    if (keys.size() == 1 || progress <= keys.first().t)
        return keys.first().v;
    if (progress >= keys.last().t)
        return keys.last().v;
    for (int i = 0; i + 1 < keys.size(); ++i) {
        const ClipAnimKey &a = keys.at(i);
        const ClipAnimKey &b = keys.at(i + 1);
        if (progress > b.t)
            continue;
        const double span = b.t - a.t;
        const double u = span > 1e-9 ? (progress - a.t) / span : 1.0;
        return a.v + (b.v - a.v) * eased(a.ease, u);
    }
    return keys.last().v;
}

double ClipAnimTrack::maxAbs() const
{
    double m = 0.0;
    for (const ClipAnimKey &k : keys)
        m = std::max(m, std::abs(k.v));
    return m;
}

std::optional<ClipAnimationPreset> ClipAnimationPreset::fromJson(const QJsonObject &o, QString *error)
{
    ClipAnimationPreset p;
    p.id = o.value(QStringLiteral("id")).toString();
    if (p.id.isEmpty()) {
        if (error)
            *error = QStringLiteral("preset has no id");
        return std::nullopt;
    }
    p.label = catalogText(o.value(QStringLiteral("label")).toString(p.id));
    p.category = o.value(QStringLiteral("category")).toString(QStringLiteral("basic"));
    for (const QJsonValue &v : o.value(QStringLiteral("slots")).toArray())
        p.slotKinds.append(clipAnimSlotFromString(v.toString()));
    if (p.slotKinds.isEmpty())
        p.slotKinds.append(ClipAnimSlot::In);
    p.order = o.value(QStringLiteral("order")).toInt(100);
    p.trending = o.value(QStringLiteral("trending")).toBool(false);
    p.defaultSeconds = std::max(0.0, o.value(QStringLiteral("duration")).toDouble(p.defaultSeconds));

    const QJsonObject keys = o.value(QStringLiteral("keys")).toObject();
    p.x = trackFromJson(keys.value(QStringLiteral("x")));
    p.y = trackFromJson(keys.value(QStringLiteral("y")));
    p.scale = trackFromJson(keys.value(QStringLiteral("scale")));
    p.scaleX = trackFromJson(keys.value(QStringLiteral("scaleX")));
    p.scaleY = trackFromJson(keys.value(QStringLiteral("scaleY")));
    p.rotation = trackFromJson(keys.value(QStringLiteral("rotation")));
    p.rotationX = trackFromJson(keys.value(QStringLiteral("rotationX")));
    p.rotationY = trackFromJson(keys.value(QStringLiteral("rotationY")));
    p.opacity = trackFromJson(keys.value(QStringLiteral("opacity")));
    p.blur = trackFromJson(keys.value(QStringLiteral("blur")));

    for (const QJsonValue &v : o.value(QStringLiteral("effects")).toArray()) {
        const QJsonObject e = v.toObject();
        ClipAnimPresetEffect effect;
        effect.effectId = e.value(QStringLiteral("id")).toString();
        if (effect.effectId.isEmpty())
            continue;
        const QJsonObject params = e.value(QStringLiteral("params")).toObject();
        for (auto it = params.constBegin(); it != params.constEnd(); ++it) {
            if (it->isDouble())
                effect.fixed.insert(it.key(), it->toDouble());
            else
                effect.params.insert(it.key(), trackFromJson(*it));
        }
        p.effects.append(effect);
    }
    return p;
}

ClipAnimationPresetCatalog &ClipAnimationPresetCatalog::instance()
{
    static ClipAnimationPresetCatalog catalog;
    return catalog;
}

void ClipAnimationPresetCatalog::loadDir(const QString &dir) const
{
    const QDir d(dir);
    for (const QFileInfo &info : d.entryInfoList({QStringLiteral("*.json")}, QDir::Files, QDir::Name)) {
        QFile file(info.absoluteFilePath());
        if (!file.open(QIODevice::ReadOnly))
            continue;
        QString error;
        const std::optional<ClipAnimationPreset> preset =
            ClipAnimationPreset::fromJson(QJsonDocument::fromJson(file.readAll()).object(), &error);
        if (!preset) {
            qWarning("clip animation preset %s: %s", qPrintable(info.fileName()), qPrintable(error));
            continue;
        }
        bool replaced = false;
        for (ClipAnimationPreset &existing : m_presets) {
            if (existing.id == preset->id) {
                existing = *preset;
                replaced = true;
            }
        }
        if (!replaced)
            m_presets.append(*preset);
    }
}

void ClipAnimationPresetCatalog::ensureLoaded() const
{
    if (m_loaded)
        return;
    m_loaded = true;
    m_presets.clear();
    initClipAnimationResources();
    loadDir(QStringLiteral(":/clip-animations"));
    const QString extra = qEnvironmentVariable("DRIFT_CLIP_ANIMATIONS");
    for (const QString &dir : extra.split(QRegularExpression(QStringLiteral("[;:](?![\\\\/])")), Qt::SkipEmptyParts))
        loadDir(dir);
    std::stable_sort(m_presets.begin(), m_presets.end(),
                     [](const ClipAnimationPreset &a, const ClipAnimationPreset &b) { return a.order < b.order; });
}

void ClipAnimationPresetCatalog::reload()
{
    QMutexLocker lock(&g_catalogMutex);
    m_loaded = false;
    ensureLoaded();
}

QList<ClipAnimationPreset> ClipAnimationPresetCatalog::presets() const
{
    QMutexLocker lock(&g_catalogMutex);
    ensureLoaded();
    return m_presets;
}

QList<ClipAnimationPreset> ClipAnimationPresetCatalog::presetsFor(ClipAnimSlot slot) const
{
    QList<ClipAnimationPreset> out;
    for (const ClipAnimationPreset &p : presets())
        if (p.supportsSlot(slot))
            out.append(p);
    return out;
}

std::optional<ClipAnimationPreset> ClipAnimationPresetCatalog::presetForId(const QString &id) const
{
    QMutexLocker lock(&g_catalogMutex);
    ensureLoaded();
    for (const ClipAnimationPreset &p : std::as_const(m_presets))
        if (p.id == id)
            return p;
    return std::nullopt;
}

void applyClipAnimationPreset(const ClipAnimationPreset &preset, double progress, double boxW, double boxH,
                              double shortSidePx, ClipAnimSample *sample)
{
    if (!sample)
        return;
    progress = std::clamp(progress, 0.0, 1.0);
    double x = 0.0, y = 0.0, scale = 100.0, scaleX = 100.0, scaleY = 100.0, rotation = 0.0;
    double rotationX = 0.0, rotationY = 0.0, opacity = 100.0, blur = 0.0;
    addTrack(preset.x, progress, 0.0, &x);
    addTrack(preset.y, progress, 0.0, &y);
    addTrack(preset.scale, progress, 100.0, &scale);
    addTrack(preset.scaleX, progress, 100.0, &scaleX);
    addTrack(preset.scaleY, progress, 100.0, &scaleY);
    addTrack(preset.rotation, progress, 0.0, &rotation);
    addTrack(preset.rotationX, progress, 0.0, &rotationX);
    addTrack(preset.rotationY, progress, 0.0, &rotationY);
    addTrack(preset.opacity, progress, 100.0, &opacity);
    addTrack(preset.blur, progress, 0.0, &blur);

    sample->dx += x * boxW;
    sample->dy += y * boxH;
    sample->scale *= std::max(0.0, scale / 100.0);
    sample->scaleX *= std::max(0.0, scaleX / 100.0);
    sample->scaleY *= std::max(0.0, scaleY / 100.0);
    sample->rotationDeg += rotation;
    sample->rotationX += rotationX;
    sample->rotationY += rotationY;
    sample->opacity *= std::clamp(opacity / 100.0, 0.0, 1.0);
    sample->blurPx += std::max(0.0, blur) * shortSidePx / 1080.0;
    for (const ClipAnimPresetEffect &effect : preset.effects) {
        ClipAnimSampleEffect out;
        out.effectId = effect.effectId;
        for (auto it = effect.fixed.constBegin(); it != effect.fixed.constEnd(); ++it)
            out.params.insert(it.key(), it.value());
        for (auto it = effect.params.constBegin(); it != effect.params.constEnd(); ++it)
            out.params.insert(it.key(), it->at(progress, 0.0));
        sample->effects.append(out);
    }
}

} // namespace drift
