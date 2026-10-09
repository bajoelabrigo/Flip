#pragma once

#include <QByteArray>
#include <QFile>
#include <QList>
#include <QPair>
#include <QString>

#include <zlib.h>

// Writes a stored (uncompressed) zip — the minimum a .lottie bundle needs — for tests that
// exercise the readers without shipping binary fixtures.
inline bool writeStoredZip(const QString &path, const QList<QPair<QString, QByteArray>> &entries)
{
    QByteArray out;
    QByteArray central;
    auto put16 = [](QByteArray &b, quint16 v) { b.append(char(v & 0xff)); b.append(char(v >> 8)); };
    auto put32 = [&](QByteArray &b, quint32 v) { put16(b, quint16(v & 0xffff)); put16(b, quint16(v >> 16)); };
    for (const auto &entry : entries) {
        const QByteArray name = entry.first.toUtf8();
        const QByteArray &data = entry.second;
        const quint32 crc = quint32(crc32(0, reinterpret_cast<const Bytef *>(data.constData()), uInt(data.size())));
        const quint32 offset = quint32(out.size());
        put32(out, 0x04034b50); put16(out, 20); put16(out, 0); put16(out, 0); put16(out, 0); put16(out, 0);
        put32(out, crc); put32(out, quint32(data.size())); put32(out, quint32(data.size()));
        put16(out, quint16(name.size())); put16(out, 0);
        out.append(name); out.append(data);
        put32(central, 0x02014b50); put16(central, 20); put16(central, 20); put16(central, 0); put16(central, 0);
        put16(central, 0); put16(central, 0);
        put32(central, crc); put32(central, quint32(data.size())); put32(central, quint32(data.size()));
        put16(central, quint16(name.size())); put16(central, 0); put16(central, 0); put16(central, 0); put16(central, 0);
        put32(central, 0); put32(central, offset);
        central.append(name);
    }
    const quint32 cdOffset = quint32(out.size());
    out.append(central);
    put32(out, 0x06054b50); put16(out, 0); put16(out, 0);
    put16(out, quint16(entries.size())); put16(out, quint16(entries.size()));
    put32(out, quint32(central.size())); put32(out, cdOffset); put16(out, 0);
    QFile file(path);
    return file.open(QIODevice::WriteOnly) && file.write(out) == out.size();
}

// Raw deflate (no zlib header), the encoding zip method 8 stores.
inline QByteArray rawDeflate(const QByteArray &data)
{
    z_stream strm{};
    if (deflateInit2(&strm, Z_BEST_COMPRESSION, Z_DEFLATED, -MAX_WBITS, 8, Z_DEFAULT_STRATEGY) != Z_OK)
        return {};
    QByteArray out(int(deflateBound(&strm, uLong(data.size()))), Qt::Uninitialized);
    strm.next_in = reinterpret_cast<Bytef *>(const_cast<char *>(data.constData()));
    strm.avail_in = uInt(data.size());
    strm.next_out = reinterpret_cast<Bytef *>(out.data());
    strm.avail_out = uInt(out.size());
    const int ret = deflate(&strm, Z_FINISH);
    out.resize(int(strm.total_out));
    deflateEnd(&strm);
    return ret == Z_STREAM_END ? out : QByteArray();
}

// A one-entry deflated zip whose payload and declared size are taken as given, so a test can
// hand the reader a truncated stream or a header that lies about the size.
inline bool writeDeflatedZip(const QString &path, const QString &entryName, const QByteArray &payload,
                             quint32 declaredSize, quint32 crc)
{
    QByteArray out;
    QByteArray central;
    auto put16 = [](QByteArray &b, quint16 v) { b.append(char(v & 0xff)); b.append(char(v >> 8)); };
    auto put32 = [&](QByteArray &b, quint32 v) { put16(b, quint16(v & 0xffff)); put16(b, quint16(v >> 16)); };
    const QByteArray name = entryName.toUtf8();
    put32(out, 0x04034b50); put16(out, 20); put16(out, 0); put16(out, 8); put16(out, 0); put16(out, 0);
    put32(out, crc); put32(out, quint32(payload.size())); put32(out, declaredSize);
    put16(out, quint16(name.size())); put16(out, 0);
    out.append(name); out.append(payload);
    put32(central, 0x02014b50); put16(central, 20); put16(central, 20); put16(central, 0); put16(central, 8);
    put16(central, 0); put16(central, 0);
    put32(central, crc); put32(central, quint32(payload.size())); put32(central, declaredSize);
    put16(central, quint16(name.size())); put16(central, 0); put16(central, 0); put16(central, 0); put16(central, 0);
    put32(central, 0); put32(central, 0);
    central.append(name);
    const quint32 cdOffset = quint32(out.size());
    out.append(central);
    put32(out, 0x06054b50); put16(out, 0); put16(out, 0); put16(out, 1); put16(out, 1);
    put32(out, quint32(central.size())); put32(out, cdOffset); put16(out, 0);
    QFile file(path);
    return file.open(QIODevice::WriteOnly) && file.write(out) == out.size();
}
