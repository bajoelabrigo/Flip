#include "InstallStats.h"
#include "AccountController.h"
#include "engine/GpuPreference.h"

#include <QCoreApplication>
#include <QDate>
#include <QDir>
#include <QFileInfo>
#include <QJsonDocument>
#include <QJsonObject>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QNetworkRequest>
#include <QRegularExpression>
#include <QSettings>
#include <QSysInfo>
#include <QTimer>
#include <QUuid>

#ifndef DRIFT_ACCOUNT_API_URL
#define DRIFT_ACCOUNT_API_URL ""
#endif
#ifndef DRIFT_VERSION
#define DRIFT_VERSION "0"
#endif
#ifndef DRIFT_DISTRIBUTION
#define DRIFT_DISTRIBUTION "source"
#endif

namespace {

const QString kApiBase = QStringLiteral(DRIFT_ACCOUNT_API_URL);
const QString kVersion = QStringLiteral(DRIFT_VERSION);
const QString kDistribution = QStringLiteral(DRIFT_DISTRIBUTION);

// The first report waits for the editor to settle; it is never worth slowing the start for.
constexpr int kFirstReportDelayMs = 20 * 1000;

QString today()
{
    return QDate::currentDate().toString(Qt::ISODate);
}

} // namespace

InstallStats::InstallStats(AccountController *account, QObject *parent)
    : QObject(parent)
    , m_account(account)
    , m_network(new QNetworkAccessManager(this))
    , m_dailyTimer(new QTimer(this))
{
    // Hourly is enough to notice the day changed while the app stays open overnight.
    m_dailyTimer->setInterval(60 * 60 * 1000);
    connect(m_dailyTimer, &QTimer::timeout, this, &InstallStats::report);
}

bool InstallStats::available() const
{
    // Test runs (tools/e2e, CI) set FLIP_NO_STATS so they are not counted as installs.
    return !kApiBase.isEmpty() && !baseVersion(kVersion).isEmpty()
        && !qEnvironmentVariableIsSet("FLIP_NO_STATS");
}

bool InstallStats::enabled() const
{
    return QSettings().value(QStringLiteral("stats/enabled"), true).toBool();
}

void InstallStats::setEnabled(bool enabled)
{
    if (enabled == this->enabled())
        return;
    QSettings().setValue(QStringLiteral("stats/enabled"), enabled);
    emit enabledChanged();
    if (enabled)
        QTimer::singleShot(0, this, &InstallStats::report);
}

QString InstallStats::baseVersion(const QString &version)
{
    static const QRegularExpression re(QStringLiteral("^(\\d{1,4}\\.\\d{1,4}\\.\\d{1,4})(?:[-+].*)?$"));
    const QRegularExpressionMatch m = re.match(version.trimmed());
    return m.hasMatch() ? m.captured(1) : QString();
}

QString InstallStats::channel()
{
    if (kDistribution == QLatin1String("windows-store"))
        return QStringLiteral("store");
    if (kDistribution != QLatin1String("windows"))
        return QStringLiteral("unknown");
#ifdef Q_OS_WIN
    if (drift::gpu::packagedApp())
        return QStringLiteral("store");
#endif
    // The installer leaves its uninstaller next to the program; the portable zip has none.
    const QDir dir(QCoreApplication::applicationDirPath());
    return dir.exists(QStringLiteral("unins000.exe")) ? QStringLiteral("installer")
                                                     : QStringLiteral("portable");
}

InstallStats::Event InstallStats::decide(const QString &lastRunVersion, const QString &currentVersion,
                                         const QString &lastReportedDay, const QString &today)
{
    if (lastRunVersion.isEmpty())
        return {QStringLiteral("install"), {}};
    if (lastRunVersion != currentVersion)
        return {QStringLiteral("update"), lastRunVersion};
    if (lastReportedDay != today)
        return {QStringLiteral("active"), {}};
    return {};
}

void InstallStats::start()
{
    QSettings settings;
    const QString previous = settings.value(QStringLiteral("app/lastRunVersion")).toString();
    // Pending events survive in stats/pending* until the server confirms them, so an update made
    // offline is still reported later. Recording the version now keeps a later run from
    // reporting the same update twice.
    const QString current = baseVersion(kVersion);
    if (!current.isEmpty() && previous != current) {
        if (!settings.contains(QStringLiteral("stats/pendingFrom")))
            settings.setValue(QStringLiteral("stats/pendingFrom"),
                              previous.isEmpty() ? QStringLiteral("-") : previous);
        settings.setValue(QStringLiteral("app/lastRunVersion"), current);
    }
    if (!available())
        return;
    QTimer::singleShot(kFirstReportDelayMs, this, &InstallStats::report);
    m_dailyTimer->start();
}

void InstallStats::report()
{
    if (!available() || !enabled() || m_sending)
        return;
    QSettings settings;
    const QString current = baseVersion(kVersion);
    QString installId = settings.value(QStringLiteral("stats/installId")).toString();
    if (QUuid::fromString(installId).isNull()) {
        installId = QUuid::createUuid().toString(QUuid::WithoutBraces);
        settings.setValue(QStringLiteral("stats/installId"), installId);
    }

    // "-" in pendingFrom means the first run of a build that reports, with no earlier version.
    const QString pending = settings.value(QStringLiteral("stats/pendingFrom")).toString();
    const QString lastRun = pending.isEmpty() ? current : (pending == QLatin1String("-") ? QString() : pending);
    const Event event = decide(lastRun, current, settings.value(QStringLiteral("stats/lastReportedDay")).toString(),
                               today());
    if (event.type.isEmpty())
        return;

    QJsonObject body;
    body.insert(QStringLiteral("installId"), installId);
    body.insert(QStringLiteral("event"), event.type);
    body.insert(QStringLiteral("version"), current);
    if (!event.fromVersion.isEmpty())
        body.insert(QStringLiteral("fromVersion"), event.fromVersion);
    body.insert(QStringLiteral("os"), QSysInfo::prettyProductName().left(40));
    body.insert(QStringLiteral("channel"), channel());

    QString base = kApiBase;
    while (base.endsWith(QLatin1Char('/')))
        base.chop(1);
    QNetworkRequest request(QUrl(base + QStringLiteral("/v1/installs/event")));
    request.setHeader(QNetworkRequest::ContentTypeHeader, QStringLiteral("application/json"));
    request.setTransferTimeout(15000);
    if (m_account && !m_account->accessToken().isEmpty())
        request.setRawHeader("Authorization", "Bearer " + m_account->accessToken().toUtf8());

    m_sending = true;
    QNetworkReply *reply = m_network->post(request, QJsonDocument(body).toJson(QJsonDocument::Compact));
    const QString day = today();
    connect(reply, &QNetworkReply::finished, this, [this, reply, day] {
        reply->deleteLater();
        m_sending = false;
        const int status = reply->attribute(QNetworkRequest::HttpStatusCodeAttribute).toInt();
        // A 400 will not get better by retrying; drop the event rather than resend it forever.
        if (reply->error() != QNetworkReply::NoError && status != 400)
            return;
        QSettings settings;
        settings.remove(QStringLiteral("stats/pendingFrom"));
        settings.setValue(QStringLiteral("stats/lastReportedDay"), day);
    });
}
