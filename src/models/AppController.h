#pragma once

#include "core/EffectStackStore.h"
#include "core/Project.h"
#include "core/TextAnimationPreset.h"
#include "core/TimelineOps.h"
#include "core/Time.h"
#include "engine/AudioOnsets.h"
#include "engine/SceneDetect.h"
#include "engine/TransformLayer.h"
#include "engine/FilmstripTileCache.h"
#include "engine/MediaWaveform.h"
#include "engine/WaveformBlockCache.h"
#include "engine/ProjectBundle.h"
#include "TimelineClipsModel.h"
#include "models/AssetLibrary.h"
#include "models/CloudProviders.h"
#include "core/GuideSet.h"

#include <QAtomicInt>
#include <QColor>
#include <QCursor>
#include <QDateTime>
#include <QImage>
#include <QFuture>
#include <QHash>
#include <QJsonObject>
#include <QMatrix4x4>
#include <QMediaDevices>
#include <QElapsedTimer>
#include <QObject>
#include <QPair>
#include <QSet>
#include <QStringList>
#include <QTransform>
#include <QUndoStack>
#include <QUrl>
#include <QVariantList>
#include <QVariantMap>

#include <atomic>
#include <functional>
#include <QSharedPointer>
#include <QMap>

#include <memory>
#include <optional>
#include <optional>

struct EffectTemplateEntry;
struct MediaInfo;

class QTimer;
class AddonManager;
class MarketClient;
class JobRegistry;

namespace drift {
struct BrandKit;
struct MediaEditSpec;
}

#include "engine/AudioRecorder.h"
#include "playback/PlaybackEngine.h"
#include "preview/PreviewController.h"
#include "AssetPreviewController.h"
#include "CurveEditorController.h"
#include "DenoiseController.h"
#include "DepthController.h"
#include "BodyController.h"
#include "FaceTrackingController.h"
#include "MotionTrackController.h"
#include "McpController.h"
#include "RestoreController.h"
#include "SceneDetectController.h"
#include "SegmentationController.h"
#include "MediaBinController.h"
#include "StabilizeController.h"
#include "TtsController.h"
#include "VoiceLibrary.h"
#include "SpeedCurveController.h"
#include "PreferencesController.h"
#include "ProjectFileController.h"

// QML-facing controller over the core project model and undo stack.
class AppController : public QObject
{
    // Segmentation completion is normally reached only through a finished worker, which needs a
    // real backend installed. The test drives it directly instead.
    friend class EditorStateTest;
    // Moved out of this class with the preview area; it still reads the timeline and selection.
    friend class PreviewController;
    // Owns the agent server. Still reaches the timeline helpers that have not moved yet.
    friend class McpController;
    friend class ProjectFileController;
    friend class AssetPreviewController;
    friend class SpeedCurveController;
    friend class CurveEditorController;
    friend class SegmentationController;
    friend class SceneDetectController;
    friend class DepthController;
    friend class DenoiseController;
    friend class RestoreController;
    friend class FaceTrackingController;
    friend class MotionTrackController;
    friend class BodyController;
    friend class StabilizeController;
    friend class MediaBinController;
    friend class TtsController;
    friend class VoiceLibrary;

    Q_OBJECT

    Q_PROPERTY(AssetLibrary *assetLibrary READ assetLibrary CONSTANT)
    Q_PROPERTY(CloudProviders *cloudProviders READ cloudProviders CONSTANT)
    Q_PROPERTY(MediaBinController *bin READ bin CONSTANT)
    Q_PROPERTY(PlaybackEngine *playback READ playback CONSTANT)
    // The preview area's editor state, tools and overlay maths.
    Q_PROPERTY(PreviewController *preview READ preview CONSTANT)
    // App-wide preferences and persisted UI layout. QML: EditorState.preferences.
    Q_PROPERTY(PreferencesController *preferences READ preferences CONSTANT)
    // Project file lifecycle and project setup. QML: EditorState.projectFile.
    Q_PROPERTY(ProjectFileController *projectFile READ projectFile CONSTANT)
    // Media-bin preview session. QML: EditorState.assetPreview.
    Q_PROPERTY(AssetPreviewController *assetPreview READ assetPreview CONSTANT)
    // Speed-curve editing session. QML: EditorState.speedCurve.
    Q_PROPERTY(SpeedCurveController *speedCurve READ speedCurve CONSTANT)
    // Fade and transition curve sessions. QML: EditorState.curves.
    Q_PROPERTY(CurveEditorController *curves READ curves CONSTANT)
    // Cutout pipeline and prompting session. QML: EditorState.segmentation.
    Q_PROPERTY(SegmentationController *segmentation READ segmentation CONSTANT)
    // Shot detection for a video clip. QML: EditorState.scenes.
    Q_PROPERTY(SceneDetectController *scenes READ scenes CONSTANT)
    // Depth estimation for a clip. QML: EditorState.depth.
    Q_PROPERTY(DepthController *depth READ depth CONSTANT)
    // Noise removal for a clip's audio. QML: EditorState.denoise.
    Q_PROPERTY(DenoiseController *denoise READ denoise CONSTANT)
    // Video restore and enhance (decompression, upscaling). QML: EditorState.restore.
    Q_PROPERTY(RestoreController *restore READ restore CONSTANT)
    // Face landmark tracking and Face Swap source ingest. QML: EditorState.faces.
    Q_PROPERTY(FaceTrackingController *faces READ faces CONSTANT)
    Q_PROPERTY(MotionTrackController *motionTrack READ motionTrack CONSTANT)
    Q_PROPERTY(BodyController *body READ body CONSTANT)
    // Clip stabilization. QML: EditorState.stabilize.
    Q_PROPERTY(StabilizeController *stabilize READ stabilize CONSTANT)
    // Local text-to-speech and the cloned-voice library. QML: EditorState.tts, EditorState.voices.
    Q_PROPERTY(TtsController *tts READ tts CONSTANT)
    Q_PROPERTY(VoiceLibrary *voices READ voices CONSTANT)
    // Output devices to choose between, each {id, label}; the first entry has an empty id and
    // means "whatever the system default is at the time", which is also the default choice.
    Q_PROPERTY(QVariantList audioOutputDevices READ audioOutputDevices NOTIFY audioOutputDevicesChanged)
    Q_PROPERTY(QString audioOutputDeviceId READ audioOutputDeviceId WRITE setAudioOutputDeviceId
                   NOTIFY audioOutputDeviceIdChanged)
    // Audio recording (voiceover via microphone)
    Q_PROPERTY(bool isRecordingAudio READ isRecordingAudio NOTIFY audioRecordingStateChanged)
    Q_PROPERTY(bool isAudioRecordingPaused READ isAudioRecordingPaused NOTIFY audioRecordingPausedChanged)
    Q_PROPERTY(int recordingTrackIndex READ recordingTrackIndex NOTIFY audioRecordingStateChanged)
    Q_PROPERTY(float audioRecordLevel READ audioRecordLevel NOTIFY audioRecordLevelChanged)
    Q_PROPERTY(float audioRecordGain READ audioRecordGain WRITE setAudioRecordGain NOTIFY audioRecordGainChanged)
    Q_PROPERTY(double audioRecordSeconds READ audioRecordSeconds NOTIFY audioRecordSecondsChanged)
    Q_PROPERTY(QVariantList audioRecordLivePeaks READ audioRecordLivePeaks NOTIFY audioRecordLivePeaksChanged)
    Q_PROPERTY(QVariantList availableMicrophones READ availableMicrophones NOTIFY availableMicrophonesChanged)
    Q_PROPERTY(QString currentMicrophoneName READ currentMicrophoneName NOTIFY currentMicrophoneChanged)
    Q_PROPERTY(QVariantList tracks READ tracks NOTIFY tracksChanged)
    // A change token for the bindings that read `tracks` only to re-evaluate on an edit. Reading
    // the list for that rebuilt every clip in the project into QVariantMaps, once per binding,
    // per emission — with two dozen such bindings across the desktop and touch shells.
    Q_PROPERTY(quint32 tracksRevision READ tracksRevision NOTIFY tracksChanged)
    // For the bindings that only ask how many tracks there are, or whether there are any.
    Q_PROPERTY(int trackCount READ trackCount NOTIFY tracksChanged)
    // "Is the timeline empty?" — asked by the empty-state copy in both shells, which used to
    // answer it by serialising the project and looping over every track.
    Q_PROPERTY(int clipCount READ clipCount NOTIFY tracksChanged)
    // A loudness measurement (normalizeClipLoudness) is running.
    Q_PROPERTY(bool normalizing READ normalizing NOTIFY normalizingChanged)
    // Whether the touch shell's grow/shrink-all-lanes buttons have anywhere left to go, for their
    // enabled state. Properties rather than invokables so QML gets real bindings: an invokable
    // would have to be given a dependency to re-evaluate on, and the only one available is
    // `tracks`, which rebuilds a QVariantList of every clip in the project each time it is read.
    Q_PROPERTY(bool canGrowTrackHeights READ canGrowTrackHeights NOTIFY tracksChanged)
    Q_PROPERTY(bool canShrinkTrackHeights READ canShrinkTrackHeights NOTIFY tracksChanged)
    Q_PROPERTY(double playheadSeconds READ playheadSeconds WRITE setPlayheadSeconds NOTIFY playheadSecondsChanged)
    // The same playhead, announced at most ~10 times a second while playing and on every change
    // otherwise. Inspectors bind this: a value readout does not need frame rate, and ~45 rows
    // re-evaluating per frame is a large share of the GUI thread during playback.
    Q_PROPERTY(double inspectorPlayheadSeconds READ playheadSeconds NOTIFY inspectorPlayheadChanged)
    Q_PROPERTY(double durationSeconds READ durationSeconds NOTIFY tracksChanged)
    Q_PROPERTY(bool playing READ playing WRITE setPlaying NOTIFY playingChanged)
    // Between beginScrub and endScrub. Preview overlays stand aside the way they do for
    // playback: the playhead moves on every scroll event, and re-resolving their clips each
    // time was most of what a scrub step cost on the GUI thread.
    Q_PROPERTY(bool scrubbing READ scrubbing NOTIFY scrubbingChanged)
    Q_PROPERTY(bool previewDragActive READ previewDragActive NOTIFY previewDragActiveChanged)
    Q_PROPERTY(bool snapEnabled READ snapEnabled WRITE setSnapEnabled NOTIFY snapEnabledChanged)
    Q_PROPERTY(bool rippleEnabled READ rippleEnabled WRITE setRippleEnabled NOTIFY rippleEnabledChanged)
    Q_PROPERTY(bool allowClipOverlap READ allowClipOverlap WRITE setAllowClipOverlap NOTIFY allowClipOverlapChanged)
  // Per-project UI prefs (serialized with the .drift file, not global QSettings).
    Q_PROPERTY(bool mediaGridMode READ mediaGridMode WRITE setMediaGridMode NOTIFY mediaGridModeChanged)
    // "grid" | "list" | "tree". mediaGridMode above is the older two-state view of the same
    // setting, kept because MCP and saved projects already speak it.
    Q_PROPERTY(QString mediaViewMode READ mediaViewMode WRITE setMediaViewMode NOTIFY mediaViewModeChanged)
    // True when the project canvas is taller than it is wide. The workspace arrangement
    // follows this until the user picks one; that override lives on PreferencesController.
    Q_PROPERTY(bool projectPortrait READ projectPortrait NOTIFY tracksChanged)
    Q_PROPERTY(bool autoKeyEnabled READ autoKeyEnabled WRITE setAutoKeyEnabled NOTIFY autoKeyEnabledChanged)
    Q_PROPERTY(bool positionLinked READ positionLinked WRITE setPositionLinked NOTIFY positionLinkedChanged)
    // The Transform size lock (width and height together), one state for the Transform tab and the
    // Video and Text pages; QML used to write a property that did not exist (auditoria D13).
    Q_PROPERTY(bool sizeLinked READ sizeLinked WRITE setSizeLinked NOTIFY sizeLinkedChanged)
    Q_PROPERTY(double masterVolume READ masterVolume
                   WRITE setMasterVolume NOTIFY masterVolumeChanged)
    Q_PROPERTY(bool masterMuted READ masterMuted
                   WRITE setMasterMuted NOTIFY masterMutedChanged)
    Q_PROPERTY(bool playbackBenchmarkRunning READ playbackBenchmarkRunning NOTIFY playbackBenchmarkRunningChanged)
    // Session-only localhost MCP for agents. Off at every launch, unless startOnLaunch
    // opts back in. QML: EditorState.mcp.running, EditorState.mcp.url, and the rest.
    Q_PROPERTY(McpController *mcp READ mcp CONSTANT)
    // The keyframe strip draws every animated property of the selected clip. This is the subset
    // the user has folded away: a view filter only — hiding a curve never changes what renders.
    Q_PROPERTY(QStringList keyframeGraphHiddenProperties READ keyframeGraphHiddenProperties
                   NOTIFY keyframeGraphVisibilityChanged)
    // Detected beats / onsets for the keyframe strip. Transient analysis state — never
    // saved with the project, cleared whenever the underlying audio could have moved.
    Q_PROPERTY(QVariantMap beatAnalysis READ beatAnalysis NOTIFY beatAnalysisChanged)
    Q_PROPERTY(bool beatAnalysisRunning READ beatAnalysisRunning NOTIFY beatAnalysisChanged)
    // A scene template's cuts are being fitted to its music (fitTemplateCutsToBeat).
    Q_PROPERTY(bool templateBeatFitRunning READ templateBeatFitRunning NOTIFY templateBeatFitChanged)
    // The grid and the transients are independently shown and snapped to. Both come out of
    // one analysis pass — the tempo is derived from the same onset envelope — so these
    // gate display and snapping, not the DSP.
    Q_PROPERTY(bool beatGridVisible READ beatGridVisible WRITE setBeatGridVisible
                   NOTIFY beatAnalysisChanged)
    Q_PROPERTY(bool onsetsVisible READ onsetsVisible WRITE setOnsetsVisible
                   NOTIFY beatAnalysisChanged)
    Q_PROPERTY(bool subtitleEditing READ subtitleEditing WRITE setSubtitleEditing NOTIFY subtitleEditingChanged)
    Q_PROPERTY(int selectedSubtitleCue READ selectedSubtitleCue WRITE setSelectedSubtitleCue
                   NOTIFY selectedSubtitleCueChanged)
    Q_PROPERTY(bool undoAvailable READ undoAvailable NOTIFY undoStackChanged)
    Q_PROPERTY(bool redoAvailable READ redoAvailable NOTIFY undoStackChanged)
    Q_PROPERTY(bool exportInProgress READ exportInProgress NOTIFY exportInProgressChanged)
    Q_PROPERTY(double exportProgress READ exportProgress NOTIFY exportProgressChanged)
    Q_PROPERTY(bool canShareExport READ canShareExport NOTIFY canShareExportChanged)
    Q_PROPERTY(bool subtitleGenerating READ subtitleGenerating NOTIFY subtitleGeneratingChanged)
    Q_PROPERTY(double subtitleGenProgress READ subtitleGenProgress NOTIFY subtitleGenProgressChanged)
    Q_PROPERTY(QString subtitleGenStatus READ subtitleGenStatus NOTIFY subtitleGenStatusChanged)
    Q_PROPERTY(bool reverseRendering READ reverseRendering NOTIFY reverseRenderingChanged)
    Q_PROPERTY(double reverseRenderProgress READ reverseRenderProgress NOTIFY reverseRenderProgressChanged)
    Q_PROPERTY(QString reverseRenderStatus READ reverseRenderStatus NOTIFY reverseRenderStatusChanged)
    // Multicam punching session. The live project is not touched until Save; switches rewrite a
    // staged copy that playback is pointed at so the program monitor shows the mix.
    Q_PROPERTY(bool multicamActive READ multicamActive NOTIFY multicamChanged)
    // One entry per selected camera: {trackIndex, label, clipName, hasClip, active}.
    Q_PROPERTY(QVariantList multicamAngles READ multicamAngles NOTIFY multicamChanged)
    // Index into multicamAngles assigned at the playhead; -1 outside the session range.
    Q_PROPERTY(int multicamActiveAngle READ multicamActiveAngle NOTIFY multicamChanged)
    // Bumped whenever a fresh set of tiles lands; QML appends it as ?rev= to defeat the
    // URL-keyed image cache, the same way the segmentation window does.
    Q_PROPERTY(int multicamRevision READ multicamRevision NOTIFY multicamFramesChanged)
    // Staged program as a single lane: {start, duration, name, angle}. Empty before a session
    // has cameras.
    Q_PROPERTY(QVariantList multicamProgramClips READ multicamProgramClips NOTIFY multicamChanged)
    // There is enough imported video to build a rig from, and no visual clips that building one
    // would disturb. Drives the window's "set this up for me" offer.
    Q_PROPERTY(bool multicamCanSetUp READ multicamCanSetUp NOTIFY multicamChanged)
    Q_PROPERTY(int selectedTrack READ selectedTrack NOTIFY selectionChanged)
    Q_PROPERTY(int selectedClip READ selectedClip NOTIFY selectionChanged)
    Q_PROPERTY(QVariantList selection READ selection NOTIFY selectionChanged)
    // Change token and size for the selection, so a clip delegate can ask "am I selected?" and
    // "is this a multi-selection?" without the whole selection being rebuilt into QVariantMaps
    // once per delegate — which made a marquee over N clips cost O(N^2) per mouse move.
    Q_PROPERTY(int selectionRevision READ selectionRevision NOTIFY selectionChanged)
    Q_PROPERTY(int selectionCount READ selectionCount NOTIFY selectionChanged)
    Q_PROPERTY(QVariantMap selectedClipData READ selectedClipData NOTIFY selectedClipDataChanged)
    Q_PROPERTY(QVariantList selectedClipEffects READ selectedClipEffects NOTIFY selectedClipDataChanged)
    Q_PROPERTY(QVariantList selectedClipAudioEffects READ selectedClipAudioEffects NOTIFY selectedClipDataChanged)
    Q_PROPERTY(QVariantMap selectedTransitionData READ selectedTransitionData NOTIFY selectedTransitionDataChanged)
    Q_PROPERTY(int selectedTransitionTrack READ selectedTransitionTrack NOTIFY selectedTransitionDataChanged)
    Q_PROPERTY(int selectedTransitionLeftClip READ selectedTransitionLeftClip NOTIFY selectedTransitionDataChanged)
    // Tracks picked from their headers (ids, so a reorder keeps them), as in Premiere.
    Q_PROPERTY(QStringList selectedTrackIds READ selectedTrackIds NOTIFY selectedTracksChanged)
    // Every set the picker offers: built-ins, the app-wide library, then copies carried by the
    // project for sets this machine's library does not have. Each {id, name, builtIn, active,
    // inLibrary, items}.
    Q_PROPERTY(QVariantList guideSets READ guideSets NOTIFY guidesChanged)
    // The items of every active set, flattened for drawing.
    Q_PROPERTY(QVariantList guideItems READ guideItems NOTIFY guidesChanged)
    Q_PROPERTY(bool inlineTextEditing READ inlineTextEditing NOTIFY inlineTextEditingChanged)
    Q_PROPERTY(QVariantList actions READ actions NOTIFY shortcutsChanged)
    Q_PROPERTY(QVariantList bookmarks READ bookmarks NOTIFY bookmarksChanged)
    Q_PROPERTY(bool workAreaActive READ workAreaActive NOTIFY workAreaChanged)
    Q_PROPERTY(double workAreaInSeconds READ workAreaInSeconds NOTIFY workAreaChanged)
    Q_PROPERTY(double workAreaOutSeconds READ workAreaOutSeconds NOTIFY workAreaChanged)
    Q_PROPERTY(bool loopWorkAreaEnabled READ loopWorkAreaEnabled WRITE setLoopWorkAreaEnabled
                   NOTIFY loopWorkAreaEnabledChanged)
    Q_PROPERTY(QString lastMessage READ lastMessage NOTIFY lastMessageChanged)
    // Severity of lastMessage: "info" | "success" | "warning" | "error". Exists so
    // the QML toast host does not have to guess from the message wording — it used
    // to regex the prose, and none of the real failure strings matched, so a
    // corrupt-project open rendered as a neutral info toast.
    Q_PROPERTY(QString lastMessageSeverity READ lastMessageSeverity NOTIFY lastMessageChanged)
    Q_PROPERTY(int draggingAssetIndex READ draggingAssetIndex WRITE setDraggingAssetIndex NOTIFY draggingAssetIndexChanged)
    Q_PROPERTY(bool separateAudioAvailable READ canSeparateAudioSelection NOTIFY editCapabilitiesChanged)
    Q_PROPERTY(bool makeCompositeAvailable READ canMakeCompositeFromSelection NOTIFY editCapabilitiesChanged)
    Q_PROPERTY(bool transformTogetherAvailable READ canTransformSelectionTogether NOTIFY editCapabilitiesChanged)
    // Open composite tabs as [{id, name}], main timeline excluded; "" is the main timeline's id.
    Q_PROPERTY(QVariantList sequenceTabs READ sequenceTabs NOTIFY sequenceTabsChanged)
    Q_PROPERTY(QString activeSequenceId READ activeSequenceId NOTIFY sequenceTabsChanged)
    Q_PROPERTY(bool unlinkAvailable READ canUnlinkSelection NOTIFY editCapabilitiesChanged)
    Q_PROPERTY(bool linkAvailable READ canLinkSelection NOTIFY editCapabilitiesChanged)
    Q_PROPERTY(bool mergeAvailable READ canMergeSelection NOTIFY editCapabilitiesChanged)
    Q_PROPERTY(bool textToSubtitleAvailable READ canConvertSelectionToSubtitle NOTIFY editCapabilitiesChanged)
    // False until the user picks a launch layout (or decides later via first-clip setup / load).
    Q_PROPERTY(bool projectLayoutChosen READ projectLayoutChosen NOTIFY projectLayoutChosenChanged)

public:
    explicit AppController(AssetLibrary *assetLibrary, QObject *parent = nullptr);
    ~AppController() override;

    // The first half of applyProjectJson. Touches no controller state, so a load runs it on a
    // worker and hands the result to applyParsedProject on the GUI thread.
    struct ParsedProject {
        drift::Project project;
        QJsonObject root;
    };
    static std::optional<ParsedProject> parseProjectJson(const QByteArray &data, QString *error);
    static std::optional<ParsedProject> parseProjectJson(const QJsonObject &root, QString *error);

