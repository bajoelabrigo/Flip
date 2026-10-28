import QtQuick
import Drift
import ".."

// The preview toolbar's tools that work on the canvas (0.26), over the transform grips while one is
// on: Anchor point (drag the selected layer's anchor; the layer stays put), Shape (drag out a
// rectangle, ellipse, star or polygon; Shift keeps it square, Alt draws from the centre) and Text
// (click and type there). The pen has its own overlay.
Item {
    id: root

    // The selected clip's box from TransformOverlay (canvas px, with its on-screen quad), or null.
    property var box: null
    signal textEditRequested(int track, int clip)

    readonly property string tool: EditorState.preview.tool
    readonly property int canvasW: { void EditorState.tracksRevision; return Math.max(1, EditorState.projectFile.projectWidth()) }
    readonly property int canvasH: { void EditorState.tracksRevision; return Math.max(1, EditorState.projectFile.projectHeight()) }
    readonly property real sx: width / canvasW
    readonly property real sy: height / canvasH
    readonly property bool anchorReady: tool === "anchor" && !!box && !!box.quad && box.quad.length === 4
                                        && box.kind !== "transform"

    visible: tool === "shape" || tool === "text" || anchorReady
    enabled: visible && !EditorState.playing

    // Fractions of the box (0..1) ↔ overlay px, through the box's on-screen corners.
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

    // ----- Shape: the box being dragged out, in overlay px ------------------------------------
    property point dragFrom: Qt.point(0, 0)
    property rect dragRect: Qt.rect(0, 0, 0, 0)
    property bool dragging: false

    function shapeRect(from, to, shift, alt) {
        let dx = to.x - from.x
        let dy = to.y - from.y
        if (shift) {
            const m = Math.max(Math.abs(dx), Math.abs(dy))
            dx = dx < 0 ? -m : m
            dy = dy < 0 ? -m : m
        }
        if (alt)
            return Qt.rect(from.x - Math.abs(dx), from.y - Math.abs(dy), 2 * Math.abs(dx), 2 * Math.abs(dy))
        return Qt.rect(Math.min(from.x, from.x + dx), Math.min(from.y, from.y + dy), Math.abs(dx), Math.abs(dy))
    }

    Rectangle {
        visible: root.dragging && root.tool === "shape"
        x: root.dragRect.x
        y: root.dragRect.y
        width: root.dragRect.width
        height: root.dragRect.height
        radius: EditorState.preview.shapeToolKind === "ellipse" ? Math.min(width, height) / 2 : 0
        color: "transparent"
        border.width: 1.5
        border.color: Theme.primary
    }

    // ----- Anchor point -----------------------------------------------------------------------
    property point anchorLive: Qt.point(-1, -1)
    readonly property point anchorAt: {
        if (!anchorReady)
            return Qt.point(-100, -100)
        if (anchorLive.x >= 0)
            return anchorLive
        return boxToOverlay(box.anchorFx === undefined ? 0.5 : box.anchorFx, box.anchorFy === undefined ? 0.5 : box.anchorFy)
    }
    Item {
        visible: root.anchorReady
        x: root.anchorAt.x
        y: root.anchorAt.y
        Rectangle { x: -10; y: -0.75; width: 20; height: 1.5; color: Theme.primary }
        Rectangle { x: -0.75; y: -10; width: 1.5; height: 20; color: Theme.primary }
        Rectangle {
            x: -6; y: -6; width: 12; height: 12; radius: 6
            color: "transparent"; border.width: 1.5; border.color: Theme.primary
        }
    }

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: root.tool === "text" ? Qt.IBeamCursor : root.tool === "anchor" ? Qt.SizeAllCursor : Qt.CrossCursor

        onPressed: mouse => {
            if (root.tool === "shape") {
                root.dragFrom = Qt.point(mouse.x, mouse.y)
                root.dragRect = Qt.rect(mouse.x, mouse.y, 0, 0)
                root.dragging = true
            } else if (root.tool === "anchor") {
                root.anchorLive = Qt.point(mouse.x, mouse.y)
            }
        }
        onPositionChanged: mouse => {
            if (!pressed)
                return
            if (root.tool === "shape" && root.dragging)
                root.dragRect = root.shapeRect(root.dragFrom, Qt.point(mouse.x, mouse.y),
                                               mouse.modifiers & Qt.ShiftModifier, mouse.modifiers & Qt.AltModifier)
            else if (root.tool === "anchor")
                root.anchorLive = Qt.point(mouse.x, mouse.y)
        }
        onReleased: mouse => {
            if (root.tool === "shape" && root.dragging) {
                root.dragging = false
                const r = root.dragRect
                if (r.width < 4 || r.height < 4)
                    return
                EditorState.addDrawnShape(EditorState.preview.shapeToolKind, r.x / root.sx, r.y / root.sy,
                                          r.width / root.sx, r.height / root.sy, EditorState.preview.toolFill,
                                          EditorState.preview.toolStroke, EditorState.preview.toolStrokeWidth)
            } else if (root.tool === "anchor" && root.anchorReady) {
                const f = root.overlayToBox(mouse.x, mouse.y)
                root.anchorLive = Qt.point(-1, -1)
                EditorState.setAnchorKeepingPlace(root.box.track, root.box.clip, f.x, f.y)
            }
        }
        onClicked: mouse => {
            if (root.tool !== "text")
                return
            const made = EditorState.addTextAtPoint(mouse.x / root.sx, mouse.y / root.sy)
            if (made && made.track !== undefined) {
                // As After Effects: after placing one text, back to selection while you type.
                EditorState.preview.tool = "select"
                root.textEditRequested(made.track, made.clip)
            }
        }
    }
}
