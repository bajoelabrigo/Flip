#include "AccountController.h"
#include "core/SecretStore.h"

#include <QCryptographicHash>
#include <QDateTime>
#include <QClipboard>
#include <QDesktopServices>
#include <QGuiApplication>
#include <QHostAddress>
#include <QJsonDocument>
#include <QJsonObject>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QNetworkRequest>
#include <QProcess>
#include <QRandomGenerator>
#include <QSettings>
#include <QSysInfo>
#include <QTcpServer>
#include <QTcpSocket>
#include <QTimer>
#include <QUrlQuery>

#include <utility>

#ifdef Q_OS_WIN
#include <qt_windows.h>
#include <shlwapi.h>
#endif

// Configured in CMakeLists.txt. A translation unit built outside the `drift` target gets no
// account service rather than a stale hardcoded one.
#ifndef DRIFT_ACCOUNT_API_URL
#define DRIFT_ACCOUNT_API_URL ""
#endif
#ifndef DRIFT_GOOGLE_CLIENT_ID
#define DRIFT_GOOGLE_CLIENT_ID ""
#endif

namespace {

const QString kApiBase = QStringLiteral(DRIFT_ACCOUNT_API_URL);
// Public by design: Google identifies the app by it. The secret stays on api.getflipstudio.com.
const QString kGoogleClientId = QStringLiteral(DRIFT_GOOGLE_CLIENT_ID);

constexpr int kApiTimeoutMs = 20000;
// The person may need a while in the browser (choosing an account, two-step verification).
constexpr int kSignInTimeoutMs = 5 * 60 * 1000;
// Refresh this long before the access token runs out.
constexpr qint64 kRefreshSkewSecs = 120;
constexpr qsizetype kMaxRequestBytes = 16 * 1024;

QString key(const char *name)
{
    return QStringLiteral("account/") + QLatin1String(name);
}

QByteArray randomBytes(int count)
{
    QByteArray bytes(count, 0);
    for (int i = 0; i < count; ++i)
        bytes[i] = char(QRandomGenerator::system()->bounded(256));
    return bytes;
}

QByteArray base64Url(const QByteArray &data)
{
    return data.toBase64(QByteArray::Base64UrlEncoding | QByteArray::OmitTrailingEquals);
}

QByteArray pageFor(const QString &title, const QString &body)
{
    const QString html = QStringLiteral(
        "<!doctype html><html><head><meta charset=\"utf-8\"><title>Flip Studio</title>"
        "<style>body{font-family:system-ui,sans-serif;background:#111;color:#eee;display:flex;"
        "align-items:center;justify-content:center;height:100vh;margin:0}"
        "div{max-width:28em;text-align:center}h1{font-size:1.4em}</style></head>"
        "<body><div><h1>%1</h1><p>%2</p></div></body></html>")
        .arg(title.toHtmlEscaped(), body.toHtmlEscaped());
    const QByteArray content = html.toUtf8();
    return "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nCache-Control: no-store\r\n"
           "Connection: close\r\nContent-Length: "
        + QByteArray::number(content.size()) + "\r\n\r\n" + content;
}

} // namespace

AccountController::AccountController(QObject *parent)
    : QObject(parent)
    , m_network(new QNetworkAccessManager(this))
    , m_refreshTimer(new QTimer(this))
    , m_loopbackTimeout(new QTimer(this))
{
    loadStored();

    // A wall-clock check once a minute also covers waking from sleep, where a single-shot timer
    // set for "in 13 minutes" would have fired late.
    m_refreshTimer->setInterval(60 * 1000);
    connect(m_refreshTimer, &QTimer::timeout, this, [this] {
        if (signedIn() && QDateTime::currentSecsSinceEpoch() + kRefreshSkewSecs >= m_accessExpiresAt)
            refresh();
    });
    m_refreshTimer->start();

    m_loopbackTimeout->setSingleShot(true);
    m_loopbackTimeout->setInterval(kSignInTimeoutMs);
    connect(m_loopbackTimeout, &QTimer::timeout, this, [this] {
        finishLoopback();
        setError(tr("Sign-in timed out. Try again."));
        setBusy(false);
        emit signInFinished(false);
    });

    // Validates a stored session and picks up a changed name or picture.
    if (signedIn())
        QTimer::singleShot(3000, this, [this] { refresh(); });
}

