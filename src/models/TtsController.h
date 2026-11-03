#pragma once

#include "engine/ChatterboxTts.h"

#include <QObject>
#include <QPair>
#include <QString>
#include <QStringList>
#include <QTimer>
#include <QUrl>
#include <QVariantList>

#include <atomic>
#include <functional>
#include <memory>
#include <vector>

class AppController;
class JobContext;
class VoiceLibrary;

// Local Chatterbox text-to-speech, reached from QML as EditorState.tts. Owns the one shared engine:
// loading it takes about a minute, so it is loaded once on first use (warmUp() starts that early)
// and kept. Every job that touches it runs on JobRegistry's single model lane, which is what keeps
// two of them from using the engine at once.
class TtsController : public QObject
{
    Q_OBJECT

    Q_PROPERTY(bool available READ available NOTIFY availableChanged)
    Q_PROPERTY(bool modelLoaded READ modelLoaded NOTIFY loadStateChanged)
    Q_PROPERTY(bool loading READ loading NOTIFY loadStateChanged)
    Q_PROPERTY(bool running READ running NOTIFY runningChanged)
    Q_PROPERTY(double progress READ progress NOTIFY progressChanged)
    Q_PROPERTY(QString status READ status NOTIFY statusChanged)
    Q_PROPERTY(QString lastVoice READ lastVoice NOTIFY lastUsedChanged)
    Q_PROPERTY(QString lastLanguage READ lastLanguage NOTIFY lastUsedChanged)
    Q_PROPERTY(double lastExaggeration READ lastExaggeration NOTIFY lastUsedChanged)
    // What the Voz tab shows, kept here: the tab is unloaded when another one is opened (0.30).
    Q_PROPERTY(QString draftScript MEMBER m_draftScript NOTIFY panelStateChanged)
    Q_PROPERTY(QString lastResultText MEMBER m_lastResultText NOTIFY panelStateChanged)
    Q_PROPERTY(bool lastResultOk MEMBER m_lastResultOk NOTIFY panelStateChanged)
    // The take (0.30, as CapCut and ElevenLabs): the script spoken sentence by sentence, heard
    // before it goes on the timeline. [{text, url, seconds}] per sentence.
    Q_PROPERTY(QVariantList sentences READ sentences NOTIFY takeChanged)
    Q_PROPERTY(bool hasTake READ hasTake NOTIFY takeChanged)
    Q_PROPERTY(QUrl takeUrl READ takeUrl NOTIFY takeChanged)
    Q_PROPERTY(double takeSeconds READ takeSeconds NOTIFY takeChanged)
    // Editing the script of a voice already on the timeline: inserting replaces that clip's audio.
    Q_PROPERTY(bool replacing READ replacing NOTIFY takeChanged)
    Q_PROPERTY(double lastSpeed READ lastSpeed NOTIFY lastUsedChanged)
    Q_PROPERTY(double lastPitch READ lastPitch NOTIFY lastUsedChanged)

public:
    TtsController(AppController *app, QObject *parent = nullptr);

    void setVoices(VoiceLibrary *voices) { m_voices = voices; }

    bool available() const { return m_available; }
    bool modelLoaded() const { return m_loaded.load(); }
    bool loading() const { return m_loading.load(); }
    bool running() const { return m_running; }
    double progress() const { return m_progress; }
    QString status() const { return m_status; }
    QString lastVoice() const;
    QString lastLanguage() const;
    double lastExaggeration() const;

    // [{code, label}] for the languages the model supports.
    Q_INVOKABLE QVariantList languageOptions() const;
    Q_INVOKABLE void warmUp();
    Q_INVOKABLE void cancel();
    // Speaks the script into a take: one sentence at a time ([pausa 1s] marks a silence, a blank
    // line a longer breath), with speed and pitch applied after (they keep the voice's character).
    // A dialogue (lines «Ana: …», «Luis: …») speaks each person with their voice from
    // speakerVoices {name: voiceId}; the rest with voiceId.
    Q_INVOKABLE void generate(const QString &text, const QString &voiceId, const QString &lang,
                              double exaggeration, double speed = 1.0, double pitch = 1.0,
                              const QVariantMap &speakerVoices = {});
    // The people of a dialogue script, in the order they first speak (empty for a plain script).
    Q_INVOKABLE QStringList scriptSpeakers(const QString &text) const;
    // The script as [{speaker, text}] parts: a line «Name: words» starts that person's part.
    static QList<QPair<QString, QString>> dialogueParts(const QString &text);
    // Speaks one sentence of the take again (with these settings) and rebuilds the take.
    Q_INVOKABLE void regenerateSentence(int index, const QString &voiceId, const QString &lang, double exaggeration);
    // New speed and pitch for the take, without speaking it again.
    Q_INVOKABLE void retune(double speed, double pitch);
    // The take on the timeline at the playhead (or in place of the clip being edited), with its
    // captions when asked; then the take is cleared.
    Q_INVOKABLE void insertTake(bool captions);
    Q_INVOKABLE void discardTake();
    // A voice the app spoke keeps its script (MediaAsset::generator): read it, or open it in the
    // Voz tab to change and speak again (editRequested), replacing that clip's audio.
    Q_INVOKABLE QString clipScript(int trackIndex, int clipIndex) const;
    Q_INVOKABLE void editClipScript(int trackIndex, int clipIndex);
    // A text clip's words as the script; the voice is then added where the text starts.
    Q_INVOKABLE void speakTextClip(int trackIndex, int clipIndex);
    // A script from a .txt, .md or .docx file; empty when it cannot be read.
    Q_INVOKABLE QString readScriptFile(const QUrl &url) const;
    // The spoken file of that clip, saved where the user says (FLAC, as it was made).
    Q_INVOKABLE bool saveClipVoice(int trackIndex, int clipIndex, const QUrl &url) const;
    // The music on the other audio tracks goes down while this voice speaks (After Effects' and
    // CapCut's ducking); how many music clips were lowered.
    Q_INVOKABLE int duckMusicUnder(int trackIndex, int clipIndex);

