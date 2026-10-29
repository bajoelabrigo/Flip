import QtQuick
import Drift
import ".."

// The selected clip's motion path, as After Effects draws it (0.25): the line its centre travels
// along while Position is animated, with a dot per key that is dragged to move the clip there at
// that time. Only for a clip seen straight on (no parent layer, camera or 3D tilt), where the
// canvas maps onto the overlay by a plain scale.
Item {
    id: root

    // The selected clip's box from TransformOverlay (canvas px), or null.
    property var box: null
    readonly property int trackIndex: box ? box.track : -1
    readonly property int clipIndex: box ? box.clip : -1
    readonly property real sx: box ? width / Math.max(1, box.canvasWidth) : 1
    readonly property real sy: box ? height / Math.max(1, box.canvasHeight) : 1
    readonly property bool flat: !!box && !box.parentActive && !box.cameraActive
                                 && !(box.rotationX || box.rotationY || box.z)

    property bool dragging: false
    // A handle being dragged: the line redraws, the dots stay (rebuilding them would drop the drag).
    property bool shaping: false
    // [{seconds, px, py, side: "in"|"out", ox, oy, xKey, yKey, prevSeconds, nextSeconds}] in canvas
    // px: After Effects' motion path handles. X and Y are keyed apart, so a key's spatial handle is
    // the pair of its X and Y value handles (outDy of each), which is exactly how the path bends.
    property var handles: []
    // [{seconds, x, y, hasX, hasY}] in canvas px of the centre, and the sampled line.
    property var keys: []
    property var samples: []

    function valueAt(prop, seconds, base) {
        return EditorState.propertyValueAt(root.trackIndex, root.clipIndex, prop, seconds, base)
    }
    function centreAt(seconds) {
        const cw = root.box.canvasWidth
        const ch = root.box.canvasHeight
        return {
            x: root.valueAt("x", seconds, 0) + root.valueAt("width", seconds, cw) / 2,
            y: root.valueAt("y", seconds, 0) + root.valueAt("height", seconds, ch) / 2
        }
    }
    // True when a press at (mx, my) of `item` falls on the clip as it is drawn now. A straight
    // handle or another key's dot there gives the press to the clip, so the text or shape under it
    // can still be dragged: a third of the way along a segment the clip passes right over them.
    function overLayer(item, mx, my) {
        if (!root.box)
            return false
        const p = item.mapToItem(root, mx, my)
        const cx = p.x / root.sx
        const cy = p.y / root.sy
        return cx >= root.box.x && cx <= root.box.x + root.box.width
               && cy >= root.box.y && cy <= root.box.y + root.box.height
    }
    function keyAt(list, seconds) {
        for (const k of list) {
            if (Math.abs(k.seconds - seconds) < 1e-4)
                return k
        }
        return null
    }
    function samplesNow() {
        const pts = []
        const ks = root.keys
        if (ks.length > 1) {
            const a = ks[0].seconds
            const b = ks[ks.length - 1].seconds
            const steps = Math.min(240, Math.max(16, Math.round((b - a) * 30)))
            for (let i = 0; i <= steps; ++i)
                pts.push(root.centreAt(a + (b - a) * i / steps))
        }
        return pts
    }
    function buildHandles() {
        const xs = EditorState.clipKeyframes(root.trackIndex, root.clipIndex, "x") || []
        const ys = EditorState.clipKeyframes(root.trackIndex, root.clipIndex, "y") || []
        const out = []
        for (let i = 0; i < root.keys.length; ++i) {
            const k = root.keys[i]
            const xk = root.keyAt(xs, k.seconds)
            const yk = root.keyAt(ys, k.seconds)
            if (!xk || !yk || xk.hold)
                continue
            const prev = i > 0 ? root.keys[i - 1] : null
            const next = i < root.keys.length - 1 ? root.keys[i + 1] : null
            // A straight (zero) handle is drawn a third of the way along its segment, so it can
            // be taken and pulled out, as After Effects lets you.
            const side = (name, other, dx, dy) => {
                let ox = dx
                let oy = dy
                const straight = Math.abs(ox) < 1e-6 && Math.abs(oy) < 1e-6
                if (straight) {
                    ox = (other.x - k.x) / 3
                    oy = (other.y - k.y) / 3
                }
                out.push({ "seconds": k.seconds, "side": name, "px": k.x, "py": k.y, "ox": ox, "oy": oy, "straight": straight,
                           "xKey": xk, "yKey": yk,
                           "prevSeconds": prev ? prev.seconds : NaN, "nextSeconds": next ? next.seconds : NaN })
            }
            if (next)
                side("out", next, xk.outDy, yk.outDy)
            if (prev)
                side("in", prev, xk.inDy, yk.inDy)
        }
        root.handles = out
    }

    function rebuild() {
        if (root.shaping) {
            root.samples = root.samplesNow()
            path.requestPaint()
            return
        }
        if (root.dragging)
            return
        if (!root.flat || root.trackIndex < 0) {
            root.keys = []
            root.samples = []
            root.handles = []
            return
        }
        const animated = EditorState.clipAnimatedProperties(root.trackIndex, root.clipIndex) || []
        const hasX = animated.indexOf("x") >= 0
        const hasY = animated.indexOf("y") >= 0
        if (!hasX && !hasY) {
            root.keys = []
            root.samples = []
            root.handles = []
            return
        }
        const times = {}
        const collect = (prop, flag) => {
            for (const k of (EditorState.clipKeyframes(root.trackIndex, root.clipIndex, prop) || [])) {
                const slot = Math.round(k.seconds * 1000)
                times[slot] = times[slot] || { seconds: k.seconds, hasX: false, hasY: false }
                times[slot][flag] = true
            }
        }
        if (hasX)
            collect("x", "hasX")
        if (hasY)
            collect("y", "hasY")
        const list = Object.keys(times).map((k) => times[k]).sort((a, b) => a.seconds - b.seconds)
        const out = []
        for (const t of list) {
            const c = root.centreAt(t.seconds)
            out.push({ seconds: t.seconds, x: c.x, y: c.y, hasX: t.hasX, hasY: t.hasY })
        }
        root.keys = out
        // The line between the first and last key, sampled finely enough to show the curves.
        root.samples = root.samplesNow()
        root.buildHandles()
        path.requestPaint()
    }

    onBoxChanged: rebuild()
    Connections {
        target: EditorState
        function onTracksChanged() { root.rebuild() }
        function onSelectionChanged() { root.rebuild() }
        // Dragging the clip in the preview writes its keys live but only says so at the release:
        // the path stood still (and its new key was missing) until then (Jorge, 0.26). Once a frame.
        function onClipPropertiesPreviewed(trackIndex, clipIndex, keys) {
            if (trackIndex !== root.trackIndex || clipIndex !== root.clipIndex || root.rebuildQueued)
                return
            if (keys.indexOf("x") < 0 && keys.indexOf("y") < 0 && keys.indexOf("width") < 0
                    && keys.indexOf("height") < 0)
                return
            root.rebuildQueued = true
            Qt.callLater(() => {
                root.rebuildQueued = false
                root.rebuild()
            })
        }
    }
    property bool rebuildQueued: false
    onWidthChanged: path.requestPaint()
    onHeightChanged: path.requestPaint()

    Canvas {
        id: path
        anchors.fill: parent
        visible: root.samples.length > 1
        onPaint: {
            const ctx = getContext("2d")
            ctx.reset()
            const pts = root.samples
            if (pts.length < 2)
                return
            ctx.strokeStyle = Theme.primary
            ctx.lineWidth = 1.5
            ctx.setLineDash([5, 4])
            ctx.beginPath()
            ctx.moveTo(pts[0].x * root.sx, pts[0].y * root.sy)
            for (let i = 1; i < pts.length; ++i)
                ctx.lineTo(pts[i].x * root.sx, pts[i].y * root.sy)
            ctx.stroke()
        }
    }

    // The handles: a line from the key and a round grip at its end.
    Repeater {
        model: root.handles
        delegate: Item {
            id: hd
            required property var modelData
            property real liveOx: modelData.ox
            property real liveOy: modelData.oy
            readonly property real kx: modelData.px * root.sx
            readonly property real ky: modelData.py * root.sy
            Rectangle {
                x: hd.kx
                y: hd.ky
                width: Math.hypot(hd.liveOx * root.sx, hd.liveOy * root.sy)
                height: 1
                color: Theme.primary
                opacity: 0.7
                transformOrigin: Item.TopLeft
                rotation: Math.atan2(hd.liveOy * root.sy, hd.liveOx * root.sx) * 180 / Math.PI
            }
            Rectangle {
                id: grip
                width: 8
                height: 8
                radius: 4
                x: hd.kx + hd.liveOx * root.sx - width / 2
                y: hd.ky + hd.liveOy * root.sy - height / 2
                color: gripMouse.pressed ? Theme.primary : Theme.panelBackground
                border.width: 1.5
                border.color: Theme.primary
                MouseArea {
                    id: gripMouse
                    anchors.fill: parent
                    anchors.margins: -5
                    preventStealing: true
                    cursorShape: Qt.CrossCursor
                    property bool wasLinked: true
                    onPressed: (mouse) => {
                        if (hd.modelData.straight && root.overLayer(gripMouse, mouse.x, mouse.y)) {
                            mouse.accepted = false
                            return
                        }
                        wasLinked = EditorState.positionLinked
                        // The X and Y handles are set apart here; linked, one would rescale the other.
                        EditorState.setPositionLinkedForDrag(false)
                        root.shaping = true
                        EditorState.beginPreviewDrag(qsTr("Shape motion path"))
                    }
                    onPositionChanged: (mouse) => {
                        if (!pressed)
                            return
                        const p = mapToItem(root, mouse.x, mouse.y)
                        hd.liveOx = p.x / root.sx - hd.modelData.px
                        hd.liveOy = p.y / root.sy - hd.modelData.py
                        hd.apply(mouse.modifiers)
                    }
                    onReleased: finish()
                    onCanceled: finish()
                    function finish() {
                        EditorState.commitPreviewDrag()
                        EditorState.setPositionLinkedForDrag(wasLinked)
                        root.shaping = false
                        root.rebuild()
                    }
                }
            }
            // Writes this side's handle into the X and Y keys; the other side follows, mirrored,
            // unless Ctrl breaks them apart (After Effects' Convert Vertex).
            function apply(mods) {
                const m = hd.modelData
                const xk = m.xKey
                const yk = m.yKey
                const out = m.side === "out"
                const seg = out ? m.nextSeconds - m.seconds : m.seconds - m.prevSeconds
                const reach = Math.max(1 / 120, (isNaN(seg) ? 1 : seg) / 3)
                const corner = (mods & Qt.ControlModifier) !== 0 || !!xk.corner
                let xOut = xk.outDx > 0 ? xk.outDx : reach
                let xIn = xk.inDx < 0 ? xk.inDx : -reach
                const xInDyOld = xk.inDy
                const yInDyOld = yk.inDy
                const xOutDyOld = xk.outDy
                const yOutDyOld = yk.outDy
                let xo = xOutDyOld, yo = yOutDyOld, xi = xInDyOld, yi = yInDyOld
                if (out) {
                    xo = hd.liveOx
                    yo = hd.liveOy
                    if (!corner) {
                        const r = Math.abs(xIn) / Math.max(1e-6, xOut)
                        xi = -xo * r
                        yi = -yo * r
                    }
                } else {
                    xi = hd.liveOx
                    yi = hd.liveOy
                    if (!corner) {
                        const r = xOut / Math.max(1e-6, Math.abs(xIn))
                        xo = -xi * r
                        yo = -yi * r
                    }
                }
                EditorState.previewSetKeyframeTangents(root.trackIndex, root.clipIndex, "x", m.seconds,
                                                       xIn, xi, xOut, xo, corner)
                EditorState.previewSetKeyframeTangents(root.trackIndex, root.clipIndex, "y", m.seconds,
                                                       xIn, yi, xOut, yo, corner)
            }
        }
    }

    Repeater {
        model: root.keys
        delegate: Rectangle {
            id: dot
            required property var modelData
            required property int index
            readonly property bool here: Math.abs(modelData.seconds - EditorState.playheadSeconds) < 1 / 120
            width: 11
            height: 11
            radius: 2
            rotation: 45
            x: modelData.x * root.sx - width / 2
            y: modelData.y * root.sy - height / 2
            color: here || dotMouse.pressed ? Theme.primary : Theme.panelBackground
            border.width: 1.5
            border.color: Theme.primary

            MouseArea {
                id: dotMouse
                anchors.fill: parent
                anchors.margins: -5
                hoverEnabled: true
                preventStealing: true
                cursorShape: Qt.SizeAllCursor
                property point press
                property real baseX: 0
                property real baseY: 0
                onPressed: (mouse) => {
                    if (!dot.here && root.overLayer(dotMouse, mouse.x, mouse.y)) {
                        mouse.accepted = false
                        return
                    }
                    const p = mapToItem(root, mouse.x, mouse.y)
                    press = Qt.point(p.x, p.y)
                    // The keys' own values (top-left), which the drag offsets.
                    baseX = root.valueAt("x", dot.modelData.seconds, 0)
                    baseY = root.valueAt("y", dot.modelData.seconds, 0)
                    root.dragging = true
                    EditorState.playheadSeconds = dot.modelData.seconds
                    EditorState.beginPreviewDrag(qsTr("Move keyframe"))
                }
                onPositionChanged: (mouse) => {
                    if (!pressed)
                        return
                    const p = mapToItem(root, mouse.x, mouse.y)
                    const dx = (p.x - press.x) / root.sx
                    const dy = (p.y - press.y) / root.sy
                    const s = dot.modelData.seconds
                    if (dot.modelData.hasX)
                        EditorState.previewMoveClipKeyframe(root.trackIndex, root.clipIndex, "x", s, s, baseX + dx)
                    if (dot.modelData.hasY)
                        EditorState.previewMoveClipKeyframe(root.trackIndex, root.clipIndex, "y", s, s, baseY + dy)
                    dot.x = p.x - dot.width / 2 - (press.x - (dot.modelData.x * root.sx))
                    dot.y = p.y - dot.height / 2 - (press.y - (dot.modelData.y * root.sy))
                }
                onReleased: {
                    EditorState.commitPreviewDrag()
                    root.dragging = false
                    root.rebuild()
                }
                onCanceled: {
                    EditorState.commitPreviewDrag()
                    root.dragging = false
                    root.rebuild()
                }
            }

            ThemedToolTip {
                visible: dotMouse.containsMouse && !dotMouse.pressed
                text: dot.modelData.seconds.toFixed(2) + " s · " + qsTr("drag to move the clip at this keyframe")
            }
        }
    }
}