AccountController::~AccountController()
{
    finishLoopback();
}

bool AccountController::available() const
{
    return !kApiBase.isEmpty() && !kGoogleClientId.isEmpty();
}

bool AccountController::needsWelcome() const
{
    return available() && !signedIn() && !QSettings().value(key("welcomeDone"), false).toBool();
}

void AccountController::dismissWelcome()
{
    if (QSettings().value(key("welcomeDone"), false).toBool())
        return;
    QSettings().setValue(key("welcomeDone"), true);
    emit needsWelcomeChanged();
}

QString AccountController::makeCodeVerifier()
{
    // 48 random bytes → 64 characters, inside RFC 7636's 43..128.
    return QString::fromLatin1(base64Url(randomBytes(48)));
}

QString AccountController::codeChallenge(const QString &verifier)
{
    return QString::fromLatin1(
        base64Url(QCryptographicHash::hash(verifier.toLatin1(), QCryptographicHash::Sha256)));
}

bool AccountController::parseRedirectRequest(const QByteArray &requestLine, QString *code,
                                             QString *state, QString *error)
{
    const QList<QByteArray> parts = requestLine.trimmed().split(' ');
    if (parts.size() < 2 || parts.at(0) != "GET")
        return false;
    const QUrl url(QStringLiteral("http://127.0.0.1") + QString::fromLatin1(parts.at(1)));
    if (!url.isValid() || url.path() != QLatin1String("/"))
        return false;
    const QUrlQuery query(url);
    if (code)
        *code = query.queryItemValue(QStringLiteral("code"), QUrl::FullyDecoded);
    if (state)
        *state = query.queryItemValue(QStringLiteral("state"), QUrl::FullyDecoded);
    if (error)
        *error = query.queryItemValue(QStringLiteral("error"), QUrl::FullyDecoded);
    return true;
}

void AccountController::signIn()
{
    if (!available() || m_busy)
        return;
    setError({});
    finishLoopback();

    auto *server = new QTcpServer(this);
    if (!server->listen(QHostAddress::LocalHost, 0)) {
        server->deleteLater();
        setError(tr("Could not start sign-in on this computer."));
        emit signInFinished(false);
        return;
    }
    m_loopback = server;
    m_verifier = makeCodeVerifier();
    m_state = QString::fromLatin1(base64Url(randomBytes(16)));
    m_redirectUri = QStringLiteral("http://127.0.0.1:%1/").arg(server->serverPort());

    connect(server, &QTcpServer::newConnection, this, [this, server] {
        while (QTcpSocket *socket = server->nextPendingConnection()) {
            // Owned by this object, not the server: the server is closed as soon as the code
            // arrives, and the socket must live on until the browser has the reply.
            socket->setParent(this);
            connect(socket, &QTcpSocket::disconnected, socket, &QObject::deleteLater);
            QTimer::singleShot(30000, socket, &QObject::deleteLater);
            connect(socket, &QTcpSocket::readyRead, this, [this, socket] {
                if (socket->property("driftHandled").toBool()) {
                    socket->readAll();
                    return;
                }
                QByteArray buffer = socket->property("driftBuffer").toByteArray() + socket->readAll();
                if (buffer.size() > kMaxRequestBytes) {
                    socket->abort();
                    return;
                }
                socket->setProperty("driftBuffer", buffer);
                const int end = buffer.indexOf("\r\n");
                if (end < 0 || !buffer.contains("\r\n\r\n"))
                    return;
                socket->setProperty("driftHandled", true);
                handleRedirect(buffer.left(end), socket);
            });
        }
    });

    QUrl auth(QStringLiteral("https://accounts.google.com/o/oauth2/v2/auth"));
    QUrlQuery query;
    query.addQueryItem(QStringLiteral("client_id"), kGoogleClientId);
    query.addQueryItem(QStringLiteral("redirect_uri"), m_redirectUri);
    query.addQueryItem(QStringLiteral("response_type"), QStringLiteral("code"));
    query.addQueryItem(QStringLiteral("scope"), QStringLiteral("openid email profile"));
    query.addQueryItem(QStringLiteral("code_challenge"), codeChallenge(m_verifier));
    query.addQueryItem(QStringLiteral("code_challenge_method"), QStringLiteral("S256"));
    query.addQueryItem(QStringLiteral("state"), m_state);
    query.addQueryItem(QStringLiteral("prompt"), QStringLiteral("select_account"));
    auth.setQuery(query);

    m_signInUrl = auth.toString(QUrl::FullyEncoded);
    setBusy(true);
    m_loopbackTimeout->start();
    // The sign-in keeps waiting either way: with no browser opened, the dialog offers the link to
    // paste into one, and the redirect still comes back to this computer.
    if (!openBrowser(auth))
        setError(tr("Could not open the web browser. Copy the link and paste it into your browser."));
}