    // The script in sentences, each with the silence after it (seconds).
    static QList<QPair<QString, double>> splitScript(const QString &text);
    // Speed (tempo, the pitch kept) and pitch on 24 kHz mono speech.
    static std::vector<float> retuned(const std::vector<float> &pcm, double speed, double pitch);

    QVariantList sentences() const;
    bool hasTake() const { return !m_takePath.isEmpty(); }
    QUrl takeUrl() const { return m_takePath.isEmpty() ? QUrl() : QUrl::fromLocalFile(m_takePath); }
    double takeSeconds() const { return m_takeSeconds; }
    bool replacing() const { return !m_replaceClipId.isEmpty(); }
    double lastSpeed() const;
    double lastPitch() const;
    // The subtitle clip at (trackIndex, clipIndex): one voiced clip per caption, on new audio tracks.
    Q_INVOKABLE void voiceoverFromSubtitles(int trackIndex, int clipIndex, const QString &voiceId,
                                            const QString &lang, double exaggeration);

    // Model-lane workers only: loads on first use, then reuses the session.
    bool ensureLoaded(QString *err);
    drift::ChatterboxTts &engine() { return m_engine; }

public slots:
    void refreshAvailability();

signals:
    void availableChanged();
    void loadStateChanged();
    void runningChanged();
    void progressChanged();
    void statusChanged();
    void lastUsedChanged();
    void panelStateChanged();
    void takeChanged();
    // editClipScript: {text, voice, lang, exaggeration, speed, pitch} for the Voz tab to show.
    void editRequested(const QVariantMap &settings);
    void finished(bool ok, const QString &message);

private:
    struct Line
    {
        QString text;
        double pauseAfter = 0.0;
        QString voiceId; // the speaker's voice in a dialogue; empty = the take's
        std::shared_ptr<const std::vector<float>> pcm;
        QString path;
        double seconds = 0.0;
    };
    struct TakeFiles
    {
        QString path;
        double seconds = 0.0;
        QStringList linePaths;
        QList<double> lineSeconds;
        QString error;
    };
    // Writes each sentence and the whole take, retuned. Any thread.
    static TakeFiles writeTake(const QList<Line> &lines, double speed, double pitch, const QString &script);
    void adoptTake(const QList<Line> &lines, const TakeFiles &files);
    void clearTakeFiles(bool keepTake);
    void startTakeJob(const QString &label, std::function<void(JobContext &)> work,
                      std::function<void()> done);

    QList<Line> m_lines;
    QString m_takePath;
    double m_takeSeconds = 0.0;
    QString m_takeScript;
    QString m_takeVoice;
    QString m_takeLang;
    double m_takeExaggeration = 0.5;
    double m_takeSpeed = 1.0;
    double m_takePitch = 1.0;
    QString m_replaceClipId;
    double m_insertAtSeconds = -1.0; // where the take goes (a text read aloud); -1 = the playhead
    QString m_draftScript;
    QString m_lastResultText;
    bool m_lastResultOk = true;
    void remember(const QString &voiceId, const QString &lang, double exaggeration);
    void pollJob();
    void endJob();
    void setStatus(const QString &status);

    AppController *m_app = nullptr;
    VoiceLibrary *m_voices = nullptr;
    drift::ChatterboxTts m_engine;
    bool m_available = false;
    std::atomic<bool> m_loaded{false};
    std::atomic<bool> m_loading{false};
    bool m_running = false;
    double m_progress = 0.0;
    QString m_status;
    QString m_jobId;
    QString m_loadJobId;
    QTimer m_poll;
    bool m_shownLoaded = false;
    bool m_shownLoading = false;
};
