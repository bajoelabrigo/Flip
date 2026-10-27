import QtQuick
import Drift
import ".."

// The volume line over an audio clip's waveform, as Premiere's (0.25): it shows the clip's level
// across its length and is edited right there. Dragging the line moves its stretch between two
// keys up or down (the whole level when it has none), Ctrl+click puts a key on it, a key's dot is
// dragged in time and level, and a double-click on a dot takes it away. The points are the clip's
// own `volume` keys, the ones the keyframe rows and the curve editor show too.
//
// The height reads in dB, from −40 dB at the bottom to +6 dB at the top (a gain of 2).
Item {
    id: root

    property int trackIndex: -1
    property int clipIndex: -1
    // Where the clip starts on the timeline and its zoom, in the clip item's terms.
    property real clipStart: 0
    property real pxPerSecond: 100
    // The level an unkeyed clip plays at.
    property real staticGain: 1.0

    readonly property real minDb: -40
    readonly property real maxDb: 6

    // The keys, {seconds, value}, timeline seconds. Frozen while a drag lasts: each step rewrites
    // the project and rebuilding under the pointer would drop the drag.
    property bool dragging: false
    property var liveKeys: {
        void EditorState.tracksRevision
        return root.trackIndex >= 0 && root.clipIndex >= 0
            ? (EditorState.clipKeyframes(root.trackIndex, root.clipIndex, "volume") || []) : []
    }
    property var keys: []
    onLiveKeysChanged: if (!dragging) keys = liveKeys
    onDraggingChanged: if (!dragging) keys = liveKeys
    Component.onCompleted: keys = liveKeys
    // A lone key at the start is the clip's resting level, not an animation.
    readonly property bool animated: keys.length > 1 || (keys.length === 1 && keys[0].seconds > root.clipStart + 1e-4)

    function dbOf(gain) {
        return gain <= 0.0001 ? root.minDb : Math.max(root.minDb, Math.min(root.maxDb, 20 * Math.log10(gain)))
    }
    function gainOf(db) {
        return db <= root.minDb + 0.01 ? 0 : Math.pow(10, db / 20)
    }
    function yOf(gain) {
        return (1 - (dbOf(gain) - root.minDb) / (root.maxDb - root.minDb)) * root.height
    }
    function gainAtY(y) {
        const t = 1 - Math.max(0, Math.min(root.height, y)) / Math.max(1, root.height)
        return Math.min(2, gainOf(root.minDb + t * (root.maxDb - root.minDb)))
    }
    function xOf(seconds) {
        return (seconds - root.clipStart) * root.pxPerSecond
    }
    // The level the line shows at x (linear between keys, as it draws).
    function gainAtX(x) {
        if (!root.animated)
            return root.keys.length === 1 ? root.keys[0].value : root.staticGain
        const s = root.clipStart + x / root.pxPerSecond
        const ks = root.keys
        if (s <= ks[0].seconds)
            return ks[0].value
        for (let i = 1; i < ks.length; ++i) {
            if (s <= ks[i].seconds) {
                const a = ks[i - 1]
                const b = ks[i]
                const f = (s - a.seconds) / Math.max(1e-6, b.seconds - a.seconds)
                return a.value + (b.value - a.value) * f
            }
        }
        return ks[ks.length - 1].value
    }

    Canvas {
        id: line
        anchors.fill: parent
        onPaint: {
            const ctx = getContext("2d")
            ctx.reset()
            ctx.strokeStyle = Theme.primary
            ctx.lineWidth = lineMouse.containsMouse || root.dragging ? 2 : 1.25
            ctx.beginPath()
            if (!root.animated) {
                const y = root.yOf(root.gainAtX(0))
                ctx.moveTo(0, y)
                ctx.lineTo(width, y)
            } else {
                const ks = root.keys
                ctx.moveTo(0, root.yOf(ks[0].value))
                for (let i = 0; i < ks.length; ++i)
                    ctx.lineTo(root.xOf(ks[i].seconds), root.yOf(ks[i].value))
                ctx.lineTo(width, root.yOf(ks[ks.length - 1].value))
            }
            ctx.stroke()
        }
        Connections {
            target: root
            function onKeysChanged() { line.requestPaint() }
            function onStaticGainChanged() { line.requestPaint() }
            function onPxPerSecondChanged() { line.requestPaint() }
            function onHeightChanged() { line.requestPaint() }
            function onWidthChanged() { line.requestPaint() }
            function onDraggingChanged() { line.requestPaint() }
        }
    }

    // The line itself: a band a few px either side of it takes the pointer, the rest of the clip
    // keeps its own gestures (move, trim).
    MouseArea {
        id: lineMouse
        anchors.fill: parent
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton
        preventStealing: true
        property bool onLine: false
        property real pressY: 0
        // The keys the drag moves (indices into root.keys) and their levels at the press.
        property var moving: []
        property var baseGains: []
        cursorShape: onLine ? (EditorState.keyboardModifiers() & Qt.ControlModifier ? Qt.CrossCursor
                                                                                      : Qt.SizeVerCursor)
                            : Qt.ArrowCursor
        onPositionChanged: (mouse) => {
            if (!pressed) {
                onLine = Math.abs(mouse.y - root.yOf(root.gainAtX(mouse.x))) <= 5
                return
            }
            const dy = mouse.y - pressY
            const dDb = -dy / Math.max(1, root.height) * (root.maxDb - root.minDb)
            if (moving.length === 0) {
                // No keys: the clip's level.
                const g = Math.min(2, root.gainOf(root.dbOf(baseGains[0]) + dDb))
                EditorState.previewSetClipKeyframe(root.trackIndex, root.clipIndex, "volume",
                                                   root.clipStart, g)
                root.staticGain = g
                return
            }
            const next = root.keys.slice()
            for (let i = 0; i < moving.length; ++i) {
                const k = next[moving[i]]
                const g = Math.min(2, root.gainOf(root.dbOf(baseGains[i]) + dDb))
                EditorState.previewMoveClipKeyframe(root.trackIndex, root.clipIndex, "volume",
                                                    k.seconds, k.seconds, g)
                next[moving[i]] = { seconds: k.seconds, value: g }
            }
            root.keys = next
        }
        onPressed: (mouse) => {
            onLine = Math.abs(mouse.y - root.yOf(root.gainAtX(mouse.x))) <= 5
            if (!onLine) {
                mouse.accepted = false
                return
            }
            if (mouse.modifiers & Qt.ControlModifier) {
                // A key on the line where it was clicked, at the level it shows there.
                const at = EditorState.snapTime(root.clipStart + mouse.x / root.pxPerSecond)
                EditorState.addClipKeyframeAt(root.trackIndex, root.clipIndex, "volume", at)
                mouse.accepted = false
                return
            }
            pressY = mouse.y
            // The stretch under the pointer: the keys either side of it (all of the level when
            // there are none).
            const s = root.clipStart + mouse.x / root.pxPerSecond
            const idx = []
            if (root.animated) {
                let before = -1
                let after = -1
                for (let i = 0; i < root.keys.length; ++i) {
                    if (root.keys[i].seconds <= s)
                        before = i
                    else if (after < 0)
                        after = i
                }
                if (before >= 0)
                    idx.push(before)
                if (after >= 0)
                    idx.push(after)
            } else if (root.keys.length === 1) {
                idx.push(0)
            }
            moving = idx
            baseGains = idx.length > 0 ? idx.map((i) => root.keys[i].value) : [root.staticGain]
            root.dragging = true
            EditorState.beginPreviewDrag(qsTr("Adjust volume"))
        }
        onReleased: {
            if (!root.dragging)
                return
            EditorState.commitPreviewDrag()
            root.dragging = false
        }
        onCanceled: {
            if (!root.dragging)
                return
            EditorState.commitPreviewDrag()
            root.dragging = false
        }
    }

    // The keys' dots, dragged in time (between their neighbours, inside the clip) and level.
    Repeater {
        model: root.animated ? root.keys : []
        delegate: Rectangle {
            id: dot
            required property var modelData
            required property int index
            width: 9
            height: 9
            radius: 4.5
            x: root.xOf(modelData.seconds) - width / 2
            y: root.yOf(modelData.value) - height / 2
            color: dotMouse.containsMouse || dotMouse.pressed ? Theme.primary : Theme.panelBackground
            border.width: 1.5
            border.color: Theme.primary

            MouseArea {
                id: dotMouse
                anchors.fill: parent
                anchors.margins: -4
                hoverEnabled: true
                preventStealing: true
                cursorShape: Qt.SizeAllCursor
                property real pressX: 0
                property real pressY: 0
                property real fromSeconds: 0
                property real baseGain: 1
                onPressed: (mouse) => {
                    const p = mapToItem(root, mouse.x, mouse.y)
                    pressX = p.x
                    pressY = p.y
                    fromSeconds = dot.modelData.seconds
                    baseGain = dot.modelData.value
                    root.dragging = true
                    EditorState.beginPreviewDrag(qsTr("Move keyframe"))
                }
                onPositionChanged: (mouse) => {
                    if (!pressed)
                        return
                    const p = mapToItem(root, mouse.x, mouse.y)
                    const ks = root.keys
                    const frame = 1 / 60
                    const lo = dot.index > 0 ? ks[dot.index - 1].seconds + frame : root.clipStart
                    const hi = dot.index < ks.length - 1 ? ks[dot.index + 1].seconds - frame
                                                         : root.clipStart + root.width / root.pxPerSecond
                    const keepTime = (mouse.modifiers & Qt.ShiftModifier) !== 0
                    const base = ks[dot.index]
                    const at = keepTime ? base.seconds
                        : Math.max(lo, Math.min(hi, EditorState.snapTime(base.seconds
                              + (p.x - pressX) / root.pxPerSecond - (base.seconds - fromSeconds))))
                    const dDb = -(p.y - pressY) / Math.max(1, root.height) * (root.maxDb - root.minDb)
                    const g = Math.min(2, root.gainOf(root.dbOf(baseGain) + dDb))
                    EditorState.previewMoveClipKeyframe(root.trackIndex, root.clipIndex, "volume",
                                                        base.seconds, at, g)
                    const next = ks.slice()
                    next[dot.index] = { seconds: at, value: g }
                    root.keys = next
                }
                onReleased: {
                    EditorState.commitPreviewDrag()
                    root.dragging = false
                }
                onCanceled: {
                    EditorState.commitPreviewDrag()
                    root.dragging = false
                }
                onDoubleClicked: {
                    const at = dot.modelData.seconds
                    EditorState.removeClipKeyframe(root.trackIndex, root.clipIndex, "volume", at)
                }
            }

            ThemedToolTip {
                visible: dotMouse.containsMouse && !dotMouse.pressed
                text: root.dbOf(dot.modelData.value).toFixed(1) + " dB · "
                      + qsTr("double-click to remove")
            }
        }
    }

    ThemedToolTip {
        visible: lineMouse.onLine && lineMouse.containsMouse && !root.dragging
        text: root.dbOf(root.gainAtX(lineMouse.mouseX)).toFixed(1) + " dB · "
              + qsTr("drag to change the volume, Ctrl+click to add a keyframe")
    }
}