bool AccountController::openBrowser(const QUrl &url)
{
    if (QDesktopServices::openUrl(url))
        return true;
#ifdef Q_OS_WIN
    // ShellExecute hands a URL to whatever app claims its host ("Apps for websites") before the
    // default browser. A broken claimant fails every link to that host with error 2: seen with a
    // leftover Windows Subsystem for Android that claimed accounts.google.com, so no app on that
    // computer could open Google sign-in. Starting the default browser directly skips that.
    wchar_t browser[MAX_PATH] = {};
    DWORD size = MAX_PATH;
    if (SUCCEEDED(AssocQueryStringW(ASSOCF_NONE, ASSOCSTR_EXECUTABLE, L"https", L"open", browser, &size))) {
        QString exe = QString::fromWCharArray(browser);
        // Old Edge registrations point at a launcher stub that does not take a URL.
        if (exe.contains(QLatin1String("LaunchWinApp.exe"), Qt::CaseInsensitive))
            exe = QStringLiteral("msedge.exe");
        if (QProcess::startDetached(exe, {url.toString(QUrl::FullyEncoded)}))
            return true;
    }
#endif
    return false;
}

void AccountController::copySignInUrl()
{
    if (m_signInUrl.isEmpty())
        return;
    if (auto *clipboard = QGuiApplication::clipboard())
        clipboard->setText(m_signInUrl);
}

void AccountController::cancelSignIn()
{
    if (!m_loopback)
        return;
    finishLoopback();
    setBusy(false);
    emit signInFinished(false);
}

void AccountController::finishLoopback()
{
    m_loopbackTimeout->stop();
    if (m_loopback) {
        m_loopback->close();
        m_loopback->deleteLater();
    }
    m_loopback.clear();
}

void AccountController::handleRedirect(const QByteArray &requestLine, QTcpSocket *socket)
{
    QString code;
    QString state;
    QString error;
    if (!parseRedirectRequest(requestLine, &code, &state, &error)) {
        // The browser also asks for /favicon.ico; it gets nothing and the server keeps waiting.
        socket->write("HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n");
        socket->disconnectFromHost();
        return;
    }
    if (state != m_state) {
        socket->write(pageFor(tr("Sign-in failed"), tr("This page is from an older attempt. Go back to Flip Studio and try again.")));
        socket->disconnectFromHost();
        return;
    }
    if (code.isEmpty()) {
        socket->write(pageFor(tr("Sign-in cancelled"), tr("You can close this tab and go back to Flip Studio.")));
        socket->disconnectFromHost();
        finishLoopback();
        setBusy(false);
        if (error != QLatin1String("access_denied"))
            setError(tr("Google did not complete the sign-in."));
        emit signInFinished(false);
        return;
    }
    socket->write(pageFor(tr("You are signed in"), tr("You can close this tab and go back to Flip Studio.")));
    socket->disconnectFromHost();
    finishLoopback();
    exchangeCode(code);
}

QUrl AccountController::apiUrl(const QString &path) const
{
    QString base = kApiBase;
    while (base.endsWith(QLatin1Char('/')))
        base.chop(1);
    return QUrl(base + path);
}

