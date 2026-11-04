import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift 1.0
import "components"

// «Remove silences», reviewed one by one as in CapCut: every pause and filler word it would take out
// of the clip, each with a tick (untick to keep it) and a click to hear it on the timeline. A window
// rather than a dialog so the timeline and the preview stay in sight while listening.
ToolWindow {
    id: root

    property int trackIndex: -1
    property int clipIndex: -1
    property double minPause: 0.6
    property bool fillers: true
    property var pieces: []
    property var ticked: [] // one bool per piece

    readonly property int tickedCount: ticked.filter(t => t).length
    readonly property double tickedSeconds: {
        let sum = 0
        for (let i = 0; i < pieces.length; i++) {
            if (ticked[i])
                sum += pieces[i].length
        }
        return sum
    }

    width: 460
    height: 560
    minimumWidth: 380
    minimumHeight: 420
    title: qsTr("Remove silences")
    color: Theme.appBackground

    function openFor(track, clip) {
        root.trackIndex = track
        root.clipIndex = clip
        refresh()
        root.show()
        root.raise()
        root.requestActivate()
    }

    function refresh() {
        const list = EditorState.silencePieces(root.trackIndex, root.clipIndex, root.minPause, root.fillers)
        root.pieces = list
        root.ticked = list.map(() => true)
    }

    function setTicked(index, value) {
        const next = root.ticked.slice()
        next[index] = value
        root.ticked = next
    }

    function timeLabel(seconds) {
        const m = Math.floor(seconds / 60)
        const s = seconds - m * 60
        return m + ":" + (s < 10 ? "0" : "") + s.toFixed(1)
    }

    // Plays a little before and after the piece, so it is heard in context.
    function listen(index) {
        const piece = root.pieces[index]
        EditorState.playheadSeconds = Math.max(0, piece.at - 0.6)
        EditorState.playing = true
        stopTimer.interval = Math.round((piece.length + 1.2) * 1000)
        stopTimer.restart()
    }

    Timer {
        id: stopTimer
        onTriggered: EditorState.playing = false
    }

    onClosing: {
        stopTimer.stop()
        if (EditorState.playing)
            EditorState.playing = false
    }

    Column {
        id: header
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: Theme.spacingLg
        spacing: Theme.spacingMd

        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            size: "sm"
            text: qsTr("Untick what you want to keep. Click a row to hear it.")
        }

        // How long a pause has to be to go, as CapCut's chips.
        Row {
            spacing: Theme.spacingSm
            ThemedLabel {
                anchors.verticalCenter: parent.verticalCenter
                size: "sm"
                text: qsTr("Pauses longer than")
            }
            Repeater {
                model: [0.4, 0.6, 1.0, 1.5]
                ThemedButton {
                    required property var modelData
                    text: Number(modelData).toLocaleString(Qt.locale(), "f", 1) + " s"
                    variant: Math.abs(root.minPause - modelData) < 0.01 ? "secondary" : "ghost"
                    onClicked: {
                        root.minPause = modelData
                        root.refresh()
                    }
                }
            }
        }

        ThemedCheckBox {
            width: parent.width
            text: qsTr("Also filler words (eh, mmm)")
            checked: root.fillers
            onToggled: {
                root.fillers = checked
                root.refresh()
            }
        }
    }

    ListView {
        id: list
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: header.bottom
        anchors.bottom: footer.top
        anchors.margins: Theme.spacingLg
        clip: true
        spacing: 2
        model: root.pieces.length
        ScrollBar.vertical: AppScrollBar { }

        delegate: Rectangle {
            id: row
            required property int index
            readonly property var piece: root.pieces[index]
            width: list.width
            height: 40
            radius: Theme.radiusMd
            color: rowMouse.containsMouse ? Theme.panelBackground : "transparent"

            MouseArea {
                id: rowMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: root.listen(row.index)
            }

            Row {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingSm
                anchors.rightMargin: Theme.spacingSm
                spacing: Theme.spacingMd

                ThemedCheckBox {
                    anchors.verticalCenter: parent.verticalCenter
                    checked: root.ticked[row.index] === true
                    onToggled: root.setTicked(row.index, checked)
                }
                ThemedLabel {
                    anchors.verticalCenter: parent.verticalCenter
                    width: 56
                    size: "sm"
                    text: root.timeLabel(row.piece.at)
                }
                ThemedLabel {
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width - 56 - 120 - 3 * Theme.spacingMd
                    elide: Text.ElideRight
                    size: "sm"
                    tone: root.ticked[row.index] ? "default" : "muted"
                    text: row.piece.filler ? "«" + row.piece.text + "»" : qsTr("Pause")
                }
                ThemedLabel {
                    anchors.verticalCenter: parent.verticalCenter
                    width: 44
                    horizontalAlignment: Text.AlignRight
                    size: "sm"
                    text: Number(row.piece.length).toLocaleString(Qt.locale(), "f", 1) + " s"
                }
                IconButton {
                    anchors.verticalCenter: parent.verticalCenter
                    glyph: Theme.icons.play
                    tooltip: qsTr("Listen")
                    onClicked: root.listen(row.index)
                }
            }
        }

        ThemedLabel {
            anchors.centerIn: parent
            visible: root.pieces.length === 0
            width: parent.width
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            size: "sm"
            text: qsTr("No pauses this long in the clip.")
        }
    }

    Item {
        id: footer
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: Theme.spacingLg
        height: buttons.height

        ThemedLabel {
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            size: "sm"
            text: qsTr("%1 of %2 · %3 s").arg(root.tickedCount).arg(root.pieces.length)
                      .arg(Number(root.tickedSeconds).toLocaleString(Qt.locale(), "f", 1))
        }

        Row {
            id: buttons
            anchors.right: parent.right
            spacing: Theme.spacingMd

            ThemedButton {
                variant: "ghost"
                text: qsTr("Cancel")
                onClicked: root.close()
            }
            ThemedButton {
                variant: "primary"
                text: qsTr("Remove")
                enabled: root.tickedCount > 0
                onClicked: {
                    const chosen = root.pieces.filter((p, i) => root.ticked[i])
                    stopTimer.stop()
                    EditorState.playing = false
                    EditorState.removeSilencePieces(root.trackIndex, root.clipIndex, chosen)
                    root.close()
                }
            }
        }
    }
}
