import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// Motion Tools › Trim (0.26, Jorge: as the Trim-Pack script): one click animates the Trim Paths of
// the selected shapes, and the strokes of the selected texts. Settings as Trim-Pack's: how many
// frames, how far the offset turns and how many copies; its Alt and Shift keys are the two
// switches (draw from the other end, turn the offset too).
Column {
    id: root

    property int frames: 20
    property real offsetRange: 180
    property int copies: 4
    property bool reverse: false
    property bool animateOffset: false

    function run(mode) {
        EditorState.applyTrimPack(mode, root.frames, root.offsetRange, root.copies, root.reverse, root.animateOffset)
    }

    spacing: Theme.spacingMd

    ThemedLabel {
        width: parent.width
        wrapMode: Text.WordWrap
        size: "sm"
        opacity: 0.8
        text: qsTr("Select shapes or texts with a stroke. Each button writes the keys from the playhead; Out ends at the end of the clip.")
    }

    Grid {
        width: parent.width
        columns: 3
        columnSpacing: Theme.spacingSm
        rowSpacing: 2
        ThemedLabel { text: qsTr("Frames") }
        ThemedLabel { text: qsTr("Offset range") }
        ThemedLabel { text: qsTr("Copies") }
        ThemedNumberField {
            width: (root.width - 2 * Theme.spacingSm) / 3
            from: 1; to: 600; step: 1
            value: root.frames
            onEdited: v => root.frames = Math.round(v)
        }
        ThemedNumberField {
            width: (root.width - 2 * Theme.spacingSm) / 3
            from: -3600; to: 3600; step: 15; unit: "°"
            value: root.offsetRange
            onEdited: v => root.offsetRange = v
        }
        ThemedNumberField {
            width: (root.width - 2 * Theme.spacingSm) / 3
            from: 1; to: 12; step: 1
            value: root.copies
            onEdited: v => root.copies = Math.round(v)
        }
    }

    ThemedSwitch {
        width: parent.width
        text: qsTr("Reverse direction")
        tooltip: qsTr("Draw from the other end of the path")
        checked: root.reverse
        onToggled: root.reverse = checked
    }
    ThemedSwitch {
        width: parent.width
        text: qsTr("Turn the offset too")
        tooltip: qsTr("The line also travels round the path by the offset range")
        checked: root.animateOffset
        onToggled: root.animateOffset = checked
    }

    component TrimButton: ThemedButton {
        property string mode: ""
        width: (root.width - 2 * Theme.spacingSm) / 3
        onClicked: root.run(mode)
    }

    ThemedLabel { text: qsTr("Draw"); opacity: 0.7 }
    Flow {
        width: parent.width
        spacing: Theme.spacingSm
        TrimButton { mode: "in"; text: qsTr("In"); tooltip: qsTr("The line draws on") }
        TrimButton { mode: "out"; text: qsTr("Out"); tooltip: qsTr("The line draws off, ending with the clip") }
        TrimButton { mode: "inout"; text: qsTr("In & Out"); tooltip: qsTr("Draws on from the playhead and off at the end") }
        TrimButton { mode: "centerIn"; text: qsTr("From centre"); tooltip: qsTr("Grows both ways from the middle of the path") }
        TrimButton { mode: "centerOut"; text: qsTr("To centre"); tooltip: qsTr("Shrinks into the middle of the path, ending with the clip") }
        TrimButton { mode: "swap"; text: qsTr("Swap"); tooltip: qsTr("The keys already there run from the other end") }
    }

    ThemedLabel { text: qsTr("Copies and trace"); opacity: 0.7 }
    Flow {
        width: parent.width
        spacing: Theme.spacingSm
        TrimButton { mode: "copies"; text: qsTr("Copies"); tooltip: qsTr("Copies above, each one drawing on a little later") }
        TrimButton { mode: "traceIn"; text: qsTr("Trace In"); tooltip: qsTr("A short line runs ahead while it draws on") }
        TrimButton { mode: "traceOut"; text: qsTr("Trace Out"); tooltip: qsTr("A short line runs off as it ends") }
        TrimButton { mode: "traceInOut"; text: qsTr("Trace I&O"); tooltip: qsTr("A trace on the way in and on the way out") }
        ThemedButton {
            width: (root.width - 2 * Theme.spacingSm) / 3
            text: qsTr("Convert")
            tooltip: qsTr("A text or shape into an editable path, so it can be trimmed letter by letter")
            onClicked: EditorState.convertSelectionToShape()
        }
        TrimButton { mode: "clear"; text: qsTr("Clear"); variant: "ghost"; tooltip: qsTr("Take the Trim Paths animation off") }
    }
}
