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
    // Stock's LUTs here too (0.22): Trending first (the most used), then Stock's categories in chips
    // of their own after these; none matches a chip of this tab.
    readonly property string trendsId: "__trends__"
    readonly property string favoritesId: "__favorites__"
    property string activeCategory: Market.configured ? trendsId : "factory"
    property int stockTick: 0
    readonly property var stockChips: {
        void root.stockTick
        return Market.authenticated ? Market.stockChips("lut", ["factory", "imported"])
                                    : ({ extra: [], categoriesOf: {} })
    }
    readonly property var categories: (Market.configured ? [{ id: root.trendsId, label: qsTr("Trending") }] : [])
        .concat([
            { id: "factory", label: qsTr("Looks") },
            { id: "imported", label: qsTr("Imported") }
        ]).concat(root.stockChips.extra || [])
    readonly property var stockCategoriesHere: (root.stockChips.categoriesOf || {})[root.activeCategory] || []
    readonly property bool showingStockOnly: root.query.length === 0
                                             && (root.activeCategory === root.trendsId
                                                 || root.activeCategory.indexOf("stock:") === 0)
    property int favoritesTick: 0
    readonly property var stockFavorites: {
        void root.favoritesTick
        void Market.favoriteItemsRevision
        return root.activeCategory === root.favoritesId && root.query.length === 0
               ? Market.stockFavoriteItems(EditorState.assetFavoriteIds("luts"), ["lut"], "luts")
               : []
    }
    readonly property bool stockFooter: root.query.length === 0 && !root.showingStockOnly
                                        && (root.stockFavorites.length > 0 || root.stockCategoriesHere.length > 0)
    property string importError: ""

    Connections {
        target: Market
        function onAuthChanged() { root.stockTick++ }
        function onCatalogChanged() { root.stockTick++ }
    }

    // The star's key, as the web's (lutStore.ts): "factory:cinematic" for the looks that come with
    // the app, so a favorite follows the account to the browser; an imported one keeps its own id.
    function favoriteKey(lut) {
        const id = String(lut.id || "")
        return lut.factory ? id.replace(/\.cube$/i, "") : id
    }
    // A Stock LUT lands in the library as "user:<file>" (MarketClient::placedId).
    function stockLut(item) {
        void root.libraryRevision
        const placed = Market.placedId(item.id)
        return placed.length > 0 ? root.library.find(l => l.id === placed) : undefined
    }

    property int libraryRevision: 0
    readonly property var library: {
        void libraryRevision
        return EditorState.lutLibrary()
    }

    Connections {
        target: EditorState
        function onLutLibraryChanged() { root.libraryRevision++ }
        function onAssetFavoritesChanged() { root.favoritesTick++ }
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
        if (root.activeCategory === root.favoritesId) {
            void root.favoritesTick
            return root.library.filter(l => EditorState.isAssetFavorite("luts", root.favoriteKey(l)))
        }
        if (root.activeCategory !== "factory" && root.activeCategory !== "imported")
            return []
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
                visible: root.visibleLuts.length === 0 && !root.showingStockOnly && !root.stockFooter
                text: root.query.length > 0
                      ? qsTr("No filters match “%1”.").arg(search.text.trim())
                      : (root.activeCategory === "imported"
                         ? qsTr("No imported LUTs yet. Import a .cube file, or get LUTs in Stock.")
                         : root.activeCategory === root.favoritesId
                         ? qsTr("No favorites yet. Star filters to save them here.")
                         : qsTr("Nothing in this category."))
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                wrapMode: Text.WordWrap
            }

            // Trending, or a chip of Stock's own: Stock's LUTs only.
            Flickable {
                id: stockView
                anchors.fill: parent
                visible: root.showingStockOnly
                clip: true
                contentHeight: stockOnlyCards.height + Theme.spacingXl
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: AppScrollBar { }

                StockPanelCards {
                    id: stockOnlyCards
                    width: stockView.width
                    sidePadding: Theme.pagePadding
                    flickable: stockView
                    type: "lut"
                    categories: root.activeCategory === root.trendsId ? [] : root.stockCategoriesHere
                    glyph: Theme.icons.blend
                    isInstalled: function(item) { return !!root.stockLut(item) }
                    apply: function(item) {
                        root.libraryRevision++
                        const lut = root.stockLut(item)
                        if (lut)
                            root.use(lut.path)
                    }
                }
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
                visible: !root.showingStockOnly
                model: root.visibleLuts
                ScrollBar.vertical: AppScrollBar {}

                // The starred Stock LUTs after the local ones in Favorites.
                footer: StockPanelCards {
                    width: lutGrid.width - Theme.assetCardGap
                    visible: root.stockFooter
                    height: visible ? implicitHeight : 0
                    bare: true
                    flickable: lutGrid
                    type: "lut"
                    categories: root.stockCategoriesHere
                    items: root.activeCategory === root.favoritesId ? root.stockFavorites : null
                    isInstalled: function(item) { return !!root.stockLut(item) }
                    apply: function(item) {
                        root.libraryRevision++
                        const lut = root.stockLut(item)
                        if (lut)
                            root.use(lut.path)
                    }
                }

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

                        // Under the pointer: the reference photo without the look, wiping to it.
                        BeforeAfterImage {
                            anchors.fill: parent
                            anchors.margins: 3
                            beforeSource: EditorState.lutReference(tile.modelData.path)
                            afterSource: EditorState.lutThumbnail(tile.modelData.path)
                            playing: tileHover.hovered
                        }

                        AssetFavoriteButton {
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.margins: 3
                            z: 2
                            tabId: "luts"
                            itemId: root.favoriteKey(tile.modelData)
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
