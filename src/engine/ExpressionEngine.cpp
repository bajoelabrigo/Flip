#include "engine/ExpressionEngine.h"

#include "core/Clip.h"
#include "core/Keyframe.h"
#include "core/Project.h"

#include <QHash>
#include <QJSEngine>
#include <QJSValue>
#include <QObject>

#include <memory>

namespace drift {

namespace {

// What the JavaScript calls back into: smooth noise and other layers' properties.
class ExpressionHelper : public QObject
{
    Q_OBJECT
public:
    Q_INVOKABLE double noise(double x, int seed) const { return behaviorNoise(x, seed); }

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
};

// The scaffolding every expression runs inside. `__e` is the expression's own text, run by eval so
// its last statement is the result, with value / time / wiggle / layer in scope.
const char *const kPrelude = R"JS(
(function (__e) {
    return function (value, time) {
        function wiggle(freq, amount, seed) { return value + amount * __fx.noise(time * freq, seed || 0); }
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
        const QJSValue result = fn.call({QJSValue(value), QJSValue(seconds)});
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
    const QJSValue result = fn.call({QJSValue(0.0), QJSValue(0.0)});
    if (result.isError())
        return result.toString();
    const QJSValue scalar = result.isArray() ? result.property(0) : result;
    if (!std::isfinite(scalar.toNumber()))
        return QStringLiteral("The expression does not give a number");
    return {};
}

} // namespace drift

#include "ExpressionEngine.moc"
