#pragma once

#include "Keyframe.h"
#include "Time.h"
#include "VectorSource.h"

#include <QColor>
#include <QJsonObject>
#include <QJsonValue>
#include <QList>
#include <QMap>
#include <QPointF>
#include <QString>

#include <optional>

// Per-fragment text animation, modelled on After Effects text animators as Skottie implements
// them (modules/skottie/src/text): an animator is a set of property deltas plus range selectors
// that yield a coverage weight per fragment (character / word / line); the deltas are applied
// scaled by that weight. Every preset in the In / Out / Loop galleries is data on top of this.
//
// This header is Skia-free and layout-free: the renderer hands over fragment metadata and gets
// back per-fragment props. Nothing here knows about glyphs or pixels beyond an advance width.

namespace drift {

// Order the staggered fragments fire in. Kept here (not TextStyle.h) because selectors own it.
enum class TextAnimOrder { Forward, Backward, CenterOut, Random };
QString textAnimOrderToString(TextAnimOrder order);
TextAnimOrder textAnimOrderFromString(const QString &order);

// Easing over a 0..1 progress. Back and Bounce overshoot on purpose (that is the pop / bounce
// look); Bezier is a unit cubic through c1/c2 whose y may leave [0,1].
enum class TextEaseKind { Linear, EaseIn, EaseOut, EaseInOut, Back, Bounce, Smooth, Bezier };
struct TextEaseSpec
{
    TextEaseKind kind = TextEaseKind::EaseOut;
    QPointF c1{0.42, 0.0};
    QPointF c2{0.58, 1.0};
    double value(double t) const;
};
QString textEaseKindToString(TextEaseKind kind);
TextEaseKind textEaseKindFromString(const QString &kind);

// A scalar that is either a constant or a curve over the slot's normalised progress. Curves reuse
// KeyframeTrack (bezier tangents, hold) with the key "time" being progress × kProgressScale.
constexpr TimeUs kProgressScale = 1'000'000;
struct TextAnimParam
{
    double value = 0.0;
    KeyframeTrack<double> curve;

    TextAnimParam() = default;
    TextAnimParam(double v) : value(v) {}

    bool isConstant() const { return curve.isEmpty(); }
    double at(double progress) const;
    // Largest magnitude the param can take over the whole progress range (bounds/bleed).
    double maxAbs() const;
};

enum class TextSelectorDriver { Curves, Stagger, Wiggle, Karaoke };
// All = one group covering the whole block (whole-layer motion); the rest are AE's domains.
enum class TextSelectorDomain { All, Chars, CharsExcludingSpaces, Words, Lines };
enum class TextSelectorUnits { Percent, Index };
enum class TextSelectorShape { Square, RampUp, RampDown, Triangle, Round, Smooth };
enum class TextSelectorMode { Add, Subtract, Intersect, Min, Max, Difference };
enum class TextWiggleWave { Sine, Triangle, Noise };

// Index-unit selectors default their end to "everything"; the value is clamped on resolve.
constexpr double kTextSelectorIndexEnd = 1e9;

struct TextRangeSelector
{
    TextSelectorDriver driver = TextSelectorDriver::Stagger;
    TextSelectorDomain domain = TextSelectorDomain::Words;
    TextSelectorMode mode = TextSelectorMode::Add;

    // Curves (AE range selector): the window [start, end] + offset in `units`, a shape across it,
    // ease on both ends, and an amount multiplier. All animatable over progress.
    TextSelectorUnits units = TextSelectorUnits::Percent;
    TextSelectorShape shape = TextSelectorShape::Square;
    TextAnimParam start{0.0};
    TextAnimParam end{100.0};
    TextAnimParam offset{0.0};
    TextAnimParam amount{100.0};
    TextAnimParam easeLo{0.0};
    TextAnimParam easeHi{0.0};
    TextAnimParam smoothness{100.0};

    // Stagger (the reveal): each fragment starts `staggerUs` after the previous slot and ramps
    // over `durationUs` with `ease`; 0 duration is a hard step (typewriter). Coverage 1 = fully
    // away from its resting state, so In and Out share one formula with mirrored slots.
    TimeUs staggerUs = 60000;
    TimeUs durationUs = 400000;
    TextEaseSpec ease;
    TextAnimOrder order = TextAnimOrder::Forward;

