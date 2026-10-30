#pragma once

#include <QDateTime>
#include <QObject>
#include <QPointer>
#include <QString>
#include <QUrl>

#include <functional>
#include <memory>

class QNetworkAccessManager;
class QNetworkReply;
class QTcpServer;
class QTimer;

// Flip Studio account: Google sign-in through api.getflipstudio.com.
//
// Sign-in is the desktop flow Google asks for: the system browser opens Google's consent page
// with PKCE, Google redirects to a one-shot server on 127.0.0.1, and the code plus verifier go to
// our API, which exchanges them with the client secret. No secret ships in the app; the client id
// is public by design.
//
// The API answers with a 15-minute access token and a refresh token that rotates on every use.
// The refresh token is sealed with DPAPI (drift::secrets); the access token is shared through
// QSettings too, so two running copies do not both rotate the same refresh token — the server
// treats a reused one as stolen and ends the session.
class AccountController : public QObject
{
    Q_OBJECT
    // Empty when this build has no account service.
    Q_PROPERTY(bool available READ available CONSTANT)
    Q_PROPERTY(bool signedIn READ signedIn NOTIFY accountChanged)
    // Waiting for the browser or the server.
    Q_PROPERTY(bool busy READ busy NOTIFY busyChanged)
    Q_PROPERTY(QString name READ name NOTIFY accountChanged)
    Q_PROPERTY(QString email READ email NOTIFY accountChanged)
    Q_PROPERTY(QUrl avatarUrl READ avatarUrl NOTIFY accountChanged)
    // When the account was created on api.getflipstudio.com; invalid until the server said.
    Q_PROPERTY(QDateTime memberSince READ memberSince NOTIFY accountChanged)
    // Last failure in one sentence, cleared when a new attempt starts.
    Q_PROPERTY(QString error READ error NOTIFY errorChanged)
    // Google's sign-in page while a sign-in is waiting, so it can be copied when no browser opened.
    Q_PROPERTY(QString signInUrl READ signInUrl NOTIFY busyChanged)
    // The first-launch welcome ("Sign in with Google / Continue without an account") is still due.
    Q_PROPERTY(bool needsWelcome READ needsWelcome NOTIFY needsWelcomeChanged)

public:
    explicit AccountController(QObject *parent = nullptr);
    ~AccountController() override;

    bool available() const;
    bool signedIn() const { return !m_refreshToken.isEmpty(); }
    bool busy() const { return m_busy; }
    QString name() const { return m_name; }
    QString email() const { return m_email; }
    QUrl avatarUrl() const { return m_avatarUrl; }
    QDateTime memberSince() const { return m_memberSince; }
    QString error() const { return m_error; }
    QString signInUrl() const { return m_busy ? m_signInUrl : QString(); }
    bool needsWelcome() const;

    // A valid access token, or empty when signed out. May be about to expire; callers that get a
    // 401 call refresh().
    QString accessToken() const { return m_accessToken; }

    Q_INVOKABLE void signIn();
    Q_INVOKABLE void cancelSignIn();
    // Puts signInUrl on the clipboard, for pasting into a browser by hand.
    Q_INVOKABLE void copySignInUrl();
    Q_INVOKABLE void signOut();
    // Deletes the account on the server (sessions too; installs become anonymous), then signs out.
    Q_INVOKABLE void deleteAccount();
    Q_INVOKABLE void dismissWelcome();

    // Gets a fresh access token. `then(ok)` runs once; concurrent calls share one request.
    void refresh(const std::function<void(bool)> &then = {});

    // Pure helpers, public for the tests.
    static QString makeCodeVerifier();
    static QString codeChallenge(const QString &verifier);
    // From the first line of the loopback request ("GET /?code=…&state=… HTTP/1.1"): the query,
    // or an empty one when the path is not the redirect target.
    static bool parseRedirectRequest(const QByteArray &requestLine, QString *code, QString *state,
                                     QString *error);

signals:
    void accountChanged();
    void busyChanged();
    void errorChanged();
    void needsWelcomeChanged();
    // The access token was replaced (or cleared on sign-out).
    void accessTokenChanged();
    void signInFinished(bool ok);

private:
    QUrl apiUrl(const QString &path) const;
    QNetworkReply *postJson(const QString &path, const QByteArray &body, bool withAuth = false);
    void setBusy(bool busy);
    void setError(const QString &error);
    void finishLoopback();
    bool openBrowser(const QUrl &url);
    void handleRedirect(const QByteArray &requestLine, class QTcpSocket *socket);
    void exchangeCode(const QString &code);
    void applySession(const QByteArray &payload);
    void loadStored();
    void store();
    void clearLocal();

    QNetworkAccessManager *m_network = nullptr;
    QTimer *m_refreshTimer = nullptr;
    QPointer<QTcpServer> m_loopback;
    QTimer *m_loopbackTimeout = nullptr;
    QString m_verifier;
    QString m_state;
    QString m_redirectUri;
    QString m_signInUrl;

    QString m_accessToken;
    qint64 m_accessExpiresAt = 0;
    QString m_refreshToken;
    QString m_name;
    QString m_email;
    QUrl m_avatarUrl;
    QDateTime m_memberSince;
    QString m_error;
    bool m_busy = false;

    bool m_refreshing = false;
    QList<std::function<void(bool)>> m_refreshWaiters;
    // Held from the refresh POST until its reply, across running copies of the app: two copies
    // sending the same refresh token made the server see a reuse and close the whole session.
    std::unique_ptr<class QLockFile> m_refreshLock;
    // Bumped by clearLocal: a refresh reply from before a sign-out must not sign the user back in.
    quint64 m_sessionGeneration = 0;
};
