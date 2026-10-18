import QtQuick
import QtQuick.Controls.Basic
import Drift

// The "IA" mark beside a feature that runs an AI model, with a "?" that explains it on hover, as
// Filmora marks its AI tools (Jorge, 2026-10-18). Ours says what Filmora's cannot: it runs on this
// computer, without internet, so the video never leaves it.
Row {
    id: root

    // What this feature does with AI, one sentence; the local-and-offline line is added below it.
    property string info: ""
    // Just the "IA" letters (tight spots: toolbar buttons, page tabs). Hovering them shows the same
    // explanation unless the host already does (showTip false, as the toolbar's own tooltip).
    property bool compact: false
    property bool showTip: true

    readonly property string fullInfo: (root.info.length > 0 ? root.info + "\n\n" : "")
        + qsTr("Runs with AI on your computer, without internet: your video never leaves it.")

    spacing: 4

    Rectangle {
        id: help
        visible: !root.compact
        anchors.verticalCenter: parent.verticalCenter
        width: 14
        height: 14
        radius: 7
        color: "transparent"
        border.width: 1
        border.color: helpHover.hovered ? Theme.foreground : Theme.mutedForeground
        Text {
            anchors.centerIn: parent
            text: "?"
            color: helpHover.hovered ? Theme.foreground : Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: 9
            font.weight: Font.Bold
        }
        HoverHandler { id: helpHover }
        ThemedToolTip {
            text: root.fullInfo
            visible: helpHover.hovered
            delay: 150
        }
    }

    Text {
        id: mark
        anchors.verticalCenter: parent.verticalCenter
        text: qsTr("AI")
        color: Theme.primary
        font.family: Theme.fontFamily
        font.pixelSize: root.compact ? 8 : Theme.fontSizeXs
        font.weight: Font.Black
        font.italic: true

        HoverHandler { id: markHover; enabled: root.compact && root.showTip }
        ThemedToolTip {
            text: root.fullInfo
            visible: root.compact && root.showTip && markHover.hovered
            delay: 150
        }
    }

    Accessible.role: Accessible.StaticText
    Accessible.name: qsTr("AI") + ". " + root.fullInfo
}