    AssetLibrary *assetLibrary() const { return m_assetLibrary; }
    CloudProviders *cloudProviders() const { return m_cloud; }
    MediaBinController *bin() const { return m_bin; }
    PlaybackEngine *playback() { return &m_playback; }
    PreviewController *preview() const { return m_preview; }
    PreferencesController *preferences() const { return m_preferences; }
    ProjectFileController *projectFile() const { return m_projectFile; }
    AssetPreviewController *assetPreview() const { return m_assetPreview; }
    SpeedCurveController *speedCurve() const { return m_speedCurve; }
    CurveEditorController *curves() const { return m_curves; }
    SegmentationController *segmentation() const { return m_segmentation; }
    SceneDetectController *scenes() const { return m_sceneDetect; }
    DepthController *depth() const { return m_depth; }
    DenoiseController *denoise() const { return m_denoise; }
    RestoreController *restore() const { return m_restore; }
    FaceTrackingController *faces() const { return m_faces; }
    MotionTrackController *motionTrack() const { return m_motionTrack; }
    BodyController *body() const { return m_body; }
    StabilizeController *stabilize() const { return m_stabilize; }
    TtsController *tts() const { return m_tts; }
    VoiceLibrary *voices() const { return m_voices; }
    McpController *mcp() const { return m_mcpController; }
    QVariantList audioOutputDevices() const;
    QString audioOutputDeviceId() const { return m_audioOutputDeviceId; }
    void setAudioOutputDeviceId(const QString &id);

    bool isRecordingAudio() const;
    bool isAudioRecordingPaused() const;
    int recordingTrackIndex() const;
    float audioRecordLevel() const;
    float audioRecordGain() const;
    Q_INVOKABLE void setAudioRecordGain(float gain);
    double audioRecordSeconds() const;
    QVariantList audioRecordLivePeaks() const;
    QVariantList availableMicrophones() const;
    QString currentMicrophoneName() const;

    Q_INVOKABLE void startAudioRecording(int trackIndex = -1);
    Q_INVOKABLE void pauseAudioRecording();
    Q_INVOKABLE void resumeAudioRecording();
    Q_INVOKABLE void toggleAudioRecordingPause();
    Q_INVOKABLE void stopAudioRecording();
    Q_INVOKABLE void cancelAudioRecording();
    Q_INVOKABLE void selectMicrophone(const QString &id);
    // Handing out a mutable pointer is the point past which this object can no longer know what
    // happened to the project, so the derived caches are dropped here rather than trusted. Two
    // bool writes, and nothing in src/ takes this overload — it exists for tests and for code
    // that edits the project behind the controller's back, which is exactly the case that would
    // otherwise read a stale tracks() list.
    drift::Project *project()
    {
        m_tracksCacheValid = false;
        m_durationCacheValid = false;
        return &m_project;
    }
    const drift::Project *project() const { return &m_project; }

    QVariantList tracks() const;
    // The clips of one track, as a role model. This is where the timeline delegate's data lives;
    // `tracks` above carries only what the panel's JS helpers need to lay a row out. Index slots
    // are never reused or freed, so a model handed to a Repeater stays valid for the session.
    Q_INVOKABLE QObject *clipsModel(int trackIndex) const;
    quint32 tracksRevision() const { return m_tracksRevision; }
    int trackCount() const { return m_project.tracks().size(); }
    int clipCount() const;
    double playheadSeconds() const;
    double durationSeconds() const;
    // {start, duration} covering every clip on a video or audio track, for the subtitle lane's
    // voice waveform. In C++ because the QML that needed it was reading the whole `tracks` graph.
    Q_INVOKABLE QVariantMap mediaExtentSeconds() const;
    bool playing() const { return m_playing; }
    bool previewDragActive() const { return m_previewDragActive; }
    bool snapEnabled() const { return m_snapEnabled; }
    bool rippleEnabled() const { return m_rippleEnabled; }
    bool allowClipOverlap() const { return m_allowClipOverlap; }
    bool projectPortrait() const { return m_project.height() > m_project.width(); }
    bool mediaGridMode() const { return m_mediaViewMode == QLatin1String("grid"); }
    QString mediaViewMode() const { return m_mediaViewMode; }
    bool autoKeyEnabled() const { return m_autoKeyEnabled; }
    bool positionLinked() const { return m_positionLinked; }
    void setPositionLinked(bool linked);
    bool sizeLinked() const { return m_sizeLinked; }
    void setSizeLinked(bool linked);
    double masterVolume() const;
    void setMasterVolume(double volume);
    bool masterMuted() const;
    void setMasterMuted(bool muted);
    // Every clip in the project as a flat run of numbers — lane, clip-type code, start seconds,
    // duration seconds — for the overview strip's canvas. Flat because the strip repaints off
    // it: a list of numbers costs a fraction of what converting the clip graph to JS does.
    Q_INVOKABLE QVariantList timelineOverviewBlocks() const;
    // How many bands the strip splits its height into. Adjustment lanes are drawn inside their
    // parent's row on the timeline and get no band of their own here.
    Q_INVOKABLE int timelineOverviewLaneCount() const;
    QStringList keyframeGraphHiddenProperties() const { return m_keyframeGraphHiddenProperties; }
    bool subtitleEditing() const { return m_subtitleEditing; }
    int selectedSubtitleCue() const { return m_selectedSubtitleCue; }
    bool undoAvailable() const { return m_undoStack.canUndo(); }
    bool redoAvailable() const { return m_undoStack.canRedo(); }
    bool exportInProgress() const { return m_exportInProgress; }
    double exportProgress() const;
    bool canShareExport() const;
    bool subtitleGenerating() const { return m_subtitleGenerating; }
    double subtitleGenProgress() const { return m_subtitleGenProgress; }
    QString subtitleGenStatus() const { return m_subtitleGenStatus; }
    bool reverseRendering() const { return m_reverseRendering; }
    double reverseRenderProgress() const { return m_reverseProgress; }
    QString reverseRenderStatus() const { return m_reverseStatus; }
    int selectedTrack() const { return m_selectedTrack; }
    int selectedClip() const { return m_selectedClip; }
    QVariantList selection() const;
    int selectionRevision() const { return m_selectionRevision; }
    int selectionCount() const { return m_selection.size(); }

    // For the scene-graph timeline, which draws in C++ and should not go through QVariant.
    // Same values the QML waveform and filmstrip queries return; empty means still decoding.
    QVector<float> waveformDisplayPeaks(const QString &path, double startSeconds, double durSeconds,
                                        int buckets, int audioStreamIndex, int channel = -1) const;
    QStringList waveformChannelNames(const QString &path, int audioStreamIndex) const;
    QString filmstripTilePath(const QString &path, int level, qint64 index,
                              int rotationCorrection) const;
    QVariantMap selectedClipData() const;
    QVariantList selectedClipEffects() const;
    QVariantList selectedClipAudioEffects() const;
    QVariantMap selectedTransitionData() const;
    int selectedTransitionTrack() const { return m_selectedTransitionTrack; }
    int selectedTransitionLeftClip() const { return m_selectedTransitionLeftClip; }
    QStringList selectedTrackIds() const;
    QVariantList guideSets() const;
    QVariantList guideItems() const;
    Q_INVOKABLE void setGuideSetActive(const QString &id, bool active);
    // Edges of the active guides for a canvas of this size, as {x: [px], y: [px]}.
    Q_INVOKABLE QVariantMap guideSnapTargets(double width, double height) const;
    // Library editing. Built-in sets and project-only copies are read-only; each returns the new id.
    Q_INVOKABLE QString createGuideSet(const QString &name);
    Q_INVOKABLE QString duplicateGuideSet(const QString &id);
    Q_INVOKABLE void renameGuideSet(const QString &id, const QString &name);
    Q_INVOKABLE void deleteGuideSet(const QString &id);
    // Copies a set the project carries into this machine's library.
    Q_INVOKABLE void saveGuideSetToLibrary(const QString &id);
    Q_INVOKABLE QString addGuideItem(const QString &setId, const QString &kind);
    // key: pos, left, top, right, bottom, aspectW, aspectH, color, opacity or locked.
    Q_INVOKABLE void setGuideItemProperty(const QString &setId, const QString &itemId,
                                          const QString &key, const QVariant &value);
    Q_INVOKABLE void removeGuideItem(const QString &setId, const QString &itemId);
    QVariantList actions() const;
    QVariantList bookmarks() const;
    bool workAreaActive() const { return m_project.hasWorkArea(); }
    double workAreaInSeconds() const;
    double workAreaOutSeconds() const;
    bool loopWorkAreaEnabled() const { return m_loopWorkAreaEnabled; }
    void setLoopWorkAreaEnabled(bool enabled);
    QString lastMessage() const { return m_lastMessage; }
    QString lastMessageSeverity() const { return m_lastMessageSeverity; }
    int draggingAssetIndex() const { return m_draggingAssetIndex; }
    void setDraggingAssetIndex(int index);

    void setPlayheadSeconds(double seconds);
    void setPlaying(bool playing);
    void setSnapEnabled(bool enabled);
    void setRippleEnabled(bool enabled);
    void setAllowClipOverlap(bool enabled);
    void setMediaGridMode(bool enabled);
    void setMediaViewMode(const QString &mode);
    void setAutoKeyEnabled(bool enabled);
    Q_INVOKABLE QVariantMap debugInfo() const;
    Q_INVOKABLE QString debugInfoText() const;
    Q_INVOKABLE void copyDebugInfo();

    // Playback diagnostics. The environment and counter half is cheap enough to call whenever
    // the dialog opens; the benchmark decodes for a couple of seconds and so runs off the GUI
    // thread and answers with playbackBenchmarkFinished.
    bool playbackBenchmarkRunning() const { return m_benchmarkRunning.load(); }
    Q_INVOKABLE QVariantMap playbackDiagnostics() const;
    Q_INVOKABLE void startPlaybackBenchmark();
    // One paste for a bug report: host facts and codec support followed by what playback is
    // actually doing. Split across two clipboard copies, reporters send whichever tab they
    // happened to have open, which is rarely the one that explains the problem.
    //
    // `benchmarkInfo` carries only the sweep's own sections — the live rows are collected here,
    // beside the host facts. Taking them from the dialog instead meant the two halves of a
    // pasted report described different moments: the rows were captured when the dialog opened
    // and never refreshed, so a report could say NVDEC in one section and Direct3D 11 in the
    // other, for the same machine, in the same paste.
    Q_INVOKABLE void copyDiagnosticsReport(const QVariantMap &benchmarkInfo);


    JobRegistry *jobRegistry() const { return m_jobs; }

    struct GeneratedAudioImport
    {
        bool ok = false;
        QString errorCode; // "not_found" | "import_failed"
        QString error;
        QString assetId;
        double durationSeconds = -1.0; // -1 when the asset has no probed duration yet
        QString clipId;                // set when a clip was placed
    };
    // Imports an audio file the app generated, waits for its probe, records `generator` on the
    // asset and, with `place`, drops a clip at atSeconds. track < 0 picks the first audio lane with
    // room for the whole clip, else a new one. Blocks in a nested event loop: GUI thread only.
    GeneratedAudioImport importGeneratedAudio(const QString &path, const QJsonObject &generator,
                                              bool place, double atSeconds, int track);

    struct GeneratedAudioPlacement
    {
        QString path; // already imported through importGeneratedAudio
        double atSeconds = 0.0;
    };
    // Lays the clips out on new audio tracks as one undo step. A clip that would overlap the
    // previous one on a lane goes on the next lane that is free, adding lanes as needed. Returns
    // how many clips were placed.
    int placeGeneratedAudioOnNewTracks(const QList<GeneratedAudioPlacement> &items,
                                       const QString &undoText);

    void setAddonManager(AddonManager *manager);
    // Also hears Stock's templates: installed ones reload the Templates tab, "Use" places them.
    void setMarketClient(MarketClient *client);
    MarketClient *marketClient() const { return m_marketClient; }
    AddonManager *addonManager() const { return m_addonManager; }
    // Strip chip click — folds `prop`'s curve away, or brings it back. Purely a view filter: the
    // chip stays put either way, and the animation keeps playing while it is hidden.
    Q_INVOKABLE void toggleKeyframeGraphPropertyVisible(const QString &prop);
    // Editing a property's value/diamond/interpolation un-hides its curve, so the thing just
    // edited is the thing on screen.
    Q_INVOKABLE void showKeyframeGraphProperty(const QString &prop);
    void setSubtitleEditing(bool editing);
    void setSelectedSubtitleCue(int index);
    void setProjectName(const QString &name);

    Q_INVOKABLE void addClipFromAsset(int assetIndex);
    // Multi-select "Add to timeline": each asset lands on its own kind-appropriate default
    // track (creating one if needed, exactly like addClipFromAsset), placed back to back in
    // the given order starting at the playhead — not all stacked on top of each other at the
    // same start time. One undo step for the whole batch.
    Q_INVOKABLE void addClipsFromAssets(const QStringList &assetIds);
    Q_INVOKABLE void addClipFromAssetAt(int assetIndex, int trackIndex, double atSeconds);
    Q_INVOKABLE void addClipFromAssetOnNewTrack(int assetIndex, double atSeconds);
    // Same, but the new track goes at insertIndex rather than always on top, so
    // a timeline drop can create a lane below the tracks as well as above them.
    Q_INVOKABLE void addClipFromAssetOnNewTrackAt(int assetIndex, int insertIndex, double atSeconds);
    Q_INVOKABLE int clipCountForAsset(int assetIndex) const;
    Q_INVOKABLE bool removeAsset(int assetIndex);
    // Multi-select bulk removal, one undo step for the whole batch. Like removeAsset, refuses
    // the whole batch if any id is still referenced by a clip (see clipCountForAsset) — the
    // guard is enforced here, not just by the QML confirmation flow, so a caller that skips
    // that flow can't orphan a timeline clip. Ids that no longer resolve are skipped.
    // Returns how many were actually removed.
    Q_INVOKABLE int removeAssets(const QStringList &assetIds);

    // Explicit destructive variant used only after user confirmation. Removes every
    // timeline clip referencing the selected assets, cleans transitions that reference
    // those clips, then removes the assets from the project. The source files on disk
    // are never touched. The whole operation is recorded as one undo step.
    Q_INVOKABLE int removeAssetsAndClips(const QStringList &assetIds);
    // Bin label only — does not rename the file on disk or rewrite clip names.
    Q_INVOKABLE bool renameAsset(int assetIndex, const QString &name);
    // Bin-preview orientation for a video asset (absolute 0/90/180/270; -1 = the file's own tag),
    // as one undoable edit — AssetLibrary::setAssetRotation on its own leaves no undo entry.
    Q_INVOKABLE bool setAssetRotation(int assetIndex, int degrees);
    Q_INVOKABLE bool setClipSourceFrame(const QString &clipId, double x, double y, double w, double h);
    Q_INVOKABLE bool trackAcceptsAsset(int trackIndex, int assetIndex) const;
    Q_INVOKABLE QString trackTypeForAsset(int assetIndex) const;
    // The same two questions asked of a bare media kind ("video", "audio", "image", ...) rather
    // than of a bin row. A file dragged in from the file manager has no row yet — it is not
    // imported until it is dropped — but its extension already says which track it belongs on,
    // which is all the drag preview needs to promise a landing spot.
    Q_INVOKABLE bool trackAcceptsKind(int trackIndex, const QString &mediaKind) const;
    Q_INVOKABLE QString trackTypeForKind(const QString &mediaKind) const;
    // presetId applies a built-in style pack on create; empty keeps the default text style.
    Q_INVOKABLE void addTextClip(const QString &text, double atSeconds,
                                 const QString &presetId = QString(), int trackIndex = -1);
    Q_INVOKABLE void addSubtitleClip(double atSeconds);
    // A combined template from Extras: one text clip per part, placed and timed together, one undo.
    void addTextTemplate(const drift::TextPreset &preset, double atSeconds);
    // Import a subtitle file (.srt, .vtt, .ass/.ssa) as a new subtitle clip at the playhead (or atSeconds).
    Q_INVOKABLE bool importSubtitleFile(const QUrl &url, double atSeconds = -1.0);
    // Replace cues on an existing subtitle clip from a subtitle file (.srt, .vtt, .ass/.ssa).
    Q_INVOKABLE bool importSubtitleFileIntoClip(int trackIndex, int clipIndex, const QUrl &url);
    // Export a subtitle clip's cues as SRT, WebVTT or ASS (by extension). Timestamps are clip-local unless timelineTimes,
    // which offsets them by the clip's start so they line up with the exported video.
    Q_INVOKABLE bool exportSubtitleFile(int trackIndex, int clipIndex, const QUrl &url,
                                        bool timelineTimes = false);
    // maxWordsPerCue caps words per caption; 0 keeps the recommended (character-width) packing.
    Q_INVOKABLE void generateSubtitlesForClip(int trackIndex, int clipIndex,
                                              const QString &language = QString(),
                                              int maxWordsPerCue = 0);
    // Captions every selected video/audio clip into one subtitle clip (falls back to the focused
    // clip). Returns false when the selection cannot be transcribed, e.g. clips overlap in time.
    // The same run with Whisper's translate task: English captions, on a track of their own and
    // placed above the original ones, for bilingual videos.
    Q_INVOKABLE bool generateEnglishSubtitlesForSelection(const QString &language = QString(),
                                                          int maxWordsPerCue = 0);
    Q_INVOKABLE bool generateSubtitlesForSelection(const QString &language = QString(),
                                                   int maxWordsPerCue = 0);
    // Same, for the given (track, clip) pairs instead of the selection.
    bool generateSubtitlesForClips(const QList<QPair<int, int>> &pairs, const QString &language = QString(),
                                   int maxWordsPerCue = 0);
    // Captions every video/audio clip on the track within [startSec, endSec) into one subtitle clip.
    bool generateSubtitlesForRange(int trackIndex, double startSec, double endSec,
                                   const QString &language = QString(), int maxWordsPerCue = 0);
    Q_INVOKABLE void cancelSubtitleGeneration();
    Q_INVOKABLE QVariantList whisperLanguages();

    // Starts a punching session from the current video selection (two or more clips on
    // distinct tracks). Returns false when there is nothing to punch and no empty-timeline
    // setup to offer; the window should stay closed.
    Q_INVOKABLE bool beginMulticamSession();
    Q_INVOKABLE void endMulticamSession();
    bool multicamActive() const { return m_multicamActive; }
    QVariantList multicamAngles() const;
    int multicamActiveAngle() const;
    quint64 multicamPlayheadSignature() const;
    int multicamRevision() const { return m_multicamRevision; }
    QVariantList multicamProgramClips() const;
    bool multicamCanSetUp() const;
    // One video track per imported camera, stacked from the top, extras muted. One undoable
    // edit; if a session is already open it then snapshots those clips as the cameras.
    Q_INVOKABLE void setUpMulticamFromAssets();
    // Punch `angleIndex` at the playhead on the staged copy. The live project is untouched.
    Q_INVOKABLE void switchMulticamAngle(int angleIndex);
    Q_INVOKABLE void saveMulticamAsSeparateTracks();
    Q_INVOKABLE void saveMulticamCombined();

    Q_INVOKABLE void clearClipSpeedCurve(int trackIndex, int clipIndex);

    Q_INVOKABLE void setTransitionEasing(int trackIndex, const QString &transitionId,
                                         const QString &curve);


    // Whether the optional object-labelling pass can run. False until the object-model
    // addon is installed, which is what the panel's toggle is gated on.
    Q_INVOKABLE bool objectDetectionAvailable() const;
    // shapeKind/shapeId is a catalog id from builtinShapes(), which is not always a ShapeKind name:
    // "circle" and "ellipse" are the same kind with different default aspects.
    Q_INVOKABLE void addShapeClip(const QString &shapeKind, double atSeconds);
    Q_INVOKABLE void addShapeClipAt(const QString &shapeId, int trackIndex, double atSeconds);
    Q_INVOKABLE void addAdjustmentClip(double atSeconds = -1.0, double durationSeconds = -1.0);
    Q_INVOKABLE void addAdjustmentClipAt(int trackIndex, double atSeconds = -1.0, double durationSeconds = -1.0);
    Q_INVOKABLE void addAdjustmentClipWithEffect(const QString &effectId, int trackIndex = -1, double atSeconds = -1.0, double durationSeconds = -1.0);

