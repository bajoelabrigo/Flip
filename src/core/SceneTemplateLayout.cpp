#include "SceneTemplateLayout.h"

#include "core/TimelineOps.h"

namespace drift {

namespace {

// value → value * scale + offset, tangents included (their dy is in value units).
void mapTrack(KeyframeTrack<double> &track, double scale, double offset, double implicitValue)
{
    if (track.isEmpty()) {
        track.setKeyframe(0, implicitValue * scale + offset);
        return;
    }
    KeyframeTrack<double> mapped;
    mapped.copySettingsFrom(track);
    const QMap<TimeUs, Keyframe<double>> &keys = track.keyframes();
    for (auto it = keys.constBegin(); it != keys.constEnd(); ++it) {
        Keyframe<double> key = it.value();
        key.value = key.value * scale + offset;
        key.inDy *= scale;
        key.outDy *= scale;
        mapped.setKeyframe(it.key(), key);
    }
    track = mapped;
}

void scaleKeyed(QMap<QString, KeyframeTrack<double>> &keyframes, const QString &name, double scale)
{
    auto it = keyframes.find(name);
    if (it != keyframes.end() && !it->isEmpty())
        mapTrack(*it, scale, 0.0, 0.0);
}

} // namespace

void scaleTemplateLayout(QList<Track> &tracks, int fromW, int fromH, int toW, int toH)
{
    if (fromW <= 0 || fromH <= 0 || toW <= 0 || toH <= 0 || (fromW == toW && fromH == toH))
        return;
    const double scale = qMin(double(toW) / fromW, double(toH) / fromH);
    const double offsetX = (toW - fromW * scale) / 2.0;
    const double offsetY = (toH - fromH * scale) / 2.0;
    for (Track &track : tracks) {
        if (track.type == TrackType::Audio)
            continue;
        for (Clip &clip : track.clips) {
            if (clip.type == ClipType::Audio)
                continue;
            // A box that is the canvas itself (transform layers) follows the canvas, not the art.
            if (clipBoxIsCanvasReferenced(clip))
                continue;
            mapTrack(clip.transformX, scale, offsetX, 0.0);
            mapTrack(clip.transformY, scale, offsetY, 0.0);
            mapTrack(clip.transformW, scale, 0.0, fromW);
            mapTrack(clip.transformH, scale, 0.0, fromH);
            if (!clip.positionZ.isEmpty())
                mapTrack(clip.positionZ, scale, 0.0, 0.0);
            if (clip.type == ClipType::Text || clip.type == ClipType::Subtitle) {
                scaleTextStyle(clip.textStyle, scale);
            } else if (clip.type == ClipType::Shape) {
                clip.shapeStyle.cornerRadius *= scale;
                scaleKeyed(clip.shapeStyle.keyframes, QStringLiteral("cornerRadius"), scale);
            }
        }
    }
}

QRectF coverSourceFrame(const QSizeF &mediaSize, const QSizeF &slotSize, const QRectF &within)
{
    if (mediaSize.width() <= 0 || mediaSize.height() <= 0 || slotSize.width() <= 0
        || slotSize.height() <= 0 || within.width() <= 0 || within.height() <= 0) {
        return within;
    }
    const double mediaAspect = (mediaSize.width() * within.width()) / (mediaSize.height() * within.height());
    const double slotAspect = slotSize.width() / slotSize.height();
    QRectF frame = within;
    if (mediaAspect > slotAspect) {
        // Wider than the slot: keep the full height, take the middle of the width.
        const double w = within.width() * slotAspect / mediaAspect;
        frame.setX(within.x() + (within.width() - w) / 2.0);
        frame.setWidth(w);
    } else if (mediaAspect < slotAspect) {
        const double h = within.height() * mediaAspect / slotAspect;
        frame.setY(within.y() + (within.height() - h) / 2.0);
        frame.setHeight(h);
    }
    return frame;
}

} // namespace drift