QNetworkReply *AccountController::postJson(const QString &path, const QByteArray &body, bool withAuth)
{
    QNetworkRequest request(apiUrl(path));
    request.setHeader(QNetworkRequest::ContentTypeHeader, QStringLiteral("application/json"));
    request.setRawHeader("Accept", "application/json");
    request.setTransferTimeout(kApiTimeoutMs);
    if (withAuth && !m_accessToken.isEmpty())
        request.setRawHeader("Authorization", "Bearer " + m_accessToken.toUtf8());
    return m_network->post(request, body);
}

void AccountController::exchangeCode(const QString &code)
{
    QJsonObject body;
    body.insert(QStringLiteral("code"), code);
    body.insert(QStringLiteral("codeVerifier"), m_verifier);
    body.insert(QStringLiteral("redirectUri"), m_redirectUri);
    body.insert(QStringLiteral("device"), QSysInfo::prettyProductName());
    m_verifier.clear();
    QNetworkReply *reply = postJson(QStringLiteral("/v1/auth/google"),
                                    QJsonDocument(body).toJson(QJsonDocument::Compact));
    connect(reply, &QNetworkReply::finished, this, [this, reply] {
        reply->deleteLater();
        setBusy(false);
        const QByteArray payload = reply->readAll();
        if (reply->error() != QNetworkReply::NoError) {
            const QString message =
                QJsonDocument::fromJson(payload).object().value(QStringLiteral("error")).toString();
            setError(message.isEmpty() ? tr("Could not reach Flip Studio. Check your connection and try again.")
                                       : message);
            emit signInFinished(false);
            return;
        }
        applySession(payload);
        dismissWelcome();
        emit signInFinished(true);
    });
}

void AccountController::applySession(const QByteArray &payload)
{
    const QJsonObject obj = QJsonDocument::fromJson(payload).object();
    const QString access = obj.value(QStringLiteral("accessToken")).toString();
    const QString refreshToken = obj.value(QStringLiteral("refreshToken")).toString();
    if (access.isEmpty() || refreshToken.isEmpty())
        return;
    m_accessToken = access;
    m_refreshToken = refreshToken;
    m_accessExpiresAt = QDateTime::currentSecsSinceEpoch()
        + qMax(60, obj.value(QStringLiteral("expiresIn")).toInt(900));
    const QJsonObject user = obj.value(QStringLiteral("user")).toObject();
    if (!user.isEmpty()) {
        m_name = user.value(QStringLiteral("name")).toString();
        m_email = user.value(QStringLiteral("email")).toString();
        m_avatarUrl = QUrl(user.value(QStringLiteral("avatar")).toString());
        const QDateTime created = QDateTime::fromString(
            user.value(QStringLiteral("createdAt")).toString(), Qt::ISODateWithMs);
        if (created.isValid())
            m_memberSince = created;
    }
    store();
    emit accountChanged();
    emit accessTokenChanged();
    emit needsWelcomeChanged();
}

void AccountController::refresh(const std::function<void(bool)> &then)
{
    if (then)
        m_refreshWaiters.append(then);
    if (m_refreshing)
        return;
    const auto finish = [this](bool ok) {
        m_refreshing = false;
        const auto waiters = std::exchange(m_refreshWaiters, {});
        for (const auto &w : waiters)
            w(ok);
    };
    // Another running copy may already have rotated the token; adopt what it stored.
    {
        QSettings settings;
        const QString stored = drift::secrets::readSecret(settings, key("refreshToken"));
        if (stored.isEmpty() && !m_refreshToken.isEmpty()) {
            // Signed out elsewhere.
            clearLocal();
            finish(false);
            return;
        }
        if (stored != m_refreshToken)
            loadStored();
    }
    if (!signedIn()) {
        finish(false);
        return;
    }
    if (QDateTime::currentSecsSinceEpoch() + kRefreshSkewSecs < m_accessExpiresAt
        && !m_accessToken.isEmpty() && !then) {
        // Timer-driven call with a token that is still good: nothing to do.
        finish(true);
        return;
    }
    m_refreshing = true;
    QJsonObject body;
    body.insert(QStringLiteral("refreshToken"), m_refreshToken);
    QNetworkReply *reply = postJson(QStringLiteral("/v1/auth/refresh"),
                                    QJsonDocument(body).toJson(QJsonDocument::Compact));
    connect(reply, &QNetworkReply::finished, this, [this, reply, finish] {
        reply->deleteLater();
        const int status = reply->attribute(QNetworkRequest::HttpStatusCodeAttribute).toInt();
        if (status == 401) {
            // The session was closed (signed out elsewhere, account deleted, or the token was
            // reused). Only a real 401 signs out; a network failure keeps the session.
            clearLocal();
            finish(false);
            return;
        }
        if (reply->error() != QNetworkReply::NoError) {
            finish(false);
            return;
        }
        applySession(reply->readAll());
        finish(true);
    });
}

