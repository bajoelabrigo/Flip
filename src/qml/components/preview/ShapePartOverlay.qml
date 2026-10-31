import QtQuick
import QtQuick.Shapes
import Drift
import ".."

// After Effects' parts on the preview (0.28 stage 4), inside a selected shape layer's box: the picked part's
// outline with its own grips (drag inside to move it, a corner to scale it, Shift for both sides alike, the
// round grip to turn it, Shift in 15° steps), and the part under the pointer outlined faintly at the level
// being worked on. Double-click enters (a part, or a group's parts); a click picks a part beside the picked
// one, or goes back to the layer; Esc goes up a level. Everything in fractions of the layer's box, as
// AppController::shapePartFrames gives them, so it follows the box however it is turned or tilted.
Item {
    id: parts

    property int track: -1
    property int clip: -1
    // The box is selected, flat, and the editor is in Pro.
    property bool live: false

    // Bumped when anything the frames read changes (an edit, a preview drag, the playhead).
    property int rev: 0
    readonly property var frames: {
        void parts.rev
        void EditorState.tracksRevision
        void EditorState.playheadSeconds
        return parts.live && parts.track >= 0 ? EditorState.shapePartFrames(parts.track, parts.clip) : []
    }
    readonly property bool active: frames.length > 0
    readonly property string focusId: active ? EditorState.selectedShapePart : ""
    readonly property var focusFrame: frameOf(focusId)
    property string hoverId: ""

    Connections {
        target: EditorState
        function onClipPropertiesPreviewed() { parts.rev++ }
        function onSelectedShapePartChanged() { parts.rev++ }
    }

    function frameOf(id) {
        if (!id)
            return null
        for (const f of parts.frames) {
            if (f.id === id)
                return f
        }
        return null
    }

    // Point in a frame's quad (fractions; an affine map keeps a convex quad convex, so the sign test holds).
    function inside(f, fx, fy) {
        const p = f.pts
        let sign = 0
        for (let i = 0; i < 4; ++i) {
            const ax = p[2 * i], ay = p[2 * i + 1]
            const bx = p[(2 * i + 2) % 8], by = p[(2 * i + 3) % 8]
            const c = (bx - ax) * (fy - ay) - (by - ay) * (fx - ax)
            if (Math.abs(c) < 1e-12)
                continue
            const s = c > 0 ? 1 : -1
            if (sign === 0)
                sign = s
            else if (s !== sign)
                return false
        }
        return true
    }

    // The top-most visible part of a level (parent id; "" the layer's own) under a point.
    function hitAt(level, fx, fy) {
        for (const f of parts.frames) {
            if (f.parent === level && f.visible && inside(f, fx, fy))
                return f
        }
        return null
    }

    // The level a click works on: the picked group's parts, or the picked part's neighbours.
    function workingLevel() {
        const f = parts.focusFrame
        if (!f)
            return ""
        return f.group ? f.id : f.parent
    }

    function pick(id) {
        EditorState.selectShapePart(parts.track, parts.clip, id || "")
    }

    // Double-click: in a step (the layer's parts, then a group's), or onto the part beside.
    function enterAt(fx, fy) {
        if (!parts.active)
            return false
        let hit = hitAt(workingLevel(), fx, fy)
        if (!hit && workingLevel() !== "")
            hit = hitAt("", fx, fy)
        if (!hit)
            return false
        pick(hit.id)
        return true
    }

    // A single click while inside: a part at the same level, or back to the whole layer.
    function clickAt(fx, fy) {
        const f = parts.focusFrame
        if (!f)
            return
        if (inside(f, fx, fy))
            return
        const hit = hitAt(f.parent, fx, fy)
        pick(hit ? hit.id : "")
    }

    function goUp() {
        const f = parts.focusFrame
        if (!f)
            return false
        pick(f.parent)
        return true
    }

    function frac(item, x, y) {
        const p = item.mapToItem(parts, x, y)
        return Qt.point(p.x / Math.max(1, parts.width), p.y / Math.max(1, parts.height))
    }

    // Fractions -> the part's parent units, through the inverse of the parent's linear map.
    function toParent(f, dx, dy) {
        const m11 = f.lin[0], m12 = f.lin[1], m21 = f.lin[2], m22 = f.lin[3]
        const det = m11 * m22 - m21 * m12
        if (Math.abs(det) < 1e-12)
            return Qt.point(0, 0)
        return Qt.point((m22 * dx - m21 * dy) / det, (-m12 * dx + m11 * dy) / det)
    }

    function setValue(id, field, value) {
        EditorState.previewSetPropertyValue(parts.track, parts.clip, "part." + id + "." + field,
                                            EditorState.playheadSeconds, value)
    }

    // The quad of a frame in this item's pixels.
    function corner(f, i) {
        return Qt.point(f.pts[2 * i] * parts.width, f.pts[2 * i + 1] * parts.height)
    }

    visible: active

    // The part the pointer is over, at the working level: where a double-click goes.
    HoverHandler {
        id: hoverWatch
        enabled: parts.active
        onPointChanged: {
            const fx = hoverWatch.point.position.x / Math.max(1, parts.width)
            const fy = hoverWatch.point.position.y / Math.max(1, parts.height)
            const hit = parts.hitAt(parts.workingLevel(), fx, fy) || parts.hitAt("", fx, fy)
            parts.hoverId = hit ? hit.id : ""
        }
        onHoveredChanged: {
            if (!hovered)
                parts.hoverId = ""
        }
    }

    // The hovered part, faint.
    Shape {
        id: hoverOutline
        anchors.fill: parent
        readonly property var f: parts.hoverId !== parts.focusId ? parts.frameOf(parts.hoverId) : null
        visible: f !== null
        ShapePath {
            strokeColor: Theme.guideStrong
            strokeWidth: 1
            strokeStyle: ShapePath.DashLine
            dashPattern: [3, 3]
            fillColor: "transparent"
            PathPolyline {
                path: {
                    const f = hoverOutline.f
                    if (!f)
                        return []
                    const out = []
                    for (let i = 0; i <= 4; ++i)
                        out.push(parts.corner(f, i % 4))
                    return out
                }
            }
        }
    }

    // The picked part: its outline.
    Shape {
        id: focusOutline
        anchors.fill: parent
        visible: parts.focusFrame !== null
        ShapePath {
            strokeColor: Theme.clipTransform
            strokeWidth: 2
            fillColor: "transparent"
            PathPolyline {
                path: {
                    const f = parts.focusFrame
                    if (!f)
                        return []
                    const out = []
                    for (let i = 0; i <= 4; ++i)
                        out.push(parts.corner(f, i % 4))
                    return out
                }
            }
        }
    }

    // Drag inside the picked part: moves it (its own Position). Presses elsewhere go through to the layer.
    MouseArea {
        id: moveArea
        // Over the picked part's own box (it can lie outside the layer's box), a little larger.
        readonly property rect span: {
            const f = parts.focusFrame
            if (!f)
                return Qt.rect(0, 0, 0, 0)
            let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9
            for (let i = 0; i < 4; ++i) {
                const c = parts.corner(f, i)
                x0 = Math.min(x0, c.x); y0 = Math.min(y0, c.y); x1 = Math.max(x1, c.x); y1 = Math.max(y1, c.y)
            }
            return Qt.rect(x0 - 8, y0 - 8, x1 - x0 + 16, y1 - y0 + 16)
        }
        x: span.x
        y: span.y
        width: span.width
        height: span.height
        enabled: parts.focusFrame !== null
        // The layer's own drag (a DragHandler on the box) would take the gesture over once it moves and drag
        // the whole layer: the part keeps it.
        preventStealing: true
        cursorShape: containsPress ? Qt.SizeAllCursor : Qt.ArrowCursor
        property var start: null
        onPressed: mouse => {
            const p = parts.frac(moveArea, mouse.x, mouse.y)
            const f = parts.focusFrame
            if (!f || !parts.inside(f, p.x, p.y)) {
                mouse.accepted = false
                return
            }
            moveArea.start = { "p": p, "f": f, "moved": false }
        }
        onPositionChanged: mouse => {
            const s = moveArea.start
            if (!s)
                return
            const p = parts.frac(moveArea, mouse.x, mouse.y)
            if (!s.moved) {
                EditorState.beginPreviewDrag(qsTr("Move part"))
                s.moved = true
            }
            const d = parts.toParent(s.f, p.x - s.p.x, p.y - s.p.y)
            parts.setValue(s.f.id, "x", s.f.x + d.x)
            parts.setValue(s.f.id, "y", s.f.y + d.y)
        }
        // Inside the picked part: a double-click goes one step in (a group's parts).
        onDoubleClicked: mouse => {
            const p = parts.frac(moveArea, mouse.x, mouse.y)
            parts.enterAt(p.x, p.y)
        }
        onReleased: {
            if (moveArea.start && moveArea.start.moved)
                EditorState.commitPreviewDrag()
            moveArea.start = null
        }
        onCanceled: {
            if (moveArea.start && moveArea.start.moved)
                EditorState.commitPreviewDrag()
            moveArea.start = null
        }
    }

    // The anchor of the picked part: a small crosshair, as the layer's.
    Item {
        visible: parts.focusFrame !== null
        x: parts.focusFrame ? parts.focusFrame.anchor[0] * parts.width : 0
        y: parts.focusFrame ? parts.focusFrame.anchor[1] * parts.height : 0
        Rectangle { x: -6; y: -0.5; width: 12; height: 1; color: Theme.clipTransform }
        Rectangle { x: -0.5; y: -6; width: 1; height: 12; color: Theme.clipTransform }
    }

    // Grips: the four corners scale, the round one turns. Each solved around the part's anchor.
    Repeater {
        model: parts.focusFrame ? 5 : 0
        delegate: Rectangle {
            id: grip
            required property int index
            readonly property bool turn: index === 4
            readonly property point at: {
                const f = parts.focusFrame
                if (!f)
                    return Qt.point(0, 0)
                if (!turn)
                    return parts.corner(f, index)
                // The round grip, off the middle of the top edge, away from the centre.
                const a = parts.corner(f, 0), b = parts.corner(f, 1)
                const c = parts.corner(f, 2), d = parts.corner(f, 3)
                const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2
                const cx = (a.x + c.x) / 2, cy = (a.y + c.y) / 2
                const len = Math.max(1, Math.hypot(mx - cx, my - cy))
                return Qt.point(mx + (mx - cx) / len * 26, my + (my - cy) / len * 26)
            }
            x: at.x - width / 2
            y: at.y - height / 2
            width: turn ? 12 : 10
            height: width
            radius: turn ? width / 2 : 2
            color: Theme.onMedia
            border.width: 1.5
            border.color: Theme.clipTransform
            z: 3

            MouseArea {
                id: gripArea
                anchors.fill: parent
                anchors.margins: -6
                preventStealing: true
                cursorShape: grip.turn ? Qt.CrossCursor : Qt.SizeFDiagCursor
                property var start: null
                function offset(mouse) {
                    const p = parts.frac(gripArea, mouse.x, mouse.y)
                    const f = start.f
                    return parts.toParent(f, p.x - f.anchor[0], p.y - f.anchor[1])
                }
                onPressed: mouse => {
                    const f = parts.focusFrame
                    start = { "f": f }
                    start.q0 = offset(mouse)
                    EditorState.beginPreviewDrag(grip.turn ? qsTr("Rotate part") : qsTr("Scale part"))
                }
                onPositionChanged: mouse => {
                    if (!start)
                        return
                    const f = start.f
                    const q = offset(mouse)
                    const q0 = start.q0
                    if (grip.turn) {
                        let deg = f.rotation + (Math.atan2(q.y, q.x) - Math.atan2(q0.y, q0.x)) * 180 / Math.PI
                        if (mouse.modifiers & Qt.ShiftModifier)
                            deg = Math.round(deg / 15) * 15
                        parts.setValue(f.id, "rotation", deg)
                        return
                    }
                    let kx = 1, ky = 1
                    if (mouse.modifiers & Qt.ShiftModifier) {
                        const k = Math.hypot(q.x, q.y) / Math.max(1e-9, Math.hypot(q0.x, q0.y))
                        kx = k
                        ky = k
                    } else {
                        // Along the part's own axes, so a turned part stretches the way it points.
                        const r = f.rotation * Math.PI / 180
                        const ex = Qt.point(Math.cos(r), Math.sin(r))
                        const ey = Qt.point(-Math.sin(r), Math.cos(r))
                        const a0x = q0.x * ex.x + q0.y * ex.y, a0y = q0.x * ey.x + q0.y * ey.y
                        const ax = q.x * ex.x + q.y * ex.y, ay = q.x * ey.x + q.y * ey.y
                        if (Math.abs(a0x) > 1e-9)
                            kx = ax / a0x
                        if (Math.abs(a0y) > 1e-9)
                            ky = ay / a0y
                    }
                    parts.setValue(f.id, "scaleX", f.scaleX * kx)
                    parts.setValue(f.id, "scaleY", f.scaleY * ky)
                }
                onReleased: {
                    if (start)
                        EditorState.commitPreviewDrag()
                    start = null
                }
                onCanceled: {
                    if (start)
                        EditorState.commitPreviewDrag()
                    start = null
                }
                // A grip taken away mid-drag (the part let go) closes its drag, or it stayed open and the
                // next edit joined its undo step.
                Component.onDestruction: {
                    if (start)
                        EditorState.commitPreviewDrag()
                }
            }
        }
    }
}
