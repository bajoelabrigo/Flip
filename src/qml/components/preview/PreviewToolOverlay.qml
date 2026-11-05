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
    signal textEditRequested(int track, int clip, bool selectAll)

    readonly property string tool: EditorState.preview.tool
    readonly property int canvasW: { void EditorState.tracksRevision; return Math.max(1, EditorState.projectFile.projectWidth()) }
    readonly property int canvasH: { void EditorState.tracksRevision; return Math.max(1, EditorState.projectFile.projectHeight()) }
    readonly property real sx: width / canvasW
    readonly property real sy: height / canvasH
    readonly property bool anchorReady: tool === "anchor" && !!box && !!box.quad && box.quad.length === 4
                                        && box.kind !== "transform"

    readonly property bool sketchReady: tool === "sketch" && !!box && box.kind !== "transform"
    readonly property bool puppetReady: tool === "puppet" && !!box && !!box.quad && box.quad.length === 4
                                        && box.kind !== "transform"
    // The pins where they are at the playhead, in fractions of the layer.
    readonly property var puppet: {
        void EditorState.tracksRevision
        void EditorState.playheadSeconds
        return puppetReady ? EditorState.puppetPins(box.track, box.clip) : null
    }
    property int puppetDrag: -1
    property point puppetLive: Qt.point(0, 0)
    function puppetPinAt(px, py) {
        if (!puppet)
            return -1
        for (let i = 0; i < puppet.pins.length; ++i) {
            const p = boxToOverlay(puppet.pins[i].x, puppet.pins[i].y)
            if (Math.abs(p.x - px) <= 9 && Math.abs(p.y - py) <= 9)
                return i
        }
        return -1
    }
    visible: tool === "shape" || tool === "text" || tool === "roi" || anchorReady || sketchReady || puppetReady
    enabled: visible && !EditorState.playing

    // With the shape tool, a shape drawn while a shape layer is picked goes into that layer (0.28, Pro); Esc
    // lets go of the layer so the next one gets a layer of its own.
    Keys.onEscapePressed: event => {
        if (root.tool === "shape" && EditorState.selectedClip >= 0) {
            EditorState.clearSelection()
            event.accepted = true
        } else {
            event.accepted = false
        }
    }

    // Fractions of the box (0..1) ↔ overlay px, through the box's on-screen corners.
    function boxToOverlay(u, v) {
        const a = box.quad[0], b = box.quad[1], d = box.quad[3]
        return Qt.point((a.x + (b.x - a.x) * u + (d.x - a.x) * v) * sx, (a.y + (b.y - a.y) * u + (d.y - a.y) * v) * sy)
    }
    // Ctrl while dragging the anchor sticks it to the layer's centre, corners and edge middles (After Effects).
    function anchorSnap(px, py, mods) {
        if (!(mods & Qt.ControlModifier) || !root.anchorReady)
            return Qt.point(px, py)
        let best = null
        let bestD = 18
        for (const u of [0, 0.5, 1]) {
            for (const v of [0, 0.5, 1]) {
                const q = root.boxToOverlay(u, v)
                const d = Math.hypot(q.x - px, q.y - py)
                if (d < bestD) {
                    bestD = d
                    best = q
                }
            }
        }
        return best || Qt.point(px, py)
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
    property point dragTo: Qt.point(0, 0)
    property bool dragging: false
    readonly property bool lineTool: tool === "shape" && EditorState.preview.shapeToolKind === "line"
    // After Effects' Polygon and Star (0.30): drawn out from the centre, turning with the pointer (Shift keeps
    // them upright) and with the wheel adding or taking away points while the button is down.
    readonly property bool polystarTool: tool === "shape" && (EditorState.preview.shapeToolKind === "star"
                                                              || EditorState.preview.shapeToolKind === "polygon")
    property real dragRotation: 0
    property int dragPoints: 5
    function polystarRect(from, to, shift) {
        const r = Math.max(1, Math.hypot(to.x - from.x, to.y - from.y))
        // A point aims at the pointer.
        root.dragRotation = shift ? 0 : Math.atan2(to.y - from.y, to.x - from.x) * 180 / Math.PI + 90
        return Qt.rect(from.x - r, from.y - r, 2 * r, 2 * r)
    }

    // The Line tool: Shift keeps it at 0°, 45° or 90°, as AE's pen with Shift.
    function linePoint(from, to, shift) {
        if (!shift)
            return to
        const dx = to.x - from.x
        const dy = to.y - from.y
        const a = Math.round(Math.atan2(dy, dx) / (Math.PI / 4)) * (Math.PI / 4)
        const len = Math.sqrt(dx * dx + dy * dy)
        return Qt.point(from.x + Math.cos(a) * len, from.y + Math.sin(a) * len)
    }

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
        visible: root.dragging && root.lineTool
        x: root.dragFrom.x
        y: root.dragFrom.y - height / 2
        width: Math.sqrt(Math.pow(root.dragTo.x - root.dragFrom.x, 2) + Math.pow(root.dragTo.y - root.dragFrom.y, 2))
        height: Math.max(2, EditorState.preview.toolStrokeWidth * root.sx)
        transformOrigin: Item.Left
        rotation: Math.atan2(root.dragTo.y - root.dragFrom.y, root.dragTo.x - root.dragFrom.x) * 180 / Math.PI
        color: Theme.primary
        opacity: 0.8
    }

    Rectangle {
        visible: root.dragging && !root.lineTool && (root.tool === "shape" || root.tool === "roi")
        x: root.dragRect.x
        y: root.dragRect.y
        width: root.dragRect.width
        height: root.dragRect.height
        radius: EditorState.preview.shapeToolKind === "ellipse" ? Math.min(width, height) / 2
              : EditorState.preview.shapeToolKind === "roundedRectangle" ? Math.min(20 * root.sx, Math.min(width, height) / 2) : 0
        rotation: root.polystarTool ? root.dragRotation : 0
        color: "transparent"
        border.width: root.polystarTool ? 0 : 1.5
        border.color: Theme.primary
        // The polygon or star itself while it is drawn out (0.30, as After Effects), not its box.
        Canvas {
            id: polystarOutline
            anchors.fill: parent
            visible: root.polystarTool
            readonly property int points: root.dragPoints
            readonly property bool star: EditorState.preview.shapeToolKind === "star"
            onPointsChanged: requestPaint()
            onStarChanged: requestPaint()
            onWidthChanged: requestPaint()
            onHeightChanged: requestPaint()
            onPaint: {
                const ctx = getContext("2d")
                ctx.reset()
                const n = Math.max(3, points)
                const cx = width / 2, cy = height / 2
                const r = Math.min(width, height) / 2
                const steps = star ? n * 2 : n
                ctx.beginPath()
                for (let i = 0; i < steps; ++i) {
                    const a = -Math.PI / 2 + i * 2 * Math.PI / steps
                    const rr = star && i % 2 === 1 ? r * 0.5 : r
                    const px = cx + Math.cos(a) * rr, py = cy + Math.sin(a) * rr
                    if (i === 0)
                        ctx.moveTo(px, py)
                    else
                        ctx.lineTo(px, py)
                }
                ctx.closePath()
                ctx.lineWidth = 1.5
                ctx.strokeStyle = Theme.primary
                ctx.stroke()
            }
        }
        // How many points the polygon or star gets (the wheel changes it).
        Text {
            visible: root.polystarTool
            anchors.centerIn: parent
            rotation: -parent.rotation
            text: root.dragPoints
            color: Theme.primary
            font.pixelSize: 14
            font.bold: true
        }
    }

    // ----- Motion sketch: the pointer's path while the playhead runs in real time ---------------
    property var sketch: []
    property real sketchStart: 0
    property int sketchTrack: -1
    property int sketchClip: -1
    onSketchReadyChanged: {
        // The tool or the clip went away mid-sketch: stop instead of running the playhead on.
        if (!sketchReady && sketchTimer.running) {
            sketchTimer.stop()
            if (sketch.length > 1 && sketchTrack >= 0)
                EditorState.applyMotionSketch(sketchTrack, sketchClip, sketch, 2.0)
            sketch = []
        }
    }
    property real sketchClock: 0
    property point sketchPointer: Qt.point(0, 0)
    Timer {
        id: sketchTimer
        interval: 16
        repeat: true
        onTriggered: {
            const t = root.sketchStart + (Date.now() - root.sketchClock) / 1000
            EditorState.playheadSeconds = t
            root.sketch = root.sketch.concat([{ t: t, x: root.sketchPointer.x / root.sx, y: root.sketchPointer.y / root.sy }])
        }
    }
    Canvas {
        id: sketchTrail
        anchors.fill: parent
        visible: root.sketchReady && root.sketch.length > 1
        property var pts: root.sketch
        onPtsChanged: requestPaint()
        onPaint: {
            const c = getContext("2d")
            c.reset()
            if (pts.length < 2) return
            c.strokeStyle = Theme.primary
            c.lineWidth = 2
            c.beginPath()
            c.moveTo(pts[0].x * root.sx, pts[0].y * root.sy)
            for (let i = 1; i < pts.length; ++i)
                c.lineTo(pts[i].x * root.sx, pts[i].y * root.sy)
            c.stroke()
        }
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

    // Puppet pins: yellow dots, the one being dragged follows the pointer.
    Repeater {
        model: root.puppet ? root.puppet.pins : []
        delegate: Rectangle {
            required property var modelData
            required property int index
            readonly property point at: root.puppetDrag === index ? root.puppetLive
                                                                    : root.boxToOverlay(modelData.x, modelData.y)
            x: at.x - 6
            y: at.y - 6
            width: 12
            height: 12
            radius: 6
            color: "#ffffd23c"
            border.width: 1.5
            border.color: "#ff202020"
        }
    }

    MouseArea {
        id: area
        anchors.fill: parent
        // A shape can be started a little outside the frame (0.29: a drag begun right on its edge drew nothing),
        // as After Effects draws from the pasteboard. Coordinates below are the overlay's (area.x/y added).
        anchors.margins: root.tool === "shape" ? -32 : 0
        // The preview drags the selected clip from further up; these drags are ours.
        preventStealing: true
        hoverEnabled: true
        cursorShape: root.tool === "text" ? Qt.IBeamCursor
                     : root.tool === "anchor" || root.tool === "sketch" || root.tool === "puppet" ? Qt.SizeAllCursor
                     : Qt.CrossCursor

        onWheel: wheel => {
            if (!(root.polystarTool && root.dragging)) {
                wheel.accepted = false
                return
            }
            const turn = wheel.angleDelta.y !== 0 ? wheel.angleDelta.y : wheel.angleDelta.x
            root.dragPoints = Math.max(3, Math.min(60, root.dragPoints + (turn > 0 ? 1 : -1)))
        }
        onPressed: mouse => {
            if (root.puppetReady) {
                const hit = root.puppetPinAt((mouse.x + area.x), (mouse.y + area.y))
                if (hit >= 0) {
                    root.puppetDrag = hit
                    root.puppetLive = Qt.point((mouse.x + area.x), (mouse.y + area.y))
                } else {
                    const f = root.overlayToBox((mouse.x + area.x), (mouse.y + area.y))
                    if (f.x >= 0 && f.y >= 0 && f.x <= 1 && f.y <= 1)
                        EditorState.addPuppetPin(root.box.track, root.box.clip, f.x, f.y)
                }
                return
            }
            if (root.tool === "shape" || root.tool === "roi") {
                root.dragRotation = 0
                root.dragFrom = Qt.point((mouse.x + area.x), (mouse.y + area.y))
                root.dragTo = Qt.point((mouse.x + area.x), (mouse.y + area.y))
                root.dragRect = Qt.rect((mouse.x + area.x), (mouse.y + area.y), 0, 0)
                root.dragging = true
            } else if (root.tool === "anchor") {
                root.anchorLive = root.anchorSnap(mouse.x + area.x, mouse.y + area.y, mouse.modifiers)
            } else if (root.sketchReady) {
                // The clip being sketched, kept: once the playhead runs past its end `box` is null.
                root.sketchTrack = root.box.track
                root.sketchClip = root.box.clip
                root.sketchPointer = Qt.point((mouse.x + area.x), (mouse.y + area.y))
                root.sketchStart = EditorState.playheadSeconds
                root.sketchClock = Date.now()
                root.sketch = [{ t: root.sketchStart, x: (mouse.x + area.x) / root.sx, y: (mouse.y + area.y) / root.sy }]
                sketchTimer.start()
            }
        }
        onPositionChanged: mouse => {
            if (!pressed)
                return
            if (root.puppetDrag >= 0) {
                root.puppetLive = Qt.point((mouse.x + area.x), (mouse.y + area.y))
                return
            }
            if (root.lineTool && root.dragging)
                root.dragTo = root.linePoint(root.dragFrom, Qt.point((mouse.x + area.x), (mouse.y + area.y)), mouse.modifiers & Qt.ShiftModifier)
            else if (root.polystarTool && root.dragging)
                root.dragRect = root.polystarRect(root.dragFrom, Qt.point((mouse.x + area.x), (mouse.y + area.y)),
                                                  mouse.modifiers & Qt.ShiftModifier)
            else if ((root.tool === "shape" || root.tool === "roi") && root.dragging)
                root.dragRect = root.shapeRect(root.dragFrom, Qt.point((mouse.x + area.x), (mouse.y + area.y)),
                                               mouse.modifiers & Qt.ShiftModifier, mouse.modifiers & Qt.AltModifier)
            else if (root.tool === "anchor")
                root.anchorLive = root.anchorSnap(mouse.x + area.x, mouse.y + area.y, mouse.modifiers)
            else if (root.tool === "sketch")
                root.sketchPointer = Qt.point((mouse.x + area.x), (mouse.y + area.y))
        }
        onReleased: mouse => {
            if (root.puppetDrag >= 0) {
                const f = root.overlayToBox((mouse.x + area.x), (mouse.y + area.y))
                const pin = root.puppetDrag
                root.puppetDrag = -1
                EditorState.movePuppetPin(root.box.track, root.box.clip, pin, f.x, f.y)
                return
            }
            if (root.tool === "roi" && root.dragging) {
                root.dragging = false
                const q = root.dragRect
                if (q.width >= 6 && q.height >= 6)
                    EditorState.playback.regionOfInterest = Qt.rect(q.x / root.width, q.y / root.height,
                                                                    q.width / root.width, q.height / root.height)
                EditorState.preview.tool = "select"
                return
            }
            if (root.lineTool && root.dragging) {
                root.dragging = false
                const a = root.dragFrom
                const b = root.dragTo
                if (Math.abs(b.x - a.x) < 3 && Math.abs(b.y - a.y) < 3)
                    return
                EditorState.addPenShape([{ x: a.x / root.sx, y: a.y / root.sy }, { x: b.x / root.sx, y: b.y / root.sy }], false)
                root.forceActiveFocus()
            } else if (root.tool === "shape" && root.dragging) {
                root.dragging = false
                const r = Qt.rect(root.dragRect.x, root.dragRect.y, root.dragRect.width, root.dragRect.height)
                // A thin bar (a rule, a line under a title) is a real shape too (0.29: under 4 px it was dropped
                // without a word); only a click with no drag is ignored.
                if (r.width < 3 && r.height < 3)
                    return
                r.width = Math.max(r.width, 1)
                r.height = Math.max(r.height, 1)
                // «Tool creates mask» (0.30, After Effects): the drawn box becomes a mask on the picked layer.
                if (EditorState.preview.shapeToolMask && root.box && root.box.quad && root.box.quad.length === 4) {
                    const a0 = root.overlayToBox(r.x, r.y)
                    const a1 = root.overlayToBox(r.x + r.width, r.y + r.height)
                    const kind = EditorState.preview.shapeToolKind
                    const shape = kind === "ellipse" ? "ellipse" : kind === "star" ? "star" : "rectangle"
                    const track = root.box.track, clip = root.box.clip
                    const id = EditorState.addMaskToClipInPlace(track, clip, shape)
                    // The new lane can shift the tracks: the mask is found again by its id.
                    const e = id ? EditorState.clipLocation(id) : ({})
                    if (e.track !== undefined && e.track >= 0) {
                        const cur = Object.assign({}, (EditorState.clipAt(e.track, e.clip) || {}).mask || {})
                        cur.x = (a0.x + a1.x) / 2
                        cur.y = (a0.y + a1.y) / 2
                        cur.w = Math.abs(a1.x - a0.x)
                        cur.h = Math.abs(a1.y - a0.y)
                        EditorState.setClipMask(e.track, e.clip, cur)
                    }
                    root.forceActiveFocus()
                    return
                }
                EditorState.addDrawnShape(EditorState.preview.shapeToolKind, r.x / root.sx, r.y / root.sy,
                                          r.width / root.sx, r.height / root.sy, EditorState.preview.toolFill,
                                          EditorState.preview.toolStroke, EditorState.preview.toolStrokeWidth,
                                          root.polystarTool ? root.dragRotation : 0,
                                          root.polystarTool ? root.dragPoints : 0)
                root.forceActiveFocus()
            } else if (root.tool === "sketch" && sketchTimer.running) {
                sketchTimer.stop()
                if (root.sketch.length > 1 && root.sketchTrack >= 0)
                    EditorState.applyMotionSketch(root.sketchTrack, root.sketchClip, root.sketch, 2.0)
                root.sketch = []
            } else if (root.tool === "anchor" && root.anchorReady && root.box) {
                const at = root.anchorSnap(mouse.x + area.x, mouse.y + area.y, mouse.modifiers)
                const f = root.overlayToBox(at.x, at.y)
                root.anchorLive = Qt.point(-1, -1)
                EditorState.setAnchorKeepingPlace(root.box.track, root.box.clip, f.x, f.y)
            }
        }
        // A popup or Alt-Tab mid-gesture: nothing half done is left running (the sketch timer moved
        // the playhead forever and grew its trail without limit).
        onCanceled: {
            sketchTimer.stop()
            root.sketch = []
            root.dragging = false
            root.puppetDrag = -1
            root.anchorLive = Qt.point(-1, -1)
        }
        onClicked: mouse => {
            if (root.tool !== "text")
                return
            // The colour under the click picks dark or light words (0.29: white words on a white label).
            const px = (mouse.x + area.x)
            const py = (mouse.y + area.y)
            const place = function (backdrop) {
                const made = EditorState.addTextAtPoint(px / root.sx, py / root.sy, backdrop)
                if (made && made.track !== undefined) {
                    // As After Effects: after placing one text, back to selection while you type.
                    EditorState.preview.tool = "select"
                    root.textEditRequested(made.track, made.clip, true)
                }
            }
            // The whole window, as the eyedropper does: this overlay and its parent are transparent over
            // the preview, so grabbing them read nothing and the words always came out white.
            const target = root.Window.contentItem
            const at = target ? root.mapToItem(target, px, py) : Qt.point(0, 0)
            const grabbed = target && target.grabToImage(function (result) {
                place(AppController.imagePixel(result.image, Math.floor(at.x), Math.floor(at.y)))
            }, Qt.size(Math.round(target.width), Math.round(target.height)))
            if (!grabbed)
                place(Qt.rgba(0, 0, 0, 0))
        }
    }
}
