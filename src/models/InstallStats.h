#pragma once

#include <QObject>
#include <QString>

class AccountController;
class QNetworkAccessManager;
class QTimer;

// Anonymous install statistics for api.getflipstudio.com: how many machines run Flip Studio,
// which versions, and which updates were applied.
//
// What is sent: a random id this install made for itself (a UUID, nothing derived from the
// machine or the person), the event ("install", "update" with the version it came from, or
// "active" at most once a day), the version, the Windows edition and how the app was installed
// (Store, installer or portable). No IP is stored by the server, no project, no file name.
//
// When the person is signed in, the request carries the account token and the server ties the
// install to the account; that is said in the privacy policy. With the switch off nothing is sent
// at all, signed in or not.
class InstallStats : public QObject
{
    Q_OBJECT
    Q_PROPERTY(bool available READ available CONSTANT)
    Q_PROPERTY(bool enabled READ enabled WRITE setEnabled NOTIFY enabledChanged)

public:
    explicit InstallStats(AccountController *account, QObject *parent = nullptr);

    bool available() const;
    bool enabled() const;
    void setEnabled(bool enabled);

    // Records this run (the version it was, for detecting updates) and schedules the first report.
    void start();

    struct Event {
        QString type; // "install", "update", "active", or empty for nothing to send
        QString fromVersion;
    };
    // Pure decision, public for the tests. An empty `lastRunVersion` is a first report: a fresh
    // install, or an older one whose earlier version is unknown — both count as an install.
    static Event decide(const QString &lastRunVersion, const QString &currentVersion,
                        const QString &lastReportedDay, const QString &today);
    // "0.9.9-nightly.3" → "0.9.9"; anything that is not a plain version → empty.
    static QString baseVersion(const QString &version);
    // "store", "installer", "portable" or "unknown".
    static QString channel();

signals:
    void enabledChanged();

private:
    void report();

    AccountController *m_account = nullptr;
    QNetworkAccessManager *m_network = nullptr;
    QTimer *m_dailyTimer = nullptr;
    bool m_sending = false;
};