    // Adjustment tracks and lanes. `kind` is "videoEffects" | "audioEffects" | "mask".
    //
    // A standalone track applies to everything composited below it; a lane is nested in one
    // track and applies only to that track's clips. Which of the two you get is the whole
    // difference between the two placements, so they are separate calls rather than a flag.
    Q_INVOKABLE void addAdjustmentTrack(const QString &kind);
    // False, with the reason, for an effect that reads one clip's face landmarks or depth map
    // aimed at a standalone adjustment layer (trackIndex < 0 means a new one): the canvas it
    // grades has neither, so the effect would silently do nothing.
    bool effectFitsTrack(int trackIndex, const QString &effectId, QString *why = nullptr) const;
    // Index of a lane on `parentTrackIndex` able to hold `kind` over [atSeconds, +durationSeconds),
    // creating one when every existing lane is occupied there. Returns -1 if the parent cannot
    // take a lane. Note this shifts track indices when it inserts.
    Q_INVOKABLE int ensureAdjustmentLane(int parentTrackIndex, const QString &kind,
                                         double atSeconds = -1.0, double durationSeconds = -1.0);
    // Move an adjustment clip between the two placements. Both unlink it first: a pinned
    // adjustment belongs to its clip's track, so re-scoping it would leave the link meaningless.
    // `atSeconds` < 0 keeps the adjustment where it is on the timeline; a drag passes the
    // position it was released at.
    Q_INVOKABLE void moveAdjustmentToLane(int fromTrack, int fromClip, int parentTrackIndex,
                                          double atSeconds = -1.0);
    Q_INVOKABLE void moveAdjustmentToOwnTrack(int fromTrack, int fromClip,
                                              double atSeconds = -1.0);
    // Release an adjustment from the clip it is pinned to, leaving it where it is. Its edges
    // become draggable and it stops following the clip.
    Q_INVOKABLE void unlinkAdjustment(int trackIndex, int clipIndex);
    Q_INVOKABLE void relinkAdjustment(int trackIndex, int clipIndex, int mediaTrack, int mediaClip);
    // What an adjustment or mask layer applies to, as Photoshop's clipped adjustment layers:
    // everything below it (standalone), one track (a lane) or one clip of it (a pinned lane).
    // {mode: "allBelow"|"track"|"clip", targetTrack, targetClipId, targets: [{track, clip, id,
    // name, kind, trackLabel}]}; targets are the visual clips below it that it overlaps, nearest
    // track first. Empty for anything that is not such a layer.
    Q_INVOKABLE QVariantMap adjustmentTargetState(int trackIndex, int clipIndex) const;
    // One undo step that re-scopes it and keeps it selected: targetTrack < 0 for everything below,
    // else that track, pinned to `targetClip` when it is >= 0.
    Q_INVOKABLE void setAdjustmentTarget(int trackIndex, int clipIndex, int targetTrack, int targetClip);
    Q_INVOKABLE void addStickerClip(const QString &stickerId, double atSeconds,
                                    int trackIndex = -1);
    Q_INVOKABLE QVariantList builtinStickers() const;
    Q_INVOKABLE QVariantList builtinStickerCategories() const;
    // The full emoji set behind the sticker packs; empty until the pack carrying the font is
    // installed.
    Q_INVOKABLE QVariantList emojiCatalog() const;
    Q_INVOKABLE QStringList emojiGroups() const;
    Q_INVOKABLE QString emojiFontFamily() const;
    Q_INVOKABLE void addEmojiClip(const QString &emoji, const QString &name, double atSeconds,
                                  int trackIndex = -1);
    Q_INVOKABLE QVariantList builtinShapes() const;
    Q_INVOKABLE QVariantList builtinShapeCategories() const;
    // Shapes installed from Stock (AppData/shapes): the same rows as builtinShapes() plus
    // `user: true`, and the categories they use. Shown after the built-in ones in Shapes and Masks.
    Q_INVOKABLE QVariantList userShapes() const;
    Q_INVOKABLE QVariantList userShapeCategories() const;
    Q_INVOKABLE bool removeUserShape(const QString &shapeId);
    // The scene camera as the preview's camera overlay needs it: {active, track, clip} plus the
    // seven values, all at the playhead. Taken once when a drag starts, so the drag solves from a
    // fixed starting point instead of accumulating its own rounding.
    Q_INVOKABLE QVariantMap cameraStateAtPlayhead() const;

    // Asset drag-and-drop. One resolver for every kind a browser can lift (AssetDrag.qml has
    // the list; media keeps its own asset-index path), shared by the desktop and phone
    // timelines and both previews (the preview's own pair is on PreviewController). plan* only says what a drop would do — the hover outline
    // comes from it — and drop* does exactly that, so the two cannot disagree.
    //
    // A plan is {accepted, mode, track, clip, landingStart, landingDuration, newTrackIndex,
    // message}; mode is "clip" (applied to a clip), "gap" (lands on the track), "newTrack",
    // "junction" (between two clips), or "canvas" (a preview drop). `newTrackIndex` >= 0 asks
    // for a fresh track inserted at that index.
    Q_INVOKABLE bool trackAcceptsDropKind(int trackIndex, const QString &kind) const;
    Q_INVOKABLE bool isPlaceableDropKind(const QString &kind) const;
    Q_INVOKABLE QVariantMap planAssetDrop(const QString &kind, const QString &payload, int trackIndex,
                                          double seconds, int newTrackIndex) const;
    Q_INVOKABLE QVariantMap dropAsset(const QString &kind, const QString &payload, const QString &label,
                                      int trackIndex, double seconds, int newTrackIndex);
    // Preview › "⋯" and right-click: mode "fit" shows the whole picture, "cover" fills the canvas
    // keeping its proportions (centred, the overflow cut off by the frame), "stretch" fills it exactly.
    Q_INVOKABLE void fillCanvasWithClip(int trackIndex, int clipIndex, const QString &mode);
    // Pixel of an Item.grabToImage result, for the colour eyedropper; transparent when outside.
    Q_INVOKABLE QColor imagePixel(const QImage &image, int x, int y) const;
    // Left clip of the cut a transition dropped at this time would bridge, or -1.
    Q_INVOKABLE int transitionJunctionAt(int trackIndex, double seconds) const;
    Q_INVOKABLE void beginPreviewDrag(const QString &undoText = {});
    Q_INVOKABLE void previewSetClipPosition(int trackIndex, int clipIndex, double xPixels, double yPixels);
    Q_INVOKABLE void previewSetClipSize(int trackIndex, int clipIndex, double widthPixels, double heightPixels);
    Q_INVOKABLE void previewSetClipRect(int trackIndex, int clipIndex, double xPixels, double yPixels,
                                        double widthPixels, double heightPixels);
    // Text resizes scale the glyphs along with the box, so the size rides with the rect.
    Q_INVOKABLE void previewSetTextRect(int trackIndex, int clipIndex, double xPixels, double yPixels,
                                        double widthPixels, double heightPixels, double pixelSize);
    Q_INVOKABLE void previewSetClipRotation(int trackIndex, int clipIndex, double degrees);
    Q_INVOKABLE void previewSetClipKeyframe(int trackIndex, int clipIndex, const QString &prop,
                                            double atSeconds, double value);
    Q_INVOKABLE void previewSetEffectParam(int trackIndex, int clipIndex, int effectIndex,
                                           const QString &key, double value);
    Q_INVOKABLE void previewSetEffectVec2Param(int trackIndex, int clipIndex, int effectIndex,
                                               const QString &key, double x, double y);
    // Needs an explicit beginPreviewDrag; the colour eyedropper bypasses the effect it is picking
    // for (a chroma key would otherwise sample its own keyed-out output) and then cancels.
    Q_INVOKABLE void previewSetEffectEnabled(int trackIndex, int clipIndex, int effectIndex,
                                             bool enabled);
    Q_INVOKABLE void previewSetClipSpeed(int trackIndex, int clipIndex, double speed);
    Q_INVOKABLE void previewSetClipMask(int trackIndex, int clipIndex, const QVariantMap &mask);
    Q_INVOKABLE void previewSetClipFade(int trackIndex, int clipIndex, double fadeInSeconds, double fadeOutSeconds);
    Q_INVOKABLE void commitPreviewDrag();
    Q_INVOKABLE void cancelPreviewDrag();
    Q_INVOKABLE void applyCanvasCrop(double x, double y, double width, double height);
    Q_INVOKABLE bool timelineHasVisualClips() const;
    Q_INVOKABLE bool shouldConfigureProjectForAsset(int assetIndex) const;
    Q_INVOKABLE QVariantMap suggestedProjectSetupForAsset(int assetIndex) const;
    bool projectLayoutChosen() const { return m_projectLayoutChosen; }
    Q_INVOKABLE void markProjectLayoutChosen();
    Q_INVOKABLE void selectClip(int trackIndex, int clipIndex);
    // Selects a clip by id. Pinning a mask or adding an effect inserts a lane and normalization
    // reorders, so an index captured before the edit is stale by the time there is something to select.
    Q_INVOKABLE bool selectClipById(const QString &clipId);
    Q_INVOKABLE void addToSelection(int trackIndex, int clipIndex);
    Q_INVOKABLE void setSelection(const QVariantList &pairs);
    Q_INVOKABLE void selectAllClips();
    Q_INVOKABLE void clearSelection();
    Q_INVOKABLE QVariantMap clipAt(int trackIndex, int clipIndex) const;
    Q_INVOKABLE QVariantMap activeVideoClipAtPlayhead() const;
    Q_INVOKABLE QVariantMap activeAudioClipAtPlayhead() const;
    Q_INVOKABLE double sourceTimeAtPlayhead() const;
    Q_INVOKABLE double sourceTimeForClip(const QVariantMap &clip) const;
    Q_INVOKABLE void deleteSelectedClip();
    Q_INVOKABLE void duplicateSelectedClip();
    Q_INVOKABLE void moveClip(int trackIndex, int clipIndex, double newStart);
    Q_INVOKABLE void moveClipToTrack(int trackIndex, int clipIndex, int newTrackIndex, double newStart);
    // While a clip is dragged: where it would land on targetTrack and which clips moveClip /
    // moveClipToTrack would push right to make room, so the timeline can open the space live
    // (as CapCut does) instead of only on release. {start, ids, delta}; ids empty when nothing moves.
    Q_INVOKABLE QVariantMap moveRoomPreview(const QString &clipId, int targetTrack, double newStart) const;
    // Dragging a clip above the top track or below the last one: a new track of the clip's kind
    // is made at insertIndex and the clip moves onto it, in one undo step (as on CapCut).
    Q_INVOKABLE void moveClipToNewTrack(int trackIndex, int clipIndex, int insertIndex, double newStart);
    // Shifts every clip on `trackIndex` starting at/after `gapStartSeconds` left by the
    // width of the gap immediately following that position, closing it. Linked partner
    // clips on other tracks (e.g. a companion audio clip) follow along to stay in sync.
    Q_INVOKABLE void closeGap(int trackIndex, double gapStartSeconds);
    Q_INVOKABLE void alignSelectedClipLeft();
    Q_INVOKABLE void alignSelectedClipRight();
    // Mirrors drift::Haptics::TrimState (Haptics.h), which has documented since it was written
    // that it mirrors this enum. It does now — before, it mirrored nothing.
    enum TrimOutcome {
        TrimNone = 0,
        TrimMoved = 1,
        TrimSnapped = 2,
        TrimBlocked = 3,
    };
    Q_ENUM(TrimOutcome)

    Q_INVOKABLE void splitSelectedClipLeft();
    Q_INVOKABLE void splitSelectedClipRight();
    Q_INVOKABLE void splitAtPlayhead();
    Q_INVOKABLE void splitClipAt(int trackIndex, int clipIndex, double seconds);
    Q_INVOKABLE void splitClipLeftAt(int trackIndex, int clipIndex, double seconds);
    Q_INVOKABLE void splitClipRightAt(int trackIndex, int clipIndex, double seconds);
    // What a trim would do, without doing it. The drag previews through these: applying the
    // edit on every pointer sample meant rebuilding the whole timeline model each time, which on
    // a heavy project cost far more than the edit itself. The commit on release runs the very
    // same computation, so the clip lands exactly where the preview showed it.
    //
    // Returns { ok, changed, outcome, start, duration, inPoint, outPoint } in seconds, or
    // { ok: false } for an out-of-range clip.
    Q_INVOKABLE QVariantMap previewTrimLeft(int trackIndex, int clipIndex, double newStart) const;
    Q_INVOKABLE QVariantMap previewTrimRight(int trackIndex, int clipIndex, double newEnd) const;

    // Opens and closes a trim drag. Scoping the gesture lets a repeated pointer position be
    // rejected before any work is done, and lets the caller find out whether the edge ever
    // actually moved — a press and release with no movement must not leave an undo step behind.
    Q_INVOKABLE void beginTrimGesture(int trackIndex, int clipIndex, int side);
    Q_INVOKABLE void endTrimGesture();
    // The whole release in one call: the edit, closing the gesture, and the undo commit. Done
    // separately from QML they sent three "the timeline changed" notifications -- one for the
    // edit, one for the undo push, one from finishEdit -- and each rebuilt the entire timeline
    // model. `side` < 0 is the left edge. `seconds` < 0 means the gesture never moved the edge,
    // so there is nothing to commit.
    Q_INVOKABLE void commitTrim(int trackIndex, int clipIndex, int side, double seconds);
    Q_INVOKABLE bool trimGestureChangedProject() const { return m_trimGestureChanged; }

    // One step of a live trim drag, in timeline seconds. Returns a TrimOutcome rather than void:
    // snapping and every limit that can stop this edge live inside these, and the one the user
    // most needs told — the source running out — has no cue on screen at all. Haptics::trimStep
    // has always been handed this return value; until the enum existed it was reading undefined.
    Q_INVOKABLE int trimClipLeft(int trackIndex, int clipIndex, double newStart);
    Q_INVOKABLE int trimClipRight(int trackIndex, int clipIndex, double newEnd);
    Q_INVOKABLE void setClipTrim(int trackIndex, int clipIndex, double inPoint, double outPoint);
    Q_INVOKABLE void setClipStart(int trackIndex, int clipIndex, double start);
    Q_INVOKABLE void setClipDuration(int trackIndex, int clipIndex, double duration);
    Q_INVOKABLE void setClipTextContent(int trackIndex, int clipIndex, const QString &text);
    // Display label on the timeline / inspector. Does not rename the source file.
    Q_INVOKABLE void setClipName(int trackIndex, int clipIndex, const QString &name);
    // Switches a clip off (or back on) without removing it: it keeps every setting, but the
    // compositor leaves it out. What an adjustment layer's on/off switch does.
    Q_INVOKABLE void setClipDisabled(int trackIndex, int clipIndex, bool disabled);

    // A standalone adjustment layer's mask stack (Clip::mask then Clip::extraMasks). Adding puts
    // the new mask in focus; the focused one is what setClipMask, the Masks tab, the preview
    // handles and the "mask.<key>" keyframes edit.
    Q_INVOKABLE bool addLayerMask(int trackIndex, int clipIndex, const QString &shapeId);
    Q_INVOKABLE void setLayerMaskFocus(int trackIndex, int clipIndex, int index);
    Q_INVOKABLE bool removeLayerMask(int trackIndex, int clipIndex, int index);
    static QVariantList layerMaskList(const drift::Clip &clip);
    // A clip's masks either cut it (the default) or limit where its effects and colour show.
    Q_INVOKABLE void setMasksLimitEffects(int trackIndex, int clipIndex, bool limit);
    Q_INVOKABLE void commitTextEdit(int trackIndex, int clipIndex, const QString &text);
    bool inlineTextEditing() const { return m_inlineTextEditing; }

    // In-place editing where the compositor's render is the only visible text. A hidden QML
    // TextEdit feeds the keyboard and the input method; every change re-renders the clip live with
    // a caret, a selection and a preedit underline drawn over it. The clip stays visible and rests
    // (no in/out/loop animation). One undo step covers the whole edit.
    //
    // Offsets are UTF-16 into the model text, the editor's own, which never holds the preedit; the
    // preedit is inserted at `cursor` for rendering only.
    Q_INVOKABLE void beginInlineTextEdit(int trackIndex, int clipIndex);
    Q_INVOKABLE void updateInlineTextEdit(int trackIndex, int clipIndex, const QString &text, int cursor,
                                          int selStart, int selEnd, const QString &preeditText);
    // commit: one undo step (no step when nothing changed); otherwise the original text returns.
    Q_INVOKABLE void endInlineTextEdit(bool commit);
    // Geometry in canvas (project pixel) coordinates, rotation included. A quad is four points,
    // top-left, top-right, bottom-right, bottom-left of the clip's unrotated box, then rotated.
    // The caret's quad is the bar as drawn. Empty when no inline edit is active.
    Q_INVOKABLE QVariantList inlineCaretQuad() const;
    Q_INVOKABLE QVariantList inlineSelectionQuads() const;
    // Canvas point -> model offset (the nearest caret stop; never inside the preedit).
    Q_INVOKABLE int inlineHitTest(const QPointF &canvasPoint) const;
    // {start, end} around the model offset.
    Q_INVOKABLE QVariantMap inlineWordAt(int pos) const;
    // Up/Down: remembers the column across consecutive moves.
    Q_INVOKABLE int inlineMoveCaretLines(int pos, int deltaLines);
    // Home/End of the line holding pos.
    Q_INVOKABLE int inlineLineEdge(int pos, bool toEnd) const;
    Q_INVOKABLE void setSubtitleCues(int trackIndex, int clipIndex, const QVariantList &cues);
    // Find & replace across a subtitle clip's captions (whole words, any case); returns how many
    // captions changed. `remember` also adds the pair to the subtitle dictionary.
    Q_INVOKABLE int replaceInSubtitles(int trackIndex, int clipIndex, const QString &find,
                                       const QString &replace, bool remember);
    // Hesitations out, first letters up, dictionary applied — what new captions get.
    Q_INVOKABLE void cleanUpSubtitles(int trackIndex, int clipIndex);
    // The user's corrections ([{find, replace}]), applied to every generated caption.
    Q_INVOKABLE QVariantList subtitleDictionary() const;
    Q_INVOKABLE void setSubtitleDictionary(const QVariantList &entries);
    // The text style auto captions are created with (a text preset id) and whether they are
    // cleaned up as they arrive.
    Q_INVOKABLE QString subtitleStylePreset() const;
    Q_INVOKABLE void setSubtitleStylePreset(const QString &presetId);
    Q_INVOKABLE bool subtitleCleanupEnabled() const;
    Q_INVOKABLE void setSubtitleCleanupEnabled(bool enabled);
    // Caption-ready styles for the picker: built-in caption packs then the add-on "subtitulos".
    Q_INVOKABLE QVariantList subtitleStyleChoices() const;
    // Emojis for keywords at the end of captions: an option for new captions, and an action.
    Q_INVOKABLE bool subtitleEmojisEnabled() const;
    Q_INVOKABLE void setSubtitleEmojisEnabled(bool enabled);
    Q_INVOKABLE void addEmojisToSubtitles(int trackIndex, int clipIndex);
    Q_INVOKABLE void previewSetSubtitleCues(int trackIndex, int clipIndex, const QVariantList &cues);
    Q_INVOKABLE double subtitleLocalPlayheadSeconds(int trackIndex, int clipIndex) const;
    Q_INVOKABLE void upsertSubtitleCueAtPlayhead(int trackIndex, int clipIndex, const QString &text);
    Q_INVOKABLE void seekToSubtitleCue(int trackIndex, int clipIndex, int cueIndex);
    Q_INVOKABLE void setTextStyle(int trackIndex, int clipIndex, const QVariantMap &style);

    // Los tramos del texto (0.23): {start, end, colorEnabled, color, sizeEnabled, sizeScale,
    // boldEnabled, bold, italicEnabled, italic}. Leerlos para la ventana de Texto avanzado y
    // reemplazarlos de una vez (una sola entrada de deshacer).
    Q_INVOKABLE QVariantList textRuns(int trackIndex, int clipIndex);
    Q_INVOKABLE void setTextRuns(int trackIndex, int clipIndex, const QVariantList &runs);
    // The text bar on the letters [start, end): only the keys given (color, sizeScale, bold, italic,
    // underline, fontFamily) change, and what those letters already had stays.
    Q_INVOKABLE void patchTextRuns(int trackIndex, int clipIndex, int start, int end, const QVariantMap &patch);
    // The letters [start, end) of that text clip that the inspector has shaded (0.24, as in
    // Filmora). While set, the layer calls (add/remove/duplicate/move/set/preview), the looks, the
    // templates and the quick styles edit the stack those letters paint with, not the block's.
    // -1, -1 clears it. The inspector sets it whenever its selection changes.
    Q_INVOKABLE void setTextStyleRange(int trackIndex, int clipIndex, int start, int end);


