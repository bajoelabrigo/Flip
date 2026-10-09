#include "SecretStore.h"

#include <QByteArray>
#include <QSettings>

#ifdef Q_OS_WIN
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <wincrypt.h> // CryptProtectData / CryptUnprotectData (dpapi.h)
#endif

namespace drift::secrets {
namespace {

#ifdef Q_OS_WIN
QByteArray seal(const QByteArray &plain)
{
    DATA_BLOB in{static_cast<DWORD>(plain.size()), reinterpret_cast<BYTE *>(const_cast<char *>(plain.data()))};
    DATA_BLOB out{};
    if (!CryptProtectData(&in, L"Flip Studio", nullptr, nullptr, nullptr, CRYPTPROTECT_UI_FORBIDDEN, &out))
        return {};
    const QByteArray blob(reinterpret_cast<const char *>(out.pbData), static_cast<qsizetype>(out.cbData));
    LocalFree(out.pbData);
    return blob;
}

// Empty when the blob was sealed by another Windows user or machine, or is damaged.
QByteArray unseal(const QByteArray &blob)
{
    DATA_BLOB in{static_cast<DWORD>(blob.size()), reinterpret_cast<BYTE *>(const_cast<char *>(blob.data()))};
    DATA_BLOB out{};
    if (!CryptUnprotectData(&in, nullptr, nullptr, nullptr, nullptr, CRYPTPROTECT_UI_FORBIDDEN, &out))
        return {};
    const QByteArray plain(reinterpret_cast<const char *>(out.pbData), static_cast<qsizetype>(out.cbData));
    SecureZeroMemory(out.pbData, out.cbData);
    LocalFree(out.pbData);
    return plain;
}
#endif

QString stored(const QString &value)
{
#ifdef Q_OS_WIN
    const QByteArray blob = seal(value.toUtf8());
    if (!blob.isEmpty())
        return QLatin1String(kSealedPrefix) + QString::fromLatin1(blob.toBase64());
#endif
    return value;
}

} // namespace

bool sealingAvailable()
{
#ifdef Q_OS_WIN
    return true;
#else
    return false;
#endif
}

QString readSecret(QSettings &settings, const QString &key)
{
    const QString raw = settings.value(key).toString();
    if (raw.isEmpty())
        return {};
    if (raw.startsWith(QLatin1String(kSealedPrefix))) {
#ifdef Q_OS_WIN
        const QByteArray blob = QByteArray::fromBase64(raw.mid(qsizetype(sizeof(kSealedPrefix)) - 1).toLatin1());
        return QString::fromUtf8(unseal(blob));
#else
        return {};
#endif
    }
    // Written by a build before sealing existed: hand it back and seal it in place.
    if (sealingAvailable())
        settings.setValue(key, stored(raw));
    return raw;
}

void writeSecret(QSettings &settings, const QString &key, const QString &value)
{
    if (value.isEmpty())
        settings.remove(key);
    else
        settings.setValue(key, stored(value));
}

} // namespace drift::secrets
