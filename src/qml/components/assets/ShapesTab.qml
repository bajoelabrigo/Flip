import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."
import "."

// Shapes tab. Shapes used to be a page inside the Stickers tab, where they came
// and went with the sticker addon and had no room for categories of their own.
Item {
    id: root
    // The panel's sidebar drives the category (0.23): its chips are not shown.
    property bool panelDriven: false

    // A clip landed on the timeline. The phone shell closes the sheet on this —
    // the thing you came for is behind it.
    signal added()

    readonly property string favoritesId: "__favorites__"
    // Shapes installed from Stock come after the built-in ones, in their own categories.
    property int userShapesTick: 0
    readonly property var ownCategories: {
        void root.userShapesTick
        return EditorState.builtinShapeCategories().concat(EditorState.userShapeCategories())
    }
    // Stock's shapes here too (0.22): Trending first (the most used), the rest spread over these
    // chips by category after the local ones, or in chips of their own («stock:<category>»).
    readonly property string trendsId: "__trends__"
    property int stockTick: 0
    readonly property var stockChips: {
        void root.stockTick
        return Market.authenticated ? Market.stockChips("shape", root.ownCategories.map(c => ({ "id": c.id, "label": c.label })))
                                    : ({ extra: [], categoriesOf: {} })
    }
    readonly property var categories: Market.configured
        ? [{ "id": root.trendsId, "label": qsTr("Trending") }].concat(root.ownCategories).concat(root.stockChips.extra || [])
        : root.ownCategories
    readonly property var stockCategoriesHere: (root.stockChips.categoriesOf || {})[root.activeCategory] || []
    readonly property bool showingStockOnly: root.query.length === 0
                                             && (root.activeCategory === root.trendsId
                                                 || root.activeCategory.indexOf("stock:") === 0)
    readonly property var stockFavorites: {
        void root.favoritesTick
        void Market.favoriteItemsRevision
        return root.activeCategory === root.favoritesId && root.query.length === 0
               ? Market.stockFavoriteItems(EditorState.assetFavoriteIds("shapes"), ["shape"], "shapes")
               : []
    }
    readonly property bool stockFooter: root.query.length === 0 && !root.showingStockOnly
                                        && (root.stockFavorites.length > 0 || root.stockCategoriesHere.length > 0)

    Connections {
        target: Market
        function onAuthChanged() { root.stockTick++ }
        function onCatalogChanged() { root.stockTick++ }
    }

    // A Stock shape installs as "user-shape:<id>" (drift::installUserShapeFile).
    function stockShapeId(item) {
        const placed = Market.placedId(item.id)
        return placed.length > 0 ? placed : "user-shape:" + String(item.id || "").split(":").pop()
    }
    function stockInstalled(item) {
        void root.userShapesTick
        const id = root.stockShapeId(item)
        return root.allShapes.some(s => s.id === id)
    }
    function applyStock(item) {
        root.userShapesTick++
        EditorState.addShapeClip(root.stockShapeId(item), -1)
        root.added()
    }
    readonly property var allShapes: {
        void root.userShapesTick
        return EditorState.builtinShapes().concat(EditorState.userShapes())
    }
    property string activeCategory: categories.length > 0 ? categories[0].id : ""
    property alias searchText: search.text
    readonly property string query: search.text.trim().toLowerCase()
    property int favoritesTick: 0

    Connections {
        target: EditorState
        function onAssetFavoritesChanged() {
            root.favoritesTick++
        }
        function onUserShapesChanged() {
            root.userShapesTick++
        }
    }

    readonly property var currentShapes: {
        void root.favoritesTick
        const q = root.query
        if (q.length > 0) {
            return root.allShapes.filter(function(s) {
                const label = (s.label || "").toLowerCase()
                const id = (s.id || "").toLowerCase()
                return label.indexOf(q) >= 0 || id.indexOf(q) >= 0
            })
        }
        if (root.activeCategory === root.favoritesId) {
            return root.allShapes.filter(function(s) {
                return EditorState.isAssetFavorite("shapes", s.id)
            })
        }
        if (root.showingStockOnly)
            return []
        return root.allShapes.filter(function(s) { return s.category === root.activeCategory })
    }

    Column {
        anchors.fill: parent
        spacing: 0

        AssetSearchBar {
            id: search
            placeholderText: qsTr("Search shapes")
        }

        Item {
            width: 1
            height: Theme.spacingSm
        }

        AssetCategoryChips {
            id: categoryChips
            panelDriven: root.panelDriven
            width: parent.width
            categories: root.categories
            activeCategory: root.activeCategory
            searching: root.query.length > 0
            onCategoryActivated: (categoryId) => root.activeCategory = categoryId
        }

        Item {
            width: parent.width
            height: Math.max(0, parent.height - search.height - Theme.spacingSm - categoryChips.height)

            Text {
                id: emptySearchHint
                x: Theme.pagePadding
                y: Theme.pagePadding
                width: parent.width - Theme.pagePadding * 2
                visible: root.currentShapes.length === 0 && !root.showingStockOnly && !root.stockFooter
                text: root.query.length > 0
                      ? qsTr("No shapes match “%1”.").arg(search.text.trim())
                      : (root.activeCategory === root.favoritesId
                         ? qsTr("No favorites yet. Star shapes to save them here.")
                         : qsTr("Nothing in this category."))
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                wrapMode: Text.WordWrap
            }

            // Trending, or a chip of Stock's own: Stock's shapes only.
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
                    y: Theme.pagePadding
                    width: stockView.width
                    sidePadding: Theme.pagePadding
                    flickable: stockView
                    type: "shape"
                    layout: "square"
                    categories: root.activeCategory === root.trendsId ? [] : root.stockCategoriesHere
                    glyph: Theme.icons.shapes
                    isInstalled: function(item) { return root.stockInstalled(item) }
                    apply: function(item) { root.applyStock(item) }
                }
            }

            FontMetrics {
                id: labelMetrics
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeCard
            }

            // One trailing gap wider than the padded area, so the cards pack from the left exactly
            // as the old Grid did.
            // Past the end of a category, the wheel goes on into the next one (CapCut).
            CategoryScrollOn {
                anchors.fill: shapeGrid
                flickable: shapeGrid
                categories: root.categories
                activeCategory: root.activeCategory
                active: root.query.length === 0
                onCategoryActivated: (categoryId) => root.activeCategory = categoryId
            }

            GridView {
                id: shapeGrid
                // As many columns as fit at the nominal card size, rounded, with the cards stretched or
                // squeezed a little to fill the row — a fixed card left a column's worth of empty space.
                readonly property int columnCount: Math.max(1, Math.round(width / (Theme.assetCardWidth + Theme.assetCardGap)))
                readonly property real cardSize: Math.floor(width / columnCount) - Theme.assetCardGap
                x: Theme.pagePadding
                width: parent.width - Theme.pagePadding * 2 + Theme.assetCardGap
                height: parent.height
                topMargin: Theme.pagePadding
                bottomMargin: Theme.pagePadding
                visible: root.currentShapes.length > 0 || root.stockFooter
                clip: true
                reuseItems: true
                boundsBehavior: Flickable.StopAtBounds
                acceptedButtons: Theme.touchUi ? Qt.LeftButton : Qt.NoButton
                ScrollBar.vertical: AppScrollBar { }
                cellWidth: Math.floor(width / columnCount)
                cellHeight: shapeGrid.cardSize + Theme.spacingSm + Math.ceil(labelMetrics.height) + Theme.assetCardGap
                model: root.currentShapes

                // The chip's Stock shapes after its own (and the starred ones in Favorites).
                footer: StockPanelCards {
                    width: shapeGrid.width - Theme.assetCardGap
                    visible: root.stockFooter
                    height: visible ? implicitHeight : 0
                    bare: true
                    layout: "square"
                    flickable: shapeGrid
                    type: "shape"
                    categories: root.stockCategoriesHere
                    items: root.activeCategory === root.favoritesId ? root.stockFavorites : null
                    isInstalled: function(item) { return root.stockInstalled(item) }
                    apply: function(item) { root.applyStock(item) }
                }

                delegate: Column {
                    id: shapeCard
                    required property var modelData
                    width: shapeGrid.cardSize
                    spacing: Theme.spacingSm

                    opacity: shapeDrag.active ? 0.85 : 1
                    scale: shapeDrag.active ? 1.04 : (shapeDrag.pressed ? 0.97 : 1.0)

                    Behavior on opacity {
                        NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                    }
                    Behavior on scale {
                        NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                    }

                    Rectangle {
                        width: shapeGrid.cardSize
                        height: shapeGrid.cardSize
                        radius: Theme.radiusSm
                        color: shapeDrag.hovered ? Theme.popoverHover : Theme.panelAccent
                        border.width: 1
                        border.color: shapeDrag.hovered ? Theme.accent : "transparent"

                        Behavior on color {
                            ColorAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                        }
                        Behavior on border.color {
                            ColorAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                        }

                        // The catalog entry drawn with its real default style, so the card
                        // shows what lands on the timeline.
                        Image {
                            anchors.fill: parent
                            anchors.margins: Theme.pagePadding
                            source: "image://shape/" + shapeCard.modelData.id
                            sourceSize: Qt.size(shapeGrid.cardSize * 2, shapeGrid.cardSize * 2)
                            fillMode: Image.PreserveAspectFit
                            asynchronous: true
                            cache: true
                            scale: shapeDrag.pressed ? 0.94 : shapeDrag.hovered ? 1.06 : 1.0
                            Behavior on scale {
                                NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                            }
                        }

                        ThemedToolTip {
                            text: qsTr("%1 — click to add, or drag to the timeline or preview").arg(shapeCard.modelData.label)
                            visible: shapeDrag.hovered && !shapeDrag.active
                        }

                        AssetDragSource {
                            id: shapeDrag
                            hasContextMenu: true
                            onContextMenuRequested: cardMenu.popup()
                            anchors.fill: parent
                            kind: "shape"
                            payload: shapeCard.modelData.id
                            label: shapeCard.modelData.label
                            glyph: Theme.icons.shapes
                            onTapped: {
                                EditorState.addShapeClip(shapeCard.modelData.id, -1)
                                root.added()
                            }
                        }

                        ThemedContextMenu {
                            id: cardMenu

                            property bool favorited: false

                            onAboutToShow: favorited = EditorState.isAssetFavorite("shapes", shapeCard.modelData.id)

                            ThemedMenuItem {
                                text: qsTr("Add at playhead")
                                icon.name: Theme.icons.plus
                                onTriggered: shapeDrag.tapped()
                            }
                            ThemedMenuItem {
                                text: cardMenu.favorited ? qsTr("Remove from favorites") : qsTr("Add to favorites")
                                icon.name: Theme.icons.star
                                onTriggered: EditorState.toggleAssetFavorite("shapes", shapeCard.modelData.id)
                            }
                            ThemedMenuItem {
                                visible: shapeCard.modelData.user === true
                                height: visible ? implicitHeight : 0
                                text: qsTr("Remove from my shapes")
                                icon.name: Theme.icons.trash
                                onTriggered: EditorState.removeUserShape(shapeCard.modelData.id)
                            }
                        }

                        AssetFavoriteButton {
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.margins: 3
                            tabId: "shapes"
                            itemId: shapeCard.modelData.id
                        }
                    }

                    Text {
                        width: parent.width
                        text: modelData.label
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeCard
                        horizontalAlignment: Text.AlignHCenter
                        elide: Text.ElideRight
                    }
                }
            }
        }
        
    }
}
