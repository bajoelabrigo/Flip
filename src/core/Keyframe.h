#pragma once

#include "Bezier.h"
#include "Time.h"

#include <QMap>
#include <QString>
#include <QtMath>

#include <cmath>
#include <type_traits>

namespace drift {

// Named tangent shapes. These are *presets* that write handles onto a single key, not a
// separate interpolation system — except Hold, which is a step discontinuity and therefore
// not expressible as a bezier at all, so it stays a flag on the key.
enum class Interpolation { Linear, Hold, Ease };

inline QString interpolationToString(Interpolation mode)
{
    switch (mode) {
    case Interpolation::Hold:
        return QStringLiteral("hold");
    case Interpolation::Ease:
        return QStringLiteral("ease");
    case Interpolation::Linear:
    default:
        return QStringLiteral("linear");
    }
}

inline Interpolation interpolationFromString(const QString &mode)
{
    if (mode == QLatin1String("hold"))
        return Interpolation::Hold;
    if (mode == QLatin1String("ease"))
        return Interpolation::Ease;
    return Interpolation::Linear;
}

// A keyframe and its outgoing/incoming tangents.
//
// Handles are stored relative to the key, in curve space: dx in microseconds, dy in the
// property's own units. `outDx` runs forward (>= 0), `inDx` back (<= 0). Zero-length handles
// evaluate to a straight line, because x and y then share the same blend weights — so a
// default-constructed key is exactly the old Linear behaviour.
template<typename T>
struct Keyframe
{
    T value{};
    double inDx = 0.0;
    double inDy = 0.0;
    double outDx = 0.0;
    double outDy = 0.0;
    bool corner = false; // when false the editor holds the two tangents collinear
    bool hold = false;   // step: keep this value until the next key

    bool operator==(const Keyframe &other) const
    {
        return value == other.value && qFuzzyCompare(inDx + 1.0, other.inDx + 1.0)
            && qFuzzyCompare(inDy + 1.0, other.inDy + 1.0)
            && qFuzzyCompare(outDx + 1.0, other.outDx + 1.0)
            && qFuzzyCompare(outDy + 1.0, other.outDy + 1.0) && corner == other.corner
            && hold == other.hold;
    }
};

// After Effects' expressions most used in motion graphics (0.26), as a behaviour of the track
// itself rather than code: every animatable property gets them, and the timeline, preview and
// export read them through evaluateAt like any key. They combine as `loopOut() + time * speed +
// wiggle()` would, in that order. Only double tracks use them.
enum class LoopMode { None, Cycle, PingPong, Offset, Continue };

struct TrackBehavior
{
    // loopOut(): after the last key the keys from the first to the last repeat (Cycle), go back
    // and forth (PingPong), repeat adding the change each time (Offset), or carry on at the speed
    // the last key leaves with (Continue).
    LoopMode loop = LoopMode::None;
    // time * speed: units of the property per second, added from the clip's start.
    double speed = 0.0;
    // wiggle(frequency, amount): a smooth random offset up to `wiggleAmount` either way,
    // changing `wiggleFrequency` times a second; `wiggleSeed` picks another sequence.
    double wiggleFrequency = 0.0;
    double wiggleAmount = 0.0;
    int wiggleSeed = 0;
    // Motion Tools' Elastic and Bounce (0.26): where the keys come to rest (after the last one, or
    // between two equal ones) the value overshoots and settles (Elastic) or bounces back off the
    // key (Bounce), from the speed it arrived with. Amplitude in seconds of that speed, frequency
    // in swings a second, decay per second.
    enum class Settle { None, Elastic, Bounce };
    Settle settle = Settle::None;
    double settleAmplitude = 0.05;
    double settleFrequency = 3.0;
    double settleDecay = 5.0;
    // Bounce as a ball (0.26): the share of the speed each hop leaves with, gravity as a multiple of
    // the one the fall itself implies, how many hops at most, and «Jump In/Out» (hops on the far
    // side of the key, as if passing through it, instead of back off it).
    double bounceElasticity = 0.6;
    double bounceGravity = 1.0;
    int bounceMaxJumps = 5;
    bool bounceJumpOut = false;
    // A JavaScript expression run last, on the value with everything above (empty = none).
    QString expression;

