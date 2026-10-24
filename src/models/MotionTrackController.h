#pragma once

#include "core/Time.h"

#include <QAtomicInt>
#include <QList>
#include <QObject>
#include <QRectF>
#include <QString>
#include <QVariantList>
#include <QVariantMap>

class AppController;

namespace drift {
struct Clip;
}

// Motion tracking as CapCut and Filmora do it, reached from QML as EditorState.motionTrack: a text,
// sticker or picture follows something in the video under it. "object" follows whatever the
// element covers at the playhead (RegionTracker, which picks a lost subject up again), "face"
// follows one of the video's scanned faces without swapping it for somebody else. What was found
// is kept on the element (Clip::motionTrack) and baked into its position (and, with Scale, size)
// keyframes in one undo step, so it plays and exports like any animation and can be retouched;
// Scale and Distance re-bake it without analysing again.
class MotionTrackController : public QObject
{
    Q_OBJECT
    Q_PROPERTY(bool busy READ busy NOTIFY busyChanged)
    Q_PROPERTY(double progress READ progress NOTIFY progressChanged)
    Q_PROPERTY(QString status READ status NOTIFY statusChanged)
    // Bumped whenever an element's tracking changes, so bindings on info()/targetAt() refresh.
    Q_PROPERTY(int revision READ revision NOTIFY revisionChanged)
    // Objects found at the playhead (detectObjects), to pick one on the preview: [{x, y, w, h
    // (canvas pixels), region {x, y, w, h} (normalized to the video frame), classId, score}].
    Q_PROPERTY(QVariantList objectTargets READ objectTargets NOTIFY objectTargetsChanged)
    Q_PROPERTY(bool detectingObjects READ detectingObjects NOTIFY objectTargetsChanged)
    // What the preview offers to pick while the Tracking tab is open: "" (nothing), "face" (the
    // scanned faces) or "object" (the detected objects, or a box drawn by hand).
    Q_PROPERTY(QString chooser READ chooser WRITE setChooser NOTIFY chooserChanged)
    // What was picked there: {} (follow what the element covers / the nearest face), {faceSlot},
    // or {region: {x, y, w, h} normalized to the video frame, classId (-1 for a drawn box)}.
    Q_PROPERTY(QVariantMap pick READ pick WRITE setPick NOTIFY pickChanged)

public:
    explicit MotionTrackController(AppController *app, QObject *parent = nullptr);

    bool busy() const { return m_busy; }
    double progress() const { return m_progress; }
    QString status() const { return m_status; }
    int revision() const { return m_revision; }
    QVariantList objectTargets() const { return m_objectTargets; }
    QString chooser() const { return m_chooser; }
    void setChooser(const QString &chooser);
    QVariantMap pick() const { return m_pick; }
    void setPick(const QVariantMap &pick);
    // A box drawn on the preview (canvas pixels) as a region of the video under the element, for
    // `pick`: {ok, x, y, w, h} normalized to that video's frame.
    Q_INVOKABLE QVariantMap regionFromCanvas(int trackIndex, int clipIndex, double x, double y, double w,
                                             double h) const;
    bool detectingObjects() const { return m_detectingObjects; }
    // Whether the object model (the "seguimiento.objetos" extra, YOLOX) is installed.
    Q_INVOKABLE bool objectModelReady() const;
    // Finds the objects in the video under the element at the playhead (off the GUI thread).
    Q_INVOKABLE void detectObjects(int trackIndex, int clipIndex);
    Q_INVOKABLE void clearObjectTargets();

    // What a track on this clip would follow, for the inspector: {ok, source (clip name),
    // canScale, hasFaces, reason}. Cheap; called on every selection change.
    Q_INVOKABLE QVariantMap sourceFor(int trackIndex, int clipIndex) const;
    // The element's stored tracking: {has, mode, faceSlot, followScale, keepDistance, direction,
    // samples, lost, sourceMissing, sourceChanged}.
    Q_INVOKABLE QVariantMap info(int trackIndex, int clipIndex) const;
    // The faces of the video under the element at the playhead, for picking one on the preview:
    // [{slot, x, y, w, h (canvas pixels), selected}].
    Q_INVOKABLE QVariantList faceTargets(int trackIndex, int clipIndex) const;
    // What the element follows at the playhead: {ok, x, y, w, h (canvas pixels), state:
    // "tracked" | "lost" | "recovered"}.
    Q_INVOKABLE QVariantMap targetAt(int trackIndex, int clipIndex) const;

