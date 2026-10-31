import QtQuick
import Drift
import ".."

// After Effects' Contents (0.28) as a list like Photoshop's layers: the shape layer on top, then
// its parts (the first one is drawn on top), groups folding open. A click picks what the rest of
// the inspector edits; the same pick shows in the timeline and the preview. Pro only.
Column {
    id: list

    // The selected clip's data (ShapeInspector's), for its name and to refresh the rows.
    property var clipData: ({})
    property int revision: 0

    readonly property int trackIndex: EditorState.selectedTrack
    readonly property int clipIndex: EditorState.selectedClip
    readonly property string focusedPart: {
        void list.revision
        return EditorState.selectedShapePart
    }
    readonly property var rows: {
        void list.revision
        return EditorState.shapePartRows(list.trackIndex, list.clipIndex)
    }
    readonly property bool hasParts: rows.length > 0
    readonly property var focusedRow: {
        for (let i = 0; i < rows.length; ++i) {
            if (rows[i].id === list.focusedPart)
                return rows[i]
        }
        return null
    }
    // Drag to reorder: the row being dragged, and where it would land.
    property string dragId: ""
    property string dropTargetId: ""
    property string dropWhere: ""

    function pick(id) {
        EditorState.selectShapePart(list.trackIndex, list.clipIndex, id)
        list.forceActiveFocus()
    }
    function add(kind) {
        EditorState.addShapePart(list.trackIndex, list.clipIndex, kind)
    }
    function removeFocused() {
        if (list.focusedPart.length > 0)
            EditorState.removeShapePart(list.trackIndex, list.clipIndex, list.focusedPart)
    }
    function duplicateFocused() {
        if (list.focusedPart.length > 0)
            EditorState.duplicateShapePart(list.trackIndex, list.clipIndex, list.focusedPart)
    }
    function groupFocused() {
        if (list.focusedPart.length > 0)
            EditorState.groupShapePart(list.trackIndex, list.clipIndex, list.focusedPart)
    }

    width: parent ? parent.width : 280
    spacing: 4
    activeFocusOnTab: true

    // As After Effects: Delete removes the picked part, Ctrl+D duplicates it, Ctrl+G groups it,
    // F2 renames it.
    Keys.onPressed: event => {
        if (list.focusedPart.length === 0)
            return
        if (event.key === Qt.Key_Delete || event.key === Qt.Key_Backspace) {
            list.removeFocused()
            event.accepted = true
        } else if (event.key === Qt.Key_D && (event.modifiers & Qt.ControlModifier)) {
            list.duplicateFocused()
            event.accepted = true
        } else if (event.key === Qt.Key_G && (event.modifiers & Qt.ControlModifier)) {
            if (event.modifiers & Qt.ShiftModifier) {
                if (list.focusedRow && list.focusedRow.group)
                    EditorState.ungroupShapePart(list.trackIndex, list.clipIndex, list.focusedPart)
            } else {
                list.groupFocused()
            }
            event.accepted = true
        } else if (event.key === Qt.Key_F2) {
            list.renameRequested(list.focusedPart)
            event.accepted = true
        }
    }
    signal renameRequested(string partId)

    Connections {
        target: EditorState
        function onSelectedShapePartChanged() { list.revision++ }
        function onSelectedClipDataChanged() { list.revision++ }
        function onTracksChanged() { list.revision++ }
        function onSelectionChanged() { list.revision++ }
    }

    // ----- Title and «+ Add» ---------------------------------------------------------------
    Row {
        width: parent.width
        spacing: Theme.spacingSm

        Text {
            width: parent.width - addButton.width - parent.spacing
            anchors.verticalCenter: parent.verticalCenter
            text: qsTr("Contents")
            color: Theme.panelForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSm
            font.weight: Font.DemiBold
        }
        ThemedButton {
            id: addButton
            variant: "secondary"
            glyph: Theme.icons.plus
            text: qsTr("Add")
            tooltip: qsTr("Add a shape or a group to this layer (After Effects: Add)")
            // Under the button, not wherever the pointer is.
            onClicked: addMenu.popup(addButton, 0, addButton.height)

            ThemedContextMenu {
                id: addMenu
                ThemedMenuItem { text: qsTr("Rectangle"); onTriggered: list.add("rectangle") }
                ThemedMenuItem { text: qsTr("Ellipse"); onTriggered: list.add("ellipse") }
                ThemedMenuItem { text: qsTr("Star"); onTriggered: list.add("star") }
                ThemedMenuItem { text: qsTr("Polygon"); onTriggered: list.add("polygon") }
                ThemedMenuSeparator { }
                ThemedMenuItem { text: qsTr("Empty group"); onTriggered: list.add("group") }
            }
        }
    }

    Text {
        width: parent.width
        wrapMode: Text.WordWrap
        visible: !list.hasParts
        text: qsTr("This layer is one shape. Add another one to build it from parts: each part has its own fill, border and position.")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }

    // ----- The layer itself --------------------------------------------------------------------
    Rectangle {
        width: parent.width
        height: 28
        radius: Theme.radiusSm
        color: list.focusedPart.length === 0 ? Theme.panelAccent : (layerHover.hovered ? Theme.popoverHover : "transparent")

        Row {
            anchors.fill: parent
            anchors.leftMargin: 6
            spacing: 6
            IconGlyph {
                anchors.verticalCenter: parent.verticalCenter
                glyph: Theme.icons.layers
                iconSize: 13
                iconColor: Theme.panelForeground
            }
            Text {
                anchors.verticalCenter: parent.verticalCenter
                width: parent.width - 40
                elide: Text.ElideRight
                text: (list.clipData && list.clipData.name) || qsTr("Shape layer")
                color: Theme.panelForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                font.weight: Font.DemiBold
            }
        }
        HoverHandler { id: layerHover }
        MouseArea {
            anchors.fill: parent
            onClicked: list.pick("")
        }
        ThemedToolTip {
            visible: layerHover.hovered
            text: qsTr("The whole layer. Its position and size are in the Transform tab.")
        }
    }

    // ----- The parts ---------------------------------------------------------------------------
    Repeater {
        model: list.rows.length
        delegate: Rectangle {
            id: partRow
            required property int index
            readonly property var rowData: list.rows[index] || ({})
            readonly property string partId: rowData.id || ""
            readonly property bool picked: partId === list.focusedPart
            readonly property bool dropHere: list.dragId.length > 0 && list.dropTargetId === partId
            property bool renaming: false

            width: list.width
            height: 28
            radius: Theme.radiusSm
            color: picked ? Theme.panelAccent : (rowHover.hovered ? Theme.popoverHover : "transparent")
            border.width: dropHere && list.dropWhere === "inside" ? 1 : 0
            border.color: Theme.accent

            Connections {
                target: list
                function onRenameRequested(partId) {
                    if (partId === partRow.partId)
                        partRow.renaming = true
                }
            }

            // Where a dragged part would go: a line above or below this row.
            Rectangle {
                visible: partRow.dropHere && list.dropWhere !== "inside"
                width: parent.width
                height: 2
                color: Theme.accent
                y: list.dropWhere === "before" ? 0 : parent.height - 2
                z: 2
            }

            Row {
                anchors.fill: parent
                anchors.leftMargin: 6 + 16 * ((partRow.rowData.depth || 0) + 1)
                spacing: 4

                IconButton {
                    anchors.verticalCenter: parent.verticalCenter
                    visible: !!partRow.rowData.group
                    glyph: partRow.rowData.expanded ? Theme.icons.chevronDown : Theme.icons.chevronRight
                    variant: "ghost"
                    buttonSize: 20
                    iconSize: 11
                    tooltip: partRow.rowData.expanded ? qsTr("Fold the group") : qsTr("Open the group")
                    onClicked: EditorState.setShapeGroupExpanded(list.trackIndex, list.clipIndex, partRow.partId,
                                                                 !partRow.rowData.expanded)
                }
                Item {
                    visible: !partRow.rowData.group
                    width: 20
                    height: 20
                    anchors.verticalCenter: parent.verticalCenter
                }
                IconButton {
                    anchors.verticalCenter: parent.verticalCenter
                    glyph: partRow.rowData.visible === false ? Theme.icons.eyeOff : Theme.icons.eye
                    variant: "ghost"
                    buttonSize: 20
                    iconSize: 12
                    tooltip: partRow.rowData.visible === false ? qsTr("Show") : qsTr("Hide")
                    onClicked: EditorState.setShapePartVisible(list.trackIndex, list.clipIndex, partRow.partId,
                                                               partRow.rowData.visible === false)
                }
                // The part's colour, or a folder for a group.
                Item {
                    width: 16
                    height: 16
                    anchors.verticalCenter: parent.verticalCenter
                    Rectangle {
                        visible: !partRow.rowData.group
                        anchors.fill: parent
                        radius: partRow.rowData.kind === "ellipse" ? 8 : 3
                        color: partRow.rowData.color || Theme.accent
                        border.width: 1
                        border.color: Theme.panelBorder
                    }
                    IconGlyph {
                        visible: !!partRow.rowData.group
                        anchors.centerIn: parent
                        glyph: Theme.icons.folder
                        iconSize: 14
                        iconColor: Theme.panelForeground
                    }
                }
                Text {
                    visible: !partRow.renaming
                    anchors.verticalCenter: parent.verticalCenter
                    width: partRow.width - x - 30
                    elide: Text.ElideRight
                    text: partRow.rowData.name || ""
                    opacity: partRow.rowData.visible === false ? 0.5 : 1.0
                    color: Theme.panelForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSm
                }
                ThemedTextField {
                    id: renameField
                    visible: partRow.renaming
                    anchors.verticalCenter: parent.verticalCenter
                    width: partRow.width - x - 12
                    text: partRow.rowData.name || ""
                    onVisibleChanged: if (visible) { forceActiveFocus(); selectAll() }
                    onAccepted: {
                        EditorState.renameShapePart(list.trackIndex, list.clipIndex, partRow.partId, text)
                        partRow.renaming = false
                        list.forceActiveFocus()
                    }
                    onActiveFocusChanged: if (!activeFocus && partRow.renaming) partRow.renaming = false
                    Keys.onEscapePressed: { partRow.renaming = false; list.forceActiveFocus() }
                }
            }

            HoverHandler { id: rowHover }

            // Click picks, double-click renames, right-click opens the menu, drag reorders.
            MouseArea {
                anchors.fill: parent
                anchors.leftMargin: 6 + 16 * ((partRow.rowData.depth || 0) + 1) + 48
                enabled: !partRow.renaming
                acceptedButtons: Qt.LeftButton | Qt.RightButton
                // The inspector scrolls: without this a reordering drag was taken over by the scroll and left
                // its drop line (and the part to move) behind for the next drag.
                preventStealing: true
                property real pressY: 0
                onPressed: mouse => {
                    pressY = mouse.y
                    list.pick(partRow.partId)
                    if (mouse.button === Qt.RightButton)
                        partMenu.popup(partRow, mouse.x + 6 + 16 * ((partRow.rowData.depth || 0) + 1) + 48, mouse.y)
                }
                onDoubleClicked: partRow.renaming = true
                onPositionChanged: mouse => {
                    if (!(mouse.buttons & Qt.LeftButton))
                        return
                    if (list.dragId.length === 0 && Math.abs(mouse.y - pressY) > 6)
                        list.dragId = partRow.partId
                    if (list.dragId.length === 0)
                        return
                    // The row under the pointer, and the third of it: above, inside (groups) or below.
                    const p = mapToItem(list, mouse.x, mouse.y)
                    const target = list.childAt(10, p.y)
                    if (!target || target.partId === undefined || target.partId === list.dragId) {
                        list.dropTargetId = ""
                        return
                    }
                    const local = p.y - target.y
                    list.dropTargetId = target.partId
                    list.dropWhere = target.rowData.group && local > target.height / 3 && local < target.height * 2 / 3
                                     ? "inside" : (local < target.height / 2 ? "before" : "after")
                }
                onReleased: {
                    if (list.dragId.length > 0 && list.dropTargetId.length > 0)
                        EditorState.moveShapePart(list.trackIndex, list.clipIndex, list.dragId, list.dropTargetId,
                                                  list.dropWhere)
                    list.dragId = ""
                    list.dropTargetId = ""
                }
                onCanceled: {
                    list.dragId = ""
                    list.dropTargetId = ""
                }
            }

            ThemedContextMenu {
                id: partMenu
                ThemedMenuItem { text: qsTr("Rename"); onTriggered: partRow.renaming = true }
                ThemedMenuItem { text: qsTr("Duplicate") + "\tCtrl+D"; onTriggered: list.duplicateFocused() }
                ThemedMenuItem { text: qsTr("Group") + "\tCtrl+G"; onTriggered: list.groupFocused() }
                ThemedMenuItem {
                    visible: !!partRow.rowData.group
                    height: visible ? implicitHeight : 0
                    text: qsTr("Ungroup") + "\tCtrl+Shift+G"
                    onTriggered: EditorState.ungroupShapePart(list.trackIndex, list.clipIndex, partRow.partId)
                }
                ThemedMenuItem {
                    text: partRow.rowData.visible === false ? qsTr("Show") : qsTr("Hide")
                    onTriggered: EditorState.setShapePartVisible(list.trackIndex, list.clipIndex, partRow.partId,
                                                                 partRow.rowData.visible === false)
                }
                ThemedMenuSeparator { }
                ThemedMenuItem { text: qsTr("Delete") + "\tDel"; onTriggered: list.removeFocused() }
            }
        }
    }
}
