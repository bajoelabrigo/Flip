#include "engine/ExpressionEngine.h"

#include "core/Clip.h"
#include "core/Keyframe.h"
#include "core/Project.h"

#include <QCoreApplication>
#include <QHash>
#include <QJSEngine>
#include <QJSValue>
#include <QObject>

#include <chrono>
#include <condition_variable>
#include <memory>
#include <mutex>
#include <thread>
#include <unordered_map>

namespace drift {

namespace {

// Interrupts an expression that runs too long. A `while (true) {}` typed in the editor, or saved
// in a project or a Stock template, used to freeze the GUI, the preview and the export for good.
// One thread for the whole app; an engine is armed only while a call runs.
class ExpressionWatchdog
{
public:
    static ExpressionWatchdog &instance()
    {
        // Never destroyed: engines live in thread_local storage and can outlive any static.
        static ExpressionWatchdog *dog = new ExpressionWatchdog;
        return *dog;
    }

    void arm(QJSEngine *engine, std::chrono::milliseconds budget)
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        m_armed[engine] = std::chrono::steady_clock::now() + budget;
        m_wake.notify_one();
    }

    void disarm(QJSEngine *engine)
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        m_armed.erase(engine);
    }

private:
    ExpressionWatchdog()
    {
        std::thread([this]() { loop(); }).detach();
    }

    void loop()
    {
        std::unique_lock<std::mutex> lock(m_mutex);
        for (;;) {
            if (m_armed.empty()) {
                m_wake.wait(lock);
                continue;
            }
            auto next = std::chrono::steady_clock::time_point::max();
            for (const auto &entry : m_armed)
                next = std::min(next, entry.second);
            m_wake.wait_until(lock, next);
            const auto now = std::chrono::steady_clock::now();
            for (auto it = m_armed.begin(); it != m_armed.end();) {
                if (it->second <= now) {
                    // Thread-safe in QJSEngine: the running script throws at its next check.
                    it->first->setInterrupted(true);
                    it = m_armed.erase(it);
                } else {
                    ++it;
                }
            }
        }
    }

    std::mutex m_mutex;
    std::condition_variable m_wake;
    std::unordered_map<QJSEngine *, std::chrono::steady_clock::time_point> m_armed;
};

// An expression gets this long per call. Real ones take microseconds.
constexpr std::chrono::milliseconds kExpressionBudget{50};

// What the JavaScript calls back into: smooth noise and other layers' properties.
class ExpressionHelper : public QObject
{
    Q_OBJECT
public:
    Q_INVOKABLE double noise(double x, int seed) const { return behaviorNoise(x, seed); }

    // The property's own keys at another time (0.30): valueAtTime(), velocity.
    Q_INVOKABLE double selfAt(double seconds) const
    {
        const ExpressionSelf &self = expressionSelfRef();
        return self.keysAt ? self.keysAt(self.track, seconds) : 0.0;
    }

    Q_INVOKABLE double prop(const QString &layerName, const QString &prop, double seconds) const
    {
        const Project *project = static_cast<const Project *>(expressionContext().project);
        if (!project)
            return 0.0;
        for (const Track &track : project->tracks()) {
            for (const Clip &clip : track.clips) {
                if (clip.name != layerName)
                    continue;
                const TimeUs relative = expressionContext().timelineUs >= 0
                                            ? expressionContext().timelineUs - clip.timelineStart
                                            : TimeUs(seconds * 1e6);
                const auto at = [&](const KeyframeTrack<double> &t, double fallback) {
                    return t.isEmpty() ? fallback : t.evaluateAt(relative);
                };
                if (prop == QLatin1String("x"))
                    return at(clip.transformX, 0.0);
                if (prop == QLatin1String("y"))
                    return at(clip.transformY, 0.0);
                if (prop == QLatin1String("width"))
                    return at(clip.transformW, project->width());
                if (prop == QLatin1String("height"))
                    return at(clip.transformH, project->height());
                if (prop == QLatin1String("rotation"))
                    return at(clip.rotation, 0.0);
                if (prop == QLatin1String("opacity"))
                    return at(clip.opacity, 1.0) * 100.0;
                if (prop == QLatin1String("anchorX"))
                    return at(clip.anchorX, 0.5) * at(clip.transformW, project->width());
                if (prop == QLatin1String("anchorY"))
                    return at(clip.anchorY, 0.5) * at(clip.transformH, project->height());
                return 0.0;
            }
        }
        return 0.0;
    }

