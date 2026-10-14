import QtQuick
import QtQuick.Controls.Basic
import Drift

// First launch, after the language: sign in with Google or continue without an account. Shown
// once (Account.needsWelcome); Settings › Account offers sign-in afterwards.
ThemedDialog {
    id: root

    title: qsTr("Welcome to Flip Studio")
    showFooter: false
    preferredWidth: Theme.dialogWidthSm
    closePolicy: Popup.NoAutoClose

    Connections {
        target: Account
        function onSignInFinished(ok) {
            if (ok)
                root.close()
        }
    }

    contentItem: Column {
        spacing: Theme.spacingXl
        width: parent ? parent.width : 360

        ThemedLabel {
            width: parent.width
            size: "sm"
            wrapMode: Text.WordWrap
            text: qsTr("Sign in with your Google account to search free photos and videos from Pexels and Pixabay right inside the editor. Your account will also hold your templates and your store.")
        }

        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            text: qsTr("You can also continue without an account: editing works exactly the same.")
        }

        ThemedButton {
            width: parent.width
            variant: "primary"
            glyph: Account.busy ? Theme.icons.spinner : Theme.icons.brandGoogle
            text: Account.busy ? qsTr("Waiting for the browser…") : qsTr("Sign in with Google")
            enabled: !Account.busy
            onClicked: Account.signIn()
        }

        ThemedLabel {
            width: parent.width
            visible: Account.busy
            wrapMode: Text.WordWrap
            text: qsTr("Choose your account in the browser window that opened, then come back here.")
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
            text: Account.busy ? qsTr("Cancel") : qsTr("Continue without an account")
            onClicked: {
                if (Account.busy) {
                    Account.cancelSignIn()
                    return
                }
                root.close()
            }
        }

        Rectangle {
            width: parent.width
            height: Theme.borderWidth
            color: Theme.panelBorder
            visible: UsageStats.available
        }

        Column {
            width: parent.width
            spacing: Theme.spacingSm
            visible: UsageStats.available

            ThemedSwitch {
                width: parent.width
                checked: UsageStats.enabled
                text: qsTr("Send anonymous usage statistics")
                onToggled: UsageStats.enabled = checked
            }

            ThemedLabel {
                width: parent.width
                wrapMode: Text.WordWrap
                textFormat: Text.StyledText
                linkColor: Theme.primary
                text: qsTr("Only the version, the Windows edition and a random install number, to count installs and updates. Never your projects or files. <a href=\"https://getflipstudio.com/privacidad.html\">Privacy policy</a>")
                onLinkActivated: (link) => Qt.openUrlExternally(link)
            }
        }
    }
}