    // A window that edits live and ends in Apply or Cancel (Texto avanzado, 0.23): every edit made
    // in between lands in one undo step, and Cancel takes all of it back. Ending one that was
    // never begun does nothing.
    Q_INVOKABLE void beginEditSession(const QString &label);
    Q_INVOKABLE void endEditSession(bool keep);
    // The shading stack of a text, subtitle or shape clip: layers[0] is drawn first. Each call
    // is one undo step; the preview variants coalesce into one through begin/commitPreviewDrag.
    Q_INVOKABLE QString addStyleLayer(int trackIndex, int clipIndex, const QString &kind, int atIndex = -1);
    Q_INVOKABLE bool removeStyleLayer(int trackIndex, int clipIndex, const QString &layerId);
    Q_INVOKABLE QString duplicateStyleLayer(int trackIndex, int clipIndex, const QString &layerId);
    Q_INVOKABLE bool moveStyleLayer(int trackIndex, int clipIndex, const QString &layerId, int toIndex);
    Q_INVOKABLE void setStyleLayer(int trackIndex, int clipIndex, const QString &layerId, const QVariantMap &patch);
    Q_INVOKABLE void previewSetStyleLayer(int trackIndex, int clipIndex, const QString &layerId, const QVariantMap &patch);
    // The text-only spellings, kept for the MCP tools and scripts that use them.
    // `rangeStart`/`rangeEnd` (0.24): con letras sombreadas, la capa va solo a esas letras.
    Q_INVOKABLE QString addTextLayer(int trackIndex, int clipIndex, const QString &kind, int atIndex = -1,
                                     int rangeStart = -1, int rangeEnd = -1);
    Q_INVOKABLE bool removeTextLayer(int trackIndex, int clipIndex, const QString &layerId);
    Q_INVOKABLE QString duplicateTextLayer(int trackIndex, int clipIndex, const QString &layerId);
    Q_INVOKABLE bool moveTextLayer(int trackIndex, int clipIndex, const QString &layerId, int toIndex);
    Q_INVOKABLE void setTextLayer(int trackIndex, int clipIndex, const QString &layerId, const QVariantMap &patch);
    Q_INVOKABLE void previewSetTextLayer(int trackIndex, int clipIndex, const QString &layerId, const QVariantMap &patch);
    // In / Out / Loop animation slots: {preset, params, duration, stagger, unit, order, ease, …}.
    Q_INVOKABLE void setTextAnimationSlot(int trackIndex, int clipIndex, const QString &slot, const QVariantMap &patch);
    Q_INVOKABLE void previewSetTextAnimationSlot(int trackIndex, int clipIndex, const QString &slot, const QVariantMap &patch);
    Q_INVOKABLE void clearTextAnimationSlot(int trackIndex, int clipIndex, const QString &slot);
    Q_INVOKABLE QVariantList textAnimationPresets(const QString &slot = {}) const;
    Q_INVOKABLE QVariantList textAnimationCategories(const QString &slot) const;
    // Video › Animation: the clip animation presets of a slot ("in", "out", "combo"), their chips,
    // and a preset's pose at a progress (for the gallery's live cards).
    Q_INVOKABLE QVariantList clipAnimationPresets(const QString &slot) const;
    Q_INVOKABLE QVariantList clipAnimationCategories(const QString &slot) const;
    Q_INVOKABLE QVariantMap clipAnimationPreviewSample(const QString &presetId, double progress) const;
    // Where to seek to preview the slot: the window start (In), before the exit (Out), the playhead (Loop).
    Q_INVOKABLE double textAnimationSlotStartSeconds(int trackIndex, int clipIndex, const QString &slot) const;
    // Looks: one-click recipes that rewrite the layer stack from a few params.
    Q_INVOKABLE QVariantList textLooks() const;
    Q_INVOKABLE void applyTextLook(int trackIndex, int clipIndex, const QString &lookId, const QVariantMap &params = {});
    // The Básico / Efectos quick styles and the Burbuja backgrounds (core/TextQuickStyles.h):
    // {id, label, category} lists, their categories as {id, label}, and one-step apply.
    Q_INVOKABLE QVariantList textQuickStyles() const;
    Q_INVOKABLE QVariantList textQuickStyleCategories() const;
    Q_INVOKABLE void applyTextQuickStyle(int trackIndex, int clipIndex, const QString &styleId,
                                      int rangeStart = -1, int rangeEnd = -1);
    Q_INVOKABLE QVariantList textBubbles() const;
    Q_INVOKABLE QVariantList textBubbleCategories() const;
    Q_INVOKABLE void applyTextBubble(int trackIndex, int clipIndex, const QString &bubbleId);
    Q_INVOKABLE void setTextLookParam(int trackIndex, int clipIndex, const QString &key, const QVariant &value);
    Q_INVOKABLE void previewSetTextLookParam(int trackIndex, int clipIndex, const QString &key, const QVariant &value);
    Q_INVOKABLE QVariantList textPaintEffects() const;
    Q_INVOKABLE QVariantList textGradientPresets() const;
    // Copies this caption clip's style (not its keyframes) to every other subtitle clip on the
    // track ("track") or in the project ("project"). Returns how many changed; one undo step.
    Q_INVOKABLE int applyTextStyleToCaptions(int trackIndex, int clipIndex, const QString &scope = QStringLiteral("track"));
    // Animation presets imported from Lottie (After Effects text animators) or exported earlier.
    // Returns {ok, id, error, unsupported:[…]}; the preset lands in the slot's "Imported" category.
    Q_INVOKABLE QVariantMap importTextAnimationPreset(const QUrl &fileUrl, const QString &slot = {});
    Q_INVOKABLE bool renameUserTextAnimationPreset(const QString &presetId, const QString &label);
    // A text clip's In / Out / Loop slot as one of the user's own animations: the slot's preset
    // with the clip's settings as its defaults, listed under "Mine". Returns the new id.
    Q_INVOKABLE QString saveTextAnimationAsPreset(int trackIndex, int clipIndex, const QString &slot,
                                                  const QString &label);
    // The visual animation editor (Personalizar): a slot as the animator list it plays, to edit
    // and send back through setTextAnimationSlot({animators, particles, …}). A preset is expanded
    // for this slot, an inline slot gives its own, an empty one a fade by character (a gentle
    // wiggle on Loop). Returns {animators, particles, delay, durationOverride, period, source:
    // "preset"|"inline"|"new", label}.
    Q_INVOKABLE QVariantMap textAnimationSlotForEditing(int trackIndex, int clipIndex, const QString &slot) const;
    // The animator list as a slot stores it: defaults dropped, enum spellings settled.
    Q_INVOKABLE QVariantList normalizeTextAnimators(const QVariantList &animators) const;
    Q_INVOKABLE bool deleteUserTextAnimationPreset(const QString &presetId);
    Q_INVOKABLE bool exportUserTextAnimationPreset(const QString &presetId, const QUrl &fileUrl);
    // Human label for a text keyframe property ("Shadow · Blur"); empty for non-text props.
    Q_INVOKABLE QString keyframePropertyLabel(int trackIndex, int clipIndex, const QString &prop) const;
    Q_INVOKABLE void applyTextPreset(int trackIndex, int clipIndex, const QString &presetId);
    Q_INVOKABLE QVariantList textPresets() const;
    // Style packs the user saved from the inspector. Kept out of textPresets() so the built-in
    // catalog (and the MCP list it feeds) stays a stable, shippable set.
    Q_INVOKABLE QVariantList userTextPresets() const;
    // The library id of the style installed from a Stock item ("flip:text-style:<id>"), or empty
    // while it has not been downloaded.
    Q_INVOKABLE QString stockTextPresetId(const QString &stockItemId) const;
    // Template packs from Extras (kind "text-styles"): {id, label, category, sampleText}, and their
    // categories {id, label} in display order.
    Q_INVOKABLE QVariantList addonTextPresets() const;
    Q_INVOKABLE QVariantList addonTextPresetCategories() const;
    Q_INVOKABLE QString saveTextStyleAsPreset(int trackIndex, int clipIndex, const QString &label);
    Q_INVOKABLE bool renameUserTextPreset(const QString &presetId, const QString &label);
    // Saves the look of a text clip over one of My styles, so a style can be refined in place.
    Q_INVOKABLE bool updateUserTextPreset(const QString &presetId, int trackIndex, int clipIndex);
    Q_INVOKABLE bool deleteUserTextPreset(const QString &presetId);
    Q_INVOKABLE bool exportUserTextPreset(const QString &presetId, const QUrl &fileUrl);
    Q_INVOKABLE bool importUserTextPreset(const QUrl &fileUrl);
    Q_INVOKABLE QVariantList fontCatalog() const;
    Q_INVOKABLE QVariantList fontCategories() const;
    // Several font files at once, through importFontFile. {ok, families, error}.
    Q_INVOKABLE QVariantMap importFonts(const QList<QUrl> &urls);
    // Most recently picked families first, at most eight.
    Q_INVOKABLE QStringList recentFonts() const;
    Q_INVOKABLE void noteRecentFont(const QString &family);
    // Families of the system fonts not already offered by the font catalog; computed once.
    Q_INVOKABLE QStringList systemFontFamilies() const;
    Q_INVOKABLE QStringList userFonts() const;
    // The families the file provides (empty on failure, with a toast).
    Q_INVOKABLE QStringList importFontFile(const QUrl &fileUrl);
    Q_INVOKABLE bool removeUserFont(const QString &family);
    Q_INVOKABLE void setClipBlendMode(int trackIndex, int clipIndex, const QString &mode);
    Q_INVOKABLE bool setClipSpeed(int trackIndex, int clipIndex, double speed);
    Q_INVOKABLE void setClipReverse(int trackIndex, int clipIndex, bool reverse);
    // Turns reverse on for a video clip and renders the proxy that makes it play back smoothly.
    // Reverse itself applies immediately; cancelling the render leaves the clip reversed on the
    // slow live-decode path, which is what clipHasReverseProxy reports.
    // Entry point for the Reverse control. Clips a proxy would do nothing for (audio, or one
    // already covered by a render) reverse straight away; anything else emits
    // reverseConfirmRequested so the dialog can ask before starting a render.
    Q_INVOKABLE void requestClipReverse(int trackIndex, int clipIndex);
    Q_INVOKABLE void applyClipReverse(int trackIndex, int clipIndex);
    Q_INVOKABLE void cancelReverseRender();
    Q_INVOKABLE bool clipHasReverseProxy(int trackIndex, int clipIndex) const;
    Q_INVOKABLE void setClipFlip(int trackIndex, int clipIndex, bool flipH, bool flipV);
    // Corner pin: {enabled, points: [x0, y0, … x3, y3]} in project px, the corners' offsets.
    Q_INVOKABLE void setClipCornerPin(int trackIndex, int clipIndex, const QVariantMap &pin);
    // Per-clip "3D layer" switch: the tilt/depth/perspective values render (and get grips) only
    // while it is on. Off keeps the values.
    Q_INVOKABLE void setClipLayer3d(int trackIndex, int clipIndex, bool enabled);
    // Per-clip opt-in: let depth decide what covers this clip instead of the track order. Needs
    // the 3D switch on and a Normal blend mode; does nothing otherwise.
    Q_INVOKABLE void setClipDepthOcclude(int trackIndex, int clipIndex, bool enabled);
    // Stereo balance, -1..+1. previewSet* coalesces a slider drag into one undo entry the way
    // previewSetClipSpeed does; setClipPan is the one-shot for typing or resetting to centre.
    Q_INVOKABLE void previewSetClipPan(int trackIndex, int clipIndex, double pan);
    Q_INVOKABLE void setClipPan(int trackIndex, int clipIndex, double pan);
    Q_INVOKABLE void setClipRotationSnap(int trackIndex, int clipIndex, double degrees);
    // Discrete, lossless orientation fix (absolute 0/90/180/270, as the inspector shows it) —
    // distinct from the free decorative "Angle" above. Re-fits the clip's box for the new
    // orientation and decodes losslessly; see drift::Clip::rotationCorrection.
    Q_INVOKABLE void setClipOrientation(int trackIndex, int clipIndex, int degrees);
    Q_INVOKABLE bool canMergeSelection() const;
    Q_INVOKABLE void mergeSelectedClips();
    // True when the track holds two or more subtitle clips.
    Q_INVOKABLE bool canMergeAllSubtitlesOnTrack(int trackIndex) const;
    // Merge every subtitle clip on the track into one, regardless of the selection.
    Q_INVOKABLE void mergeAllSubtitlesOnTrack(int trackIndex);
    // One text clip per non-empty cue, placed at the cue's time on a text track; the subtitle
    // clip is removed. Each keeps the subtitle's style and layout.
    Q_INVOKABLE void convertSubtitleToTextClips(int trackIndex, int clipIndex);
    // True when the selection is made up only of text clips.
    Q_INVOKABLE bool canConvertSelectionToSubtitle() const;
    // Replaces the selected text clips with one subtitle clip, one cue per text clip. Style,
    // layout and keyframes come from the earliest clip; the rest contribute only text and timing.
    Q_INVOKABLE void convertSelectionToSubtitle();
    Q_INVOKABLE bool canSeparateAudioSelection() const;
    Q_INVOKABLE void separateAudioFromSelection();

    // Composite clips: a nested timeline played as one clip. Making one moves the selection (and
    // its linked partners) into a new sequence and leaves a composite clip in its place.
    Q_INVOKABLE bool canMakeCompositeFromSelection() const;
    Q_INVOKABLE void makeCompositeFromSelection();

    // Transform layers: a Range adjustment track whose Transform clips move, scale, rotate, tilt
    // and fade every visual track from just below it down to its span end, as one.
    //
    // A layer at the top spanning to the lowest visual track, with one identity clip over the
    // whole timeline (at least 5 s).
    Q_INVOKABLE void addTransformTrack();
    // An identity transform clip on the layer at `trackIndex`; `atSeconds` < 0 is the playhead.
    Q_INVOKABLE void addTransformClip(int trackIndex, double atSeconds = -1.0,
                                      double durationSeconds = -1.0);
    // A layer covering just `trackIndex`, with a clip spanning that track's content.
    Q_INVOKABLE void addTransformLayerAbove(int trackIndex);
    // The toolbar/Add entry: "Transform together" with a selection, otherwise a layer at the top
    // covering everything below with a 5 s clip at the playhead.
    Q_INVOKABLE void addTransformLayerForSelection();
    bool canTransformSelectionTogether() const;

    // The scene camera: one viewpoint the whole sequence is seen through (engine/SceneCamera3d.h).
    // Stored as Camera clips on a Camera adjustment track, so the camera animates on the timeline
    // with the ordinary keyframe machinery and two clips in a row read as a camera cut.
    //
    // Adds the camera track with one clip at rest over the sequence's length, or just the clip
    // when the track is already there. A camera at rest changes nothing on screen, which is what
    // makes this safe to offer from a menu. Selects the new clip.
    Q_INVOKABLE void addCameraTrack();
    // A camera clip on the existing camera track; `atSeconds` < 0 is the playhead. Use this for a
    // camera cut.
    Q_INVOKABLE void addCameraClip(double atSeconds = -1.0, double durationSeconds = -1.0);
    // True once the sequence has a camera track, whether or not any clip is on it.
    Q_INVOKABLE bool hasCameraTrack() const;
    Q_INVOKABLE void makeTransformLayerFromSelection();
    // A layer directly above the topmost track holding one of `clipIds`, spanning to the lowest,
    // with one clip over their time range (or [atSeconds, +durationSeconds) when given). One undo
    // step; selects the new clip. Returns {track, clip, id}, empty when no clip is on a visual track.
    QVariantMap makeTransformLayerForClips(const QStringList &clipIds, double atSeconds = -1.0,
                                           double durationSeconds = -1.0);
    // Sets the last track the layer at `trackIndex` covers; `endTrackId` must be one of
    // transformSpanOptions. One undo step. False when refused.
    Q_INVOKABLE bool setTransformSpan(int trackIndex, const QString &endTrackId);
    // The valid span ends for the layer at `trackIndex`, top to bottom:
    // [{endId, endIndex, firstIndex, count, kind: "only" | "range" | "all", current}]. An end never
    // cuts through a nested layer's span or reaches past an enclosing layer's end.
    Q_INVOKABLE QVariantList transformSpanOptions(int trackIndex) const;
    // {endIndex, endId, covers: [track indexes], count, depth} for the layer at `trackIndex`.
    Q_INVOKABLE QVariantMap transformLayerCoverage(int trackIndex) const;
    // The clips on covered tracks overlapping clips[clipIndex] of the layer, as [{track, clip}].
    Q_INVOKABLE QVariantList transformLayerCoveredClips(int trackIndex, int clipIndex) const;
    // The layers covering `trackIndex`, outermost first.
    Q_INVOKABLE QVariantList transformLayersCovering(int trackIndex) const;
    // What the layers over `trackIndex` do at the playhead: {active, affine, parent: [9], matrix, opacity}.
    Q_INVOKABLE QVariantMap transformParentAt(int trackIndex) const;
    // Selects the innermost transform clip over the selected clip (Shift+G).
    Q_INVOKABLE void selectTransformParent();
    // Selects the clips the transform clip at (trackIndex, clipIndex) moves.
    Q_INVOKABLE void selectTransformChildren(int trackIndex, int clipIndex);
    QVariantList sequenceTabs() const;
    // Every composite in the project as [{id, name}], open or not, for the timeline's switcher.
    Q_INVOKABLE QVariantList compositeSequences() const;
    QString activeSequenceId() const { return m_project.activeSequenceId(); }
    // Opens (or switches to) a composite's tab. "" switches to the main timeline.
    Q_INVOKABLE void openSequence(const QString &sequenceId);
    Q_INVOKABLE void openCompositeClip(int trackIndex, int clipIndex);
    Q_INVOKABLE void openCompositeAsset(const QString &assetId);
    Q_INVOKABLE void closeSequenceTab(const QString &sequenceId);
    // Renders the composite clip's range to a new video file and swaps the clip (and any audio
    // separated from it) over to that file. Runs in the background on the export slot.
    Q_INVOKABLE bool flattenComposite(int trackIndex, int clipIndex);
    // Puts a group's clips back on the main timeline where it plays them, as Photoshop's Ungroup.
    // One undo step. Refused (with a message) when the group has motion, speed, effects or layers
    // of its own that would be lost.
    Q_INVOKABLE bool ungroupComposite(int trackIndex, int clipIndex);
    Q_INVOKABLE void separateAllAudioTracks(int trackIndex, int clipIndex);
    Q_INVOKABLE void separateAllAudioTracksFromSelection();
    Q_INVOKABLE QVariantList clipAudioStreams(int trackIndex, int clipIndex) const;
    Q_INVOKABLE int clipAudioStreamCount(int trackIndex, int clipIndex) const;
    Q_INVOKABLE void setClipAudioStreamIndex(int trackIndex, int clipIndex, int streamIndex);
    Q_INVOKABLE bool canUnlinkSelection() const;
    Q_INVOKABLE void unlinkSelectedClips();
    Q_INVOKABLE bool canLinkSelection() const;
    Q_INVOKABLE void linkSelectedClips();
    Q_INVOKABLE void setClipMask(int trackIndex, int clipIndex, const QVariantMap &mask);

    // The mask shapes the assets panel offers as cards: {id, label} per entry. A "media" mask is
    // not here — it needs a file, so the panel asks for one and calls addMediaMaskToClip.
    Q_INVOKABLE QVariantList maskCatalog() const;
    // The mask as an SVG "d" string on the 0..100 grid MasksTab.qml scales from, for the
    // asset cards. Serialized from the same drift::maskPath the compositor rasterizes.
    Q_INVOKABLE QString maskShapeSvgPath(const QString &shape) const;
    // Pin a new mask to a clip, stacking on any already there rather than replacing them, and
    // select the mask adjustment it created. Ignores clips that cannot carry a mask.
    Q_INVOKABLE void addMaskToClip(int trackIndex, int clipIndex, const QString &shape);
    // Every mask adjustment pinned to this clip, oldest first, as
    // {track, index, id, name, shape, media}. A clip's masks live on adjustments in its lanes, not
    // on the clip, so this is what lets the inspector list them while the media clip is selected —
    // which is where a user looks for them after applying one.
    Q_INVOKABLE QVariantList linkedMaskClips(int trackIndex, int clipIndex) const;
    // The Video > Mask page edits a clip's masks in place, CapCut style, without moving the
    // selection to the mask's lane: it adds one and makes it the "focused" mask, which is the one
    // the keyframe rows (redirectToKeyframeHost) and the preview handles reach while the media
    // clip stays selected. Returns the new mask's clip id, or empty.
    Q_INVOKABLE QString addMaskToClipInPlace(int trackIndex, int clipIndex, const QString &shape);
    Q_INVOKABLE void setFocusedMask(const QString &maskClipId);
    Q_INVOKABLE QString focusedMask() const { return m_focusedMaskId; }
    // Deletes one mask (a Mask adjustment linked to a clip), and its lane when that empties it.
    Q_INVOKABLE void removeLinkedMask(int maskTrackIndex, int maskClipIndex);
    // A freeform/pen point the user picked in the preview, so the inspector's "Delete point" and
    // the Delete key act on it. -1: none. Not saved, not undoable: it is a view state.
    Q_PROPERTY(int maskPointFocus READ maskPointFocus WRITE setMaskPointFocus NOTIFY maskPointFocusChanged)
    int maskPointFocus() const { return m_maskPointFocus; }
    void setMaskPointFocus(int index)
    {
        if (m_maskPointFocus == index)
            return;
        m_maskPointFocus = index;
        emit maskPointFocusChanged();
    }
    Q_SIGNAL void maskPointFocusChanged();
    Q_SIGNAL void focusedMaskChanged();
    // A mask clip on one of `trackIndex`'s lanes, pinned to nothing: it masks whatever that track
    // shows over its span. This is what dropping a mask on empty track space means.
    Q_INVOKABLE void addMaskLaneClip(int trackIndex, const QString &shape, double atSeconds = -1.0,
                                     double durationSeconds = -1.0);
    // Pin an image or video as a raster mask, the way a segmentation matte is pinned.
    Q_INVOKABLE void addMediaMaskToClip(int trackIndex, int clipIndex, const QUrl &url);
    // Freeform vertex editing, driven by the preview overlay. `pointIndex` is the insertion slot,
    // so passing the index after an edge's first vertex splits that edge.
    Q_INVOKABLE void insertMaskPoint(int trackIndex, int clipIndex, int pointIndex, double x,
                                     double y);
    Q_INVOKABLE void removeMaskPoint(int trackIndex, int clipIndex, int pointIndex);
    // Partial patch: only the keys present are applied, like setTextStyle.
    Q_INVOKABLE void setShapeStyle(int trackIndex, int clipIndex, const QVariantMap &style);