    bool hasWiggle() const { return wiggleFrequency > 0.0 && wiggleAmount != 0.0; }
    bool isActive() const
    {
        return loop != LoopMode::None || speed != 0.0 || hasWiggle() || settle != Settle::None || !expression.isEmpty();
    }
    bool operator==(const TrackBehavior &o) const
    {
        return loop == o.loop && speed == o.speed && wiggleFrequency == o.wiggleFrequency
               && wiggleAmount == o.wiggleAmount && wiggleSeed == o.wiggleSeed && settle == o.settle
               && settleAmplitude == o.settleAmplitude && settleFrequency == o.settleFrequency
               && settleDecay == o.settleDecay && bounceElasticity == o.bounceElasticity
               && bounceGravity == o.bounceGravity && bounceMaxJumps == o.bounceMaxJumps
               && bounceJumpOut == o.bounceJumpOut && expression == o.expression;
    }
};

// After Effects' expressions (0.26): the evaluator the engine installs (engine/ExpressionEngine),
// and what it reads other layers from on this thread. Core cannot see the engine, hence a hook.
using ExpressionEvaluator = double (*)(const QString &expression, double value, double seconds);
inline ExpressionEvaluator &expressionEvaluatorRef()
{
    static ExpressionEvaluator evaluator = nullptr;
    return evaluator;
}
struct ExpressionContext
{
    const void *project = nullptr; // a drift::Project
    qint64 timelineUs = -1;        // the frame's timeline time; -1 = the evaluating clip's own
};
inline ExpressionContext &expressionContext()
{
    thread_local ExpressionContext context;
    return context;
}

// Smooth noise in about -1..1, the same for the same (x, seed): what wiggle() rides on.
inline double behaviorNoise(double x, int seed)
{
    const auto hash = [seed](qint64 i) {
        quint64 h = quint64(i) * 0x9E3779B97F4A7C15ull ^ (quint64(quint32(seed)) * 0xC2B2AE3D27D4EB4Full);
        h ^= h >> 31;
        h *= 0xBF58476D1CE4E5B9ull;
        h ^= h >> 27;
        return double(h & 0xFFFFFF) / double(0xFFFFFF) * 2.0 - 1.0;
    };
    const double f = std::floor(x);
    const double t = x - f;
    const double s = t * t * t * (t * (t * 6.0 - 15.0) + 10.0);
    const qint64 i = qint64(f);
    // Two octaves, the second at half the amplitude, as AE's wiggle defaults to.
    const double a = hash(i) + (hash(i + 1) - hash(i)) * s;
    const double x2 = x * 2.0 + 17.0;
    const double f2 = std::floor(x2);
    const double t2 = x2 - f2;
    const double s2 = t2 * t2 * t2 * (t2 * (t2 * 6.0 - 15.0) + 10.0);
    const qint64 j = qint64(f2) + 7919;
    const double b = hash(j) + (hash(j + 1) - hash(j)) * s2;
    return (a + 0.5 * b) / 1.5;
}

QString loopModeToString(LoopMode mode);
LoopMode loopModeFromString(const QString &mode);

template<typename T>
class KeyframeTrack
{
public:
    bool isEmpty() const { return m_values.isEmpty(); }

    // Animation can be switched off for a property without discarding its keys: the track then
    // holds its first key's value for the whole clip, and switching it back on restores the
    // animation exactly as it was.
    bool enabled() const { return m_enabled; }
    void setEnabled(bool enabled) { m_enabled = enabled; }

    // After Effects' stopwatch (0.25): the keys were put there on purpose (a diamond, the
    // stopwatch, a value typed while animated), so even a lone key at the clip's start is an
    // animation and shows. Without it, such a key is just where a static value is kept.
    bool stopwatch() const { return m_stopwatch; }
    void setStopwatch(bool on) { m_stopwatch = on; }

