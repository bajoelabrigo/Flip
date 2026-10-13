import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// CapCut's Adjust panel for a picture clip, in its five pages: Basic (light and colour sliders),
// HSL (hue, saturation and lightness per colour), Curves (luma, red, green, blue), Color wheels
// (shadows, midtones, highlights, offset) and Mask. Each of the first four edits one effect of the
// colour category (effects/color_*), added to the clip the first time a control moves, so the
// Effects tab shows the same effect and an untouched page costs nothing.
Item {
    id: root

    property string page: "basic"

    readonly property var pages: [
        { id: "basic", label: qsTr("Basic") },
        { id: "hsl", label: qsTr("HSL") },
        { id: "curves", label: qsTr("Curves") },
        { id: "wheels", label: qsTr("Color wheels") },
        { id: "lut", label: qsTr("LUT") },
        { id: "mask", label: qsTr("Mask") }
    ]
    readonly property int pageIndex: Math.max(0, pages.findIndex(p => p.id === root.page))

    // The clip's effect stack (on the clip's own adjustment when it has one: AppController
    // redirects reads and writes there).
    readonly property var effects: EditorState.selectedClipEffects || []

    function effectIndex(effectId) {
        for (let i = effects.length - 1; i >= 0; i--) {
            if (effects[i].catalogId === effectId)
                return i
        }
        return -1
    }

    function value(effectId, key, fallback) {
        const i = effectIndex(effectId)
        if (i < 0)
            return fallback
        const params = effects[i].params || []
        for (let j = 0; j < params.length; j++) {
            if (params[j].key === key)
                return Number(params[j].value)
        }
        return fallback
    }

    // A control is being moved: make sure the effect exists, open one undo step for the gesture.
    // addEffect moves the selection to whatever hosts the stack, so the index is read after it.
    property int editIndex: -1
    function beginEdit(effectId, undoText) {
        if (effectIndex(effectId) < 0)
            EditorState.addEffect(EditorState.selectedTrack, EditorState.selectedClip, effectId)
        editIndex = effectIndex(effectId)
        if (editIndex >= 0)
            EditorState.beginPreviewDrag(undoText)
    }
    function preview(key, v) {
        if (editIndex >= 0)
            EditorState.previewSetEffectParam(EditorState.selectedTrack, EditorState.selectedClip,
                                              editIndex, key, v)
    }
    function endEdit() {
        if (editIndex >= 0)
            EditorState.commitPreviewDrag()
        editIndex = -1
    }
    // Several keys in one undo step (the reset buttons). Nothing to reset without the effect.
    function setMany(effectId, undoText, values) {
        if (effectIndex(effectId) < 0)
            return
        setManyOrAdd(effectId, undoText, values)
    }
    // The same, adding the effect first when it is not there yet (a typed value).
    function setManyOrAdd(effectId, undoText, values) {
        beginEdit(effectId, undoText)
        for (const k in values)
            preview(k, values[k])
        endEdit()
    }

    readonly property bool canEdit: {
        const d = EditorState.selectedClipData
        return !!d && (d.caps || []).indexOf("adj:videoEffects") >= 0
    }

    height: contentCol.height
    implicitHeight: contentCol.height

    function refreshFields() {}

    // One slider row bound to an effect parameter: label, value, slider, double-click to reset.
    component ParamSlider: Column {
        id: ps
        // Inline components cannot see this file's ids: the inspector is handed in.
        property var host: null
        property string effectId
        property string key
        property string label
        property real from: -1
        property real to: 1
        property real defaultValue: 0
        // Shown as -100..100 (or 0..100) like CapCut, whatever the shader's range.
        property real displayScale: 100
        readonly property real current: host ? host.value(effectId, key, defaultValue) : defaultValue

        width: parent ? parent.width : 0
        spacing: 2
        enabled: !!host && host.canEdit

        Row {
            width: parent.width
            Text {
                width: parent.width - 48
                text: ps.label
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
                elide: Text.ElideRight
            }
            // The number can be typed too: Enter applies it (clamped to the range) as one step.
            TextInput {
                id: typed
                width: 48
                horizontalAlignment: Text.AlignRight
                text: Math.round(slider.value * ps.displayScale)
                color: Theme.panelForeground
                font.family: Theme.monoFontFamily
                font.pixelSize: Theme.fontSizeXs
                selectByMouse: true
                validator: IntValidator {
                    bottom: Math.round(ps.from * ps.displayScale)
                    top: Math.round(ps.to * ps.displayScale)
                }
                onAccepted: {
                    const v = Math.max(ps.from, Math.min(ps.to, Number(text) / ps.displayScale))
                    ps.host.setManyOrAdd(ps.effectId, qsTr("Adjust %1").arg(ps.label), ({ [ps.key]: v }))
                    focus = false
                }
            }
        }
        ThemedSlider {
            id: slider
            width: parent.width
            label: ps.label
            from: ps.from
            to: ps.to
            Binding on value {
                when: !slider.pressed
                value: ps.current
            }
            onMoved: ps.host.preview(ps.key, value)
            onPressedChanged: {
                if (pressed)
                    ps.host.beginEdit(ps.effectId, qsTr("Adjust %1").arg(ps.label))
                else
                    ps.host.endEdit()
            }
            TapHandler {
                acceptedButtons: Qt.LeftButton
                onDoubleTapped: ps.host.setMany(ps.effectId, qsTr("Reset %1").arg(ps.label),
                                             ({ [ps.key]: ps.defaultValue }))
            }
        }
    }

    component SectionTitle: Text {
        color: Theme.foreground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeSm
        font.weight: Font.Medium
    }

    component ResetButton: ThemedButton {
        text: qsTr("Reset")
        variant: "ghost"
    }

    Column {
        id: contentCol
        width: root.width
        spacing: Theme.spacingXl

        // The page strip, drawn like the Video tab's.
        Rectangle {
            width: parent.width
            height: strip.height + 6
            radius: Theme.radiusSm
            color: Theme.panelAccent

            Row {
                id: strip
                anchors.centerIn: parent
                width: parent.width - 6
                spacing: 2

                // Every cell as tall as the tallest label, so "Círculo cromático" wraps to two
                // lines instead of turning into "Círculo cr…".
                // One font size for every label: the largest at which the longest single word
                // ("cromático") still fits its cell, since a word cannot wrap.
                property real cellHeight: 0
                property real labelPx: Theme.fontSizeXs
                onWidthChanged: Qt.callLater(measure)
                Component.onCompleted: Qt.callLater(measure)
                function measure() {
                    const room = (width - 8) / root.pages.length - 4
                    let px = Theme.fontSizeXs
                    for (const page of root.pages) {
                        for (const word of String(page.label).split(" ")) {
                            wordMetrics.text = word
                            if (room > 0 && wordMetrics.advanceWidth > room)
                                px = Math.min(px, Math.floor(Theme.fontSizeXs * room / wordMetrics.advanceWidth))
                        }
                    }
                    labelPx = Math.max(8, px)
                    let h = 0
                    for (let i = 0; i < stripCells.count; i++) {
                        const c = stripCells.itemAt(i)
                        if (c)
                            h = Math.max(h, c.labelHeight)
                    }
                    cellHeight = h + 14
                }

                TextMetrics {
                    id: wordMetrics
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                    font.weight: Font.Medium
                }

                Repeater {
                    id: stripCells
                    model: root.pages
                    delegate: Rectangle {
                        id: cell
                        required property var modelData
                        required property int index
                        readonly property real labelHeight: cellLabel.implicitHeight
                        onLabelHeightChanged: Qt.callLater(strip.measure)
                        width: (strip.width - 8) / root.pages.length
                        height: strip.cellHeight
                        radius: Theme.radiusSm
                        color: index === root.pageIndex ? Theme.popoverHover : "transparent"

                        Text {
                            id: cellLabel
                            anchors.centerIn: parent
                            width: parent.width - 4
                            horizontalAlignment: Text.AlignHCenter
                            wrapMode: Text.WordWrap
                            maximumLineCount: 2
                            elide: Text.ElideRight
                            text: cell.modelData.label
                            color: cell.index === root.pageIndex ? Theme.foreground : Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: strip.labelPx
                            font.weight: cell.index === root.pageIndex ? Font.Medium : Font.Normal
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: root.page = cell.modelData.id
                        }
                    }
                }
            }
        }

        Text {
            visible: !root.canEdit
            width: parent.width
            wrapMode: Text.WordWrap
            text: qsTr("Select a video or image clip to adjust its colour.")
            color: Theme.warning
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }

        // --- Basic ---------------------------------------------------------------------------
        Column {
            visible: root.page === "basic"
            width: parent.width
            spacing: Theme.spacingMd

            readonly property var light: [
                { key: "exposure", label: qsTr("Exposure") },
                { key: "brightness", label: qsTr("Brightness") },
                { key: "contrast", label: qsTr("Contrast") },
                { key: "highlights", label: qsTr("Highlights") },
                { key: "shadows", label: qsTr("Shadows") },
                { key: "whites", label: qsTr("Whites") },
                { key: "blacks", label: qsTr("Blacks") }
            ]
            // Fade only goes one way (0 = none), like CapCut's.
            readonly property var colour: [
                { key: "saturation", label: qsTr("Saturation") },
                { key: "vibrance", label: qsTr("Vibrance") },
                { key: "temperature", label: qsTr("Temperature") },
                { key: "tint", label: qsTr("Tint") },
                { key: "fade", label: qsTr("Fade"), from: 0 }
            ]

            Row {
                width: parent.width
                SectionTitle { text: qsTr("Light"); width: parent.width - lightReset.width }
                ResetButton {
                    id: lightReset
                    onClicked: root.setMany("color.basic", qsTr("Reset light"), ({
                        exposure: 0, brightness: 0, contrast: 0, highlights: 0, shadows: 0,
                        whites: 0, blacks: 0 }))
                }
            }
            Repeater {
                model: parent.light
                delegate: ParamSlider {
                    host: root
                    required property var modelData
                    effectId: "color.basic"
                    key: modelData.key
                    label: modelData.label
                }
            }
            Row {
                width: parent.width
                topPadding: Theme.spacingSm
                SectionTitle { text: qsTr("Colour"); width: parent.width - colourReset.width }
                ResetButton {
                    id: colourReset
                    onClicked: root.setMany("color.basic", qsTr("Reset colour"), ({
                        saturation: 0, vibrance: 0, temperature: 0, tint: 0, fade: 0 }))
                }
            }
            Repeater {
                model: parent.colour
                delegate: ParamSlider {
                    host: root
                    required property var modelData
                    effectId: "color.basic"
                    key: modelData.key
                    label: modelData.label
                    from: modelData.from !== undefined ? modelData.from : -1
                }
            }
        }

        // --- HSL -----------------------------------------------------------------------------
        Column {
            id: hslPage
            visible: root.page === "hsl"
            width: parent.width
            spacing: Theme.spacingMd

            property string band: "red"
            readonly property var bands: [
                { id: "red", label: qsTr("Red"), color: "#e5484d" },
                { id: "orange", label: qsTr("Orange"), color: "#f2994a" },
                { id: "yellow", label: qsTr("Yellow"), color: "#f2d64b" },
                { id: "green", label: qsTr("Green"), color: "#46c26a" },
                { id: "aqua", label: qsTr("Aqua"), color: "#3fd0d4" },
                { id: "blue", label: qsTr("Blue"), color: "#3d7be0" },
                { id: "purple", label: qsTr("Purple"), color: "#8e55e0" },
                { id: "magenta", label: qsTr("Magenta"), color: "#d94fd1" }
            ]

            Row {
                width: parent.width
                SectionTitle { text: qsTr("Colour to change"); width: parent.width - hslReset.width }
                ResetButton {
                    id: hslReset
                    onClicked: {
                        const v = {}
                        for (const b of hslPage.bands) { v[b.id + "Hue"] = 0; v[b.id + "Sat"] = 0; v[b.id + "Lum"] = 0 }
                        root.setMany("color.hsl", qsTr("Reset HSL"), v)
                    }
                }
            }

            Row {
                id: swatches
                width: parent.width
                spacing: (width - 8 * 26) / 7

                Repeater {
                    model: hslPage.bands
                    delegate: Rectangle {
                        id: swatch
                        required property var modelData
                        readonly property bool current: hslPage.band === modelData.id
                        width: 26
                        height: 26
                        radius: 13
                        color: current ? modelData.color : "transparent"
                        border.width: 3
                        border.color: modelData.color

                        Rectangle {
                            visible: swatch.current
                            anchors.centerIn: parent
                            width: 32
                            height: 32
                            radius: 16
                            color: "transparent"
                            border.width: 1
                            border.color: Theme.foreground
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: hslPage.band = swatch.modelData.id
                        }
                        ThemedToolTip {
                            text: swatch.modelData.label
                            visible: swatchHover.hovered
                        }
                        HoverHandler { id: swatchHover }
                    }
                }
            }

            ParamSlider { host: root; effectId: "color.hsl"; key: hslPage.band + "Hue"; label: qsTr("Hue") }
            ParamSlider { host: root; effectId: "color.hsl"; key: hslPage.band + "Sat"; label: qsTr("Saturation") }
            ParamSlider { host: root; effectId: "color.hsl"; key: hslPage.band + "Lum"; label: qsTr("Lightness") }
        }

        // --- Curves --------------------------------------------------------------------------
        Column {
            id: curvesPage
            visible: root.page === "curves"
            width: parent.width
            spacing: Theme.spacingMd

            property string channel: "l"
            readonly property var channels: [
                { id: "l", label: qsTr("Luma"), color: "#ffffff" },
                { id: "r", label: qsTr("Red"), color: "#e5484d" },
                { id: "g", label: qsTr("Green"), color: "#46c26a" },
                { id: "b", label: qsTr("Blue"), color: "#3d7be0" }
            ]
            readonly property var channelInfo: channels.find(c => c.id === channel)
            // The five points of the open channel (x = 0, .25, .5, .75, 1).
            readonly property var points: [0, 1, 2, 3, 4].map(i => root.value("color.curves", channel + i, i / 4))
            // While a point is dragged its live value, so the drawing follows the pointer.
            property int dragIndex: -1
            property real dragValue: 0
            function pointAt(i) { return i === dragIndex ? dragValue : points[i] }

            // Same curve as the shader: Catmull-Rom with tangents limited to the segment.
            function curveAt(x) {
                const p = [0, 1, 2, 3, 4].map(i => pointAt(i))
                x = Math.max(0, Math.min(1, x))
                const seg = Math.min(Math.floor(x * 4), 3)
                const t = x * 4 - seg
                const y0 = p[seg], y1 = p[seg + 1]
                let m0 = seg > 0 ? (p[seg + 1] - p[seg - 1]) * 0.5 : (y1 - y0)
                let m1 = seg < 3 ? (p[seg + 2] - p[seg]) * 0.5 : (y1 - y0)
                const lim = Math.abs(y1 - y0) * 3
                m0 = Math.max(-lim, Math.min(lim, m0))
                m1 = Math.max(-lim, Math.min(lim, m1))
                const t2 = t * t, t3 = t2 * t
                return Math.max(0, Math.min(1, (2 * t3 - 3 * t2 + 1) * y0 + (t3 - 2 * t2 + t) * m0
                                               + (-2 * t3 + 3 * t2) * y1 + (t3 - t2) * m1))
            }

            Row {
                width: parent.width
                spacing: Theme.spacingSm

                Repeater {
                    model: curvesPage.channels
                    delegate: ThemedChip {
                        required property var modelData
                        text: modelData.label
                        variant: "outline"
                        selected: curvesPage.channel === modelData.id
                        onClicked: curvesPage.channel = modelData.id
                    }
                }
                Item { width: 1; height: 1 }
            }

            Rectangle {
                id: graph
                width: parent.width
                height: width
                color: "#0b0b0d"
                border.width: 1
                border.color: Theme.panelBorder
                radius: Theme.radiusSm

                readonly property real pad: 10
                readonly property real span: width - pad * 2
                function px(x) { return pad + x * span }
                function py(y) { return pad + (1 - y) * span }

                Canvas {
                    id: curveCanvas
                    anchors.fill: parent
                    onPaint: {
                        const ctx = getContext("2d")
                        ctx.reset()
                        ctx.strokeStyle = "rgba(255,255,255,0.08)"
                        ctx.lineWidth = 1
                        for (let i = 1; i < 4; i++) {
                            ctx.beginPath(); ctx.moveTo(graph.px(i / 4), graph.py(0)); ctx.lineTo(graph.px(i / 4), graph.py(1)); ctx.stroke()
                            ctx.beginPath(); ctx.moveTo(graph.px(0), graph.py(i / 4)); ctx.lineTo(graph.px(1), graph.py(i / 4)); ctx.stroke()
                        }
                        ctx.strokeStyle = "rgba(255,255,255,0.18)"
                        ctx.beginPath(); ctx.moveTo(graph.px(0), graph.py(0)); ctx.lineTo(graph.px(1), graph.py(1)); ctx.stroke()
                        ctx.strokeStyle = curvesPage.channelInfo.color
                        ctx.lineWidth = 2
                        ctx.beginPath()
                        for (let s = 0; s <= 64; s++) {
                            const x = s / 64
                            if (s === 0) ctx.moveTo(graph.px(x), graph.py(curvesPage.curveAt(x)))
                            else ctx.lineTo(graph.px(x), graph.py(curvesPage.curveAt(x)))
                        }
                        ctx.stroke()
                    }
                    Connections {
                        target: curvesPage
                        function onPointsChanged() { curveCanvas.requestPaint() }
                        function onDragValueChanged() { curveCanvas.requestPaint() }
                        function onChannelChanged() { curveCanvas.requestPaint() }
                    }
                }

                // The five handles; each moves up and down only, at its fixed x.
                Repeater {
                    model: 5
                    delegate: Rectangle {
                        id: handle
                        required property int index
                        width: 14
                        height: 14
                        radius: 7
                        x: graph.px(index / 4) - width / 2
                        y: graph.py(curvesPage.pointAt(index)) - height / 2
                        color: area.pressed ? curvesPage.channelInfo.color : "#0b0b0d"
                        border.width: 2
                        border.color: curvesPage.channelInfo.color
                        enabled: root.canEdit

                        MouseArea {
                            id: area
                            anchors.fill: parent
                            anchors.margins: -6
                            cursorShape: Qt.SizeVerCursor
                            preventStealing: true
                            onPressed: {
                                curvesPage.dragValue = curvesPage.points[handle.index]
                                curvesPage.dragIndex = handle.index
                                root.beginEdit("color.curves", qsTr("Edit curve"))
                            }
                            onPositionChanged: (mouse) => {
                                const p = mapToItem(graph, mouse.x, mouse.y)
                                const v = Math.max(0, Math.min(1, 1 - (p.y - graph.pad) / graph.span))
                                curvesPage.dragValue = v
                                root.preview(curvesPage.channel + handle.index, v)
                            }
                            onReleased: {
                                root.endEdit()
                                curvesPage.dragIndex = -1
                            }
                            onDoubleClicked: root.setMany("color.curves", qsTr("Reset curve point"),
                                                          ({ [curvesPage.channel + handle.index]: handle.index / 4 }))
                        }
                    }
                }
            }

            Row {
                spacing: Theme.spacingSm
                ResetButton {
                    text: qsTr("Reset %1").arg(curvesPage.channelInfo.label)
                    onClicked: {
                        const v = {}
                        for (let i = 0; i < 5; i++) v[curvesPage.channel + i] = i / 4
                        root.setMany("color.curves", qsTr("Reset curve"), v)
                    }
                }
                ResetButton {
                    text: qsTr("Reset all")
                    onClicked: {
                        const v = {}
                        for (const c of curvesPage.channels)
                            for (let i = 0; i < 5; i++) v[c.id + i] = i / 4
                        root.setMany("color.curves", qsTr("Reset curves"), v)
                    }
                }
            }

            Text {
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("Drag a point up to brighten that part of the image, down to darken it. Double-click a point to put it back.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
        }

        // --- Color wheels --------------------------------------------------------------------
        Column {
            id: wheelsPage
            visible: root.page === "wheels"
            width: parent.width
            spacing: Theme.spacingMd

            readonly property var wheels: [
                { id: "shadows", label: qsTr("Shadows") },
                { id: "midtones", label: qsTr("Midtones") },
                { id: "highlights", label: qsTr("Highlights") },
                { id: "offset", label: qsTr("Offset") }
            ]

            ParamSlider {
                host: root
                effectId: "color.wheels"
                key: "intensity"
                label: qsTr("Intensity")
                from: 0
                to: 1
                defaultValue: 1
            }

            Grid {
                id: wheelGrid
                width: parent.width
                columns: 2
                columnSpacing: Theme.spacingLg
                rowSpacing: Theme.spacingLg
                readonly property real cell: (width - columnSpacing) / 2

                Repeater {
                    model: wheelsPage.wheels
                    delegate: Column {
                        id: wheelCell
                        required property var modelData
                        width: wheelGrid.cell
                        spacing: 4

                        readonly property real rv: root.value("color.wheels", modelData.id + "R", 0)
                        readonly property real gv: root.value("color.wheels", modelData.id + "G", 0)
                        readonly property real bv: root.value("color.wheels", modelData.id + "B", 0)
                        // The three channels as a point on the wheel: red at 0°, green at 120°,
                        // blue at 240°, distance from the centre = how strong the tint is.
                        property bool dragging: false
                        property real dx: 0
                        property real dy: 0
                        readonly property real ptX: dragging ? dx : (2 * rv - gv - bv) / 3
                        readonly property real ptY: dragging ? dy : (gv - bv) / Math.sqrt(3)

                        function channels(x, y) {
                            return [x, -x / 2 + y * Math.sqrt(3) / 2, -x / 2 - y * Math.sqrt(3) / 2]
                        }

                        Row {
                            width: parent.width
                            Text {
                                width: parent.width - wheelReset.width
                                text: wheelCell.modelData.label
                                color: Theme.foreground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeXs
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            IconButton {
                                id: wheelReset
                                glyph: Theme.icons.reset
                                variant: "ghost"
                                buttonSize: 22
                                iconSize: 12
                                tooltip: qsTr("Reset")
                                onClicked: root.setMany("color.wheels", qsTr("Reset %1").arg(wheelCell.modelData.label), ({
                                    [wheelCell.modelData.id + "R"]: 0, [wheelCell.modelData.id + "G"]: 0, [wheelCell.modelData.id + "B"]: 0 }))
                            }
                        }

                        Item {
                            id: wheel
                            width: parent.width
                            height: width
                            readonly property real radius: width / 2 - 4

                            Canvas {
                                anchors.fill: parent
                                onPaint: {
                                    const ctx = getContext("2d")
                                    ctx.reset()
                                    const c = width / 2
                                    const r = wheel.radius
                                    for (let i = 0; i < 72; i++) {
                                        const a0 = -(i * 5) * Math.PI / 180
                                        const a1 = -((i + 1) * 5 + 0.5) * Math.PI / 180
                                        ctx.beginPath()
                                        ctx.moveTo(c, c)
                                        ctx.arc(c, c, r, a0, a1, true)
                                        ctx.closePath()
                                        ctx.fillStyle = Qt.hsla(i / 72, 0.85, 0.5, 1)
                                        ctx.fill()
                                    }
                                    const g = ctx.createRadialGradient(c, c, 0, c, c, r)
                                    g.addColorStop(0, "rgba(20,20,22,1)")
                                    g.addColorStop(0.85, "rgba(20,20,22,0.35)")
                                    g.addColorStop(1, "rgba(20,20,22,0)")
                                    ctx.beginPath()
                                    ctx.arc(c, c, r, 0, Math.PI * 2)
                                    ctx.fillStyle = g
                                    ctx.fill()
                                }
                            }

                            Rectangle {
                                width: 12
                                height: 12
                                radius: 6
                                color: "white"
                                border.width: 2
                                border.color: "#111"
                                x: wheel.width / 2 + wheelCell.ptX * wheel.radius - width / 2
                                y: wheel.height / 2 - wheelCell.ptY * wheel.radius - height / 2
                            }

                            MouseArea {
                                anchors.fill: parent
                                enabled: root.canEdit
                                preventStealing: true
                                function place(mx, my) {
                                    let x = (mx - wheel.width / 2) / wheel.radius
                                    let y = -(my - wheel.height / 2) / wheel.radius
                                    const len = Math.sqrt(x * x + y * y)
                                    if (len > 1) { x /= len; y /= len }
                                    wheelCell.dx = x
                                    wheelCell.dy = y
                                    const ch = wheelCell.channels(x, y)
                                    root.preview(wheelCell.modelData.id + "R", ch[0])
                                    root.preview(wheelCell.modelData.id + "G", ch[1])
                                    root.preview(wheelCell.modelData.id + "B", ch[2])
                                }
                                onPressed: (mouse) => {
                                    wheelCell.dx = wheelCell.ptX
                                    wheelCell.dy = wheelCell.ptY
                                    wheelCell.dragging = true
                                    root.beginEdit("color.wheels", qsTr("Adjust %1").arg(wheelCell.modelData.label))
                                    place(mouse.x, mouse.y)
                                }
                                onPositionChanged: (mouse) => place(mouse.x, mouse.y)
                                onReleased: {
                                    root.endEdit()
                                    wheelCell.dragging = false
                                }
                            }
                        }

                        Row {
                            spacing: 4
                            anchors.horizontalCenter: parent.horizontalCenter
                            Repeater {
                                model: [
                                    { c: "#e5484d", v: wheelCell.dragging ? wheelCell.channels(wheelCell.dx, wheelCell.dy)[0] : wheelCell.rv },
                                    { c: "#46c26a", v: wheelCell.dragging ? wheelCell.channels(wheelCell.dx, wheelCell.dy)[1] : wheelCell.gv },
                                    { c: "#3d7be0", v: wheelCell.dragging ? wheelCell.channels(wheelCell.dx, wheelCell.dy)[2] : wheelCell.bv }
                                ]
                                delegate: Column {
                                    required property var modelData
                                    spacing: 1
                                    Rectangle { width: 30; height: 3; radius: 1; color: modelData.c }
                                    Text {
                                        width: 30
                                        horizontalAlignment: Text.AlignHCenter
                                        text: Number(modelData.v).toFixed(2)
                                        color: Theme.panelForeground
                                        font.family: Theme.monoFontFamily
                                        font.pixelSize: 10
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // --- LUT -----------------------------------------------------------------------------
        LutPage {
            visible: root.page === "lut"
            width: parent.width
            host: root
        }

        // --- Mask ----------------------------------------------------------------------------
        Column {
            visible: root.page === "mask"
            width: parent.width
            spacing: Theme.spacingLg

            Text {
                width: parent.width
                text: qsTr("Add mask")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            Grid {
                width: parent.width
                columns: 3
                spacing: Theme.spacingSm
                readonly property real cell: (width - spacing * 2) / 3

                Repeater {
                    model: EditorState.maskCatalog()
                    delegate: ThemedButton {
                        required property var modelData
                        width: parent.cell
                        text: modelData.label
                        enabled: root.canEdit
                        onClicked: EditorState.addMaskToClip(EditorState.selectedTrack,
                                                             EditorState.selectedClip,
                                                             modelData.id)
                    }
                }
            }

            MasksInspector { width: parent.width }
        }
    }
}