    // Vector (Lottie / SVG) clips. `source` is the document text itself or a path to a .json/.svg
    // file; opts keys: kind (lottie|svg, else detected), fit, loop, offset (seconds), slots
    // ({id: value}), name, duration (seconds; default = the animation's own length, 5 s for a
    // still). Every reply is {ok, error?} plus the inspect summary of the document.
    Q_INVOKABLE bool vectorSupportAvailable() const;
    Q_INVOKABLE QVariantMap addVectorClip(const QString &source, int trackIndex, double atSeconds,
                                          const QVariantMap &opts = {});
    Q_INVOKABLE QVariantMap setVectorSource(int trackIndex, int clipIndex, const QString &source,
                                            const QVariantMap &opts = {});
    Q_INVOKABLE QString setVectorOptions(int trackIndex, int clipIndex, const QVariantMap &opts);
    // Keys: firstPage, lastPage (0 = through the end), layout, gridColumns, gap.
    Q_INVOKABLE QString setPdfOptions(int trackIndex, int clipIndex, const QVariantMap &opts);
    // A null/invalid value removes the override. Returns an error string, empty on success.
    Q_INVOKABLE QString setVectorSlot(int trackIndex, int clipIndex, const QString &name,
                                      const QVariant &value);
    // Declared slots with the clip's current overrides: [{id, type, value?}].
    Q_INVOKABLE QVariantList vectorSlots(int trackIndex, int clipIndex) const;
    Q_INVOKABLE QVariantMap inspectVector(const QString &source, const QString &kind = {}) const;
    Q_INVOKABLE QVariantMap inspectVectorClip(int trackIndex, int clipIndex) const;
    Q_INVOKABLE QString vectorSourceText(int trackIndex, int clipIndex) const;
    // 3D model (.glb) clips. opts keys: animation (index), loop, offset (seconds), name, duration
    // (seconds; default = the first animation's length, 5 s for a static model), and the pose /
    // light statics (scale, depth, rotX, rotY, rotZ, lightYaw, lightPitch, lightIntensity,
    // ambient) as plain values — keyframe them through setClipKeyframe with "model3d.<key>".
    Q_INVOKABLE QVariantMap addModel3dClip(const QString &path, int trackIndex, double atSeconds,
                                           const QVariantMap &opts = {});
    Q_INVOKABLE QVariantMap setModel3dSource(int trackIndex, int clipIndex, const QString &path,
                                             const QVariantMap &opts = {});
    // Returns an error string, empty on success.
    Q_INVOKABLE QString setModel3dOptions(int trackIndex, int clipIndex, const QVariantMap &opts);
    Q_INVOKABLE QVariantMap inspectModel3d(const QString &path) const;
    Q_INVOKABLE QVariantMap inspectModel3dClip(int trackIndex, int clipIndex) const;
    Q_INVOKABLE void setClipFade(int trackIndex, int clipIndex, double fadeInSeconds, double fadeOutSeconds);
    Q_INVOKABLE void setClipFadeCurve(int trackIndex, int clipIndex, const QString &curve);
    // which: "animIn" | "animOut" | "animCombo". Partial patch: kind / preset / duration / curve
    // (or legacy ease). A combo clears the in and out motion; an in or out motion clears the combo.
    Q_INVOKABLE void setClipAnimation(int trackIndex, int clipIndex, const QString &which,
                                      const QVariantMap &patch);
    // linkedAudio: also add the same transition between the two clips' linked audio, when they sit
    // next to each other on one audio track.
    Q_INVOKABLE void addTransition(int trackIndex, int clipIndex, const QString &kind, double durationSeconds,
                                   bool linkedAudio = true);
    Q_INVOKABLE void removeTransition(int trackIndex, const QString &transitionId);
    Q_INVOKABLE void setTransitionDuration(int trackIndex, const QString &transitionId, double durationSeconds);
    Q_INVOKABLE void setTransitionKind(int trackIndex, const QString &transitionId, const QString &kind);
    Q_INVOKABLE bool setTransitionParam(int trackIndex, const QString &transitionId, const QString &key,
                                        double value);
    Q_INVOKABLE void previewSetTransitionParam(int trackIndex, const QString &transitionId,
                                               const QString &key, double value);
    Q_INVOKABLE QVariantMap transitionBetweenClips(int trackIndex, int clipIndex) const;
    Q_INVOKABLE QVariantList transitionKinds() const;
    // The kinds that make sense on this track: on an audio track only those with an audible
    // curve (crossfade, dip); everything elsewhere.
    Q_INVOKABLE QVariantList transitionKindsForTrack(int trackIndex) const;
    Q_INVOKABLE QVariantList transitionCategories() const;
    Q_INVOKABLE void selectTransition(int trackIndex, int leftClipIndex);
    Q_INVOKABLE void clearTransitionSelection();
    // A colour property ("text.color") fans out to its four channel tracks (<prop>.r/g/b/a) as
    // one undo step. Clears every channel when the colour is invalid.
    Q_INVOKABLE void setClipColorKeyframe(int trackIndex, int clipIndex, const QString &prop,
                                          double atSeconds, const QColor &color);
    Q_INVOKABLE void setClipKeyframe(int trackIndex, int clipIndex, const QString &prop, double atSeconds,
                                     double value);
    // A vec2 effect param ("fx.<i>.<key>") keys its two axis tracks (<prop>.x/.y) as one undo step.
    Q_INVOKABLE void setClipVec2Keyframe(int trackIndex, int clipIndex, const QString &prop,
                                         double atSeconds, double x, double y);
    // Removes the key nearest atSeconds from each <prop><suffix> track as one undo step; for
    // params whose keys live on several channel tracks (colour ".r/.g/.b/.a", vec2 ".x/.y").
    Q_INVOKABLE void removeClipChannelKeyframes(int trackIndex, int clipIndex, const QString &prop,
                                                double atSeconds, const QStringList &suffixes);
    Q_INVOKABLE void removeClipKeyframe(int trackIndex, int clipIndex, const QString &prop, double atSeconds);
    Q_INVOKABLE void previewMoveClipKeyframe(int trackIndex, int clipIndex, const QString &prop,
                                             double fromSeconds, double toSeconds, double value);
    Q_INVOKABLE QVariantList clipKeyframes(int trackIndex, int clipIndex, const QString &prop) const;
    // Every property of the clip that carries an animation, in strip order.
    Q_INVOKABLE QStringList clipAnimatedProperties(int trackIndex, int clipIndex) const;
    // Whether a property's keyframes drive it. Switched off, the keys are kept but the property
    // holds its first key's value — the inspector row's label is what toggles this.
    Q_INVOKABLE bool clipPropertyKeyframesEnabled(int trackIndex, int clipIndex,
                                                  const QString &prop) const;
    Q_INVOKABLE void setClipPropertyKeyframesEnabled(int trackIndex, int clipIndex,
                                                     const QString &prop, bool enabled);
    Q_INVOKABLE void toggleClipPropertyKeyframesEnabled(int trackIndex, int clipIndex,
                                                        const QString &prop);
    Q_INVOKABLE double propertyValueAt(int trackIndex, int clipIndex, const QString &prop,
                                       double atSeconds, double fallback) const;
    // What the property evaluates to with no keyframes at all — the same implicit defaults
    // the compositor uses, so an unkeyed curve is drawn where the clip actually sits.
    Q_INVOKABLE double propertyBaseValue(int trackIndex, int clipIndex, const QString &prop,
                                         double fallback = 0.0) const;
    // Tangent handles for the curve editor. dx/dy arrive in seconds / property units, relative
    // to the key. `preview` variants coalesce a drag into one undo entry via begin/commitPreviewDrag.
    Q_INVOKABLE void setKeyframeTangents(int trackIndex, int clipIndex, const QString &prop,
                                         double atSeconds, double inDx, double inDy, double outDx,
                                         double outDy, bool corner);
    Q_INVOKABLE void previewSetKeyframeTangents(int trackIndex, int clipIndex, const QString &prop,
                                                double atSeconds, double inDx, double inDy,
                                                double outDx, double outDy, bool corner);
    Q_INVOKABLE void setKeyframeHold(int trackIndex, int clipIndex, const QString &prop,
                                     double atSeconds, bool hold);
    Q_INVOKABLE void setKeyframeInterpolation(int trackIndex, int clipIndex, const QString &prop,
                                              const QString &mode);
    // The key nearest atSeconds: "linear", "ease", "easeIn", "easeOut" or "hold".
    Q_INVOKABLE void setKeyframeEasingAt(int trackIndex, int clipIndex, const QString &prop,
                                         double atSeconds, const QString &mode);
    // The keys picked on a track's keyframe rows, each {clip, prop, seconds}, as one undo step:
    // their easing (the modes above), a cubic-bezier on the stretch each one starts (x1, y1, x2,
    // y2 as CSS's; on a last key, the stretch that ends there: Curvas, as the web's and CapCut's
    // Gráficos), or removed.
    Q_INVOKABLE void setKeyframesEasing(int trackIndex, const QVariantList &keys, const QString &mode);
    Q_INVOKABLE void setKeyframesCurve(int trackIndex, const QVariantList &keys, double x1, double y1,
                                       double x2, double y2);
    Q_INVOKABLE void removeKeyframes(int trackIndex, const QVariantList &keys);
    // Copy and paste of picked keys (0.22.1, After Effects' Ctrl+C / Ctrl+V on keys): the keys
    // ({clip, prop, seconds}) with their values and curves, by their time after the first one;
    // pasted on a clip's same properties starting at the playhead. Returns how many were copied.
    Q_INVOKABLE int copyKeyframes(int trackIndex, const QVariantList &keys);
    Q_INVOKABLE bool pasteKeyframes(int trackIndex, int clipIndex);
    Q_INVOKABLE bool hasCopiedKeyframes() const { return !m_keyClipboard.isEmpty(); }
    // A drag of the picked keys (each {clip, prop, seconds} where it started), inside a preview
    // drag: the keys that sit fromDelta seconds off their start move to toDelta off it, all
    // together, keeping their shape. The caller keeps them between their unpicked neighbours.
    Q_INVOKABLE void previewShiftKeyframes(int trackIndex, const QVariantList &keys, double fromDelta,
                                           double toDelta);
    // A key at atSeconds with the value the property already has there.
    Q_INVOKABLE void addClipKeyframeAt(int trackIndex, int clipIndex, const QString &prop,
                                       double atSeconds);
    Q_INVOKABLE void resetClipTransform(int trackIndex, int clipIndex);
    Q_INVOKABLE QVariantList effectCatalog() const;

    // LUTs (the color.lut effect). The factory looks that ship with the app and the ones the
    // person imported, each {id, name, path, factory, category}. Imported LUTs are copied into the
    // person's LUT library (AppData/luts), so the original can move or go without breaking a
    // project, and a project carried elsewhere finds them by name (CubeLut::resolve).
    Q_INVOKABLE QVariantList lutLibrary() const;
    // Checks a .cube file and copies it into the library: {ok, path, name} or {ok:false, error}.
    Q_INVOKABLE QVariantMap importLut(const QUrl &url);

    // Stock: puts a downloaded file where its kind belongs and says where on the status line.
    // `delivery` is the catalog's: "lut" (LUT library), "effect-preset" (My presets), "text-style"
    // (My styles), "text-animation" (text animations), "transition" (a .driftfx package into the
    // transitions folder) or "shape" (the shapes library). `done` runs exactly once, possibly
    // later — a package installs on a worker thread — with ok, a short phrase for the download
    // list saying where it went, the installed file or folder, an error, and what it is called in
    // its panel now (a LUT's, a style's, a shape's or a preset's id; empty when there is none).
    using StockInstallDone = std::function<void(bool ok, const QString &where, const QString &installedPath,
                                                const QString &error, const QString &localId)>;
    void installStockFile(const QString &delivery, const QString &path, const QString &title,
                          const StockInstallDone &done);
    // Mi cuenta › Stock downloads. mode "save" keeps the item where it belongs (Media for a file,
    // its own panel for an effect, a look, a LUT, a transition, a shape, a text style or animation,
    // a template); "place" also puts it in the edit: on the selected clip, text or cut, else at the
    // playhead. Downloads it first when this computer does not have it; says what it did on the
    // status line.
    Q_INVOKABLE void useStockLibraryItem(const QVariantMap &item, const QString &mode);
    // How a row of that list is delivered ("media", "lut", "scene-template"…), also for the
    // signed-out history, which keeps no delivery of its own for older downloads.
    Q_INVOKABLE QString stockLibraryDelivery(const QVariantMap &item) const;
    // {ok, name, missing, error, size, is3d} for a LUT path as a project saved it.
    Q_INVOKABLE QVariantMap lutInfo(const QString &path) const;
    // A small picture graded by the LUT (the real table applied on the CPU to a reference photo),
    // as a file URL, cached by the LUT file's contents. Empty when the LUT cannot be read.
    Q_INVOKABLE QUrl lutThumbnail(const QString &path) const;
    // The photo lutThumbnail draws that look on, without the look: the "before" of its card.
    Q_INVOKABLE QUrl lutReference(const QString &path) const;
    // Deletes an imported LUT from the library (never a factory one). Projects that used it keep
    // their saved path and report it missing.
    Q_INVOKABLE bool removeImportedLut(const QString &path);
    static QString lutLibraryDir();
    static QString factoryLutDir();
    void updateLutSearchDirs();
    Q_INVOKABLE QVariantList effectCategories() const;
    Q_INVOKABLE QVariantList effectTemplateCatalog() const;
    Q_INVOKABLE QVariantList effectTemplateCategories() const;
    Q_INVOKABLE void addEffect(int trackIndex, int clipIndex, const QString &effectId);
    // Retouch tiles: sets `values` on the clip's last effectId, adding it first when there is none,
    // and leaves the clip selected (addEffect moves the selection to the adjustment it creates,
    // which unloads the Video tab that asked).
    Q_INVOKABLE void applyRetouchLook(int trackIndex, int clipIndex, const QString &effectId,
                                      const QVariantMap &values);
    // The selected clip, or the top picture clip under the playhead.
    Q_INVOKABLE void applyEffectTemplateToCurrentClip(const QString &templateId);
    Q_INVOKABLE void applyEffectTemplate(int trackIndex, int clipIndex, const QString &templateId);
    // The single-clip effect template on this clip (its effects carry a template tag), for the
    // Effects › Template section: name, rhythm, intensity, decay. Empty when there is none.
    Q_INVOKABLE QVariantMap effectTemplateInfo(int trackIndex, int clipIndex) const;
    // Rebuilds every pulse of that template; 1 = as designed for both.
    Q_INVOKABLE void setEffectTemplateShape(int trackIndex, int clipIndex, double intensity,
                                            double decay);
    // "onset", "beat", "bar" or "clip"; analyses the music first when it has to.
    Q_INVOKABLE void setEffectTemplateRhythm(int trackIndex, int clipIndex, const QString &sync);
    // Takes the template's effects (and its speed curve) off the clip in one step.
    Q_INVOKABLE void removeEffectTemplate(int trackIndex, int clipIndex);
    // The composition a template made ("Template: …"), when this clip is one on the main timeline
    // or the open tab is one: {assetId, name, inside}. Empty otherwise.
    Q_INVOKABLE QVariantMap templateCompositeInfo(int trackIndex, int clipIndex) const;
    // Undoes a template applied as a composition: every instance on the main timeline is replaced
    // by the original clip (and what was linked to it) as it was before, without the template's
    // layers, and the composition leaves Media. One undo step. Refused, with a message, when an
    // instance has motion, speed or effects of its own that would be lost.
    Q_INVOKABLE bool removeTemplateComposite(const QString &assetId);
    // Scene templates (SceneTemplates.cpp): packaged little edits that go in as one composition
    // with photo slots and texts to fill. {id, name, category, categoryLabel, thumbnail, preview,
    // slots, texts, durationSec, width, height, premium, tags}.
    Q_INVOKABLE QVariantList sceneTemplates() const;
    Q_INVOKABLE QVariantList sceneTemplateCategoryList() const;
    Q_INVOKABLE QString sceneTemplateCategoryLabelFor(const QString &categoryId) const;
    // At the playhead, on top of the stack. An empty project takes the template's size first.
    // Returns the composition clip's id, or empty.
    Q_INVOKABLE QString insertSceneTemplate(const QString &templateId);
    // The scene template asset behind a clip (or the open composition), or empty.
    Q_INVOKABLE QString sceneTemplateAssetAt(int trackIndex, int clipIndex) const;
    // {assetId, name, emptySlots, slots[{clipId, slotId, number, label, empty, kind, mediaName,
    // thumbnail, startSec, durationSec}], texts[{clipId, slotId, label, text, ...}]}.
    Q_INVOKABLE QVariantMap sceneTemplateInfo(const QString &compositeAssetId) const;
    // Puts a bin photo or video in a slot, cut to fill its box; one undo step.
    Q_INVOKABLE bool fillTemplateSlot(const QString &slotClipId, const QString &mediaAssetId);
    // Imports the files and fills the given slot, then the empty ones after it. Returns how many.
    Q_INVOKABLE int fillTemplateSlotsFromUrls(const QString &compositeAssetId, const QString &firstSlotClipId,
                                              const QList<QUrl> &urls);
    Q_INVOKABLE bool setTemplateText(const QString &textClipId, const QString &text);
    // Templates of one's own. Inside a composition a photo or video can be made a slot and a text
    // made editable: {kind: "media"|"text", marked, label}, empty when the clip can be neither.
    Q_INVOKABLE QVariantMap clipPlaceholderState(int trackIndex, int clipIndex) const;
    Q_INVOKABLE bool setClipPlaceholder(int trackIndex, int clipIndex, bool marked);
    // Opens the Save as template dialog (saveTemplateRequested) for a composition.
    Q_INVOKABLE void requestSaveTemplate(const QString &compositeAssetId);
    Q_INVOKABLE QString clipAssetId(int trackIndex, int clipIndex) const;
    // {name, slots, texts} of a composition, for that dialog.
    Q_INVOKABLE QVariantMap compositeTemplateSummary(const QString &compositeAssetId) const;
    // Writes the composition as a scene template under AppData/scene-templates ("My templates"):
    // its media copied in, its slots left empty, a thumbnail of its middle frame. Returns the id.
    Q_INVOKABLE QString saveCompositeAsTemplate(const QString &compositeAssetId, const QString &name,
                                                const QString &category = QString());
    // Only templates of one's own can be deleted.
    Q_INVOKABLE bool deleteUserSceneTemplate(const QString &templateId);
    // Faster use (0.14.0). Use with my photos: the installed templates that fit these files best
    // (slot count, the shape most of them have, the project's shape) as sceneTemplates() rows plus
    // {score, shape}, and what to ask Stock for: {count, shape, stockShape, bucket, nextBucket,
    // installed}.
    Q_INVOKABLE QVariantMap suggestSceneTemplatesForMedia(const QList<QUrl> &urls) const;
    // The same for replacing a template already filled (its filled slots and the project's shape),
    // without the template itself; adds currentId.
    Q_INVOKABLE QVariantMap suggestSceneTemplatesForSwap(const QString &compositeAssetId) const;
    // Inserts the template and fills its slots with the files in order. Returns the clip id.
    Q_INVOKABLE QString insertSceneTemplateWithMedia(const QString &templateId, const QList<QUrl> &urls);
    // A Stock template: downloads it if needed, then inserts it with these files, or swaps it for
    // the template swapAssetId when that is set.
    Q_INVOKABLE void useStockSceneTemplate(const QString &itemId, const QString &title, const QList<QUrl> &urls,
                                           const QString &swapAssetId = QString());
    // Change template: puts templateId where the composition's instance is, refills its slots in
    // order with the same pictures and the texts the user changed (by what they are for, then by
    // position), and drops the old one. One undo step. Returns the new clip id.
    Q_INVOKABLE QString swapSceneTemplate(const QString &compositeAssetId, const QString &templateId);
    // The text form: {clipId: text} applied as one undo step. Returns how many changed.
    Q_INVOKABLE int setTemplateTexts(const QVariantMap &textsByClipId);
    // Moves the cuts between the template's photo slots to the beats of its music (or of what plays
    // under it), with a steady 120 BPM when there is no beat. Asynchronous; one undo step.
    Q_INVOKABLE void fitTemplateCutsToBeat(const QString &compositeAssetId);
    bool templateBeatFitRunning() const { return m_templateBeatFitRunning; }
    // Replaces the template's music with the file (cut to the template's length), then fits the
    // cuts to its beat when fitCuts.
    Q_INVOKABLE void replaceTemplateMusic(const QString &compositeAssetId, const QUrl &url, bool fitCuts);
    // My brand: {logo (url), logoPath, colors ["#rrggbb"], font, autoApply, empty}, in QSettings
    // (the logo is copied to AppData/brand). Business templates and those with a logo slot or
    // brand roles take it when inserted (autoApply), any template from the Template panel.
    Q_INVOKABLE QVariantMap brandKit() const;
    Q_INVOKABLE bool setBrandKit(const QVariantMap &values);
    Q_INVOKABLE bool applyBrandKitToTemplate(const QString &compositeAssetId);
    // The window owns these dialogs (a panel that asks may be unloaded by the edit it starts):
    // mode "photos" with the chosen files, or "swap" with the composition to replace.
    Q_INVOKABLE void requestTemplatePicker(const QString &mode, const QString &compositeAssetId,
                                           const QList<QUrl> &urls)
    {
        emit templatePickerRequested(mode, compositeAssetId, urls);
    }
    Q_INVOKABLE void requestBrandKitDialog() { emit brandKitDialogRequested(); }
    Q_INVOKABLE void removeEffect(int trackIndex, int clipIndex, int effectIndex);
    Q_INVOKABLE void setEffectEnabled(int trackIndex, int clipIndex, int effectIndex, bool enabled);
    Q_INVOKABLE void moveEffect(int trackIndex, int clipIndex, int fromIndex, int toIndex);
    Q_INVOKABLE bool setEffectParam(int trackIndex, int clipIndex, int effectIndex, const QString &key,
                                    double value);
    Q_INVOKABLE bool setEffectVec2Param(int trackIndex, int clipIndex, int effectIndex,
                                        const QString &key, double x, double y);
    Q_INVOKABLE bool setEffectColorParam(int trackIndex, int clipIndex, int effectIndex,
                                         const QString &key, const QString &value);
    // File-path params (model3d .glb). Same commit-once path as colour — no preview stream.
    // Takes a QUrl like bin().replaceSource / importSubtitleFile so the portal and native
    // dialogs hand us a real local path without QML having to call toLocalFile().
    Q_INVOKABLE bool setEffectStringParam(int trackIndex, int clipIndex, int effectIndex,
                                          const QString &key, const QUrl &url);
    // Clip params ("clip" type, e.g. the clip Behind Subject sits in). Empty clears the choice
    // back to automatic.
    Q_INVOKABLE bool setEffectClipParam(int trackIndex, int clipIndex, int effectIndex,
                                        const QString &key, const QString &clipId);
    // What a clip param can point at: every video or image clip on a visible track beneath the
    // clip that overlaps it in time, nearest track first. [{id, name, track, clip, hasDepth}]
    Q_INVOKABLE QVariantList effectClipCandidates(int trackIndex, int clipIndex) const;
    // The clip a clip param resolves to right now — the chosen one, or with none chosen the
    // nearest video or image clip beneath at the playhead, which is what the renderer uses.
    // {explicit, id, name, track, clip, hasDepth}; empty when there is none.
    Q_INVOKABLE QVariantMap effectClipTarget(int trackIndex, int clipIndex, int effectIndex,
                                             const QString &key) const;
    // The Face Props effect's picker. [{id, name, thumbnailPath, description, license, modelPath,
    // removable}]; removable is true for props the user imported.
    Q_INVOKABLE QVariantList facePropLibrary() const;
    // A .zip or a folder holding one or many props (each a folder with a prop.json). Reports in the
    // toast; returns {installed: [ids], errors: [messages]}.
    Q_INVOKABLE QVariantMap importFaceProps(const QUrl &url);
    Q_INVOKABLE bool removeFaceProp(const QString &propId);
    // Points a face_props effect at the prop and resets its placement to the prop's fitted values,
    // as one undo step. Lighting and the face index are the user's and stay as they are.
    Q_INVOKABLE bool applyFaceProp(int trackIndex, int clipIndex, int effectIndex,
                                   const QString &propId);
    // Adds a Face Props effect to the clip and applies the prop to it, as one undo step.
    Q_INVOKABLE bool addFaceProp(int trackIndex, int clipIndex, const QString &propId);
    Q_INVOKABLE QVariantList audioEffectCatalog() const;
    Q_INVOKABLE QVariantList audioEffectCategories() const;
    Q_INVOKABLE void addAudioEffect(int trackIndex, int clipIndex, const QString &effectId);
    // CapCut's "Enhance voice": noise gate, de-esser, compressor and leveler, as one edit.
    Q_INVOKABLE void enhanceVoice(int trackIndex, int clipIndex);
    // Sound effects from the "sound-effects" extras: [{id, label, category, path, url, duration}],
    // their categories [{id, label}], and adding one at the playhead (it joins the media bin).
    Q_INVOKABLE QVariantList soundEffects() const;
    Q_INVOKABLE QVariantList soundEffectCategories() const;
    Q_INVOKABLE void addSoundEffect(const QString &id);
    // A file Stock just put in Media (music, a sound, a sticker, an overlay…) onto the timeline at
    // the playhead, once its length is known (a first import still holds a 5 s placeholder).
    Q_INVOKABLE void addAssetClipWhenReady(const QString &assetId);
    // CapCut's "remove silences / filler words": keeps only the spoken parts of a clip, dropping
    // pauses longer than `minPause` seconds and hesitations (eh, mmm), from a word-level
    // transcript of its media (made first when there is none). One undo step.
    // Returns an error message when nothing could start, empty otherwise.
    Q_INVOKABLE QString cutSilencesAndFillers(int trackIndex, int clipIndex, double minPause = 0.6,
                                           bool removeFillers = true);
    Q_INVOKABLE void removeAudioEffect(int trackIndex, int clipIndex, int effectIndex);
    // Voice changer: the "voz.*" filter on a clip ("" for none), and replacing it in one undo
    // step on this clip or, with allClips, on every clip with sound.
    Q_INVOKABLE QString voiceFilterOf(int trackIndex, int clipIndex) const;
    Q_INVOKABLE void setVoiceFilter(int trackIndex, int clipIndex, const QString &effectId, bool allClips);
    Q_INVOKABLE double voiceFilterIntensity(int trackIndex, int clipIndex) const;
    Q_INVOKABLE void setVoiceFilterIntensity(int trackIndex, int clipIndex, double value);
    // The Audio tab's basics: fades on the sound only, "fill channel" (0 left, 1 right, 2 auto,
    // -1 off) and loudness normalisation to a target (ITU-R BS.1770), measured off the GUI thread.
    Q_INVOKABLE void setClipAudioFade(int trackIndex, int clipIndex, double fadeInSeconds, double fadeOutSeconds);
    Q_INVOKABLE int channelFillOf(int trackIndex, int clipIndex) const;
    Q_INVOKABLE void setChannelFill(int trackIndex, int clipIndex, int mode);
    Q_INVOKABLE void normalizeClipLoudness(int trackIndex, int clipIndex, double targetLufs);
    bool normalizing() const { return m_normalizing; }
    Q_INVOKABLE void setAudioEffectEnabled(int trackIndex, int clipIndex, int effectIndex, bool enabled);
    Q_INVOKABLE void moveAudioEffect(int trackIndex, int clipIndex, int fromIndex, int toIndex);
    Q_INVOKABLE bool setAudioEffectParam(int trackIndex, int clipIndex, int effectIndex,
                                         const QString &key, double value);
    Q_INVOKABLE void previewSetAudioEffectParam(int trackIndex, int clipIndex, int effectIndex,
                                                const QString &key, double value);

