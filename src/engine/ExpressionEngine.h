#pragma once

#include <QString>

namespace drift {

class Project;

// After Effects' expressions (0.26): a property's JavaScript, run on top of its keys and behaviour.
// Installs the evaluator KeyframeTrack calls (core/Keyframe.h, expressionEvaluatorRef). Each thread
// gets its own QJSEngine, and each expression is compiled once per thread.
//
// In the expression: `value` (the property before the expression), `time` (seconds from the clip's
// start), `wiggle(freq, amount[, seed])`, `Math`, and `thisComp.layer("Name")` /
// `layer("Name")` with `.transform.position[0|1]`, `.transform.rotation`, `.transform.opacity`,
// `.transform.scale[0|1]`, `.transform.anchorPoint[0|1]` (also `.x`, `.y`, `.rotation`,
// `.opacity`, `.width`, `.height` directly). The last statement is the result.
void installExpressionEngine();

// Makes `project` the one layer("...") looks into on this thread, at timeline time `timelineUs`
// (-1: the evaluating clip's own time), until the returned guard goes away.
class ExpressionScope
{
public:
    ExpressionScope(const Project *project, qint64 timelineUs);
    ~ExpressionScope();
    ExpressionScope(const ExpressionScope &) = delete;
    ExpressionScope &operator=(const ExpressionScope &) = delete;

private:
    const void *m_previousProject;
    qint64 m_previousTime;
};

// For the editor: what is wrong with an expression (empty when it runs), evaluated once with
// value 0 at time 0 on the calling thread.
QString expressionError(const QString &expression);

} // namespace drift
