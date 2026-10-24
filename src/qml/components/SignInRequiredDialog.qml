import QtQuick
import QtQuick.Controls.Basic
import Drift

// Exporting asks for a signed-in account (Jorge, 2026-10-18), and so does Stock. Everything stays
// free: the dialog says so before anything else, then offers Google sign-in. Once signed in it
// closes and runs what was asked for (the Export dialog opens by itself).
ThemedDialog {
    id: root

    // What to do once signed in; null to just close.
    property var afterSignIn: null
    // What asked: "export", or "trends" (a trending animation picked while signed out).
    property string reason: "export"

    title: root.reason === "trends" ? qsTr("Sign in to use what's trending")
         : root.reason === "voices" ? qsTr("Sign in to use this voice")
         : qsTr("Sign in to export")
    showFooter: false
    preferredWidth: Theme.dialogWidthSm

    function openFor(action) {
        root.afterSignIn = action || null
        root.open()
    }

    function finish() {
        const action = root.afterSignIn
        root.afterSignIn = null
        root.close()
        if (action)
            action()
    }

    Connections {
        target: Account
        function onSignInFinished(ok) {
            if (ok && root.visible)
                root.finish()
        }
    }

    onRejected: {
        root.afterSignIn = null
        if (Account.busy)
            Account.cancelSignIn()
    }

    contentItem: Column {
        spacing: Theme.spacingXl
        width: parent ? parent.width : 360

        Row {
            width: parent.width
            spacing: Theme.spacingMd

            IconGlyph {
                anchors.verticalCenter: parent.verticalCenter
                glyph: Theme.icons.gem
                iconSize: Theme.iconSizeLg
                iconColor: Theme.primary
            }

            ThemedLabel {
                width: parent.width - Theme.iconSizeLg - Theme.spacingMd
                anchors.verticalCenter: parent.verticalCenter
                size: "sm"
                tone: "default"
                font.weight: Font.DemiBold
                wrapMode: Text.WordWrap
                text: qsTr("Flip Studio is free: exporting, Stock and every template cost nothing.")
            }
        }

        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            text: root.reason === "trends"
                  ? qsTr("Trending animations are for signed-in users. You only need to sign in with your Google account: it takes a moment, it is done once, and your project stays just as it is.")
                  : root.reason === "voices"
                  ? qsTr("The voices with the flame are for signed-in users. You only need to sign in with your Google account: it takes a moment, it is done once, and your project stays just as it is.")
                  : qsTr("To export your video you only need to sign in with your Google account. It takes a moment, it is done once, and your project stays just as it is.")
        }

        ThemedButton {
            width: parent.width
            variant: "primary"
            glyph: Account.busy ? Theme.icons.spinner : Theme.icons.brandGoogle
            text: Account.busy ? qsTr("Waiting for the browser…") : qsTr("Sign in with Google")
            enabled: Account.available && !Account.busy
            onClicked: Account.signIn()
        }

        ThemedLabel {
            width: parent.width
            visible: Account.busy
            wrapMode: Text.WordWrap
            text: qsTr("Choose your account in the browser window that opened, then come back here.")
        }

        CopySignInLinkButton {
            width: parent.width
        }

        ThemedLabel {
            width: parent.width
            visible: Account.error.length > 0
            color: Theme.destructive
            wrapMode: Text.WordWrap
            text: Account.error
        }

        ThemedButton {
            width: parent.width
            variant: "secondary"
            text: Account.busy ? qsTr("Cancel") : qsTr("Not now")
            onClicked: {
                if (Account.busy) {
                    Account.cancelSignIn()
                    return
                }
                root.afterSignIn = null
                root.close()
            }
        }
    }
}