    // Effect stacks travel as JSON on the system clipboard, so a copy also crosses to a second
    // running instance. -1 for both indices means the whole clip.
    Q_INVOKABLE void copyEffectToClipboard(int trackIndex, int clipIndex, int effectIndex);
    Q_INVOKABLE void copyAudioEffectToClipboard(int trackIndex, int clipIndex, int effectIndex);
    Q_INVOKABLE void copyClipEffectsToClipboard(int trackIndex, int clipIndex);
    // Reading the clipboard is a synchronous round-trip to whichever process owns the selection,
    // so callers ask this when a menu opens rather than binding it.
    Q_INVOKABLE bool clipboardHasEffects() const;
    Q_INVOKABLE void pasteEffectsFromClipboard(int trackIndex, int clipIndex);

    Q_INVOKABLE bool canPasteAttributes() const;
    Q_INVOKABLE QVariantMap clipboardAttributes() const;
    Q_INVOKABLE void requestPasteAttributes();
    Q_INVOKABLE void pasteAttributes(const QVariantMap &options);

    Q_INVOKABLE QVariantList userEffectPresets() const;
    Q_INVOKABLE QString saveEffectAsPreset(int trackIndex, int clipIndex, int effectIndex,
                                           const QString &label);
    Q_INVOKABLE QString saveAudioEffectAsPreset(int trackIndex, int clipIndex, int effectIndex,
                                                const QString &label);
    Q_INVOKABLE QString saveClipEffectsAsPreset(int trackIndex, int clipIndex,
                                                const QString &label);
    Q_INVOKABLE void applyEffectPreset(int trackIndex, int clipIndex, const QString &presetId);
    Q_INVOKABLE bool renameUserEffectPreset(const QString &presetId, const QString &label);
    Q_INVOKABLE bool deleteUserEffectPreset(const QString &presetId);
    // My Effects: how many effects in the project use the imported package `effectId`, and
    // deleting the package from disk. Packages from Drift itself or an add-on are refused.
    Q_INVOKABLE int userEffectUses(const QString &effectId) const;
    Q_INVOKABLE bool deleteUserEffect(const QString &effectId);
    Q_INVOKABLE bool exportUserEffectPreset(const QString &presetId, const QUrl &fileUrl);
    Q_INVOKABLE bool importUserEffectPreset(const QUrl &fileUrl);
    Q_INVOKABLE void setTrackMuted(int trackIndex, bool muted);
    Q_INVOKABLE void setTrackHidden(int trackIndex, bool hidden);
    // The padlock in a track's header (CapCut): its clips, and those of its lanes, cannot be
    // selected, moved, trimmed, split or dropped on until it is unlocked.
    Q_INVOKABLE void setTrackLocked(int trackIndex, bool locked);
    // Sony Vegas' automatic crossfade: a clip moved so that one edge runs over its neighbour on
    // the same track keeps the overlap as a dissolve. On by default; a toggle in the timeline.
    Q_PROPERTY(bool autoCrossfade READ autoCrossfade WRITE setAutoCrossfade NOTIFY autoCrossfadeChanged)
    bool autoCrossfade() const { return m_autoCrossfade; }
    void setAutoCrossfade(bool on);
    Q_SIGNAL void autoCrossfadeChanged();
    // CapCut's select-left / select-right tools: the clip and every clip that starts at or after
    // it (forward), or ends at or before it, on every unlocked track.
    Q_INVOKABLE void selectClipsFrom(int trackIndex, int clipIndex, bool forward);
    Q_INVOKABLE bool isTrackLocked(int trackIndex) const;
    Q_INVOKABLE void setTrackSolo(int trackIndex, bool solo);
    Q_INVOKABLE bool trackSolo(int trackIndex) const;
    Q_INVOKABLE void setTrackVolume(int trackIndex, double volume);
    Q_INVOKABLE void previewTrackVolume(int trackIndex, double volume);
    Q_INVOKABLE double trackVolume(int trackIndex) const;
    Q_INVOKABLE void setTrackPan(int trackIndex, double pan);
    Q_INVOKABLE void previewTrackPan(int trackIndex, double pan);
    Q_INVOKABLE double trackPan(int trackIndex) const;
    Q_INVOKABLE QVariantMap trackAudioLevels(int trackIndex) const;
    Q_INVOKABLE QVariantMap masterAudioLevels() const;
    // [masterL, masterR, track0L, track0R, ...] in one call, peaks since the previous call.
    // The mixer meters poll this rather than one QVariantMap per strip per tick.
    Q_INVOKABLE QList<float> meterLevels(const QList<int> &trackIndexes) const;
    // Empty name clears the custom label, falling back to the type+position display
    // ("Video 1") again.
    Q_INVOKABLE bool renameTrack(int trackIndex, const QString &name);
    Q_INVOKABLE bool trackMuted(int trackIndex) const;
    Q_INVOKABLE bool trackHidden(int trackIndex) const;
    // 0 = filmstrip only, 1 = filmstrip + waveform bar, 2 = waveform only (Track::ClipDisplay).
    Q_INVOKABLE void setTrackClipDisplay(int trackIndex, int mode);
    Q_INVOKABLE int trackClipDisplay(int trackIndex) const;
    Q_INVOKABLE void setTrackShowChannelWaveforms(int trackIndex, bool show);
    Q_INVOKABLE bool trackShowChannelWaveforms(int trackIndex) const;
    // Per-track row height multiplier (DAW-style lane resize). Clamped to
    // trackHeightScaleMin()..trackHeightScaleMax().
    Q_INVOKABLE void setTrackHeightScale(int trackIndex, double scale);
    // The After-Effects-style twirl on a track header: unfolds one line per animated property
    // of the track's clips under it. View-only, saved with the project.
    Q_INVOKABLE void setTrackKeyframesExpanded(int trackIndex, bool expanded);
    Q_INVOKABLE bool trackHasKeyframes(int trackIndex) const;
    // [{label, prop, clips: [{clip, prop, start, duration, keys: clipKeyframes()}]}], one per
    // property name across the track's clips.
    Q_INVOKABLE QVariantList trackKeyframeRows(int trackIndex) const;
    // "X position", "Zoom punch · Punch"… for a keyframed property of a clip.
    Q_INVOKABLE QString animatedPropertyLabel(int trackIndex, int clipIndex, const QString &prop) const;
    // How tall the waveform is drawn inside the row (0.1-1.0). View-only.
    Q_INVOKABLE void setTrackWaveformScale(int trackIndex, double scale);
    Q_INVOKABLE double trackHeightScale(int trackIndex) const;
    Q_INVOKABLE void nudgeTrackHeightScale(int trackIndex, int steps);
    // The touch timeline has no per-lane resize handle and no room in the tool strip for a control
    // per lane, so its buttons move the whole stack. One tracksChanged for the sweep rather than
    // one per track — each emission relays the entire track list into QML.
    Q_INVOKABLE void nudgeAllTrackHeightScales(int steps);
    bool canGrowTrackHeights() const;
    bool canShrinkTrackHeights() const;
    // The row height the timeline should give a track, in pixels, including any nested
    // adjustment lanes drawn inside it. A lane returns 0: it has no row of its own, it is drawn
    // as a strip across the top of its parent's.
    //
    // This lives here rather than in QML because the rule stopped being a one-liner and was
    // duplicated verbatim in TimelinePanel, TrackHeaderColumn and AndroidTimeline — three copies
    // that had to agree or the headers would drift out of line with the rows.
    //
    // `metrics` carries Theme's row heights, so the numbers stay defined in one place there:
    // keys "video", "audio", "text", "subtitle", "shape", "adjustment" and "lane". Named rather
    // than positional because seven interchangeable doubles are silently mis-orderable.
    Q_INVOKABLE int trackRowHeight(int trackIndex, const QVariantMap &metrics) const;

    // How many nested lanes a track is carrying, so the delegate knows how many strips to draw.
    Q_INVOKABLE int adjustmentLaneCount(int trackIndex) const;
    // Track indices of those lanes, topmost first.
    Q_INVOKABLE QVariantList adjustmentLanes(int trackIndex) const;

    Q_INVOKABLE double trackHeightScaleMin() const { return 0.6; }
    Q_INVOKABLE double trackHeightScaleMax() const { return 4.0; }
    Q_INVOKABLE void moveTrack(int fromIndex, int toIndex);
    Q_INVOKABLE void addTrack(const QString &type);
    Q_INVOKABLE void removeTrack(int trackIndex);
    // A click on a track header: picks that track alone; `extendRange` (Shift) adds every track
    // from the last one clicked, `toggle` (Ctrl) adds or takes off just this one. Clears the
    // clip selection, and picking a clip clears it in turn.
    Q_INVOKABLE void selectTrackHeader(int trackIndex, bool extendRange, bool toggle);
    Q_INVOKABLE void clearTrackSelection();
    Q_INVOKABLE bool isTrackSelected(int trackIndex) const;
    // How many clips the picked tracks hold (lanes included), for the confirmation.
    Q_INVOKABLE int selectedTracksClipCount() const;
    // Deletes the picked tracks with every clip on them and their lanes, in one undo step.
    Q_INVOKABLE bool removeSelectedTracks();
    // Groups everything on the picked tracks into one composition, as Group does for clips.
    Q_INVOKABLE bool groupSelectedTracks();
    Q_INVOKABLE void addBookmark(double seconds, const QString &label);
    Q_INVOKABLE void removeBookmark(int index);
    Q_INVOKABLE void updateBookmark(int index, double seconds, const QString &label);
    Q_INVOKABLE void goToBookmark(int index);
    // Seek to the next/previous bookmark by time (wraps). No-op when empty.
    Q_INVOKABLE void goToNextBookmark();
    Q_INVOKABLE void goToPreviousBookmark();
    // Seek to the next/previous cut point — any clip edge on any track, plus the two ends
    // of the timeline. Unlike the bookmark pair these clamp rather than wrap, so holding the
    // key walks to the first or last cut and stops there.
    Q_INVOKABLE void goToNextEdit();
    Q_INVOKABLE void goToPreviousEdit();
    // Add at the playhead, or remove the nearest bookmark when one already sits
    // within the snap threshold — same key for mark and unmark.
    Q_INVOKABLE void toggleBookmarkAtPlayhead();
    Q_INVOKABLE void removeBookmarkNearPlayhead();
    Q_INVOKABLE void markWorkAreaIn();
    Q_INVOKABLE void markWorkAreaOut();
    Q_INVOKABLE void goToWorkAreaIn();
    Q_INVOKABLE void goToWorkAreaOut();
    Q_INVOKABLE void clearWorkArea();
    Q_INVOKABLE void toggleLoopWorkArea();
    Q_INVOKABLE void freezeFrameAtPlayhead();
    // AI transition (RIFE) from this clip into the one right after it; see AiTransition notes in the .cpp.
    Q_INVOKABLE bool aiTransitionAvailable() const;
    Q_INVOKABLE void addAiTransitionAfter(int trackIndex, int clipIndex);
    // Smooth slow motion (0.18): a slowed video clip played back from in-between frames the AI
    // transition's model (RIFE) draws, instead of each source frame held twice or more.
    Q_INVOKABLE bool canSmoothSlowMotion(int trackIndex, int clipIndex) const;
    Q_INVOKABLE void smoothSlowMotion(int trackIndex, int clipIndex);
    // AI text: picks the closest text style to `idea` (TextEmbedder) and adds `text` with it.
    Q_INVOKABLE bool aiTextAvailable() const;
    Q_INVOKABLE void addAiText(const QString &text, const QString &idea);
    Q_INVOKABLE void copySelection();
    Q_INVOKABLE void cutSelection();
    Q_INVOKABLE void pasteAtPlayhead();
    Q_INVOKABLE void nudgeSelection(double deltaSeconds);
    Q_INVOKABLE bool selectionContains(int trackIndex, int clipIndex) const;
    Q_INVOKABLE double selectionEarliestStartSeconds() const;
    // Premiere-style trim pointer. side: -1=start, 0=off, 1=end.
    // heightPx scales the cursor to the hovered clip/track height.
    // The trim pointer is an application-wide override cursor, but every clip delegate has an
    // opinion about it. `owner` says who is asking: a clear from anyone but the current owner is
    // ignored, so a neighbouring clip's hover ending cannot drop the cursor of the clip actually
    // being trimmed.
    Q_INVOKABLE void setTimelineTrimCursor(int side, int heightPx = 0, int owner = 0);
    Q_INVOKABLE int acquireTrimCursorToken() { return ++m_trimCursorTokenSeq; }
    Q_INVOKABLE QString shortcutFor(const QString &actionId) const;
    // Returns an empty string on success, or the label of the action already bound to
    // `keys` when the binding is refused. Qt resolves an ambiguous application
    // shortcut by firing *neither* action, so a silent double-binding would break
    // both with no indication anywhere.
    Q_INVOKABLE QString setShortcut(const QString &actionId, const QString &keys);
    // Restores every default binding. Backspace clears a binding and persists the
    // empty string, so without this there was no route back from having cleared one.
    Q_INVOKABLE void resetShortcuts();
    // Canonical chord string for a key event (Ctrl+Shift+Left, …). Same names the
    // Shortcut items and the shortcut-capture field use, so a rebound chord still
    // matches when it is dispatched from Keys.onPressed rather than Shortcut {}.
    Q_INVOKABLE QString shortcutChord(int key, int modifiers) const;
    // The action bound to this arrow-key chord, or an empty string when the key is
    // not an arrow or nothing claims it. ApplicationShortcut matching for Left/Right
    // is unreliable on some Wayland compositors (Hyprland / Omarchy), and would also
    // steal the keys from text fields, so the editor resolves those chords itself
    // after the focused item. Main.qml dispatches the result through the same
    // function the Shortcut items use — a few ids are QML state with no
    // triggerAction branch, and calling triggerAction directly would do nothing.
    Q_INVOKABLE QString actionForArrowChord(int key, int modifiers) const;
    Q_INVOKABLE void triggerAction(const QString &actionId);
    // Per-tab favorites in the assets panel (effects, sounds, shapes, stickers, transitions, templates).
    Q_INVOKABLE bool isAssetFavorite(const QString &tabId, const QString &itemId) const;
    // How many favourites each group holds ({"music": 3, "effects": 1, …}), empty groups left out.
    Q_INVOKABLE QVariantMap assetFavoriteCounts() const;
    // The item ids starred in one group, sorted (font family names for "fonts").
    Q_INVOKABLE QStringList assetFavoriteIds(const QString &tabId) const;
    Q_INVOKABLE void toggleAssetFavorite(const QString &tabId, const QString &itemId);
    Q_INVOKABLE void togglePlayback();
    // Bracket a scrub gesture (a dragged playhead, or the phone timeline being scrolled under
    // its fixed playhead). In between, the preview shows approximate frames and inspectors
    // follow the playhead at a reduced rate; the exact frame is drawn at the end.
    Q_INVOKABLE void beginScrub();
    Q_INVOKABLE void endScrub();
    bool scrubbing() const { return m_scrubbing; }
    // Frame-accurate transport. Stepping quantizes to the project's frame grid first: the playhead
    // can sit between frames after a scrub, and adding a frame duration to that would carry the
    // off-grid offset forever.
    Q_INVOKABLE void stepFrames(int frames);
    Q_INVOKABLE void jumpSeconds(double seconds);
    // The transport's jump buttons pick their amount from the modifiers held at click time, and
    // AbstractButton::clicked carries none.
    Q_INVOKABLE int keyboardModifiers() const;
    Q_INVOKABLE void undo();
    Q_INVOKABLE void redo();
    // `excludeClipId` keeps a clip from snapping to its own edges while it is being dragged —
    // the model still has it at its old position, so those two targets sit right under the
    // pointer at the start of every move.
    Q_INVOKABLE double snapTime(double seconds, const QString &excludeClipId = {}) const;
    // Snapping pulls within a fixed on-screen distance, so the timeline reports its zoom here.
    Q_INVOKABLE void setSnapRadius(double pixels, double pxPerSecond);
    Q_INVOKABLE QVariantList waveformPeaks(const QString &path) const;
    // Whole-file peaks sliced to a source window, for a dialog whose x axis is a clip's trimmed
    // range rather than the whole file. Shares the dense cache and the waveformReady signal with
    // waveformPeaks() — unlike waveformPeaksRange(), which is block-backed for the timeline.
    Q_INVOKABLE QVariantList waveformPeaksForSourceRange(const QString &path, double startSeconds,
                                                         double durSeconds) const;
    // Peaks for just the source window [startSeconds, startSeconds + durSeconds), reduced to
    // `buckets` values, so a clip only ever asks for as many peaks as it has visible pixels.
    Q_INVOKABLE QVariantList waveformPeaksRange(const QString &path, double startSeconds,
                                                double durSeconds, int buckets,
                                                int audioStreamIndex = 0) const;
    // Every channel of the stream over the same window, for stacked per-channel lanes.
    // Channel-major and flat — peaks[c * buckets + b] — so one array crosses into QML rather
    // than one per channel, and the paint loop indexes it without unpacking.
    // { "channels": int, "buckets": int, "names": QStringList, "peaks": QVariantList }.
    // channels == 0 means nothing has decoded for this stream yet, not mono: until a block
    // lands the caller keeps drawing the merged lane.
    Q_INVOKABLE QVariantMap waveformChannelPeaksRange(const QString &path, double startSeconds,
                                                      double durSeconds, int buckets,
                                                      int audioStreamIndex = 0) const;
    // Channels the decoder found for a source, 0 until a block has landed. Answered from the
    // block cache — never probes the file, so it is safe from a binding or a menu.
    Q_INVOKABLE int waveformChannelCount(const QString &path, int audioStreamIndex = 0) const;
    // Widest channel count over a track's clips, for sizing the row when the lanes turn on.
    Q_INVOKABLE int trackMaxChannelCount(int trackIndex) const;
    Q_INVOKABLE QVariantList subtitleWaveformPeaks(double startSeconds, double durSeconds,
                                                   int sampleCount = 240) const;
    // Beat / onset detection over the mixed timeline audio in [startSeconds, +durSeconds).
    // Explicitly triggered from the keyframe strip: it renders the mix, so it must never
    // fire off a mere selection change. Result lands in `beatAnalysis`.
    Q_INVOKABLE void analyzeBeats(double startSeconds, double durSeconds);
    Q_INVOKABLE void clearBeatAnalysis();
    QVariantMap beatAnalysis() const { return m_beatAnalysis; }
    bool beatAnalysisRunning() const { return m_beatAnalysisRunning; }
    bool beatGridVisible() const { return m_beatGridVisible; }
    void setBeatGridVisible(bool visible);
    bool onsetsVisible() const { return m_onsetsVisible; }
    void setOnsetsVisible(bool visible);
    // Drops every cache that exists only to make the next composite faster — decoder workers,
    // still images, rasterised text, uploaded textures and the FBO pool. All of it is rebuilt on
    // demand, and a backgrounded app that hangs on to it is the one the OS picks to kill first.
    // Only for the leaving-foreground handler: calling it while active throws away exactly what
    // the current composite is about to reuse.
    Q_INVOKABLE void releaseTransientCaches();
    Q_INVOKABLE QVariantList exportPresets() const; // legacy scale ids/labels
    Q_INVOKABLE QVariantList exportScaleOptions() const;
    // Frame rate choices; the "project" entry is labelled with the current project fps.
    Q_INVOKABLE QVariantList exportFrameRateOptions() const;
    Q_INVOKABLE QVariantList exportVideoCodecs() const;
    Q_INVOKABLE QVariantList exportAudioCodecs() const;
    Q_INVOKABLE bool exportGifAvailable() const;
    Q_INVOKABLE QVariantMap exportDefaultSettings() const;
    // Last dialog choices (scale + encode). Empty until the user has exported once.
    Q_INVOKABLE QVariantMap lastExportSettings() const;
    // Directory of the last successful save-picker choice; empty if never set or gone.
    Q_INVOKABLE QString lastExportFolder() const;
    Q_INVOKABLE QString exportPreferredContainer(const QString &videoCodecId,
                                                const QString &audioCodecId) const;
    Q_INVOKABLE QString exportPreferredAudioOnlyContainer(const QString &audioCodecId) const;
    Q_INVOKABLE QStringList exportSaveFilters(const QString &container, bool audioOnly = false) const;
    Q_INVOKABLE QString exportDefaultSuffix(const QString &container, bool audioOnly = false) const;
    Q_INVOKABLE void exportProject(const QUrl &outputUrl);
    Q_INVOKABLE void exportWithPreset(const QUrl &outputUrl, const QString &presetId);
    // `rememberChoice` is what keeps an agent export out of the export dialog's memory: the GUI
    // stores what the user picked, an MCP export keeps its own (see McpController::rememberExportSettings), and
    // neither reaches into the other's.
    Q_INVOKABLE void exportWithSettings(const QUrl &outputUrl, const QVariantMap &settings,
                                        bool rememberChoice = true);
    Q_INVOKABLE void cancelExport();
    // Copies the finished export into the shared media collection and hands it to the system share
    // sheet. Deferred to this point rather than done as part of the export because it is a second
    // full copy of the video, and most exports are never shared. Android only; false/no-op elsewhere.
    Q_INVOKABLE void shareLastExport();
    // Same publish-to-gallery step as shareLastExport, handed to a player instead of a share
    // sheet. Shares the m_sharingExport guard, so the two cannot run the copy twice at once.
    Q_INVOKABLE void playLastExport();
    // Copies a file into the shared media collection (Movies/Music/Pictures under "Drift") so it
    // outlives the app's own storage. Marketplace downloads land in AppDataLocation, which is gone
    // on uninstall or a "clear data" and invisible to every file manager — for something the user
    // spent quota on, that is a file they can lose without ever having seen it.
    //
    // Asynchronous: this is a second full copy of the media, and doing it inline is an ANR on
    // anything long. Reports through savedToGallery. Android only; a no-op elsewhere, where the
    // download already went somewhere the user picked.
    Q_INVOKABLE void saveToGallery(const QString &filePath, const QString &displayName);
    Q_INVOKABLE QUrl fileUrl(const QString &path) const;
    Q_INVOKABLE QString imageUrl(const QString &path) const;
    // Same as imageUrl but requests a single frame of a filmstrip strip (see DriftImageProvider).
    Q_INVOKABLE QString filmstripFrameUrl(const QString &path, int frame, int count) const;
    // Sharp on-demand frame for one filmstrip tile — see FilmstripTileCache. Empty until the
    // decode lands, at which point filmstripTileReady() fires for that source.
    Q_INVOKABLE QString filmstripTileUrl(const QString &path, int level, double index,
                                         int rotationCorrection = 0) const;

signals:
    void userTextAnimationPresetsChanged();

