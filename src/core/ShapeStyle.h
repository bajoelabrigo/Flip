#pragma once

#include "BlendMode.h"
#include "Keyframe.h"
#include "TextShading.h"
#include "Time.h"

#include <QColor>
#include <QJsonObject>
#include <QList>
#include <QMap>
#include <QString>
#include <QStringList>

#include <vector>

namespace drift {

enum class ShapeKind {
    // Basic
    Rectangle,
    RoundedRectangle,
    Square,
    Ellipse,
    Triangle,
    RightTriangle,
    Diamond,
    Pentagon,
    Hexagon,
    Octagon,
    Parallelogram,
    Trapezoid,
    // Arrows
    Arrow,
    DoubleArrow,
    BlockArrow,
    CurvedArrow,
    Chevron,
    // Bubbles
    SpeechBubble,
    SpeechBubbleRect,
    ThoughtBubble,
    Callout,
    // Fun
    Star,
    LightningBolt,
    Cloud,
    Heart,
    Cross,
    Burst,
    Banner,
    // A shape from the person's library (Stock › Shapes): its outline is ShapeStyle::customPath,
    // carried in the project so it renders on a machine that never installed the shape.
    Custom,
};

QString shapeKindToString(ShapeKind kind);
ShapeKind shapeKindFromString(const QString &kind);

// A fill and a stroke with the catalog's stable ids, so "layer.fill.color.r" and
// "layer.stroke.width" address a fresh shape without a lookup. The fill's gradient is pre-seeded
// with fill → fillDeep so switching the paint to Gradient looks right immediately. A strokeWidth
// of 0 leaves the stroke layer disabled.
QList<TextShadingLayer> defaultShapeLayers(const QColor &fill, const QColor &fillDeep = QColor(),
                                           const QColor &stroke = Qt::white, double strokeWidth = 4.0);

struct ShapePart;

struct ShapeStyle
{
    ShapeKind kind = ShapeKind::Rectangle;

    // Ordered shading stack, layers[0] back-most. The same model TextStyle::layers uses.
    QList<TextShadingLayer> layers = defaultShapeLayers(QColor(0, 180, 255), QColor(122, 0, 255));

    // Geometry knobs. Each is read by a subset of kinds only; see ShapePath.cpp.
    double cornerRadius = 0.0; // project px — native on the rect family, a corner path effect elsewhere
    int points = 5;            // star / burst spikes
    double innerRatio = 0.5;   // star / burst inner radius, fraction of outer
    double headSize = 0.4;     // arrows / chevron / banner: head length, fraction of width
    double thickness = 0.4;    // arrows / chevron / cross: shaft, fraction of height
    double tailX = 0.25;       // bubbles: tail anchor along the bottom edge, 0..1
    double tailSize = 0.2;     // bubbles: tail extent, fraction of height
    // Custom only: an SVG path ("M L C Q Z", absolute) on a 0..100 x 0..100 box the outline spans
    // edge to edge, stretched onto the layout rect like every other kind; and its fill rule.
    QString customPath;
    bool customEvenOdd = false;

    // After Effects' shape operators (0.26), over the whole outline, fill and strokes alike.
    // Trim Paths: the part of the outline from trimStart to trimEnd (percent of its length),
    // shifted by trimOffset degrees (360° = once round), wrapping as AE does.
    double trimStart = 0.0;
    double trimEnd = 100.0;
    double trimOffset = 0.0;
    // Trim-Pack's Equal-in / Equal-out (0.26): the outline cut into this many equal stretches, each
    // trimmed from trimStart to trimEnd at once.
    double trimSegments = 1.0;
    // Trim-Pack's Reverse Path Direction (0.26): the trim runs round the outline the other way (1 = on).
    double trimReverse = 0.0;
    // Repeater: repeatCopies copies (rounded), the first at repeatOffset copies along, each one
    // moved by (repeatX, repeatY) project px, turned repeatRotation degrees and scaled
    // repeatScale percent from the one before, about the box centre; opacity runs from
    // repeatStartOpacity on the first to repeatEndOpacity on the last (percent).
    double repeatCopies = 1.0;
    double repeatOffset = 0.0;
    double repeatX = 0.0;
    double repeatY = 0.0;
    double repeatScale = 100.0;
    double repeatRotation = 0.0;
    double repeatStartOpacity = 100.0;
    double repeatEndOpacity = 100.0;
    // Wiggle Paths: the outline resampled every wiggleDetail px and each point pushed up to
    // wiggleSize px along its normal by a smooth noise that moves wiggleSpeed times a second
    // (0 = still), from wiggleSeed.
    double wiggleSize = 0.0;
    double wiggleDetail = 20.0;
    double wiggleSpeed = 0.0;
    double wiggleSeed = 0.0;
    // More of After Effects' operators (0.26, stage G): Merge Paths between the outline's
    // contours (0 off, 1 add, 2 subtract, 3 intersect, 4 exclude), Offset Paths (px, negative
    // shrinks), Zig Zag (size px, ridges per contour, smooth 0/1) and Twist (degrees at the rim).
    double mergeMode = 0.0;
    double offsetPath = 0.0;
    double zigzagSize = 0.0;
    double zigzagRidges = 12.0;
    double zigzagSmooth = 0.0;
    double twistAngle = 0.0;
    // Pucker & Bloat (0.26): percent, -100..100. Vertices towards the centre and handles away
    // (positive, bloat) or the other way (negative, pucker), as After Effects.
    double puckerBloat = 0.0;

