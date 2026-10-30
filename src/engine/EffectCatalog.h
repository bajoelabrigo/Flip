#pragma once

#include "core/Effect.h"
#include "core/EffectPreset.h"
#include "GpuEffectDefinition.h"

#include <QList>
#include <QMap>
#include <QString>
#include <QVariant>

// Engine-side preset entry: core metadata plus libavfilter / compositor / GPU wiring.
struct EffectPresetEntry
{
    drift::EffectPresetMeta meta;
    QString filterName;                    // single-filter name, e.g. "eq"
    QString graphTemplate;                 // optional multi-filter template with {{key}} placeholders
    QMap<QString, QVariant> fixedParams;   // always applied, not exposed as sliders
    bool isGpu = false;                    // true for file-based GPU effect packages
    bool isModel3d = false;                // true for "backend": "model3d" face-prop packages
    bool isFaceSwap = false;               // true for "backend": "faceswap" packages
    bool needsFace = false;                // "requires": "face" — engine injects u_face* uniforms
    bool needsDepth = false;               // "requires": "depth" — engine binds the depth map
    bool needsMask = false;                // "requires": "mask" — engine binds the clip's masks
    bool needsPose = false;                // "requires": "pose" — engine injects u_body* uniforms
    // Layer styles (0.26): room the effect draws outside the layer's box, in layer px — the sum of
    // these parameters' values plus `paddingExtra` ("padding": {"params": [...], "extra": n}).
    // The layer's texture is grown by it before the chain runs, so a shadow or a glow is not cut.
    QStringList paddingParams;
    double paddingExtra = 0.0;
    // Squash & Stretch (0.26): parameters in % of the layer's longer side ("percentParams"), for a
    // deform that reaches as far as the layer is big.
    QStringList paddingPercentParams;
    double paddingPercentFactor = 1.0; // "percentFactor": how much room each % gives (Bend: degrees)
    drift::GpuEffectDefinition gpu;        // valid when isGpu && gpu.valid; packageDir also set for model3d
    int catalogOrder = 0;                  // lower sorts first in the browser catalog
    QString thumbnailPath;                 // absolute path to package thumbnail (optional)
};

// Backward-compatible alias used across the codebase.
using EffectParamDef = drift::EffectParamSpec;
using EffectDef = EffectPresetEntry;

const QList<EffectPresetEntry> &effectCatalog();
const EffectPresetEntry *effectDefForId(const QString &id);

// Merge fixed + instance parameters for a clip effect.
QMap<QString, QVariant> resolvedEffectParameters(const drift::Effect &effect, const EffectPresetEntry &def);

// Build a libavfilter graph fragment for one catalog effect instance (empty when compositor-only / GPU).
QString buildFilterGraphForEffect(const drift::Effect &effect, const EffectPresetEntry *def = nullptr);

// All stable preset ids (for tests and validation).
QStringList effectPresetIds();

// Browser categories in display order (stable id + user-facing label).
QList<QPair<QString, QString>> effectCategories();
QString effectCategoryLabel(const QString &categoryId);

// Reload file-based GPU packages from the given roots (or defaultSearchPaths when empty).
// Built-in libav/compositor presets are always present; GPU packages are appended.
void reloadEffectCatalog(const QStringList &packageRoots = {});
