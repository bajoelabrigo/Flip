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
        visible: root.dragging && (root.tool === "shape" || root.tool === "roi")
        x: root.dragRect.x
        y: root.dragRect.y
        width: root.dragRect.width
        height: root.dragRect.height
        radius: EditorState.preview.shapeToolKind === "ellipse" ? Math.min(width, height) / 2 : 0
        color: "transparent"
        border.width: 1.5
        border.color: Theme.primary
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
        anchors.fill: parent
        // The preview drags the selected clip from further up; these drags are ours.
        preventStealing: true
        hoverEnabled: true
        cursorShape: root.tool === "text" ? Qt.IBeamCursor
                     : root.tool === "anchor" || root.tool === "sketch" || root.tool === "puppet" ? Qt.SizeAllCursor
                     : Qt.CrossCursor

        onPressed: mouse => {
            if (root.puppetReady) {
                const hit = root.puppetPinAt(mouse.x, mouse.y)
                if (hit >= 0) {
                    root.puppetDrag = hit
                    root.puppetLive = Qt.point(mouse.x, mouse.y)
                } else {
                    const f = root.overlayToBox(mouse.x, mouse.y)
                    if (f.x >= 0 && f.y >= 0 && f.x <= 1 && f.y <= 1)
                        EditorState.addPuppetPin(root.box.track, root.box.clip, f.x, f.y)
                }
                return
            }
            if (root.tool === "shape" || root.tool === "roi") {
                root.dragFrom = Qt.point(mouse.x, mouse.y)
                root.dragRect = Qt.rect(mouse.x, mouse.y, 0, 0)
                root.dragging = true
            } else if (root.tool === "anchor") {
                root.anchorLive = Qt.point(mouse.x, mouse.y)
            } else if (root.sketchReady) {
                // The clip being sketched, kept: once the playhead runs past its end `box` is null.
                root.sketchTrack = root.box.track
                root.sketchClip = root.box.clip
                root.sketchPointer = Qt.point(mouse.x, mouse.y)
                root.sketchStart = EditorState.playheadSeconds
                root.sketchClock = Date.now()
                root.sketch = [{ t: root.sketchStart, x: mouse.x / root.sx, y: mouse.y / root.sy }]
                sketchTimer.start()
            }
        }
        onPositionChanged: mouse => {
            if (!pressed)
                return
            if (root.puppetDrag >= 0) {
                root.puppetLive = Qt.point(mouse.x, mouse.y)
                return
            }
            if ((root.tool === "shape" || root.tool === "roi") && root.dragging)
                root.dragRect = root.shapeRect(root.dragFrom, Qt.point(mouse.x, mouse.y),
                                               mouse.modifiers & Qt.ShiftModifier, mouse.modifiers & Qt.AltModifier)
            else if (root.tool === "anchor")
                root.anchorLive = Qt.point(mouse.x, mouse.y)
            else if (root.tool === "sketch")
                root.sketchPointer = Qt.point(mouse.x, mouse.y)
        }
        onReleased: mouse => {
            if (root.puppetDrag >= 0) {
                const f = root.overlayToBox(mouse.x, mouse.y)
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
            if (root.tool === "shape" && root.dragging) {
                root.dragging = false
                const r = root.dragRect
                if (r.width < 4 || r.height < 4)
                    return
                EditorState.addDrawnShape(EditorState.preview.shapeToolKind, r.x / root.sx, r.y / root.sy,
                                          r.width / root.sx, r.height / root.sy, EditorState.preview.toolFill,
                                          EditorState.preview.toolStroke, EditorState.preview.toolStrokeWidth)
                root.forceActiveFocus()
            } else if (root.tool === "sketch" && sketchTimer.running) {
                sketchTimer.stop()
                if (root.sketch.length > 1 && root.sketchTrack >= 0)
                    EditorState.applyMotionSketch(root.sketchTrack, root.sketchClip, root.sketch, 2.0)
                root.sketch = []
            } else if (root.tool === "anchor" && root.anchorReady && root.box) {
                const f = root.overlayToBox(mouse.x, mouse.y)
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
            const made = EditorState.addTextAtPoint(mouse.x / root.sx, mouse.y / root.sy)
            if (made && made.track !== undefined) {
                // As After Effects: after placing one text, back to selection while you type.
                EditorState.preview.tool = "select"
                root.textEditRequested(made.track, made.clip, true)
            }
        }
    }
}