    const TrackBehavior &behavior() const { return m_behavior; }
    void setBehavior(const TrackBehavior &behavior) { m_behavior = behavior; }
    // Everything but the keys: for a track rebuilt key by key (rescaled, retimed, mapped). Copying
    // only enabled() dropped the 0.26 behaviours and the stopwatch without a word.
    template<typename U>
    void copySettingsFrom(const KeyframeTrack<U> &other)
    {
        m_enabled = other.enabled();
        m_stopwatch = other.stopwatch();
        m_behavior = other.behavior();
    }

    void setKeyframe(TimeUs time, const T &value)
    {
        auto it = m_values.find(time);
        if (it != m_values.end()) {
            it->value = value; // retune in place; the key keeps the tangents it was given
            return;
        }
        Keyframe<T> key;
        key.value = value;
        m_values.insert(time, key);
    }

    void setKeyframe(TimeUs time, const Keyframe<T> &key) { m_values.insert(time, key); }

    void removeKeyframe(TimeUs time) { m_values.remove(time); }

    // Pin whatever the curve already evaluates to at `time` as a real key there. Used when a clip
    // is cut: the new half has to start from the value the animation had at the cut, not from
    // whichever neighbouring key happens to survive.
    void pinValueAt(TimeUs time)
    {
        if (m_values.isEmpty() || m_values.contains(time))
            return;
        setKeyframe(time, evaluateKeys(time));
    }

    // Move every key along the clip's own timeline. Key times are clip-relative, so a clip that
    // keeps its material but changes where it starts — the tail of a split, for one — has to carry
    // its curve with it or the animation replays at the wrong moment. Keys that land before the
    // clip's start are dropped; the curve still evaluates from whatever key survives.
    void shiftBy(TimeUs delta)
    {
        if (delta == 0 || m_values.isEmpty())
            return;
        QMap<TimeUs, Keyframe<T>> moved;
        for (auto it = m_values.constBegin(); it != m_values.constEnd(); ++it) {
            const TimeUs at = it.key() + delta;
            if (at >= 0)
                moved.insert(at, it.value());
        }
        m_values = moved;
    }

    const QMap<TimeUs, Keyframe<T>> &keyframes() const { return m_values; }

    // Mutable access for the curve editor. Null when there is no key exactly at `time`.
    Keyframe<T> *keyframeRef(TimeUs time)
    {
        auto it = m_values.find(time);
        return it == m_values.end() ? nullptr : &it.value();
    }

    // Returns the key time within tolerance, or -1 if none.
    TimeUs nearestKeyframe(TimeUs time, TimeUs tolerance) const
    {
        TimeUs best = -1;
        TimeUs bestDist = tolerance + 1;
        for (auto it = m_values.constBegin(); it != m_values.constEnd(); ++it) {
            const TimeUs d = qAbs(it.key() - time);
            if (d < bestDist) {
                bestDist = d;
                best = it.key();
            }
        }
        return bestDist <= tolerance ? best : TimeUs{-1};
    }

    // Writes the tangents a named shape implies onto one key. Ease uses flat tangents a third
    // of the way to each neighbour, which reproduces the smoothstep the old track-wide Ease
    // mode produced, exactly.
    void setEasing(TimeUs time, Interpolation mode)
    {
        auto it = m_values.find(time);
        if (it == m_values.end())
            return;

        it->hold = mode == Interpolation::Hold;
        it->corner = false;
        if (mode == Interpolation::Ease) {
            const TimeUs toPrev = it == m_values.begin() ? 0 : time - std::prev(it).key();
            auto next = std::next(it);
            const TimeUs toNext = next == m_values.end() ? 0 : next.key() - time;
            it->inDx = -static_cast<double>(toPrev) / 3.0;
            it->outDx = static_cast<double>(toNext) / 3.0;
            it->inDy = 0.0;
            it->outDy = 0.0;
        } else {
            it->inDx = 0.0;
            it->inDy = 0.0;
            it->outDx = 0.0;
            it->outDy = 0.0;
        }
    }

