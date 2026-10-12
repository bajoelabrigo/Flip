#pragma once

#include <QImage>
#include <QQuickImageProvider>

// An animated sticker (a Lottie document on disk) played back as a sprite grid, so its card can
// move on hover instead of showing only its still:
// image://lottie/<percent-encoded path>?w=96&h=96&frames=24. Frames run left to right, six to a
// row, spanning the whole animation once; AnimatedSprite reads them in that order.
class LottiePreviewImageProvider : public QQuickImageProvider
{
public:
    LottiePreviewImageProvider();

    QImage requestImage(const QString &id, QSize *size, const QSize &requestedSize) override;
};
