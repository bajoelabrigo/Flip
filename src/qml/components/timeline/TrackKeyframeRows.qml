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
    // The picked keys, the menu and the Curves popup, shared with the curve editor above the
    // tracks (KeyframeKeyTools, one per timeline).
    property KeyframeKeyTools tools: null

    // The clip these lines act on (the diamond button, the highlighted stretch): the selected one
    // on this track, else the one under the playhead (0.24).
    readonly property int targetClip: {
        void EditorState.playheadSeconds
        void EditorState.selectedClip
        void EditorState.tracksRevision
        return EditorState.keyframeTargetClip(root.trackIndex)
    }
    // Keys read light grey; picked ones take the accent, as the timeline's selection does.
    readonly property color keyGrey: "#cfd3d6"

    height: rows.length * rowHeight
    onLiveRowsChanged: if (!dragging) rows = liveRows
    onDraggingChanged: if (!dragging) rows = liveRows
    Component.onCompleted: rows = liveRows

    // A line's name: the joined transform lines by their group, the rest as the app names them.
    function rowLabel(row) {
        switch (row.group && !row.axis ? row.group : "") {
        case "position": return qsTranslate("TrackKeyframeRows", "Position")
        case "rotation": return qsTranslate("TrackKeyframeRows", "Rotation")
        case "scale": return qsTranslate("TrackKeyframeRows", "Scale")
        case "opacity": return qsTranslate("TrackKeyframeRows", "Opacity")
        }
        switch (row.axis ? row.prop : "") {
        case "x": return "X"
        case "y": return "Y"
        case "width": return qsTranslate("TrackKeyframeRows", "Width")
        case "height": return qsTranslate("TrackKeyframeRows", "Height")
        }
        return row.label
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
                    readonly property color keyColor: root.keyGrey
                    readonly property bool target: span.modelData.clip === root.targetClip
                    x: span.modelData.start * root.pxPerSecond
                    width: Math.max(1, span.modelData.duration * root.pxPerSecond)
                    height: rowItem.height

                    // The clip's stretch on this line, faintly, so a key reads as belonging to it.
                    Rectangle {
                        anchors.fill: parent
                        anchors.topMargin: 3
                        anchors.bottomMargin: 3
                        radius: 2
                        color: span.target ? Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.10)
                                           : Qt.rgba(1, 1, 1, 0.03)
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
                            const props = rowItem.modelData.groupProps && !rowItem.modelData.axis
                                          ? rowItem.modelData.groupProps : [span.modelData.prop]
                            if (props.length > 1)
                                EditorState.beginEditSession(qsTr("Add keyframe"))
                            for (const prop of props)
                                EditorState.addClipKeyframeAt(root.trackIndex, span.modelData.clip, prop, at)
                            if (props.length > 1)
                                EditorState.endEditSession(true)
                        }
                        onClicked: {
                            root.tools.clear()
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
                            // Each axis key at this time (a joined line); one ref otherwise.
                            readonly property var refList: {
                                const refs = modelData.refs
                                if (!refs || refs.length === 0)
                                    return [{ clip: span.modelData.clip, prop: span.modelData.prop,
                                              seconds: modelData.seconds }]
                                return refs.map(r => ({ clip: span.modelData.clip, prop: r.prop,
                                                        seconds: r.seconds }))
                            }
                            readonly property var ref: refList[0]
                            readonly property bool atPlayhead: Math.abs(modelData.seconds - EditorState.playheadSeconds) < 1 / 120
                            readonly property var halves: root.tools.keyHalves(span.modelData.keys, index)
                            readonly property bool isPicked: {
                                void root.tools.keys
                                return root.tools.isPicked(root.trackIndex, ref)
                            }

                            width: 20
                            height: span.height
                            // Keys moved with others (a drag of several picked) ride the
                            // shared offset: the rows are frozen while it lasts.
                            readonly property real shiftDx: {
                                void root.tools.dragDelta
                                return root.tools.isShifted(root.trackIndex, ref)
                                       ? root.tools.dragDelta * root.pxPerSecond : 0
                            }
                            // Dragging several picked keys rather than this one alone.
                            property bool groupDrag: false
                            x: (modelData.seconds - span.modelData.start) * root.pxPerSecond
                               - width / 2 + dragDx + shiftDx
                            z: keyMouse.pressed || isPicked ? 2 : 1

                            // Under the playhead: a ring around it, the playhead line still showing.
                            Rectangle {
                                anchors.centerIn: parent
                                visible: keyItem.atPlayhead
                                width: 19
                                height: 19
                                rotation: 45
                                color: "transparent"
                                border.width: 1
                                border.color: Theme.primary
                            }

                            KeyframeGlyph {
                                anchors.centerIn: parent
                                pickedColor: Theme.primary
                                size: keyItem.isPicked ? 17 : (keyMouse.containsMouse ? 15 : 13)
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
                                    // The menu opens on release (onClicked), on the picked keys
                                    // when this is one of them.
                                    if (mouse.button === Qt.RightButton)
                                        return
                                    const ctrl = mouse.modifiers & Qt.ControlModifier
                                    const shift = mouse.modifiers & Qt.ShiftModifier
                                    // A joined key picks its axes' keys together, so they move as one.
                                    if (keyItem.refList.length > 1 && !ctrl && !shift)
                                        root.tools.pick(root.trackIndex, keyItem.refList)
                                    else
                                        root.tools.press(root.trackIndex, keyItem.ref, mouse.modifiers,
                                                         span.modelData.keys)
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
                                        keyItem.groupDrag = keyItem.isPicked && root.tools.keys.length > 1
                                        if (keyItem.groupDrag)
                                            root.tools.beginShift()
                                        else
                                            EditorState.beginPreviewDrag(qsTr("Move keyframe"))
                                    }
                                    if (keyItem.groupDrag) {
                                        const from = keyItem.modelData.seconds
                                        const moved = root.tools.shiftTo(
                                            EditorState.snapTime(from + dx / root.pxPerSecond) - from)
                                        EditorState.playheadSeconds = from + moved
                                        return
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
                                        root.trackIndex, span.modelData.clip, keyItem.ref.prop,
                                        keyItem.editSeconds, at, keyItem.modelData.value)
                                    keyItem.editSeconds = at
                                    keyItem.dragDx = (at - base) * root.pxPerSecond
                                    EditorState.playheadSeconds = at
                                }
                                onReleased: (mouse) => {
                                    if (mouse.button !== Qt.LeftButton)
                                        return
                                    if (keyItem.moved && keyItem.groupDrag) {
                                        // The picked keys stay picked at their new times.
                                        root.tools.endShift()
                                        keyItem.groupDrag = false
                                        root.dragging = false
                                    } else if (keyItem.moved) {
                                        EditorState.commitPreviewDrag()
                                        keyItem.dragDx = 0
                                        root.dragging = false
                                        // The moved key stays picked at its new time.
                                        root.tools.pick(root.trackIndex, [{ clip: span.modelData.clip,
                                                                           prop: keyItem.ref.prop,
                                                                           seconds: keyItem.editSeconds }])
                                    } else if (keyItem.dragArmed) {
                                        // A click: the clip and the playhead go to the key, so the
                                        // inspector shows the value it holds.
                                        EditorState.selectClip(root.trackIndex, span.modelData.clip)
                                        root.tools.pick(root.trackIndex, keyItem.refList)
                                        EditorState.playheadSeconds = keyItem.modelData.seconds
                                    }
                                }
                                onCanceled: {
                                    if (keyItem.moved && keyItem.groupDrag) {
                                        root.tools.endShift()
                                        keyItem.groupDrag = false
                                        root.dragging = false
                                    } else if (keyItem.moved) {
                                        EditorState.commitPreviewDrag()
                                        keyItem.dragDx = 0
                                        root.dragging = false
                                    }
                                }
                                onClicked: (mouse) => {
                                    if (mouse.button === Qt.RightButton && !keyItem.isPicked)
                                        root.tools.pick(root.trackIndex, keyItem.refList)
                                    if (mouse.button === Qt.RightButton)
                                        root.tools.openMenu(root.trackIndex, keyItem.ref, keyItem.halves,
                                                            !!keyItem.modelData.hold, false, keyItem,
                                                            Qt.point(keyItem.width / 2, keyItem.height))
                                }
                            }

                            ThemedToolTip {
                                visible: keyMouse.containsMouse && !keyMouse.pressed
                                text: root.rowLabel(rowItem.modelData) + " · "
                                      + keyItem.modelData.seconds.toFixed(2) + " s"
                                      + " · " + qsTr("right-click: Straight, Smooth, Hold, Curves")
                            }
                        }
                    }
                }
            }
        }
    }
}
