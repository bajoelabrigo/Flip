#include "MotionTrack.h"

#include "Clip.h"

#include <QJsonArray>

#include <algorithm>
#include <cmath>

namespace drift {

namespace {

// A key every this many samples: smooth enough to follow, few enough to retouch.
constexpr int kKeyEvery = 2;
// Half-width of the moving average that takes the sub-pixel shimmer out of a match.
constexpr int kSmoothRadius = 2;

QJsonArray rectToJson(const QRectF &r)
{
    return QJsonArray{r.x(), r.y(), r.width(), r.height()};
}

QRectF rectFromJson(const QJsonValue &value)
{
    const QJsonArray a = value.toArray();
    if (a.size() != 4)
        return {};
    return QRectF(a.at(0).toDouble(), a.at(1).toDouble(), a.at(2).toDouble(), a.at(3).toDouble());
}

double valueAt(const KeyframeTrack<double> &track, TimeUs relative, double fallback)
{
    return track.isEmpty() ? fallback : track.evaluateAt(relative);
}

// Where a clip sits on the canvas at a timeline time, in project pixels (the compositor's defaults:
// no keys means the whole canvas).
QRectF canvasRect(const Clip &clip, TimeUs timelineUs, int projectW, int projectH)
{
    const TimeUs relative = timelineUs - clip.timelineStart;
    return QRectF(valueAt(clip.transformX, relative, 0.0), valueAt(clip.transformY, relative, 0.0),
                  valueAt(clip.transformW, relative, double(projectW)),
                  valueAt(clip.transformH, relative, double(projectH)));
}

QRectF toCanvas(const QRectF &n, const Clip &video, TimeUs timelineUs, int projectW, int projectH)
{
    const QRectF v = canvasRect(video, timelineUs, projectW, projectH);
    return QRectF(v.x() + n.x() * v.width(), v.y() + n.y() * v.height(), n.width() * v.width(),
                  n.height() * v.height());
}

} // namespace

int MotionTrack::lostCount() const
{
    return int(std::count_if(samples.cbegin(), samples.cend(), [](const MotionTrackSample &s) {
        return s.state == MotionTrackSample::State::Lost;
    }));
}

QJsonObject motionTrackToJson(const MotionTrack &track)
{
    // One compact row per sample: [sourceUs, x, y, w, h, score, state]. A minute of 30 fps is a few
    // tens of kilobytes.
    QJsonArray rows;
    for (const MotionTrackSample &s : track.samples) {
        rows.append(QJsonArray{double(s.sourceUs), s.rect.x(), s.rect.y(), s.rect.width(), s.rect.height(),
                               std::round(s.score * 1000.0) / 1000.0, int(s.state)});
    }
    return QJsonObject{
        {QStringLiteral("version"), MotionTrack::kVersion},
        {QStringLiteral("mode"), track.mode},
        {QStringLiteral("sourceClipId"), track.sourceClipId},
        {QStringLiteral("sourcePath"), track.sourcePath},
        {QStringLiteral("faceSlot"), track.faceSlot},
        {QStringLiteral("direction"), track.direction},
        {QStringLiteral("followScale"), track.followScale},
        {QStringLiteral("keepDistance"), track.keepDistance},
        {QStringLiteral("anchorSourceUs"), double(track.anchorSourceUs)},
        {QStringLiteral("anchorTarget"), rectToJson(track.anchorTarget)},
        {QStringLiteral("anchorElement"), rectToJson(track.anchorElement)},
        {QStringLiteral("anchorPixelSize"), track.anchorPixelSize},
        {QStringLiteral("samples"), rows},
    };
}

std::optional<MotionTrack> motionTrackFromJson(const QJsonObject &object)
{
    // A newer format than this build knows is dropped, not misread: the keys it baked still play.
    const int version = object.value(QStringLiteral("version")).toInt(0);
    if (version < 1 || version > MotionTrack::kVersion)
        return std::nullopt;
    MotionTrack track;
    track.mode = object.value(QStringLiteral("mode")).toString();
    if (track.mode != QLatin1String("object") && track.mode != QLatin1String("face"))
        return std::nullopt;
    track.sourceClipId = object.value(QStringLiteral("sourceClipId")).toString();
    track.sourcePath = object.value(QStringLiteral("sourcePath")).toString();
    track.faceSlot = object.value(QStringLiteral("faceSlot")).toInt(-1);
    track.direction = object.value(QStringLiteral("direction")).toString(QStringLiteral("both"));
    track.followScale = object.value(QStringLiteral("followScale")).toBool(false);
    track.keepDistance = object.value(QStringLiteral("keepDistance")).toBool(true);
    track.anchorSourceUs = TimeUs(object.value(QStringLiteral("anchorSourceUs")).toDouble());
    track.anchorTarget = rectFromJson(object.value(QStringLiteral("anchorTarget")));
    track.anchorElement = rectFromJson(object.value(QStringLiteral("anchorElement")));
    track.anchorPixelSize = object.value(QStringLiteral("anchorPixelSize")).toDouble(0.0);
    for (const QJsonValue &value : object.value(QStringLiteral("samples")).toArray()) {
        const QJsonArray row = value.toArray();
        if (row.size() < 7)
            continue;
        MotionTrackSample s;
        s.sourceUs = TimeUs(row.at(0).toDouble());
        s.rect = QRectF(row.at(1).toDouble(), row.at(2).toDouble(), row.at(3).toDouble(), row.at(4).toDouble());
        s.score = row.at(5).toDouble();
        s.state = MotionTrackSample::State(qBound(0, row.at(6).toInt(), 2));
        track.samples.append(s);
    }
    std::sort(track.samples.begin(), track.samples.end(),
              [](const MotionTrackSample &a, const MotionTrackSample &b) { return a.sourceUs < b.sourceUs; });
    return track;
}

MotionBakeResult bakeMotionTrack(const MotionTrack &track, const Clip &video, Clip *follower, int projectW,
                                 int projectH)
{
    MotionBakeResult result;
    if (!follower || track.isEmpty() || track.anchorTarget.isEmpty() || track.anchorElement.isEmpty())
        return result;

    const TimeUs srcLo = qMin(video.srcIn, video.srcOut);
    const TimeUs srcHi = qMax(video.srcIn, video.srcOut);
    const auto timelineOf = [&](TimeUs sourceUs) {
        return video.timelineStart + video.sourceUsToClipLocalUs(sourceUs);
    };
    const TimeUs overlapStart = qMax(video.timelineStart, follower->timelineStart);
    const TimeUs overlapEnd = qMin(video.timelineStart + video.timelineDuration,
                                   follower->timelineStart + follower->timelineDuration);

    // The reference: the target at the anchor against the element there. Mapped through the
    // video's timing today, so a video moved after tracking keeps the element where it was put.
    const TimeUs anchorSource = qBound(srcLo, track.anchorSourceUs, srcHi);
    const QRectF ref = toCanvas(track.anchorTarget, video, timelineOf(anchorSource), projectW, projectH);
    if (ref.width() <= 0.0)
        return result;
    const QPointF offset = track.keepDistance ? track.anchorElement.center() - ref.center() : QPointF();

    struct Point
    {
        TimeUs t;
        QPointF centre;
        double k;
        bool gapBefore;
    };
    QList<Point> points;
    bool gap = false;
    for (const MotionTrackSample &s : track.samples) {
        if (s.sourceUs < srcLo || s.sourceUs > srcHi)
            continue;
        const TimeUs t = timelineOf(s.sourceUs);
        if (t < overlapStart || t >= overlapEnd)
            continue;
        ++result.samples;
        if (s.state == MotionTrackSample::State::Lost) {
            ++result.lost;
            gap = true;
            continue;
        }
        const QRectF c = toCanvas(s.rect, video, t, projectW, projectH);
        const double k = track.followScale ? c.width() / ref.width() : 1.0;
        points.append({t, c.center() + offset * k, k, gap});
        gap = false;
    }
    // A reversed or ramped clip can map source order onto timeline order backwards.
    std::sort(points.begin(), points.end(), [](const Point &a, const Point &b) { return a.t < b.t; });
    if (points.isEmpty())
        return result;

    // Averaged over neighbours, never across a stretch where the target was lost.
    QList<Point> smooth = points;
    for (int i = 0; i < points.size(); ++i) {
        int lo = i;
        while (lo > 0 && i - lo < kSmoothRadius && !points.at(lo).gapBefore)
            --lo;
        int hi = i;
        while (hi + 1 < points.size() && hi - i < kSmoothRadius && !points.at(hi + 1).gapBefore)
            ++hi;
        QPointF sum;
        double ks = 0.0;
        for (int j = lo; j <= hi; ++j) {
            sum += points.at(j).centre;
            ks += points.at(j).k;
        }
        smooth[i].centre = sum / (hi - lo + 1);
        smooth[i].k = ks / (hi - lo + 1);
    }

    const TimeUs first = smooth.first().t - follower->timelineStart;
    const TimeUs last = smooth.last().t - follower->timelineStart;
    const auto clearRange = [&](KeyframeTrack<double> &keys) {
        for (const TimeUs time : keys.keyframes().keys()) {
            if (time >= first && time <= last)
                keys.removeKeyframe(time);
        }
    };
    clearRange(follower->transformX);
    clearRange(follower->transformY);
    const bool scaleText = track.followScale && track.anchorPixelSize > 0.0
                           && (follower->type == ClipType::Text || follower->type == ClipType::Subtitle);
    KeyframeTrack<double> *pixelSize =
        scaleText ? &follower->textStyle.keyframes[QStringLiteral("pixelSize")] : nullptr;
    if (track.followScale) {
        clearRange(follower->transformW);
        clearRange(follower->transformH);
    }
    if (pixelSize)
        clearRange(*pixelSize);
    const QSizeF size = track.anchorElement.size();
    for (int i = 0; i < smooth.size(); ++i) {
        // Every other sample, plus both sides of a gap and the last one, so a lost stretch is an
        // interpolated glide rather than the shape of whichever key happened to land near it.
        const bool edge = i == smooth.size() - 1 || smooth.at(i).gapBefore
                          || (i + 1 < smooth.size() && smooth.at(i + 1).gapBefore);
        if (i % kKeyEvery != 0 && !edge)
            continue;
        const Point &p = smooth.at(i);
        const double w = size.width() * p.k;
        const double h = size.height() * p.k;
        const TimeUs rel = p.t - follower->timelineStart;
        follower->transformX.setKeyframe(rel, p.centre.x() - w * 0.5);
        follower->transformY.setKeyframe(rel, p.centre.y() - h * 0.5);
        if (track.followScale) {
            follower->transformW.setKeyframe(rel, w);
            follower->transformH.setKeyframe(rel, h);
        }
        if (pixelSize)
            pixelSize->setKeyframe(rel, qMax(1.0, track.anchorPixelSize * p.k));
        ++result.keys;
    }
    result.ok = true;
    return result;
}

int followFaceSlot(const QList<QRectF> &faces, const QRectF &last, int current)
{
    const auto valid = [&](int i) { return i >= 0 && i < faces.size() && !faces.at(i).isNull(); };
    if (last.isNull())
        return valid(current) ? current : -1;
    const double reach = qMax(last.width(), last.height()) * 0.75;
    const auto distance = [&](int i) {
        const QPointF d = faces.at(i).center() - last.center();
        return std::hypot(d.x(), d.y());
    };
    if (valid(current) && distance(current) <= reach)
        return current;
    int best = -1;
    for (int i = 0; i < faces.size(); ++i) {
        if (valid(i) && distance(i) <= reach && (best < 0 || distance(i) < distance(best)))
            best = i;
    }
    if (best >= 0)
        return best;
    // Nobody where the face was. Its own slot moving fast is still that person (the scan keeps a
    // face in its slot from frame to frame); any other slot would be somebody else.
    return valid(current) ? current : -1;
}

} // namespace drift