    // Wiggle: a continuous wave over absolute time, phase-shifted per fragment.
    TextWiggleWave wave = TextWiggleWave::Sine;
    double frequencyHz = 1.1;
    double spatialPhaseDeg = 34.4; // per fragment slot; 0.6 rad reproduces the legacy Wave
    double temporalPhaseDeg = 0.0;
    double minAmount = -100.0;
    double maxAmount = 100.0;

    // Karaoke: coverage 1 on the word being spoken (EvalContext::activeWordIndex).

    quint32 seed = 0; // Random order / Noise; 0 = the stable legacy hash
};

enum class TextLengthUnit { Px, Em, Box }; // Box = fraction of the layout rect
struct TextAnimVec2
{
    TextAnimParam x{0.0};
    TextAnimParam y{0.0};
    TextLengthUnit unit = TextLengthUnit::Px;
    double maxPx = 0.0; // 0 = uncapped (project px)
};

struct TextAnimWipe
{
    bool enabled = false;
    double angleDeg = -90.0; // direction the reveal travels; -90 = bottom → top
    double softness = 0.3;   // edge width as a fraction of the masked box
};

// The deltas an animator applies at coverage 1. Mirrors skottie's AnimatedProps plus skew and a
// soft-mask wipe. Position/tracking are additive, scale multiplicative, opacity and colours lerp.
struct TextAnimatorProps
{
    TextAnimVec2 position;
    TextAnimParam scaleX{100.0}; // percent
    TextAnimParam scaleY{100.0};
    TextAnimParam rotation{0.0}; // degrees about the fragment anchor
    TextAnimParam skew{0.0};     // degrees, x shear
    // Turned in depth about the anchor and seen with a perspective (door, flip, roll in 3D):
    // + X tips the top edge away, + Y swings the right edge away, as a clip's 3D layer does.
    TextAnimParam rotationX{0.0};
    TextAnimParam rotationY{0.0};

    TextAnimParam opacity{100.0};
    bool hasOpacity = false;
    TextAnimParam fillOpacity{100.0};
    bool hasFillOpacity = false;
    TextAnimParam strokeOpacity{100.0};
    bool hasStrokeOpacity = false;
    QColor fillColor;
    bool hasFillColor = false;
    QColor strokeColor;
    bool hasStrokeColor = false;

    TextAnimParam blur{0.0};        // project px
    TextAnimParam tracking{0.0};    // per fragment, additive
    TextLengthUnit trackingUnit = TextLengthUnit::Px;
    TextAnimParam lineSpacing{0.0}; // project px
    TextAnimParam strokeWidth{0.0}; // project px, additive
    TextAnimWipe wipe;
};

struct TextAnimator
{
    QString name;
    bool enabled = true;
    QList<TextRangeSelector> selectors; // empty → coverage 1 everywhere
    TextAnimatorProps props;
    // Fragments this animator hides lose their advance, so the visible part re-centres as
    // characters appear (typewriter). Only sensible with a step reveal.
    bool collapseHidden = false;
};

// Typewriter cursor drawn after the last visible fragment.
struct TextCaret
{
    // Glyph: an emoji or symbol rides after the text instead of a bar ("ABC⚡").
    enum class Shape { Bar, Underscore, Block, Glyph };

    bool enabled = false;
    TimeUs leadUs = 200000;      // blinks alone before the first fragment appears
    TimeUs blinkOnUs = 200000;
    TimeUs blinkOffUs = 300000;
    TimeUs holdAfterUs = 0;      // keep blinking this long after the reveal; -1 = whole window
    double widthEm = 0.08;
    double heightEm = 1.0;
    Shape shape = Shape::Bar;
    QColor color;                // invalid → the fill colour
    QString glyph;               // Glyph: the emoji or symbol, sized by heightEm
    double gapEm = 0.08;         // Glyph: space between the text and the glyph
    double bobEm = 0.0;          // Glyph: up-and-down sway amplitude
    double swayDeg = 0.0;        // Glyph: rocking amplitude
    double swayHz = 2.0;         // Glyph: sway frequency
};

// Particles a slot throws off its fragments: sparks, stars, dust, smoke, confetti, rings or a
// glyph. A burst fires as each fragment arrives (In) or leaves (Out) at `at` of its own motion;
// "during" keeps emitting while it moves (and for the whole window in a Loop). Lengths in em,
// times in seconds, angles in degrees (0 = right, -90 = up). Deterministic: same frame, same dots.
struct TextParticleSpec
{
    enum class Trigger { Burst, During };
    enum class Origin { Center, Area, Top, Bottom, Left, Right, Baseline };
    enum class Shape { Dot, Star, Spark, Ring, Square, Heart, Smoke, Confetti, Flare, Triangle, Glyph };

