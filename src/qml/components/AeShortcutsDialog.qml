import QtQuick
import QtQuick.Controls.Basic
import Drift

// The first time Pro is turned on (0.30, Jorge): After Effects' keys for the timeline, or Flip's own.
// Asked once; Preferences › Shortcuts changes it any time, and keys the user set stay theirs.
ThemedDialog {
    id: root

    title: qsTr("Use After Effects' shortcuts?")
    acceptText: qsTr("Use After Effects'")
    rejectText: qsTr("Keep Flip's")
    rejectVariant: "secondary"
    preferredWidth: 480

    onAccepted: EditorState.setShortcutPreset("afterEffects")

    contentItem: Column {
        spacing: Theme.spacingXl
        width: parent ? parent.width : 440

        ThemedLabel {
            width: parent.width
            size: "base"
            tone: "default"
            wrapMode: Text.WordWrap
            text: qsTr("J and K go to the previous and next keyframe, P, S, R, T and A show one property, U and UU what is animated or changed, B and N set the work area, I and O go to the layer's ends, [ ] and Alt+[ ] move and trim the layer at the playhead.")
        }
        ThemedLabel {
            width: parent.width
            size: "sm"
            tone: "muted"
            wrapMode: Text.WordWrap
            text: qsTr("You can switch any time in Preferences › Shortcuts. Shortcuts you changed yourself stay as they are.")
        }
    }
}
