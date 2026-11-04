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
    // After Effects' blue for values you can drag or type.
    property color tint: "#4aa3ff"
    // Called with the stored value inside the drag session; null writes `prop`.
    property var write: null
    // Before the first write of a drag (Scale reads where it starts).
    signal begun()
    // Tab (or Shift+Tab) confirmed the typed value: the line opens the next (previous) value, as
    // After Effects does. The focus never wanders off to the header's buttons.
    signal tabbed(bool back)

    function startEditing() {
        field.text = root.format(root.shown).replace(root.suffix, "")
        root.editing = true
        field.forceActiveFocus()
        field.selectAll()
    }

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
    function begin(keepSelection) {
        if (!keepSelection
                && (EditorState.selectedTrack !== root.trackIndex || EditorState.selectedClip !== root.clipIndex))
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
        // The hint shows only once the pointer moves over the value, and not again after a press until
        // it leaves: it sat over the line's name while the value was typed and the frames stepped, and
        // the line is rebuilt on every commit, so a still pointer over the new one must not bring it back
        // (bounce exercise #14).
        property bool hintUsed: false
        property bool movedOver: false
        onExited: {
            hintUsed = false
            movedOver = false
        }
        onPressed: (mouse) => {
            hintUsed = true
            pressX = mapToItem(null, mouse.x, mouse.y).x
            startShown = root.shown
            root.liveShown = startShown
        }
        onPositionChanged: (mouse) => {
            if (!pressed) {
                movedOver = true
                return
            }
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
            root.startEditing()
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
        // `focusLost`: the click went elsewhere (another clip): the value is kept, but the selection
        // stays where the click put it (0.30: a field left typing re-selected its own clip, so
        // clicking another clip seemed to do nothing until Esc, tests #2 and #9).
        function finish(commit, focusLost) {
            if (!root.editing)
                return
            root.editing = false
            // Untouched: nothing to write.
            if (text === root.format(root.shown).replace(root.suffix, ""))
                return
            // Sums too, as After Effects: "+50" adds to the value shown, "*2" doubles it, "100+20" is 120.
            const d = ValueMath.evaluate(text, root.shown)
            if (commit && !isNaN(d)) {
                root.begin(!!focusLost)
                root.apply(d)
                EditorState.commitPreviewDrag()
            }
        }
        Keys.onReturnPressed: finish(true)
        Keys.onEnterPressed: finish(true)
        Keys.onEscapePressed: finish(false)
        // The line asks for the next value first: the commit rebuilds the lines at once, so a signal
        // sent after it came from a destroyed item and nobody heard it (bounce exercise #10b).
        Keys.onTabPressed: (event) => {
            event.accepted = true
            root.tabbed(false)
            finish(true)
        }
        Keys.onBacktabPressed: (event) => {
            event.accepted = true
            root.tabbed(true)
            finish(true)
        }
        onActiveFocusChanged: if (!activeFocus) finish(true, true)
    }

    ThemedToolTip {
        visible: scrub.containsMouse && scrub.movedOver && !scrub.hintUsed && !root.dragging && !root.editing
        text: qsTr("Drag to change, click to type")
    }
}
