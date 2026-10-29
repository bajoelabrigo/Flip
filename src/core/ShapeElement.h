#pragma once

#include <QJsonObject>
#include <QList>
#include <QString>
#include <QStringList>

#include <optional>

// Morphings and Liquids (0.26, Jorge): animated shape elements of our own, in the manner of the
// Super Morphings and Super Liquids scripts for After Effects (presets/shape-elements/*.json, made
// by tools/shape_elements/build.py). An element is one or more shape layers whose outline is
// animated: each layer lists its outlines over the element's progress (0 → 1), all with the same
// contours and points, so the app morphs between them with linear path keys. Outlines are SVG
// paths on a 0..100 square, placed in the middle of the canvas: `size` × its short side ("center")
// or as big as its diagonal ("cover", full-screen transitions).
namespace drift {

struct ShapeElementKey
{
    double t = 0.0;
    QString svg;
};

struct ShapeElementLayer
{
    int color = 0; // which of the chosen colours
    QList<ShapeElementKey> keys;
};

struct ShapeElement
{
    QString id;
    QString label;
    QString category; // "morph" or "liquid"
    int order = 100;
    double seconds = 2.0;
    bool cover = false;
    double size = 0.4;
    QList<ShapeElementLayer> layers;

    static std::optional<ShapeElement> fromJson(const QJsonObject &o, QString *error = nullptr);
    // Each layer's outline at `progress`, morphed between its two nearest keys.
    QStringList outlinesAt(double progress) const;
};

class ShapeElementCatalog
{
public:
    static ShapeElementCatalog &instance();

    QList<ShapeElement> elements() const;
    std::optional<ShapeElement> elementForId(const QString &id) const;

private:
    ShapeElementCatalog() = default;
    void ensureLoaded() const;

    mutable bool m_loaded = false;
    mutable QList<ShapeElement> m_elements;
};

} // namespace drift