    // mode: "object" or "face". Tracks forward and backward from the playhead over the stretch
    // where the element and the video overlap.
    Q_INVOKABLE void track(int trackIndex, int clipIndex, const QString &mode, bool followScale);
    // The same with every option: {mode, followScale, keepDistance, direction ("both" | "forward" |
    // "backward"), faceSlot (-1 = the face nearest the element), region ({x, y, w, h} normalized to
    // the video frame: follow that instead of what the element covers — a box drawn or an object
    // picked on the preview), classId (the picked object's class: a lost subject is looked for
    // again among the detector's objects of that class)}. Starts from the playhead, so it is also
    // "track again from here".
    Q_INVOKABLE void trackWith(int trackIndex, int clipIndex, const QVariantMap &options);
    // Scale or Distance after tracking ("followScale" / "keepDistance"): re-baked, no analysis.
    Q_INVOKABLE bool setOption(int trackIndex, int clipIndex, const QString &key, const QVariant &value);
    // Bakes again against the followed video's current place and timing (after it was moved,
    // trimmed or sped up).
    Q_INVOKABLE bool realign(int trackIndex, int clipIndex);
    // CapCut's Mosaic: hides a face of this video clip (or photo) for its whole length with a
    // pixelate ("pixelate") or blur ("blur") layer right above it, its oval mask following the
    // face. faceSlot -1 = the face nearest the middle of the frame at the playhead. Scans the faces
    // first if they have not been.
    Q_INVOKABLE void blurFace(int trackIndex, int clipIndex, const QString &style, int faceSlot = -1);
    // The same for an object of this clip: `region` ({x, y, w, h} normalized to its frame, picked or
    // drawn on the preview) is followed by the object tracker through the whole clip; classId lets a
    // lost object be found again by the detector (-1 for a drawn box). Off the GUI thread.
    Q_INVOKABLE void hideObject(int trackIndex, int clipIndex, const QString &style, const QVariantMap &region,
                                int classId = -1);
    // A mask that follows what it covers in the video it cuts (CapCut's mask tracking): the selected
    // mask adjustment's first mask is tracked from the playhead to both ends of its clip and keyed
    // (position, and with followScale size). Off the GUI thread.
    Q_INVOKABLE void maskFollow(int trackIndex, int clipIndex, bool followScale);
    // Whether the selected clip is a mask maskFollow can drive: {ok, reason}.
    Q_INVOKABLE QVariantMap maskFollowSource(int trackIndex, int clipIndex) const;
    Q_INVOKABLE void cancel();
    // Drops the element's tracking and its position and size animation, leaving it where it is at
    // the playhead.
    Q_INVOKABLE void clear(int trackIndex, int clipIndex);

signals:
    void busyChanged();
    void progressChanged();
    void statusChanged();
    void revisionChanged();
    void objectTargetsChanged();
    void chooserChanged();
    void pickChanged();
    void finished(bool ok, const QString &message);

private:
    struct Source
    {
        int trackIndex = -1;
        int clipIndex = -1;
    };
    Source sourceUnder(int trackIndex, int clipIndex, drift::TimeUs atUs) const;
    // The picture the preview offers faces and objects from: the selected clip itself while hiding
    // something in it (chooser "hide-face" / "hide-object"), else the one under it.
    Source pickSource(int trackIndex, int clipIndex, drift::TimeUs atUs) const;
    // The followed video of a stored track: by id, else whatever is under the element now.
    const drift::Clip *followedVideo(const drift::Clip &follower, int trackIndex, int clipIndex) const;
    bool rebake(int trackIndex, int clipIndex, const QString &undoText);
    void warnIfKeysReplaced(int removed);
    // One oval key of a hide layer: its centre and size, normalized to the canvas, at a timeline time.
    struct HideKey
    {
        drift::TimeUs t = 0;
        QRectF r;
    };
    // Puts a pixelate or blur layer right above `trackIndex`, spanning `video`, its oval mask keyed to
    // `keys` (smoothed, a key every other one). `blockPx` is the pixel block size for pixelate.
    void addHideLayer(int trackIndex, const drift::Clip &video, QList<HideKey> keys, const QString &style,
                      double blockPx, const QString &name, const QString &undoText, const QString &message);
    // The mask maskFollow drives and the picture it is measured on.
    struct MaskTarget
    {
        bool ok = false;
        QString reason;
        int videoTrack = -1;
        int videoClip = -1;
        bool canvasSpace = false; // a standalone layer's mask is on the canvas, a lane's on its clip
    };
    MaskTarget maskTarget(int trackIndex, int clipIndex, drift::TimeUs atUs) const;
    void setBusy(bool busy);
    void bump();

    AppController *m_app = nullptr;
    bool m_busy = false;
    double m_progress = 0.0;
    QString m_status;
    int m_revision = 0;
    QAtomicInt m_cancel = 0;
    // A face track asked for before following a face: resumed when the scan finishes.
    QString m_pendingFaceClipId;
    QVariantMap m_pendingOptions;
    // A face blur asked for before the faces were scanned: {clipId, style, faceSlot}.
    QVariantMap m_pendingBlur;
    QVariantList m_objectTargets;
    QString m_chooser;
    QVariantMap m_pick;
    bool m_detectingObjects = false;
    int m_objectGeneration = 0;
};
