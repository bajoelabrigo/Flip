import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// Motion Tools › Bend (0.26, Jorge: as the Bend Layers script): bends the selected layers into an
// arc with the "ae.bend" effect — across or along, from a point that stays put — and animates it
// unbending in or bending out.
Column {
    id: root

    property real degrees: 90
    property bool vertical: false
    property real pivot: 50
    property int frames: 20

    spacing: Theme.spacingMd

    ThemedLabel {
        width: parent.width
        wrapMode: Text.WordWrap
        size: "sm"
        opacity: 0.8
        text: qsTr("Select the layers. Positive bends the ends up into an arch, negative down; a full 360° rolls it into a ring.")
    }

    Row {
        width: parent.width
        spacing: Theme.spacingSm
        ThemedLabel { width: 72; anchors.verticalCenter: parent.verticalCenter; text: qsTr("Bend") }
        ThemedSlider {
            id: bendSlider
            width: parent.width - 72 - bendField.width - 2 * parent.spacing
            anchors.verticalCenter: parent.verticalCenter
            from: -360; to: 360; stepSize: 1
            value: root.degrees
            valueFormatter: v => Math.round(v) + "°"
            onMoved: root.degrees = Math.round(value)
        }
        ThemedNumberField {
            id: bendField
            width: 64
            from: -360; to: 360; step: 5; unit: "°"
            value: root.degrees
            onEdited: v => root.degrees = v
        }
    }
    Row {
        width: parent.width
        spacing: Theme.spacingSm
        ThemedLabel { width: 72; anchors.verticalCenter: parent.verticalCenter; text: qsTr("Fixed point") }
        ThemedSlider {
            width: parent.width - 72 - 64 - 2 * parent.spacing
            anchors.verticalCenter: parent.verticalCenter
            from: 0; to: 100; stepSize: 1
            value: root.pivot
            valueFormatter: v => Math.round(v) + " %"
            onMoved: root.pivot = Math.round(value)
        }
        ThemedLabel {
            width: 64
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: Text.AlignRight
            text: root.pivot === 0 ? qsTr("Start") : root.pivot === 100 ? qsTr("End")
                  : root.pivot === 50 ? qsTr("Centre") : Math.round(root.pivot) + " %"
        }
    }
    ThemedSwitch {
        width: parent.width
        text: qsTr("Along the height")
        tooltip: qsTr("Bend the layer top to bottom instead of side to side")
        checked: root.vertical
        onToggled: root.vertical = checked
    }

    Flow {
        width: parent.width
        spacing: Theme.spacingSm
        Repeater {
            model: [
                { label: qsTr("Arch"), deg: 90 },
                { label: qsTr("Smile"), deg: -90 },
                { label: qsTr("Half ring"), deg: 180 },
                { label: qsTr("Ring"), deg: 360 }
            ]
            ThemedButton {
                required property var modelData
                width: (root.width - 3 * Theme.spacingSm) / 4
                text: modelData.label
                onClicked: {
                    root.degrees = modelData.deg
                    EditorState.applyBend("set", root.degrees, root.vertical, root.pivot, root.frames)
                }
            }
        }
    }

    Row {
        width: parent.width
        spacing: Theme.spacingSm
        ThemedLabel { anchors.verticalCenter: parent.verticalCenter; text: qsTr("Frames") }
        ThemedNumberField {
            width: 64
            from: 1; to: 600; step: 1
            value: root.frames
            onEdited: v => root.frames = Math.round(v)
        }
    }
    Flow {
        width: parent.width
        spacing: Theme.spacingSm
        ThemedButton {
            width: (root.width - 3 * Theme.spacingSm) / 4
            text: qsTr("Bend")
            tooltip: qsTr("Bend it this much (a key at the playhead if the bend is animated)")
            onClicked: EditorState.applyBend("set", root.degrees, root.vertical, root.pivot, root.frames)
        }
        ThemedButton {
            width: (root.width - 3 * Theme.spacingSm) / 4
            text: qsTr("Unbend in")
            tooltip: qsTr("Starts bent and straightens out from the playhead")
            onClicked: EditorState.applyBend("in", root.degrees, root.vertical, root.pivot, root.frames)
        }
        ThemedButton {
            width: (root.width - 3 * Theme.spacingSm) / 4
            text: qsTr("Bend out")
            tooltip: qsTr("Bends away at the end of the clip")
            onClicked: EditorState.applyBend("out", root.degrees, root.vertical, root.pivot, root.frames)
        }
        ThemedButton {
            width: (root.width - 3 * Theme.spacingSm) / 4
            text: qsTr("Remove")
            variant: "ghost"
            onClicked: EditorState.applyBend("remove", 0, root.vertical, root.pivot, root.frames)
        }
    }
}
