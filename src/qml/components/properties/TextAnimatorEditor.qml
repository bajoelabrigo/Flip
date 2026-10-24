import QtQuick
import Drift
import ".."

// Visual editor for one In / Out / Loop slot of a text (Personalizar, 0.22.1): the slot's
// animators, part by part, the way CapCut and After Effects build a text animation. Each part
// says what it animates by (block, character, word, line), in which order and how fast, and
// which properties it moves; their values are the animated state (where an In starts from,
// where an Out ends, how far a Loop swings), the text's own look being the resting state.
//
// A preset slot starts from the preset expanded into animators (textAnimationSlotForEditing);
// the first change turns the slot into its own inline animators. Slider drags preview through
// previewSetTextAnimationSlot between begin/commitPreviewDrag, so a drag is one undo step.
Column {
    id: root

    property string slot: "in"
    property int trackIndex: -1
    property int clipIndex: -1
    // The slot as the inspector reads it. A change that is not ours (undo, MCP, a preset picked
    // or tuned in the gallery) reloads the editor.
    property var slotData: ({})

    signal closeRequested()
    signal saveRequested()
    signal previewRequested()

    property var animators: []
    property var particles: []
    property real delay: 0
    property real durationOverride: 0
    property real period: 0
    property string source: "new"
    property string sourceLabel: ""
    // Canonical spelling of the last list we sent, to tell our own echo from an outside change.
    property string lastSent: ""
    property bool dragging: false
    // Bumped when parts or their property rows come and go (not on value edits), so the rows
    // of a part being dragged are never rebuilt under the pointer.
    property int structureRev: 0

    spacing: Theme.spacingMd

    readonly property var units: ["block", "character", "word", "line"]
    readonly property var unitLabels: [qsTr("Whole block"), qsTr("Character"), qsTr("Word"), qsTr("Line")]
    readonly property var orders: ["forward", "backward", "centerOut", "random"]
    readonly property var orderLabels: [qsTr("Forward"), qsTr("Backward"), qsTr("Center out"), qsTr("Random")]
    readonly property var easeChips: [
        { "id": "linear", "label": qsTr("Linear") },
        { "id": "easeInOut", "label": qsTr("Smooth") },
        { "id": "smooth", "label": qsTr("Gentle") },
        { "id": "easeIn", "label": qsTr("Speed up") },
        { "id": "easeOut", "label": qsTr("Snappy") },
        { "id": "back", "label": qsTr("Back") },
        { "id": "bounce", "label": qsTr("Bounce") }
    ]
    // What a part can move. `def` is the value a property starts with when switched on.
    readonly property var propDefs: [
        { "id": "moveX", "label": qsTr("Move X"), "unit": "px", "from": -1000, "to": 1000, "step": 1, "def": 100 },
        { "id": "moveY", "label": qsTr("Move Y"), "unit": "px", "from": -1000, "to": 1000, "step": 1, "def": 100 },
        { "id": "scaleX", "label": qsTr("Scale X"), "unit": "%", "from": 0, "to": 400, "step": 1, "def": 0 },
        { "id": "scaleY", "label": qsTr("Scale Y"), "unit": "%", "from": 0, "to": 400, "step": 1, "def": 0 },
        { "id": "rotation", "label": qsTr("Rotation"), "unit": "°", "from": -720, "to": 720, "step": 1, "def": 90 },
        { "id": "rotationX", "label": qsTr("3D turn X"), "unit": "°", "from": -180, "to": 180, "step": 1, "def": 90 },
        { "id": "rotationY", "label": qsTr("3D turn Y"), "unit": "°", "from": -180, "to": 180, "step": 1, "def": 90 },
        { "id": "opacity", "label": qsTr("Opacity"), "unit": "%", "from": 0, "to": 100, "step": 1, "def": 0 },
        { "id": "blur", "label": qsTr("Blur"), "unit": "px", "from": 0, "to": 100, "step": 1, "def": 20 },
        { "id": "tracking", "label": qsTr("Letter spacing"), "unit": "px", "from": -50, "to": 200, "step": 1, "def": 30 },
        { "id": "fillColor", "label": qsTr("Fill colour"), "color": true, "def": "#ff3fd0c9" },
        { "id": "strokeWidth", "label": qsTr("Stroke width"), "unit": "px", "from": 0, "to": 50, "step": 0.5, "def": 4 },
        { "id": "glow", "label": qsTr("Glow"), "unit": "px", "from": 0, "to": 100, "step": 1, "def": 20 }
    ]

    // ----- Data -------------------------------------------------------------------------------

    function canon(v) {
        if (Array.isArray(v))
            return "[" + v.map(root.canon).join(",") + "]"
        if (v !== null && typeof v === "object") {
            const keys = Object.keys(v).sort()
            return "{" + keys.map(k => JSON.stringify(k) + ":" + root.canon(v[k])).join(",") + "}"
        }
        return JSON.stringify(v)
    }
    function clone(v) {
        return JSON.parse(JSON.stringify(v === undefined ? null : v))
    }

    function reload() {
        if (root.trackIndex < 0 || root.clipIndex < 0)
            return
        const e = EditorState.textAnimationSlotForEditing(root.trackIndex, root.clipIndex, root.slot)
        root.animators = root.clone(e.animators || [])
        root.particles = root.clone(e.particles || [])
        root.delay = Number(e.delay) || 0
        root.durationOverride = Number(e.durationOverride) || 0
        root.period = Number(e.period) || 0
        root.source = e.source || "new"
        root.sourceLabel = e.label || ""
        root.lastSent = root.source === "inline" ? root.canon(root.animators) : ""
        root.structureRev++
    }

    onSlotChanged: reload()
    onTrackIndexChanged: reload()
    onClipIndexChanged: reload()
    Component.onCompleted: reload()
    onSlotDataChanged: {
        if (root.dragging)
            return
        const incoming = root.slotData && root.slotData.custom ? root.canon(root.slotData.animators || []) : ""
        if (incoming.length > 0 && incoming === root.lastSent)
            return
        root.reload()
    }

    function payload() {
        return {
            "animators": root.animators,
            "particles": root.particles,
            "delay": root.delay,
            "durationOverride": root.durationOverride,
            "period": root.period
        }
    }
    function send(preview) {
        root.lastSent = root.canon(EditorState.normalizeTextAnimators(root.animators))
        root.source = "inline"
        if (preview)
            EditorState.previewSetTextAnimationSlot(root.trackIndex, root.clipIndex, root.slot, root.payload())
        else
            EditorState.setTextAnimationSlot(root.trackIndex, root.clipIndex, root.slot, root.payload())
    }
    // Applies `fn` to a copy of the list and sends it; `preview` while a slider is held.
    function edit(fn, preview) {
        const list = root.clone(root.animators)
        fn(list)
        root.animators = list
        root.send(preview)
    }
    function beginDrag() {
        root.dragging = true
        EditorState.beginPreviewDrag(qsTr("Edit text animation"))
    }
    function endDrag() {
        EditorState.commitPreviewDrag()
        root.dragging = false
    }

    function newAnimator() {
        const sel = root.slot === "loop"
                    ? { "driver": "wiggle", "domain": "character", "wave": "sine", "frequencyHz": 1.0 }
                    : { "driver": "stagger", "domain": "character", "staggerUs": 50000, "durationUs": 400000,
                        "ease": "easeOut", "order": "forward" }
        const props = root.slot === "loop" ? { "rotation": 8 } : { "opacity": 0 }
        return { "selectors": [sel], "props": props }
    }
    function addAnimator() {
        root.edit(list => list.push(root.newAnimator()), false)
        root.structureRev++
    }
    function duplicateAnimator(i) {
        root.edit(list => list.splice(i + 1, 0, root.clone(list[i])), false)
        root.structureRev++
    }
    function removeAnimator(i) {
        root.edit(list => list.splice(i, 1), false)
        root.structureRev++
    }

    // The first selector carries what the editor shows; a part without one gets one on demand.
    function selectorOf(anim) {
        return anim && anim.selectors && anim.selectors.length > 0 ? anim.selectors[0] : null
    }
    function ensureSelector(anim) {
        if (!anim.selectors || anim.selectors.length === 0) {
            const fresh = root.newAnimator().selectors[0]
            fresh.domain = "block"
            anim.selectors = [fresh]
        }
        return anim.selectors[0]
    }
    function unitIndex(sel) {
        const d = sel ? String(sel.domain || "word") : "block"
        if (d === "block")
            return 0
        if (d === "character" || d === "characterWithSpaces")
            return 1
        if (d === "line")
            return 3
        return 2
    }
    function setSelectorKey(i, key, value, preview) {
        root.edit(list => { root.ensureSelector(list[i])[key] = value }, preview)
    }
    function easeOf(sel) {
        if (!sel || sel.ease === undefined)
            return "easeOut"
        return typeof sel.ease === "string" ? sel.ease : String(sel.ease.kind || "")
    }

    // A param is a plain number or {value, curve}; the editor shows and writes the constant.
    function paramValue(v, fallback) {
        if (v === undefined || v === null)
            return fallback
        if (typeof v === "object")
            return Number(v.value)
        return Number(v)
    }
    function isOn(anim, id) {
        const p = (anim && anim.props) || {}
        if (id === "moveX" || id === "moveY") {
            const pos = p.position
            if (!pos)
                return false
            const v = pos[id === "moveX" ? "x" : "y"]
            return typeof v === "object" || root.paramValue(v, 0) !== 0
        }
        return p[id] !== undefined
    }
    function onIds(anim) {
        return root.propDefs.filter(d => root.isOn(anim, d.id)).map(d => d.id)
    }
    function propDef(id) {
        return root.propDefs.find(d => d.id === id)
    }
    function propValue(anim, id) {
        const p = (anim && anim.props) || {}
        const def = root.propDef(id)
        if (id === "moveX" || id === "moveY")
            return root.paramValue(p.position ? p.position[id === "moveX" ? "x" : "y"] : undefined, 0)
        if (def && def.color)
            return p[id] !== undefined ? String(p[id]) : def.def
        const rest = id === "scaleX" || id === "scaleY" || id === "opacity" ? 100 : 0
        return root.paramValue(p[id], rest)
    }
    // Position and tracking may be in em or a fraction of the box (presets, Lottie imports).
    function lengthUnit(anim, id) {
        const p = (anim && anim.props) || {}
        if (id === "moveX" || id === "moveY")
            return (p.position && p.position.unit) || "px"
        if (id === "tracking")
            return p.trackingUnit || "px"
        return ""
    }
    function rangeOf(anim, def) {
        const u = root.lengthUnit(anim, def.id)
        if (u === "em")
            return { "from": def.id === "tracking" ? -1 : -20, "to": def.id === "tracking" ? 2 : 20, "step": 0.01, "unit": "em" }
        if (u === "box")
            return { "from": -2, "to": 2, "step": 0.01, "unit": "×" }
        return { "from": def.from, "to": def.to, "step": def.step, "unit": def.unit }
    }
    function writeProp(anim, id, value) {
        if (!anim.props)
            anim.props = {}
        const p = anim.props
        if (id === "moveX" || id === "moveY") {
            if (!p.position)
                p.position = { "x": 0, "y": 0, "unit": "px" }
            p.position[id === "moveX" ? "x" : "y"] = value
            return
        }
        p[id] = value
    }
    function setProp(i, id, value, preview) {
        root.edit(list => root.writeProp(list[i], id, value), preview)
    }
    function addProp(i, id) {
        root.setProp(i, id, root.propDef(id).def, false)
        root.structureRev++
    }
    function removeProp(i, id) {
        root.edit(list => {
            const p = list[i].props || {}
            if (id === "moveX" || id === "moveY") {
                if (p.position) {
                    p.position[id === "moveX" ? "x" : "y"] = 0
                    if (root.paramValue(p.position.x, 0) === 0 && root.paramValue(p.position.y, 0) === 0
                            && typeof p.position.x !== "object" && typeof p.position.y !== "object")
                        delete p.position
                }
            } else {
                delete p[id]
                if (id === "tracking")
                    delete p.trackingUnit
            }
        }, false)
        root.structureRev++
    }

    function formatted(v, step, unit) {
        const decimals = step > 0 && step < 1 ? Math.min(3, Math.ceil(-Math.log10(step))) : 0
        return Number(v).toFixed(decimals) + " " + unit
    }

    // ----- Layout -----------------------------------------------------------------------------

    Row {
        width: parent.width
        spacing: Theme.spacingSm

        Text {
            width: parent.width - previewButton.width - doneButton.width - 2 * parent.spacing
            anchors.verticalCenter: parent.verticalCenter
            text: qsTr("Customize animation")
            elide: Text.ElideRight
            color: Theme.panelForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSm
            font.weight: Font.DemiBold
        }
        IconButton {
            id: previewButton
            glyph: Theme.icons.play
            variant: "ghost"
            buttonSize: Theme.controlHeightSm
            iconSize: 14
            tooltip: qsTr("Preview this animation")
            onClicked: root.previewRequested()
        }
        IconButton {
            id: doneButton
            glyph: Theme.icons.x
            variant: "ghost"
            buttonSize: Theme.controlHeightSm
            iconSize: 14
            tooltip: qsTr("Close the editor")
            onClicked: root.closeRequested()
        }
    }

    Text {
        width: parent.width
        wrapMode: Text.WordWrap
        visible: text.length > 0
        text: root.source === "preset" && root.sourceLabel.length > 0
              ? qsTr("Starting from “%1”. Your changes make it this text's own animation.").arg(root.sourceLabel)
              : root.slot === "loop"
                ? qsTr("Each part sways the text by these values, over and over.")
                : root.slot === "out"
                  ? qsTr("Each part takes the text from its look to these values.")
                  : qsTr("Each part brings the text from these values to its look.")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }

    Repeater {
        model: root.animators.length
        delegate: Rectangle {
            id: card
            required property int index
            readonly property var anim: root.animators[index] || ({})
            readonly property var sel: root.selectorOf(anim)
            readonly property string driver: sel ? String(sel.driver || "stagger") : ""
            // Which property rows show; refreshed only when rows come and go.
            property string onKey: ""
            readonly property var onList: onKey.length > 0 ? onKey.split(",") : []
            function refresh() {
                card.onKey = root.onIds(root.animators[card.index]).join(",")
            }
            Component.onCompleted: refresh()
            Connections {
                target: root
                function onStructureRevChanged() { card.refresh() }
            }

            width: root.width
            height: cardCol.height + 2 * Theme.spacingMd
            radius: Theme.radiusSm
            color: "transparent"
            border.width: Theme.borderWidth
            border.color: Theme.panelBorder

            Column {
                id: cardCol
                x: Theme.spacingMd
                y: Theme.spacingMd
                width: parent.width - 2 * Theme.spacingMd
                spacing: Theme.spacingMd

                Row {
                    width: parent.width
                    spacing: Theme.spacingSm
                    Text {
                        width: parent.width - dupButton.width - delButton.width - 2 * parent.spacing
                        anchors.verticalCenter: parent.verticalCenter
                        text: qsTr("Part %1").arg(card.index + 1)
                        elide: Text.ElideRight
                        color: Theme.panelForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSm
                        font.weight: Font.Medium
                    }
                    IconButton {
                        id: dupButton
                        glyph: Theme.icons.copyPlus
                        variant: "ghost"
                        buttonSize: Theme.controlHeightSm
                        iconSize: 14
                        tooltip: qsTr("Duplicate part")
                        onClicked: root.duplicateAnimator(card.index)
                    }
                    IconButton {
                        id: delButton
                        glyph: Theme.icons.trash
                        variant: "ghost"
                        buttonSize: Theme.controlHeightSm
                        iconSize: 14
                        enabled: root.animators.length > 1
                        tooltip: qsTr("Remove part")
                        onClicked: root.removeAnimator(card.index)
                    }
                }

                Row {
                    width: parent.width
                    spacing: 8

                    Column {
                        width: (parent.width - parent.spacing) / 2
                        spacing: 4
                        Text {
                            text: qsTr("By")
                            color: Theme.mutedForeground
                            font.pixelSize: Theme.fontSizeXs
                            font.family: Theme.fontFamily
                        }
                        ThemedComboBox {
                            width: parent.width
                            model: root.unitLabels
                            currentIndex: root.unitIndex(card.sel)
                            onActivated: root.setSelectorKey(card.index, "domain", root.units[currentIndex], false)
                        }
                    }

                    Column {
                        width: (parent.width - parent.spacing) / 2
                        spacing: 4
                        visible: card.driver === "stagger"
                        Text {
                            text: qsTr("Order")
                            color: Theme.mutedForeground
                            font.pixelSize: Theme.fontSizeXs
                            font.family: Theme.fontFamily
                        }
                        ThemedComboBox {
                            width: parent.width
                            model: root.orderLabels
                            enabled: root.unitIndex(card.sel) !== 0
                            currentIndex: Math.max(0, root.orders.indexOf(card.sel ? String(card.sel.order || "forward") : "forward"))
                            onActivated: root.setSelectorKey(card.index, "order", root.orders[currentIndex], false)
                        }
                    }
                }

                // Stagger: each unit starts this long after the previous one and moves for the duration.
                Column {
                    width: parent.width
                    spacing: 4
                    visible: card.driver === "stagger"

                    Text {
                        text: qsTr("Stagger") + "  " + Math.round(Number(card.sel ? card.sel.staggerUs : 0) / 1000) + " ms"
                        color: Theme.mutedForeground
                        font.pixelSize: Theme.fontSizeXs
                        font.family: Theme.fontFamily
                    }
                    ThemedSlider {
                        id: staggerSlider
                        lockWhilePlaying: true
                        width: parent.width
                        label: qsTr("Stagger")
                        enabled: root.unitIndex(card.sel) !== 0
                        from: 0
                        to: 500
                        stepSize: 5
                        valueFormatter: function (v) { return Math.round(v) + " ms" }
                        Binding on value {
                            when: !staggerSlider.pressed
                            value: Number(card.sel ? card.sel.staggerUs : 0) / 1000
                        }
                        onMoved: root.setSelectorKey(card.index, "staggerUs", Math.round(value) * 1000, pressed)
                        onPressedChanged: pressed ? root.beginDrag() : root.endDrag()
                    }

                    Text {
                        text: qsTr("Duration") + "  " + (Number(card.sel ? card.sel.durationUs : 0) / 1000000).toFixed(2) + " s"
                        color: Theme.mutedForeground
                        font.pixelSize: Theme.fontSizeXs
                        font.family: Theme.fontFamily
                    }
                    ThemedSlider {
                        id: unitDurationSlider
                        lockWhilePlaying: true
                        width: parent.width
                        label: qsTr("Duration")
                        from: 0
                        to: 3
                        stepSize: 0.01
                        valueFormatter: function (v) { return Number(v).toFixed(2) + " s" }
                        Binding on value {
                            when: !unitDurationSlider.pressed
                            value: Number(card.sel ? card.sel.durationUs : 0) / 1000000
                        }
                        onMoved: root.setSelectorKey(card.index, "durationUs", Math.round(value * 1000000), pressed)
                        onPressedChanged: pressed ? root.beginDrag() : root.endDrag()
                    }

                    Text {
                        text: qsTr("Ease")
                        color: Theme.mutedForeground
                        font.pixelSize: Theme.fontSizeXs
                        font.family: Theme.fontFamily
                    }
                    Flow {
                        width: parent.width
                        spacing: Theme.spacingSm
                        Repeater {
                            model: root.easeChips
                            delegate: ThemedChip {
                                required property var modelData
                                text: modelData.label
                                selected: root.easeOf(card.sel) === modelData.id
                                onClicked: root.setSelectorKey(card.index, "ease", modelData.id, false)
                            }
                        }
                    }
                }

                // Wiggle (Loop): a wave that runs for as long as the text is on screen.
                Column {
                    width: parent.width
                    spacing: 4
                    visible: card.driver === "wiggle"

                    Text {
                        text: qsTr("Speed") + "  " + Number(card.sel ? (card.sel.frequencyHz !== undefined ? card.sel.frequencyHz : 1.1) : 0).toFixed(2) + " Hz"
                        color: Theme.mutedForeground
                        font.pixelSize: Theme.fontSizeXs
                        font.family: Theme.fontFamily
                    }
                    ThemedSlider {
                        id: speedSlider
                        lockWhilePlaying: true
                        width: parent.width
                        label: qsTr("Speed")
                        from: 0.1
                        to: 6
                        stepSize: 0.05
                        valueFormatter: function (v) { return Number(v).toFixed(2) + " Hz" }
                        Binding on value {
                            when: !speedSlider.pressed
                            value: card.sel && card.sel.frequencyHz !== undefined ? Number(card.sel.frequencyHz) : 1.1
                        }
                        onMoved: root.setSelectorKey(card.index, "frequencyHz", value, pressed)
                        onPressedChanged: pressed ? root.beginDrag() : root.endDrag()
                    }

                    Text {
                        text: qsTr("Phase") + "  " + Math.round(card.sel && card.sel.spatialPhaseDeg !== undefined ? Number(card.sel.spatialPhaseDeg) : 34.4) + "°"
                        color: Theme.mutedForeground
                        font.pixelSize: Theme.fontSizeXs
                        font.family: Theme.fontFamily
                    }
                    ThemedSlider {
                        id: phaseSlider
                        lockWhilePlaying: true
                        width: parent.width
                        label: qsTr("Phase")
                        enabled: root.unitIndex(card.sel) !== 0
                        from: 0
                        to: 180
                        stepSize: 1
                        valueFormatter: function (v) { return Math.round(v) + "°" }
                        Binding on value {
                            when: !phaseSlider.pressed
                            value: card.sel && card.sel.spatialPhaseDeg !== undefined ? Number(card.sel.spatialPhaseDeg) : 34.4
                        }
                        onMoved: root.setSelectorKey(card.index, "spatialPhaseDeg", value, pressed)
                        onPressedChanged: pressed ? root.beginDrag() : root.endDrag()
                    }
                }

                Text {
                    width: parent.width
                    wrapMode: Text.WordWrap
                    visible: card.driver !== "stagger" && card.driver !== "wiggle"
                    text: qsTr("This part keeps the timing of the animation it came from.")
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                }

                Text {
                    text: root.slot === "loop" ? qsTr("Moves by") : root.slot === "out" ? qsTr("Ends at") : qsTr("Starts from")
                    color: Theme.panelForeground
                    font.pixelSize: Theme.fontSizeXs
                    font.family: Theme.fontFamily
                    font.weight: Font.Medium
                }

                Repeater {
                    model: card.onList
                    delegate: Column {
                        id: propRow
                        required property var modelData
                        readonly property var def: root.propDef(modelData)
                        readonly property var range: root.rangeOf(card.anim, def)
                        readonly property var current: root.propValue(card.anim, modelData)
                        width: cardCol.width
                        spacing: 4

                        Row {
                            width: parent.width
                            spacing: 6
                            Text {
                                width: parent.width - removePropButton.width - parent.spacing
                                anchors.verticalCenter: parent.verticalCenter
                                text: propRow.def.color
                                      ? propRow.def.label
                                      : propRow.def.label + "  " + root.formatted(propRow.current, propRow.range.step, propRow.range.unit)
                                elide: Text.ElideRight
                                color: Theme.mutedForeground
                                font.pixelSize: Theme.fontSizeXs
                                font.family: Theme.fontFamily
                            }
                            IconButton {
                                id: removePropButton
                                glyph: Theme.icons.x
                                variant: "ghost"
                                buttonSize: 20
                                iconSize: 12
                                tooltip: qsTr("Stop animating this")
                                onClicked: root.removeProp(card.index, propRow.modelData)
                            }
                        }

                        ThemedSlider {
                            id: propSlider
                            visible: !propRow.def.color
                            lockWhilePlaying: true
                            width: parent.width
                            label: propRow.def.label
                            from: propRow.range.from
                            to: propRow.range.to
                            stepSize: propRow.range.step
                            valueFormatter: function (v) { return root.formatted(v, propRow.range.step, propRow.range.unit) }
                            Binding on value {
                                when: !propSlider.pressed
                                value: Number(propRow.current)
                            }
                            onMoved: root.setProp(card.index, propRow.modelData, value, pressed)
                            onPressedChanged: pressed ? root.beginDrag() : root.endDrag()
                        }

                        ColorSwatchField {
                            visible: !!propRow.def.color
                            hex: propRow.def.color ? String(propRow.current) : "#ffffffff"
                            tooltip: propRow.def.label
                            onEdited: value => root.setProp(card.index, propRow.modelData, value, false)
                        }
                    }
                }

                Text {
                    text: qsTr("Animate")
                    color: Theme.mutedForeground
                    font.pixelSize: Theme.fontSizeXs
                    font.family: Theme.fontFamily
                }
                Flow {
                    width: parent.width
                    spacing: Theme.spacingSm
                    Repeater {
                        model: root.propDefs
                        delegate: ThemedChip {
                            required property var modelData
                            visible: card.onList.indexOf(modelData.id) < 0
                            text: "+ " + modelData.label
                            variant: "secondary"
                            onClicked: root.addProp(card.index, modelData.id)
                        }
                    }
                }
            }
        }
    }

    Row {
        width: parent.width
        spacing: Theme.spacingSm

        ThemedButton {
            width: (parent.width - parent.spacing) / 2
            variant: "secondary"
            glyph: Theme.icons.plus
            text: qsTr("Add part")
            tooltip: qsTr("Another motion on top, with its own unit and timing")
            onClicked: root.addAnimator()
        }
        ThemedButton {
            width: (parent.width - parent.spacing) / 2
            variant: "secondary"
            glyph: Theme.icons.save
            text: qsTr("Save as my animation…")
            tooltip: qsTr("Keep it in My animations to use on other texts")
            onClicked: root.saveRequested()
        }
    }
}
