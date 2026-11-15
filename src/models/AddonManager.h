#pragma once

#include <QHash>
#include <QJsonObject>
#include <QObject>
#include <QUrl>
#include <QPointer>
#include <QElapsedTimer>
#include <QSet>
#include <QStringList>
#include <QVariantList>
#include <QVariantMap>

#include <memory>

class QLockFile;
class QNetworkAccessManager;
class QSystemTrayIcon;

// Downloads and installs addons. Lives in the app layer, not driftengine, so tools/ and tests/
// keep working with no network stack — they read the registry (drift::addon::AddonRegistry) and
// never write it.
//
// The remote index is the source of truth for what exists and at which version; installed.json is
// the source of truth for what is here. A row's state is derived by comparing the two.
class AddonManager : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QVariantList catalog READ catalog NOTIFY catalogChanged)
    Q_PROPERTY(QString status READ status NOTIFY statusChanged)
    Q_PROPERTY(bool refreshing READ refreshing NOTIFY refreshingChanged)
    // False when the build has no addon index URL: the manager then says downloads are coming
    // rather than reporting a store it cannot reach.
    Q_PROPERTY(bool serviceAvailable READ serviceAvailable CONSTANT)
    // Header attention nudge: offer the core video / transitions / audio packs when they are not
    // yet installed as addons (bundled copies still work; installing unlocks the update channel).
    Q_PROPERTY(bool remindEssential READ remindEssential WRITE setRemindEssential
                   NOTIFY remindEssentialChanged)
    // Header attention nudge: mention installed packs that have a newer version on the store.
    Q_PROPERTY(bool remindUpdates READ remindUpdates WRITE setRemindUpdates
                   NOTIFY remindUpdatesChanged)
    // «Install all» (0.32): one queue for every extra not installed yet (and the outdated ones),
    // kept here so it goes on with the Extras dialog closed, across projects, and even after the
    // window is closed (continueInBackground). {active, total, done, installed, failed, current,
    // bytesDone, bytesTotal, failedNames}.
    Q_PROPERTY(QVariantMap bulk READ bulk NOTIFY bulkChanged)

public:
    explicit AddonManager(QObject *parent = nullptr);
    ~AddonManager() override;

    // One row per known addon: id, name, description, details, author, license, kind, version,
    // installedVersion, downloadSize, installedSize, items, state.
    // state is one of: available, downloading, installing, installed, update-available, failed,
    // needs-newer-app (minAppVersion is above this build; also sets minAppVersion on the row).
    QVariantList catalog() const;
    QString status() const;
    bool refreshing() const;
    bool serviceAvailable() const;

    bool remindEssential() const;
    void setRemindEssential(bool remind);
    bool remindUpdates() const;
    void setRemindUpdates(bool remind);

    // Uses the on-disk copy of the index when it is younger than six hours unless forced, so
    // launching offline is quiet rather than an error.
    Q_INVOKABLE void refresh(bool force = false);

    Q_INVOKABLE void install(const QString &id);

    // --- Install all ------------------------------------------------------------------------
    // What «Install all» would download now: {count, bytes, names}. `only` limits it to those ids
    // (resuming a queue a closed app left half done).
    Q_INVOKABLE QVariantMap installAllPlan(const QStringList &only = {}) const;
    // Starts the queue (two at a time, smallest first). False when there is nothing to install,
    // or another Flip Studio is already installing them (a lock file in the download cache).
    Q_INVOKABLE bool installAll(const QStringList &only = {});
    Q_INVOKABLE void cancelInstallAll();
    QVariantMap bulk() const;
    // True for an extra the current (or last) queue was installing: its failures are reported
    // once, at the end, instead of one notice each.
    Q_INVOKABLE bool isBulkItem(const QString &id) const;
    // The extras a queue that never finished (the app was killed) left to install, still missing.
    Q_INVOKABLE QStringList pendingInstallAll() const;
    Q_INVOKABLE void forgetPendingInstallAll();
    // True while another Flip Studio process holds the install-all lock.
    Q_INVOKABLE bool installAllRunningElsewhere() const;
    // The window was closed while the queue runs: the process stays alive with a tray icon
    // showing the progress, and quits on its own when the queue ends.
    Q_INVOKABLE void continueInBackground();
    Q_INVOKABLE void cancel(const QString &id);
    Q_INVOKABLE void uninstall(const QString &id);

    // True when an addon providing this kind is installed — drives the empty states in
    // FontPicker, the stickers tab and subtitle generation.
    Q_INVOKABLE bool hasKind(const QString &kind) const;
    Q_INVOKABLE QString firstAddonForKind(const QString &kind) const;

    // Essential packs (effects / transitions / audio) that exist on the store but are not in
    // installed.json. Empty when the index has not been loaded or every essential is present.
    Q_INVOKABLE QVariantList missingEssentialAddons() const;
    // Installed packs with a newer version on the store.
    Q_INVOKABLE QVariantList updatableAddons() const;

    // --- User packages (.driftfx from Drift Forge) ---------------------------------------
    // Copies the picked file (a content:// URI on Android) into the cache and reads its manifest.
    // Returns name, kind ("effects" | "transitions"), version, author and description, or a map
    // with only `error`. Nothing is installed until installUserPackage(), which acts on the file
    // inspected last and answers on userPackageInstalled.
    Q_INVOKABLE QVariantMap inspectUserPackage(const QUrl &url);
    // Sniffs the magic, since a content:// URI from "Open with" rarely carries the file name.
    Q_INVOKABLE bool isUserPackage(const QUrl &url) const;
    Q_INVOKABLE void installUserPackage();
    // --- Addons from a file (.driftpkg, .zip, or a .driftfx routed to the above) ------------
    // Reads what the file claims to be and refuses it if this build cannot use it. Returns type
    // ("driftpkg" | "zip" | "driftfx"), name, version, author, description, nativeCode and
    // replaces (the name of an installed addon or store pack with the same id), or only `error`.
    // A "driftfx" result has gone through inspectUserPackage() and follows that flow instead.
    Q_INVOKABLE QVariantMap inspectAddonFile(const QUrl &url);
    // Installs the file inspected last. An officially signed .driftpkg installs straight away;
    // anything else emits addonFileNeedsConfirmation() until called again with acceptUnverified.
    // Answers on userPackageInstalled.
    Q_INVOKABLE void installAddonFile(bool acceptUnverified);
    Q_INVOKABLE void discardAddonFile();
    // customAddonsDir(), created if missing so the file manager has something to open.
    Q_INVOKABLE QUrl customAddonsFolderUrl() const;
    // Picks up folders added to or removed from the custom directory since the last look.
    Q_INVOKABLE void rescanCustomAddons();

    // Reload the catalogs behind these addon kinds and emit kindChanged for each, which is what
    // refreshes the browsers. Also used by MCP after it writes a package straight to disk.
    void reloadForKinds(const QStringList &kinds);

    // --- Acceleration ------------------------------------------------------------------
    // Whether an ONNX Runtime is installed at all. Every AI feature needs one, so this gates
    // their empty states alongside the model each of them wants.
    Q_INVOKABLE bool runtimeAvailable() const;

    // One row per selectable option: value, label, available. Always contains "auto" and "cpu".
    Q_INVOKABLE QVariantList accelerationOptions() const;
    Q_INVOKABLE QString acceleration() const;
    Q_INVOKABLE void setAcceleration(const QString &variant);

    // True once a runtime addon has been installed or removed in a session that had already
    // loaded one. The library is loaded once per process, so the change only takes effect on the
    // next launch and the dialog has to say so.
    Q_INVOKABLE bool runtimeRestartRequired() const;

