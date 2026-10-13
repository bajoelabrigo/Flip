#include "CubeLut.h"

#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QList>
#include <QMutex>
#include <QMutexLocker>

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <cstring>

namespace drift {

namespace {

// A number in the file's own notation: '.' decimals, optional exponent, never the locale's.
bool parseNumber(const QByteArray &token, float *out)
{
    if (token.isEmpty())
        return false;
    bool ok = false;
    const double v = token.toDouble(&ok); // QByteArray::toDouble is locale-independent ("C")
    if (!ok || !std::isfinite(v))
        return false;
    *out = float(v);
    return true;
}

QList<QByteArray> tokens(const QByteArray &line)
{
    QList<QByteArray> out;
    for (const QByteArray &t : line.simplified().split(' ')) {
        if (!t.isEmpty())
            out.append(t);
    }
    return out;
}

float clamp01(float v)
{
    return v < 0.f ? 0.f : (v > 1.f ? 1.f : v);
}

QMutex &searchMutex()
{
    static QMutex mutex;
    return mutex;
}

QStringList &searchList()
{
    static QStringList dirs;
    return dirs;
}

} // namespace

void CubeLut::setSearchDirs(const QStringList &dirs)
{
    QMutexLocker lock(&searchMutex());
    searchList() = dirs;
}

QStringList CubeLut::searchDirs()
{
    QMutexLocker lock(&searchMutex());
    return searchList();
}

QString CubeLut::resolve(const QString &path)
{
    if (path.isEmpty())
        return {};
    if (QFileInfo::exists(path))
        return path;
    // Saved on Windows and opened elsewhere (or the other way round): either separator.
    QString name = path;
    name.replace(QLatin1Char('\\'), QLatin1Char('/'));
    name = name.section(QLatin1Char('/'), -1);
    if (name.isEmpty())
        return {};
    for (const QString &dir : searchDirs()) {
        const QString candidate = QDir(dir).filePath(name);
        if (QFileInfo::exists(candidate))
            return candidate;
    }
    return {};
}

CubeLut CubeLut::parse(const QByteArray &text, QString *error)
{
    auto fail = [error](const QString &message) {
        if (error)
            *error = message;
        return CubeLut{};
    };

    CubeLut lut;
    int declared3d = 0;
    int declared1d = 0;
    lut.rgb.reserve(1024);
    int lineNumber = 0;
    for (QByteArray line : text.split('\n')) {
        ++lineNumber;
        const int hash = line.indexOf('#');
        if (hash >= 0)
            line.truncate(hash);
        line = line.trimmed();
        if (line.isEmpty())
            continue;

        const char first = line.at(0);
        const bool numeric = (first >= '0' && first <= '9') || first == '-' || first == '+' || first == '.';
        if (numeric) {
            if (declared3d == 0 && declared1d == 0)
                return fail(QCoreApplication::translate("CubeLut", "The table starts before LUT_3D_SIZE or LUT_1D_SIZE says how big it is."));
            const QList<QByteArray> parts = tokens(line);
            float v[3];
            if (parts.size() != 3 || !parseNumber(parts[0], &v[0]) || !parseNumber(parts[1], &v[1])
                || !parseNumber(parts[2], &v[2])) {
                return fail(QCoreApplication::translate("CubeLut", "Line %1 is not three numbers (red, green, blue).").arg(lineNumber));
            }
            if (lut.rgb.size() >= lut.entryCount() * 3)
                return fail(QCoreApplication::translate("CubeLut", "The table has more rows than its size says (%1).").arg(lut.entryCount()));
            lut.rgb.append(v[0]);
            lut.rgb.append(v[1]);
            lut.rgb.append(v[2]);
            continue;
        }

        const QList<QByteArray> parts = tokens(line);
        const QByteArray key = parts.first().toUpper();
        if (key == "TITLE") {
            const int open = line.indexOf('"');
            const int close = line.lastIndexOf('"');
            lut.title = QString::fromUtf8(open >= 0 && close > open ? line.mid(open + 1, close - open - 1)
                                                                    : line.mid(5).trimmed());
        } else if (key == "LUT_3D_SIZE" || key == "LUT_1D_SIZE") {
            if (declared3d || declared1d)
                return fail(QCoreApplication::translate("CubeLut", "The file declares more than one table; only one per file is supported."));
            bool ok = false;
            const int n = parts.size() == 2 ? parts[1].toInt(&ok) : 0;
            const bool is3d = key == "LUT_3D_SIZE";
            const int max = is3d ? kMaxCube3dSize : kMaxCube1dSize;
            if (!ok || n < 2 || n > max) {
                return fail(is3d ? QCoreApplication::translate("CubeLut", "LUT_3D_SIZE must be between 2 and %1.").arg(max)
                                 : QCoreApplication::translate("CubeLut", "LUT_1D_SIZE must be between 2 and %1.").arg(max));
            }
            lut.is3d = is3d;
            lut.size = n;
            (is3d ? declared3d : declared1d) = n;
            lut.rgb.reserve(lut.entryCount() * 3);
        } else if (key == "DOMAIN_MIN" || key == "DOMAIN_MAX") {
            float v[3];
            if (parts.size() != 4 || !parseNumber(parts[1], &v[0]) || !parseNumber(parts[2], &v[1])
                || !parseNumber(parts[3], &v[2])) {
                return fail(QCoreApplication::translate("CubeLut", "%1 needs three numbers.").arg(QString::fromLatin1(key)));
            }
            float *target = key == "DOMAIN_MIN" ? lut.domainMin : lut.domainMax;
            std::copy(v, v + 3, target);
        } else if (key == "LUT_3D_INPUT_RANGE" || key == "LUT_1D_INPUT_RANGE") {
            float lo = 0.f;
            float hi = 1.f;
            if (parts.size() != 3 || !parseNumber(parts[1], &lo) || !parseNumber(parts[2], &hi))
                return fail(QCoreApplication::translate("CubeLut", "%1 needs two numbers.").arg(QString::fromLatin1(key)));
            std::fill(lut.domainMin, lut.domainMin + 3, lo);
            std::fill(lut.domainMax, lut.domainMax + 3, hi);
        } else {
            // Other keywords (LUT_IN_VIDEO_RANGE, vendor tags) do not change the table.
        }
    }

    if (lut.size == 0)
        return fail(QCoreApplication::translate("CubeLut", "This is not a .cube LUT: it has no LUT_3D_SIZE or LUT_1D_SIZE line."));
    for (int c = 0; c < 3; ++c) {
        if (!(lut.domainMax[c] > lut.domainMin[c]))
            return fail(QCoreApplication::translate("CubeLut", "DOMAIN_MAX must be above DOMAIN_MIN on every channel."));
    }
    if (lut.rgb.size() != lut.entryCount() * 3) {
        return fail(QCoreApplication::translate("CubeLut", "The table is incomplete: it has %1 of the %2 rows its size needs.")
                        .arg(lut.rgb.size() / 3)
                        .arg(lut.entryCount()));
    }
    if (error)
        error->clear();
    return lut;
}

CubeLut CubeLut::load(const QString &path, QString *error)
{
    QFile file(path);
    if (!file.exists()) {
        if (error)
            *error = QCoreApplication::translate("CubeLut", "The LUT file is not there any more: %1").arg(QFileInfo(path).fileName());
        return {};
    }
    if (file.size() > kMaxCubeFileBytes) {
        if (error)
            *error = QCoreApplication::translate("CubeLut", "The LUT file is too large (over 64 MB).");
        return {};
    }
    if (!file.open(QIODevice::ReadOnly)) {
        if (error)
            *error = QCoreApplication::translate("CubeLut", "The LUT file could not be opened: %1").arg(file.errorString());
        return {};
    }
    CubeLut lut = parse(file.readAll(), error);
    if (lut.isValid() && lut.title.isEmpty())
        lut.title = QFileInfo(path).completeBaseName();
    return lut;
}

QImage CubeLut::toTexture() const
{
    if (!isValid())
        return {};
    const int w = is3d ? size * size : size;
    const int h = is3d ? size : 1;
    QImage image(w, h, QImage::Format_RGBA64);
    auto to16 = [](float v) { return quint16(std::lround(clamp01(v) * 65535.f)); };
    for (int i = 0; i < entryCount(); ++i) {
        int x = i;
        int y = 0;
        if (is3d) {
            const int r = i % size;
            const int g = (i / size) % size;
            const int b = i / (size * size);
            x = b * size + r;
            y = g;
        }
        QRgba64 px = QRgba64::fromRgba64(to16(rgb[i * 3]), to16(rgb[i * 3 + 1]), to16(rgb[i * 3 + 2]), 65535);
        reinterpret_cast<QRgba64 *>(image.scanLine(y))[x] = px;
    }
    return image;
}

void CubeLut::lookup(const float in[3], float out[3]) const
{
    float p[3];
    for (int c = 0; c < 3; ++c)
        p[c] = clamp01((in[c] - domainMin[c]) / (domainMax[c] - domainMin[c]));
    const int n = size;
    if (!is3d) {
        for (int c = 0; c < 3; ++c) {
            const float f = p[c] * float(n - 1);
            const int i0 = std::min(int(f), n - 2);
            const float t = f - float(i0);
            out[c] = rgb[i0 * 3 + c] * (1.f - t) + rgb[(i0 + 1) * 3 + c] * t;
        }
        return;
    }
    int i0[3];
    float t[3];
    for (int c = 0; c < 3; ++c) {
        const float f = p[c] * float(n - 1);
        i0[c] = std::min(int(f), n - 2);
        t[c] = f - float(i0[c]);
    }
    auto at = [&](int r, int g, int b, int c) { return rgb[((b * n + g) * n + r) * 3 + c]; };
    for (int c = 0; c < 3; ++c) {
        float acc = 0.f;
        for (int corner = 0; corner < 8; ++corner) {
            const int dr = corner & 1;
            const int dg = (corner >> 1) & 1;
            const int db = (corner >> 2) & 1;
            const float w = (dr ? t[0] : 1.f - t[0]) * (dg ? t[1] : 1.f - t[1]) * (db ? t[2] : 1.f - t[2]);
            acc += w * at(i0[0] + dr, i0[1] + dg, i0[2] + db, c);
        }
        out[c] = acc;
    }
}

QImage CubeLut::apply(const QImage &image, double intensity) const
{
    if (!isValid() || image.isNull())
        return image;
    QImage out = image.convertToFormat(QImage::Format_ARGB32);
    const float k = float(std::clamp(intensity, 0.0, 1.0));
    for (int y = 0; y < out.height(); ++y) {
        QRgb *row = reinterpret_cast<QRgb *>(out.scanLine(y));
        for (int x = 0; x < out.width(); ++x) {
            const QRgb px = row[x];
            const float in[3] = {qRed(px) / 255.f, qGreen(px) / 255.f, qBlue(px) / 255.f};
            float lut[3];
            lookup(in, lut);
            auto mix = [&](int c) { return int(std::lround(clamp01(in[c] + (lut[c] - in[c]) * k) * 255.f)); };
            row[x] = qRgba(mix(0), mix(1), mix(2), qAlpha(px));
        }
    }
    return out;
}

} // namespace drift
