#include "models/AccountController.h"
#include "models/InstallStats.h"

#include <QDir>
#include <QRegularExpression>
#include <QSettings>
#include <QStandardPaths>
#include <QtTest>

class TestAccount : public QObject
{
    Q_OBJECT

private slots:
    void initTestCase()
    {
        QStandardPaths::setTestModeEnabled(true);
        QCoreApplication::setOrganizationName(QStringLiteral("Flip Studio Tests"));
        QCoreApplication::setApplicationName(QStringLiteral("tst_account"));
        QSettings().clear();
    }

    void cleanupTestCase() { QSettings().clear(); }

    // RFC 7636, appendix B.
    void pkceChallengeMatchesTheRfcExample()
    {
        QCOMPARE(AccountController::codeChallenge(QStringLiteral("dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk")),
                 QStringLiteral("E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"));
    }

    void codeVerifierIsLongRandomAndUrlSafe()
    {
        const QString a = AccountController::makeCodeVerifier();
        const QString b = AccountController::makeCodeVerifier();
        QVERIFY(a != b);
        QVERIFY(a.size() >= 43 && a.size() <= 128);
        QVERIFY(QRegularExpression(QStringLiteral("^[A-Za-z0-9_-]+$")).match(a).hasMatch());
    }

    void redirectRequestIsParsed()
    {
        QString code, state, error;
        QVERIFY(AccountController::parseRedirectRequest("GET /?state=abc&code=4%2F0Ad-x HTTP/1.1", &code, &state, &error));
        QCOMPARE(code, QStringLiteral("4/0Ad-x"));
        QCOMPARE(state, QStringLiteral("abc"));
        QVERIFY(error.isEmpty());

        QVERIFY(AccountController::parseRedirectRequest("GET /?error=access_denied&state=abc HTTP/1.1", &code, &state, &error));
        QVERIFY(code.isEmpty());
        QCOMPARE(error, QStringLiteral("access_denied"));

        // The browser's other requests are not the redirect.
        QVERIFY(!AccountController::parseRedirectRequest("GET /favicon.ico HTTP/1.1", &code, &state, &error));
        QVERIFY(!AccountController::parseRedirectRequest("POST /?code=x HTTP/1.1", &code, &state, &error));
        QVERIFY(!AccountController::parseRedirectRequest("garbage", &code, &state, &error));
    }

    // This test target is built without an API URL: no service, so no prompt and no sign-in.
    void withoutServiceThereIsNoWelcome()
    {
        AccountController account;
        QVERIFY(!account.available());
        QVERIFY(!account.signedIn());
        QVERIFY(!account.needsWelcome());
        QVERIFY(account.accessToken().isEmpty());
    }

    void installEventDecision()
    {
        using E = InstallStats::Event;
        E e = InstallStats::decide({}, QStringLiteral("0.9.9"), {}, QStringLiteral("2026-10-14"));
        QCOMPARE(e.type, QStringLiteral("install"));

        e = InstallStats::decide(QStringLiteral("0.9.8"), QStringLiteral("0.9.9"), QStringLiteral("2026-10-14"), QStringLiteral("2026-10-14"));
        QCOMPARE(e.type, QStringLiteral("update"));
        QCOMPARE(e.fromVersion, QStringLiteral("0.9.8"));

        e = InstallStats::decide(QStringLiteral("0.9.9"), QStringLiteral("0.9.9"), QStringLiteral("2026-10-13"), QStringLiteral("2026-10-14"));
        QCOMPARE(e.type, QStringLiteral("active"));

        // Already reported today: nothing.
        e = InstallStats::decide(QStringLiteral("0.9.9"), QStringLiteral("0.9.9"), QStringLiteral("2026-10-14"), QStringLiteral("2026-10-14"));
        QVERIFY(e.type.isEmpty());
    }

    void baseVersionStripsBuildSuffixes()
    {
        QCOMPARE(InstallStats::baseVersion(QStringLiteral("0.9.9")), QStringLiteral("0.9.9"));
        QCOMPARE(InstallStats::baseVersion(QStringLiteral("0.10.0-nightly.12")), QStringLiteral("0.10.0"));
        QVERIFY(InstallStats::baseVersion(QStringLiteral("dev")).isEmpty());
        QVERIFY(InstallStats::baseVersion(QStringLiteral("0.9")).isEmpty());
    }

    void statisticsAreOnByDefaultAndCanBeTurnedOff()
    {
        InstallStats stats(nullptr);
        QVERIFY(!stats.available()); // no API URL in this target
        QVERIFY(stats.enabled());
        QSignalSpy spy(&stats, &InstallStats::enabledChanged);
        stats.setEnabled(false);
        QVERIFY(!stats.enabled());
        QVERIFY(!QSettings().value(QStringLiteral("stats/enabled")).toBool());
        QCOMPARE(spy.count(), 1);
        stats.setEnabled(false);
        QCOMPARE(spy.count(), 1);
        stats.setEnabled(true);
    }

    // The first run of a reporting build remembers an update even if it cannot be sent yet.
    void startRecordsTheVersionChange()
    {
        QSettings().setValue(QStringLiteral("app/lastRunVersion"), QStringLiteral("0.9.8"));
        QSettings().remove(QStringLiteral("stats/pendingFrom"));
        InstallStats stats(nullptr);
        stats.start();
        QCOMPARE(QSettings().value(QStringLiteral("app/lastRunVersion")).toString(), QStringLiteral("0.9.9"));
        QCOMPARE(QSettings().value(QStringLiteral("stats/pendingFrom")).toString(), QStringLiteral("0.9.8"));
        // A second start of the same version does not overwrite what is pending.
        InstallStats again(nullptr);
        again.start();
        QCOMPARE(QSettings().value(QStringLiteral("stats/pendingFrom")).toString(), QStringLiteral("0.9.8"));
    }

    void channelOfAZipCopyIsPortable()
    {
        // DRIFT_DISTRIBUTION is "windows" here and the test has no unins000.exe beside it.
        if (QDir(QCoreApplication::applicationDirPath()).exists(QStringLiteral("unins000.exe")))
            QSKIP("installed next to an uninstaller");
        QCOMPARE(InstallStats::channel(), QStringLiteral("portable"));
    }
};

QTEST_GUILESS_MAIN(TestAccount)
#include "tst_account.moc"