    Trigger trigger = Trigger::Burst;
    bool perBlock = false;    // one emitter at the block's centre instead of one per fragment
    double at = 0.0;          // Burst: when, as a fraction of the fragment's motion
    int count = 8;            // Burst: particles per emitter
    double rate = 20.0;       // During: particles per second per emitter
    Origin origin = Origin::Center;
    Shape shape = Shape::Dot;
    QString glyph;            // Glyph: emoji or symbol
    QList<QColor> colors;     // picked per particle; empty → the fill colour
    double sizeMin = 0.05, sizeMax = 0.12;   // em
    double speedMin = 0.6, speedMax = 1.8;   // em / s
    double angle = -90.0;     // mean direction
    double spread = 360.0;    // full cone width
    double gravity = 0.0;     // em / s², + falls
    double drag = 0.0;        // 1 / s, exponential slow-down
    double lifeMin = 0.4, lifeMax = 0.9;     // s
    double grow = 1.0;        // size at the end of life over the start
    double spin = 0.0;        // deg / s, signed per particle at random
    double fadeIn = 0.0;      // fraction of life spent fading in
    double glow = 0.0;        // 0..1 halo
    bool additive = false;    // light adds up (sparks, fire)
    bool behind = false;      // drawn under the text (smoke)
    quint32 seed = 1;
};

enum class TextAnimSlotKind { In, Out, Loop };

// One of the three gallery slots. A preset id plus typed param overrides, or an inline animator
// list when the slot was authored directly (MCP, Lottie import).
struct TextAnimationSlot
{
    QString presetId;
    QMap<QString, VectorSlotValue> params;
    QList<TextAnimator> animators;
    QList<TextParticleSpec> particles; // inline slots only; a preset brings its own
    TimeUs delayUs = 0;    // In: after the window start; Out: before the window end
    TimeUs durationUs = 0; // Curves progress length; 0 = derive from the stagger selectors
    TimeUs periodUs = 0;   // Loop: 0 = progress spans the whole window, else periodic
    bool enabled = true;

    bool isActive() const { return enabled && (!presetId.isEmpty() || !animators.isEmpty()); }
};

enum class TextAnchorGrouping { Character, Word, Line, All };

struct TextAnimationSet
{
    TextAnimationSlot in;
    TextAnimationSlot out;
    TextAnimationSlot loop;
    TextCaret caret;
    TextAnchorGrouping anchorGrouping = TextAnchorGrouping::Character;
    QPointF anchorAlignment; // -1..1 inside the anchor box

