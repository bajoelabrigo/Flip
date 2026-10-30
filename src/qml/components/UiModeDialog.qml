import QtQuick
import QtQuick.Controls.Basic
import Drift

// First run of a new install (0.27, Jorge): Simple, like CapCut, or Pro, with the After Effects
// tools. Asked once, after the language; the header's Simple | Pro switch changes it any time.
ThemedDialog {
    id: root

    title: qsTr("How do you want to start?")
    acceptText: qsTr("Simple")
    rejectText: qsTr("Pro")
    rejectVariant: "secondary"
    preferredWidth: 480
    // The choice matters, and both buttons are a choice: no closing by clicking away.
    closePolicy: Popup.NoAutoClose

    onAccepted: EditorState.preferences.setProMode(false)
    onRejected: EditorState.preferences.setProMode(true)

    contentItem: Column {
        spacing: Theme.spacingXl
        width: parent ? parent.width : 440

        ThemedLabel {
            width: parent.width
            size: "base"
            tone: "default"
            wrapMode: Text.WordWrap
            text: qsTr("Simple: the essentials, like CapCut. Cut, titles, music, effects, filters and export, without the advanced tools in the way.")
        }
        ThemedLabel {
            width: parent.width
            size: "base"
            tone: "default"
            wrapMode: Text.WordWrap
            text: qsTr("Pro: everything, with the After Effects tools too (pen, Motion Tools, curves, parenting, mattes).")
        }
        ThemedLabel {
            width: parent.width
            size: "sm"
            tone: "muted"
            wrapMode: Text.WordWrap
            text: qsTr("You can switch any time with Simple | Pro at the top. Nothing in your projects is lost.")
        }
    }
}