void AccountController::signOut()
{
    if (!signedIn())
        return;
    const QString token = m_refreshToken;
    clearLocal();
    QJsonObject body;
    body.insert(QStringLiteral("refreshToken"), token);
    QNetworkReply *reply = postJson(QStringLiteral("/v1/auth/logout"),
                                    QJsonDocument(body).toJson(QJsonDocument::Compact));
    connect(reply, &QNetworkReply::finished, reply, &QObject::deleteLater);
}

void AccountController::deleteAccount()
{
    if (!signedIn() || m_busy)
        return;
    setError({});
    setBusy(true);
    refresh([this](bool ok) {
        if (!ok) {
            setBusy(false);
            setError(tr("Could not reach Flip Studio. Check your connection and try again."));
            return;
        }
        QNetworkRequest request(apiUrl(QStringLiteral("/v1/me")));
        request.setTransferTimeout(kApiTimeoutMs);
        request.setRawHeader("Authorization", "Bearer " + m_accessToken.toUtf8());
        QNetworkReply *reply = m_network->deleteResource(request);
        connect(reply, &QNetworkReply::finished, this, [this, reply] {
            reply->deleteLater();
            setBusy(false);
            if (reply->error() != QNetworkReply::NoError) {
                setError(tr("Could not delete the account. Try again later."));
                return;
            }
            clearLocal();
        });
    });
}

void AccountController::loadStored()
{
    QSettings settings;
    m_refreshToken = drift::secrets::readSecret(settings, key("refreshToken"));
    m_accessToken = drift::secrets::readSecret(settings, key("accessToken"));
    m_accessExpiresAt = settings.value(key("accessExpiresAt")).toLongLong();
    m_name = settings.value(key("name")).toString();
    m_email = settings.value(key("email")).toString();
    m_avatarUrl = settings.value(key("avatar")).toUrl();
    m_memberSince = settings.value(key("memberSince")).toDateTime();
}

void AccountController::store()
{
    QSettings settings;
    drift::secrets::writeSecret(settings, key("refreshToken"), m_refreshToken);
    drift::secrets::writeSecret(settings, key("accessToken"), m_accessToken);
    settings.setValue(key("accessExpiresAt"), m_accessExpiresAt);
    settings.setValue(key("name"), m_name);
    settings.setValue(key("email"), m_email);
    settings.setValue(key("avatar"), m_avatarUrl);
    settings.setValue(key("memberSince"), m_memberSince);
}

void AccountController::clearLocal()
{
    const bool was = signedIn();
    m_accessToken.clear();
    m_refreshToken.clear();
    m_accessExpiresAt = 0;
    m_name.clear();
    m_email.clear();
    m_avatarUrl.clear();
    m_memberSince = {};
    QSettings settings;
    for (const char *k : {"refreshToken", "accessToken", "accessExpiresAt", "name", "email", "avatar",
                          "memberSince"})
        settings.remove(key(k));
    if (was) {
        emit accountChanged();
        emit accessTokenChanged();
    }
}

void AccountController::setBusy(bool busy)
{
    if (m_busy == busy)
        return;
    m_busy = busy;
    emit busyChanged();
}

void AccountController::setError(const QString &error)
{
    if (m_error == error)
        return;
    m_error = error;
    emit errorChanged();
}