    bool isActive() const { return in.isActive() || out.isActive() || loop.isActive(); }
};

// Enum spellings shared by the project file, the presets and MCP.
QString textSelectorDriverToString(TextSelectorDriver driver);
TextSelectorDriver textSelectorDriverFromString(const QString &driver);
QString textSelectorDomainToString(TextSelectorDomain domain);
// Accepts the gallery unit names too: block, character, word, line.
TextSelectorDomain textSelectorDomainFromString(const QString &domain);
QString textSelectorUnitsToString(TextSelectorUnits units);
TextSelectorUnits textSelectorUnitsFromString(const QString &units);
QString textSelectorShapeToString(TextSelectorShape shape);
TextSelectorShape textSelectorShapeFromString(const QString &shape);
QString textSelectorModeToString(TextSelectorMode mode);
TextSelectorMode textSelectorModeFromString(const QString &mode);
QString textWiggleWaveToString(TextWiggleWave wave);
TextWiggleWave textWiggleWaveFromString(const QString &wave);
QString textLengthUnitToString(TextLengthUnit unit);
TextLengthUnit textLengthUnitFromString(const QString &unit);
QString textAnchorGroupingToString(TextAnchorGrouping grouping);
TextAnchorGrouping textAnchorGroupingFromString(const QString &grouping);
QString textAnimSlotKindToString(TextAnimSlotKind kind);
TextAnimSlotKind textAnimSlotKindFromString(const QString &kind);
QString textCaretShapeToString(TextCaret::Shape shape);
TextCaret::Shape textCaretShapeFromString(const QString &shape);
QJsonObject textParticleSpecToJson(const TextParticleSpec &spec);
TextParticleSpec textParticleSpecFromJson(const QJsonObject &o);

// JSON. A constant param is written as a plain number, a curve as {value, curve}. Defaults are
// omitted on write and restored on read, so preset files stay short.
QJsonValue textAnimParamToJson(const TextAnimParam &param);
TextAnimParam textAnimParamFromJson(const QJsonValue &value, double fallback);
QJsonValue textEaseSpecToJson(const TextEaseSpec &ease);
TextEaseSpec textEaseSpecFromJson(const QJsonValue &value);
QJsonObject textRangeSelectorToJson(const TextRangeSelector &selector);
TextRangeSelector textRangeSelectorFromJson(const QJsonObject &o);
QJsonObject textAnimatorToJson(const TextAnimator &animator);
TextAnimator textAnimatorFromJson(const QJsonObject &o);
QJsonObject textCaretToJson(const TextCaret &caret);
TextCaret textCaretFromJson(const QJsonObject &o);
QJsonObject textAnimationSlotToJson(const TextAnimationSlot &slot);
TextAnimationSlot textAnimationSlotFromJson(const QJsonObject &o);
QJsonObject textAnimationSetToJson(const TextAnimationSet &set);
TextAnimationSet textAnimationSetFromJson(const QJsonObject &o);
// Everything that changes the evaluated motion (cache keys).
quint64 textAnimationSetHash(const TextAnimationSet &set);

namespace textanim {

// What the layout knows about one drawn fragment (grapheme cluster, or a whole word when the
// layout was not split). Fragments arrive in reading order, grouped by line.
struct FragmentInfo
{
    int charIndex = 0;     // grapheme ordinal in the source text, spaces included
    int nonSpaceIndex = 0; // ordinal among drawn fragments
    int wordIndex = 0;
    int lineIndex = 0;
    double advance = 0.0;  // render px
    double ascent = 0.0;   // render px
    int textStart = 0;
    int textLength = 0;
};

struct Domains
{
    int chars = 0;
    int nonSpaceChars = 0;
    int words = 0;
    int lines = 0;
};

// Per-fragment result. dx/dy already include the tracking / line-spacing / collapse shifts.
struct FragmentProps
{
    double dx = 0.0;
    double dy = 0.0;
    double scaleX = 1.0;
    double scaleY = 1.0;
    double rotation = 0.0;
    double skew = 0.0;
    double rotationX = 0.0;
    double rotationY = 0.0;
    double opacity = 1.0;
    double fillOpacity = 1.0;
    double strokeOpacity = 1.0;
    double blurPx = 0.0;
    double tracking = 0.0; // the raw per-fragment tracking that produced part of dx
    double lineSpacing = 0.0;
    double strokeWidthDelta = 0.0;
    std::optional<QColor> fillColor;
    std::optional<QColor> strokeColor;
    double wipeProgress = -1.0; // revealed fraction 0..1; -1 = no wipe
    double wipeAngle = -90.0;
    double wipeSoftness = 0.3;
    bool hidden = false;
};

// Whole-layer motion (animators whose selectors are all domain All). Rides on the GPU layer.
struct BlockProps
{
    double dx = 0.0;
    double dy = 0.0;
    double scale = 1.0;
    double rotation = 0.0;
    double rotationX = 0.0; // the whole layer turned in depth (rides on the GPU layer's 3D pose)
    double rotationY = 0.0;
    double opacity = 1.0;
    double blurPx = 0.0;
    double wipeProgress = -1.0;
    double wipeAngle = -90.0;
    double wipeSoftness = 0.3;
};

struct CaretState
{
    bool visible = false;
    int afterFragment = -1; // -1 = before the first fragment
    int line = 0;
    double widthPx = 0.0;
    double heightPx = 0.0;
    QColor color;
    TextCaret::Shape shape = TextCaret::Shape::Bar; // the resolved caret's, preset or style
    QString glyph;
    double gapPx = 0.0;
    double bobPx = 0.0;     // Glyph: this frame's sway
    double swayDeg = 0.0;
};

// One live particle. x/y are render px from its emitter's anchor: the fragment's cell centre at
// rest (fragment >= 0) or the block's ink centre (-1).
struct ParticleState
{
    int fragment = -1;
    int look = 0;           // index into Frame::particleLooks
    double x = 0.0;
    double y = 0.0;
    double sizePx = 0.0;
    double rotation = 0.0;  // degrees
    double heading = 0.0;   // degrees, direction of travel (sparks stretch along it)
    double speedPx = 0.0;   // current speed, render px / s
    double alpha = 1.0;
    QColor color;
};

struct Frame
{
    QList<FragmentProps> props; // index-parallel with the fragments handed in
    BlockProps block;
    CaretState caret;
    QList<TextParticleSpec> particleLooks; // shape / glyph / glow / blend of each spec in use
    QList<ParticleState> particles;
    bool collapseHidden = false;
    bool isStatic = true;  // nothing moves at this instant and nothing is time-driven
    quint64 poseHash = 0;  // quantised props, for cache keys of held poses
};

struct EvalContext
{
    TimeUs windowStartUs = 0;    // clip start, or the cue start for subtitles
    TimeUs windowDurationUs = 0;
    TimeUs timelineUs = 0;
    double emPx = 64.0;          // pixelSize × renderScale
    double boxWidthPx = 0.0;     // layout rect, render px
    double boxHeightPx = 0.0;
    double renderScale = 1.0;
    double alignFactor = 0.5;    // 0 left, 0.5 centre, 1 right
    int activeWordIndex = -1;    // karaoke
    QColor baseFillColor = Qt::white;
    QColor baseStrokeColor = Qt::black;
};

// The three resolved after preset resolution (TextAnimationPreset turns a preset id + params into
// animators; inline resolved pass through).
struct ResolvedSlots
{
    QList<TextAnimator> in;
    QList<TextAnimator> out;
    QList<TextAnimator> loop;
    QList<TextParticleSpec> inParticles;
    QList<TextParticleSpec> outParticles;
    QList<TextParticleSpec> loopParticles;
};

Frame evaluateTextAnimation(const TextAnimationSet &set, const ResolvedSlots &resolved,
                            const QList<FragmentInfo> &fragments, const Domains &domains,
                            const EvalContext &ctx);

// Building blocks, exposed for tests.
// Coverage of one domain index for a Curves selector at `progress` (0..1). Skottie's shape maths.
double rangeSelectorCoverage(const TextRangeSelector &selector, int domainIndex, int domainSize,
                             double progress);
// Coverage for a Stagger selector: `elapsedUs` is the time since the slot's origin for an In
// (or the time *until* the slot's end for an Out, with `slot` already mirrored).
double staggerCoverage(const TextRangeSelector &selector, double slot, TimeUs elapsedUs);
// The stagger slot a fragment fires in, as a fractional index, and the largest slot for a count.
double reindexForOrder(int index, int count, TextAnimOrder order, quint32 seed);
double maxReindex(int count, TextAnimOrder order);
// Unit cubic through (0,0), c1, c2, (1,1) evaluated at x (clamped to 0..1).
double unitCubic(const QPointF &c1, const QPointF &c2, double x);

// How far any fragment can stray from its resting pose over the whole animation: the bleed the
// renderer reserves. A pure function of the animators, never of time.
struct Bounds
{
    double maxDx = 0.0;
    double maxDy = 0.0;
    double maxBlurPx = 0.0;
    double maxScale = 1.0;
    double maxRotationDeg = 0.0;
    double maxTrackingPx = 0.0;
    double maxRotation3dDeg = 0.0;
    double maxParticlePx = 0.0; // farthest a particle reaches from its emitter, plus its size
};
// `caret`, when given, adds room for a glyph caret riding after the text.
Bounds animationBounds(const ResolvedSlots &resolved, const EvalContext &ctx, const TextCaret *caret = nullptr);

} // namespace textanim
} // namespace drift
