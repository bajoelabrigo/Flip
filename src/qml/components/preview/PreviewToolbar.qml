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
        if (d.safeZones === true)
            EditorState.preview.safeZones = true
    }
    Connections {
        target: EditorState.preview
        function onToolChanged() {
            EditorState.preferences.setEditorDefault("toolFill", EditorState.preview.toolFill)
            EditorState.preferences.setEditorDefault("toolStroke", EditorState.preview.toolStroke)
            EditorState.preferences.setEditorDefault("toolStrokeWidth", EditorState.preview.toolStrokeWidth)
        }
    }
    color: Theme.panelBackground

    component ToolButton: IconButton {
        property string toolId: ""
        property string shortcutId: ""
        property string label: ""
        Layout.alignment: Qt.AlignVCenter
        active: toolId.length > 0 && root.tool === toolId
        tooltip: label + root.keys(shortcutId)
        onClicked: root.pick(toolId)
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

            ThemedLabel { anchors.verticalCenter: parent.verticalCenter; text: qsTr("Fill"); size: "sm" }
            Rectangle {
                width: 22
                height: 16
                anchors.verticalCenter: parent.verticalCenter
                radius: 2
                color: EditorState.preview.toolFill === "none" ? "transparent" : EditorState.preview.toolFill
                border.width: 1
                border.color: Theme.border
                Rectangle {
                    visible: EditorState.preview.toolFill === "none"
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
                        if (mouse.button === Qt.RightButton)
                            EditorState.preview.toolFill = EditorState.preview.toolFill === "none" ? "#ffff4d6d" : "none"
                        else
                            colorDialog.openFor("fill")
                    }
                }
            }
            ThemedLabel { anchors.verticalCenter: parent.verticalCenter; text: qsTr("Stroke"); size: "sm" }
            Rectangle {
                width: 22
                height: 16
                anchors.verticalCenter: parent.verticalCenter
                radius: 2
                color: "transparent"
                border.width: 4
                border.color: EditorState.preview.toolStroke === "none" ? Theme.border : EditorState.preview.toolStroke
                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.LeftButton | Qt.RightButton
                    cursorShape: Qt.PointingHandCursor
                    onClicked: mouse => {
                        if (mouse.button === Qt.RightButton)
                            EditorState.preview.toolStroke = EditorState.preview.toolStroke === "none" ? "#ffffffff" : "none"
                        else
                            colorDialog.openFor("stroke")
                    }
                }
            }
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

    ThemedColorDialog {
        id: colorDialog
        property string target: "fill"
        function openFor(which) {
            target = which
            const c = which === "fill" ? EditorState.preview.toolFill : EditorState.preview.toolStroke
            selectedColor = c === "none" ? "#ffffff" : c
            open()
        }
        onAccepted: {
            const c = String(selectedColor)
            if (target === "fill")
                EditorState.preview.toolFill = c
            else
                EditorState.preview.toolStroke = c
        }
    }
}
