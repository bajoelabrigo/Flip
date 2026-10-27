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
    function rebuild() {
        if (root.dragging)
            return
        if (!root.flat || root.trackIndex < 0) {
            root.keys = []
            root.samples = []
            return
        }
        const animated = EditorState.clipAnimatedProperties(root.trackIndex, root.clipIndex) || []
        const hasX = animated.indexOf("x") >= 0
        const hasY = animated.indexOf("y") >= 0
        if (!hasX && !hasY) {
            root.keys = []
            root.samples = []
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
        const pts = []
        if (out.length > 1) {
            const a = out[0].seconds
            const b = out[out.length - 1].seconds
            const steps = Math.min(240, Math.max(16, Math.round((b - a) * 30)))
            for (let i = 0; i <= steps; ++i)
                pts.push(root.centreAt(a + (b - a) * i / steps))
        }
        root.samples = pts
        path.requestPaint()
    }

    onBoxChanged: rebuild()
    Connections {
        target: EditorState
        function onTracksChanged() { root.rebuild() }
        function onSelectionChanged() { root.rebuild() }
    }
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