    // After Effects' animated Path (0.26), on a custom shape: the "path" keyframe track holds, at
    // each key, the index of that key's outline in pathShapes. Between two keys the outlines
    // morph by how far the track has gone from one key's value to the next, so the track's own
    // easing and handles shape the morph. Indices are unique per key; editing the path at a key
    // replaces its entry.
    QStringList pathShapes;

    // After Effects' Contents (0.28): the layer is made of parts, each a whole shape of its own
    // (outline, fills, strokes, operators, keys) placed by its own transform, or a group of parts.
    // parts[0] is the top one, as AE lists them. Empty = a plain shape, drawn from the fields above
    // exactly as before. Parts are laid out in project px about the centre of a box
    // partsRefWidth × partsRefHeight; the layer's box stretches that box, so the clip's Scale and
    // size still scale the whole layer.
    std::vector<ShapePart> parts;
    double partsRefWidth = 0.0;
    double partsRefHeight = 0.0;
    bool hasParts() const { return !parts.empty(); }

    bool hasTrim() const { return trimStart > 0.0 || trimEnd < 100.0 || qRound(trimSegments) > 1 || trimReverse > 0.5; }
    bool hasRepeater() const { return qRound(repeatCopies) > 1 || qAbs(repeatOffset) > 1e-9; }
    bool hasWiggle() const { return wiggleSize > 0.0; }

    // Keyed by shapeKeyframeProperties() names ("cornerRadius", "layer.<id>.<field>", …); times
    // are relative to the clip start.
    QMap<QString, KeyframeTrack<double>> keyframes;

    bool isAnimated() const;
    // The style with every keyframed value baked in at the given clip time.
    ShapeStyle resolvedAt(TimeUs clipTimeUs) const;

    // The front-most enabled fill's colour — what a swatch or a clip thumbnail shows.
    QColor primaryColor() const;
    void setPrimaryColor(const QColor &color);
    // Convenience for tests and importers: replace the stack with one solid fill (+ the stroke).
    void setSolidFill(const QColor &color);
    void setStroke(double width, const QColor &color = Qt::white);
};

// After Effects' «Transform: Group» of a part (0.28): anchor, position (project px, about the
// layer's centre or the parent group's origin), scale (percent), skew (degrees, along skewAxis
// degrees), rotation (degrees) and opacity (percent). Applied as AE does: anchor, scale, skew,
// rotation, position.
struct ShapePartTransform
{
    double anchorX = 0.0;
    double anchorY = 0.0;
    double x = 0.0;
    double y = 0.0;
    double scaleX = 100.0;
    double scaleY = 100.0;
    double skew = 0.0;
    double skewAxis = 0.0;
    double rotation = 0.0;
    double opacity = 100.0;
};

struct ShapePart
{
    QString id;   // stable, unique in the layer ("p1", "p2"…): keys and the selection use it
    QString name; // what the person sees («Rectángulo 1»)
    bool visible = true;
    BlendMode blend = BlendMode::Normal;
    bool group = false;
    // A shape part: its outline fills width × height (project px) centred on its origin, drawn by
    // `shape` exactly as a plain shape layer of that size would be. A group: `children` instead.
    double width = 100.0;
    double height = 100.0;
    ShapeStyle shape;
    std::vector<ShapePart> children;
    ShapePartTransform transform;
    // The part's own keys: transform and size fields (shapePartKeyframeFields()). The shape's
    // keys live in shape.keyframes.
    QMap<QString, KeyframeTrack<double>> keyframes;

