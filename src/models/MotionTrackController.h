#pragma once

#include "core/Time.h"

#include <QAtomicInt>
#include <QObject>
#include <QRectF>
#include <QString>
#include <QVariantMap>

class AppController;

// Motion tracking as CapCut and Filmora do it, reached from QML as EditorState.motionTrack: a text,
// sticker or picture follows something in the video under it. "object" follows whatever the
// element covers at the playhead (RegionTracker), "face" follows the video's scanned face. The
// path is baked into the element's position (and, when asked, size) keyframes in one undo step, so
// it can be retouched like any other animation.
class MotionTrackController : public QObject
{
    Q_OBJECT
    Q_PROPERTY(bool busy READ busy NOTIFY busyChanged)
    Q_PROPERTY(double progress READ progress NOTIFY progressChanged)
    Q_PROPERTY(QString status READ status NOTIFY statusChanged)

public:
    explicit MotionTrackController(AppController *app, QObject *parent = nullptr);

    bool busy() const { return m_busy; }
    double progress() const { return m_progress; }
    QString status() const { return m_status; }

    // What a track on this clip would follow, for the inspector: {ok, source (clip name),
    // canScale, hasFaces, reason}. Cheap; called on every selection change.
    Q_INVOKABLE QVariantMap sourceFor(int trackIndex, int clipIndex) const;
    // mode: "object" or "face". Tracks forward and backward from the playhead over the stretch
    // where the element and the video overlap.
    Q_INVOKABLE void track(int trackIndex, int clipIndex, const QString &mode, bool followScale);
    Q_INVOKABLE void cancel();
    // Drops the element's position and size animation, leaving it where it is at the playhead.
    Q_INVOKABLE void clear(int trackIndex, int clipIndex);

signals:
    void busyChanged();
    void progressChanged();
    void statusChanged();
    void finished(bool ok, const QString &message);

private:
    struct Source
    {
        int trackIndex = -1;
        int clipIndex = -1;
    };
    Source sourceUnder(int trackIndex, int clipIndex, drift::TimeUs atUs) const;
    void setBusy(bool busy);

    AppController *m_app = nullptr;
    bool m_busy = false;
    double m_progress = 0.0;
    QString m_status;
    QAtomicInt m_cancel = 0;
    // A face track asked for before following a face: resumed when the scan finishes.
    QString m_pendingFaceClipId;
    bool m_pendingFollowScale = false;
};