    // Best-effort classification for highlighting the preset chips. Hand-dragged tangents
    // match nothing, which is what leaves every chip unlit.
    Interpolation easingAt(TimeUs time) const
    {
        auto it = m_values.constFind(time);
        if (it == m_values.constEnd())
            return Interpolation::Linear;
        if (it->hold)
            return Interpolation::Hold;

        const bool flat = qFuzzyIsNull(it->inDy) && qFuzzyIsNull(it->outDy);
        if (!flat)
            return Interpolation::Linear; // no chip will match; treated as custom by callers
        if (qFuzzyIsNull(it->inDx) && qFuzzyIsNull(it->outDx))
            return Interpolation::Linear;
        return Interpolation::Ease;
    }

    // True when the key's tangents are not one of the presets, so the UI can show "custom".
    bool hasCustomTangents(TimeUs time) const
    {
        auto it = m_values.constFind(time);
        if (it == m_values.constEnd() || it->hold)
            return false;
        if (!qFuzzyIsNull(it->inDy) || !qFuzzyIsNull(it->outDy))
            return true;
        if (qFuzzyIsNull(it->inDx) && qFuzzyIsNull(it->outDx))
            return false;

        // Flat tangents still only count as Ease at the canonical third.
        const TimeUs time_ = it.key();
        const TimeUs toPrev = it == m_values.constBegin() ? 0 : time_ - std::prev(it).key();
        auto next = std::next(it);
        const TimeUs toNext = next == m_values.constEnd() ? 0 : next.key() - time_;
        const double wantIn = -static_cast<double>(toPrev) / 3.0;
        const double wantOut = static_cast<double>(toNext) / 3.0;
        return !qFuzzyCompare(it->inDx + 1.0, wantIn + 1.0)
            || !qFuzzyCompare(it->outDx + 1.0, wantOut + 1.0);
    }

    T evaluateAt(TimeUs time) const
    {
        if constexpr (std::is_same_v<T, double>) {
            if (m_enabled && m_behavior.isActive() && !m_values.isEmpty())
                return evaluateWithBehavior(time);
        }
        return evaluateKeys(time);
    }

    // The keys alone, without the track's behaviour.
    T evaluateKeys(TimeUs time) const
    {
        if (m_values.isEmpty())
            return T{};
        if (!m_enabled)
            return m_values.constBegin()->value; // frozen at the first key

        auto it = m_values.lowerBound(time);
        if (it == m_values.end())
            return std::prev(it)->value;

        if (it.key() == time || it == m_values.begin())
            return it->value;

        const auto prev = std::prev(it);
        if (prev->hold)
            return prev->value;

        const double t0 = static_cast<double>(prev.key());
        const double t1 = static_cast<double>(it.key());
        const double span = t1 - t0;
        if (span <= 0.0)
            return it->value;

        const double v0 = static_cast<double>(prev->value);
        const double v1 = static_cast<double>(it->value);

        // Straight segment: skip the solve entirely. This is the common case.
        if (qFuzzyIsNull(prev->outDx) && qFuzzyIsNull(prev->outDy) && qFuzzyIsNull(it->inDx)
            && qFuzzyIsNull(it->inDy)) {
            return lerp(prev->value, it->value, (static_cast<double>(time) - t0) / span);
        }

        // Clamp the handles inside the segment so the curve stays single-valued in time and
        // the bisection below has something monotonic to search.
        const double x1 = qBound(t0, t0 + prev->outDx, t1);
        const double x2 = qBound(t0, t1 + it->inDx, t1);
        const double s = bezierParameterForX(t0, x1, x2, t1, static_cast<double>(time));
        const double y = cubicBezier(v0, v0 + prev->outDy, v1 + it->inDy, v1, s);
        return static_cast<T>(y);
    }