signals:
    void catalogChanged();
    void statusChanged();
    void refreshingChanged();
    void remindEssentialChanged();
    void remindUpdatesChanged();
    // Emitted continuously during download and extraction; the dialog binds this rather than
    // rebuilding the whole catalogue list several times a second.
    void progressChanged(const QString &id, double fraction, const QString &phase);
    // A kind's content changed on disk and its catalog has already been reloaded.
    void kindChanged(const QString &kind);
    // Per-transfer outcome. `status` is a mixed-purpose display string — it carries
    // store errors, per-transfer failures and the empty success state alike — so
    // these exist to let callers react to an outcome without reading its prose.
    void transferFailed(const QString &id, const QString &reason);
    void transferSucceeded(const QString &id);
    // Outcome of installUserPackage(); `error` is empty on success.
    void userPackageInstalled(const QString &name, const QString &error);
    // The file from inspectAddonFile() is not signed by the Drift team; the UI asks before
    // calling installAddonFile(true) or discardAddonFile().
    void addonFileNeedsConfirmation();
    void bulkChanged();
    // The queue ended: how many installed, how many failed (and their names), or was cancelled.
    void bulkFinished(int installed, int failed, const QStringList &failedNames, bool cancelled);
    // «Open Flip Studio» from the tray icon while the window is hidden.
    void showWindowRequested();

private:
    struct Transfer;

    void setStatus(const QString &status);
    void setRefreshing(bool refreshing);
    void applyIndex(const QByteArray &json, bool fromCache);
    void startDownload(const QString &id);
    void finishDownload(const QString &id);
    void beginExtract(const QString &id, const QString &packagePath);
    void failTransfer(const QString &id, const QString &message);
    void sweepDownloadCache();
    void pumpBulk();
    void settleBulk(const QString &id, bool ok);
    void endBulk(bool cancelled);
    void emitBulkChanged(bool force);
    void updateTray();
    void savePendingBulk() const;

    QString m_status;
    bool m_refreshing = false;
    QList<QJsonObject> m_remote;
    QHash<QString, std::shared_ptr<Transfer>> m_transfers;
    QHash<QString, QString> m_failures;
    // Download links expire after an hour, so an install started from a stale cached index gets
    // rejected. Those ids are re-driven once a fresh index lands; the set stops a rejected-twice
    // addon looping forever.
    QStringList m_awaitingFreshIndex;
    QSet<QString> m_retried;
    bool m_runtimeRestartRequired = false;
    QString m_userPackagePath;
    QString m_addonFilePath;
    QString m_addonFileType; // "driftpkg" | "zip"
    // Inside the zip: "" or "<top folder>/", whichever holds manifest.json.
    QString m_addonFileZipPrefix;
    QString m_addonFileId;
    QString m_addonFileName;
    // False when m_addonFilePath is the user's own file rather than a copy in the cache.
    bool m_addonFileOwned = false;
    bool m_addonFileBusy = false;
    QNetworkAccessManager *m_network = nullptr;

    bool m_bulkRunning = false;
    QStringList m_bulkQueue;
    QStringList m_bulkActive;
    QSet<QString> m_bulkIds;
    QHash<QString, double> m_bulkSize;
    QHash<QString, double> m_bulkFraction;
    QHash<QString, QString> m_bulkName;
    int m_bulkTotal = 0;
    int m_bulkInstalled = 0;
    QStringList m_bulkFailedNames;
    double m_bulkBytesTotal = 0.0;
    double m_bulkBytesSettled = 0.0;
    QElapsedTimer m_bulkEmitClock;
    std::unique_ptr<QLockFile> m_bulkLock;
    bool m_background = false;
    QSystemTrayIcon *m_tray = nullptr;
};