    // A text clip was added with no text; the preview should open its inline
    // editor so the user can type straight onto the canvas.
    void inlineTextEditRequested(int trackIndex, int clipIndex);
    void inlineTextEditingChanged();
    // The inline editor's text was laid out again: caret and selection geometry moved.
    void inlineEditGeometryChanged();
    void externalProjectOpenRequested(const QUrl &url);
    void tracksChanged();
    // A drag wrote these properties in place without announcing tracksChanged; the full refresh
    // follows on commit. Keys are the propertyValueAt names ("x", "fx.2.light1_x"); one ending
    // in ".*" covers every key under that prefix.
    void clipPropertiesPreviewed(int trackIndex, int clipIndex, const QStringList &keys);
    void previewDragActiveChanged();
    void playheadSecondsChanged();
    void inspectorPlayheadChanged();
    void playingChanged();
    void scrubbingChanged();
    void audioOutputDevicesChanged();
    void audioOutputDeviceIdChanged();
    void audioRecordingStateChanged();
    void audioRecordingPausedChanged();
    void audioRecordGainChanged();
    void audioRecordLevelChanged();
    void audioRecordSecondsChanged();
    void audioRecordLivePeaksChanged();
    void availableMicrophonesChanged();
    void currentMicrophoneChanged();
    void snapEnabledChanged();
    void rippleEnabledChanged();
    void allowClipOverlapChanged();
    void mediaGridModeChanged();
    void mediaViewModeChanged();
    void autoKeyEnabledChanged();
    void positionLinkedChanged();
    void sizeLinkedChanged();
    void masterVolumeChanged();
    void masterMutedChanged();
    // Carries the finished benchmark, merged into whatever the dialog already collected.
    void playbackBenchmarkFinished(const QVariantMap &info);
    void playbackBenchmarkRunningChanged();
    void keyframeGraphVisibilityChanged();
    void subtitleEditingChanged();
    void selectedSubtitleCueChanged();
    void undoStackChanged();
    void exportInProgressChanged();
    void exportProgressChanged();
    void canShareExportChanged();
    // `location` is a human-readable folder ("Movies/Drift"), empty when ok is false.
    void savedToGallery(const QString &displayName, bool ok, const QString &location,
                        const QString &error);
    void subtitleGeneratingChanged();
    void subtitleGenProgressChanged();
    void subtitleGenStatusChanged();
    void subtitleGenerationFinished(bool ok, const QString &message);
    void reverseRenderingChanged();
    void reverseRenderProgressChanged();
    void reverseRenderStatusChanged();
    void reverseRenderFinished(bool ok, const QString &message);
    void reverseConfirmRequested(int trackIndex, int clipIndex, double seconds);
    void multicamChanged();
    void multicamFramesChanged();
    // Raised by the "multicam" shortcut/action. QML owns the window, as with the file actions.
    void openMulticamWindowRequested();
    void selectionChanged();
    void editCapabilitiesChanged();
    void sequenceTabsChanged();
    void selectedClipDataChanged();
    // An imported LUT was added to or removed from the library.
    void lutLibraryChanged();
    void userShapesChanged();
    void selectedTransitionDataChanged();
    void selectedTracksChanged();
    // Delete was pressed with tracks picked: the headers ask before deleting them.
    void trackDeletionRequested();
    void bookmarksChanged();
    void workAreaChanged();
    void loopWorkAreaEnabledChanged();
    void lastMessageChanged();
    void draggingAssetIndexChanged();
    void exportFinished(bool success);
    void projectMutated();
    void waveformReady(const QString &path);
    // A block of the timeline waveform landed. Separate from waveformReady so the dialogs,
    // which want the whole file, don't re-fetch (and blank) on every block.
    void waveformRangeReady(const QString &path);
    void filmstripTileReady(const QString &path);
    void subtitleWaveformReady(double startSeconds, double durSeconds, int sampleCount);
    void beatAnalysisChanged();
    void guidesChanged();
    void shortcutsChanged();
    void assetFavoritesChanged();
    void userTextPresetsChanged();
    void normalizingChanged();
    void fontCatalogChanged();
    // Scene templates were installed or removed (Stock, Extras).
    void sceneTemplatesChanged();
    void templateBeatFitChanged();
    void brandKitChanged();
    void templatePickerRequested(const QString &mode, const QString &compositeAssetId, const QList<QUrl> &urls);
    void brandKitDialogRequested();
    void saveTemplateRequested(const QString &compositeAssetId, const QString &name);
    void userFontsChanged();
    void userEffectPresetsChanged();
    void facePropsChanged();
    void projectLayoutChosenChanged();
    // The document has been swapped wholesale (New Project, or opening another one). The
    // auxiliary windows edit one clip each, so they have nothing left to act on and close.
    void projectReset();
    void transformBlocked(const QString &reason);
    void openPasteAttributesRequested();

protected:
    // Every path that changes the timeline model goes through this instead of a bare
    // `emit tracksChanged()`. The cache has to be dropped *before* the signal goes out: whether
    // a slot connected in the constructor runs ahead of QML's binding re-evaluation is not a
    // guarantee worth depending on, and getting it wrong would serve QML one stale rebuild per
    // emission — intermittent, and indistinguishable from a model bug.
    // The trim math, factored out so the live preview and the commit cannot drift apart: both
    // call this, one discards the result and one writes it back. `clip` is the clip as it would
    // be after the trim; `changed` is false when the edge had nowhere to go.
    struct TrimComputation {
        bool ok = false;
        bool changed = false;
        int outcome = 0;
        drift::Clip clip;
        // With ripple on, everything at or after rippleFrom on the clip's tracks moves by
        // rippleDelta when the trim is applied.
        drift::TimeUs rippleFrom = 0;
        drift::TimeUs rippleDelta = 0;
    };
    TrimComputation computeTrimLeft(int trackIndex, int clipIndex, double newStart, bool snap = true) const;
    TrimComputation computeTrimRight(int trackIndex, int clipIndex, double newEnd, bool snap = true) const;
    int applyTrim(int trackIndex, int clipIndex, const TrimComputation &computed, int side);
    QVariantMap trimPreviewToMap(int trackIndex, int clipIndex, const TrimComputation &computed) const;

    void notifyTracksChanged();

    // Refills the per-track clip models from the project. Called by notifyTracksChanged() before
    // the signal goes out, so a binding that wakes on tracksChanged already sees the new rows.
    void syncClipModels();
    TimelineClipsModel::Decorations trackDecorations(const drift::Track &track,
                                                     const QList<int> &laneIndexes) const;
    TimelineClipsModel::Row clipRow(const drift::Clip &clip, const drift::Clip *videoEffectHost,
                                    const drift::Clip *audioEffectHost) const;
    // Holds tracksChanged for the length of an operation that touches the project several times.
    // The caches are still dropped immediately, so anything reading tracks() inside the batch
    // sees fresh data -- only the notification waits, and only one goes out.
    void beginTracksBatch() { ++m_tracksBatchDepth; }
    void endTracksBatch();
    int m_tracksBatchDepth = 0;
    bool m_tracksBatchPending = false;
    // Same rule as notifyTracksChanged(): bump the revision before the signal goes out, so no
    // reader can observe the old value on the new selection.
    void notifySelectionChanged();
    // Stabilization progress/state (stabilizing, stabilizeProgress, stabilizeStatus) changes
    // outside the undo-tracked edit path — see its call sites — so it never reaches
    // notifyTracksChanged(). Use this instead of a bare emit selectedClipDataChanged() wherever
    // that state changes. No-ops unless clipId is the clip currently selected: the signal only
    // describes that one clip, so a background stabilization on some other clip must not
    // re-notify a selection it has nothing to do with.
    void notifyStabilizeStateChanged(const QString &clipId);

    void pushProjectEdit(const drift::Project &before, const QString &text);
    // A catalogue effect with its fixed and default parameters, as addEffect builds it; nullopt for
    // an unknown id. For controllers that assemble a layer themselves (MotionTrackController).
    std::optional<drift::Effect> effectWithDefaults(const QString &effectId) const;

    // Lifts one effect, one audio effect, or the whole stack off a clip. Every copy and
    // save-as-preset entry point funnels through this, so all of them produce one payload shape.
    drift::EffectStackPreset effectStackFor(int trackIndex, int clipIndex, int effectIndex,
                                            int audioEffectIndex) const;
    // Rescales, rebuilds against the catalog, then appends. Shared by paste and preset-apply.
    void applyEffectStack(int trackIndex, int clipIndex, const drift::EffectStackPreset &stack,
                          const QString &undoLabel);
    void copyEffectStack(const drift::EffectStackPreset &stack, const QString &message);
    QString saveEffectStack(const drift::EffectStackPreset &stack, const QString &label);
    static drift::EffectStackPreset effectStackOnClipboard();
    void finishEdit(const QString &message);
    // Keeps the keyframe strip's index-addressed hidden series in sync after an effect is removed.
    void dropKeyframeGraphPropertiesForEffect(int removedIndex, bool audio = false);
    // Same idea after a reorder: fx.N.* indices move with the effect.
    void remapKeyframeGraphPropertiesForEffectMove(int fromIndex, int toIndex, bool audio = false);
    // Publishes a finished beat analysis into m_beatAnalysis / m_beatSnapTargets.
    void applyBeatAnalysis(const AudioBeatAnalysis &analysis, double startSeconds, double durSeconds,
                           const QByteArray &fingerprint);
    // Builds m_shortcuts from the defaults plus whatever QSettings holds, migrating
    // stored values that a new release has superseded and dropping any default that
    // would end up sharing a chord with a stored one.
    void loadShortcuts();
    void loadAssetFavorites();
    void saveAssetFavorites(const QString &tabId);
    // Favorites kept with the account: what the service has, merged with or replacing these.
    void mergeAccountFavorites(const QVariantMap &server, const QDateTime &updatedAt);
    QVariantMap assetFavoritesMap() const;
    void applyEffectTemplateInternal(int trackIndex, int clipIndex, const EffectTemplateEntry &entry,
                                   const QString &mattePath = {},
                                   drift::TimeUs matteSrcOffsetUs = 0);
    bool resolveTemplateApplyTarget(int *trackIndex, int *clipIndex) const;
    bool beatAnalysisCoversClip(const drift::Clip &clip) const;
    bool beatAnalysisReadyForClip(const drift::Clip &clip, const QString &sync) const;
    QList<drift::TimeUs> templateSyncPoints(const drift::Clip &sourceClip, const QString &sync) const;
    // Removes the effects of a single-clip template (all of them when templateId is empty) from
    // the clip and its linked effects adjustment, and its speed curve. No undo step of its own.
    void removeTemplateEffects(int trackIndex, int clipIndex, const QString &templateId,
                               bool dropEmptyLayer = false);
    void refreshTemplateSpans(drift::Project &project) const;
    // Moves the clips in `ids` into a new composite placed where they were, and returns the
    // composite clip's id (empty when nothing could be nested). `prepareInner` may add to the
    // inner tracks first (it gets them shifted to start at 0, plus the original start). No undo
    // step: the caller records one.
    bool fillTemplateSlotWithAsset(const QString &slotClipId, const QString &mediaAssetId, bool recordUndo,
                                   bool contain = false);
    // insertSceneTemplate without its undo step and messages when !recordUndo (Change template
    // records one for the whole swap); allowResize lets an empty project take the template's size.
    QString placeSceneTemplate(const QString &templateId, bool recordUndo, bool allowResize);
    static QString templateTextKindLabel(const QString &kind);
    void applyTemplateBeatFit(const QString &compositeAssetId, const AudioBeatAnalysis &analysis,
                              drift::TimeUs offsetUs);
    bool setTemplateMusicAsset(const QString &compositeAssetId, const QString &musicAssetId);
    drift::BrandKit currentBrandKit() const;
    bool brandKitAutoApply() const;
    static bool templateWantsBrand(const QString &category, const QStringList &tags,
                                   const QList<drift::Track> &tracks);
    // Puts the brand logo in these slots of a timeline (fitted whole). No undo step. Returns how many.
    int fillLogoSlots(const QString &sequenceId, const QStringList &placeholderIds);
    static QStringList missingTemplateFonts(const QList<drift::Track> &tracks);
    QString buildCompositeFromClipIds(
        const QSet<QString> &ids, const QString &name,
        const std::function<void(drift::TrackList &, drift::TimeUs)> &prepareInner);
    // Records on the composition's asset that a template made it: which template, the clips it
    // added inside (everything not in `idsBefore`) and the source clip, so it can be undone later.
    void markTemplateComposite(const QString &compositeClipId, const QString &templateId,
                               const drift::Clip &sourceClip, const QSet<QString> &idsBefore);
    // Ungroup's work without the checks or the undo step: replaces the composite clip with the
    // clips it plays, minus `dropClipIds` (ids inside the sequence). `idMap` gets inner id → new
    // id. Returns the first restored clip's id, empty when nothing was put back.
    QString ungroupCompositeAt(int trackIndex, int clipIndex, const QSet<QString> &dropClipIds,
                            QHash<QString, QString> *idMap);
    bool reshapeEffectTemplate(int trackIndex, int clipIndex, double intensity, double decay,
                               const QString &sync, const QList<drift::TimeUs> *points);
    // Digest of everything the AudioMixer reads; a change means detected beats are stale.
    QByteArray audioLayoutFingerprint() const;
    // Single key lookup for the tangent editors; null when nothing sits at `atSeconds`.
    drift::Keyframe<double> *keyframeAt(int trackIndex, int clipIndex, const QString &prop,
                                        double atSeconds);
    static void applyTangents(drift::Keyframe<double> &key, double inDx, double inDy, double outDx,
                              double outDy, bool corner);
    void syncLinkedTangents(int trackIndex, int clipIndex, const QString &prop, double atSeconds,
                            double inDx, double inDy, double outDx, double outDy, bool corner);
    // setKeyframeEasingAt without its undo step (and setKeyframesEasing's per key). True on a change.
    bool applyKeyframeEasing(int trackIndex, int clipIndex, const QString &prop, double atSeconds,
                             const QString &mode);
    // Every clip's keys as magnets for the playhead (After Effects' snap to keyframes), but the
    // dragged clip's own.
    void appendKeyframeSnapTargets(QList<drift::TimeUs> *targets, const QString &excludeClipId) const;
    // Recollects m_beatSnapTargets from whichever layers are currently visible.
    void rebuildBeatSnapTargets();
    // Beat onsets plus project bookmarks — anything clips should magnet to when snap is on.
    QList<drift::TimeUs> extraSnapTargets() const;
    // Same list, rebuilt only when the beat grid, bookmarks or the work area move. It has no
    // clip dependency, so an edit to the timeline does not invalidate it.
    const QList<drift::TimeUs> &extraSnapTargetsCached() const;
    void invalidateExtraSnapTargets() { m_extraSnapTargetsValid = false; }
    // Snaps against the vector pinned for the current trim gesture, falling back to a one-shot
    // build when called outside one.
    drift::TimeUs snapTimeForGesture(drift::TimeUs rawUs) const;
    // Decodes one frame per angle at the playhead and publishes them to MulticamImageStore.
    // Coalesces: a refresh requested while one is in flight is dropped, not queued.
    void refreshMulticamTiles();
    // Drops in-flight tile decodes. The worker captures `this`, so teardown has to wait
    // for it before AppController members disappear.
    void waitForMulticamRefresh();
    // Playhead rounded to the project's frame grid — a switch must land on a frame boundary,
    // the same rule stepFrames() follows.
    drift::TimeUs multicamSwitchTimeUs() const;
    bool startMulticamPunching(const QList<QPair<int, int>> &videoClips);
    void rebuildMulticamStaged();
    void applyMulticamSlicesToProject(drift::Project &project, bool combined);
    struct SubtitleSource
    {
        QString path;
        drift::TimeUs srcIn = 0;
        drift::TimeUs srcOut = 0;
        drift::TimeUs timelineStart = 0;
        drift::TimeUs timelineDuration = 0;
        double speed = 1.0;
        bool reverse = false;
        QString assetId;
    };
    static SubtitleSource subtitleSourceFromClip(const drift::Clip &clip);
    // Captions straight from stored transcripts, when every source has a current one. Empty
    // when any source would need transcribing.
    std::optional<QList<drift::SubtitleCue>> cuesFromStoredTranscripts(const QList<SubtitleSource> &sources,
                                                                       drift::TimeUs rangeStart,
                                                                       int maxWordsPerCue) const;
    // Silence cuts waiting on a transcription job: job id -> {clip id, min pause, fillers}.
    QHash<QString, QVariantMap> m_pendingSilenceCuts;
    void applySilenceCut(const QString &clipId, double minPause, bool removeFillers);
    bool m_subtitleTranslateNext = false; // the next generation run translates to English
    bool generateSubtitlesForSources(QList<SubtitleSource> sources, const QString &language,
                                     int maxWordsPerCue);
    void finishNormalize(const QString &clipId, double lufs, double targetLufs);
    bool m_normalizing = false;
    void finalizeGeneratedSubtitles(drift::TimeUs timelineStart, drift::TimeUs timelineDuration,
                                    const QList<drift::SubtitleCue> &cues, bool translated = false);
    // Defaulted severity so the existing call sites, which report ordinary status,
    // stay unchanged; pass "error"/"warning" explicitly where a failure is reported.
    Q_INVOKABLE void setLastMessage(const QString &message,
                                    const QString &severity = QStringLiteral("info"));
    drift::TimeUs playheadUs() const { return m_playheadUs; }
    void setPlayheadUs(drift::TimeUs us);

    // Stickers and emoji are both a PNG dropped on an image track at the playhead.
    void addImageOverlayClip(const QString &path, const QString &name, const QString &emoji,
                             double atSeconds, const QString &undoText,
                             int requestedTrack = -1);

    // The inspector's and the MCP tools' view of a clip: every field, including the sub-maps
    // only an open inspector reads. The timeline strip does NOT come through here — it reads
    // clipRow() through TimelineClipsModel, which is what keeps an edit from rebuilding a
    // textStyle map for every clip in the project.
    //
    // `effectHost` supplies the stack to report for a media clip, whose effects now live on the
    // adjustment linked to it. Passing it in rather than looking it up keeps a whole-project
    // rebuild linear — resolving per clip would make it quadratic.
    // `faceSource` runs the other way: face landmarks are baked onto the media clip, but the
    // effects inspector now only ever sees the adjustment, so a linked adjustment reports the
    // clip it is pinned to. Null means "this clip's own", which is right for a media clip and for
    // an unlinked adjustment (which has no source to scan).
    QVariantMap clipToMap(const drift::Clip &clip, const drift::Clip *videoEffectHost = nullptr,
                          const drift::Clip *audioEffectHost = nullptr,
                          const drift::Clip *maskHost = nullptr,
                          const drift::Clip *faceSource = nullptr) const;

    // The media clip behind (trackIndex, clipIndex): a linked adjustment resolves to the clip it
    // is pinned to, anything else to itself. The per-clip bake jobs — face tracking today — are
    // reached through the adjustment that needs them, so they have to find their way back.
    drift::ClipRef sourceClipRef(int trackIndex, int clipIndex) const;

    // The clip whose `effects` / `audioEffects` list holds the stack for (trackIndex, clipIndex).
    // An adjustment hosts its own; a media clip's lives on the adjustment linked to it in one of
    // its track's lanes. `create` mints that lane and adjustment on demand, which is what lets
    // addEffect() keep taking a plain (trackIndex, clipIndex). Returns {-1,-1} when there is no
    // host and none was created. Creating INSERTS A TRACK, so indices captured earlier go stale.
    drift::ClipRef effectHostRef(int trackIndex, int clipIndex, drift::AdjustmentKind kind,
                                 bool create);
    const drift::Clip *effectHostClip(int trackIndex, int clipIndex,
                                      drift::AdjustmentKind kind) const;
    drift::ClipRef createLinkedAdjustment(int trackIndex, int clipIndex, drift::AdjustmentKind kind);
    int ensureAdjustmentLaneFor(int parentTrackIndex, drift::AdjustmentKind kind,
                                drift::TimeUs startUs, drift::TimeUs durationUs);

