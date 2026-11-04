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
        { id: "roundedRectangle", label: qsTr("Rounded rectangle"), glyph: "square-rounded" },
        { id: "ellipse", label: qsTr("Ellipse"), glyph: "circle" },
        { id: "star", label: qsTr("Star"), glyph: "star" },
        { id: "polygon", label: qsTr("Polygon"), glyph: "hexagon" },
        { id: "line", label: qsTr("Line"), glyph: "slash" }
    ]
    readonly property var currentShape: {
        for (const k of shapeKinds) {
            if (k.id === EditorState.preview.shapeToolKind && k.id !== "ellipse" && k.id !== "line")
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
        if (!root.pickedStyled())
            return null
        const style = data.kind === "shape" ? data.shapeStyle : data.textStyle
        const layers = (style && style.layers) || []
        for (let i = 0; i < layers.length; ++i) {
            if (layers[i].kind === which)
                return layers[i]
        }
        return null
    }
    // The paint edits the picked clip when it is a shape, or a text while no drawing tool is on; with
    // the shape or pen tool and a text picked, it is the tool's paint, as in After Effects.
    function pickedStyled() {
        const data = EditorState.selectedClipData
        return !!data && EditorState.selectedClip >= 0
               && (data.kind === "shape" || (data.kind === "text" && !root.paintOptions))
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
            // Alt+click (After Effects): the next kind, None, Solid, Linear, Radial, without the window.
            onClicked: mouse => {
                if (mouse.modifiers & Qt.AltModifier)
                    fillOptions.cycle(paintLabel.which, !root.pickedStyled())
                else
                    fillOptions.openFor(paintLabel.which, !root.pickedStyled())
            }
        }
        ThemedToolTip {
            visible: labelMouse.containsMouse
            text: paintLabel.which === "fill"
                  ? qsTr("Fill Options: none, solid, linear or radial gradient, blend mode and opacity. Alt+click: the next kind")
                  : qsTr("Stroke Options: none, solid, linear or radial gradient, blend mode and opacity. Alt+click: the next kind")
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
        ThemedToolTip {
            visible: swatchMouse.containsMouse
            text: swatch.which === "fill" ? qsTr("Fill colour. Right-click: no fill (or back on)")
                                          : qsTr("Stroke colour. Right-click: no stroke (or back on)")
        }
        MouseArea {
            id: swatchMouse
            anchors.fill: parent
            hoverEnabled: true
            acceptedButtons: Qt.LeftButton | Qt.RightButton
            cursorShape: Qt.PointingHandCursor
            onClicked: mouse => {
                const layer = root.pickedLayer(swatch.which)
                if (mouse.button === Qt.RightButton) {
                    if (layer) {
                        EditorState.setStyleLayer(EditorState.selectedTrack, EditorState.selectedClip, layer.id,
                                                  { "enabled": layer.enabled === false })
                        if (root.paintOptions && swatch.which === "stroke")
                            EditorState.preview.toolStroke = layer.enabled === false ? "#ffffffff" : "none"
                        else if (root.paintOptions)
                            EditorState.preview.toolFill = layer.enabled === false ? "#ffff4d6d" : "none"
                    } else if (root.pickedStyled()) {
                        fillOptions.openFor(swatch.which, !root.pickedStyled())
                    } else if (swatch.which === "fill") {
                        EditorState.preview.toolFill = EditorState.preview.toolFill === "none" ? "#ffff4d6d" : "none"
                    } else {
                        EditorState.preview.toolStroke = EditorState.preview.toolStroke === "none" ? "#ffffffff" : "none"
                    }
                    return
                }
                // A gradient, or a picked clip with no such layer yet: the options; else the colour.
                // (Right-click: none, as the label's options; bounce exercise #1 looked for it here.)
                if (swatch.isGradient || (root.pickedStyled() && !layer))
                    fillOptions.openFor(swatch.which, !root.pickedStyled())
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
            label: qsTr("Shape: drag on the preview (Shift for a square or circle). Alt+click: the next shape; double-click: one the size of the frame") + " · " + root.currentShape.label
            glyph: root.currentShape.glyph
            // After Effects' Alt+click on the shape tool (0.30): the next shape, Rectangle, Rounded Rectangle,
            // Ellipse, Polygon, Star.
            function cycleKind() {
                const order = ["rectangle", "roundedRectangle", "ellipse", "polygon", "star"]
                const at = order.indexOf(EditorState.preview.shapeToolKind)
                EditorState.preview.shapeToolKind = order[(at + 1) % order.length]
                root.pick("shape")
            }
            // A double-click makes the shape the size of the frame (After Effects' double-click on the tool).
            // Also told by two clicks close together: the button does not always get the double-click itself.
            property real lastClickMs: 0
            property real lastFrameShapeMs: 0
            onDoubleClicked: frameShape()
            function frameShape() {
                menuTimer.stop()
                const now = Date.now()
                if (now - lastFrameShapeMs < 600)
                    return
                lastFrameShapeMs = now
                lastClickMs = 0
                const w = EditorState.projectFile.projectWidth()
                const h = EditorState.projectFile.projectHeight()
                if (w > 0 && h > 0)
                    EditorState.addDrawnShape(EditorState.preview.shapeToolKind === "line" ? "rectangle"
                                                                                             : EditorState.preview.shapeToolKind,
                                              0, 0, w, h, EditorState.preview.toolFill, EditorState.preview.toolStroke,
                                              EditorState.preview.toolStrokeWidth)
            }
            Timer {
                id: menuTimer
                interval: Qt.styleHints.mouseDoubleClickInterval
                onTriggered: shapeMenu.popup(shapeButton, 0, shapeButton.height)
            }
            onClicked: {
                if (EditorState.keyboardModifiers() & Qt.AltModifier) {
                    shapeButton.cycleKind()
                    return
                }
                const now = Date.now()
                if (now - lastClickMs < Qt.styleHints.mouseDoubleClickInterval) {
                    frameShape()
                    return
                }
                lastClickMs = now
                // Ellipse and Line have buttons of their own (0.29): coming from them, this one is the
                // rectangle again (it kept the line, and a drag meant for a label drew a line).
                const k = EditorState.preview.shapeToolKind
                if (k === "ellipse" || k === "line") {
                    EditorState.preview.shapeToolKind = "rectangle"
                    root.pick("shape")
                    return
                }
                // A second click on the active tool, as AE's long press, offers the other shapes.
                if (root.tool === "shape")
                    menuTimer.restart()
                else
                    root.pick("shape")
            }
            active: root.tool === "shape" && EditorState.preview.shapeToolKind !== "ellipse"
                    && EditorState.preview.shapeToolKind !== "line"
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
        // After Effects' «Tool creates shape / mask» (0.30): with a layer picked, the shape tool can draw a mask on it.
        IconButton {
            Layout.alignment: Qt.AlignVCenter
            visible: root.tool === "shape" && EditorState.selectedClip >= 0
            glyph: "square-dashed"
            active: EditorState.preview.shapeToolMask
            tooltip: EditorState.preview.shapeToolMask
                     ? qsTr("The shape tool draws a mask on the picked layer. Click: draw shapes again")
                     : qsTr("The shape tool draws shapes. Click: draw a mask on the picked layer instead")
            onClicked: EditorState.preview.shapeToolMask = !EditorState.preview.shapeToolMask
        }
        // Ellipse and Line one click away (0.29), not only behind the shape button's second click.
        IconButton {
            Layout.alignment: Qt.AlignVCenter
            glyph: "circle"
            active: root.tool === "shape" && EditorState.preview.shapeToolKind === "ellipse"
            tooltip: qsTr("Ellipse: drag on the preview (Shift for a circle)")
            onClicked: {
                EditorState.preview.shapeToolKind = "ellipse"
                root.pick("shape")
            }
        }
        IconButton {
            Layout.alignment: Qt.AlignVCenter
            glyph: "slash"
            active: root.tool === "shape" && EditorState.preview.shapeToolKind === "line"
            tooltip: qsTr("Line: drag on the preview (Shift for 0°, 45° or 90°); it takes the stroke colour and width")
            onClicked: {
                EditorState.preview.shapeToolKind = "line"
                root.pick("shape")
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

        // The tool's options, as AE's right side of the Tools panel; with the Selection tool, the picked
        // shape's own fill, stroke and width (0.29), as AE shows them with any tool.
        Row {
            Layout.alignment: Qt.AlignVCenter
            spacing: Theme.spacingSm
            visible: root.paintOptions || (root.tool === "select" && root.pickedStyled()
                                           && EditorState.selectedClipData.kind === "shape")

            PaintLabel { which: "fill"; text: qsTr("Fill") }
            PaintSwatch { which: "fill" }
            PaintLabel { which: "stroke"; text: qsTr("Stroke") }
            PaintSwatch { which: "stroke" }
            ThemedNumberField {
                id: strokeWidthField
                readonly property var pickedStroke: { void EditorState.selectedClipData; return root.pickedLayer("stroke") }
                width: 64
                anchors.verticalCenter: parent.verticalCenter
                from: 0
                to: 200
                unit: "px"
                value: pickedStroke ? (pickedStroke.width || 0) : EditorState.preview.toolStrokeWidth
                onEdited: v => {
                    if (pickedStroke)
                        EditorState.setStyleLayer(EditorState.selectedTrack, EditorState.selectedClip, pickedStroke.id,
                                                  { "enabled": v > 0, "width": v })
                    // With a drawing tool on, the next shapes take the width too (0.30): a 0 typed with a
                    // shape picked left the new ones with the old stroke (bounce exercise #2).
                    if (!pickedStroke || root.paintOptions)
                        EditorState.preview.toolStrokeWidth = v
                }
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
                // With a drawing tool on, the next shapes take it too (0.30, as After Effects).
                if (!root.paintOptions)
                    return
            }
            if (target === "fill")
                EditorState.preview.toolFill = c
            else
                EditorState.preview.toolStroke = c
        }
    }
}
