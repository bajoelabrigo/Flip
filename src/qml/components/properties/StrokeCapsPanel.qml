import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// Motion Tools › Caps (0.26, Jorge: as the ButtCapper script): the Line Cap and Line Join of every
// stroke of the selected shapes and texts, in one click. Each button draws what it does.
Column {
    id: root

    property int revision: 0
    readonly property var capsState: {
        void root.revision
        void EditorState.selectedClip
        void EditorState.tracksRevision
        return EditorState.strokeCapsState() || {}
    }

    spacing: Theme.spacingMd

    ThemedLabel {
        width: parent.width
        wrapMode: Text.WordWrap
        size: "sm"
        opacity: 0.8
        text: (root.capsState.strokes || 0) > 0
              ? qsTr("%n stroke(s) in the selection.", "", root.capsState.strokes)
              : qsTr("Select shapes or texts with a stroke.")
    }

    // A thick stroke ending, or turning a corner, the way the option draws it.
    component CapButton: Rectangle {
        id: cb
        property string cap: ""
        property string join: ""
        property string label: ""
        readonly property bool current: cap.length > 0 ? root.capsState.cap === cap : root.capsState.join === join
        width: (root.width - 2 * Theme.spacingSm) / 3
        height: 64
        radius: Theme.radiusSm
        color: area.containsMouse ? Theme.panelAccent : Theme.panelBackground
        border.width: current ? Theme.borderWidthFocus : Theme.borderWidth
        border.color: current ? Theme.primary : Theme.panelBorder
        Canvas {
            id: drawing
            anchors.top: parent.top
            anchors.topMargin: 6
            anchors.horizontalCenter: parent.horizontalCenter
            width: 56
            height: 32
            onPaint: {
                const ctx = getContext("2d")
                ctx.reset()
                ctx.strokeStyle = Theme.primary
                ctx.lineWidth = 12
                ctx.lineCap = cb.cap.length > 0 ? cb.cap : "round"
                ctx.lineJoin = cb.join.length > 0 ? cb.join : "round"
                ctx.beginPath()
                if (cb.cap.length > 0) {
                    ctx.moveTo(10, 16)
                    ctx.lineTo(40, 16)
                } else {
                    ctx.moveTo(10, 26)
                    ctx.lineTo(28, 8)
                    ctx.lineTo(46, 26)
                }
                ctx.stroke()
                if (cb.cap.length > 0) {
                    // Where the path really ends: the cap is what reaches past it.
                    ctx.strokeStyle = Theme.panelForeground
                    ctx.lineWidth = 1
                    ctx.beginPath()
                    ctx.moveTo(40, 4)
                    ctx.lineTo(40, 28)
                    ctx.stroke()
                }
            }
        }
        ThemedLabel {
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 4
            anchors.horizontalCenter: parent.horizontalCenter
            text: cb.label
        }
        MouseArea {
            id: area
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: {
                EditorState.setStrokeCaps(cb.cap, cb.join)
                root.revision++
            }
        }
    }

    ThemedLabel { text: qsTr("Line cap"); opacity: 0.7 }
    Row {
        spacing: Theme.spacingSm
        CapButton { cap: "butt"; label: qsTr("Butt") }
        CapButton { cap: "round"; label: qsTr("Round") }
        CapButton { cap: "square"; label: qsTr("Square") }
    }
    ThemedLabel { text: qsTr("Line join"); opacity: 0.7 }
    Row {
        spacing: Theme.spacingSm
        CapButton { join: "miter"; label: qsTr("Miter") }
        CapButton { join: "round"; label: qsTr("Round") }
        CapButton { join: "bevel"; label: qsTr("Bevel") }
    }
}