    // Rewrites (trackIndex, clipIndex) to the clip a property's keyframes actually live on:
    // transform props stay put, "fx.<i>.<param>" follows the effects to the linked adjustment.
    // A no-op when there is no such adjustment, so callers fail exactly as they did before.
    void redirectToKeyframeHost(int *trackIndex, int *clipIndex, const QString &prop) const;

    // In-place form of effectHostRef for the effect invokables, which all take a plain
    // (trackIndex, clipIndex) from QML and MCP. False when the clip has no stack of that kind
    // and none was created, in which case the caller should do nothing — the same outcome an
    // out-of-range effectIndex has always produced.
    bool redirectToEffectHost(int *trackIndex, int *clipIndex, drift::AdjustmentKind kind,
                              bool create);

    // Mirrors every pinned adjustment's span onto the clip it is linked to, and unlinks the ones
    // whose clip is gone. Runs in finishEdit so moves, trims, splits and deletes all keep links
    // true without every call site having to remember.
    void syncLinkedAdjustments(drift::Project &project) const;

    // Write a mask for (trackIndex, clipIndex), whether that names a mask adjustment (the mask is
    // its payload) or a media clip (the mask is pinned to it through a lane). MAY INSERT TRACKS.
    void writeClipMask(int trackIndex, int clipIndex, const drift::Mask &mask);
    // A ready-to-use mask for a maskCatalog() id, Freeform already seeded with the quad its rect
    // implies. An unknown id yields a mask with shape None, which contributes nothing.
    drift::Mask maskFromCatalogId(const QString &shape) const;
    // Re-establishes the two structural invariants the adjustment model rests on: no stack sits
    // on a media clip, and every lane is adjacent to and directly above its parent. Both passes
    // can insert or reorder tracks, so the selection is carried across by id. Idempotent and
    // cheap when nothing is out of place, which is why it can run on every edit.

    void normalizeProjectStructure(const drift::Project *before = nullptr);
    // What the transform layers over `trackIndex` do at the playhead; identity when none.
    drift::TransformParent transformParentFor(int trackIndex) const;
    // Keeps open tabs pointing at sequences that exist, and the active one among them.
    void reconcileSequenceTabs();
    // A composite asset's duration follows its sequence's content.
    void syncCompositeAssetDurations();
    // Drops sequences no composite bin item refers to any more, leaving their tab if open.
    void pruneOrphanSequences();
    bool compositeAssetPlaceable(const QVariantMap &asset) const;
    void finishFlatten(const QString &clipId, const QString &sequenceId, const QString &path,
                       const QString &name, drift::TimeUs srcInUs, drift::TimeUs durationUs);

    // Keeps each lane adjacent to and directly above its parent, and demotes lanes whose parent
    // is no longer able to hold them.
    void normalizeAdjustmentLanes(drift::Project &project) const;
    void clampStoredTransitionDurations(drift::Project &project) const;

    // Selection survives a track-list reshuffle by id rather than index arithmetic: a move now
    // drags a track's lanes with it, so the destination index no longer says where things landed.
    QString trackIdAt(int trackIndex) const;
    QList<QPair<QString, int>> captureSelectionByTrackId() const;
    void restoreSelectionByTrackId(const QList<QPair<QString, int>> &captured);
    int assetIndexForClip(const drift::Clip &clip) const;
    drift::TimeUs clipDurationForAssetIndex(int assetIndex) const;
    // The absolute orientation (0/90/180/270) a video clip's frames come out at: its file's own
    // tag plus its rotationCorrection. setClipOrientationTo stores the correction that lands on
    // `degrees`.
    int clipOrientation(const drift::Clip &clip) const;
    void setClipOrientationTo(drift::Clip &clip, int degrees);
    drift::TimeUs sourceDurationForClip(const drift::Clip &clip) const;
    void startReverseRender(const QString &sourcePath, drift::TimeUs coverInUs,
                            drift::TimeUs coverOutUs);
    // Cached dense peaks for `path`, or nullptr while the off-thread decode is still running
    // (waveformReady is emitted when it lands).
    const MediaWaveform::Dense *densePeaksFor(const QString &path) const;
    struct SegmentReplaceResult
    {
        QStringList ids;
        drift::TimeUs deltaUs = 0;
    };
    // Replaces the clip at (trackIndex, clipIndex) and each linked partner with the segments
    // `build` makes from it, keeping ids, links, transitions and pinned effects attached, then
    // ripples every track in the group. No undo step: the caller snapshots and pushes one.
    bool replaceClipGroupWithSegments(int trackIndex, int clipIndex,
                                      const std::function<QList<drift::Clip>(const drift::Clip &)> &build,
                                      bool ripple, SegmentReplaceResult *out, QString *error);
    void trimClipGroupAt(int trackIndex, int clipIndex, drift::TimeUs atUs, bool dropLeft);
    void applyRippleShift(drift::Track &track, int fromClipIndex, drift::TimeUs delta);
    void restoreFilmstripsAfterLoad();
    void normalizeSelection();
    bool isValidClipIndex(int trackIndex, int clipIndex) const;
    // Adds a video Drift rendered to the bin as one undoable edit; returns its asset id.
    QString addRenderedVideoAsset(const QString &path, const QString &name,
                                  const QString &folderId, const MediaInfo &info,
                                  const QString &undoText);
    // The same without the undo step, for a caller folding it into an edit of its own.
    QString insertRenderedVideoAsset(const QString &path, const QString &name,
                                     const QString &folderId, const MediaInfo &info);
    QList<int> subtitleMergeIndices(const QList<QPair<int, int>> &pairs) const;
    void mergeSubtitleClipsAt(int trackIndex, QList<int> clipIndices);

    // Drops everything scoped to the outgoing project — clipboard, timeline-keyed caches, the
    // auxiliary-window sessions. Called by both newProject and applyProjectJson, before the
    // document is replaced, so the two paths cannot drift apart again.
    void resetSessionState();

    QByteArray serializeProjectJson() const;
    bool applyProjectJson(const QByteArray &data, QString *error);
    // Second half of applyProjectJson, on the GUI thread; parseProjectJson is the first.
    void applyParsedProject(ParsedProject parsed);
    // Persist the save-picker folder and encode/scale choices for the next Export dialog.
    // Empty `outputPath` updates settings only and leaves lastExportFolder unchanged.
    void rememberExportChoice(const QString &outputPath, const QVariantMap &settings);
    QJsonObject sessionJson() const;
    QString historyHashAt(int stackIndex) const;
    int historyIndexForHash(const QString &prefix) const;
    QByteArray historyJsonAt(int stackIndex) const;
    static QString historySnapshotDir();
    static void pruneHistorySnapshots();

    AssetLibrary *m_assetLibrary = nullptr;
    AddonManager *m_addonManager = nullptr;
    MarketClient *m_marketClient = nullptr;
    // A Stock template asked for with photos or to replace another, until it is downloaded.
    QString m_pendingTemplateId;
    QList<QUrl> m_pendingTemplateUrls;
    QString m_pendingTemplateSwap;
    // Mi cuenta › Stock downloads asked to put these in the edit once downloaded: item id -> name.
    QHash<QString, QString> m_pendingStockPlace;
    void placeStockItem(const QString &itemId, const QString &delivery, const QString &name,
                        const QString &installedId, const QString &filePath, const QString &assetId);
    QString installedStockId(const QString &delivery, const QString &itemId, const QVariantMap &local) const;
    QVariantMap stockHistoryEntry(const QString &itemId) const;
    bool m_templateBeatFitRunning = false;
    quint64 m_templateBeatFitGeneration = 0;
    JobRegistry *m_jobs = nullptr;
    CloudProviders *m_cloud = nullptr;
    // These trees must outlive m_playback: the compositor thread holds a bare
    // pointer into whichever one is live and may still be mid-composite at
    // teardown. During a multicam session that is m_multicamStaged, otherwise
    // m_project. Members are destroyed in reverse declaration order.
    drift::Project m_project;
    drift::Project m_multicamBase;
    drift::Project m_multicamStaged;
    PlaybackEngine m_playback;
    // Only for its audioOutputsChanged signal — the sinks resolve devices themselves.
    QMediaDevices m_mediaDevices;
    QString m_audioOutputDeviceId;
    drift::AudioRecorder m_audioRecorder;
    drift::TimeUs m_recordingStartPlayheadUs = 0;
    int m_voiceoverCounter = 0;
    // The audio error already on screen, so a device that fails repeatedly toasts once.
    QString m_lastAudioError;
    QUndoStack m_undoStack;
    bool m_editSessionOpen = false;
    // tracks() serialises every clip in the project into nested QVariantMaps, and used to do it
    // once per binding that read it. Cached between edits; notifyTracksChanged() drops it.
    mutable QVariantList m_tracksCache;
    mutable bool m_tracksCacheValid = false;
    // durationUs() is an uncached full scan behind the durationSeconds property, which notifies
    // on the same signal and is read just as widely (the overview strip sizes itself from it).
    mutable double m_durationSecondsCache = 0.0;
    mutable bool m_durationCacheValid = false;
    quint32 m_tracksRevision = 0;
    // One model per track index, parented to this. Grown on demand and never shrunk: a Repeater
    // holds the pointer it was handed, and deleting the model out from under it on a track
    // removal would leave it dangling. An unused slot just holds no rows.
    QList<TimelineClipsModel *> m_clipModels;
    // Live trim drag scope. The memo rejects a repeated pointer position before snapTime() and
    // the sync passes run; m_trimGestureChanged is what tells the caller whether the gesture
    // earned an undo step.
    mutable QList<drift::TimeUs> m_extraSnapTargetsCache;
    mutable bool m_extraSnapTargetsValid = false;
    // Pinned for the duration of a trim drag. Nothing can add or remove a clip mid-gesture, and
    // the only targets that do move are the dragged clip's own edges.
    drift::SnapTargets m_gestureSnapTargets;
    bool m_trimGestureActive = false;
    bool m_trimGestureChanged = false;
    drift::TimeUs m_trimGestureLastInputUs = -1;
    int m_trimGestureLastOutcome = 0;
    drift::TimeUs m_playheadUs = 0;
    bool m_playing = false;
    bool m_scrubbing = false;
    bool m_snapEnabled = true;
    bool m_rippleEnabled = false;
    drift::TimeUs m_snapThresholdUs = drift::kSnapThresholdUs;
    bool m_allowClipOverlap = false;
    bool m_loopWorkAreaEnabled = false;
    QString m_mediaViewMode = QStringLiteral("grid");
    bool m_autoKeyEnabled = false;
    bool m_positionLinked = true;
    bool m_sizeLinked = true;
    // One benchmark at a time: it drives the shared decoders and the GL thread, and two
    // sweeps interleaved would measure each other rather than the pipeline.
    std::atomic<bool> m_benchmarkRunning{false};
    QStringList m_keyframeGraphHiddenProperties;
    bool m_subtitleEditing = false;
    int m_selectedSubtitleCue = -1;
    bool m_exportInProgress = false;
    double m_exportProgress = 0.0;
    QAtomicInt m_exportCancel = 0;
    QUrl m_lastExportUrl;
    QString m_lastExportName;
    // Android: the publish-to-gallery copy behind Share is on a worker, so canShareExport reports
    // false while it runs — that both hides the button (the dialog binds its visibility to it) and
    // stops a second tap from starting the copy again. Unused on desktop.
    bool m_sharingExport = false;
    bool m_subtitleGenerating = false;
    double m_subtitleGenProgress = 0.0;
    QString m_subtitleGenStatus;
    QAtomicInt m_subtitleGenCancel = 0;

    struct MulticamAngleSnap {
        int trackIndex = -1;
        QString clipId;
        drift::Clip original;
        int audioTrackIndex = -1;
        QString audioClipId;
        drift::Clip originalAudio;
        bool hasAudio = false;
    };

    // Multicam punching session. `m_project` stays the stacked originals until Save.
    bool m_multicamActive = false;
    QList<MulticamAngleSnap> m_multicamSnaps;
    drift::TimeUs m_multicamRangeStart = 0;
    drift::TimeUs m_multicamRangeEnd = 0;
    QList<drift::MulticamCut> m_multicamCuts;
    int m_multicamRevision = 0;
    quint64 m_multicamPlayheadSignature = 0;
    QElapsedTimer m_inspectorPlayheadClock;
    // A refresh already running. Tiles are dropped rather than queued while it is set, so a
    // machine that cannot keep up falls behind in frame rate instead of in wall-clock time.
    bool m_multicamRefreshing = false;
    int m_multicamGeneration = 0; // bumped per refresh; stale decodes are dropped
    QFuture<void> m_multicamRefreshFuture;
    // Drives tile refreshes during playback only; scrubbing and paused edits refresh directly
    // off the signal that caused them.
    QTimer *m_multicamTimer = nullptr;

    bool m_reverseRendering = false;
    double m_reverseProgress = 0.0;
    QString m_reverseStatus;
    QAtomicInt m_reverseCancel = 0;

    // Playhead per timeline, so switching tabs returns to where each was left. "" = main.
    QHash<QString, drift::TimeUs> m_sequencePlayheads;
    int m_selectedTrack = -1;
    int m_selectedClip = -1;
    int m_selectedTransitionTrack = -1;
    int m_selectedTransitionLeftClip = -1;
    QStringList m_selectedTrackIds;
    QString m_trackSelectionAnchor;
    QString m_focusedMaskId;
    bool m_autoCrossfade = true; // read from QSettings in the constructor
    // The (from, to) clip ids a move should crossfade, or empty. See moveClip.
    QPair<QString, QString> autoCrossfadeFor(int trackIndex, int clipIndex, const QSet<QString> &movedIds) const;
    static QPair<QString, QString> autoCrossfadeOnTrack(const drift::Track &track, const drift::Clip &moved,
                                                        const QSet<QString> &movedIds);
    void addAutoCrossfade(int trackIndex, const QString &fromId, const QString &toId);
    int m_maskPointFocus = -1;
    QList<QPair<int, int>> m_selection;
    int m_selectionRevision = 0;
    int m_timelineTrimCursorSide = 0;
    int m_timelineTrimCursorHeight = 0;
    int m_timelineTrimCursorOwner = 0;
    int m_trimCursorTokenSeq = 0;
    // The pointer is drawn with QPainter at the track's height. Heights come from a handful of
    // row sizes, so this stays tiny — and a member rather than a function-local static because a
    // QCursor holds a platform cursor that must not outlive QGuiApplication.
    mutable QHash<int, QCursor> m_trimCursorCache;
    QCursor trimCursorFor(int side, int heightPx) const;
    PreviewController *m_preview = nullptr;
    PreferencesController *m_preferences = nullptr;
    ProjectFileController *m_projectFile = nullptr;
    AssetPreviewController *m_assetPreview = nullptr;
    SpeedCurveController *m_speedCurve = nullptr;
    CurveEditorController *m_curves = nullptr;
    SegmentationController *m_segmentation = nullptr;
    SceneDetectController *m_sceneDetect = nullptr;
    DepthController *m_depth = nullptr;
    DenoiseController *m_denoise = nullptr;
    RestoreController *m_restore = nullptr;
    FaceTrackingController *m_faces = nullptr;
    MotionTrackController *m_motionTrack = nullptr;
    BodyController *m_body = nullptr;
    StabilizeController *m_stabilize = nullptr;
    MediaBinController *m_bin = nullptr;
    TtsController *m_tts = nullptr;
    VoiceLibrary *m_voices = nullptr;
    QStringList m_activeGuideSets{QStringLiteral("thirds")};
    // App-wide custom sets.
    QList<drift::GuideSet> m_guideLibrary;
    // Copies of custom sets the open project uses, so its guides draw on a machine without them.
    QList<drift::GuideSet> m_projectGuideSets;
    const drift::GuideSet *findGuideSet(const QString &id) const;
    drift::GuideSet *libraryGuideSet(const QString &id);
    // Persists the library; an edit to an active set also changes what the project saves.
    void guideLibraryEdited(const QString &id);
    QHash<QString, QString> m_shortcuts;
    QHash<QString, QSet<QString>> m_assetFavorites;
    int m_draggingAssetIndex = -1;
    QString m_lastMessage;
    QString m_lastMessageSeverity = QStringLiteral("info");
    bool m_inlineTextEditing = false;
    struct InlineTextEdit
    {
        bool active = false;
        int track = -1;
        int clip = -1;
        QString clipId;
        QString original;
        QList<drift::TextRun> originalRuns; // the letters' own styles, restored on cancel
        QString text;   // model text, no preedit
        int cursor = 0;
        int selStart = -1;
        int selEnd = -1;
        QString preedit;
        double preferredX = 0.0;
        int preferredFor = -1;
    };
    InlineTextEdit m_inlineEdit;
    drift::Clip *inlineEditClip();
    const drift::Clip *inlineEditClip() const;
    // The clip's laid-out block, and block-local render px -> canvas project px.
    bool inlineEditLayout(FrameCompositor::TextEditGeometry *geometry, QTransform *toCanvas, double *scale) const;
    int inlineRenderedPos(int modelPos) const;
    int inlineModelPos(int renderedPos) const;
    bool m_previewDragActive = false;
    drift::Clip *textClipAt(int trackIndex, int clipIndex);
    // A text, subtitle or shape clip: anything that carries a shading stack.
    drift::Clip *styledClipAt(int trackIndex, int clipIndex, bool textOnly = false);
    static void applyTextStylePatch(drift::TextStyle &style, const QVariantMap &patch);
    static QVariantMap textAnimationPresetToMap(const drift::TextAnimationPreset &preset);
    drift::Project m_previewDragBefore;
    QString m_previewDragText;
    // Something was written since beginPreviewDrag; a press with no movement commits nothing.
    bool m_previewDragDirty = false;
    // The shaded letters the layer calls aim at (setTextStyleRange).
    int m_textRangeTrack = -1;
    int m_textRangeClip = -1;
    int m_textRangeStart = -1;
    int m_textRangeEnd = -1;
    // The range [start, end) for that clip when one is shaded on it, clamped to its text.
    bool textStyleRangeFor(int trackIndex, int clipIndex, int *start, int *end) const;
    // The stack those letters paint with now: their stretch's own, or a copy of the block's.
    QList<drift::TextShadingLayer> textRangeLayers(const drift::Clip &clip, int start) const;
    // Gives the letters [start, end) the stack `layers` (and keeps everything else they had).
    void writeTextRangeLayers(drift::Clip &clip, int start, int end, const QList<drift::TextShadingLayer> &layers);
    // The same, plus the font of `styled` when it differs from the block's (a look, a quick style).
    void writeTextRangeStyle(drift::Clip &clip, int start, int end, const drift::TextStyle &styled);
    // Begun by a setter rather than a press (keyboard nudges); commits once the nudges stop.
    bool m_previewDragAuto = false;
    QTimer *m_previewAutoCommit = nullptr;
    void emitPreviewFrame();
    void emitPreviewEdit(int trackIndex, int clipIndex, const QStringList &keys);
    void beginImplicitPreviewDrag(const QString &undoText);
    struct ClipboardItem
    {
        drift::Clip clip;
        drift::TrackType trackType = drift::TrackType::Video;
        QList<drift::Transition> transitions;
        // Carried separately because a mask lives on the adjustments pinned to the clip, not on
        // the clip: copying the Clip alone would silently drop it.
        QList<drift::Mask> masks;
    };
    QList<ClipboardItem> m_clipboard;
    struct CopiedKey
    {
        QString prop;
        drift::TimeUs afterFirstUs = 0;
        drift::Keyframe<double> key;
    };
    QList<CopiedKey> m_keyClipboard;

    // Whole-file peaks, for the dialogs that show a complete clip at once (Denoise, Speed
    // Curve). The timeline uses m_waveformBlocks instead — see waveformPeaksRange.
    mutable QHash<QString, MediaWaveform::Dense> m_waveformCache;
    mutable QSet<QString> m_waveformPending;

    mutable WaveformBlockCache m_waveformBlocks;

    mutable FilmstripTileCache m_filmstripTiles;

    // Subtitle-lane voice waveform: the mixed audio underneath a subtitle clip's
    // span, voice band-passed. Keyed by "<startUs>:<durUs>"; invalidated on edits.
    mutable QHash<QString, QVariantList> m_subtitleWaveformCache;
    mutable QSet<QString> m_subtitleWaveformPending;

    // Beat detection. Only one range is live at a time, so this needs no cache — just a
    // generation counter so a job whose range the user has since left is dropped on arrival.
    AudioBeatAnalysis m_beatAnalysisRaw; // kept so snap targets can be rebuilt per layer
    QVariantMap m_beatAnalysis;          // the same result, shaped for QML
    bool m_beatAnalysisRunning = false;
    quint64 m_beatAnalysisGeneration = 0;
    QByteArray m_beatAudioFingerprint;
    bool m_beatGridVisible = false;
    bool m_onsetsVisible = false;
    struct PendingEffectTemplate
    {
        int trackIndex = -1;
        int clipIndex = -1;
        QString templateId;
        bool valid() const { return trackIndex >= 0 && clipIndex >= 0 && !templateId.isEmpty(); }
    };
    std::optional<PendingEffectTemplate> m_pendingEffectTemplate;
    // A template rhythm change waiting on beat analysis: (clip id, sync).
    std::optional<QPair<QString, QString>> m_pendingTemplateRhythm;
    // Beats and onsets as snap targets, thinned so a dense onset list cannot make every
    // position on the timeline snap to something. Only the visible layers contribute.
    QList<drift::TimeUs> m_beatSnapTargets;

    // Launch layout picker / first-clip setup completed for this empty project.
    bool m_projectLayoutChosen = false;

    McpController *m_mcpController = nullptr;
    // Protected wrappers for this TU's file-local clip writers. McpController calls them.
    bool writeClipProp(drift::Clip &clip, const QString &prop, drift::TimeUs relative, double value,
                       bool autoKey, bool force);
    drift::KeyframeTrack<double> *transformTrack(drift::Clip &clip, const QString &prop);
    void clearPose3d(drift::Clip &clip);
    // Freeze frames and full-size MCP captures share one media path.
    static QString newFreezeFramePath(const QString &projectId);

    void setProjectLayoutChosen(bool chosen);

    static constexpr int kMaxUndoSteps = 50;
};
