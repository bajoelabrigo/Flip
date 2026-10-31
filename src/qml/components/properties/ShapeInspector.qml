import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// The shape clip's inspector: which shape, its shading stack (the same layer rows text uses,
// keyed "shape.layer.<id>.<field>") and the keyframable geometry knobs.
Item {
    id: root

    property int clipDataRevision: 0
    readonly property var clipData: {
        void clipDataRevision
        return EditorState.selectedClipData
    }
    readonly property bool hasSelection: !!clipData && Object.keys(clipData).length > 0
    readonly property string clipKind: hasSelection ? (clipData.kind || "") : ""

    readonly property bool hasShapeStyle: hasSelection && clipKind === "shape" && !!clipData.shapeStyle
    // After Effects' Contents (0.28, Pro): a layer of parts and the part picked in the list. A shape
    // part is edited here exactly as a plain shape layer is; a group only has its transform.
    readonly property bool proMode: EditorState.preferences.proMode
    readonly property bool hasParts: hasSelection && clipData.shapeHasParts === true
    readonly property var part: hasSelection && clipData.shapePart ? clipData.shapePart : null
    readonly property bool editingPart: !!part && !part.group
    readonly property string partPrefix: part ? "part." + part.id + "." : ""
    readonly property bool showShapeSections: !hasParts || editingPart
    readonly property var shapeStyle: editingPart && part.shapeStyle ? part.shapeStyle
                                    : hasShapeStyle ? clipData.shapeStyle : ({
                                                                       "kind": "rectangle",
                                                                       "layers": [],
                                                                       "cornerRadius": 0,
                                                                       "points": 5,
                                                                       "innerRatio": 0.5,
                                                                       "headSize": 0.4,
                                                                       "thickness": 0.4,
                                                                       "tailX": 0.25,
                                                                       "tailSize": 0.2
                                                                   })
    readonly property var layers: (shapeStyle && shapeStyle.layers) || []
    readonly property var shapeCatalog: EditorState.builtinShapes()
    // Which rows are open, keyed by layer id so it survives reorders and delegate rebuilds.
    property var expandedLayerIds: ({})

    // Which geometry controls apply to the selected kind. The catalog id and the stored kind are
    // not always the same word ("circle" is an ellipse), so match on the stored kind.
    readonly property var shapeFamilies: ({
        "star": ["star", "burst"],
        // After Effects' roundness (0.28): stars and the regular polygons.
        "round": ["star", "burst", "pentagon", "hexagon", "octagon"],
        "arrow": ["arrow", "double-arrow", "block-arrow", "chevron", "banner"],
        "shaft": ["arrow", "double-arrow", "chevron", "cross", "curved-arrow"],
        "bubble": ["speech-bubble", "speech-bubble-rect", "thought-bubble", "callout"]
    })
    function shapeHas(family) {
        return root.shapeFamilies[family].indexOf(root.shapeStyle.kind) >= 0
    }

    function setShapeKey(key, value) {
        const patch = {}
        patch[key] = value
        EditorState.setShapeStyle(EditorState.selectedTrack, EditorState.selectedClip, patch)
    }
    function knob(key, label, decimals) {
        return { "key": "shape." + key, "label": label, "def": Number(root.shapeStyle[key]) || 0, "decimals": decimals }
    }
    // A part's own value (0.28): "part.<id>.<field>", keyframable like any clip property.
    function partKnob(field, label, decimals) {
        return { "key": root.partPrefix + field, "label": label,
                 "def": root.part ? Number(root.part[field]) || 0 : 0, "decimals": decimals }
    }
    function partKeyframes(field) {
        const keys = root.part && root.part.keyframes
        const entry = keys && keys[field]
        return (entry && entry.points) || []
    }
    function knobKeyframes(key) {
        const keys = root.shapeStyle && root.shapeStyle.keyframes
        const entry = keys && keys[key]
        return (entry && entry.points) || []
    }
    function setLayerExpanded(id, on) {
        const next = Object.assign({}, root.expandedLayerIds)
        if (on)
            next[id] = true
        else
            delete next[id]
        root.expandedLayerIds = next
    }
    function addLayer(kind) {
        const id = EditorState.addStyleLayer(EditorState.selectedTrack, EditorState.selectedClip, kind)
        if (id && id.length > 0)
            root.setLayerExpanded(id, true)
    }

    height: shapeTabColumn.height
    implicitHeight: shapeTabColumn.height

    Connections {
        target: EditorState
        function onSelectionChanged() { root.clipDataRevision++ }
        function onSelectedClipDataChanged() { root.clipDataRevision++ }
        function onTracksChanged() { root.clipDataRevision++ }
    }

    Column {
        id: shapeTabColumn
        width: root.width
        spacing: Theme.spacingXl

        // One entry per ShapeKind: the catalog lists "circle" and "ellipse"
        // separately so each gets its own default aspect, but they are one kind.
        readonly property var kindOptions: {
            const seen = ({})
            const out = []
            // A shape from the library (Stock › Shapes) has no built-in kind to name it.
            if (root.shapeStyle.kind === "custom")
                out.push({ "id": "", "kind": "custom",
                           "label": (root.clipData && root.clipData.name) || qsTr("Library shape") })
            for (let i = 0; i < root.shapeCatalog.length; ++i) {
                const entry = root.shapeCatalog[i]
                if (seen[entry.kind])
                    continue
                seen[entry.kind] = true
                out.push(entry)
            }
            return out
        }

        // ----- After Effects' Contents (0.28, Pro): the parts of this layer -------------------
        ShapeContentsList {
            width: parent.width
            visible: root.proMode && root.hasShapeStyle
            clipData: root.clipData
        }

        // In Simple a layer of parts is one shape: its colour goes to every part.
        Column {
            width: parent.width
            visible: !root.proMode && root.hasParts
            spacing: Theme.spacingSm
            ThemedLabel {
                width: parent.width
                wrapMode: Text.WordWrap
                opacity: 0.8
                text: qsTr("This shape is made of several parts. To edit each part, switch to Pro.")
            }
            ThemedButton {
                variant: "secondary"
                text: qsTr("See in Pro")
                onClicked: EditorState.preferences.setProMode(true)
            }
        }

        // The whole layer of parts picked: what to do next.
        ThemedLabel {
            width: parent.width
            visible: root.proMode && root.hasParts && !root.part
            wrapMode: Text.WordWrap
            opacity: 0.8
            text: qsTr("Pick a part in the list to edit its shape, fill and border. To move or scale the whole layer, use the Transform tab.")
        }

        // ----- The picked part's own transform (After Effects: Transform: <part>) ----------------
        CollapsibleSection {
            width: parent.width
            visible: root.proMode && !!root.part
            expanded: true
            title: root.part && root.part.group ? qsTr("Position and turn of the group") : qsTr("Position and turn of the part")
            tooltip: qsTr("In After Effects: Transform: %1").arg(root.part ? root.part.name : "")

            Column {
                width: parent.width
                spacing: Theme.spacingMd

                Row {
                    width: parent.width
                    spacing: 8
                    visible: root.editingPart
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.partKnob("width", qsTr("Width"), 0)
                        keyframeList: root.partKeyframes("width")
                        useSlider: true
                        sliderFrom: 1
                        sliderTo: 2000
                        unit: "px"
                    }
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.partKnob("height", qsTr("Height"), 0)
                        keyframeList: root.partKeyframes("height")
                        useSlider: true
                        sliderFrom: 1
                        sliderTo: 2000
                        unit: "px"
                    }
                }
                Row {
                    width: parent.width
                    spacing: 8
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.partKnob("x", qsTr("Position X"), 0)
                        keyframeList: root.partKeyframes("x")
                        useSlider: true
                        sliderFrom: -2000
                        sliderTo: 2000
                        unit: "px"
                    }
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.partKnob("y", qsTr("Position Y"), 0)
                        keyframeList: root.partKeyframes("y")
                        useSlider: true
                        sliderFrom: -2000
                        sliderTo: 2000
                        unit: "px"
                    }
                }
                Row {
                    width: parent.width
                    spacing: 8
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.partKnob("scaleX", qsTr("Scale X"), 0)
                        keyframeList: root.partKeyframes("scaleX")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: 400
                        unit: "%"
                    }
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.partKnob("scaleY", qsTr("Scale Y"), 0)
                        keyframeList: root.partKeyframes("scaleY")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: 400
                        unit: "%"
                    }
                }
                PropertyKeyframeRow {
                    width: parent.width
                    propDef: root.partKnob("rotation", qsTr("Rotation"), 1)
                    keyframeList: root.partKeyframes("rotation")
                    useSlider: true
                    sliderFrom: -360
                    sliderTo: 360
                    unit: "°"
                }
                PropertyKeyframeRow {
                    width: parent.width
                    propDef: root.partKnob("opacity", qsTr("Opacity"), 0)
                    keyframeList: root.partKeyframes("opacity")
                    useSlider: true
                    sliderFrom: 0
                    sliderTo: 100
                    unit: "%"
                }
                ThemedLabel { text: qsTr("Blend mode") }
                ThemedComboBox {
                    readonly property var modes: ["normal", "multiply", "screen", "overlay", "add", "darken", "lighten"]
                    width: parent.width
                    model: [qsTr("Normal"), qsTr("Multiply"), qsTr("Screen"), qsTr("Overlay"), qsTr("Add"),
                            qsTr("Darken"), qsTr("Lighten")]
                    currentIndex: Math.max(0, modes.indexOf(root.part ? root.part.blend : "normal"))
                    onActivated: index => EditorState.setShapePartBlend(EditorState.selectedTrack, EditorState.selectedClip,
                                                                       root.part.id, modes[index])
                }
                // After Effects' Wiggle Transform (0.28): the part jitters on its own; nothing moves while the
                // amounts are 0.
                CollapsibleSection {
                    width: parent.width
                    expanded: false
                    title: qsTr("Wiggle")
                    Column {
                        width: parent.width
                        spacing: Theme.spacingMd
                        ThemedLabel {
                            width: parent.width
                            wrapMode: Text.WordWrap
                            text: qsTr("The part jitters on its own, as After Effects' Wiggle Transform. Leave the amounts at 0 to keep it still.")
                            color: Theme.mutedForeground
                            font.pixelSize: Theme.fontSizeXs
                        }
                        PropertyKeyframeRow {
                            width: parent.width
                            propDef: root.partKnob("wigglePosition", qsTr("Position"), 0)
                            keyframeList: root.partKeyframes("wigglePosition")
                            useSlider: true
                            sliderFrom: 0
                            sliderTo: 200
                            unit: "px"
                        }
                        Row {
                            width: parent.width
                            spacing: 8
                            PropertyKeyframeRow {
                                width: (parent.width - parent.spacing) / 2
                                propDef: root.partKnob("wiggleRotation", qsTr("Rotation"), 0)
                                keyframeList: root.partKeyframes("wiggleRotation")
                                useSlider: true
                                sliderFrom: 0
                                sliderTo: 90
                                unit: "°"
                            }
                            PropertyKeyframeRow {
                                width: (parent.width - parent.spacing) / 2
                                propDef: root.partKnob("wiggleScale", qsTr("Scale"), 0)
                                keyframeList: root.partKeyframes("wiggleScale")
                                useSlider: true
                                sliderFrom: 0
                                sliderTo: 50
                                unit: "%"
                            }
                        }
                        Row {
                            width: parent.width
                            spacing: 8
                            PropertyKeyframeRow {
                                width: (parent.width - parent.spacing) / 2
                                propDef: root.partKnob("wiggleSpeed", qsTr("Wiggles per second"), 1)
                                keyframeList: root.partKeyframes("wiggleSpeed")
                                useSlider: true
                                sliderFrom: 0
                                sliderTo: 10
                            }
                            PropertyKeyframeRow {
                                width: (parent.width - parent.spacing) / 2
                                propDef: root.partKnob("wiggleSeed", qsTr("Seed"), 0)
                                keyframeList: root.partKeyframes("wiggleSeed")
                                useSlider: true
                                sliderFrom: 0
                                sliderTo: 100
                            }
                        }
                    }
                }
                CollapsibleSection {
                    width: parent.width
                    expanded: false
                    title: qsTr("Skew and anchor point")
                    Column {
                        width: parent.width
                        spacing: Theme.spacingMd
                        Row {
                            width: parent.width
                            spacing: 8
                            PropertyKeyframeRow {
                                width: (parent.width - parent.spacing) / 2
                                propDef: root.partKnob("skew", qsTr("Skew"), 1)
                                keyframeList: root.partKeyframes("skew")
                                useSlider: true
                                sliderFrom: -85
                                sliderTo: 85
                                unit: "°"
                            }
                            PropertyKeyframeRow {
                                width: (parent.width - parent.spacing) / 2
                                propDef: root.partKnob("skewAxis", qsTr("Skew axis"), 1)
                                keyframeList: root.partKeyframes("skewAxis")
                                useSlider: true
                                sliderFrom: -180
                                sliderTo: 180
                                unit: "°"
                            }
                        }
                        Row {
                            width: parent.width
                            spacing: 8
                            PropertyKeyframeRow {
                                width: (parent.width - parent.spacing) / 2
                                propDef: root.partKnob("anchorX", qsTr("Anchor X"), 0)
                                keyframeList: root.partKeyframes("anchorX")
                                useSlider: true
                                sliderFrom: -1000
                                sliderTo: 1000
                                unit: "px"
                            }
                            PropertyKeyframeRow {
                                width: (parent.width - parent.spacing) / 2
                                propDef: root.partKnob("anchorY", qsTr("Anchor Y"), 0)
                                keyframeList: root.partKeyframes("anchorY")
                                useSlider: true
                                sliderFrom: -1000
                                sliderTo: 1000
                                unit: "px"
                            }
                        }
                    }
                }
            }
        }

        Column {
            visible: root.showShapeSections
            width: parent.width
            spacing: Theme.spacingXs

            ThemedLabel { text: qsTr("Shape") }

            ThemedLabel {
                width: parent.width
                opacity: 0.8
                text: qsTr("Swapping the shape keeps its position, size, style and effects.")
            }

            ThemedComboBox {
                id: shapeKindBox
                width: parent.width
                model: shapeTabColumn.kindOptions
                textRole: "label"
                valueRole: "id"
                tooltip: qsTr("Shape drawn by this clip")
                currentIndex: {
                    const options = shapeTabColumn.kindOptions
                    for (let i = 0; i < options.length; ++i) {
                        if (options[i].kind === root.shapeStyle.kind)
                            return i
                    }
                    return 0
                }
                onActivated: {
                    if (currentValue)
                        root.setShapeKey("kind", currentValue)
                }
            }
        }

        // ----- Layers -----------------------------------------------------
        Column {
            visible: root.showShapeSections
            width: parent.width
            spacing: Theme.spacingMd

            Row {
                width: parent.width
                spacing: Theme.spacingSm

                Text {
                    width: parent.width - addLayerButton.width - parent.spacing
                    anchors.verticalCenter: parent.verticalCenter
                    text: qsTr("Layers")
                    color: Theme.panelForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSm
                    font.weight: Font.DemiBold
                }
                ThemedButton {
                    id: addLayerButton
                    variant: "secondary"
                    glyph: Theme.icons.plus
                    text: qsTr("Add layer")
                    tooltip: qsTr("Add a fill, stroke, shadow, glow or extrude layer")
                    onClicked: addLayerMenu.popup()

                    ThemedContextMenu {
                        id: addLayerMenu
                        ThemedMenuItem { text: qsTr("Fill"); onTriggered: root.addLayer("fill") }
                        ThemedMenuItem { text: qsTr("Stroke"); onTriggered: root.addLayer("stroke") }
                        ThemedMenuItem { text: qsTr("Shadow"); onTriggered: root.addLayer("shadow") }
                        ThemedMenuItem { text: qsTr("Glow"); onTriggered: root.addLayer("glow") }
                        ThemedMenuItem { text: qsTr("Extrude"); onTriggered: root.addLayer("extrude") }
                    }
                }
            }

            Text {
                visible: root.layers.length === 0
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("No layers. Add a fill to start.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            // Integer model so rows survive the fresh QVariantList every edit produces; the list
            // is walked from the back so the front-most layer sits on top.
            Repeater {
                model: root.layers.length
                delegate: ShadingLayerRow {
                    required property int index
                    width: parent.width
                    layerData: root.layers[root.layers.length - 1 - index] || ({})
                    styleData: root.shapeStyle
                    keyPrefix: "shape"
                    position: index
                    count: root.layers.length
                    expanded: root.expandedLayerIds[layerId] === true
                    onToggleRequested: root.setLayerExpanded(layerId, !expanded)
                }
            }
        }

        // ----- Geometry ---------------------------------------------------
        CollapsibleSection {
            visible: root.showShapeSections
            width: parent.width
            title: qsTr("Geometry")

            Column {
                width: parent.width
                spacing: Theme.spacingMd

                PropertyKeyframeRow {
                    width: parent.width
                    visible: root.shapeStyle.kind !== "ellipse"
                    propDef: root.knob("cornerRadius", qsTr("Corner radius"), 0)
                    keyframeList: root.knobKeyframes("cornerRadius")
                    useSlider: true
                    sliderFrom: 0
                    sliderTo: 400
                    unit: "px"
                }

                Row {
                    width: parent.width
                    spacing: 8
                    visible: root.shapeHas("star")

                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("points", qsTr("Points"), 0)
                        keyframeList: root.knobKeyframes("points")
                        useSlider: true
                        sliderFrom: 3
                        sliderTo: 60
                    }
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("innerRatio", qsTr("Inner radius"), 2)
                        keyframeList: root.knobKeyframes("innerRatio")
                        useSlider: true
                        sliderFrom: 0.05
                        sliderTo: 0.95
                        percent: true
                    }
                }

                // Rounded corners as After Effects' Outer / Inner Roundness: at 100 % a polygon is a circle.
                Row {
                    width: parent.width
                    spacing: 8
                    visible: root.shapeHas("round")

                    PropertyKeyframeRow {
                        width: root.shapeHas("star") ? (parent.width - parent.spacing) / 2 : parent.width
                        propDef: root.knob("outerRoundness", qsTr("Outer roundness"), 0)
                        keyframeList: root.knobKeyframes("outerRoundness")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: 100
                        unit: "%"
                    }
                    PropertyKeyframeRow {
                        visible: root.shapeHas("star")
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("innerRoundness", qsTr("Inner roundness"), 0)
                        keyframeList: root.knobKeyframes("innerRoundness")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: 100
                        unit: "%"
                    }
                }

                Row {
                    width: parent.width
                    spacing: 8
                    visible: root.shapeHas("arrow") || root.shapeHas("shaft")

                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        visible: root.shapeHas("arrow")
                        propDef: root.knob("headSize", qsTr("Head size"), 2)
                        keyframeList: root.knobKeyframes("headSize")
                        useSlider: true
                        sliderFrom: 0.05
                        sliderTo: 0.9
                        percent: true
                    }
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        visible: root.shapeHas("shaft")
                        propDef: root.knob("thickness", qsTr("Thickness"), 2)
                        keyframeList: root.knobKeyframes("thickness")
                        useSlider: true
                        sliderFrom: 0.05
                        sliderTo: 1
                        percent: true
                    }
                }

                Row {
                    width: parent.width
                    spacing: 8
                    visible: root.shapeHas("bubble")

                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("tailX", qsTr("Tail position"), 2)
                        keyframeList: root.knobKeyframes("tailX")
                        useSlider: true
                        sliderFrom: 0.08
                        sliderTo: 0.92
                        percent: true
                    }
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("tailSize", qsTr("Tail size"), 2)
                        keyframeList: root.knobKeyframes("tailSize")
                        useSlider: true
                        sliderFrom: 0.05
                        sliderTo: 0.5
                        percent: true
                    }
                }
            }
        }

        // ----- After Effects' Path (0.26): edit and animate a drawn outline -
        CollapsibleSection {
            visible: root.showShapeSections && !root.hasParts
            width: parent.width
            title: qsTr("Path")
            // Every shape: a rectangle, ellipse or star turns into an editable path on "Edit points"
            // (Jorge, 0.26: the section was missing on them and nothing said why).
            readonly property bool editablePath: root.shapeStyle.kind === "custom"

            Column {
                width: parent.width
                spacing: Theme.spacingMd

                readonly property var pathState: {
                    void root.clipDataRevision
                    void EditorState.playheadSeconds
                    return EditorState.shapePathState(EditorState.selectedTrack, EditorState.selectedClip)
                }

                ThemedLabel {
                    width: parent.width
                    opacity: 0.8
                    wrapMode: Text.WordWrap
                    text: qsTr("As in After Effects. Edit points: click a point to select it, Shift+click or drag a box for several, drag to move them, drag a line to bend it, Delete removes them and the arrows nudge them. Alt+click turns a point corner or smooth, Alt+drag pulls new handles, Ctrl+click removes it. Pen: click for corners, click and drag for curves, click the first point to close, Enter to leave it open; over a selected shape it adds a point on a line, carries on an open end, or starts another path. With the stopwatch on, each change is a key at the playhead and the shape morphs between them.")
                }
                ThemedLabel {
                    width: parent.width
                    visible: root.shapeStyle.kind !== "custom"
                    wrapMode: Text.WordWrap
                    size: "sm"
                    opacity: 0.7
                    text: qsTr("This shape becomes an editable path when you edit its points.")
                }
                Row {
                    width: parent.width
                    spacing: 8
                    ThemedButton {
                        width: (parent.width - parent.spacing) / 2
                        text: EditorState.preview.pathEditMode ? qsTr("Done editing") : qsTr("Edit points")
                        glyph: Theme.icons.pencil
                        variant: EditorState.preview.pathEditMode ? "primary" : "secondary"
                        onClicked: {
                            if (!EditorState.preview.pathEditMode && root.shapeStyle.kind !== "custom")
                                EditorState.convertSelectionToShape()
                            EditorState.preview.pathEditMode = !EditorState.preview.pathEditMode
                        }
                    }
                    ThemedButton {
                        width: (parent.width - parent.spacing) / 2
                        text: qsTr("Draw with the pen")
                        variant: "secondary"
                        onClicked: EditorState.preview.penMode = true
                    }
                }
                // Close or open every path, and reverse its direction (where Trim Paths starts).
                Row {
                    width: parent.width
                    spacing: 8
                    visible: root.shapeStyle.kind === "custom" && (parent.pathState.contours || []).length > 0
                    readonly property bool allClosed: {
                        const list = parent.pathState.contours || []
                        for (const k of list)
                            if (!k.closed)
                                return false
                        return list.length > 0
                    }
                    function rewrite(change) {
                        const list = JSON.parse(JSON.stringify(parent.pathState.contours || []))
                        for (const k of list)
                            change(k)
                        EditorState.setShapePathPoints(EditorState.selectedTrack, EditorState.selectedClip, list)
                    }
                    ThemedButton {
                        width: (parent.width - parent.spacing) / 2
                        text: parent.allClosed ? qsTr("Open path") : qsTr("Close path")
                        variant: "secondary"
                        onClicked: {
                            const close = !parent.allClosed
                            parent.rewrite(k => { k.closed = close })
                        }
                    }
                    ThemedButton {
                        width: (parent.width - parent.spacing) / 2
                        text: qsTr("Reverse direction")
                        tooltip: qsTr("The path runs the other way: Trim Paths draws it from the other end")
                        variant: "secondary"
                        onClicked: parent.rewrite(k => {
                            k.points.reverse()
                            for (const p of k.points) {
                                const ix = p.ix, iy = p.iy
                                p.ix = p.ox; p.iy = p.oy
                                p.ox = ix; p.oy = iy
                            }
                        })
                    }
                }
                ThemedSwitch {
                    width: parent.width
                    visible: root.shapeStyle.kind === "custom"
                    text: qsTr("Animate the path")
                    tooltip: qsTr("After Effects' Path stopwatch: a key with this outline at the playhead")
                    checked: parent.pathState.animated === true
                    onToggled: EditorState.setShapePathAnimated(EditorState.selectedTrack, EditorState.selectedClip, checked)
                }
                ThemedLabel {
                    width: parent.width
                    visible: parent.pathState.animated === true
                    opacity: 0.8
                    text: parent.pathState.keyHere ? qsTr("Editing the key at the playhead.")
                                                    : qsTr("Moving a point here adds a key at the playhead.")
                }
            }
        }

        // ----- After Effects' shape operators (0.26) ----------------------
        CollapsibleSection {
            visible: root.showShapeSections
            width: parent.width
            title: qsTr("Trim paths")
            expanded: Number(root.shapeStyle.trimStart || 0) > 0 || Number(root.shapeStyle.trimEnd === undefined ? 100 : root.shapeStyle.trimEnd) < 100
                      || Number(root.shapeStyle.trimOffset || 0) !== 0

            Column {
                width: parent.width
                spacing: Theme.spacingMd

                ThemedLabel {
                    width: parent.width
                    opacity: 0.8
                    text: qsTr("Shows only part of the outline: animate Start or End to draw the shape on, and Offset to run it round.")
                }
                Row {
                    width: parent.width
                    spacing: 8
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("trimStart", qsTr("Start"), 1)
                        keyframeList: root.knobKeyframes("trimStart")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: 100
                        unit: "%"
                    }
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("trimEnd", qsTr("End"), 1)
                        keyframeList: root.knobKeyframes("trimEnd")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: 100
                        unit: "%"
                    }
                }
                PropertyKeyframeRow {
                    width: parent.width
                    propDef: root.knob("trimOffset", qsTr("Offset"), 0)
                    keyframeList: root.knobKeyframes("trimOffset")
                    useSlider: true
                    sliderFrom: -360
                    sliderTo: 360
                    inputFrom: -36000
                    inputTo: 36000
                    unit: "°"
                }
            }
        }

        CollapsibleSection {
            visible: root.showShapeSections
            width: parent.width
            title: qsTr("Repeater")
            expanded: Number(root.shapeStyle.repeatCopies || 1) > 1

            Column {
                width: parent.width
                spacing: Theme.spacingMd

                ThemedLabel {
                    width: parent.width
                    opacity: 0.8
                    text: qsTr("Copies of the shape, each one moved, turned and scaled from the one before.")
                }
                Row {
                    width: parent.width
                    spacing: 8
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("repeatCopies", qsTr("Copies"), 0)
                        keyframeList: root.knobKeyframes("repeatCopies")
                        useSlider: true
                        sliderFrom: 1
                        sliderTo: 50
                        inputTo: 200
                    }
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("repeatOffset", qsTr("Offset"), 2)
                        keyframeList: root.knobKeyframes("repeatOffset")
                        useSlider: true
                        sliderFrom: -10
                        sliderTo: 10
                        inputFrom: -200
                        inputTo: 200
                    }
                }
                Row {
                    width: parent.width
                    spacing: 8
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("repeatX", qsTr("Position X"), 0)
                        keyframeList: root.knobKeyframes("repeatX")
                        useSlider: true
                        sliderFrom: -500
                        sliderTo: 500
                        inputFrom: -10000
                        inputTo: 10000
                        unit: "px"
                    }
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("repeatY", qsTr("Position Y"), 0)
                        keyframeList: root.knobKeyframes("repeatY")
                        useSlider: true
                        sliderFrom: -500
                        sliderTo: 500
                        inputFrom: -10000
                        inputTo: 10000
                        unit: "px"
                    }
                }
                Row {
                    width: parent.width
                    spacing: 8
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("repeatScale", qsTr("Scale"), 0)
                        keyframeList: root.knobKeyframes("repeatScale")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: 200
                        inputTo: 1000
                        unit: "%"
                    }
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("repeatRotation", qsTr("Rotation"), 0)
                        keyframeList: root.knobKeyframes("repeatRotation")
                        useSlider: true
                        sliderFrom: -180
                        sliderTo: 180
                        inputFrom: -36000
                        inputTo: 36000
                        unit: "°"
                    }
                }
                Row {
                    width: parent.width
                    spacing: 8
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("repeatStartOpacity", qsTr("Start opacity"), 0)
                        keyframeList: root.knobKeyframes("repeatStartOpacity")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: 100
                        unit: "%"
                    }
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("repeatEndOpacity", qsTr("End opacity"), 0)
                        keyframeList: root.knobKeyframes("repeatEndOpacity")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: 100
                        unit: "%"
                    }
                }
            }
        }

        CollapsibleSection {
            visible: root.showShapeSections
            width: parent.width
            title: qsTr("Wiggle paths")
            expanded: Number(root.shapeStyle.wiggleSize || 0) > 0

            Column {
                width: parent.width
                spacing: Theme.spacingMd

                ThemedLabel {
                    width: parent.width
                    opacity: 0.8
                    text: qsTr("Makes the outline wobble: Size is how far it moves, Detail how often along the edge, and Wiggles per second how fast.")
                }
                Row {
                    width: parent.width
                    spacing: 8
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("wiggleSize", qsTr("Size"), 1)
                        keyframeList: root.knobKeyframes("wiggleSize")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: 100
                        inputTo: 1000
                        unit: "px"
                    }
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("wiggleDetail", qsTr("Detail"), 0)
                        keyframeList: root.knobKeyframes("wiggleDetail")
                        useSlider: true
                        sliderFrom: 2
                        sliderTo: 200
                        inputTo: 500
                        unit: "px"
                    }
                }
                Row {
                    width: parent.width
                    spacing: 8
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("wiggleSpeed", qsTr("Wiggles per second"), 1)
                        keyframeList: root.knobKeyframes("wiggleSpeed")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: 10
                        inputTo: 30
                    }
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("wiggleSeed", qsTr("Random seed"), 0)
                        keyframeList: root.knobKeyframes("wiggleSeed")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: 100
                        inputTo: 1000
                    }
                }
            }
        }
        // ----- Several shapes in one layer, Merge / Offset / Zig zag / Twist (0.26, stage G) --------
        CollapsibleSection {
            visible: root.showShapeSections && !root.proMode && !root.hasParts
            width: parent.width
            title: qsTr("Shapes in this layer")
            expanded: Number(root.shapeStyle.mergeMode || 0) > 0

            Column {
                width: parent.width
                spacing: Theme.spacingMd

                ThemedLabel {
                    width: parent.width
                    opacity: 0.8
                    text: qsTr("Add more shapes to the same layer, then choose how they combine (Merge paths).")
                }
                Flow {
                    width: parent.width
                    spacing: Theme.spacingSm
                    Repeater {
                        model: [
                            { id: "rectangle", label: qsTr("+ Rectangle") },
                            { id: "ellipse", label: qsTr("+ Ellipse") },
                            { id: "star", label: qsTr("+ Star") },
                            { id: "polygon", label: qsTr("+ Polygon") }
                        ]
                        ThemedButton {
                            required property var modelData
                            text: modelData.label
                            variant: "secondary"
                            onClicked: EditorState.addShapeToLayer(EditorState.selectedTrack, EditorState.selectedClip, modelData.id)
                        }
                    }
                }
                ThemedLabel { text: qsTr("Merge paths") }
                ThemedComboBox {
                    width: parent.width
                    model: [qsTr("Off"), qsTr("Add"), qsTr("Subtract"), qsTr("Intersect"), qsTr("Exclude intersections")]
                    currentIndex: Math.round(Number(root.shapeStyle.mergeMode || 0))
                    onActivated: index => root.setShapeKey("mergeMode", index)
                }
            }
        }

        CollapsibleSection {
            visible: root.showShapeSections
            width: parent.width
            title: qsTr("Offset, pucker, zig zag and twist")
            expanded: Number(root.shapeStyle.offsetPath || 0) !== 0 || Number(root.shapeStyle.zigzagSize || 0) > 0
                      || Number(root.shapeStyle.twistAngle || 0) !== 0 || Number(root.shapeStyle.puckerBloat || 0) !== 0

            Column {
                width: parent.width
                spacing: Theme.spacingMd

                PropertyKeyframeRow {
                    width: parent.width
                    propDef: root.knob("offsetPath", qsTr("Offset paths"), 0)
                    keyframeList: root.knobKeyframes("offsetPath")
                    useSlider: true
                    sliderFrom: -100
                    sliderTo: 100
                    inputFrom: -500
                    inputTo: 500
                    unit: "px"
                }
                PropertyKeyframeRow {
                    width: parent.width
                    propDef: root.knob("puckerBloat", qsTr("Pucker & Bloat"), 0)
                    keyframeList: root.knobKeyframes("puckerBloat")
                    useSlider: true
                    sliderFrom: -100
                    sliderTo: 100
                    inputFrom: -100
                    inputTo: 100
                    unit: "%"
                }
                Row {
                    width: parent.width
                    spacing: 8
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("zigzagSize", qsTr("Zig zag size"), 0)
                        keyframeList: root.knobKeyframes("zigzagSize")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: 100
                        inputTo: 500
                        unit: "px"
                    }
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.knob("zigzagRidges", qsTr("Ridges"), 0)
                        keyframeList: root.knobKeyframes("zigzagRidges")
                        useSlider: true
                        sliderFrom: 1
                        sliderTo: 60
                        inputTo: 200
                    }
                }
                ThemedSwitch {
                    width: parent.width
                    text: qsTr("Smooth zig zag")
                    checked: Number(root.shapeStyle.zigzagSmooth || 0) >= 0.5
                    onToggled: root.setShapeKey("zigzagSmooth", checked ? 1 : 0)
                }
                PropertyKeyframeRow {
                    width: parent.width
                    propDef: root.knob("twistAngle", qsTr("Twist"), 0)
                    keyframeList: root.knobKeyframes("twistAngle")
                    useSlider: true
                    sliderFrom: -360
                    sliderTo: 360
                    inputFrom: -3600
                    inputTo: 3600
                    unit: "°"
                }
            }
        }
    }
}
