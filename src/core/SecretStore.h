#pragma once

#include <QString>

class QSettings;

// API keys and tokens kept in QSettings. On Windows the value is sealed with DPAPI, so it only
// decrypts under the same Windows user; elsewhere it is stored as before, until those platforms
// get a keychain. Plaintext written by older builds is read as-is and re-sealed on first read.
namespace drift::secrets {

// Stored form of a sealed value: this prefix, then base64 of the DPAPI blob.
inline constexpr char kSealedPrefix[] = "dpapi:v1:";

bool sealingAvailable();

QString readSecret(QSettings &settings, const QString &key);
// An empty value removes the key.
void writeSecret(QSettings &settings, const QString &key, const QString &value);

} // namespace drift::secrets
