#include "LottiePreviewImageProvider.h"

#include "core/VectorSource.h"
#include "engine/VectorClipRenderer.h"
#include "engine/VectorInspect.h"

#include <QCache>
#include <QFileInfo>
#include <QMutex>
#include <QMutexLocker>
#include <QPainter>
#include <QUrl>
#include <QUrlQuery>

namespace {

QMutex g_sheetMutex;
// Counted per sheet: a 24-frame grid of 96 px cells is about 0.9 MB, so this holds a page of
// recently hovered stickers without growing with the catalog.
QCache<QString, QImage> g_sheetCache(32);

void setSize(QSize *size, const QImage &image)
{
    if (size)
        *size = image.size();
}

} // namespace

LottiePreviewImageProvider::LottiePreviewImageProvider()
    : QQuickImageProvider(QQuickImageProvider::Image)
{
}

QImage LottiePreviewImageProvider::requestImage(const QString &id, QSize *size, const QSize &requestedSize)
{
    Q_UNUSED(requestedSize);
    {
        QMutexLocker lock(&g_sheetMutex);
        if (const QImage *hit = g_sheetCache.object(id)) {
            setSize(size, *hit);
            return *hit;
        }
    }

    // The path is percent-encoded by the caller, so a '?' in it cannot be mistaken for the query.
    const qsizetype queryAt = id.indexOf(QLatin1Char('?'));
    const QString path = QUrl::fromPercentEncoding(id.left(queryAt < 0 ? id.size() : queryAt).toUtf8());
    const QUrlQuery query(queryAt < 0 ? QString() : id.mid(queryAt + 1));
    const int frameW = qBound(16, query.queryItemValue(QStringLiteral("w")).toInt(), 256);
    const int frameH = qBound(16, query.queryItemValue(QStringLiteral("h")).toInt(), 256);
    const int frames = qBound(1, query.queryItemValue(QStringLiteral("frames")).toInt(), 48);
    const int columns = qMin(6, frames);
    const int rows = (frames + columns - 1) / columns;

    if (!QFileInfo(path).isFile()) {
        setSize(size, {});
        return {};
    }
    drift::VectorSource source;
    source.kind = drift::VectorKind::Lottie;
    source.path = path;
    if (!drift::vec::probeVectorSource(source)) {
        setSize(size, {});
        return {};
    }

    QImage sheet(frameW * columns, frameH * rows, QImage::Format_ARGB32_Premultiplied);
    sheet.fill(Qt::transparent);
    QPainter p(&sheet);
    for (int i = 0; i < frames; ++i) {
        // The last frame stops short of 1.0: a loop's end usually equals its start, and drawing
        // both would hold that pose for two frames on every pass.
        const double at = double(i) / double(frames);
        const QImage frame = drift::vec::renderThumbnail(source, QSize(frameW, frameH), at);
        if (!frame.isNull())
            p.drawImage((i % columns) * frameW, (i / columns) * frameH, frame);
    }
    p.end();

    {
        QMutexLocker lock(&g_sheetMutex);
        g_sheetCache.insert(id, new QImage(sheet));
    }
    setSize(size, sheet);
    return sheet;
}
