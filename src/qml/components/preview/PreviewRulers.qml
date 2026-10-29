import QtQuick
import Drift
import ".."

// After Effects' rulers (Ctrl+R, 0.26): a strip along the top and the left of the preview, marked
// in project pixels and following the zoom and pan, with the pointer's place on each. A guide is
// dragged out of a ruler, moved by dragging it, and removed by dragging it back onto a ruler or off
// the frame. Only presses on a ruler or on one of its guides are taken: the rest of the preview
// (the clip, its handles) gets the pointer as before.
Item {
    id: root

    property Item viewport
    readonly property Item canvas: viewport ? viewport.canvas : null

    readonly property real rulerPx: 18
    readonly property real hitTolPx: 5
    readonly property real cx: canvas ? viewport.x + canvas.x : 0
    readonly property real cy: canvas ? viewport.y + canvas.y : 0
    readonly property real cw: canvas ? Math.max(1, canvas.width) : 1
    readonly property real ch: canvas ? Math.max(1, canvas.height) : 1
    // Read again whenever the frame is resized on screen, which a change of project size does too.
    readonly property real projectW: {
        void root.cw
        return Math.max(1, EditorState.projectFile.projectWidth())
    }
    readonly property real projectH: {
        void root.ch
        return Math.max(1, EditorState.projectFile.projectHeight())
    }
    // Screen px per project px.
    readonly property real scale: cw / projectW

    // The ruler guides: those of the set the rulers own, while guides are on.
    property string setId: ""
    readonly property var guides: {
        if (!EditorState.preview.guidesEnabled || !setId)
            return []
        const sets = EditorState.guideSets
        for (let i = 0; i < sets.length; ++i) {
            if (sets[i].id === setId && sets[i].active)
                return sets[i].items.filter(it => it.kind === "h" || it.kind === "v")
        }
        return []
    }
    Component.onCompleted: setId = EditorState.existingRulerGuideSet()

    // {id, axis: "x"|"y"} of the guide being dragged; isNew while it comes out of a ruler.
    property var drag: null
    property bool dragIsNew: false
    property bool dragRemoves: false
    property real dragPx: 0

    // The step between labelled ticks: the smallest round number at least 60 screen px apart.
    function majorStep() {
        const steps = [1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 5000]
        for (const s of steps) {
            if (s * root.scale >= 60)
                return s
        }
        return 10000
    }
    function guideAt(px, py) {
        let best = null
        let bestDist = hitTolPx
        for (const g of root.guides) {
            const along = g.kind === "v" ? py : px
            const lo = g.kind === "v" ? cy : cx
            const hi = g.kind === "v" ? cy + ch : cx + cw
            if (along < lo || along > hi)
                continue
            const at = g.kind === "v" ? cx + g.pos * cw : cy + g.pos * ch
            const d = Math.abs((g.kind === "v" ? px : py) - at)
            if (d < bestDist) {
                bestDist = d
                best = { id: g.id, axis: g.kind === "v" ? "x" : "y" }
            }
        }
        return best
    }
    function inTopRuler(px, py) {
        return py >= 0 && py < rulerPx && px >= rulerPx
    }
    function inLeftRuler(px, py) {
        return px >= 0 && px < rulerPx && py >= rulerPx
    }
    function moveDrag(px, py, shift) {
        const vertical = drag.axis === "x"
        let value = vertical ? (px - cx) / root.scale : (py - cy) / root.scale
        if (shift)
            value = Math.round(value / 10) * 10
        else
            value = Math.round(value)
        const size = vertical ? projectW : projectH
        dragPx = value
        dragRemoves = (vertical ? inLeftRuler(px, py) || px < cx || px > cx + cw
                                : inTopRuler(px, py) || py < cy || py > cy + ch)
        EditorState.setGuideItemProperty(setId, drag.id, "pos", Math.max(0, Math.min(1, value / size)))
    }
    function endDrag() {
        if (dragRemoves)
            EditorState.removeGuideItem(setId, drag.id)
        drag = null
        dragIsNew = false
        dragRemoves = false
    }

    HoverHandler {
        id: hover
        readonly property bool overGuide: !!root.guideAt(point.position.x, point.position.y)
        readonly property bool overRuler: root.inTopRuler(point.position.x, point.position.y)
                                          || root.inLeftRuler(point.position.x, point.position.y)
        cursorShape: {
            if (root.drag)
                return root.drag.axis === "x" ? Qt.SplitHCursor : Qt.SplitVCursor
            if (overRuler)
                return root.inTopRuler(point.position.x, point.position.y) ? Qt.SplitVCursor : Qt.SplitHCursor
            const g = root.guideAt(point.position.x, point.position.y)
            if (g)
                return g.axis === "x" ? Qt.SplitHCursor : Qt.SplitVCursor
            return undefined
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton
        preventStealing: true
        onPressed: (mouse) => {
            const hit = root.guideAt(mouse.x, mouse.y)
            const top = root.inTopRuler(mouse.x, mouse.y)
            const left = root.inLeftRuler(mouse.x, mouse.y)
            if (!hit && !top && !left) {
                mouse.accepted = false
                return
            }
            if (hit) {
                root.drag = hit
                root.dragIsNew = false
            } else {
                root.setId = EditorState.rulerGuideSet()
                const id = EditorState.addGuideItem(root.setId, top ? "h" : "v")
                root.drag = { id: id, axis: top ? "y" : "x" }
                root.dragIsNew = true
            }
            root.moveDrag(mouse.x, mouse.y, mouse.modifiers & Qt.ShiftModifier)
        }
        onPositionChanged: (mouse) => {
            if (root.drag)
                root.moveDrag(mouse.x, mouse.y, mouse.modifiers & Qt.ShiftModifier)
        }
        onReleased: if (root.drag) root.endDrag()
        onCanceled: if (root.drag) root.endDrag()
    }

    // The two rulers and the corner where they meet.
    Rectangle {
        x: 0
        y: 0
        width: root.rulerPx
        height: root.rulerPx
        color: Theme.panelBackground
        border.width: Theme.borderWidth
        border.color: Theme.panelBorder
    }
    Canvas {
        id: topRuler
        x: root.rulerPx
        y: 0
        width: root.width - root.rulerPx
        height: root.rulerPx
        onPaint: root.paintRuler(getContext("2d"), width, height, true)
    }
    Canvas {
        id: leftRuler
        x: 0
        y: root.rulerPx
        width: root.rulerPx
        height: root.height - root.rulerPx
        onPaint: root.paintRuler(getContext("2d"), width, height, false)
    }
    onCxChanged: repaintRulers()
    onCyChanged: repaintRulers()
    onCwChanged: repaintRulers()
    onChChanged: repaintRulers()
    onWidthChanged: repaintRulers()
    onHeightChanged: repaintRulers()
    function repaintRulers() {
        topRuler.requestPaint()
        leftRuler.requestPaint()
    }

    // Ticks in project px: a labelled one every majorStep, five small ones between.
    function paintRuler(ctx, w, h, horizontal) {
        ctx.reset()
        ctx.fillStyle = Theme.panelBackground
        ctx.fillRect(0, 0, w, h)
        ctx.strokeStyle = Theme.panelBorder
        ctx.lineWidth = 1
        ctx.beginPath()
        if (horizontal) {
            ctx.moveTo(0, h - 0.5)
            ctx.lineTo(w, h - 0.5)
        } else {
            ctx.moveTo(w - 0.5, 0)
            ctx.lineTo(w - 0.5, h)
        }
        ctx.stroke()
        const step = root.majorStep()
        const minor = step / 5
        // The ruler's own origin: canvas 0 sits at cx (cy) of the overlay, the ruler starts at rulerPx.
        const origin = (horizontal ? root.cx : root.cy) - root.rulerPx
        const length = horizontal ? w : h
        const first = Math.floor(-origin / root.scale / minor) * minor
        const last = (length - origin) / root.scale
        ctx.strokeStyle = Theme.mutedForeground
        ctx.fillStyle = Theme.mutedForeground
        ctx.font = "9px sans-serif"
        ctx.beginPath()
        for (let v = first; v <= last; v += minor) {
            const p = Math.round(origin + v * root.scale) + 0.5
            const major = Math.abs(v / step - Math.round(v / step)) < 1e-6
            if (horizontal) {
                ctx.moveTo(p, h)
                ctx.lineTo(p, h - (major ? h * 0.6 : h * 0.25))
            } else {
                ctx.moveTo(w, p)
                ctx.lineTo(w - (major ? w * 0.6 : w * 0.25), p)
            }
            if (major) {
                const label = String(Math.round(v))
                if (horizontal) {
                    ctx.fillText(label, p + 2, 9)
                } else {
                    ctx.save()
                    ctx.translate(9, p - 2)
                    ctx.rotate(-Math.PI / 2)
                    ctx.fillText(label, 0, 0)
                    ctx.restore()
                }
            }
        }
        ctx.stroke()
    }

    // Where the pointer is, on each ruler.
    Rectangle {
        visible: hover.hovered
        x: hover.point.position.x
        y: 0
        width: 1
        height: root.rulerPx
        color: Theme.primary
    }
    Rectangle {
        visible: hover.hovered
        x: 0
        y: hover.point.position.y
        width: root.rulerPx
        height: 1
        color: Theme.primary
    }

    // The guide being dragged, highlighted, and its place in px.
    Rectangle {
        visible: !!root.drag
        readonly property bool vertical: !!root.drag && root.drag.axis === "x"
        x: vertical ? root.cx + root.dragPx * root.scale - 1 : root.cx
        y: vertical ? root.cy : root.cy + root.dragPx * root.scale - 1
        width: vertical ? 3 : root.cw
        height: vertical ? root.ch : 3
        color: root.dragRemoves ? Theme.destructive : Theme.primary
        opacity: 0.8
    }
    Rectangle {
        visible: !!root.drag
        x: Math.min(root.width - width, mouseArea.mouseX + Theme.spacingLg)
        y: Math.min(root.height - height, mouseArea.mouseY + Theme.spacingLg)
        width: readout.implicitWidth + Theme.spacingMd * 2
        height: readout.implicitHeight + Theme.spacingSm * 2
        radius: Theme.radiusSm
        color: Theme.panelBackground
        border.width: Theme.borderWidth
        border.color: Theme.panelBorder
        Text {
            id: readout
            anchors.centerIn: parent
            text: root.dragRemoves ? qsTr("Release to remove") : root.dragPx + " px"
            color: Theme.foreground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }
    }
}
