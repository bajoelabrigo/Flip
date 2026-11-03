import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift 1.0
import "components"

// Editing the video by its text, as Descript: the clip's words in reading order; a click strikes a
// word out (Shift + click, everything since the last one), a double click plays it, and «Cut» takes
// the struck words out of the video in one undo step. A window, so the preview stays in sight.
ToolWindow {
    id: root

    property int trackIndex: -1
    property int clipIndex: -1
    property var words: []
    property var struck: [] // one bool per word
    property int lastClicked: -1
    // The clip is being listened to first: the window is open, with how far it has got.
    property bool listening: false
    property real listenProgress: 0
    property string listenStatus: ""
    property string failure: ""

    readonly property int struckCount: struck.filter(s => s).length
    readonly property double struckSeconds: {
        let sum = 0
        for (let i = 0; i < words.length; i++) {
            if (struck[i])
                sum += words[i].end - words[i].start
        }
        return sum
    }

    width: 560
    height: 600
    minimumWidth: 420
    minimumHeight: 420
    title: qsTr("Edit by text")
    color: Theme.appBackground

    function openListening(track, clip) {
        root.trackIndex = track
        root.clipIndex = clip
        root.words = []
        root.struck = []
        root.listening = true
        root.listenProgress = 0
        root.listenStatus = ""
        root.failure = ""
        root.show()
        root.raise()
        root.requestActivate()
    }

    Connections {
        target: EditorState
        function onTextEditProgress(fraction, status) {
            root.listenProgress = fraction
            if (status.length > 0)
                root.listenStatus = status
        }
        function onTextEditFailed(message) {
            root.listening = false
            root.failure = message
        }
    }
    onClosing: {
        if (root.listening)
            EditorState.cancelTextEditListening()
        root.listening = false
    }

    function openFor(track, clip) {
        root.listening = false
        root.failure = ""
        root.trackIndex = track
        root.clipIndex = clip
        root.words = EditorState.clipTranscriptWords(track, clip)
        root.struck = root.words.map(() => false)
        root.lastClicked = -1
        root.show()
        root.raise()
        root.requestActivate()
    }

    function toggle(index, range) {
        const next = root.struck.slice()
        if (range && root.lastClicked >= 0) {
            const value = !next[index]
            for (let i = Math.min(index, root.lastClicked); i <= Math.max(index, root.lastClicked); i++)
                next[i] = value
        } else {
            next[index] = !next[index]
        }
        root.struck = next
        root.lastClicked = index
    }

    function listen(index) {
        const w = root.words[index]
        EditorState.playheadSeconds = Math.max(0, w.at - 0.3)
        EditorState.playing = true
        stopTimer.interval = Math.round((w.end - w.start + 0.8) * 1000)
        stopTimer.restart()
    }

    // The struck words as stretches of the source: a run of struck words goes as one piece.
    function struckPieces() {
        const pieces = []
        let i = 0
        while (i < root.words.length) {
            if (!root.struck[i]) {
                ++i
                continue
            }
            let j = i
            while (j + 1 < root.words.length && root.struck[j + 1])
                ++j
            pieces.push({ start: root.words[i].start, end: root.words[j].end, words: true })
            i = j + 1
        }
        return pieces
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

    ThemedLabel {
        id: hint
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: Theme.spacingLg
        wrapMode: Text.WordWrap
        size: "sm"
        text: qsTr("Click the words to take out (Shift + click for a stretch). Double click to hear one.")
    }

    Flickable {
        id: page
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: hint.bottom
        anchors.bottom: footer.top
        anchors.margins: Theme.spacingLg
        clip: true
        contentWidth: width
        contentHeight: flow.height
        ScrollBar.vertical: AppScrollBar { }

        Flow {
            id: flow
            width: page.width
            spacing: 2

            Repeater {
                model: root.words.length
                delegate: Rectangle {
                    id: wordBox
                    required property int index
                    readonly property bool gone: root.struck[index] === true
                    width: wordText.implicitWidth + 8
                    height: wordText.implicitHeight + 4
                    radius: 3
                    color: gone ? Qt.rgba(Theme.destructive.r, Theme.destructive.g, Theme.destructive.b, 0.18)
                                : (wordMouse.containsMouse ? Theme.panelBackground : "transparent")

                    Text {
                        id: wordText
                        anchors.centerIn: parent
                        text: root.words[wordBox.index].text
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeBase
                        font.strikeout: wordBox.gone
                        color: wordBox.gone ? Theme.mutedForeground : Theme.foreground
                    }

                    MouseArea {
                        id: wordMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: mouse => root.toggle(wordBox.index, mouse.modifiers & Qt.ShiftModifier)
                        onDoubleClicked: root.listen(wordBox.index)
                    }
                }
            }
        }

        ThemedLabel {
            anchors.centerIn: parent
            visible: root.words.length === 0 && !root.listening
            width: parent.width
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            size: "sm"
            text: root.failure.length > 0 ? root.failure : qsTr("No words found in this clip.")
        }

        Column {
            anchors.centerIn: parent
            visible: root.listening
            width: Math.min(parent.width - 40, 360)
            spacing: Theme.spacingMd
            ThemedLabel {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                text: qsTr("Listening to the clip to write down what is said… %1%")
                          .arg(Math.round(root.listenProgress * 100))
            }
            ThemedProgressBar {
                width: parent.width
                value: root.listenProgress
            }
            ThemedLabel {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                size: "sm"
                tone: "muted"
                text: root.listenStatus.length > 0 ? root.listenStatus
                                                   : qsTr("The first time takes a while; then it opens at once.")
            }
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
            text: qsTr("%1 words · %2 s").arg(root.struckCount)
                      .arg(Number(root.struckSeconds).toLocaleString(Qt.locale(), "f", 1))
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
                text: qsTr("Cut")
                enabled: root.struckCount > 0
                onClicked: {
                    stopTimer.stop()
                    EditorState.playing = false
                    EditorState.removeSilencePieces(root.trackIndex, root.clipIndex, root.struckPieces())
                    root.close()
                }
            }
        }
    }
}
