import QtQuick
import Drift
import ".."

// After Effects' Pen tool and path editing (0.26), over the preview.
//
// Pen (EditorState.preview.penMode): a click puts a corner vertex, a press-and-drag pulls out its
// two handles; clicking the first vertex closes the outline, a double click or Enter leaves it
// open, Backspace takes the last vertex back and Escape gives up. The outline becomes a new shape.
//
// Path editing (EditorState.preview.pathEditMode, on a selected custom shape): its vertices and
// handles at the playhead, dragged where the shape's box sits on screen. Dragging a vertex
// carries its handles; a handle drags its partner opposite unless Alt is held; Alt+click on a
// vertex turns a smooth one into a corner and back; Ctrl+click removes it. With the Path
// stopwatch on, every edit is a key at the playhead.
Item {
    id: root

    // The selected clip's box from TransformOverlay (canvas px, with its on-screen quad), or null.
    property var box: null

    readonly property bool penActive: EditorState.preview.penMode
    readonly property int canvasW: { void EditorState.tracksRevision; return Math.max(1, EditorState.projectFile.projectWidth()) }
    readonly property int canvasH: { void EditorState.tracksRevision; return Math.max(1, EditorState.projectFile.projectHeight()) }
    readonly property real sx: width / canvasW
    readonly property real sy: height / canvasH

    // ----- Pen ------------------------------------------------------------------------------
    // [{x, y, ix, iy, ox, oy}] in canvas px.
    property var penPoints: []
    property point penCursor: Qt.point(-1, -1)
    property bool penDragging: false

    function toCanvas(p) { return Qt.point(p.x / root.sx, p.y / root.sy) }
    function finishPen(closed) {
        if (root.penPoints.length >= 2)
            EditorState.addPenShape(root.penPoints, closed && root.penPoints.length >= 3)
        root.penPoints = []
        EditorState.preview.penMode = false
    }
    function cancelPen() {
        root.penPoints = []
        EditorState.preview.penMode = false
    }
    onPenActiveChanged: {
        root.penPoints = []
        if (penActive)
            keyCatcher.forceActiveFocus()
    }

    // ----- Path editing ---------------------------------------------------------------------
    readonly property bool editActive: EditorState.preview.pathEditMode && !!box && box.kind === "shape"
                                       && !EditorState.playing && !penActive
    property int stateRevision: 0
    readonly property var pathState: {
        void root.stateRevision
        void EditorState.tracksRevision
        void EditorState.playheadSeconds
        return root.editActive ? EditorState.shapePathState(root.box.track, root.box.clip) : ({ editable: false })
    }
    readonly property bool editing: editActive && pathState.editable === true
    // The contours being dragged, edited in place and written back on every move.
    property var liveContours: null
    readonly property var contours: liveContours || (pathState.contours || [])

    // The box's quad on the overlay: fractions of the box (0..1) map through its three corners.
    readonly property var quad: box && box.quad && box.quad.length === 4 ? box.quad : null
    function boxToOverlay(u, v) {
        if (!root.quad)
            return Qt.point(0, 0)
        const a = root.quad[0], b = root.quad[1], d = root.quad[3]
        return Qt.point((a.x + (b.x - a.x) * u + (d.x - a.x) * v) * root.sx,
                        (a.y + (b.y - a.y) * u + (d.y - a.y) * v) * root.sy)
    }
    function overlayToBox(px, py) {
        const a = root.quad[0], b = root.quad[1], d = root.quad[3]
        const ux = (b.x - a.x) * root.sx, uy = (b.y - a.y) * root.sy
        const vx = (d.x - a.x) * root.sx, vy = (d.y - a.y) * root.sy
        const det = ux * vy - uy * vx
        if (Math.abs(det) < 1e-9)
            return Qt.point(0, 0)
        const qx = px - a.x * root.sx, qy = py - a.y * root.sy
        return Qt.point((qx * vy - qy * vx) / det, (ux * qy - uy * qx) / det)
    }
    function cloneContours(list) { return JSON.parse(JSON.stringify(list)) }

    // Which grip is under the pointer: {c, i, part: "point"|"in"|"out"} or null.
    function gripAt(px, py) {
        const r = 7
        let best = null
        let bestD = r * r
        for (let c = 0; c < root.contours.length; ++c) {
            const pts = root.contours[c].points
            for (let i = 0; i < pts.length; ++i) {
                const p = pts[i]
                for (const part of ["in", "out", "point"]) {
                    const u = part === "point" ? p.x : part === "in" ? p.ix : p.ox
                    const v = part === "point" ? p.y : part === "in" ? p.iy : p.oy
                    if (part !== "point" && Math.abs(u - p.x) < 1e-6 && Math.abs(v - p.y) < 1e-6)
                        continue
                    const o = root.boxToOverlay(u, v)
                    const d = (o.x - px) * (o.x - px) + (o.y - py) * (o.y - py)
                    if (d <= bestD) {
                        bestD = d
                        best = { c: c, i: i, part: part }
                    }
                }
            }
        }
        return best
    }

    visible: penActive || editing

    Item {
        id: keyCatcher
        focus: root.penActive
        Keys.onPressed: event => {
            if (!root.penActive)
                return
            if (event.key === Qt.Key_Escape) {
                root.cancelPen()
                event.accepted = true
            } else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                root.finishPen(false)
                event.accepted = true
            } else if (event.key === Qt.Key_Backspace || event.key === Qt.Key_Delete) {
                root.penPoints = root.penPoints.slice(0, -1)
                event.accepted = true
            }
        }
    }

    Canvas {
        id: drawing
        anchors.fill: parent
        renderStrategy: Canvas.Cooperative
        property var points: root.penActive ? root.penPoints : []
        property var shapes: root.editing ? root.contours : []
        property point cursor: root.penCursor
        onPointsChanged: requestPaint()
        onShapesChanged: requestPaint()
        onCursorChanged: if (root.penActive) requestPaint()
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()

        function grip(ctx, x, y, filled, size) {
            ctx.fillStyle = filled ? Theme.primary : "#ffffff"
            ctx.strokeStyle = Theme.primary
            ctx.lineWidth = 1.5
            ctx.fillRect(x - size / 2, y - size / 2, size, size)
            ctx.strokeRect(x - size / 2, y - size / 2, size, size)
        }
        function handle(ctx, x, y, hx, hy) {
            if (Math.abs(hx - x) < 0.5 && Math.abs(hy - y) < 0.5)
                return
            ctx.strokeStyle = Theme.primary
            ctx.lineWidth = 1
            ctx.beginPath()
            ctx.moveTo(x, y)
            ctx.lineTo(hx, hy)
            ctx.stroke()
            ctx.beginPath()
            ctx.arc(hx, hy, 3.5, 0, Math.PI * 2)
            ctx.fillStyle = "#ffffff"
            ctx.fill()
            ctx.stroke()
        }

        onPaint: {
            const ctx = getContext("2d")
            ctx.reset()
            if (root.penActive) {
                const pts = points
                const s = (p, k) => k === "p" ? Qt.point(p.x * root.sx, p.y * root.sy)
                                    : k === "i" ? Qt.point(p.ix * root.sx, p.iy * root.sy)
                                                : Qt.point(p.ox * root.sx, p.oy * root.sy)
                if (pts.length > 0) {
                    ctx.strokeStyle = Theme.primary
                    ctx.lineWidth = 2
                    ctx.beginPath()
                    const f = s(pts[0], "p")
                    ctx.moveTo(f.x, f.y)
                    for (let i = 1; i < pts.length; ++i) {
                        const o = s(pts[i - 1], "o"), n = s(pts[i], "i"), p = s(pts[i], "p")
                        ctx.bezierCurveTo(o.x, o.y, n.x, n.y, p.x, p.y)
                    }
                    if (!root.penDragging && cursor.x >= 0) {
                        const o = s(pts[pts.length - 1], "o")
                        ctx.bezierCurveTo(o.x, o.y, cursor.x, cursor.y, cursor.x, cursor.y)
                    }
                    ctx.stroke()
                    for (let i = 0; i < pts.length; ++i) {
                        const p = s(pts[i], "p")
                        handle(ctx, p.x, p.y, s(pts[i], "i").x, s(pts[i], "i").y)
                        handle(ctx, p.x, p.y, s(pts[i], "o").x, s(pts[i], "o").y)
                        grip(ctx, p.x, p.y, i === 0, i === 0 ? 9 : 7)
                    }
                }
                return
            }
            for (const contour of shapes) {
                const pts = contour.points
                if (!pts || pts.length === 0)
                    continue
                const at = (u, v) => root.boxToOverlay(u, v)
                ctx.strokeStyle = Theme.primary
                ctx.lineWidth = 1.5
                ctx.beginPath()
                const f = at(pts[0].x, pts[0].y)
                ctx.moveTo(f.x, f.y)
                const segs = contour.closed ? pts.length : pts.length - 1
                for (let i = 0; i < segs; ++i) {
                    const a = pts[i], b = pts[(i + 1) % pts.length]
                    const o = at(a.ox, a.oy), n = at(b.ix, b.iy), p = at(b.x, b.y)
                    ctx.bezierCurveTo(o.x, o.y, n.x, n.y, p.x, p.y)
                }
                ctx.stroke()
                for (const p of pts) {
                    const o = at(p.x, p.y)
                    handle(ctx, o.x, o.y, at(p.ix, p.iy).x, at(p.ix, p.iy).y)
                    handle(ctx, o.x, o.y, at(p.ox, p.oy).x, at(p.ox, p.oy).y)
                    grip(ctx, o.x, o.y, false, 7)
                }
            }
        }
    }

    // The pen's pointer.
    MouseArea {
        anchors.fill: parent
        enabled: root.penActive
        visible: enabled
        hoverEnabled: true
        cursorShape: Qt.CrossCursor
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        property point pressAt

        onPositionChanged: mouse => {
            root.penCursor = Qt.point(mouse.x, mouse.y)
            if (!pressed || root.penPoints.length === 0 || !root.penDragging)
                return
            // Dragging out of a fresh vertex pulls its handles: out where the pointer is, in opposite.
            const pts = root.penPoints.slice()
            const last = Object.assign({}, pts[pts.length - 1])
            const c = root.toCanvas(Qt.point(mouse.x, mouse.y))
            last.ox = c.x
            last.oy = c.y
            last.ix = 2 * last.x - c.x
            last.iy = 2 * last.y - c.y
            pts[pts.length - 1] = last
            root.penPoints = pts
        }
        onPressed: mouse => {
            keyCatcher.forceActiveFocus()
            if (mouse.button === Qt.RightButton) {
                root.finishPen(false)
                return
            }
            const pts = root.penPoints
            if (pts.length >= 3) {
                const first = pts[0]
                const dx = first.x * root.sx - mouse.x, dy = first.y * root.sy - mouse.y
                if (dx * dx + dy * dy <= 81) {
                    root.finishPen(true)
                    return
                }
            }
            const c = root.toCanvas(Qt.point(mouse.x, mouse.y))
            root.penPoints = pts.concat([{ x: c.x, y: c.y, ix: c.x, iy: c.y, ox: c.x, oy: c.y }])
            root.penDragging = true
        }
        onReleased: root.penDragging = false
        onDoubleClicked: mouse => {
            // The double click's second press added a vertex on top of the last one: drop it.
            if (root.penPoints.length > 2)
                root.penPoints = root.penPoints.slice(0, -1)
            root.finishPen(false)
        }
        onExited: root.penCursor = Qt.point(-1, -1)
    }

    // Grips of the path being edited: only they take the pointer, the rest goes to the boxes below.
    MouseArea {
        id: editArea
        anchors.fill: parent
        enabled: root.editing
        visible: enabled
        hoverEnabled: true
        property var grab: null
        property point last

        // Clicks off the grips fall through to the preview, so the shape can still be moved.
        function hit(mouse) {
            return root.gripAt(mouse.x, mouse.y)
        }
        onPressed: mouse => {
            const g = hit(mouse)
            if (!g) {
                mouse.accepted = false
                return
            }
            const list = root.cloneContours(root.contours)
            const pts = list[g.c].points
            if (g.part === "point" && (mouse.modifiers & Qt.ControlModifier)) {
                if (pts.length > 2) {
                    pts.splice(g.i, 1)
                    EditorState.setShapePathPoints(root.box.track, root.box.clip, list)
                }
                return
            }
            if (g.part === "point" && (mouse.modifiers & Qt.AltModifier)) {
                const p = pts[g.i]
                const corner = Math.abs(p.ix - p.x) < 1e-6 && Math.abs(p.iy - p.y) < 1e-6
                               && Math.abs(p.ox - p.x) < 1e-6 && Math.abs(p.oy - p.y) < 1e-6
                if (corner) {
                    // Smooth again: handles along the line between its neighbours, a third of the way.
                    const prev = pts[(g.i - 1 + pts.length) % pts.length]
                    const next = pts[(g.i + 1) % pts.length]
                    const tx = (next.x - prev.x) / 6, ty = (next.y - prev.y) / 6
                    p.ix = p.x - tx; p.iy = p.y - ty
                    p.ox = p.x + tx; p.oy = p.y + ty
                } else {
                    p.ix = p.x; p.iy = p.y
                    p.ox = p.x; p.oy = p.y
                }
                EditorState.setShapePathPoints(root.box.track, root.box.clip, list)
                return
            }
            grab = { c: g.c, i: g.i, part: g.part, alt: (mouse.modifiers & Qt.AltModifier) !== 0 }
            last = Qt.point(mouse.x, mouse.y)
            root.liveContours = list
            EditorState.beginPreviewDrag(qsTr("Path edited"))
        }
        onPositionChanged: mouse => {
            if (!grab || !root.liveContours)
                return
            const list = root.cloneContours(root.liveContours)
            const p = list[grab.c].points[grab.i]
            const now = root.overlayToBox(mouse.x, mouse.y)
            const was = root.overlayToBox(last.x, last.y)
            const dx = now.x - was.x, dy = now.y - was.y
            if (grab.part === "point") {
                p.x += dx; p.y += dy
                p.ix += dx; p.iy += dy
                p.ox += dx; p.oy += dy
            } else {
                const mine = grab.part === "in" ? ["ix", "iy"] : ["ox", "oy"]
                const other = grab.part === "in" ? ["ox", "oy"] : ["ix", "iy"]
                p[mine[0]] += dx
                p[mine[1]] += dy
                if (!grab.alt) {
                    // The partner stays opposite, keeping its own length.
                    const len = Math.hypot(p[other[0]] - p.x, p[other[1]] - p.y)
                    const ax = p.x - p[mine[0]], ay = p.y - p[mine[1]]
                    const al = Math.hypot(ax, ay)
                    if (al > 1e-9 && len > 1e-9) {
                        p[other[0]] = p.x + ax / al * len
                        p[other[1]] = p.y + ay / al * len
                    }
                }
            }
            last = Qt.point(mouse.x, mouse.y)
            root.liveContours = list
            EditorState.setShapePathPoints(root.box.track, root.box.clip, list)
        }
        onReleased: {
            if (!grab)
                return
            grab = null
            EditorState.commitPreviewDrag()
            root.liveContours = null
            root.stateRevision++
        }
        onCanceled: {
            grab = null
            EditorState.cancelPreviewDrag()
            root.liveContours = null
        }
    }
}
