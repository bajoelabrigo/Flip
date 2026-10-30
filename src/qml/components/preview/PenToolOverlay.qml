import QtQuick
import Drift
import ".."

// After Effects' Pen tool and path editing (0.26), over the preview — as AE does it (Jorge: «investiga
// cómo funciona el tema de formas en After Effects y replícalo»).
//
// Pen (EditorState.preview.penMode):
//   - the first click makes the shape layer at once (it is on the timeline while you draw);
//   - click = a corner vertex; click and drag = a smooth one, its handles pulled out (Alt while
//     dragging moves only the outgoing handle, Shift keeps the angle to 45° steps);
//   - clicking the first vertex closes the path (dragging there sets its handles);
//   - Enter, Escape, a double click or a right click ends an open path, keeping it; Backspace takes
//     the last vertex back; Escape with nothing being drawn leaves the Pen;
//   - with a shape selected: a click on a segment adds a vertex there without changing the curve,
//     Ctrl+click on a vertex deletes it, Alt+click turns it corner <-> smooth, Alt+drag from it pulls
//     new handles, a click on an end of an open path carries it on, and a click elsewhere starts
//     another path in the same layer.
// Path editing (EditorState.preview.pathEditMode, the Selection tool): click a vertex to select it,
// Shift+click to add or remove one, drag a box round several; dragging moves every selected one;
// Delete removes them; the arrows nudge them (Shift: 10 px); dragging a segment bends it; handles
// keep their partner opposite unless Alt is held; Ctrl+A selects them all; Escape ends editing.
// With the Path stopwatch on, every edit is a key at the playhead.
Item {
    id: root

    // The selected clip's box from TransformOverlay (canvas px, with its on-screen quad), or null.
    property var box: null

    readonly property bool penActive: EditorState.preview.penMode
    readonly property int canvasW: { void EditorState.tracksRevision; return Math.max(1, EditorState.projectFile.projectWidth()) }
    readonly property int canvasH: { void EditorState.tracksRevision; return Math.max(1, EditorState.projectFile.projectHeight()) }
    readonly property real sx: width / canvasW
    readonly property real sy: height / canvasH

    // ----- The shape being drawn or edited -----------------------------------------------------
    property int stateRevision: 0
    readonly property bool targetIsShape: !!box && box.kind === "shape" && !EditorState.playing
    readonly property var pathState: {
        void root.stateRevision
        void EditorState.tracksRevision
        void EditorState.playheadSeconds
        return root.targetIsShape ? EditorState.shapePathState(root.box.track, root.box.clip) : ({ editable: false })
    }
    readonly property bool targetEditable: targetIsShape && pathState.editable === true
    // Points show while editing, and with the Pen over a selected shape (to add, delete, carry on).
    readonly property bool showPath: (EditorState.preview.pathEditMode && targetEditable) || (penActive && (targetEditable || drawing !== null))

    // The contours edited in place (fractions of the box), written back on every change.
    property var liveContours: null
    readonly property var contours: liveContours || (pathState.contours || [])
    // While drawing: {c: contour index, fresh: a layer made by this stroke (its box is the canvas)}.
    property var drawing: null
    // Selected vertices: ["c:i", ...].
    property var selected: []
    property point cursor: Qt.point(-1, -1)
    property var marquee: null

    function isSelected(c, i) { return root.selected.indexOf(c + ":" + i) >= 0 }

    // The box's quad on the overlay: fractions of the box (0..1) map through its three corners. A
    // fresh pen layer's box is the canvas until the overlay catches up.
    readonly property var quad: box && box.quad && box.quad.length === 4 ? box.quad : null
    function corners() {
        if (root.drawing && root.drawing.fresh || !root.quad)
            return [Qt.point(0, 0), Qt.point(root.canvasW, 0), Qt.point(root.canvasW, root.canvasH), Qt.point(0, root.canvasH)]
        return root.quad
    }
    function boxToOverlay(u, v) {
        const q = root.corners()
        const a = q[0], b = q[1], d = q[3]
        return Qt.point((a.x + (b.x - a.x) * u + (d.x - a.x) * v) * root.sx,
                        (a.y + (b.y - a.y) * u + (d.y - a.y) * v) * root.sy)
    }
    function overlayToBox(px, py) {
        const q = root.corners()
        const a = q[0], b = q[1], d = q[3]
        const ux = (b.x - a.x) * root.sx, uy = (b.y - a.y) * root.sy
        const vx = (d.x - a.x) * root.sx, vy = (d.y - a.y) * root.sy
        const det = ux * vy - uy * vx
        if (Math.abs(det) < 1e-9)
            return Qt.point(0, 0)
        const qx = px - a.x * root.sx, qy = py - a.y * root.sy
        return Qt.point((qx * vy - qy * vx) / det, (ux * qy - uy * qx) / det)
    }
    // One overlay pixel in box fractions, along x and y (for nudging).
    function pixelInBox() {
        const o = root.overlayToBox(0, 0), x = root.overlayToBox(1, 0), y = root.overlayToBox(0, 1)
        return { x: Math.hypot(x.x - o.x, x.y - o.y), y: Math.hypot(y.x - o.x, y.y - o.y) }
    }
    function cloneContours(list) { return JSON.parse(JSON.stringify(list)) }
    function vertex(p) { return { x: p.x, y: p.y, ix: p.x, iy: p.y, ox: p.x, oy: p.y } }
    function isCorner(p) {
        return Math.abs(p.ix - p.x) < 1e-6 && Math.abs(p.iy - p.y) < 1e-6
               && Math.abs(p.ox - p.x) < 1e-6 && Math.abs(p.oy - p.y) < 1e-6
    }

    function write(list) {
        root.liveContours = list
        const t = EditorState.selectedTrack, c = EditorState.selectedClip
        if (t >= 0 && c >= 0)
            EditorState.setShapePathPoints(t, c, list)
    }

    // ----- Hit testing -------------------------------------------------------------------------
    // A vertex or a handle under (px, py): {c, i, part: "point"|"in"|"out"} or null.
    function gripAt(px, py) {
        const r = 8
        let best = null
        let bestD = r * r
        for (let c = 0; c < root.contours.length; ++c) {
            const pts = root.contours[c].points
            for (let i = 0; i < pts.length; ++i) {
                const p = pts[i]
                for (const part of ["point", "in", "out"]) {
                    const u = part === "point" ? p.x : part === "in" ? p.ix : p.ox
                    const v = part === "point" ? p.y : part === "in" ? p.iy : p.oy
                    if (part !== "point" && Math.abs(u - p.x) < 1e-6 && Math.abs(v - p.y) < 1e-6)
                        continue
                    const o = root.boxToOverlay(u, v)
                    const d = (o.x - px) * (o.x - px) + (o.y - py) * (o.y - py)
                    if (d < bestD || (d === bestD && part === "point")) {
                        bestD = d
                        best = { c: c, i: i, part: part }
                    }
                }
            }
        }
        return best
    }
    function bez(p0, p1, p2, p3, t) {
        const m = 1 - t
        return Qt.point(m * m * m * p0.x + 3 * m * m * t * p1.x + 3 * m * t * t * p2.x + t * t * t * p3.x,
                        m * m * m * p0.y + 3 * m * m * t * p1.y + 3 * m * t * t * p2.y + t * t * t * p3.y)
    }
    // The segment under (px, py): {c, i (its first vertex), t} or null.
    function segmentAt(px, py) {
        const r2 = 7 * 7
        let best = null
        let bestD = r2
        for (let c = 0; c < root.contours.length; ++c) {
            const k = root.contours[c]
            const pts = k.points
            const segs = k.closed ? pts.length : pts.length - 1
            for (let i = 0; i < segs; ++i) {
                const a = pts[i], b = pts[(i + 1) % pts.length]
                const p0 = root.boxToOverlay(a.x, a.y), p1 = root.boxToOverlay(a.ox, a.oy)
                const p2 = root.boxToOverlay(b.ix, b.iy), p3 = root.boxToOverlay(b.x, b.y)
                for (let s = 1; s < 40; ++s) {
                    const t = s / 40
                    const q = root.bez(p0, p1, p2, p3, t)
                    const d = (q.x - px) * (q.x - px) + (q.y - py) * (q.y - py)
                    if (d < bestD) {
                        bestD = d
                        best = { c: c, i: i, t: t }
                    }
                }
            }
        }
        return best
    }

    // ----- Edits -------------------------------------------------------------------------------
    // A vertex on the segment after vertex i at t, the curve unchanged (de Casteljau). Its index.
    function insertVertex(list, c, i, t) {
        const k = list[c]
        const pts = k.points
        const a = pts[i], j = (i + 1) % pts.length, b = pts[j]
        const L = (p, q) => ({ x: p.x + (q.x - p.x) * t, y: p.y + (q.y - p.y) * t })
        const P0 = { x: a.x, y: a.y }, P1 = { x: a.ox, y: a.oy }, P2 = { x: b.ix, y: b.iy }, P3 = { x: b.x, y: b.y }
        const Q0 = L(P0, P1), Q1 = L(P1, P2), Q2 = L(P2, P3)
        const R0 = L(Q0, Q1), R1 = L(Q1, Q2)
        const S = L(R0, R1)
        a.ox = Q0.x; a.oy = Q0.y
        b.ix = Q2.x; b.iy = Q2.y
        const at = j === 0 ? pts.length : i + 1
        pts.splice(at, 0, { x: S.x, y: S.y, ix: R0.x, iy: R0.y, ox: R1.x, oy: R1.y })
        return at
    }
    function deleteVertices(list, keys) {
        const byContour = {}
        for (const key of keys) {
            const [c, i] = key.split(":").map(Number)
            byContour[c] = (byContour[c] || []).concat([i])
        }
        for (const c of Object.keys(byContour).map(Number).sort((a, b) => b - a)) {
            const pts = list[c].points
            for (const i of byContour[c].sort((a, b) => b - a))
                pts.splice(i, 1)
            if (pts.length < 2)
                list.splice(c, 1)
        }
        return list
    }
    function toggleCorner(list, c, i) {
        const pts = list[c].points
        const p = pts[i]
        if (root.isCorner(p)) {
            // Smooth: handles along the line between its neighbours, a sixth of it each way.
            const prev = pts[(i - 1 + pts.length) % pts.length]
            const next = pts[(i + 1) % pts.length]
            const tx = (next.x - prev.x) / 6, ty = (next.y - prev.y) / 6
            p.ix = p.x - tx; p.iy = p.y - ty
            p.ox = p.x + tx; p.oy = p.y + ty
        } else {
            p.ix = p.x; p.iy = p.y
            p.ox = p.x; p.oy = p.y
        }
    }
    function reverseContour(k) {
        k.points.reverse()
        for (const p of k.points) {
            const ix = p.ix, iy = p.iy
            p.ix = p.ox; p.iy = p.oy
            p.ox = ix; p.oy = iy
        }
    }
    // Shift: the point turned round `from` to the nearest 45°.
    function constrain(from, p) {
        const dx = p.x - from.x, dy = p.y - from.y
        const len = Math.hypot(dx, dy)
        const a = Math.round(Math.atan2(dy, dx) / (Math.PI / 4)) * (Math.PI / 4)
        return Qt.point(from.x + Math.cos(a) * len, from.y + Math.sin(a) * len)
    }

    // ----- Pen ---------------------------------------------------------------------------------
    function endDrawing(keep) {
        if (!root.drawing)
            return
        root.drawing = null
        EditorState.finishPenShape(keep)
        root.liveContours = null
        root.selected = []
        root.stateRevision++
    }
    onPenActiveChanged: {
        if (!penActive)
            endDrawing(true)
        else
            keyCatcher.forceActiveFocus()
    }
    Connections {
        target: EditorState.preview
        function onPathEditModeChanged() {
            root.selected = []
            if (EditorState.preview.pathEditMode)
                keyCatcher.forceActiveFocus()
        }
    }

    visible: showPath || penActive

    Item {
        id: keyCatcher
        focus: root.penActive || root.showPath
        // The editor's shortcuts (Delete removes the selected clip, Space plays, arrows move it)
        // must not fire while the pen or the path editor has these keys.
        Keys.onShortcutOverride: event => {
            const k = event.key
            if ((root.penActive || root.showPath)
                    && (k === Qt.Key_Escape || k === Qt.Key_Return || k === Qt.Key_Enter || k === Qt.Key_Backspace
                        || k === Qt.Key_Delete || (root.selected.length > 0 && (k === Qt.Key_Left || k === Qt.Key_Right
                                                                               || k === Qt.Key_Up || k === Qt.Key_Down))
                        || (k === Qt.Key_A && (event.modifiers & Qt.ControlModifier))))
                event.accepted = true
        }
        Keys.onPressed: event => {
            const k = event.key
            if (root.drawing) {
                if (k === Qt.Key_Escape || k === Qt.Key_Return || k === Qt.Key_Enter) {
                    root.endDrawing(true)
                    event.accepted = true
                } else if (k === Qt.Key_Backspace || k === Qt.Key_Delete) {
                    const list = root.cloneContours(root.contours)
                    const pts = list[root.drawing.c].points
                    if (pts.length > 1) {
                        pts.pop()
                        root.write(list)
                    }
                    event.accepted = true
                }
                return
            }
            if (k === Qt.Key_Escape) {
                if (root.penActive)
                    EditorState.preview.penMode = false
                else if (EditorState.preview.pathEditMode)
                    EditorState.preview.pathEditMode = false
                event.accepted = true
                return
            }
            if (!root.showPath)
                return
            if (k === Qt.Key_A && (event.modifiers & Qt.ControlModifier)) {
                const all = []
                for (let c = 0; c < root.contours.length; ++c)
                    for (let i = 0; i < root.contours[c].points.length; ++i)
                        all.push(c + ":" + i)
                root.selected = all
                drawing_.requestPaint()
                event.accepted = true
            } else if ((k === Qt.Key_Delete || k === Qt.Key_Backspace) && root.selected.length > 0) {
                const list = root.deleteVertices(root.cloneContours(root.contours), root.selected)
                root.selected = []
                if (list.length > 0)
                    root.write(list)
                root.liveContours = null
                root.stateRevision++
                event.accepted = true
            } else if (root.selected.length > 0 && (k === Qt.Key_Left || k === Qt.Key_Right || k === Qt.Key_Up || k === Qt.Key_Down)) {
                const step = (event.modifiers & Qt.ShiftModifier) ? 10 : 1
                const px = root.pixelInBox()
                // One canvas pixel is sx overlay pixels.
                const dx = (k === Qt.Key_Left ? -1 : k === Qt.Key_Right ? 1 : 0) * step * px.x * root.sx
                const dy = (k === Qt.Key_Up ? -1 : k === Qt.Key_Down ? 1 : 0) * step * px.y * root.sy
                const list = root.cloneContours(root.contours)
                for (const key of root.selected) {
                    const [c, i] = key.split(":").map(Number)
                    const p = list[c].points[i]
                    p.x += dx; p.ix += dx; p.ox += dx
                    p.y += dy; p.iy += dy; p.oy += dy
                }
                root.write(list)
                root.liveContours = null
                root.stateRevision++
                event.accepted = true
            }
        }
    }

    Canvas {
        id: drawing_
        anchors.fill: parent
        renderStrategy: Canvas.Cooperative
        property var shapes: root.showPath || root.drawing ? root.contours : []
        property point cur: root.cursor
        property var marq: root.marquee
        property var sel: root.selected
        onShapesChanged: requestPaint()
        onCurChanged: if (root.drawing || root.penActive) requestPaint()
        onMarqChanged: requestPaint()
        onSelChanged: requestPaint()
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
            const at = (u, v) => root.boxToOverlay(u, v)
            for (let c = 0; c < shapes.length; ++c) {
                const contour = shapes[c]
                const pts = contour.points
                if (!pts || pts.length === 0)
                    continue
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
                // The rubber band from the last vertex to the pointer while drawing.
                if (root.drawing && root.drawing.c === c && !contour.closed && cur.x >= 0 && !penMouse.pressed) {
                    const last = pts[pts.length - 1]
                    const o = at(last.ox, last.oy)
                    ctx.bezierCurveTo(o.x, o.y, cur.x, cur.y, cur.x, cur.y)
                }
                ctx.stroke()
                for (let i = 0; i < pts.length; ++i) {
                    const p = pts[i]
                    const o = at(p.x, p.y)
                    const sel = root.isSelected(c, i)
                    // Handles show on selected vertices, on the one being drawn, and when few are.
                    if (sel || pts.length <= 12 || (root.drawing && root.drawing.c === c && i >= pts.length - 2)) {
                        handle(ctx, o.x, o.y, at(p.ix, p.iy).x, at(p.ix, p.iy).y)
                        handle(ctx, o.x, o.y, at(p.ox, p.oy).x, at(p.ox, p.oy).y)
                    }
                    const first = root.drawing && root.drawing.c === c && i === 0
                    grip(ctx, o.x, o.y, sel || first, first ? 10 : 7)
                }
            }
            if (marq) {
                ctx.strokeStyle = Theme.primary
                ctx.setLineDash([4, 3])
                ctx.lineWidth = 1
                ctx.strokeRect(Math.min(marq.x0, marq.x1), Math.min(marq.y0, marq.y1),
                               Math.abs(marq.x1 - marq.x0), Math.abs(marq.y1 - marq.y0))
                ctx.setLineDash([])
            }
            // What the Pen will do here: + add a vertex, − delete, ○ close.
            if (root.penActive && cur.x >= 0 && penMouse.hint.length > 0) {
                ctx.fillStyle = "#ffffff"
                ctx.strokeStyle = "#000000"
                ctx.lineWidth = 3
                ctx.font = "bold 14px sans-serif"
                ctx.strokeText(penMouse.hint, cur.x + 10, cur.y + 18)
                ctx.fillText(penMouse.hint, cur.x + 10, cur.y + 18)
            }
        }
    }

    // ----- The Pen's pointer ---------------------------------------------------------------------
    MouseArea {
        id: penMouse
        anchors.fill: parent
        preventStealing: true
        enabled: root.penActive
        visible: enabled
        hoverEnabled: true
        cursorShape: Qt.CrossCursor
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        // {type, c, i, moved, start} while pressed.
        property var op: null
        property string hint: ""

        function updateHint(mouse) {
            hint = ""
            if (root.drawing) {
                const pts = root.contours[root.drawing.c] ? root.contours[root.drawing.c].points : []
                if (pts.length >= 2) {
                    const f = root.boxToOverlay(pts[0].x, pts[0].y)
                    if (Math.hypot(f.x - mouse.x, f.y - mouse.y) <= 9)
                        hint = "○"
                }
                return
            }
            if (!root.targetEditable)
                return
            const g = root.gripAt(mouse.x, mouse.y)
            if (g && g.part === "point") {
                const k = root.contours[g.c]
                if (mouse.modifiers & Qt.ControlModifier)
                    hint = "−"
                else if (mouse.modifiers & Qt.AltModifier)
                    hint = "^"
                else if (!k.closed && (g.i === 0 || g.i === k.points.length - 1))
                    hint = "/"
                return
            }
            if (!g && root.segmentAt(mouse.x, mouse.y))
                hint = "+"
        }

        onPositionChanged: mouse => {
            root.cursor = Qt.point(mouse.x, mouse.y)
            if (!pressed || !op) {
                updateHint(mouse)
                return
            }
            op.moved = true
            const list = root.cloneContours(root.contours)
            const k = list[op.c]
            if (!k)
                return
            const p = k.points[op.i]
            const now = root.overlayToBox(mouse.x, mouse.y)
            if (op.type === "handles") {
                // Out where the pointer is, in opposite (Alt: only the out handle moves).
                p.ox = now.x; p.oy = now.y
                if (!(mouse.modifiers & Qt.AltModifier)) {
                    p.ix = 2 * p.x - now.x
                    p.iy = 2 * p.y - now.y
                }
            } else if (op.type === "move") {
                const was = root.overlayToBox(op.last.x, op.last.y)
                const dx = now.x - was.x, dy = now.y - was.y
                p.x += dx; p.ix += dx; p.ox += dx
                p.y += dy; p.iy += dy; p.oy += dy
                op.last = Qt.point(mouse.x, mouse.y)
            } else if (op.type === "convert") {
                p.ox = now.x; p.oy = now.y
                p.ix = 2 * p.x - now.x
                p.iy = 2 * p.y - now.y
            } else if (op.type === "handle") {
                const mine = op.part === "in" ? ["ix", "iy"] : ["ox", "oy"]
                const other = op.part === "in" ? ["ox", "oy"] : ["ix", "iy"]
                p[mine[0]] = now.x
                p[mine[1]] = now.y
                if (!(mouse.modifiers & Qt.AltModifier)) {
                    const len = Math.hypot(p[other[0]] - p.x, p[other[1]] - p.y)
                    const ax = p.x - now.x, ay = p.y - now.y
                    const al = Math.hypot(ax, ay)
                    if (al > 1e-9 && len > 1e-9) {
                        p[other[0]] = p.x + ax / al * len
                        p[other[1]] = p.y + ay / al * len
                    }
                }
            }
            root.write(list)
        }
        onPressed: mouse => {
            keyCatcher.forceActiveFocus()
            op = null
            if (mouse.button === Qt.RightButton) {
                root.endDrawing(true)
                return
            }
            let here = root.overlayToBox(mouse.x, mouse.y)
            // ---- Drawing: close on the first vertex, else a new vertex.
            if (root.drawing) {
                const list = root.cloneContours(root.contours)
                const k = list[root.drawing.c]
                const pts = k.points
                const f = root.boxToOverlay(pts[0].x, pts[0].y)
                if (pts.length >= 2 && Math.hypot(f.x - mouse.x, f.y - mouse.y) <= 9) {
                    k.closed = true
                    root.write(list)
                    op = { type: "close", c: root.drawing.c, i: 0, moved: false }
                    return
                }
                if (mouse.modifiers & Qt.ShiftModifier) {
                    const last = pts[pts.length - 1]
                    const lo = root.boxToOverlay(last.x, last.y)
                    const q = root.constrain(lo, Qt.point(mouse.x, mouse.y))
                    here = root.overlayToBox(q.x, q.y)
                }
                pts.push(root.vertex(here))
                root.write(list)
                op = { type: "handles", c: root.drawing.c, i: pts.length - 1, moved: false }
                return
            }
            // ---- A selected shape: add, delete, convert, carry on, or another path in it.
            if (root.targetEditable) {
                const id = (EditorState.clipAt(root.box.track, root.box.clip) || {}).id || ""
                const g = root.gripAt(mouse.x, mouse.y)
                if (g && g.part === "point") {
                    const list = root.cloneContours(root.contours)
                    const k = list[g.c]
                    if (mouse.modifiers & Qt.ControlModifier) {
                        root.deleteVertices(list, [g.c + ":" + g.i])
                        if (list.length > 0)
                            root.write(list)
                        root.liveContours = null
                        root.stateRevision++
                        return
                    }
                    if (mouse.modifiers & Qt.AltModifier) {
                        EditorState.beginPreviewDrag(qsTr("Convert vertex"))
                        root.liveContours = list
                        op = { type: "convert", c: g.c, i: g.i, moved: false }
                        return
                    }
                    if (!k.closed && (g.i === 0 || g.i === k.points.length - 1)) {
                        // Carry the open path on from this end.
                        EditorState.beginPenShape(id)
                        if (g.i === 0)
                            root.reverseContour(k)
                        root.drawing = { c: g.c, fresh: false }
                        root.write(list)
                        return
                    }
                    EditorState.beginPreviewDrag(qsTr("Path edited"))
                    root.liveContours = list
                    op = { type: "move", c: g.c, i: g.i, last: Qt.point(mouse.x, mouse.y), moved: false }
                    return
                }
                if (g) {
                    EditorState.beginPreviewDrag(qsTr("Path edited"))
                    root.liveContours = root.cloneContours(root.contours)
                    op = { type: "handle", c: g.c, i: g.i, part: g.part, moved: false }
                    return
                }
                const seg = root.segmentAt(mouse.x, mouse.y)
                if (seg) {
                    EditorState.beginPreviewDrag(qsTr("Add vertex"))
                    const list = root.cloneContours(root.contours)
                    const at = root.insertVertex(list, seg.c, seg.i, seg.t)
                    root.write(list)
                    op = { type: "move", c: seg.c, i: at, last: Qt.point(mouse.x, mouse.y), moved: true }
                    return
                }
                // Another path in the same layer.
                EditorState.beginPenShape(id)
                const list = root.cloneContours(root.contours)
                list.push({ closed: false, points: [root.vertex(here)] })
                root.drawing = { c: list.length - 1, fresh: false }
                root.write(list)
                op = { type: "handles", c: list.length - 1, i: 0, moved: false }
                return
            }
            // ---- Nothing editable selected: a new shape layer, right now.
            const newId = EditorState.beginPenShape("")
            if (newId.length === 0)
                return
            root.drawing = { c: 0, fresh: true }
            here = Qt.point(mouse.x / root.sx / root.canvasW, mouse.y / root.sy / root.canvasH)
            const list = [{ closed: false, points: [root.vertex(here)] }]
            root.write(list)
            op = { type: "handles", c: 0, i: 0, moved: false }
        }
        onReleased: mouse => {
            const d = op
            op = null
            if (!d)
                return
            if (d.type === "close") {
                root.endDrawing(true)
                return
            }
            if (d.type === "convert") {
                if (!d.moved) {
                    const list = root.cloneContours(root.contours)
                    root.toggleCorner(list, d.c, d.i)
                    root.write(list)
                }
                EditorState.commitPreviewDrag()
                root.liveContours = null
                root.stateRevision++
                return
            }
            if (d.type === "move" || d.type === "handle") {
                EditorState.commitPreviewDrag()
                root.liveContours = null
                root.stateRevision++
            }
        }
        onDoubleClicked: mouse => {
            // The second press of a double click put a vertex on top of the last one: take it back.
            if (root.drawing) {
                const list = root.cloneContours(root.contours)
                const pts = list[root.drawing.c].points
                if (pts.length > 2) {
                    pts.pop()
                    root.write(list)
                }
                root.endDrawing(true)
            }
        }
        onExited: {
            root.cursor = Qt.point(-1, -1)
            hint = ""
        }
    }

    // ----- Path editing with the Selection tool ------------------------------------------------
    MouseArea {
        id: editArea
        anchors.fill: parent
        preventStealing: true
        enabled: root.showPath && !root.penActive
        visible: enabled
        hoverEnabled: true
        property var grab: null
        property point last

        onPressed: mouse => {
            keyCatcher.forceActiveFocus()
            const g = root.gripAt(mouse.x, mouse.y)
            const shift = (mouse.modifiers & Qt.ShiftModifier) !== 0
            if (g && g.part === "point") {
                const key = g.c + ":" + g.i
                if (mouse.modifiers & Qt.ControlModifier) {
                    const list = root.deleteVertices(root.cloneContours(root.contours), [key])
                    root.selected = []
                    if (list.length > 0)
                        root.write(list)
                    root.liveContours = null
                    root.stateRevision++
                    return
                }
                if (mouse.modifiers & Qt.AltModifier) {
                    EditorState.beginPreviewDrag(qsTr("Convert vertex"))
                    root.liveContours = root.cloneContours(root.contours)
                    grab = { type: "convert", c: g.c, i: g.i, moved: false }
                    return
                }
                if (shift) {
                    const sel = root.selected.slice()
                    const at = sel.indexOf(key)
                    if (at >= 0)
                        sel.splice(at, 1)
                    else
                        sel.push(key)
                    root.selected = sel
                    return
                }
                if (!root.isSelected(g.c, g.i))
                    root.selected = [key]
                EditorState.beginPreviewDrag(qsTr("Path edited"))
                root.liveContours = root.cloneContours(root.contours)
                grab = { type: "move" }
                last = Qt.point(mouse.x, mouse.y)
                return
            }
            if (g) {
                EditorState.beginPreviewDrag(qsTr("Path edited"))
                root.liveContours = root.cloneContours(root.contours)
                grab = { type: "handle", c: g.c, i: g.i, part: g.part, alt: (mouse.modifiers & Qt.AltModifier) !== 0 }
                return
            }
            const seg = root.segmentAt(mouse.x, mouse.y)
            if (seg) {
                // Bending a segment: its two handles move so the point grabbed follows the pointer.
                EditorState.beginPreviewDrag(qsTr("Path edited"))
                root.liveContours = root.cloneContours(root.contours)
                grab = { type: "bend", c: seg.c, i: seg.i, t: seg.t }
                last = Qt.point(mouse.x, mouse.y)
                return
            }
            // A box round several vertices.
            if (!shift)
                root.selected = []
            root.marquee = { x0: mouse.x, y0: mouse.y, x1: mouse.x, y1: mouse.y, add: shift }
        }
        onPositionChanged: mouse => {
            if (root.marquee) {
                root.marquee = Object.assign({}, root.marquee, { x1: mouse.x, y1: mouse.y })
                return
            }
            if (!grab || !root.liveContours)
                return
            const list = root.cloneContours(root.liveContours)
            const now = root.overlayToBox(mouse.x, mouse.y)
            if (grab.type === "move") {
                const was = root.overlayToBox(last.x, last.y)
                const dx = now.x - was.x, dy = now.y - was.y
                for (const key of root.selected) {
                    const [c, i] = key.split(":").map(Number)
                    const p = list[c].points[i]
                    p.x += dx; p.ix += dx; p.ox += dx
                    p.y += dy; p.iy += dy; p.oy += dy
                }
                last = Qt.point(mouse.x, mouse.y)
            } else if (grab.type === "handle") {
                const p = list[grab.c].points[grab.i]
                const mine = grab.part === "in" ? ["ix", "iy"] : ["ox", "oy"]
                const other = grab.part === "in" ? ["ox", "oy"] : ["ix", "iy"]
                p[mine[0]] = now.x
                p[mine[1]] = now.y
                if (!grab.alt && !(mouse.modifiers & Qt.AltModifier)) {
                    const len = Math.hypot(p[other[0]] - p.x, p[other[1]] - p.y)
                    const ax = p.x - now.x, ay = p.y - now.y
                    const al = Math.hypot(ax, ay)
                    if (al > 1e-9 && len > 1e-9) {
                        p[other[0]] = p.x + ax / al * len
                        p[other[1]] = p.y + ay / al * len
                    }
                }
            } else if (grab.type === "convert") {
                grab.moved = true
                const p = list[grab.c].points[grab.i]
                p.ox = now.x; p.oy = now.y
                p.ix = 2 * p.x - now.x
                p.iy = 2 * p.y - now.y
            } else if (grab.type === "bend") {
                const was = root.overlayToBox(last.x, last.y)
                const dx = now.x - was.x, dy = now.y - was.y
                const k = list[grab.c]
                const a = k.points[grab.i], b = k.points[(grab.i + 1) % k.points.length]
                const t = grab.t, m = 1 - t
                const wa = 3 * m * m * t, wb = 3 * m * t * t
                const n = wa * wa + wb * wb
                a.ox += dx * wa / n; a.oy += dy * wa / n
                b.ix += dx * wb / n; b.iy += dy * wb / n
                last = Qt.point(mouse.x, mouse.y)
            }
            root.liveContours = list
            EditorState.setShapePathPoints(EditorState.selectedTrack, EditorState.selectedClip, list)
        }
        onReleased: mouse => {
            if (root.marquee) {
                const m = root.marquee
                const x0 = Math.min(m.x0, m.x1), x1 = Math.max(m.x0, m.x1)
                const y0 = Math.min(m.y0, m.y1), y1 = Math.max(m.y0, m.y1)
                const sel = m.add ? root.selected.slice() : []
                for (let c = 0; c < root.contours.length; ++c) {
                    const pts = root.contours[c].points
                    for (let i = 0; i < pts.length; ++i) {
                        const o = root.boxToOverlay(pts[i].x, pts[i].y)
                        if (o.x >= x0 && o.x <= x1 && o.y >= y0 && o.y <= y1 && sel.indexOf(c + ":" + i) < 0)
                            sel.push(c + ":" + i)
                    }
                }
                root.selected = sel
                root.marquee = null
                return
            }
            if (!grab)
                return
            if (grab.type === "convert" && !grab.moved) {
                const list = root.cloneContours(root.liveContours)
                root.toggleCorner(list, grab.c, grab.i)
                EditorState.setShapePathPoints(EditorState.selectedTrack, EditorState.selectedClip, list)
            }
            grab = null
            EditorState.commitPreviewDrag()
            root.liveContours = null
            root.stateRevision++
        }
        onCanceled: {
            grab = null
            root.marquee = null
            EditorState.cancelPreviewDrag()
            root.liveContours = null
        }
    }
}
