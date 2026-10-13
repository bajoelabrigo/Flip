#pragma once

#include <QString>

namespace drift {

// SoftLight is the W3C/Photoshop soft light (a gentle overlay), saved as "soft-light".
enum class BlendMode { Normal, Multiply, Screen, Overlay, Add, Darken, Lighten, SoftLight };

QString blendModeToString(BlendMode mode);
BlendMode blendModeFromString(const QString &mode);

} // namespace drift