    // After Effects' content("…") (0.28): a part of a shape layer, found by name down the path of groups
    // (names joined by U+0001), its transform and size at the time.
    Q_INVOKABLE double partProp(const QString &layerName, const QString &path, const QString &prop, double seconds) const
    {
        const Project *project = static_cast<const Project *>(expressionContext().project);
        if (!project)
            return 0.0;
        const QStringList names = path.split(QChar(1));
        for (const Track &track : project->tracks()) {
            for (const Clip &clip : track.clips) {
                if (clip.name != layerName || !clip.shapeStyle.hasParts())
                    continue;
                const TimeUs relative = expressionContext().timelineUs >= 0
                                            ? expressionContext().timelineUs - clip.timelineStart
                                            : TimeUs(seconds * 1e6);
                const std::vector<ShapePart> *level = &clip.shapeStyle.parts;
                const ShapePart *found = nullptr;
                for (const QString &name : names) {
                    found = nullptr;
                    for (const ShapePart &part : *level) {
                        if (part.name == name) {
                            found = &part;
                            break;
                        }
                    }
                    if (!found)
                        return 0.0;
                    level = &found->children;
                }
                if (!found)
                    return 0.0;
                const ShapePart at = found->resolvedAt(relative);
                double value = 0.0;
                if (prop == QLatin1String("width"))
                    return at.width;
                if (prop == QLatin1String("height"))
                    return at.height;
                return shapePartScalar(at, prop, &value) ? value : 0.0;
            }
        }
        return 0.0;
    }
};

// The scaffolding every expression runs inside. `__e` is the expression's own text, run by eval so
// its last statement is the result, with value / time / wiggle / layer in scope.
const char *const kPrelude = R"JS(
(function (__e) {
    return function (value, time) {
        function wiggle(freq, amount, seed) { return value + amount * __fx.noise(time * freq, seed || 0); }
        // After Effects' interpolation and maths (0.30), on numbers and on [x, y] arrays alike.
        function __map(a, b, f) {
            if (Array.isArray(a) || Array.isArray(b)) {
                var n = Math.max(Array.isArray(a) ? a.length : 1, Array.isArray(b) ? b.length : 1), out = [];
                for (var i = 0; i < n; ++i)
                    out.push(f(Array.isArray(a) ? a[Math.min(i, a.length - 1)] : a, Array.isArray(b) ? b[Math.min(i, b.length - 1)] : b));
                return out;
            }
            return f(a, b);
        }
        function clamp(v, lo, hi) { return __map(v, 0, function (x) { return Math.min(Math.max(x, Math.min(lo, hi)), Math.max(lo, hi)); }); }
        function __interp(shape, t, tMin, tMax, v1, v2) {
            if (v1 === undefined) { v1 = tMin; v2 = tMax; tMin = 0; tMax = 1; }
            var u = tMax === tMin ? (t >= tMax ? 1 : 0) : (t - tMin) / (tMax - tMin);
            u = shape(Math.min(1, Math.max(0, u)));
            return __map(v1, v2, function (a, b) { return a + (b - a) * u; });
        }
        function linear(t, a, b, c, d) { return __interp(function (u) { return u; }, t, a, b, c, d); }
        function ease(t, a, b, c, d) { return __interp(function (u) { return u * u * (3 - 2 * u); }, t, a, b, c, d); }
        function easeIn(t, a, b, c, d) { return __interp(function (u) { return u * u; }, t, a, b, c, d); }
        function easeOut(t, a, b, c, d) { return __interp(function (u) { return 1 - (1 - u) * (1 - u); }, t, a, b, c, d); }
        function degreesToRadians(d) { return d * Math.PI / 180; }
        function radiansToDegrees(r) { return r * 180 / Math.PI; }
        function valueAtTime(t) { return __fx.selfAt(t); }
        var __h = 1 / 240;
        var velocity = (__fx.selfAt(time + __h) - __fx.selfAt(time - __h)) / (2 * __h);
        var speed = Math.abs(velocity);
        // Inside a longer expression the loop is the behaviour's (set alone, it becomes one).
        function loopOut() { return value; }
        function loopIn() { return value; }
        function __layer(name) {
            function g(p) { return __fx.prop(name, p, time); }
            var t = {};
            Object.defineProperty(t, "position", { get: function () { return [g("x"), g("y")]; } });
            Object.defineProperty(t, "rotation", { get: function () { return g("rotation"); } });
            Object.defineProperty(t, "opacity", { get: function () { return g("opacity"); } });
            Object.defineProperty(t, "scale", { get: function () { return [g("width"), g("height")]; } });
            Object.defineProperty(t, "anchorPoint", { get: function () { return [g("anchorX"), g("anchorY")]; } });
            var l = { transform: t };
            ["x", "y", "rotation", "opacity", "width", "height"].forEach(function (p) {
                Object.defineProperty(l, p, { get: function () { return g(p); } });
            });
            // After Effects' content("Rectangle 1"), and content("Group 1").content("Ellipse 1") inside groups.
            function __content(path) {
                function q(p) { return __fx.partProp(name, path.join(""), p, time); }
                var pt = {};
                Object.defineProperty(pt, "position", { get: function () { return [q("x"), q("y")]; } });
                Object.defineProperty(pt, "rotation", { get: function () { return q("rotation"); } });
                Object.defineProperty(pt, "opacity", { get: function () { return q("opacity"); } });
                Object.defineProperty(pt, "scale", { get: function () { return [q("scaleX"), q("scaleY")]; } });
                Object.defineProperty(pt, "anchorPoint", { get: function () { return [q("anchorX"), q("anchorY")]; } });
                Object.defineProperty(pt, "skew", { get: function () { return q("skew"); } });
                var c = { transform: pt, content: function (n) { return __content(path.concat([n])); } };
                Object.defineProperty(c, "size", { get: function () { return [q("width"), q("height")]; } });
                return c;
            }
            l.content = function (n) { return __content([n]); };
            return l;
        }
        var layer = __layer;
        var thisComp = { layer: __layer };
        return eval(__e);
    };
})
)JS";

