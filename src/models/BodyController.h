#pragma once

#include "core/Time.h"

#include <QAtomicInt>
#include <QObject>
#include <QString>
#include <QVariantMap>

class AppController;

// Retouch › Body and Hair, reached from QML as EditorState.body. Both run the body model over the
// clip off the GUI thread, like the face scan: Body bakes the pose that the body warps follow,
// Hair bakes a hair matte and pins a hair-colour adjustment to the clip, masked by it.
class BodyController : public QObject
{
    Q_OBJECT
    Q_PROPERTY(bool running READ running NOTIFY runningChanged)
    Q_PROPERTY(QString job READ job NOTIFY runningChanged)
    Q_PROPERTY(double progress READ progress NOTIFY progressChanged)
    Q_PROPERTY(QString status READ status NOTIFY statusChanged)

public:
    explicit BodyController(AppController *app, QObject *parent = nullptr);

    bool running() const { return m_running; }
    QString job() const { return m_job; }
    double progress() const { return m_progress; }
    QString status() const { return m_status; }

    // Whether the body model addon is installed. A file check: safe to call from bindings.
    Q_INVOKABLE bool available();
    Q_INVOKABLE void cancel();

    // Bakes the clip's body pose so the body warps have something to follow.
    Q_INVOKABLE void analyzeBody(int trackIndex, int clipIndex);
    Q_INVOKABLE void clearBody(int trackIndex, int clipIndex);

    // Recolours the clip's hair. The first time it bakes the hair matte and pins a "Hair colour"
    // adjustment to the clip; after that it only changes that adjustment's shade.
    Q_INVOKABLE void colorHair(int trackIndex, int clipIndex, const QString &shade);
    // The clip's hair-colour adjustment as {trackIndex, clipIndex, shade, strength}, or an empty
    // map when it has none.
    Q_INVOKABLE QVariantMap hairColor(int trackIndex, int clipIndex) const;
    // Takes the hair-colour adjustment off the clip (undoable; the matte stays in the cache).
    Q_INVOKABLE void removeHairColor(int trackIndex, int clipIndex);

signals:
    void runningChanged();
    void progressChanged();
    void statusChanged();
    void finished(bool ok, const QString &message);

private:
    friend class EditorStateTest;

    bool begin(const QString &job, const QString &message);
    void finalizeBody(const QString &clipId, const QString &trackPath, drift::TimeUs srcOffsetUs);
    void finalizeHair(const QString &clipId, const QString &mattePath, drift::TimeUs srcOffsetUs,
                      const QString &shade);

    AppController *m_app = nullptr;
    bool m_running = false;
    QString m_job;
    double m_progress = 0.0;
    QString m_status;
    QAtomicInt m_cancel = 0;
};
