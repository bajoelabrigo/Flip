import QtQuick
import Drift
import ".."

// After Effects' gradient handles (0.29): with the selection tool, a shape or text painted with a
// gradient shows its two points on the video — where the first and last colour sit (linear), or
// the centre and the radius / start direction (radial, sweep). Dragging one rewrites the gradient's
// angle, scale, offset and centre as one undo step; with the property's stopwatch on, as a key.
Item {
    id: root

    // The selected clip's box from TransformOverlay (canvas px, with its on-screen quad), or null.
    property var box: null

    readonly property int canvasW: { void EditorState.tracksRevision; return Math.max(1, EditorState.projectFile.projectWidth()) }
    readonly property int canvasH: { void EditorState.tracksRevision; return Math.max(1, EditorState.projectFile.projectHeight()) }
    readonly property real sx: width / canvasW
    readonly property real sy: height / canvasH
    readonly property bool boxReady: !!box && !!box.quad && box.quad.length === 4 && box.kind !== "transform"
    readonly property var handles: {
        void EditorState.tracksRevision
        void EditorState.selectedClipData
        void EditorState.playheadSeconds
        if (!boxReady || EditorState.preview.tool !== "select")
            return null
        const h = EditorState.gradientHandles(box.track, box.clip)
        return h && h.layerId ? h : null
    }

    // The points while one is dragged (box fractions), so they follow the pointer at once.
    property int dragging: -1
    property point live0: Qt.point(0, 0)
    property point live1: Qt.point(1, 1)
    readonly property point p0: dragging >= 0 ? live0 : (handles ? Qt.point(handles.x0, handles.y0) : Qt.point(0, 0))
    readonly property point p1: dragging >= 0 ? live1 : (handles ? Qt.point(handles.x1, handles.y1) : Qt.point(1, 1))
    readonly property point s0: boxReady ? boxToOverlay(p0.x, p0.y) : Qt.point(0, 0)
    readonly property point s1: boxReady ? boxToOverlay(p1.x, p1.y) : Qt.point(0, 0)

    visible: !!handles && !EditorState.playing

    function boxToOverlay(u, v) {
        const a = box.quad[0], b = box.quad[1], d = box.quad[3]
        return Qt.point((a.x + (b.x - a.x) * u + (d.x - a.x) * v) * sx, (a.y + (b.y - a.y) * u + (d.y - a.y) * v) * sy)
    }
    function overlayToBox(px, py) {
        const a = box.quad[0], b = box.quad[1], d = box.quad[3]
        const ux = (b.x - a.x) * sx, uy = (b.y - a.y) * sy
        const vx = (d.x - a.x) * sx, vy = (d.y - a.y) * sy
        const det = ux * vy - uy * vx
        if (Math.abs(det) < 1e-9)
            return Qt.point(0.5, 0.5)
        const qx = px - a.x * sx, qy = py - a.y * sy
        return Qt.point((qx * vy - qy * vx) / det, (ux * qy - uy * qx) / det)
    }

    // The axis between the two points, as AE draws it.
    Canvas {
        id: axis
        anchors.fill: parent
        onPaint: {
            const ctx = getContext("2d")
            ctx.reset()
            if (!root.handles)
                return
            ctx.lineWidth = 1.5
            ctx.strokeStyle = "#f0f0f0"
            ctx.setLineDash([5, 4])
            ctx.beginPath()
            if (root.handles.kind === "radial") {
                const r = Math.hypot(root.s1.x - root.s0.x, root.s1.y - root.s0.y)
                ctx.arc(root.s0.x, root.s0.y, r, 0, Math.PI * 2)
            }
            ctx.moveTo(root.s0.x, root.s0.y)
            ctx.lineTo(root.s1.x, root.s1.y)
            ctx.stroke()
        }
        Connections {
            target: root
            function onS0Changed() { axis.requestPaint() }
            function onS1Changed() { axis.requestPaint() }
            function onHandlesChanged() { axis.requestPaint() }
        }
    }

    Repeater {
        model: 2
        Rectangle {
            id: grip
            required property int index
            readonly property point at: index === 0 ? root.s0 : root.s1
            width: 14
            height: 14
            radius: index === 0 ? 7 : 2
            x: at.x - width / 2
            y: at.y - height / 2
            color: index === 0 ? "#ffffff" : "#202020"
            border.width: 2
            border.color: index === 0 ? "#202020" : "#ffffff"

            MouseArea {
                id: gripMouse
                anchors.fill: parent
                anchors.margins: -6
                hoverEnabled: true
                cursorShape: Qt.SizeAllCursor
                preventStealing: true
                property point grab: Qt.point(0, 0)
                onPressed: mouse => {
                    const p = mapToItem(root, mouse.x, mouse.y)
                    grab = Qt.point(grip.at.x - p.x, grip.at.y - p.y)
                    root.live0 = root.p0
                    root.live1 = root.p1
                    root.dragging = grip.index
                    EditorState.beginPreviewDrag(qsTr("Move gradient"))
                }
                onPositionChanged: mouse => {
                    if (root.dragging !== grip.index)
                        return
                    const p = mapToItem(root, mouse.x, mouse.y)
                    const f = root.overlayToBox(p.x + grab.x, p.y + grab.y)
                    if (grip.index === 0) {
                        // The centre of a radial or sweep carries its radius handle along with it.
                        if (root.handles.kind !== "linear")
                            root.live1 = Qt.point(root.live1.x + f.x - root.live0.x, root.live1.y + f.y - root.live0.y)
                        root.live0 = f
                    } else {
                        root.live1 = f
                    }
                    EditorState.previewGradientHandles(root.box.track, root.box.clip, root.handles.layerId,
                                                       root.live0.x, root.live0.y, root.live1.x, root.live1.y)
                }
                onReleased: {
                    if (root.dragging === grip.index)
                        EditorState.commitPreviewDrag()
                    root.dragging = -1
                }
                onCanceled: {
                    if (root.dragging === grip.index)
                        EditorState.cancelPreviewDrag()
                    root.dragging = -1
                }
            }
            ThemedToolTip {
                visible: gripMouse.containsMouse && root.dragging < 0
                text: grip.index === 0
                      ? (root.handles && root.handles.kind !== "linear" ? qsTr("Gradient centre: drag to move it")
                                                                       : qsTr("Gradient start: drag to move it"))
                      : (root.handles && root.handles.kind === "radial" ? qsTr("Gradient radius: drag to resize it")
                                                                        : qsTr("Gradient end: drag to move it"))
            }
        }
    }
}