    bool isAnimated() const;
    ShapePart resolvedAt(TimeUs clipTimeUs) const;
};

// The part keys: anchorX, anchorY, x, y, scaleX, scaleY, skew, skewAxis, rotation, opacity, width,
// height (the last two on shape parts only).
QStringList shapePartKeyframeFields(const ShapePart &part);
bool shapePartScalar(const ShapePart &part, const QString &field, double *out);
bool setShapePartScalar(ShapePart &part, const QString &field, double value);
// Depth-first, top part first.
ShapePart *findShapePart(std::vector<ShapePart> &parts, const QString &id);
const ShapePart *findShapePart(const std::vector<ShapePart> &parts, const QString &id);
// A fresh id no part of the layer uses yet.
QString mintShapePartId(const ShapeStyle &style);
// A plain shape turned into a layer with one part that draws the same: the part is the old shape
// (its keys included) at the layer's box size `boxWidth` × `boxHeight` (project px), the
// reference box is that box. A layer that already has parts comes back unchanged.
ShapeStyle shapeWithParts(const ShapeStyle &style, double boxWidth, double boxHeight, const QString &partName);
QJsonObject shapePartToJson(const ShapePart &part);
ShapePart shapePartFromJson(const QJsonObject &o);

QStringList shapeKeyframeProperties(const ShapeStyle &style);
// The stored key for a property name, or empty when the style has no such scalar.
QString shapeKeyframeCanonicalKey(const QString &key, const ShapeStyle &style);
QString shapeKeyframeLabel(const QString &key, const ShapeStyle &style);
bool shapeStyleScalar(const ShapeStyle &style, const QString &key, double *out);
bool setShapeStyleScalar(ShapeStyle &style, const QString &key, double value);
// The key of the animated path (0.26) and the outline it gives at clip time `clipTimeUs`, or the
// static customPath when the path is not animated.
inline constexpr char kShapePathKey[] = "path";
QString shapePathAt(const ShapeStyle &style, TimeUs clipTimeUs);
// Puts `svg` on the path at clip time `clipTimeUs`: replaces the key there (within `toleranceUs`),
// adds one, or, when the path is not animated, sets customPath.
void setShapePathAt(ShapeStyle &style, TimeUs clipTimeUs, const QString &svg, TimeUs toleranceUs);
// Starts animating the path with a key at `clipTimeUs` (stopwatch on), or stops: the outline at
// that time stays as the static path.
void setShapePathAnimated(ShapeStyle &style, bool on, TimeUs clipTimeUs);
// Everything that changes pixels (render cache keys). Keyframes are not part of it.
quint64 shapeStyleHash(const ShapeStyle &style);
// A paint that moves on its own (gradient offsetSpeed, a time-driven shader effect).
bool shapeTimeDrivenPaint(const ShapeStyle &style);

QJsonObject shapeStyleToJson(const ShapeStyle &style);
// Reads the layered form, or the flat fill/stroke form projects before format 8 wrote.
ShapeStyle shapeStyleFromJson(const QJsonObject &o);

// The shapes offered in the assets panel. Several entries can share a ShapeKind and differ only in
// their default aspect or colour ("circle" vs "ellipse"), so ids — not kinds — are what the UI and
// the drag mime data carry.
struct ShapeCatalogEntry
{
    QString id;
    QString label;
    QString category;
    double aspect; // default layout box width / height
    ShapeStyle style;
};

struct ShapeCategory
{
    QString id;
    QString label;
};

// The built-in shapes. User shapes (below) are not in this list.
const QList<ShapeCatalogEntry> &shapeCatalog();
// A built-in or user shape by id. A user entry stays valid for the life of the process, even after
// a rescan replaces it, so the pointer may be held across calls.
const ShapeCatalogEntry *shapeCatalogEntry(const QString &id);
QList<ShapeCategory> shapeCategories();

// --- User shapes (Stock › Shapes) ---------------------------------------------------------------
// One JSON file per shape in userShapesDir():
//   {"format": 1, "id": "heart-classic", "names": {"es": "…", "en": "…"}, "category": "hearts",
//    "categoryNames": {"es": "Corazones", …}, "aspect": 1.0, "path": "M … Z",
//    "fillRule": "nonzero" | "evenodd", "fill": "#RRGGBB", "fillDeep": "#RRGGBB", "tags": […]}
// Their catalog ids are kUserShapePrefix + id, so they can never collide with a built-in.
inline constexpr char kUserShapePrefix[] = "user-shape:";
QString userShapesDir();
// Rescans userShapesDir(). Cheap; called on start and after an install.
void reloadUserShapes();
// The installed user shapes, ordered by category then name, labels in the UI language.
QList<ShapeCatalogEntry> userShapeCatalog();
// The categories the installed user shapes use, in first-seen order, labels in the UI language.
QList<ShapeCategory> userShapeCategories();
// Checks a shape file and copies it into userShapesDir() (replacing one with the same id). Returns
// the catalog id, or empty with *error set.
QString installUserShapeFile(const QString &path, QString *error = nullptr);
bool removeUserShape(const QString &catalogId);

} // namespace drift
