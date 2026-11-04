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

namespace {

// Every visual clip's box, value → value * scale + offset.
void mapLayout(QList<Track> &tracks, int fromW, int fromH, double scale, double offsetX, double offsetY)
{
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

double valueAtKey(const KeyframeTrack<double> &track, TimeUs at, double implicitValue)
{
    return track.isEmpty() ? implicitValue : track.evaluateAt(at);
}

} // namespace

void scaleTemplateLayout(QList<Track> &tracks, int fromW, int fromH, int toW, int toH)
{
    if (fromW <= 0 || fromH <= 0 || toW <= 0 || toH <= 0 || (fromW == toW && fromH == toH))
        return;
    const double scale = qMin(double(toW) / fromW, double(toH) / fromH);
    mapLayout(tracks, fromW, fromH, scale, (toW - fromW * scale) / 2.0, (toH - fromH * scale) / 2.0);
}

void fitLowerThirdLayout(QList<Track> &tracks, int fromW, int fromH, int toW, int toH)
{
    if (fromW <= 0 || fromH <= 0 || toW <= 0 || toH <= 0)
        return;
    // What it draws: every visual clip's box at each of its keys (and at its start).
    QRectF art;
    for (const Track &track : std::as_const(tracks)) {
        if (track.type == TrackType::Audio)
            continue;
        for (const Clip &clip : track.clips) {
            if (clip.type == ClipType::Audio || clipBoxIsCanvasReferenced(clip))
                continue;
            QList<TimeUs> times{0};
            for (const KeyframeTrack<double> *t : {&clip.transformX, &clip.transformY, &clip.transformW, &clip.transformH})
                for (auto it = t->keyframes().constBegin(); it != t->keyframes().constEnd(); ++it)
                    times.append(it.key());
            for (const TimeUs at : std::as_const(times)) {
                const QRectF box(valueAtKey(clip.transformX, at, 0.0), valueAtKey(clip.transformY, at, 0.0),
                                 valueAtKey(clip.transformW, at, fromW), valueAtKey(clip.transformH, at, fromH));
                // A box as big as the canvas is a backdrop, not the art.
                if (box.width() <= 0 || box.height() <= 0 || (box.width() >= fromW * 0.98 && box.height() >= fromH * 0.98))
                    continue;
                art = art.isNull() ? box : art.united(box);
            }
        }
    }
    if (art.isNull() || art.width() <= 0 || art.height() <= 0) {
        scaleTemplateLayout(tracks, fromW, fromH, toW, toH);
        return;
    }
    // As wide as 92 % of the frame, never taller than a third of it, never more than twice its own size.
    const double scale = qMin(2.0, qMin(toW * 0.92 / art.width(), toH * 0.34 / art.height()));
    const double offsetX = (toW - art.width() * scale) / 2.0 - art.x() * scale;
    // Its bottom on the lower part of the frame: a Short keeps clear of the captions and buttons near the
    // bottom; a wide video sits on its usual lower third.
    const double bottom = toH > toW ? toH * 0.74 : toH * 0.88;
    const double offsetY = bottom - (art.y() + art.height()) * scale;
    mapLayout(tracks, fromW, fromH, scale, offsetX, offsetY);
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
