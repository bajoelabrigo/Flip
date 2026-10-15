#include "engine/PoseTrack.h"

#include <QDateTime>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QHash>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QMutex>
#include <QMutexLocker>
#include <QRandomGenerator>
#include <QStandardPaths>

#include <algorithm>
#include <cmath>

namespace drift {
namespace {

constexpr int kFormatVersion = 1;

// uv to four decimals is a tenth of a pixel on a 4K frame, and keeps a minute of 30 fps under a
// megabyte.
double round4(double v)
{
    return std::round(v * 10000.0) / 10000.0;
}

QJsonValue poseToJson(const BodyPose &pose)
{
    if (!pose.valid)
        return QJsonValue::Null;
    QJsonArray points;
    for (const QPointF &p : pose.points) {
        points.append(round4(p.x()));
        points.append(round4(p.y()));
    }
    QJsonArray visibility;
    for (const float v : pose.visibility)
        visibility.append(std::round(v * 100.0) / 100.0);
    QJsonObject obj;
    obj[QStringLiteral("s")] = std::round(pose.score * 100.0) / 100.0;
    obj[QStringLiteral("p")] = points;
    obj[QStringLiteral("v")] = visibility;
    obj[QStringLiteral("r")] = QJsonArray{round4(pose.roiCenter.x()), round4(pose.roiCenter.y()),
                                          round4(pose.roiSize)};
    return obj;
}

bool poseFromJson(const QJsonValue &value, BodyPose *out)
{
    *out = BodyPose();
    if (value.isNull())
        return true;
    if (!value.isObject())
        return false;
    const QJsonObject obj = value.toObject();
    const QJsonArray points = obj.value(QStringLiteral("p")).toArray();
    const QJsonArray visibility = obj.value(QStringLiteral("v")).toArray();
    if (points.size() != body::kPointCount * 2 || visibility.size() != body::kPointCount)
        return false;
    for (int i = 0; i < body::kPointCount; ++i) {
        out->points.append(QPointF(points.at(i * 2).toDouble(), points.at(i * 2 + 1).toDouble()));
        out->visibility.append(float(visibility.at(i).toDouble()));
    }
    const QJsonArray roi = obj.value(QStringLiteral("r")).toArray();
    if (roi.size() == 3) {
        out->roiCenter = QPointF(roi.at(0).toDouble(), roi.at(1).toDouble());
        out->roiSize = roi.at(2).toDouble();
    }
    out->score = obj.value(QStringLiteral("s")).toDouble();
    out->valid = true;
    return true;
}

struct CacheEntry
{
    QDateTime modified;
    qint64 size = 0;
    std::shared_ptr<const PoseTrack> track;
};

QMutex g_cacheMutex;
QHash<QString, CacheEntry> g_cache;

} // namespace

BodyPose PoseTrack::sample(TimeUs relativeUs) const
{
    if (frames.isEmpty() || fps <= 0)
        return {};

    const double frameUs = double(kUsPerSecond) / fps;
    const double exact = double(relativeUs) / frameUs;
    if (exact <= 0.0)
        return frames.first();
    if (exact >= frames.size() - 1)
        return frames.last();

    const int i0 = int(exact);
    const double t = exact - i0;
    const BodyPose &a = frames.at(i0);
    const BodyPose &b = frames.at(i0 + 1);
    if (!a.valid || !b.valid)
        return {};

    BodyPose out = a;
    for (int i = 0; i < out.points.size() && i < b.points.size(); ++i) {
        out.points[i] = a.points.at(i) * (1.0 - t) + b.points.at(i) * t;
        out.visibility[i] = float(a.visibility.at(i) * (1.0 - t) + b.visibility.at(i) * t);
    }
    out.score = a.score * (1.0 - t) + b.score * t;
    return out;
}

void smoothPoseTrack(PoseTrack *track, int radius)
{
    if (!track || radius <= 0)
        return;
    const PoseTrack source = *track;
    const int count = source.frames.size();
    for (int i = 0; i < count; ++i) {
        if (!source.frames.at(i).valid)
            continue;
        // The run of valid frames around i, clipped to the radius.
        int lo = i;
        while (lo > i - radius && lo > 0 && source.frames.at(lo - 1).valid)
            --lo;
        int hi = i;
        while (hi < i + radius && hi < count - 1 && source.frames.at(hi + 1).valid)
            ++hi;
        // Symmetric, so a still body stays exactly where it is and motion is not delayed.
        const int reach = std::min(i - lo, hi - i);
        if (reach <= 0)
            continue;
        BodyPose &out = track->frames[i];
        for (int p = 0; p < out.points.size(); ++p) {
            QPointF sum;
            for (int j = i - reach; j <= i + reach; ++j)
                sum += source.frames.at(j).points.at(p);
            out.points[p] = sum / double(2 * reach + 1);
        }
    }
}

void applyPoseUniforms(QMap<QString, QVariant> *parameters, const BodyPose &pose)
{
    parameters->insert(QStringLiteral("u_bodyValid"), pose.valid ? 1.0 : 0.0);
    if (!pose.valid || pose.points.size() != body::kPointCount)
        return;

    auto point = [&](const char *name, int index) {
        const QPointF &p = pose.points.at(index);
        parameters->insert(QLatin1String(name) + QLatin1String("X"), p.x());
        parameters->insert(QLatin1String(name) + QLatin1String("Y"), p.y());
        parameters->insert(QLatin1String(name) + QLatin1String("Vis"), double(pose.visibility.at(index)));
    };
    point("u_bodyNose", body::kNose);
    point("u_bodyShoulderL", body::kShoulderLeft);
    point("u_bodyShoulderR", body::kShoulderRight);
    point("u_bodyElbowL", body::kElbowLeft);
    point("u_bodyElbowR", body::kElbowRight);
    point("u_bodyWristL", body::kWristLeft);
    point("u_bodyWristR", body::kWristRight);
    point("u_bodyHipL", body::kHipLeft);
    point("u_bodyHipR", body::kHipRight);
    point("u_bodyKneeL", body::kKneeLeft);
    point("u_bodyKneeR", body::kKneeRight);
    point("u_bodyAnkleL", body::kAnkleLeft);
    point("u_bodyAnkleR", body::kAnkleRight);
}

QString poseTrackCacheDir()
{
    const QString root = QStandardPaths::writableLocation(QStandardPaths::AppDataLocation);
    if (root.isEmpty())
        return {};
    const QString dir = QDir(root).filePath(QStringLiteral("posetracks"));
    if (!QDir().mkpath(dir))
        return {};
    return dir;
}

QString newPoseTrackPath()
{
    const QString dir = poseTrackCacheDir();
    if (dir.isEmpty())
        return {};
    const QString name = QStringLiteral("pose-%1-%2.json")
                             .arg(QDateTime::currentMSecsSinceEpoch())
                             .arg(QRandomGenerator::global()->bounded(100000), 5, 10,
                                  QLatin1Char('0'));
    return QDir(dir).filePath(name);
}

bool writePoseTrack(const QString &path, const PoseTrack &track, QString *errorOut)
{
    QJsonObject root;
    root[QStringLiteral("version")] = kFormatVersion;
    root[QStringLiteral("fps")] = track.fps;
    root[QStringLiteral("startSrcUs")] = qint64(track.startSrcUs);
    QJsonArray frames;
    for (const BodyPose &pose : track.frames)
        frames.append(poseToJson(pose));
    root[QStringLiteral("frames")] = frames;

    const QString partPath = path + QStringLiteral(".part");
    QFile f(partPath);
    if (!f.open(QIODevice::WriteOnly | QIODevice::Truncate)) {
        if (errorOut)
            *errorOut = QStringLiteral("Could not write %1").arg(partPath);
        return false;
    }
    f.write(QJsonDocument(root).toJson(QJsonDocument::Compact));
    f.close();

    QFile::remove(path);
    if (!QFile::rename(partPath, path)) {
        QFile::remove(partPath);
        if (errorOut)
            *errorOut = QStringLiteral("Could not finalize %1").arg(path);
        return false;
    }
    return true;
}

bool readPoseTrack(const QString &path, PoseTrack *out, QString *errorOut)
{
    QFile f(path);
    if (!f.open(QIODevice::ReadOnly)) {
        if (errorOut)
            *errorOut = QStringLiteral("Could not read %1").arg(path);
        return false;
    }
    QJsonParseError parseError{};
    const QJsonDocument doc = QJsonDocument::fromJson(f.readAll(), &parseError);
    if (parseError.error != QJsonParseError::NoError || !doc.isObject()) {
        if (errorOut)
            *errorOut = QStringLiteral("Pose track %1 is not valid JSON").arg(path);
        return false;
    }
    const QJsonObject root = doc.object();
    const int version = root.value(QStringLiteral("version")).toInt();
    if (version < 1 || version > kFormatVersion) {
        if (errorOut)
            *errorOut = QStringLiteral("Pose track %1 has an unsupported format version").arg(path);
        return false;
    }
    out->fps = root.value(QStringLiteral("fps")).toInt();
    out->startSrcUs = TimeUs(root.value(QStringLiteral("startSrcUs")).toInteger(0));
    out->frames.clear();
    const QJsonArray frames = root.value(QStringLiteral("frames")).toArray();
    out->frames.reserve(frames.size());
    for (const QJsonValue &value : frames) {
        BodyPose pose;
        if (!poseFromJson(value, &pose)) {
            if (errorOut)
                *errorOut = QStringLiteral("Pose track %1 has a malformed entry").arg(path);
            return false;
        }
        out->frames.append(pose);
    }
    if (out->fps <= 0) {
        if (errorOut)
            *errorOut = QStringLiteral("Pose track %1 has no frame rate").arg(path);
        return false;
    }
    return true;
}

std::shared_ptr<const PoseTrack> loadPoseTrackCached(const QString &path)
{
    if (path.isEmpty())
        return nullptr;
    const QFileInfo info(path);
    if (!info.exists())
        return nullptr;

    QMutexLocker lock(&g_cacheMutex);
    const auto it = g_cache.constFind(path);
    if (it != g_cache.cend() && it->modified == info.lastModified() && it->size == info.size())
        return it->track;

    auto track = std::make_shared<PoseTrack>();
    QString error;
    if (!readPoseTrack(path, track.get(), &error)) {
        // The failure is cached too, so a broken sidecar is not re-read on every frame.
        g_cache.insert(path, CacheEntry{info.lastModified(), info.size(), nullptr});
        return nullptr;
    }
    g_cache.insert(path, CacheEntry{info.lastModified(), info.size(), track});
    return track;
}

} // namespace drift
