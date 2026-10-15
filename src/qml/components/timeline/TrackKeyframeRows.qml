import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// The rows a track unfolds into under its clips when the twirl in its header is open, as a
// layer's properties do in After Effects: one line per animated property, its keys drawn where
// they fall on the timeline. Keys are dragged to move them, double-click on a line adds one with
// the value the property already has there, and right-click shapes or removes a key. A key's
// glyph shows its shape: a diamond is linear, a round side eases, a square holds.
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
                        onClicked: EditorState.selectClip(root.trackIndex, span.modelData.clip)

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
                            readonly property bool easeIn: !modelData.hold && modelData.inDx < -1e-6
                                                           && Math.abs(modelData.inDy) < 1e-6
                            readonly property bool easeOut: !modelData.hold && modelData.outDx > 1e-6
                                                            && Math.abs(modelData.outDy) < 1e-6
                            readonly property real glyph: 10
                            readonly property bool atPlayhead:
                                Math.abs(EditorState.playheadSeconds - modelData.seconds) < 1 / 60

                            width: 14
                            height: span.height
                            x: (modelData.seconds - span.modelData.start) * root.pxPerSecond
                               - width / 2 + dragDx
                            z: keyMouse.pressed ? 2 : 1

                            // Each half of the glyph is its own shape: the left half is how the key
                            // is entered, the right half how it is left.
                            Repeater {
                                model: 2
                                delegate: Item {
                                    required property int index
                                    readonly property bool rightSide: index === 1
                                    readonly property bool eased: rightSide ? keyItem.easeOut : keyItem.easeIn
                                    x: rightSide ? keyItem.width / 2 : keyItem.width / 2 - keyItem.glyph / 2
                                    y: (keyItem.height - keyItem.glyph) / 2
                                    width: keyItem.glyph / 2
                                    height: keyItem.glyph
                                    clip: true

                                    Rectangle {
                                        // Centred on the key, so the clip shows one half of it.
                                        x: parent.rightSide ? -keyItem.glyph / 2 : 0
                                        width: keyItem.glyph
                                        height: keyItem.glyph
                                        rotation: keyItem.modelData.hold || parent.eased ? 0 : 45
                                        scale: keyItem.modelData.hold || parent.eased ? 0.9 : 0.72
                                        radius: parent.eased ? width / 2 : 1
                                        color: keyMouse.containsMouse || keyMouse.pressed || keyItem.atPlayhead
                                               ? Qt.lighter(span.keyColor, 1.35) : span.keyColor
                                        border.width: keyItem.atPlayhead ? 1.5 : 1
                                        border.color: keyItem.atPlayhead ? Theme.panelForeground
                                                                         : Qt.rgba(0, 0, 0, 0.55)
                                    }
                                }
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
                                    if (mouse.button !== Qt.LeftButton)
                                        return
                                    keyItem.pressX = mapToItem(root, mouse.x, mouse.y).x
                                    keyItem.editSeconds = keyItem.modelData.seconds
                                    keyItem.moved = false
                                }
                                onPositionChanged: (mouse) => {
                                    if (!pressed || !(mouse.buttons & Qt.LeftButton))
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
                                    } else {
                                        // A click: the clip and the playhead go to the key, so the
                                        // inspector shows the value it holds.
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
                            }

                            ThemedContextMenu {
                                id: keyMenu

                                function shape(mode) {
                                    EditorState.setKeyframeEasingAt(root.trackIndex, span.modelData.clip,
                                                                    span.modelData.prop,
                                                                    keyItem.modelData.seconds, mode)
                                }

                                ThemedMenuItem {
                                    text: qsTr("Linear")
                                    icon.name: !keyItem.modelData.hold && !keyItem.easeIn && !keyItem.easeOut
                                               && !keyItem.modelData.custom ? Theme.icons.check : ""
                                    onTriggered: keyMenu.shape("linear")
                                }
                                ThemedMenuItem {
                                    text: qsTr("Easy ease")
                                    icon.name: keyItem.easeIn && keyItem.easeOut ? Theme.icons.check : ""
                                    onTriggered: keyMenu.shape("ease")
                                }
                                ThemedMenuItem {
                                    text: qsTr("Easy ease in")
                                    icon.name: keyItem.easeIn && !keyItem.easeOut ? Theme.icons.check : ""
                                    onTriggered: keyMenu.shape("easeIn")
                                }
                                ThemedMenuItem {
                                    text: qsTr("Easy ease out")
                                    icon.name: keyItem.easeOut && !keyItem.easeIn ? Theme.icons.check : ""
                                    onTriggered: keyMenu.shape("easeOut")
                                }
                                ThemedMenuItem {
                                    text: qsTr("Hold")
                                    icon.name: keyItem.modelData.hold ? Theme.icons.check : ""
                                    onTriggered: keyMenu.shape("hold")
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
                                    text: qsTr("Delete keyframe")
                                    icon.name: Theme.icons.trash
                                    onTriggered: EditorState.removeClipKeyframe(
                                        root.trackIndex, span.modelData.clip, span.modelData.prop,
                                        keyItem.modelData.seconds)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
