import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift
import ".."
import "."

// Stickers tab: category bar over a grid of the built-in sticker set.
Item {
    id: root
    // The panel's sidebar drives the category (0.23): its chips are not shown.
    property bool panelDriven: false

    // A clip landed on the timeline. The phone shell closes the sheet on this —
    // the thing you came for is behind it.
    signal added()
    // AssetsPanel owns the emoji picker; the button for it lives in this tab's search bar.
    signal emojiPickerRequested()
    property bool emojiPickerOpen: false

    readonly property string favoritesId: "__favorites__"
    property var ownCategories: EditorState.builtinStickerCategories()
    property var allStickers: EditorState.builtinStickers()
    readonly property bool hasStickers: allStickers.length > 0
    // Stock's animated stickers (Lottie) and backgrounds here too (0.22): Trending first (the most
    // used), Backgrounds, and the stickers spread over these chips by category after the local
    // ones, or in chips of their own («stock:<category>»).
    readonly property string trendsId: "__trends__"
    readonly property string backgroundsId: "__stock_backgrounds__"
    property int stockTick: 0
    readonly property var stockChips: {
        void root.stockTick
        return Market.authenticated ? Market.stockChips("animation", root.ownCategories.map(c => ({ "id": c.id, "label": c.label })))
                                    : ({ extra: [], categoriesOf: {} })
    }
    readonly property var categories: Market.configured
        ? [{ "id": root.trendsId, "label": qsTr("Trending") }, { "id": root.backgroundsId, "label": qsTr("Backgrounds") }]
              .concat(root.ownCategories).concat(root.stockChips.extra || [])
        : root.ownCategories
    readonly property var stockCategoriesHere: (root.stockChips.categoriesOf || {})[root.activeCategory] || []
    readonly property bool showingStockOnly: root.query.length === 0
                                             && (root.activeCategory === root.trendsId
                                                 || root.activeCategory === root.backgroundsId
                                                 || root.activeCategory.indexOf("stock:") === 0)
    readonly property var stockFavorites: {
        void root.favoritesTick
        void Market.favoriteItemsRevision
        return root.activeCategory === root.favoritesId && root.query.length === 0
               ? Market.stockFavoriteItems(EditorState.assetFavoriteIds("stickers"), ["animation", "background"], "stickers")
               : []
    }
    readonly property bool stockFooter: root.query.length === 0 && !root.showingStockOnly
                                        && (root.stockFavorites.length > 0 || root.stockCategoriesHere.length > 0)
    property string activeCategory: categories.length > 0 ? categories[0].id : ""

    Connections {
        target: Market
        function onAuthChanged() { root.stockTick++ }
        function onCatalogChanged() { root.stockTick++ }
    }

    // A Stock sticker or background is a file in Media: put at the playhead.
    function stockInstalled(item) {
        const asset = Market.placedId(item.id)
        return asset.length > 0 && AssetLibrary.indexOfId(asset) >= 0
    }
    function applyStock(item) {
        EditorState.addAssetClipWhenReady(Market.placedId(item.id))
        root.added()
    }
    property alias searchText: search.text
    readonly property string query: search.text.trim().toLowerCase()
    property int favoritesTick: 0

    Connections {
        target: EditorState
        function onAssetFavoritesChanged() {
            root.favoritesTick++
        }
    }

    readonly property var currentStickers: {
        void root.favoritesTick
        const q = root.query
        if (q.length > 0) {
            return root.allStickers.filter(function(s) {
                const label = (s.label || "").toLowerCase()
                const id = (s.id || "").toLowerCase()
                return label.indexOf(q) >= 0 || id.indexOf(q) >= 0
            })
        }
        if (root.activeCategory === root.favoritesId) {
            return root.allStickers.filter(function(s) {
                return EditorState.isAssetFavorite("stickers", s.id)
            })
        }
        if (root.showingStockOnly)
            return []
        return root.allStickers.filter(function(s) { return s.category === root.activeCategory })
    }

    Connections {
        target: Addons
        function onKindChanged(kind) {
            if (kind !== "stickers")
                return
            root.ownCategories = EditorState.builtinStickerCategories()
            root.allStickers = EditorState.builtinStickers()
            root.activeCategory = root.categories.length > 0 ? root.categories[0].id : ""
        }
    }

    Column {
        anchors.fill: parent
        spacing: 0

        AssetSearchBar {
            id: search
            visible: root.hasStickers
            height: visible ? implicitHeight : 0
            placeholderText: qsTr("Search stickers")

            // The sticker packs are a curated subset of the emoji set, so the rest live behind
            // this button rather than being unreachable.
            IconButton {
                glyph: Theme.icons.plus
                variant: "ghost"
                buttonSize: Theme.controlHeight
                tooltip: qsTr("More emoji")
                active: root.emojiPickerOpen
                onClicked: root.emojiPickerRequested()
            }
        }

        Item {
            width: 1
            height: root.hasStickers ? Theme.spacingSm : 0
        }

        AssetCategoryChips {
            id: categoryChips
            panelDriven: root.panelDriven
            width: parent.width
            categories: root.hasStickers || Market.configured ? root.categories : []
            activeCategory: root.activeCategory
            searching: root.query.length > 0
            onCategoryActivated: (categoryId) => root.activeCategory = categoryId
        }

        Item {
            width: parent.width
            height: Math.max(0, parent.height - search.height
                             - (root.hasStickers ? Theme.spacingSm : 0) - categoryChips.height)

            EmptyState {
                visible: !root.hasStickers && !root.showingStockOnly
                x: Theme.pagePadding
                y: Theme.pagePadding
                width: parent.width - Theme.pagePadding * 2
                compact: true
                glyph: Theme.icons.smile
                title: qsTr("No sticker packs installed")
                hint: qsTr("Install the emoji pack to add stickers.")
                actionText: qsTr("Get extras")
                actionVariant: "primary"
                onActionTriggered: root.Window.window.openAddonManager("stickers")
            }

            // Trending, Backgrounds, or a chip of Stock's own: Stock's cards only.
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
                    type: root.activeCategory === root.backgroundsId ? "background" : "animation"
                    layout: root.activeCategory === root.backgroundsId ? "wide" : "square"
                    categories: root.activeCategory === root.backgroundsId ? [""]
                              : root.activeCategory === root.trendsId ? [] : root.stockCategoriesHere
                    glyph: Theme.icons.smile
                    isInstalled: function(item) { return root.stockInstalled(item) }
                    apply: function(item) { root.applyStock(item) }
                }
            }

            EmptyState {
                visible: root.hasStickers && root.currentStickers.length === 0 && !root.showingStockOnly
                         && !root.stockFooter
                x: Theme.pagePadding
                y: Theme.pagePadding
                width: parent.width - Theme.pagePadding * 2
                compact: true
                glyph: Theme.icons.smile
                title: root.query.length > 0
                       ? qsTr("No stickers match “%1”").arg(search.text.trim())
                       : (root.activeCategory === root.favoritesId
                          ? qsTr("No favorites yet")
                          : qsTr("Nothing in this category"))
                hint: root.query.length > 0
                      ? qsTr("Try a different name.")
                      : (root.activeCategory === root.favoritesId
                         ? qsTr("Star stickers to save them here.")
                         : qsTr("Pick another category."))
            }

            FontMetrics {
                id: labelMetrics
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeCard
            }

            // One trailing gap wider than the padded area, so the cards pack from the left
            // exactly as the old Grid did.
            // Past the end of a category, the wheel goes on into the next one (CapCut).
            CategoryScrollOn {
                anchors.fill: stickerGrid
                flickable: stickerGrid
                categories: root.categories
                activeCategory: root.activeCategory
                active: root.query.length === 0
                onCategoryActivated: (categoryId) => root.activeCategory = categoryId
            }

            GridView {
                id: stickerGrid
                // As many columns as fit at the nominal card size, rounded, with the cards stretched or
                // squeezed a little to fill the row — a fixed card left a column's worth of empty space.
                readonly property int columnCount: Math.max(1, Math.round(width / (Theme.assetCardWidth + Theme.assetCardGap)))
                readonly property real cardSize: Math.floor(width / columnCount) - Theme.assetCardGap
                x: Theme.pagePadding
                width: parent.width - Theme.pagePadding * 2 + Theme.assetCardGap
                height: parent.height
                topMargin: Theme.pagePadding
                bottomMargin: Theme.pagePadding
                visible: root.currentStickers.length > 0 || root.stockFooter
                clip: true
                reuseItems: true
                // A mouse drag on a card drags the sticker; the wheel and touchpad scroll.
                acceptedButtons: Theme.touchUi ? Qt.LeftButton : Qt.NoButton
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: AppScrollBar { }
                cellWidth: Math.floor(width / columnCount)
                cellHeight: stickerGrid.cardSize + Theme.spacingSm + Math.ceil(labelMetrics.height) + Theme.assetCardGap
                model: root.currentStickers

                // The chip's Stock stickers after its own (and the starred ones in Favorites).
                footer: StockPanelCards {
                    width: stickerGrid.width - Theme.assetCardGap
                    visible: root.stockFooter
                    height: visible ? implicitHeight : 0
                    bare: true
                    layout: "square"
                    flickable: stickerGrid
                    type: "animation"
                    categories: root.stockCategoriesHere
                    items: root.activeCategory === root.favoritesId ? root.stockFavorites : null
                    isInstalled: function(item) { return root.stockInstalled(item) }
                    apply: function(item) { root.applyStock(item) }
                }

                delegate: Column {
                    required property var modelData
                    width: stickerGrid.cardSize
                    spacing: Theme.spacingSm
                    opacity: stickerDrag.active ? 0.85 : 1
                    scale: stickerDrag.active ? 1.04 : stickerDrag.pressed ? 0.97 : (stickerDrag.hovered ? 1.02 : 1.0)

                    Behavior on opacity {
                        NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                    }
                    Behavior on scale {
                        NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                    }

                    Rectangle {
                        width: stickerGrid.cardSize
                        height: stickerGrid.cardSize
                        radius: Theme.radiusSm
                        color: stickerDrag.hovered ? Theme.popoverHover : Theme.panelAccent
                        clip: true

                        Behavior on color {
                            ColorAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                        }

                        SkeletonBox {
                            anchors.fill: parent
                            anchors.margins: Theme.pagePadding
                            visible: stickerImage.status === Image.Loading
                        }

                        // Hover gives the sticker a little life: a pop, then a gentle sway while
                        // the pointer rests on it. An animated sticker plays its own motion instead.
                        HoverPop {
                            id: stickerPop
                            target: stickerImage
                            active: stickerDrag.hovered && !stickerDrag.active
                            sway: modelData.animated !== true
                        }

                        Image {
                            id: stickerImage
                            anchors.fill: parent
                            anchors.margins: Theme.pagePadding
                            visible: !stickerMotion.visible
                            source: EditorState.imageUrl(modelData.thumbnail || modelData.path)
                            fillMode: Image.PreserveAspectFit
                            asynchronous: true
                            sourceSize: Qt.size(Math.ceil((stickerGrid.cardSize - Theme.pagePadding * 2) * Screen.devicePixelRatio),
                                                 Math.ceil((stickerGrid.cardSize - Theme.pagePadding * 2) * Screen.devicePixelRatio))
                            opacity: status === Image.Ready ? 1 : 0

                            Behavior on opacity {
                                NumberAnimation { duration: Theme.durationBase; easing.type: Theme.easing }
                            }
                        }

                        LottieHoverSprite {
                            id: stickerMotion
                            anchors.fill: parent
                            anchors.margins: Theme.pagePadding
                            path: modelData.animated === true ? modelData.path : ""
                            hovered: stickerDrag.hovered && !stickerDrag.active
                            scale: stickerImage.scale
                        }

                        IconGlyph {
                            anchors.centerIn: parent
                            visible: stickerImage.status === Image.Error
                            glyph: Theme.icons.error
                            iconSize: Theme.iconSizeLg
                            iconColor: Theme.mutedForeground
                        }

                        ThemedToolTip {
                            text: qsTr("%1 — click to add, or drag to the timeline or preview").arg(modelData.label)
                            visible: stickerDrag.hovered && !stickerDrag.active
                        }

                        AssetDragSource {
                            id: stickerDrag
                            hasContextMenu: true
                            onContextMenuRequested: cardMenu.popup()
                            anchors.fill: parent
                            kind: "sticker"
                            payload: modelData.id
                            label: modelData.label
                            thumbnail: modelData.thumbnail || modelData.path
                            onTapped: {
                                EditorState.addStickerClip(modelData.id, -1)
                                root.added()
                            }
                        }

                        ThemedContextMenu {
                            id: cardMenu

                            property bool favorited: false

                            onAboutToShow: favorited = EditorState.isAssetFavorite("stickers", modelData.id)

                            ThemedMenuItem {
                                text: qsTr("Add at playhead")
                                icon.name: Theme.icons.plus
                                onTriggered: stickerDrag.tapped()
                            }
                            ThemedMenuItem {
                                text: cardMenu.favorited ? qsTr("Remove from favorites") : qsTr("Add to favorites")
                                icon.name: Theme.icons.star
                                onTriggered: EditorState.toggleAssetFavorite("stickers", modelData.id)
                            }
                        }

                        AssetFavoriteButton {
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.margins: 3
                            tabId: "stickers"
                            itemId: modelData.id
                        }

                        // Animated stickers move once placed; the grid shows their still until
                        // hovered, when the card plays them (so no "Animated" tooltip over it).
                        Rectangle {
                            visible: modelData.animated === true
                            anchors.left: parent.left
                            anchors.bottom: parent.bottom
                            anchors.margins: 4
                            width: 18
                            height: 18
                            radius: 9
                            color: Theme.scrimStrong

                            IconGlyph {
                                anchors.centerIn: parent
                                glyph: Theme.icons.play
                                iconSize: 10
                                iconColor: Theme.onMedia
                            }
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
