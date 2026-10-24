import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// The rows a track unfolds into under its clips when the twirl in its header is open, as a
// layer's properties do in After Effects: one line per animated property, its keys drawn where
// they fall on the timeline. Keys are dragged to move them, double-click on a line adds one with
// the value the property already has there, and right-click shapes or removes a key. A key's
// glyph shows its shape as After Effects draws it (KeyframeGlyph): its left half how the value
// arrives, its right half how it leaves.
//
// Keys are picked like After Effects': a click picks one (and brings the playhead to it), Ctrl
// adds or takes one away, Shift picks the run on that line. The menu and After Effects' keys
// (F9 Suave, Shift+F9 Suave al llegar, Ctrl+Shift+F9 Suave al salir, Ctrl+Alt+H Salto,
// Ctrl+Alt+K Recto) act on every picked key at once.
Item {
    id: root

    property int trackIndex: -1
    property real pxPerSecond: 100
    // EditorState.trackKeyframeRows(trackIndex), as TimelinePanel last read it.
    property var liveRows: []
    // What the delegates draw. Held while a key is dragged: each step of the drag rewrites the
    // project, and rebuilding the rows under the pointer would drop the drag halfway.
    property var rows: []
    property bool dragging: false
    readonly property real rowHeight: Theme.keyframeRowHeight
    // The picked keys, each {clip, prop, seconds}; only while this track holds the pick.
    property var picked: []
    property bool pickActive: false
    readonly property var pickedKeys: pickActive ? picked : []
    // A run with Shift starts here: {clip, prop, seconds}.
    property var runFrom: null
    signal picking()

    height: rows.length * rowHeight
    onLiveRowsChanged: if (!dragging) rows = liveRows
    onDraggingChanged: if (!dragging) rows = liveRows
    Component.onCompleted: rows = liveRows

    function keyAt(clipEntry, seconds) {
        const keys = clipEntry.keys || []
        for (let i = 0; i < keys.length; ++i) {
            if (Math.abs(keys[i].seconds - seconds) < 1e-4)
                return i
        }
        return -1
    }

    function sameKey(a, b) {
        return a.clip === b.clip && a.prop === b.prop && Math.abs(a.seconds - b.seconds) < 1e-4
    }

    function isPicked(key) {
        for (let i = 0; i < root.pickedKeys.length; ++i) {
            if (sameKey(root.pickedKeys[i], key))
                return true
        }
        return false
    }

    function setPicked(list) {
        root.picking()
        root.picked = list
    }

    // How a key arrives and leaves, from its handles: none is straight, a flat one eased, any
    // other a shape of its own; a hold on the key before squares the way in.
    function halfOf(dx, dy) {
        if (Math.abs(dx) < 1e-9 && Math.abs(dy) < 1e-9)
            return "linear"
        return Math.abs(dy) < 1e-6 ? "ease" : "bezier"
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
        if (root.pickedKeys.length)
            EditorState.setKeyframesEasing(root.trackIndex, root.pickedKeys, mode)
    }

    Shortcut {
        sequence: "F9"
        enabled: root.pickedKeys.length > 0
        onActivated: root.applyEasing("ease")
    }
    Shortcut {
        sequence: "Shift+F9"
        enabled: root.pickedKeys.length > 0
        onActivated: root.applyEasing("easeIn")
    }
    Shortcut {
        sequence: "Ctrl+Shift+F9"
        enabled: root.pickedKeys.length > 0
        onActivated: root.applyEasing("easeOut")
    }
    Shortcut {
        sequence: "Ctrl+Alt+H"
        enabled: root.pickedKeys.length > 0
        onActivated: root.applyEasing("hold")
    }
    Shortcut {
        sequence: "Ctrl+Alt+K"
        enabled: root.pickedKeys.length > 0
        onActivated: root.applyEasing("linear")
    }

    KeyframeCurvesPopup {
        id: curvesPopup
        onCurvePicked: (x1, y1, x2, y2, hold) => {
            if (hold)
                root.applyEasing("hold")
            else if (root.pickedKeys.length)
                EditorState.setKeyframesCurve(root.trackIndex, root.pickedKeys, x1, y1, x2, y2)
        }
    }

    Repeater {
        model: root.rows
        delegate: Item {
            id: rowItem
            required property var modelData
            required property int index
            y: index * root.rowHeight
            width: root.width
            height: root.rowHeight

            Rectangle {
                anchors.fill: parent
                color: Qt.rgba(0, 0, 0, rowItem.index % 2 === 0 ? 0.16 : 0.08)
            }
            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                height: 1
                color: Qt.rgba(0, 0, 0, 0.25)
            }

            Repeater {
                model: rowItem.modelData.clips
                delegate: Item {
                    id: span
                    required property var modelData
                    readonly property color keyColor: Theme.keyframeCurveColor(span.modelData.prop)
                    x: span.modelData.start * root.pxPerSecond
                    width: Math.max(1, span.modelData.duration * root.pxPerSecond)
                    height: rowItem.height

                    // The clip's stretch on this line, faintly, so a key reads as belonging to it.
                    Rectangle {
                        anchors.fill: parent
                        anchors.topMargin: 3
                        anchors.bottomMargin: 3
                        radius: 2
                        color: Qt.rgba(span.keyColor.r, span.keyColor.g, span.keyColor.b, 0.10)
                    }

                    // The interpolation between keys: a thin line, dashed where a key holds.
                    Repeater {
                        model: Math.max(0, (span.modelData.keys || []).length - 1)
                        delegate: Rectangle {
                            required property int index
                            readonly property var from: span.modelData.keys[index]
                            readonly property var to: span.modelData.keys[index + 1]
                            x: (from.seconds - span.modelData.start) * root.pxPerSecond
                            width: Math.max(0, (to.seconds - from.seconds) * root.pxPerSecond)
                            y: span.height / 2
                            height: 1
                            color: span.keyColor
                            opacity: from.hold ? 0.2 : 0.45
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        acceptedButtons: Qt.LeftButton
                        hoverEnabled: true
                        onDoubleClicked: (mouse) => {
                            const at = Math.max(span.modelData.start,
                                Math.min(span.modelData.start + span.modelData.duration,
                                         EditorState.snapTime(span.modelData.start
                                                              + mouse.x / root.pxPerSecond)))
                            EditorState.addClipKeyframeAt(root.trackIndex, span.modelData.clip,
                                                          span.modelData.prop, at)
                        }
                        onClicked: {
                            root.picked = []
                            EditorState.selectClip(root.trackIndex, span.modelData.clip)
                        }

                        ThemedToolTip {
                            visible: parent.containsMouse
                            text: qsTr("Double-click to add a keyframe")
                        }
                    }

                    Repeater {
                        model: span.modelData.keys
                        delegate: Item {
                            id: keyItem
                            required property var modelData
                            required property int index
                            // Where the key sits while it is dragged, in timeline seconds.
                            property real editSeconds: modelData.seconds
                            property real dragDx: 0
                            property real pressX: 0
                            property bool moved: false
                            property bool dragArmed: false
                            readonly property var ref: ({ clip: span.modelData.clip,
                                                          prop: span.modelData.prop,
                                                          seconds: modelData.seconds })
                            readonly property var halves: root.keyHalves(span.modelData.keys, index)
                            readonly property bool atPlayhead:
                                Math.abs(EditorState.playheadSeconds - modelData.seconds) < 1 / 60
                            readonly property bool isPicked: root.isPicked(ref)

                            width: 16
                            height: span.height
                            x: (modelData.seconds - span.modelData.start) * root.pxPerSecond
                               - width / 2 + dragDx
                            z: keyMouse.pressed || isPicked ? 2 : 1

                            KeyframeGlyph {
                                anchors.centerIn: parent
                                size: keyItem.isPicked ? 15 : (keyMouse.containsMouse ? 13 : 11)
                                inHalf: keyItem.halves["in"]
                                outHalf: keyItem.halves["out"]
                                color: span.keyColor
                                picked: keyItem.isPicked
                                // Only the pointer lights a key: lighting every key under the
                                // playhead read as several picked at once (X and Y together).
                                lit: keyMouse.containsMouse || keyMouse.pressed
                            }

                            MouseArea {
                                id: keyMouse
                                anchors.fill: parent
                                anchors.margins: -2
                                hoverEnabled: true
                                acceptedButtons: Qt.LeftButton | Qt.RightButton
                                cursorShape: pressed ? Qt.ClosedHandCursor : Qt.PointingHandCursor
                                preventStealing: true

                                onPressed: (mouse) => {
                                    if (mouse.button === Qt.RightButton) {
                                        // The menu acts on the picked keys when this is one of them.
                                        if (!keyItem.isPicked)
                                            root.setPicked([keyItem.ref])
                                        return
                                    }
                                    const ctrl = mouse.modifiers & Qt.ControlModifier
                                    const shift = mouse.modifiers & Qt.ShiftModifier
                                    if (ctrl) {
                                        root.setPicked(keyItem.isPicked
                                            ? root.pickedKeys.filter((k) => !root.sameKey(k, keyItem.ref))
                                            : root.pickedKeys.concat([keyItem.ref]))
                                    } else if (shift && root.runFrom && root.runFrom.clip === keyItem.ref.clip
                                               && root.runFrom.prop === keyItem.ref.prop) {
                                        const lo = Math.min(root.runFrom.seconds, keyItem.ref.seconds) - 1e-4
                                        const hi = Math.max(root.runFrom.seconds, keyItem.ref.seconds) + 1e-4
                                        root.setPicked(span.modelData.keys
                                            .filter((k) => k.seconds >= lo && k.seconds <= hi)
                                            .map((k) => ({ clip: span.modelData.clip,
                                                           prop: span.modelData.prop,
                                                           seconds: k.seconds })))
                                    } else if (!keyItem.isPicked) {
                                        root.setPicked([keyItem.ref])
                                    }
                                    if (!shift)
                                        root.runFrom = keyItem.ref
                                    // Only a plain press drags (as the clip strip's keys).
                                    keyItem.dragArmed = !ctrl && !shift
                                    keyItem.pressX = mapToItem(root, mouse.x, mouse.y).x
                                    keyItem.editSeconds = keyItem.modelData.seconds
                                    keyItem.moved = false
                                }
                                onPositionChanged: (mouse) => {
                                    if (!pressed || !keyItem.dragArmed || !(mouse.buttons & Qt.LeftButton))
                                        return
                                    const dx = mapToItem(root, mouse.x, mouse.y).x - keyItem.pressX
                                    if (!keyItem.moved) {
                                        if (Math.abs(dx) < 3)
                                            return
                                        keyItem.moved = true
                                        root.dragging = true
                                        EditorState.beginPreviewDrag(qsTr("Move keyframe"))
                                    }
                                    // Between its neighbours: passing one would land on it and
                                    // overwrite it.
                                    const keys = span.modelData.keys
                                    const frame = 1 / 60
                                    const lo = keyItem.index > 0 ? keys[keyItem.index - 1].seconds + frame
                                                                 : span.modelData.start
                                    const hi = keyItem.index < keys.length - 1
                                             ? keys[keyItem.index + 1].seconds - frame
                                             : span.modelData.start + span.modelData.duration
                                    const base = keyItem.modelData.seconds
                                    const at = Math.max(lo, Math.min(hi,
                                        EditorState.snapTime(base + dx / root.pxPerSecond)))
                                    if (Math.abs(at - keyItem.editSeconds) < 1e-6)
                                        return
                                    EditorState.previewMoveClipKeyframe(
                                        root.trackIndex, span.modelData.clip, span.modelData.prop,
                                        keyItem.editSeconds, at, keyItem.modelData.value)
                                    keyItem.editSeconds = at
                                    keyItem.dragDx = (at - base) * root.pxPerSecond
                                    EditorState.playheadSeconds = at
                                }
                                onReleased: (mouse) => {
                                    if (mouse.button !== Qt.LeftButton)
                                        return
                                    if (keyItem.moved) {
                                        EditorState.commitPreviewDrag()
                                        keyItem.dragDx = 0
                                        root.dragging = false
                                        // The moved key stays picked at its new time.
                                        root.setPicked([{ clip: span.modelData.clip,
                                                          prop: span.modelData.prop,
                                                          seconds: keyItem.editSeconds }])
                                    } else if (keyItem.dragArmed) {
                                        // A click: the clip and the playhead go to the key, so the
                                        // inspector shows the value it holds.
                                        root.setPicked([keyItem.ref])
                                        EditorState.selectClip(root.trackIndex, span.modelData.clip)
                                        EditorState.playheadSeconds = keyItem.modelData.seconds
                                    }
                                }
                                onCanceled: {
                                    if (keyItem.moved) {
                                        EditorState.commitPreviewDrag()
                                        keyItem.dragDx = 0
                                        root.dragging = false
                                    }
                                }
                                onClicked: (mouse) => {
                                    if (mouse.button === Qt.RightButton)
                                        keyMenu.popup()
                                }
                            }

                            ThemedToolTip {
                                visible: keyMouse.containsMouse && !keyMouse.pressed
                                text: rowItem.modelData.label + " · "
                                      + keyItem.modelData.seconds.toFixed(2) + " s"
                                      + " · " + qsTr("right-click: Straight, Smooth, Hold, Curves")
                            }

                            ThemedContextMenu {
                                id: keyMenu

                                readonly property bool one: root.pickedKeys.length <= 1
                                function check(inHalf, outHalf) {
                                    return keyMenu.one && keyItem.halves["in"] === inHalf
                                           && keyItem.halves["out"] === outHalf ? Theme.icons.check : ""
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
                                    icon.name: keyMenu.one && keyItem.modelData.hold ? Theme.icons.check : ""
                                    onTriggered: root.applyEasing("hold")
                                }
                                ThemedMenuItem {
                                    text: qsTr("Curves…")
                                    icon.name: Theme.icons.penCurve
                                    onTriggered: {
                                        const p = keyItem.mapToItem(root, keyItem.width / 2, keyItem.height)
                                        curvesPopup.x = p.x
                                        curvesPopup.y = p.y
                                        curvesPopup.open()
                                    }
                                }
                                ThemedMenuSeparator {}
                                ThemedMenuItem {
                                    text: qsTr("Edit curve…")
                                    icon.name: Theme.icons.penCurve
                                    onTriggered: {
                                        EditorState.selectClip(root.trackIndex, span.modelData.clip)
                                        EditorState.playheadSeconds = keyItem.modelData.seconds
                                        EditorState.preferences.curveEditorVisible = true
                                    }
                                }
                                ThemedMenuItem {
                                    text: keyMenu.one ? qsTr("Delete keyframe") : qsTr("Delete keyframes")
                                    icon.name: Theme.icons.trash
                                    onTriggered: {
                                        EditorState.removeKeyframes(root.trackIndex, root.pickedKeys.length
                                                                    ? root.pickedKeys : [keyItem.ref])
                                        root.picked = []
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
