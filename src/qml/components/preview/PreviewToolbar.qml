import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import Drift
import ".."

// After Effects' Tools panel over the preview (0.26): selection, hand, zoom, anchor point, shapes,
// pen, text, roto and the 3D camera, with the options of the tool in use on the right (fill and
// stroke for shapes and the pen). The tool lives in EditorState.preview.tool.
Rectangle {
    id: root

    readonly property string tool: EditorState.preview.tool
    readonly property var shapeKinds: [
        { id: "rectangle", label: qsTr("Rectangle"), glyph: Theme.icons.square },
        { id: "ellipse", label: qsTr("Ellipse"), glyph: "circle" },
        { id: "star", label: qsTr("Star"), glyph: "star" },
        { id: "polygon", label: qsTr("Polygon"), glyph: "hexagon" }
    ]
    readonly property var currentShape: {
        for (const k of shapeKinds) {
            if (k.id === EditorState.preview.shapeToolKind)
                return k
        }
        return shapeKinds[0]
    }
    readonly property bool paintOptions: tool === "shape" || tool === "pen"

    function keys(id) {
        const k = Theme.shortcutDisplay(EditorState.shortcutFor(id))
        return k && k.length > 0 ? "  (" + k + ")" : ""
    }
    function pick(tool) {
        EditorState.preview.tool = tool
    }

    implicitHeight: 34

    // The toolbar's paints and the safe zones are remembered between sessions (Preferences, 0.26).
    Component.onCompleted: {
        const d = EditorState.preferences.editorDefaults
        EditorState.preview.toolFill = d.toolFill
        EditorState.preview.toolStroke = d.toolStroke
        EditorState.preview.toolStrokeWidth = Number(d.toolStrokeWidth)
        EditorState.preview.toolFillOptions = d.toolFillOptions || {}
        EditorState.preview.toolStrokeOptions = d.toolStrokeOptions || {}
        if (d.safeZones === true)
            EditorState.preview.safeZones = true
    }
    Connections {
        target: EditorState.preview
        function onToolChanged() {
            EditorState.preferences.setEditorDefault("toolFill", EditorState.preview.toolFill)
            EditorState.preferences.setEditorDefault("toolStroke", EditorState.preview.toolStroke)
            EditorState.preferences.setEditorDefault("toolStrokeWidth", EditorState.preview.toolStrokeWidth)
            EditorState.preferences.setEditorDefault("toolFillOptions", EditorState.preview.toolFillOptions)
            EditorState.preferences.setEditorDefault("toolStrokeOptions", EditorState.preview.toolStrokeOptions)
        }
    }
    color: Theme.panelBackground

    // The paint the swatches show and edit (0.29, as After Effects' tools bar): a picked shape's or
    // text's own Fill / Stroke layer, else the paint new shapes are drawn with.
    function pickedLayer(which) {
        const data = EditorState.selectedClipData
        if (!data || EditorState.selectedClip < 0 || (data.kind !== "shape" && data.kind !== "text"))
            return null
        const style = data.kind === "shape" ? data.shapeStyle : data.textStyle
        const layers = (style && style.layers) || []
        for (let i = 0; i < layers.length; ++i) {
            if (layers[i].kind === which)
                return layers[i]
        }
        return null
    }
    function pickedStyled() {
        const data = EditorState.selectedClipData
        return !!data && EditorState.selectedClip >= 0 && (data.kind === "shape" || data.kind === "text")
    }
    function paintOf(which) {
        if (root.pickedStyled()) {
            const layer = root.pickedLayer(which)
            if (!layer || layer.enabled === false)
                return { "kind": "none" }
            return layer.paint || { "kind": "solid" }
        }
        const color = which === "fill" ? EditorState.preview.toolFill : EditorState.preview.toolStroke
        if (color === "none")
            return { "kind": "none" }
        const options = (which === "fill" ? EditorState.preview.toolFillOptions
                                          : EditorState.preview.toolStrokeOptions) || {}
        return Object.assign({ "kind": "solid", "color": color }, options.paint || {})
    }
    function qtColor(hex) {
        const h = String(hex || "").replace("#", "")
        if (h.length === 8)
            return Qt.rgba(parseInt(h.substr(2, 2), 16) / 255, parseInt(h.substr(4, 2), 16) / 255,
                           parseInt(h.substr(6, 2), 16) / 255, parseInt(h.substr(0, 2), 16) / 255)
        return String(hex || "white")
    }

    // Clicking the word opens Fill / Stroke Options, as After Effects.
    component PaintLabel: ThemedLabel {
        id: paintLabel
        property string which: "fill"
        anchors.verticalCenter: parent.verticalCenter
        size: "sm"
        font.underline: labelMouse.containsMouse
        MouseArea {
            id: labelMouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: fillOptions.openFor(paintLabel.which)
        }
        ThemedToolTip {
            visible: labelMouse.containsMouse
            text: paintLabel.which === "fill"
                  ? qsTr("Fill Options: none, solid, linear or radial gradient, blend mode and opacity")
                  : qsTr("Stroke Options: none, solid, linear or radial gradient, blend mode and opacity")
        }
    }

    // The swatch: a click picks the colour of a solid paint (a gradient opens its options);
    // right-click switches the paint off and on.
    component PaintSwatch: Rectangle {
        id: swatch
        property string which: "fill"
        readonly property var paint: {
            void EditorState.tracksRevision
            void EditorState.selectedClipData
            void EditorState.preview.toolFillOptions
            void EditorState.preview.toolStrokeOptions
            return root.paintOf(which)
        }
        readonly property bool none: paint.kind === "none"
        readonly property bool isGradient: paint.kind === "gradient"
        readonly property var stops: (isGradient && paint.gradient && paint.gradient.stops) || []
        width: 22
        height: 16
        anchors.verticalCenter: parent.verticalCenter
        radius: 2
        color: none || which === "stroke" ? "transparent" : root.qtColor(paint.color)
        border.width: which === "stroke" ? 4 : 1
        border.color: which === "stroke" && !none && !isGradient ? root.qtColor(paint.color) : Theme.border
        Rectangle {
            visible: swatch.isGradient
            anchors.fill: parent
            anchors.margins: swatch.which === "stroke" ? 0 : 1
            radius: 2
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: swatch.stops.length > 0 ? root.qtColor(swatch.stops[0].color) : "white" }
                GradientStop { position: 1.0; color: swatch.stops.length > 0 ? root.qtColor(swatch.stops[swatch.stops.length - 1].color) : "black" }
            }
            // A stroke shows the gradient only on its edge.
            Rectangle {
                visible: swatch.which === "stroke"
                anchors.fill: parent
                anchors.margins: 4
                color: Theme.panelBackground
            }
        }
        Rectangle {
            visible: swatch.none
            anchors.centerIn: parent
            width: parent.width * 1.1
            height: 1.5
            rotation: -35
            color: "#e04040"
        }
        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.LeftButton | Qt.RightButton
            cursorShape: Qt.PointingHandCursor
            onClicked: mouse => {
                const layer = root.pickedLayer(swatch.which)
                if (mouse.button === Qt.RightButton) {
                    if (layer) {
                        EditorState.setStyleLayer(EditorState.selectedTrack, EditorState.selectedClip, layer.id,
                                                  { "enabled": layer.enabled === false })
                    } else if (root.pickedStyled()) {
                        fillOptions.openFor(swatch.which)
                    } else if (swatch.which === "fill") {
                        EditorState.preview.toolFill = EditorState.preview.toolFill === "none" ? "#ffff4d6d" : "none"
                    } else {
                        EditorState.preview.toolStroke = EditorState.preview.toolStroke === "none" ? "#ffffffff" : "none"
                    }
                    return
                }
                // A gradient, or a picked clip with no such layer yet: the options; else the colour.
                if (swatch.isGradient || (root.pickedStyled() && !layer))
                    fillOptions.openFor(swatch.which)
                else
                    colorDialog.openFor(swatch.which)
            }
        }
    }

    component ToolButton: IconButton {
        property string toolId: ""
        property string shortcutId: ""
        property string label: ""
        Layout.alignment: Qt.AlignVCenter
        active: toolId.length > 0 && root.tool === toolId
        tooltip: label + root.keys(shortcutId)
        // The shape button handles its own click (a second one opens the shape list): picking here as
        // well made the first click already count as the second.
        onClicked: if (toolId !== "shape") root.pick(toolId)
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: Theme.spacingMd
        anchors.rightMargin: Theme.spacingMd
        spacing: 2

        ToolButton { toolId: "select"; shortcutId: "selectTool"; label: qsTr("Selection"); glyph: Theme.icons.mousePointer }
        ToolButton { toolId: "hand"; shortcutId: "previewHandTool"; label: qsTr("Hand: drag to move the view"); glyph: "hand" }
        ToolButton { toolId: "zoom"; shortcutId: "previewZoomTool"; label: qsTr("Zoom: click to zoom in, Alt+click to zoom out"); glyph: Theme.icons.search }
        // After Effects' Region of Interest (0.26): only that part of the frame is drawn.
        ToolButton { toolId: "roi"; label: qsTr("Region of interest: drag the part of the frame to preview; the rest is not drawn, so it plays faster"); glyph: Theme.icons.crop }
        IconButton {
            Layout.alignment: Qt.AlignVCenter
            visible: EditorState.playback.regionOfInterest.width > 0
            glyph: Theme.icons.x
            tooltip: qsTr("Reset the region of interest")
            onClicked: EditorState.playback.regionOfInterest = Qt.rect(0, 0, 0, 0)
        }

        Rectangle { Layout.preferredWidth: 1; Layout.preferredHeight: 18; color: Theme.border }

        ToolButton { toolId: "anchor"; shortcutId: "previewAnchorTool"; label: qsTr("Anchor point: drag it without moving the layer"); glyph: Theme.icons.locateFixed }

        Rectangle { Layout.preferredWidth: 1; Layout.preferredHeight: 18; color: Theme.border }

        ToolButton {
            id: shapeButton
            toolId: "shape"
            shortcutId: "previewShapeTool"
            label: qsTr("Shape: drag on the preview (Shift for a square or circle)") + " · " + root.currentShape.label
            glyph: root.currentShape.glyph
            onClicked: {
                // A second click on the active tool, as AE's long press, offers the other shapes.
                if (root.tool === "shape")
                    shapeMenu.popup(shapeButton, 0, shapeButton.height)
                else
                    root.pick("shape")
            }
            ThemedContextMenu {
                id: shapeMenu
                Instantiator {
                    model: root.shapeKinds
                    delegate: ThemedMenuItem {
                        required property var modelData
                        text: modelData.label
                        icon.name: EditorState.preview.shapeToolKind === modelData.id ? Theme.icons.check : ""
                        onTriggered: {
                            EditorState.preview.shapeToolKind = modelData.id
                            root.pick("shape")
                        }
                    }
                    onObjectAdded: (index, object) => shapeMenu.insertItem(index, object)
                    onObjectRemoved: (index, object) => shapeMenu.removeItem(object)
                }
            }
        }
        ToolButton { toolId: "pen"; shortcutId: "previewPenTool"; label: qsTr("Pen: click for corners, drag for curves"); glyph: Theme.icons.pencil }
        ToolButton { toolId: "text"; shortcutId: "previewTextTool"; label: qsTr("Text: click on the preview and type"); glyph: Theme.icons.type }
        // After Effects' Motion Sketch (0.26).
        // After Effects' Puppet pin tool (0.26).
        ToolButton { toolId: "puppet"; label: qsTr("Puppet pins: click on the selected layer to pin it, drag a pin to bend it (each move is a keyframe)"); glyph: "map-pin" }
        ToolButton { toolId: "sketch"; label: qsTr("Motion sketch: drag the selected layer and the path becomes its Position keys, in real time"); glyph: "spline" }

        Rectangle { Layout.preferredWidth: 1; Layout.preferredHeight: 18; color: Theme.border }

        IconButton {
            Layout.alignment: Qt.AlignVCenter
            glyph: "eraser"
            tooltip: qsTr("Roto: cut the person or object out of the selected video")
            enabled: !!EditorState.selectedClipData && EditorState.selectedClipData.kind === "video"
            onClicked: EditorState.preview.openInspectorPage("video", "fondo")
        }
        IconButton {
            Layout.alignment: Qt.AlignVCenter
            glyph: Theme.icons.box
            active: EditorState.preview.mode === "3d"
            tooltip: qsTr("3D camera: orbit, move and zoom the view") + root.keys("previewCameraTool")
            onClicked: EditorState.preview.mode = EditorState.preview.mode === "3d" ? "2d" : "3d"
        }

        Item { Layout.fillWidth: true }

        // The tool's options, as AE's right side of the Tools panel.
        Row {
            Layout.alignment: Qt.AlignVCenter
            spacing: Theme.spacingSm
            visible: root.paintOptions

            PaintLabel { which: "fill"; text: qsTr("Fill") }
            PaintSwatch { which: "fill" }
            PaintLabel { which: "stroke"; text: qsTr("Stroke") }
            PaintSwatch { which: "stroke" }
            ThemedNumberField {
                width: 64
                anchors.verticalCenter: parent.verticalCenter
                from: 0
                to: 200
                unit: "px"
                value: EditorState.preview.toolStrokeWidth
                onEdited: v => EditorState.preview.toolStrokeWidth = v
            }
            ThemedLabel { anchors.verticalCenter: parent.verticalCenter; text: "px"; size: "sm"; opacity: 0.7 }
        }
    }

    FillOptionsDialog {
        id: fillOptions
    }

    ThemedColorDialog {
        id: colorDialog
        property string target: "fill"
        property string layerId: ""
        function openFor(which) {
            target = which
            const layer = root.pickedLayer(which)
            layerId = layer ? layer.id : ""
            const c = layer ? ((layer.paint && layer.paint.color) || "#ffffffff")
                            : which === "fill" ? EditorState.preview.toolFill : EditorState.preview.toolStroke
            selectedColor = c === "none" ? "#ffffff" : root.qtColor(c)
            open()
        }
        onAccepted: {
            const c = String(selectedColor)
            if (layerId.length > 0) {
                EditorState.setStyleLayer(EditorState.selectedTrack, EditorState.selectedClip, layerId,
                                          { "enabled": true, "paint": { "kind": "solid", "color": c } })
                return
            }
            if (target === "fill")
                EditorState.preview.toolFill = c
            else
                EditorState.preview.toolStroke = c
        }
    }
}
