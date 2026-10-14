import QtQuick
import Drift

// While a Google sign-in waits for the browser: copies the sign-in page's link, for when no
// browser window opened. Paste it into any browser on this computer and the sign-in completes.
ThemedButton {
    id: root

    property bool copied: false

    visible: Account.busy && Account.signInUrl.length > 0
    variant: "ghost"
    glyph: copied ? Theme.icons.check : Theme.icons.link
    text: copied ? qsTr("Link copied — paste it into your browser") : qsTr("Copy the link")
    tooltip: qsTr("If no browser window opened, paste this link into your browser to sign in.")
    onClicked: {
        Account.copySignInUrl()
        root.copied = true
    }

    Connections {
        target: Account
        function onBusyChanged() {
            root.copied = false
        }
    }
}
