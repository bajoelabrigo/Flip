import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// Motion Tools › Trim (0.26, Jorge: as the Trim-Pack script): one click animates the Trim Paths of
// the selected shapes, and the strokes of the selected texts (every letter at once, as After
// Effects' "Simultaneously"). The buttons are Trim-Pack's — In, Out, I&O, Mid-in, Mid-out,
// Equal-in, Equal-out — each drawing what it does; its settings are here (frames, offset range,
// copies) and its Alt and Shift keys are the two switches (reverse, offset).
Column {
    id: root

    property int frames: 20
    property real offsetRange: 180
    property int copies: 4
    property bool reverse: false
    property bool animateOffset: false

    function run(mode) {
        EditorState.applyTrimPack(mode, root.frames, root.offsetRange, root.copies, root.reverse, root.animateOffset)
    }

    spacing: Theme.spacingMd

    ThemedLabel {
        width: parent.width
        wrapMode: Text.WordWrap
        size: "sm"
        opacity: 0.8
        text: qsTr("Select shapes or texts with a stroke. The keys start at the playhead; I&O ends with the clip. For Trace, pick the layers that ride the line first and the line last (with none, a dot rides it).")
    }

    // A Trim-Pack button: its icon is a ring with the part that the animation draws.
    component TrimButton: Rectangle {
        id: tb
        property string mode: ""
        property string label: ""
        property string tip: ""
        // "in", "out", "io", "midIn", "midOut", "equalIn", "equalOut", "gap", "swap", "copies",
        // "traceIn", "traceOut", "traceIo", "clear"
        property string icon: ""
        property color tint: "#ffd23f"
        signal activated()
        width: (root.width - 3 * Theme.spacingSm) / 4
        height: 62
        radius: Theme.radiusSm
        color: area.pressed ? Theme.panelMuted : (area.containsMouse ? Theme.panelAccent : Theme.panelBackground)
        border.width: Theme.borderWidth
        border.color: area.containsMouse ? tb.tint : Theme.panelBorder
        Canvas {
            id: glyph
            width: 34
            height: 34
            anchors.top: parent.top
            anchors.topMargin: 5
            anchors.horizontalCenter: parent.horizontalCenter
            onPaint: {
                const ctx = getContext("2d")
                ctx.reset()
                const cx = width / 2, cy = height / 2, r = 12
                const top = -Math.PI / 2
                const arc = (a0, a1, color, w) => {
                    ctx.beginPath()
                    ctx.strokeStyle = color
                    ctx.lineWidth = w
                    ctx.lineCap = "butt"
                    ctx.arc(cx, cy, r, top + a0 * 2 * Math.PI, top + a1 * 2 * Math.PI, false)
                    ctx.stroke()
                }
                const ghost = Qt.rgba(1, 1, 1, 0.14)
                arc(0, 1, ghost, 3)
                const c = tb.tint
                switch (tb.icon) {
                case "in": arc(0, 0.62, c, 4); break
                case "out": arc(0.38, 1, c, 4); break
                case "io": arc(0.2, 0.7, c, 4); break
                case "midIn": arc(-0.28, 0.28, c, 4); break
                case "midOut": arc(0.22, 0.4, c, 4); arc(0.6, 0.78, c, 4); break
                case "equalIn": for (let i = 0; i < 4; ++i) arc(i / 4, i / 4 + 0.1, c, 4); break
                case "equalOut": for (let i = 0; i < 4; ++i) arc(i / 4 + 0.12, i / 4 + 0.25, c, 4); break
                case "gap": arc(0.1, 0.94, c, 4); break
                case "traceIn": arc(0, 0.45, c, 4); arc(0.5, 0.62, "#ffffff", 4); break
                case "traceOut": arc(0.55, 1, c, 4); arc(0.38, 0.5, "#ffffff", 4); break
                case "traceIo": arc(0.2, 0.6, c, 4); arc(0.66, 0.76, "#ffffff", 4); break
                case "copies":
                    arc(0, 0.55, c, 4)
                    ctx.globalAlpha = 0.5
                    arc(0, 0.35, c, 4)
                    ctx.globalAlpha = 1
                    break
                case "swap":
                    ctx.strokeStyle = c
                    ctx.fillStyle = c
                    ctx.lineWidth = 3
                    ctx.beginPath(); ctx.moveTo(6, 12); ctx.lineTo(26, 12); ctx.stroke()
                    ctx.beginPath(); ctx.moveTo(28, 22); ctx.lineTo(8, 22); ctx.stroke()
                    ctx.beginPath(); ctx.moveTo(4, 22); ctx.lineTo(10, 17); ctx.lineTo(10, 27); ctx.fill()
                    break
                case "hline":
                case "vline":
                    ctx.strokeStyle = c
                    ctx.lineWidth = 3
                    ctx.beginPath()
                    for (let i = 0; i < 3; ++i) {
                        if (tb.icon === "hline") { ctx.moveTo(8, 11 + i * 6); ctx.lineTo(26, 11 + i * 6) }
                        else { ctx.moveTo(11 + i * 6, 8); ctx.lineTo(11 + i * 6, 26) }
                    }
                    ctx.stroke()
                    break
                case "clear":
                    ctx.strokeStyle = c
                    ctx.lineWidth = 3
                    ctx.beginPath(); ctx.moveTo(10, 10); ctx.lineTo(24, 24); ctx.moveTo(24, 10); ctx.lineTo(10, 24)
                    ctx.stroke()
                    break
                }
            }
        }
        Text {
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 5
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 4
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
            text: tb.label
            color: tb.tint
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
            font.weight: Font.DemiBold
        }
        MouseArea {
            id: area
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: tb.mode.length > 0 ? root.run(tb.mode) : tb.activated()
        }
        ThemedToolTip { visible: area.containsMouse && tb.tip.length > 0; text: tb.tip }
    }

    Flow {
        width: parent.width
        spacing: Theme.spacingSm
        TrimButton { mode: "in"; icon: "in"; label: qsTr("In"); tip: qsTr("The line draws on from its start") }
        TrimButton { mode: "out"; icon: "out"; label: qsTr("Out"); tip: qsTr("The line draws off from its start") }
        TrimButton { mode: "inout"; icon: "io"; label: qsTr("I&O"); tip: qsTr("Draws on from the playhead and off at the end of the clip") }
        TrimButton { mode: "reversePath"; icon: "swap"; label: qsTr("Reverse"); tip: qsTr("Reverse path direction: the trim runs round the other way") }
        TrimButton { mode: "midIn"; icon: "midIn"; tint: "#8ddc5a"; label: qsTr("Mid-in"); tip: qsTr("Grows both ways from the middle (reversed: in from both ends)") }
        TrimButton { mode: "midOut"; icon: "midOut"; tint: "#8ddc5a"; label: qsTr("Mid-out"); tip: qsTr("Shrinks into the middle (reversed: off towards both ends)") }
        TrimButton { mode: "divideIn"; icon: "equalIn"; tint: "#3fb6f0"; label: qsTr("Divide-in"); tip: qsTr("The path in equal parts (as many as Copies) that draw on at once") }
        TrimButton { mode: "divideOut"; icon: "equalOut"; tint: "#3fb6f0"; label: qsTr("Divide-out"); tip: qsTr("The path in equal parts (as many as Copies) that draw off at once") }
        TrimButton { mode: "gapLoop"; icon: "gap"; tint: "#ffffff"; label: qsTr("Running gap"); tip: qsTr("A small gap runs round each outline all the clip long, as an outlined title") }
        TrimButton { mode: "copies"; icon: "copies"; tint: "#c58cf5"; label: qsTr("Copies"); tip: qsTr("Copies above, each one drawing on a little later") }
        TrimButton { mode: "traceIn"; icon: "traceIn"; tint: "#ff9b54"; label: qsTr("Trace In"); tip: qsTr("Draws on with another layer riding its end") }
        TrimButton { mode: "traceOut"; icon: "traceOut"; tint: "#ff9b54"; label: qsTr("Trace Out"); tip: qsTr("Draws off with another layer riding its end") }
        TrimButton { mode: "traceInOut"; icon: "traceIo"; tint: "#ff9b54"; label: qsTr("Trace I&O"); tip: qsTr("A layer on each end, in and out") }
        TrimButton { mode: "midTraceIn"; icon: "midIn"; tint: "#2ee6c0"; label: qsTr("MidTrace In"); tip: qsTr("Grows from the middle with a layer on each end") }
        TrimButton { mode: "midTraceOut"; icon: "midOut"; tint: "#2ee6c0"; label: qsTr("MidTrace Out"); tip: qsTr("Shrinks into the middle with a layer on each end") }
        TrimButton { mode: "addHLine"; icon: "hline"; tint: "#c58cf5"; label: qsTr("Add line"); tip: qsTr("Add a horizontal line to trim") }
        TrimButton { mode: "addVLine"; icon: "vline"; tint: "#c58cf5"; label: qsTr("Add line"); tip: qsTr("Add a vertical line to trim") }
        TrimButton {
            icon: "copies"
            tint: "#f06ab4"
            label: qsTr("Convert")
            tip: qsTr("A text or shape into an editable path, so it can be trimmed letter by letter")
            onActivated: EditorState.convertSelectionToShape()
        }
        TrimButton { mode: "clear"; icon: "clear"; tint: "#9aa0a6"; label: qsTr("Clear"); tip: qsTr("Take the Trim Paths animation off") }
    }

    // Trim-Pack's settings.
    Grid {
        width: parent.width
        columns: 3
        columnSpacing: Theme.spacingSm
        rowSpacing: 2
        ThemedLabel { text: qsTr("Frames") }
        ThemedLabel { text: qsTr("Offset range") }
        ThemedLabel { text: qsTr("Copies") }
        ThemedNumberField {
            width: (root.width - 2 * Theme.spacingSm) / 3
            from: 1; to: 600; step: 1
            value: root.frames
            onEdited: v => root.frames = Math.round(v)
        }
        ThemedNumberField {
            width: (root.width - 2 * Theme.spacingSm) / 3
            from: -3600; to: 3600; step: 15; unit: "°"
            value: root.offsetRange
            onEdited: v => root.offsetRange = v
        }
        ThemedNumberField {
            width: (root.width - 2 * Theme.spacingSm) / 3
            from: 1; to: 12; step: 1
            value: root.copies
            onEdited: v => root.copies = Math.round(v)
        }
    }

    ThemedSwitch {
        width: parent.width
        text: qsTr("Reverse (Alt)")
        tooltip: qsTr("Draw from the other end of the path")
        checked: root.reverse
        onToggled: root.reverse = checked
    }
    ThemedSwitch {
        width: parent.width
        text: qsTr("Offset (Shift)")
        tooltip: qsTr("The line also travels round the path by the offset range")
        checked: root.animateOffset
        onToggled: root.animateOffset = checked
    }
}