    // Break Qt implicit sharing so a cross-thread reader cannot race a detach on the live copy.
    void detachSharedData() { m_values.detach(); }

private:
    // Elastic / Bounce: the swing after the key the curve last came to rest on.
    double settleOffset(TimeUs time) const
    {
        auto next = m_values.upperBound(time);
        if (next == m_values.begin())
            return 0.0;
        auto rest = std::prev(next);
        if (rest == m_values.begin())
            return 0.0;
        // Only where the value then holds still: after the last key, or before an equal one.
        if (next != m_values.end() && !qFuzzyCompare(double(next->value) + 1.0, double(rest->value) + 1.0))
            return 0.0;
        const TimeUs at = rest.key();
        const TimeUs step = qMin<TimeUs>(10000, qMax<TimeUs>(1, at - std::prev(rest).key()));
        const double velocity = (double(evaluateKeys(at)) - double(evaluateKeys(at - step))) / (double(step) / 1e6);
        if (qAbs(velocity) < 1e-9)
            return 0.0;
        const double t = double(time - at) / 1e6;
        if (m_behavior.settle == TrackBehavior::Settle::Bounce) {
            // A ball: it leaves the key at a share of the speed it came in with, under a gravity
            // taken from the fall itself (reaching that speed over the previous stretch), so each
            // hop climbs back e² of the height of the one before and they shorten until it rests.
            // (A tiny sine wobble read as a shiver, not a bounce: Jorge, 0.26.)
            const double elasticity = qBound(0.0, m_behavior.bounceElasticity, 0.98);
            const double fall = qMax(0.05, double(at - std::prev(rest).key()) / 1e6);
            const double speed = qAbs(velocity);
            const double gravity = speed / fall * qMax(0.05, m_behavior.bounceGravity);
            // Back off the key, or (Jump In/Out) on through to its far side.
            const double side = (velocity > 0 ? -1.0 : 1.0) * (m_behavior.bounceJumpOut ? -1.0 : 1.0);
            double hop = elasticity * speed;
            double left = t;
            for (int n = 0; n < qBound(0, m_behavior.bounceMaxJumps, 50) && hop > 1e-3; ++n) {
                const double flight = 2.0 * hop / gravity;
                if (left < flight)
                    return side * (hop * left - 0.5 * gravity * left * left);
                left -= flight;
                hop *= elasticity;
            }
            return 0.0;
        }
        const double wave = std::sin(m_behavior.settleFrequency * t * 6.2831853) / std::exp(m_behavior.settleDecay * t);
        const double swing = velocity * m_behavior.settleAmplitude * wave;
        return swing;
    }

    double evaluateWithBehavior(TimeUs time) const
    {
        const TimeUs first = m_values.firstKey();
        const TimeUs last = m_values.lastKey();
        const TimeUs span = last - first;
        double value = 0.0;
        if (m_behavior.loop != LoopMode::None && span > 0 && time > last) {
            const TimeUs from = time - first;
            const qint64 lap = from / span;
            const TimeUs into = from % span;
            switch (m_behavior.loop) {
            case LoopMode::Cycle:
                value = double(evaluateKeys(first + into));
                break;
            case LoopMode::PingPong:
                value = double(evaluateKeys(lap % 2 == 0 ? first + into : last - into));
                break;
            case LoopMode::Offset:
                value = double(evaluateKeys(first + into))
                        + double(lap) * (double(m_values.last().value) - double(m_values.first().value));
                break;
            case LoopMode::Continue: {
                const TimeUs step = qMin<TimeUs>(span, 10000);
                const double slope = (double(evaluateKeys(last)) - double(evaluateKeys(last - step))) / double(step);
                value = double(m_values.last().value) + slope * double(time - last);
                break;
            }
            case LoopMode::None:
                break;
            }
        } else {
            value = double(evaluateKeys(time));
        }
        if (m_behavior.settle != TrackBehavior::Settle::None && m_values.size() >= 2)
            value += settleOffset(time);
        const double seconds = double(time) / 1e6;
        value += m_behavior.speed * seconds;
        if (m_behavior.hasWiggle())
            value += m_behavior.wiggleAmount * behaviorNoise(seconds * m_behavior.wiggleFrequency, m_behavior.wiggleSeed);
        if (!m_behavior.expression.isEmpty())
            if (ExpressionEvaluator evaluator = expressionEvaluatorRef())
                value = evaluator(m_behavior.expression, value, seconds);
        return value;
    }

    static double lerp(double a, double b, double t) { return a + (b - a) * t; }

    static float lerp(float a, float b, double t)
    {
        return static_cast<float>(a + (b - a) * static_cast<float>(t));
    }

    QMap<TimeUs, Keyframe<T>> m_values;
    bool m_enabled = true;
    bool m_stopwatch = false;
    TrackBehavior m_behavior;
};

} // namespace drift
