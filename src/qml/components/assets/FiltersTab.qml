import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."
import "."

// Filters tab: the LUT gallery of Adjust > LUT, in the sidebar like Filmora's Filters. A tile puts
// that look on the selected clip (the clip's color.lut effect, the same one Adjust > LUT edits:
// strength, on/off and removing it stay there). LUTs from Stock land in "Imported".
Item {
    id: root

    property alias searchText: search.text
    readonly property string query: search.text.trim().toLowerCase()
    property string activeCategory: "factory"
    readonly property var categories: [
        { id: "factory", label: qsTr("Looks") },
        { id: "imported", label: qsTr("Imported") }
    ]
    property string importError: ""

    property int libraryRevision: 0
    readonly property var library: {
        void libraryRevision
        return EditorState.lutLibrary()
    }

    Connections {
        target: EditorState
        function onLutLibraryChanged() { root.libraryRevision++ }
    }

    readonly property var effects: EditorState.selectedClipEffects || []
    readonly property bool canEdit: {
        const d = EditorState.selectedClipData
        return !!d && (d.caps || []).indexOf("adj:videoEffects") >= 0
    }

    function effectIndex() {
        for (let i = effects.length - 1; i >= 0; i--) {
            if (effects[i].catalogId === "color.lut")
                return i
        }
        return -1
    }

    readonly property string lutPath: {
        const i = effectIndex()
        if (i < 0)
            return ""
        const params = effects[i].params || []
        for (let p = 0; p < params.length; p++) {
            if (params[p].key === "lut")
                return params[p].value || ""
        }
        return ""
    }

    readonly property var visibleLuts: {
        const q = root.query
        if (q.length > 0)
            return root.library.filter(l => String(l.name || "").toLowerCase().indexOf(q) >= 0)
        const factory = root.activeCategory === "factory"
        return root.library.filter(l => !!l.factory === factory)
    }

    function fileName(path) {
        return String(path).split(/[/\\]/).pop()
    }

    // Same as Adjust > LUT: adds the effect the first time, then points it at the file.
    function use(path) {
        if (!root.canEdit) {
            Toasts.info(qsTr("Select a video or photo clip first."))
            return
        }
        if (root.effectIndex() < 0)
            EditorState.addEffect(EditorState.selectedTrack, EditorState.selectedClip, "color.lut")
        const i = root.effectIndex()
        if (i >= 0)
            EditorState.setEffectStringParam(EditorState.selectedTrack, EditorState.selectedClip, i, "lut",
                                             "file:///" + String(path).replace(/^\/+/, ""))
    }

    function importFile() {
        const url = FileDialogs.openFile(qsTr("Import LUT"), [qsTr("LUT (*.cube)"), qsTr("All files (*)")])
        if (!url || url.toString() === "")
            return
        const result = EditorState.importLut(url)
        if (!result.ok) {
            root.importError = result.error || qsTr("This file is not a LUT that can be used.")
            return
        }
        root.importError = ""
        root.activeCategory = "imported"
        if (root.canEdit)
            root.use(result.path)
    }

    Column {
        anchors.fill: parent
        spacing: 0

        AssetSearchBar {
            id: search
            placeholderText: qsTr("Search filters")
        }

        Item {
            width: 1
            height: Theme.spacingSm
        }

        AssetCategoryChips {
            id: categoryChips
            width: parent.width
            categories: root.categories
            activeCategory: root.activeCategory
            searching: root.query.length > 0
            showFavorites: false
            onCategoryActivated: (categoryId) => root.activeCategory = categoryId
        }

        Column {
            id: hints
            x: Theme.pagePadding
            width: parent.width - Theme.pagePadding * 2
            topPadding: Theme.spacingSm
            bottomPadding: Theme.spacingSm
            spacing: Theme.spacingSm

            Row {
                width: parent.width
                spacing: Theme.spacingSm

                Text {
                    width: parent.width - importButton.width - Theme.spacingSm
                    anchors.verticalCenter: parent.verticalCenter
                    wrapMode: Text.WordWrap
                    text: root.canEdit ? qsTr("Click a filter to put it on the selected clip. Its strength is in Adjust › LUT.")
                                       : qsTr("Select a video or photo clip, then click a filter.")
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                }

                ThemedButton {
                    id: importButton
                    text: qsTr("Import LUT…")
                    variant: "ghost"
                    glyph: Theme.icons.upload
                    onClicked: root.importFile()
                }
            }

            Text {
                visible: root.importError.length > 0
                width: parent.width
                wrapMode: Text.WordWrap
                text: root.importError
                color: Theme.destructive
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
        }

        Item {
            width: parent.width
            height: Math.max(0, parent.height - search.height - Theme.spacingSm - categoryChips.height - hints.height)

            Text {
                x: Theme.pagePadding
                y: Theme.pagePadding
                width: parent.width - Theme.pagePadding * 2
                visible: root.visibleLuts.length === 0
                text: root.query.length > 0
                      ? qsTr("No filters match “%1”.").arg(search.text.trim())
                      : (root.activeCategory === "imported"
                         ? qsTr("No imported LUTs yet. Import a .cube file, or get LUTs in Stock.")
                         : qsTr("Nothing in this category."))
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                wrapMode: Text.WordWrap
            }

            GridView {
                id: lutGrid
                readonly property int columnCount: Math.max(1, Math.round(width / (Theme.assetCardWidth + Theme.assetCardGap)))
                readonly property real cardSize: Math.floor(width / columnCount) - Theme.assetCardGap
                x: Theme.pagePadding
                width: parent.width - Theme.pagePadding * 2 + Theme.assetCardGap
                height: parent.height
                clip: true
                cellWidth: cardSize + Theme.assetCardGap
                cellHeight: cardSize + Theme.fontSizeCard + 14
                boundsBehavior: Flickable.StopAtBounds
                // With a mouse the grid scrolls by wheel only and leaves the press to the tile, as the
                // other asset grids do; otherwise the flick took the click and no filter was applied.
                acceptedButtons: Theme.touchUi ? Qt.LeftButton : Qt.NoButton
                model: root.visibleLuts
                ScrollBar.vertical: AppScrollBar {}

                delegate: Item {
                    id: tile
                    required property var modelData
                    readonly property bool current: !!root.lutPath
                        && root.fileName(root.lutPath) === root.fileName(modelData.path)
                    width: lutGrid.cardSize
                    height: lutGrid.cellHeight

                    Rectangle {
                        id: frame
                        width: parent.width
                        height: width
                        radius: Theme.radiusSm
                        color: Theme.panelMuted
                        border.width: tile.current ? 2 : Theme.borderWidth
                        border.color: tile.current ? Theme.primary : (tileHover.hovered ? Theme.foreground
                                                                                               : Theme.panelBorder)
                        scale: tileTap.pressed ? 0.97 : (tileHover.hovered ? 1.02 : 1.0)
                        Behavior on scale {
                            NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                        }

                        Image {
                            anchors.fill: parent
                            anchors.margins: 3
                            fillMode: Image.PreserveAspectCrop
                            asynchronous: true
                            source: EditorState.lutThumbnail(tile.modelData.path)
                        }
                    }

                    Text {
                        anchors.top: frame.bottom
                        anchors.topMargin: 4
                        width: parent.width
                        horizontalAlignment: Text.AlignHCenter
                        elide: Text.ElideRight
                        text: tile.modelData.name
                        color: tile.current ? Theme.foreground : Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeCard
                    }

                    // Pointer handlers, as the other asset cards (AssetDragSource): a MouseArea here
                    // never got the click in the window test.
                    HoverHandler {
                        id: tileHover
                        cursorShape: Qt.PointingHandCursor
                    }

                    TapHandler {
                        id: tileTap
                        acceptedButtons: Qt.LeftButton
                        onTapped: root.use(tile.modelData.path)
                    }

                    TapHandler {
                        acceptedButtons: Qt.RightButton
                        onTapped: if (!tile.modelData.factory) deleteMenu.popup()
                    }

                    ThemedToolTip {
                        text: tile.modelData.name
                        visible: tileHover.hovered
                    }

                    ThemedContextMenu {
                        id: deleteMenu
                        ThemedMenuItem {
                            text: qsTr("Delete from my LUTs")
                            onTriggered: EditorState.removeImportedLut(tile.modelData.path)
                        }
                    }
                }
            }
        }
    }
}
