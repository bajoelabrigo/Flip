import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// The picked keys, shared by the curve editor above the tracks (KeyframeGraph) and the rows a
// track unfolds into (TrackKeyframeRows): a key picked in one is picked in the other, and the
// menu, the Curves popup and After Effects' keys (F9 Suave, Shift+F9 Suave al llegar,
// Ctrl+Shift+F9 Suave al salir, Ctrl+Alt+H Salto, Ctrl+Alt+K Recto) are the same in both.
// Picking keys on another track drops the ones picked before, so the keys act on one set.
Item {
    id: root

    width: 0
    height: 0

    // The track the picked keys are on, and the keys themselves, each {clip, prop, seconds}.
    property int track: -1
    property var keys: []
    // A run with Shift starts here: {clip, prop, seconds}.
    property var runFrom: null
    readonly property bool hasPick: track >= 0 && keys.length > 0

    // The key the menu was opened on: how it arrives and leaves, and whether it holds.
    property var menuHalves: ({ "in": "linear", "out": "linear" })
    property bool menuHold: false
    property bool menuFromGraph: false
    property int menuClip: -1
    property real menuSeconds: 0

    function sameKey(a, b) {
        return a.clip === b.clip && a.prop === b.prop && Math.abs(a.seconds - b.seconds) < 1e-4
    }

    function isPicked(trackIndex, key) {
        if (trackIndex !== root.track)
            return false
        for (let i = 0; i < root.keys.length; ++i) {
            if (sameKey(root.keys[i], key))
                return true
        }
        return false
    }

    function pick(trackIndex, list) {
        root.track = trackIndex
        root.keys = list
    }

    function clear() {
        root.keys = []
        root.runFrom = null
    }

    // A press on a key, as After Effects picks: plain picks it (unless it already is one of the
    // picked, so a drag moves them all), Ctrl adds or takes it away, Shift picks the run on that
    // property between the last key picked and this one. `siblings` are the keys of its property
    // on that clip, for the run.
    function press(trackIndex, ref, modifiers, siblings) {
        const ctrl = modifiers & Qt.ControlModifier
        const shift = modifiers & Qt.ShiftModifier
        const mine = trackIndex === root.track ? root.keys : []
        if (ctrl) {
            pick(trackIndex, isPicked(trackIndex, ref)
                 ? mine.filter((k) => !sameKey(k, ref))
                 : mine.concat([ref]))
        } else if (shift && root.runFrom && trackIndex === root.track
                   && root.runFrom.clip === ref.clip && root.runFrom.prop === ref.prop) {
            const lo = Math.min(root.runFrom.seconds, ref.seconds) - 1e-4
            const hi = Math.max(root.runFrom.seconds, ref.seconds) + 1e-4
            pick(trackIndex, (siblings || [])
                 .filter((k) => k.seconds >= lo && k.seconds <= hi)
                 .map((k) => ({ clip: ref.clip, prop: ref.prop, seconds: k.seconds })))
        } else if (!isPicked(trackIndex, ref)) {
            pick(trackIndex, [ref])
        }
        if (!shift)
            root.runFrom = ref
    }

    // How a key arrives and leaves, from its handles: none is straight, a flat one eased, any
    // other a shape of its own; a hold on the key before squares the way in.
    function halfOf(dx, dy) {
        if (Math.abs(dx || 0) < 1e-9 && Math.abs(dy || 0) < 1e-9)
            return "linear"
        return Math.abs(dy || 0) < 1e-6 ? "ease" : "bezier"
    }
    function keyHalves(keys, i) {
        const k = keys[i]
        const prev = i > 0 ? keys[i - 1] : null
        const next = i < keys.length - 1 ? keys[i + 1] : null
        const inHalf = prev ? (prev.hold ? "hold" : halfOf(k.inDx, k.inDy)) : null
        const outHalf = next ? (k.hold ? "hold" : halfOf(k.outDx, k.outDy)) : null
        return {
            "in": inHalf !== null ? inHalf : (outHalf !== null ? outHalf : (k.hold ? "hold" : "linear")),
            "out": outHalf !== null ? outHalf : (k.hold ? "hold" : (inHalf !== null ? inHalf : "linear"))
        }
    }

    function applyEasing(mode) {
        if (root.hasPick)
            EditorState.setKeyframesEasing(root.track, root.keys, mode)
    }

    function removePicked() {
        if (!root.hasPick)
            return false
        EditorState.removeKeyframes(root.track, root.keys)
        clear()
        return true
    }

    // The menu for the key `ref` on `trackIndex`, opened at the pointer. `at` is the point in
    // `item` the Curves popup opens from.
    function openMenu(trackIndex, ref, halves, hold, fromGraph, item, at) {
        if (!isPicked(trackIndex, ref))
            pick(trackIndex, [ref])
        root.menuHalves = halves
        root.menuHold = hold
        root.menuFromGraph = fromGraph
        root.menuClip = ref.clip
        root.menuSeconds = ref.seconds
        const p = item.mapToItem(curvesPopup.parent, at.x, at.y)
        curvesPopup.x = p.x
        curvesPopup.y = p.y
        keyMenu.popup()
    }

    // A key picked on a clip that is no longer the selected one would be deleted by Delete while
    // the clip is what the user means: the pick follows the selection.
    Connections {
        target: EditorState
        function onSelectionChanged() {
            if (!root.hasPick)
                return
            if (EditorState.selectedTrack !== root.track
                    || !root.keys.some((k) => k.clip === EditorState.selectedClip))
                root.clear()
        }
    }

    Shortcut {
        sequence: "F9"
        enabled: root.hasPick
        onActivated: root.applyEasing("ease")
    }
    Shortcut {
        sequence: "Shift+F9"
        enabled: root.hasPick
        onActivated: root.applyEasing("easeIn")
    }
    Shortcut {
        sequence: "Ctrl+Shift+F9"
        enabled: root.hasPick
        onActivated: root.applyEasing("easeOut")
    }
    Shortcut {
        sequence: "Ctrl+Alt+H"
        enabled: root.hasPick
        onActivated: root.applyEasing("hold")
    }
    Shortcut {
        sequence: "Ctrl+Alt+K"
        enabled: root.hasPick
        onActivated: root.applyEasing("linear")
    }

    KeyframeCurvesPopup {
        id: curvesPopup
        onCurvePicked: (x1, y1, x2, y2, hold) => {
            if (hold)
                root.applyEasing("hold")
            else if (root.hasPick)
                EditorState.setKeyframesCurve(root.track, root.keys, x1, y1, x2, y2)
        }
    }

    ThemedContextMenu {
        id: keyMenu

        readonly property bool one: root.keys.length <= 1
        function check(inHalf, outHalf) {
            return keyMenu.one && root.menuHalves["in"] === inHalf
                   && root.menuHalves["out"] === outHalf ? Theme.icons.check : ""
        }

        ThemedMenuItem {
            text: qsTr("Straight")
            shortcutText: "Ctrl+Alt+K"
            icon.name: keyMenu.check("linear", "linear")
            onTriggered: root.applyEasing("linear")
        }
        ThemedMenuItem {
            text: qsTr("Smooth")
            shortcutText: "F9"
            icon.name: keyMenu.check("ease", "ease")
            onTriggered: root.applyEasing("ease")
        }
        ThemedMenuItem {
            text: qsTr("Smooth in")
            shortcutText: "Shift+F9"
            icon.name: keyMenu.check("ease", "linear")
            onTriggered: root.applyEasing("easeIn")
        }
        ThemedMenuItem {
            text: qsTr("Smooth out")
            shortcutText: "Ctrl+Shift+F9"
            icon.name: keyMenu.check("linear", "ease")
            onTriggered: root.applyEasing("easeOut")
        }
        ThemedMenuItem {
            text: qsTr("Hold")
            shortcutText: "Ctrl+Alt+H"
            icon.name: keyMenu.one && root.menuHold ? Theme.icons.check : ""
            onTriggered: root.applyEasing("hold")
        }
        ThemedMenuItem {
            text: qsTr("Curves…")
            icon.name: Theme.icons.penCurve
            onTriggered: curvesPopup.open()
        }
        ThemedMenuSeparator {}
        ThemedMenuItem {
            // The curve editor is where this menu was opened from when it came from the graph.
            visible: !root.menuFromGraph
            height: visible ? implicitHeight : 0
            text: qsTr("Edit curve…")
            icon.name: Theme.icons.penCurve
            onTriggered: {
                EditorState.selectClip(root.track, root.menuClip)
                EditorState.playheadSeconds = root.menuSeconds
                EditorState.preferences.curveEditorVisible = true
            }
        }
        ThemedMenuItem {
            text: keyMenu.one ? qsTr("Delete keyframe") : qsTr("Delete keyframes")
            icon.name: Theme.icons.trash
            onTriggered: root.removePicked()
        }
    }
}
