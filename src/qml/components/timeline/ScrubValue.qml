import QtQuick
import Drift
import ".."

// After Effects' "hot text" (0.25): a value on a keyframe line that is dragged sideways to change
// it, or clicked to type it. With the property animated the change is a key at the playhead
// (EditorState.previewSetPropertyValue), otherwise it is the value itself. One undo step per drag
// or per typed value.
Item {
    id: root

    property int trackIndex: -1
    property int clipIndex: -1
    // The property written by default; `write` replaces it for the ones that move several
    // (Scale writes width, height and keeps the centre).
    property string prop: ""
    // The value as stored (gain 0..2, opacity 0..1, …), at the playhead.
    property real value: 0
    // Stored value <-> what is shown and typed (dB, %, …).
    property var toDisplay: function (v) { return v }
    property var fromDisplay: function (d) { return d }
    property real displayMin: -1e9
    property real displayMax: 1e9
    // Shown units moved per pixel of drag.
    property real step: 1
    property int decimals: 0
    property string suffix: ""
    property string undoLabel: qsTr("Edit value")
    property color tint: Theme.primary
    // Called with the stored value inside the drag session; null writes `prop`.
    property var write: null
    // Before the first write of a drag (Scale reads where it starts).
    signal begun()

    readonly property real shown: toDisplay(value)
    property bool editing: false
    property bool dragging: false
    property real liveShown: 0

    implicitWidth: label.implicitWidth + 2
    implicitHeight: label.implicitHeight

    function format(d) {
        return (decimals > 0 ? Number(d).toFixed(decimals) : String(Math.round(d))) + suffix
    }
    function clampShown(d) {
        return Math.max(displayMin, Math.min(displayMax, d))
    }
    function apply(shownValue) {
        const stored = fromDisplay(clampShown(shownValue))
        if (root.write)
            root.write(stored)
        else
            EditorState.previewSetPropertyValue(root.trackIndex, root.clipIndex, root.prop,
                                                EditorState.playheadSeconds, stored)
    }
    function begin() {
        if (EditorState.selectedTrack !== root.trackIndex || EditorState.selectedClip !== root.clipIndex)
            EditorState.selectClip(root.trackIndex, root.clipIndex)
        EditorState.beginPreviewDrag(root.undoLabel)
        root.begun()
    }

    Text {
        id: label
        anchors.verticalCenter: parent.verticalCenter
        visible: !root.editing
        text: root.format(root.dragging ? root.liveShown : root.shown)
        color: root.tint
        font.family: Theme.monoFontFamily
        font.pixelSize: Theme.fontSizeTiny
        font.underline: scrub.containsMouse || root.dragging
    }

    MouseArea {
        id: scrub
        anchors.fill: label
        anchors.margins: -3
        visible: !root.editing
        enabled: root.trackIndex >= 0 && root.clipIndex >= 0
        hoverEnabled: true
        preventStealing: true
        cursorShape: Qt.SizeHorCursor
        property real pressX: 0
        property real startShown: 0
        onPressed: (mouse) => {
            pressX = mapToItem(null, mouse.x, mouse.y).x
            startShown = root.shown
            root.liveShown = startShown
        }
        onPositionChanged: (mouse) => {
            if (!pressed)
                return
            const dx = mapToItem(null, mouse.x, mouse.y).x - pressX
            if (!root.dragging) {
                if (Math.abs(dx) < 3)
                    return
                root.dragging = true
                root.begin()
            }
            // Shift moves ten times as fast, Ctrl ten times as fine, as After Effects.
            const mods = mouse.modifiers
            const k = (mods & Qt.ShiftModifier) ? 10 : (mods & Qt.ControlModifier) ? 0.1 : 1
            root.liveShown = root.clampShown(startShown + dx * root.step * k)
            root.apply(root.liveShown)
        }
        onReleased: {
            if (root.dragging) {
                EditorState.commitPreviewDrag()
                root.dragging = false
                return
            }
            // A click: type the value.
            field.text = root.format(root.shown).replace(root.suffix, "")
            root.editing = true
            field.forceActiveFocus()
            field.selectAll()
        }
        onCanceled: {
            if (root.dragging) {
                EditorState.commitPreviewDrag()
                root.dragging = false
            }
        }
    }

    Rectangle {
        visible: root.editing
        anchors.fill: field
        anchors.margins: -2
        radius: 2
        color: Theme.panelBackground
        border.width: 1
        border.color: root.tint
    }
    TextInput {
        id: field
        visible: root.editing
        anchors.verticalCenter: parent.verticalCenter
        width: Math.max(36, contentWidth + 4)
        color: Theme.panelForeground
        font.family: Theme.monoFontFamily
        font.pixelSize: Theme.fontSizeTiny
        selectByMouse: true
        inputMethodHints: Qt.ImhFormattedNumbersOnly
        function finish(commit) {
            if (!root.editing)
                return
            root.editing = false
            const d = parseFloat(String(text).replace(",", "."))
            if (commit && !isNaN(d)) {
                root.begin()
                root.apply(d)
                EditorState.commitPreviewDrag()
            }
        }
        Keys.onReturnPressed: finish(true)
        Keys.onEnterPressed: finish(true)
        Keys.onEscapePressed: finish(false)
        onActiveFocusChanged: if (!activeFocus) finish(true)
    }

    ThemedToolTip {
        visible: scrub.containsMouse && !root.dragging && !root.editing
        text: qsTr("Drag to change, click to type")
    }
}
