#include "SceneTemplateLayout.h"

#include "core/TimelineOps.h"

#include <QHash>

#include <tuple>

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
void mapLayout(QList<Track> &tracks, int fromW, int fromH, double scale, double offsetX, double offsetY,
               const QList<const Clip *> &leave = {})
{
    for (Track &track : tracks) {
        if (track.type == TrackType::Audio)
            continue;
        for (Clip &clip : track.clips) {
            if (clip.type == ClipType::Audio)
                continue;
            // A box that is the canvas itself (transform layers) follows the canvas, not the art.
            if (clipBoxIsCanvasReferenced(clip) || leave.contains(&clip))
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

namespace {

// A box drawn over the whole canvas at every key (a backdrop, a shade, a flash): it keeps covering the canvas.
bool coversCanvas(const Clip &clip, int fromW, int fromH)
{
    QList<TimeUs> times{0};
    for (const KeyframeTrack<double> *t : {&clip.transformX, &clip.transformY, &clip.transformW, &clip.transformH})
        for (auto it = t->keyframes().constBegin(); it != t->keyframes().constEnd(); ++it)
            times.append(it.key());
    for (const TimeUs at : std::as_const(times)) {
        const double w = valueAtKey(clip.transformW, at, fromW);
        const double h = valueAtKey(clip.transformH, at, fromH);
        if (w < fromW * 0.98 || h < fromH * 0.98)
            return false;
    }
    return true;
}

} // namespace

void fitOverlayLayout(QList<Track> &tracks, int fromW, int fromH, int toW, int toH, OverlayFit fit)
{
    if (fromW <= 0 || fromH <= 0 || toW <= 0 || toH <= 0)
        return;
    const QRectF canvas(0, 0, fromW, fromH);
    // What it draws: every visual clip's box at each of its keys (and at its start), the part on the canvas (a
    // piece that slides in from outside is not drawn out there).
    QRectF art;
    QList<Clip *> backdrops;
    QList<const Clip *> leave;
    for (Track &track : tracks) {
        if (track.type == TrackType::Audio)
            continue;
        for (Clip &clip : track.clips) {
            if (clip.type == ClipType::Audio || clipBoxIsCanvasReferenced(clip))
                continue;
            const bool text = clip.type == ClipType::Text || clip.type == ClipType::Subtitle;
            if (clip.layoutRole == QLatin1String("backdrop")
                || (clip.layoutRole.isEmpty() && !text && coversCanvas(clip, fromW, fromH))) {
                backdrops.append(&clip);
                continue;
            }
            QList<TimeUs> times{0};
            for (const KeyframeTrack<double> *t : {&clip.transformX, &clip.transformY, &clip.transformW, &clip.transformH})
                for (auto it = t->keyframes().constBegin(); it != t->keyframes().constEnd(); ++it)
                    times.append(it.key());
            for (const TimeUs at : std::as_const(times)) {
                QRectF box(valueAtKey(clip.transformX, at, 0.0), valueAtKey(clip.transformY, at, 0.0),
                           valueAtKey(clip.transformW, at, fromW), valueAtKey(clip.transformH, at, fromH));
                box = box.normalized().intersected(canvas);
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
    const bool tall = toH > toW;
    double scale = 1.0;
    double offsetX = 0.0;
    double offsetY = 0.0;
    if (fit == OverlayFit::LowerThird) {
        // As wide as 92 % of the frame, never taller than a third of it, never more than twice its own size.
        scale = qMin(2.0, qMin(toW * 0.92 / art.width(), toH * 0.34 / art.height()));
        offsetX = (toW - art.width() * scale) / 2.0 - art.x() * scale;
        // Its bottom on the lower part of the frame: a Short keeps clear of the captions and buttons near the
        // bottom; a wide video sits on its usual lower third.
        const double bottom = tall ? toH * 0.74 : toH * 0.88;
        offsetY = bottom - (art.y() + art.height()) * scale;
    } else {
        // Same size against the short side (what reads the same on a phone and on a TV), kept where it was
        // (a corner stays a corner, the middle the middle), inside the part of the frame nothing covers: a Short
        // keeps clear of the captions and buttons at the bottom and on the right.
        const QRectF safe = tall ? QRectF(toW * 0.04, toH * 0.06, toW * 0.92, toH * 0.74)
                                 : QRectF(toW * 0.04, toH * 0.05, toW * 0.92, toH * 0.90);
        const double shortSide = double(qMin(toW, toH)) / qMax(1, qMin(fromW, fromH));
        scale = qMin(qMin(2.0, shortSide), qMin(safe.width() / art.width(), safe.height() / art.height()));
        const double w = art.width() * scale;
        const double h = art.height() * scale;
        double x = art.center().x() / fromW * toW - w / 2.0;
        double y = art.center().y() / fromH * toH - h / 2.0;
        x = qBound(safe.left(), x, safe.right() - w);
        y = qBound(safe.top(), y, safe.bottom() - h);
        offsetX = x - art.x() * scale;
        offsetY = y - art.y() * scale;
    }
    // The backdrops go on covering the frame: stretched to it, not moved with the art.
    const double sx = double(toW) / fromW;
    const double sy = double(toH) / fromH;
    for (Clip *clip : std::as_const(backdrops)) {
        if (clip->type == ClipType::Text || clip->type == ClipType::Subtitle) {
            // A word behind (a giant ghost, a wall of words) keeps its size and moves with the frame: its centre
            // goes where the frame takes it, so it is not squeezed into another wrap.
            QList<TimeUs> times{0};
            for (const KeyframeTrack<double> *t : {&clip->transformX, &clip->transformY, &clip->transformW, &clip->transformH})
                for (auto it = t->keyframes().constBegin(); it != t->keyframes().constEnd(); ++it)
                    times.append(it.key());
            const double w0 = valueAtKey(clip->transformW, 0, fromW);
            const double h0 = valueAtKey(clip->transformH, 0, fromH);
            mapTrack(clip->transformX, 1.0, (sx - 1.0) * (valueAtKey(clip->transformX, 0, 0.0) + w0 / 2.0), 0.0);
            mapTrack(clip->transformY, 1.0, (sy - 1.0) * (valueAtKey(clip->transformY, 0, 0.0) + h0 / 2.0), 0.0);
            leave.append(clip);
            continue;
        }
        mapTrack(clip->transformX, sx, 0.0, 0.0);
        mapTrack(clip->transformY, sy, 0.0, 0.0);
        mapTrack(clip->transformW, sx, 0.0, fromW);
        mapTrack(clip->transformH, sy, 0.0, fromH);
        if (clip->type == ClipType::Shape) {
            clip->shapeStyle.cornerRadius *= qMin(sx, sy);
            scaleKeyed(clip->shapeStyle.keyframes, QStringLiteral("cornerRadius"), qMin(sx, sy));
        }
        leave.append(clip);
    }
    // A photo that fills the frame behind the design and shows only through a mask (a word, a strip, a window):
    // the photo goes on filling the frame, the window follows the design (it would be stretched with the frame).
    QHash<QString, const Clip *> backdropById;
    for (const Clip *clip : std::as_const(backdrops))
        backdropById.insert(clip->id, clip);
    for (Track &track : tracks) {
        for (Clip &clip : track.clips) {
            if (clip.type != ClipType::Adjustment || clip.adjustmentKind != AdjustmentKind::Mask
                || clip.linkedClipId.isEmpty() || !backdropById.contains(clip.linkedClipId))
                continue;
            const auto remap = [&](double norm, bool horizontal, bool size) {
                const double from = horizontal ? fromW : fromH;
                const double to = horizontal ? toW : toH;
                const double offset = horizontal ? offsetX : offsetY;
                return size ? norm * from * scale / to : (norm * from * scale + offset) / to;
            };
            Mask &m = clip.mask;
            m.x = remap(m.x, true, false);
            m.y = remap(m.y, false, false);
            m.w = remap(m.w, true, true);
            m.h = remap(m.h, false, true);
            for (const auto &[key, horizontal, size] : {std::tuple{QStringLiteral("x"), true, false},
                                                       std::tuple{QStringLiteral("y"), false, false},
                                                       std::tuple{QStringLiteral("w"), true, true},
                                                       std::tuple{QStringLiteral("h"), false, true}}) {
                auto it = m.keyframes.find(key);
                if (it == m.keyframes.end() || it->isEmpty())
                    continue;
                const double from = horizontal ? fromW : fromH;
                const double to = horizontal ? toW : toH;
                const double offset = horizontal ? offsetX : offsetY;
                mapTrack(*it, from * scale / to, size ? 0.0 : offset / to, 0.0);
            }
        }
    }
    mapLayout(tracks, fromW, fromH, scale, offsetX, offsetY, leave);
}

void fitLowerThirdLayout(QList<Track> &tracks, int fromW, int fromH, int toW, int toH)
{
    fitOverlayLayout(tracks, fromW, fromH, toW, toH, OverlayFit::LowerThird);
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
