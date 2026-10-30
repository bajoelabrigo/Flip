import QtQuick
import QtQuick.Controls.Basic
import QtCore
import Drift
import ".."

// Curvas (0.26, Jorge: «creame este para curvas… que se abra en la barra lateral»), as EasyCurve
// works: a graph of the speed curve with its handles to drag, Ease in / Ease out / Ease in-out /
// Linear / Custom, a 4-key mode where the curve goes up to a peak and back (the stretches before
// and after the middle key of three), Read (the picked keys' curve into the graph), Apply to the
// keys picked on the timeline, and presets of your own with their picture, exported and imported
// as a JSON file.
Item {
    id: root

    readonly property var picked: EditorState.pickedKeyframes || ({})
    readonly property int pickedCount: (picked.keys || []).length
    // What a curve goes onto: the picked keys, else every key of the selected clip's animated
    // properties. Re-read when the pick, the selection or the clips change.
    readonly property int targetCount: {
        root.picked
        EditorState.selectionRevision
        EditorState.tracksRevision
        const t = EditorState.curveTargetKeys()
        return (t && t.keys) ? t.keys.length : 0
    }
    // "two" or "four" (EasyCurve's 4-KEY).
    property string mode: "two"
    // The handles in graph coordinates (x 0..1 left to right, y 0 at the bottom key and 1 at the
    // top one): two for a 2-key curve, four for a 4-key one (the peak sits at x 0.5).
    property var handles: [Qt.point(0.42, 0), Qt.point(0.58, 1)]
    property string preset: "easeInOut"

    readonly property var twoPresets: [
        { "id": "easeIn", "label": qsTr("Ease in"), "h": [[0.42, 0], [1, 1]] },
        { "id": "easeOut", "label": qsTr("Ease out"), "h": [[0, 0], [0.58, 1]] },
        { "id": "easeInOut", "label": qsTr("Ease in-out"), "h": [[0.42, 0], [0.58, 1]] },
        { "id": "linear", "label": qsTr("Linear"), "h": [[0.333, 0.333], [0.667, 0.667]] },
        { "id": "back", "label": qsTr("Overshoot"), "h": [[0.34, 0], [0.64, 1.35]] },
        { "id": "anticipate", "label": qsTr("Anticipate"), "h": [[0.36, -0.35], [0.66, 1]] }
    ]
    readonly property var fourPresets: [
        { "id": "easeIn", "label": qsTr("Ease in"), "h": [[0.21, 0], [0.5, 1], [0.5, 1], [0.79, 0]] },
        { "id": "easeOut", "label": qsTr("Ease out"), "h": [[0, 0], [0.29, 1], [0.71, 1], [1, 0]] },
        { "id": "easeInOut", "label": qsTr("Ease in-out"), "h": [[0.21, 0], [0.29, 1], [0.71, 1], [0.79, 0]] },
        { "id": "linear", "label": qsTr("Linear"), "h": [[0.167, 0.333], [0.333, 0.667], [0.667, 0.667], [0.833, 0.333]] },
        { "id": "spike", "label": qsTr("Spike"), "h": [[0.25, 0], [0.5, 1], [0.5, 1], [0.75, 0]] }
    ]
    readonly property var presetList: mode === "four" ? fourPresets : twoPresets

    function pointsOf(list) {
        return list.map(p => Qt.point(p[0], p[1]))
    }
    function choose(p, keep) {
        root.preset = p.id
        root.handles = root.pointsOf(p.h)
        graph.requestPaint()
        if (!keep)
            root.apply()
    }
    function setMode(m) {
        if (root.mode === m)
            return
        root.mode = m
        root.choose(root.presetList[2], true)
    }
    function reset() {
        root.choose(root.presetList[2], true)
    }
    // The handles as the two stretches' unit curves for applyCurveToPicked.
    function curves() {
        const h = root.handles
        if (root.mode === "two")
            return { "a": [h[0].x, h[0].y, h[1].x, h[1].y], "b": [] }
        return { "a": [h[0].x / 0.5, h[0].y, h[1].x / 0.5, h[1].y],
                 "b": [(h[2].x - 0.5) / 0.5, 1 - h[2].y, (h[3].x - 0.5) / 0.5, 1 - h[3].y] }
    }
    // As EasyCurve: a preset chosen or a handle let go goes straight onto the keys.
    function apply() {
        if (root.targetCount === 0)
            return
        const c = root.curves()
        EditorState.applyCurveToPicked(c.a, c.b)
    }
    // EasyCurve's READ: the picked keys' curve into the graph.
    function read() {
        const r = EditorState.pickedKeyframeCurves()
        if (!r.ok)
            return
        const a = r.a
        if (r.b && r.keys >= 3) {
            root.mode = "four"
            const b = r.b
            root.handles = [Qt.point(a[0] * 0.5, a[1]), Qt.point(a[2] * 0.5, a[3]),
                            Qt.point(0.5 + b[0] * 0.5, 1 - b[1]), Qt.point(0.5 + b[2] * 0.5, 1 - b[3])]
        } else {
            root.mode = "two"
            root.handles = [Qt.point(a[0], a[1]), Qt.point(a[2], a[3])]
        }
        root.preset = "custom"
        graph.requestPaint()
    }

    // ----- Saved curves (per mode), kept with the app's settings --------------------------------
    Settings {
        id: store
        category: "curves"
        property string two: "[]"
        property string four: "[]"
    }
    property var saved: []
    function loadSaved() {
        try {
            root.saved = JSON.parse(root.mode === "four" ? store.four : store.two) || []
        } catch (e) {
            root.saved = []
        }
    }
    function writeSaved(list) {
        const text = JSON.stringify(list)
        if (root.mode === "four")
            store.four = text
        else
            store.two = text
        root.saved = list
    }
    function saveCurrent() {
        const list = root.saved.slice()
        list.push({ "h": root.handles.map(p => [Math.round(p.x * 1000) / 1000, Math.round(p.y * 1000) / 1000]) })
        root.writeSaved(list)
    }
    function removeSaved(i) {
        const list = root.saved.slice()
        list.splice(i, 1)
        root.writeSaved(list)
    }
    function exportSaved() {
        const url = FileDialogs.saveFile(qsTr("Export curves"), [qsTr("Curves (*.json)")], "curvas", "json")
        if (!url || url.toString() === "")
            return
        const ok = EditorState.writeTextFile(url, JSON.stringify({ "flipCurves": 1, "mode": root.mode, "curves": root.saved }, null, 1))
        if (ok)
            Toasts.success(qsTr("Curves exported"))
    }
    function importSaved() {
        const url = FileDialogs.openFile(qsTr("Import curves"), [qsTr("Curves (*.json)")])
        if (!url || url.toString() === "")
            return
        try {
            const doc = JSON.parse(EditorState.readTextFile(url))
            const want = root.mode === "four" ? 4 : 2
            const add = (doc.curves || []).filter(c => c && c.h && c.h.length === want)
            if (add.length === 0) {
                Toasts.error(qsTr("No curves of this mode in that file"))
                return
            }
            root.writeSaved(root.saved.concat(add))
            Toasts.success(qsTr("%n curves imported", "", add.length))
        } catch (e) {
            Toasts.error(qsTr("That file is not a curves file"))
        }
    }
    onModeChanged: loadSaved()
    Component.onCompleted: loadSaved()

    height: col.height
    implicitHeight: col.height

    Column {
        id: col
        width: parent.width
        spacing: Theme.spacingMd

        Row {
            width: parent.width
            spacing: 6
            ThemedChip {
                text: qsTr("2 keys")
                variant: "outline"
                selected: root.mode === "two"
                tooltip: qsTr("A curve from one key to the next")
                onClicked: root.setMode("two")
            }
            ThemedChip {
                text: qsTr("4 keys")
                variant: "outline"
                selected: root.mode === "four"
                tooltip: qsTr("Up to a peak and back: the stretches before and after the middle of three keys")
                onClicked: root.setMode("four")
            }
            Item { width: 1; height: 1 }
            ThemedChip {
                text: qsTr("Read")
                variant: "outline"
                enabled: root.targetCount > 0
                tooltip: qsTr("Puts the curve of the picked keys in the graph")
                onClicked: root.read()
            }
        }

        Flow {
            width: parent.width
            spacing: 6
            Repeater {
                model: root.presetList
                delegate: ThemedChip {
                    required property var modelData
                    text: modelData.label
                    variant: "outline"
                    selected: root.preset === modelData.id
                    onClicked: root.choose(modelData)
                }
            }
            ThemedChip {
                text: qsTr("Custom")
                variant: "outline"
                selected: root.preset === "custom"
                enabled: false
            }
        }

        // ----- The graph ---------------------------------------------------------------------
        Rectangle {
            id: frame
            width: parent.width
            height: width
            radius: Theme.radiusMd
            color: Theme.darkMode ? "#0d1420" : "#eef2f8"
            border.width: Theme.borderWidth
            border.color: Theme.panelBorder

            // y from -0.35 to 1.35 so handles can overshoot, as EasyCurve's.
            readonly property real pad: 14
            readonly property real lo: -0.35
            readonly property real hi: 1.35
            function toPx(p) {
                const w = width - 2 * pad, h = height - 2 * pad
                return Qt.point(pad + p.x * w, pad + (hi - p.y) / (hi - lo) * h)
            }
            function fromPx(x, y) {
                const w = width - 2 * pad, h = height - 2 * pad
                return Qt.point((x - pad) / w, hi - (y - pad) / h * (hi - lo))
            }
            // The fixed points: the keys (and the peak in 4-key mode).
            function keyPoints() {
                return root.mode === "four" ? [Qt.point(0, 0), Qt.point(0.5, 1), Qt.point(1, 0)]
                                            : [Qt.point(0, 0), Qt.point(1, 1)]
            }

            Canvas {
                id: graph
                anchors.fill: parent
                property var h: root.handles
                property string m: root.mode
                onHChanged: requestPaint()
                onMChanged: requestPaint()
                onWidthChanged: requestPaint()
                onPaint: {
                    const ctx = getContext("2d")
                    ctx.reset()
                    const P = p => frame.toPx(p)
                    // Grid: quarters, and the 0 and 1 lines brighter.
                    ctx.lineWidth = 1
                    for (let i = 0; i <= 4; ++i) {
                        ctx.strokeStyle = Theme.darkMode ? "#1d2a3d" : "#d5dce8"
                        const x = P(Qt.point(i / 4, 0)).x
                        ctx.beginPath(); ctx.moveTo(x, frame.pad); ctx.lineTo(x, height - frame.pad); ctx.stroke()
                        const y = P(Qt.point(0, i / 4)).y
                        ctx.beginPath(); ctx.moveTo(frame.pad, y); ctx.lineTo(width - frame.pad, y); ctx.stroke()
                    }
                    const a = frame.keyPoints()
                    const hs = root.handles
                    const segs = root.mode === "four" ? [[a[0], hs[0], hs[1], a[1]], [a[1], hs[2], hs[3], a[2]]]
                                                      : [[a[0], hs[0], hs[1], a[1]]]
                    // Handle lines.
                    ctx.strokeStyle = Theme.darkMode ? "#5a7aa8" : "#7d93b8"
                    ctx.setLineDash([3, 3])
                    for (const s of segs) {
                        const p0 = P(s[0]), p1 = P(s[1]), p2 = P(s[2]), p3 = P(s[3])
                        ctx.beginPath(); ctx.moveTo(p0.x, p0.y); ctx.lineTo(p1.x, p1.y); ctx.stroke()
                        ctx.beginPath(); ctx.moveTo(p3.x, p3.y); ctx.lineTo(p2.x, p2.y); ctx.stroke()
                    }
                    ctx.setLineDash([])
                    // The curve.
                    ctx.strokeStyle = Theme.primary
                    ctx.lineWidth = 2.5
                    ctx.beginPath()
                    const s0 = P(segs[0][0])
                    ctx.moveTo(s0.x, s0.y)
                    for (const s of segs) {
                        const p1 = P(s[1]), p2 = P(s[2]), p3 = P(s[3])
                        ctx.bezierCurveTo(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y)
                    }
                    ctx.stroke()
                    // Keys (rings) and handles (dots).
                    ctx.lineWidth = 2
                    for (const k of a) {
                        const p = P(k)
                        ctx.beginPath(); ctx.arc(p.x, p.y, 5, 0, Math.PI * 2)
                        ctx.fillStyle = Theme.darkMode ? "#0d1420" : "#eef2f8"
                        ctx.fill(); ctx.strokeStyle = Theme.primary; ctx.stroke()
                    }
                    for (let i = 0; i < hs.length; ++i) {
                        const p = P(hs[i])
                        ctx.beginPath(); ctx.arc(p.x, p.y, i === dragArea.grabbed ? 7 : 6, 0, Math.PI * 2)
                        ctx.fillStyle = Theme.primary
                        ctx.fill()
                    }
                }
            }

            MouseArea {
                id: dragArea
                anchors.fill: parent
                preventStealing: true
                hoverEnabled: true
                property int grabbed: -1
                cursorShape: grabbed >= 0 ? Qt.ClosedHandCursor : Qt.CrossCursor
                function nearest(x, y) {
                    let best = -1, bestD = 18 * 18
                    for (let i = 0; i < root.handles.length; ++i) {
                        const p = frame.toPx(root.handles[i])
                        const d = (p.x - x) * (p.x - x) + (p.y - y) * (p.y - y)
                        if (d < bestD) {
                            bestD = d
                            best = i
                        }
                    }
                    return best
                }
                // Applied live while a handle is dragged, the whole drag one undo step.
                property bool live: false
                onPressed: mouse => {
                    grabbed = nearest(mouse.x, mouse.y)
                    graph.requestPaint()
                    live = grabbed >= 0 && root.targetCount > 0
                    if (live)
                        EditorState.beginEditSession(qsTr("Curve applied"))
                }
                onPositionChanged: mouse => {
                    if (grabbed < 0)
                        return
                    const p = frame.fromPx(mouse.x, mouse.y)
                    // A handle stays within its own stretch in time (x), free in value (y).
                    let x0 = 0, x1 = 1
                    if (root.mode === "four") {
                        x0 = grabbed < 2 ? 0 : 0.5
                        x1 = grabbed < 2 ? 0.5 : 1
                    }
                    const list = root.handles.slice()
                    list[grabbed] = Qt.point(Math.max(x0, Math.min(x1, p.x)), Math.max(frame.lo, Math.min(frame.hi, p.y)))
                    root.handles = list
                    root.preset = "custom"
                    if (live)
                        root.apply()
                }
                onReleased: {
                    grabbed = -1
                    graph.requestPaint()
                    if (live)
                        EditorState.endEditSession(true)
                    live = false
                }
                onCanceled: {
                    grabbed = -1
                    if (live)
                        EditorState.endEditSession(true)
                    live = false
                }
                onDoubleClicked: root.reset()
            }
        }

        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            size: "sm"
            opacity: 0.75
            text: root.pickedCount > 0
                  ? qsTr("%n keys picked on the timeline.", "", root.pickedCount)
                  : root.targetCount > 0
                  ? qsTr("Goes onto every key of the selected clip. To shape only some, pick their diamonds on the timeline (Ctrl for more).")
                  : (root.mode === "four"
                     ? qsTr("Pick three keys on the timeline (click the diamonds, Ctrl for more): the curve rises to the middle one and comes back.")
                     : qsTr("Pick keys on the timeline (click the diamonds, Ctrl for more): each one takes the curve to the next."))
        }

        Row {
            width: parent.width
            spacing: 6
            ThemedButton {
                width: (parent.width - 12) / 3
                text: qsTr("Reset")
                variant: "secondary"
                onClicked: root.reset()
            }
            ThemedButton {
                width: (parent.width - 12) / 3
                text: qsTr("Apply")
                variant: "primary"
                enabled: root.targetCount > 0
                onClicked: root.apply()
            }
            ThemedButton {
                width: (parent.width - 12) / 3
                text: qsTr("Save")
                tooltip: qsTr("Keeps this curve in My curves")
                variant: "secondary"
                onClicked: root.saveCurrent()
            }
        }

        // ----- My curves ---------------------------------------------------------------------
        Row {
            width: parent.width
            spacing: 6
            ThemedLabel {
                anchors.verticalCenter: parent.verticalCenter
                width: parent.width - exportButton.width - importButton.width - 12
                text: (root.mode === "four" ? qsTr("My 4-key curves") : qsTr("My curves")) + "  (" + root.saved.length + ")"
                size: "sm"
            }
            ThemedButton {
                id: exportButton
                text: qsTr("Export")
                variant: "secondary"
                enabled: root.saved.length > 0
                onClicked: root.exportSaved()
            }
            ThemedButton {
                id: importButton
                text: qsTr("Import")
                variant: "secondary"
                onClicked: root.importSaved()
            }
        }

        Flow {
            width: parent.width
            spacing: 6
            Repeater {
                model: root.saved
                delegate: Rectangle {
                    id: tile
                    required property var modelData
                    required property int index
                    width: 64
                    height: 64
                    radius: Theme.radiusSm
                    color: Theme.darkMode ? "#0d1420" : "#eef2f8"
                    border.width: tileMouse.containsMouse ? 2 : Theme.borderWidth
                    border.color: tileMouse.containsMouse ? Theme.primary : Theme.panelBorder
                    Canvas {
                        anchors.fill: parent
                        anchors.margins: 8
                        onPaint: {
                            const ctx = getContext("2d")
                            ctx.reset()
                            const h = tile.modelData.h || []
                            const four = h.length === 4
                            const P = p => Qt.point(p[0] * width, (1.35 - p[1]) / 1.7 * height)
                            const keys = four ? [[0, 0], [0.5, 1], [1, 0]] : [[0, 0], [1, 1]]
                            ctx.strokeStyle = Theme.primary
                            ctx.lineWidth = 2
                            ctx.beginPath()
                            const k0 = P(keys[0])
                            ctx.moveTo(k0.x, k0.y)
                            const a = P(h[0]), b = P(h[1]), k1 = P(keys[1])
                            ctx.bezierCurveTo(a.x, a.y, b.x, b.y, k1.x, k1.y)
                            if (four) {
                                const c = P(h[2]), d = P(h[3]), k2 = P(keys[2])
                                ctx.bezierCurveTo(c.x, c.y, d.x, d.y, k2.x, k2.y)
                            }
                            ctx.stroke()
                        }
                    }
                    MouseArea {
                        id: tileMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        acceptedButtons: Qt.LeftButton | Qt.RightButton
                        onClicked: mouse => {
                            if (mouse.button === Qt.RightButton) {
                                root.removeSaved(tile.index)
                                return
                            }
                            root.choose({ "id": "custom", "h": tile.modelData.h })
                        }
                        onDoubleClicked: {
                            root.choose({ "id": "custom", "h": tile.modelData.h })
                            if (root.pickedCount > 0)
                                root.apply()
                        }
                    }
                    ThemedToolTip {
                        visible: tileMouse.containsMouse
                        text: qsTr("Click to load it, double click to apply it, right click to delete it")
                    }
                }
            }
            Rectangle {
                width: 64
                height: 64
                radius: Theme.radiusSm
                color: "transparent"
                border.width: Theme.borderWidth
                border.color: Theme.panelBorder
                Text {
                    anchors.centerIn: parent
                    text: "+"
                    color: Theme.mutedForeground
                    font.pixelSize: 26
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: root.saveCurrent()
                }
            }
        }
    }
}