struct ThreadEngine
{
    std::unique_ptr<QJSEngine> engine;
    QJSValue factory;
    QHash<QString, QJSValue> compiled;
    int depth = 0;
};

ThreadEngine &threadEngine()
{
    thread_local ThreadEngine t;
    if (!t.engine) {
        t.engine = std::make_unique<QJSEngine>();
        t.engine->installExtensions(QJSEngine::ConsoleExtension);
        auto *helper = new ExpressionHelper;
        helper->setParent(t.engine.get());
        t.engine->globalObject().setProperty(QStringLiteral("__fx"), t.engine->newQObject(helper));
        t.factory = t.engine->evaluate(QString::fromUtf8(kPrelude));
    }
    return t;
}

// The expression's function on this thread, compiled on first use; an error value if it does not parse.
QJSValue compiledFor(ThreadEngine &t, const QString &expression)
{
    auto it = t.compiled.constFind(expression);
    if (it != t.compiled.constEnd())
        return it.value();
    if (t.compiled.size() > 512)
        t.compiled.clear();
    QJSValue fn = t.factory.call({QJSValue(expression)});
    t.compiled.insert(expression, fn);
    return fn;
}

double evaluate(const QString &expression, double value, double seconds)
{
    ThreadEngine &t = threadEngine();
    // An expression that reads a layer whose expression reads this one would never end.
    if (t.depth > 4)
        return value;
    ++t.depth;
    const QJSValue fn = compiledFor(t, expression);
    double out = value;
    if (fn.isCallable()) {
        // Only the outermost call is timed: one reading another layer runs inside its budget.
        const bool outer = t.depth == 1;
        if (outer)
            ExpressionWatchdog::instance().arm(t.engine.get(), kExpressionBudget);
        const QJSValue result = fn.call({QJSValue(value), QJSValue(seconds)});
        if (outer) {
            ExpressionWatchdog::instance().disarm(t.engine.get());
            if (t.engine->isInterrupted()) {
                t.engine->setInterrupted(false);
                // Never run it again on this thread: the property keeps its keyframed value.
                t.compiled.insert(expression, QJSValue());
                --t.depth;
                return value;
            }
        }
        if (!result.isError()) {
            // A [x, y] answer on a scalar property takes its first entry.
            const QJSValue scalar = result.isArray() ? result.property(0) : result;
            const double number = scalar.toNumber();
            if (std::isfinite(number))
                out = number;
        }
    }
    --t.depth;
    return out;
}

} // namespace

void installExpressionEngine()
{
    expressionEvaluatorRef() = &evaluate;
}

ExpressionScope::ExpressionScope(const Project *project, qint64 timelineUs)
    : m_previousProject(expressionContext().project), m_previousTime(expressionContext().timelineUs)
{
    expressionContext().project = project;
    expressionContext().timelineUs = timelineUs;
}

ExpressionScope::~ExpressionScope()
{
    expressionContext().project = m_previousProject;
    expressionContext().timelineUs = m_previousTime;
}

QString expressionError(const QString &expression)
{
    if (expression.trimmed().isEmpty())
        return {};
    ThreadEngine &t = threadEngine();
    const QJSValue fn = compiledFor(t, expression);
    if (fn.isError())
        return fn.toString();
    if (!fn.isCallable())
        return QStringLiteral("not a function");
    ExpressionWatchdog::instance().arm(t.engine.get(), kExpressionBudget);
    const QJSValue result = fn.call({QJSValue(0.0), QJSValue(0.0)});
    ExpressionWatchdog::instance().disarm(t.engine.get());
    if (t.engine->isInterrupted()) {
        t.engine->setInterrupted(false);
        t.compiled.insert(expression, QJSValue());
        return QCoreApplication::translate("Expressions", "The expression takes too long (does it loop forever?)");
    }
    if (result.isError())
        return result.toString();
    const QJSValue scalar = result.isArray() ? result.property(0) : result;
    if (!std::isfinite(scalar.toNumber()))
        return QStringLiteral("The expression does not give a number");
    return {};
}

} // namespace drift

#include "ExpressionEngine.moc"
