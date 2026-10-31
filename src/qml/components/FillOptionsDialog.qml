import QtQuick
import Drift


// Fill Options / Stroke Options (0.29), as After Effects opens them from the tools bar: None, Solid,
// Linear, Radial (and Sweep, which the engine also paints), blend mode and opacity, with Preview and
// OK / Cancel. With a shape or text picked it edits that clip's own Fill / Stroke layer (the same one
// the Shape panel lists) inside one edit session, so Cancel puts everything back; with nothing
// picked it sets the paint the next shapes and the pen are drawn with.
ThemedDialog {
    id: root

    property string target: "fill"
    // Editing a clip's layer ("layer") or the tools bar's paint for new shapes ("tool").
    property string mode: "tool"
    property int editTrack: -1
    property int editClip: -1
    property string layerId: ""
    property bool sessionOpen: false

    // The working copy: kind is "none" | "solid" | "linear" | "radial" | "sweep".
    property string kind: "solid"
    property string colorHex: "#ffffffff"
    property var gradient: ({})
    property real opacity01: 1.0
    property string blend: "normal"
    property real strokeWidth: 4

    readonly property bool isGradient: kind === "linear" || kind === "radial" || kind === "sweep"
    readonly property var blendModes: ["normal", "multiply", "screen", "overlay", "add", "darken", "lighten"]
    readonly property var blendLabels: [qsTr("Normal"), qsTr("Multiply"), qsTr("Screen"), qsTr("Overlay"),
                                        qsTr("Add"), qsTr("Darken"), qsTr("Lighten")]
    readonly property var defaultGradient: ({
        "kind": "linear", "angle": 0, "offset": 0, "scale": 1,
        "stops": [{ "pos": 0, "color": "#ffffffff" }, { "pos": 1, "color": "#ff000000" }]
    })

    title: target === "fill" ? qsTr("Fill Options") : qsTr("Stroke Options")
    preferredWidth: Theme.dialogWidthMd
    movable: true
    // Enter confirms the colour or number being typed, not the window (0.29: Enter accepted before
    // the hex field had written its colour, and the shape came out in the old one).
    acceptOnReturn: false

    function layerOf(style, kindName) {
        const layers = (style && style.layers) || []
        for (let i = 0; i < layers.length; ++i) {
            if (layers[i].kind === kindName)
                return layers[i]
        }
        return null
    }

    function readLayer(layer) {
        const paint = layer.paint || {}
        root.opacity01 = layer.opacity !== undefined ? Number(layer.opacity) : 1
        root.blend = layer.blend || "normal"
        root.strokeWidth = layer.width !== undefined ? Number(layer.width) : 4
        root.colorHex = paint.color || "#ffffffff"
        root.gradient = paint.gradient && paint.gradient.stops ? paint.gradient : root.defaultGradient
        if (layer.enabled === false)
            root.kind = "none"
        else if (paint.kind === "gradient")
            root.kind = (paint.gradient && paint.gradient.kind) || "linear"
        else
            root.kind = "solid"
    }

    function openFor(which, toolOnly) {
        root.target = which
        const data = EditorState.selectedClipData
        const style = data ? (data.kind === "shape" ? data.shapeStyle : data.kind === "text" ? data.textStyle : null)
                           : null
        root.layerId = ""
        if (style && EditorState.selectedClip >= 0 && !toolOnly) {
            root.mode = "layer"
            root.editTrack = EditorState.selectedTrack
            root.editClip = EditorState.selectedClip
            const layer = root.layerOf(style, which)
            if (layer) {
                root.layerId = layer.id
                root.readLayer(layer)
            } else {
                root.kind = "none"
                root.colorHex = which === "fill" ? "#ffff4d6d" : "#ffffffff"
                root.gradient = root.defaultGradient
                root.opacity01 = 1
                root.blend = "normal"
                root.strokeWidth = 4
            }
            EditorState.beginEditSession(root.title)
            root.sessionOpen = true
        } else {
            root.mode = "tool"
            const color = which === "fill" ? EditorState.preview.toolFill : EditorState.preview.toolStroke
            const options = (which === "fill" ? EditorState.preview.toolFillOptions
                                              : EditorState.preview.toolStrokeOptions) || {}
            root.readLayer({
                "enabled": color !== "none",
                "opacity": options.opacity !== undefined ? options.opacity : 1,
                "blend": options.blend || "normal",
                "width": EditorState.preview.toolStrokeWidth > 0 ? EditorState.preview.toolStrokeWidth : 4,
                "paint": Object.assign({ "kind": "solid", "color": color === "none" ? "#ffffffff" : color },
                                       options.paint || {})
            })
        }
        previewBox.checked = true
        open()
    }

    // The layer patch for the working copy (without the switch on/off).
    function patch() {
        const p = { "opacity": root.opacity01, "blend": root.blend }
        if (root.target === "stroke")
            p.width = root.strokeWidth
        if (root.isGradient) {
            const g = Object.assign({}, root.gradient)
            g.kind = root.kind
            p.paint = { "kind": "gradient", "color": root.colorHex, "gradient": g }
        } else {
            p.paint = { "kind": "solid", "color": root.colorHex }
        }
        return p
    }

    // Live on the clip while Preview is on.
    function push() {
        if (root.mode !== "layer" || !previewBox.checked)
            return
        root.write()
    }

    function write() {
        if (root.kind === "none") {
            if (root.layerId.length > 0)
                EditorState.setStyleLayer(root.editTrack, root.editClip, root.layerId, { "enabled": false })
            return
        }
        if (root.layerId.length === 0) {
            const id = EditorState.addStyleLayer(root.editTrack, root.editClip, root.target)
            if (!id)
                return
            root.layerId = id
        }
        const p = root.patch()
        p.enabled = true
        EditorState.setStyleLayer(root.editTrack, root.editClip, root.layerId, p)
    }

    function set(field, value) {
        root[field] = value
        root.push()
    }

    onAccepted: {
        if (root.mode === "layer") {
            if (!previewBox.checked)
                root.write()
            if (root.sessionOpen)
                EditorState.endEditSession(true)
            root.sessionOpen = false
            return
        }
        // The tools bar: the colour of the swatch (a gradient's first stop) and the rest as options.
        const stops = (root.gradient && root.gradient.stops) || []
        const swatch = root.kind === "none" ? "none"
                     : root.isGradient && stops.length > 0 ? stops[0].color : root.colorHex
        const plain = root.kind === "solid" && root.opacity01 >= 0.999 && root.blend === "normal"
        const options = root.kind === "none" || plain ? ({}) : root.patch()
        if (root.target === "fill") {
            EditorState.preview.toolFill = swatch
            EditorState.preview.toolFillOptions = options
        } else {
            EditorState.preview.toolStroke = swatch
            EditorState.preview.toolStrokeOptions = options
            if (root.kind !== "none")
                EditorState.preview.toolStrokeWidth = root.strokeWidth
        }
    }
    onRejected: {
        if (root.sessionOpen)
            EditorState.endEditSession(false)
        root.sessionOpen = false
    }

    contentItem: Column {
        spacing: Theme.spacingLg
        width: parent ? parent.width : 420

        // After Effects' row of paint kinds.
        Row {
            spacing: Theme.spacingSm
            Repeater {
                model: [
                    { "id": "none", "tip": qsTr("None") },
                    { "id": "solid", "tip": qsTr("Solid Color") },
                    { "id": "linear", "tip": qsTr("Linear Gradient") },
                    { "id": "radial", "tip": qsTr("Radial Gradient") },
                    { "id": "sweep", "tip": qsTr("Sweep Gradient") }
                ]
                Rectangle {
                    id: kindChip
                    required property var modelData
                    readonly property bool picked: root.kind === modelData.id
                    width: 34
                    height: 26
                    radius: Theme.radiusSm
                    color: picked ? Theme.primary : Theme.panelAccent
                    border.width: 1
                    border.color: picked ? Theme.primary : Theme.border

                    // The swatch: a red slash, a flat colour, or the gradient's shape.
                    Rectangle {
                        anchors.centerIn: parent
                        width: 20
                        height: 14
                        radius: kindChip.modelData.id === "radial" ? 7 : 2
                        border.width: 1
                        border.color: "#80000000"
                        color: kindChip.modelData.id === "none" ? "white" : kindChip.modelData.id === "solid" ? "#3b6fd8" : "white"
                        gradient: kindChip.modelData.id === "linear" || kindChip.modelData.id === "radial"
                                  || kindChip.modelData.id === "sweep" ? chipGradient : null
                        Gradient {
                            id: chipGradient
                            orientation: kindChip.modelData.id === "linear" ? Gradient.Horizontal : Gradient.Vertical
                            GradientStop { position: 0.0; color: kindChip.modelData.id === "sweep" ? "#3b6fd8" : "white" }
                            GradientStop { position: 1.0; color: kindChip.modelData.id === "sweep" ? "#e04040" : "#202020" }
                        }
                        Rectangle {
                            visible: kindChip.modelData.id === "none"
                            anchors.centerIn: parent
                            width: parent.width * 1.1
                            height: 1.5
                            rotation: -35
                            color: "#e04040"
                        }
                    }
                    MouseArea {
                        id: chipMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            const next = kindChip.modelData.id
                            if (next !== "none" && next !== "solid" && !(root.gradient && root.gradient.stops))
                                root.gradient = root.defaultGradient
                            root.set("kind", next)
                        }
                    }
                    ThemedToolTip { visible: chipMouse.containsMouse; text: kindChip.modelData.tip }
                }
            }
            ThemedLabel {
                anchors.verticalCenter: parent.verticalCenter
                leftPadding: Theme.spacingSm
                text: root.kind === "none" ? qsTr("None") : root.kind === "solid" ? qsTr("Solid Color")
                    : root.kind === "linear" ? qsTr("Linear Gradient") : root.kind === "radial"
                    ? qsTr("Radial Gradient") : qsTr("Sweep Gradient")
            }
        }

        // Solid: its colour.
        Column {
            visible: root.kind === "solid"
            width: parent.width
            spacing: Theme.spacingXs
            ThemedLabel { text: qsTr("Colour") }
            ColorSwatchField {
                width: parent.width
                hex: root.colorHex
                onEdited: value => root.set("colorHex", value)
            }
        }

        // A gradient: the stops, presets and spread, the editor the Shape panel uses.
        GradientStopEditor {
            visible: root.isGradient
            width: parent.width
            standalone: true
            keyPrefix: "shape"
            gradient: Object.assign({}, root.gradient, { "kind": root.kind })
            onEdited: p => {
                // A preset carries its own kind: the row of kinds above decides (0.29: picking a preset
                // with Radial chosen turned it Linear). Only the Type box changes the kind.
                const typeOnly = p.kind !== undefined && Object.keys(p).length === 1
                if (typeOnly)
                    root.kind = p.kind
                const g = Object.assign({}, root.gradient, p)
                g.kind = root.kind
                root.set("gradient", g)
            }
        }
        Row {
            visible: root.isGradient
            width: parent.width
            spacing: Theme.spacingLg
            Column {
                width: (parent.width - parent.spacing) / 2
                spacing: Theme.spacingXs
                ThemedLabel { text: qsTr("Angle") }
                ThemedNumberField {
                    width: parent.width
                    from: -360
                    to: 360
                    unit: "°"
                    value: Number(root.gradient && root.gradient.angle) || 0
                    onEdited: v => root.set("gradient", Object.assign({}, root.gradient, { "angle": v }))
                }
            }
            ThemedLabel {
                width: (parent.width - parent.spacing) / 2
                anchors.bottom: parent.bottom
                wrapMode: Text.WordWrap
                opacity: 0.75
                size: "sm"
                text: qsTr("Drag its two handles on the video to place it, as in After Effects.")
            }
        }

        Row {
            width: parent.width
            spacing: Theme.spacingLg
            Column {
                width: (parent.width - parent.spacing) / 2
                spacing: Theme.spacingXs
                ThemedLabel { text: qsTr("Blend mode") }
                ThemedComboBox {
                    width: parent.width
                    enabled: root.kind !== "none"
                    model: root.blendLabels
                    currentIndex: Math.max(0, root.blendModes.indexOf(root.blend))
                    onActivated: root.set("blend", root.blendModes[currentIndex])
                }
            }
            Column {
                width: (parent.width - parent.spacing) / 2
                spacing: Theme.spacingXs
                ThemedLabel { text: qsTr("Opacity") }
                ThemedNumberField {
                    width: parent.width
                    enabled: root.kind !== "none"
                    from: 0
                    to: 100
                    unit: "%"
                    value: Math.round(root.opacity01 * 100)
                    onEdited: v => root.set("opacity01", v / 100)
                }
            }
        }

        Column {
            visible: root.target === "stroke"
            width: parent.width
            spacing: Theme.spacingXs
            ThemedLabel { text: qsTr("Stroke width") }
            ThemedNumberField {
                width: parent.width
                enabled: root.kind !== "none"
                from: 0
                to: 200
                unit: "px"
                value: root.strokeWidth
                onEdited: v => root.set("strokeWidth", v)
            }
        }

        ThemedCheckBox {
            id: previewBox
            visible: root.mode === "layer"
            text: qsTr("Preview")
            checked: true
            onToggled: {
                // Off: what is on screen goes back to how it was until OK; on: the copy shows again.
                if (!root.sessionOpen)
                    return
                EditorState.endEditSession(false)
                EditorState.beginEditSession(root.title)
                // A layer added under the preview went back with it.
                const data = EditorState.selectedClipData
                const style = data ? (data.kind === "shape" ? data.shapeStyle : data.textStyle) : null
                const layer = root.layerOf(style, root.target)
                root.layerId = layer ? layer.id : ""
                if (checked)
                    root.write()
            }
        }
    }
}
