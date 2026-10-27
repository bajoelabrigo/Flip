import QtQuick
import QtQuick.Controls.Basic
import Drift

// Edit › Find and replace… (Ctrl+H), as in Word and Premiere: looks for a word in every text clip
// and every subtitle caption of the open sequence, lists where it is (a click selects that clip
// and moves the playhead there) and replaces one match or all of them, each time in one undo
// step. Non-modal and movable, so the preview and the timeline stay in sight.
ThemedDialog {
    id: root

    title: qsTr("Find and replace")
    preferredWidth: Theme.dialogWidthLg
    movable: true
    modal: false
    closePolicy: Popup.CloseOnEscape
    showFooter: false
    acceptOnReturn: false

    property var matches: []
    property int currentIndex: -1
    property bool matchCase: false
    property bool wholeWord: false
    // "all", "texts" or "subtitles".
    property string scope: "all"

    readonly property int clipCount: {
        const seen = {}
        let n = 0
        for (let i = 0; i < root.matches.length; ++i) {
            const m = root.matches[i]
            const key = m.track + ":" + m.clip
            if (!seen[key]) {
                seen[key] = true
                ++n
            }
        }
        return n
    }

    function options() {
        return { "matchCase": root.matchCase, "wholeWord": root.wholeWord, "scope": root.scope }
    }

    function refresh() {
        const keep = root.currentIndex
        root.matches = findField.text.length > 0 ? EditorState.findInTexts(findField.text, root.options()) : []
        root.currentIndex = root.matches.length === 0 ? -1 : Math.min(Math.max(keep, 0), root.matches.length - 1)
    }

    function openDialog() {
        // Keeps the last search, selected, so typing replaces it and Enter walks it again.
        open()
        refresh()
        Qt.callLater(function() {
            findField.forceActiveFocus()
            findField.selectAll()
        })
    }

    function goTo(index) {
        if (index < 0 || index >= root.matches.length)
            return
        root.currentIndex = index
        const m = root.matches[index]
        EditorState.selectClip(m.track, m.clip)
        EditorState.playheadSeconds = m.seconds
        resultList.positionViewAtIndex(index, ListView.Contain)
    }

    function replaceCurrent() {
        if (root.currentIndex < 0 || root.currentIndex >= root.matches.length)
            return
        const m = root.matches[root.currentIndex]
        EditorState.replaceInTexts(findField.text, replaceField.text, root.options(),
                                   [{ "track": m.track, "clip": m.clip, "cue": m.cue, "start": m.start }])
        refresh()
        // The next match has moved into the replaced one's row: show it.
        if (root.currentIndex >= 0)
            goTo(root.currentIndex)
    }

    function replaceAll() {
        if (root.matches.length === 0)
            return
        EditorState.replaceInTexts(findField.text, replaceField.text, root.options(), [])
        refresh()
    }

    function escaped(s) {
        return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    }

    onMatchCaseChanged: refresh()
    onWholeWordChanged: refresh()
    onScopeChanged: refresh()

    // Undo, redo or any other edit while the window is open moves the matches.
    Connections {
        target: EditorState
        enabled: root.visible
        function onTracksChanged() {
            root.refresh()
        }
    }

    contentItem: Column {
        width: parent ? parent.width : Theme.dialogWidthLg
        spacing: Theme.spacingLg

        Column {
            width: parent.width
            spacing: Theme.spacingSm

            ThemedLabel {
                text: qsTr("Find")
            }
            ThemedTextField {
                id: findField
                width: parent.width
                font.family: Theme.fontFamily
                placeholderText: qsTr("Word or phrase in your texts and subtitles")
                onTextChanged: root.refresh()
                onAccepted: root.goTo(root.currentIndex < 0 ? 0 : (root.currentIndex + 1) % Math.max(1, root.matches.length))
            }
        }

        Column {
            width: parent.width
            spacing: Theme.spacingSm

            ThemedLabel {
                text: qsTr("Replace with")
            }
            ThemedTextField {
                id: replaceField
                width: parent.width
                font.family: Theme.fontFamily
                onAccepted: root.replaceCurrent()
            }
        }

        Flow {
            width: parent.width
            spacing: Theme.spacingLg

            ThemedCheckBox {
                text: qsTr("Match case")
                checked: root.matchCase
                onToggled: root.matchCase = checked
            }
            ThemedCheckBox {
                text: qsTr("Whole word")
                checked: root.wholeWord
                onToggled: root.wholeWord = checked
            }
        }

        Row {
            spacing: Theme.spacingSm

            ThemedLabel {
                anchors.verticalCenter: parent.verticalCenter
                text: qsTr("Look in")
            }
            ThemedChip {
                text: qsTr("Texts and subtitles")
                selected: root.scope === "all"
                onClicked: root.scope = "all"
            }
            ThemedChip {
                text: qsTr("Texts")
                selected: root.scope === "texts"
                onClicked: root.scope = "texts"
            }
            ThemedChip {
                text: qsTr("Subtitles")
                selected: root.scope === "subtitles"
                onClicked: root.scope = "subtitles"
            }
        }

        Text {
            width: parent.width
            wrapMode: Text.WordWrap
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSm
            text: findField.text.length === 0
                  ? qsTr("Type what to look for.")
                  : (root.matches.length === 0
                     ? qsTr("No matches")
                     : qsTr("%1 in %n clip(s)", "", root.clipCount)
                       .arg(qsTr("%n match(es)", "", root.matches.length)))
        }

        Rectangle {
            width: parent.width
            height: Math.min(Math.max(1, resultList.contentHeight), 220) + 2 * Theme.borderWidth
            visible: root.matches.length > 0
            radius: Theme.radiusSm
            color: "transparent"
            border.width: Theme.borderWidth
            border.color: Theme.panelBorder

            ListView {
                id: resultList
                anchors.fill: parent
                anchors.margins: Theme.borderWidth
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                model: root.matches
                currentIndex: root.currentIndex
                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

                delegate: Rectangle {
                    id: row
                    required property var modelData
                    required property int index
                    width: ListView.view.width
                    height: rowColumn.implicitHeight + 2 * Theme.spacingSm
                    color: row.index === root.currentIndex ? Theme.panelSecondaryBg
                                                           : (rowMouse.containsMouse ? Theme.popoverHover : "transparent")

                    Column {
                        id: rowColumn
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.leftMargin: Theme.spacingLg
                        anchors.rightMargin: Theme.spacingLg
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 2

                        Text {
                            width: parent.width
                            elide: Text.ElideRight
                            color: Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                            text: {
                                const d = row.modelData
                                const kind = d.kind === "subtitle"
                                             ? qsTr("Subtitle · caption %1").arg(d.cue + 1)
                                             : qsTr("Text")
                                const name = d.clipName && d.clipName.length > 0 ? d.clipName : qsTr("Clip")
                                const locked = d.locked ? " · " + qsTr("locked track, it is not replaced") : ""
                                return kind + " · " + name + locked
                            }
                        }
                        Text {
                            width: parent.width
                            elide: Text.ElideRight
                            textFormat: Text.StyledText
                            color: Theme.panelForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeSm
                            text: root.escaped(row.modelData.before)
                                  + "<b><font color=\"" + Theme.primary + "\">" + root.escaped(row.modelData.match)
                                  + "</font></b>" + root.escaped(row.modelData.after)
                        }
                    }

                    MouseArea {
                        id: rowMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.goTo(row.index)
                    }
                }
            }
        }

        Row {
            anchors.right: parent.right
            spacing: Theme.spacingMd

            ThemedButton {
                variant: "ghost"
                text: qsTr("Close")
                onClicked: root.close()
            }
            ThemedButton {
                text: qsTr("Replace")
                enabled: root.currentIndex >= 0 && root.matches.length > 0
                         && !root.matches[root.currentIndex].locked
                onClicked: root.replaceCurrent()
            }
            ThemedButton {
                variant: "primary"
                text: qsTr("Replace all")
                enabled: root.matches.length > 0
                onClicked: root.replaceAll()
            }
        }
    }
}
