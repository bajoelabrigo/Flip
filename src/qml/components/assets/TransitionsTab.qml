import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift
import ".."
import "."

// Transitions tab: category bar over a grid of transition kinds, dragged onto clip overlaps.
Item {
    id: root

    // Bumped when an addon changes the transitions on disk (an imported .driftfx, a pack install).
    property int catalogTick: 0
    readonly property var ownCategories: { void catalogTick; return EditorState.transitionCategories() }
    readonly property var catalog: { void catalogTick; return EditorState.transitionKinds() }
    readonly property string favoritesId: "__favorites__"
    readonly property string mineId: "__mine__"
    // Stock's transitions here too (0.22): Trending first (the most used), the rest spread over the
    // chips by category after the local cards, or in chips of their own («stock:<category>»).
    readonly property string trendsId: "__trends__"
    property int stockTick: 0
    readonly property var stockChips: {
        void root.stockTick
        return Market.authenticated ? Market.stockChips("transition", root.ownCategories.map(c => c.id))
                                    : ({ extra: [], categoriesOf: {} })
    }
    readonly property var categories: Market.configured
                                      ? [{ "id": root.trendsId, "label": qsTr("Trending") }].concat(root.ownCategories)
                                            .concat(root.stockChips.extra || [])
                                      : root.ownCategories
    readonly property var stockCategoriesHere: (root.stockChips.categoriesOf || {})[root.activeCategory] || []
    readonly property bool showingStockOnly: root.query.length === 0
                                             && (root.activeCategory === root.trendsId
                                                 || root.activeCategory.indexOf("stock:") === 0)
    readonly property var stockFavorites: {
        void root.favoritesTick
        void Market.favoriteItemsRevision
        return root.activeCategory === root.favoritesId && root.query.length === 0
               ? Market.stockFavoriteItems(EditorState.assetFavoriteIds("transitions"), ["transition"], "transitions")
               : []
    }
    readonly property bool stockFooter: root.query.length === 0 && !root.showingStockOnly
                                        && (root.stockFavorites.length > 0 || root.stockCategoriesHere.length > 0)

    Connections {
        target: Market
        function onAuthChanged() { root.stockTick++ }
        function onCatalogChanged() { root.stockTick++ }
    }

    // A Stock transition installs as "stock.<id>" (tools/transitions_stock › package_id).
    function stockKind(item) {
        const placed = Market.placedId(item.id)
        if (placed.length > 0)
            return placed
        const slug = String(item.id || "").split(":").pop().toLowerCase()
        return "stock." + slug.replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "")
    }
    function stockInstalled(item) {
        void root.catalogTick
        const kind = root.stockKind(item)
        return root.catalog.some(t => t.kind === kind)
    }
    function applyKind(kind) {
        if (EditorState.selectedTransitionTrack >= 0)
            EditorState.addTransition(EditorState.selectedTransitionTrack,
                                      EditorState.selectedTransitionLeftClip, kind, 0.5)
        else if (EditorState.selectedClip >= 0)
            EditorState.addTransition(EditorState.selectedTrack, EditorState.selectedClip, kind, 0.5)
        else
            Toasts.info(qsTr("Select the first of the two clips on the timeline."))
    }
    function applyStock(item) {
        root.catalogTick++
        root.applyKind(root.stockKind(item))
    }
    property string activeCategory: categories.length > 0 ? categories[0].id : ""
    property alias searchText: transitionSearch.text
    readonly property string query: transitionSearch.text.trim().toLowerCase()
    property int favoritesTick: 0

    Connections {
        target: Addons
        function onKindChanged(kind) {
            if (kind === "transitions")
                root.catalogTick++
        }
    }

    Connections {
        target: EditorState
        function onAssetFavoritesChanged() {
            root.favoritesTick++
        }
    }

    // Search spans every category — once you have a name, the sectors are in the way.
    readonly property var visibleTransitions: {
        void root.favoritesTick
        const q = root.query
        if (q.length > 0) {
            return root.catalog.filter(function(item) {
                const label = (item.label || "").toLowerCase()
                const kind = (item.kind || "").toLowerCase()
                return label.indexOf(q) >= 0 || kind.indexOf(q) >= 0
            })
        }
        if (root.activeCategory === root.favoritesId) {
            return root.catalog.filter(function(item) {
                return EditorState.isAssetFavorite("transitions", item.kind)
            })
        }
        if (root.activeCategory === root.mineId)
            return root.catalog.filter(function(item) { return item.user === true })
        if (root.activeCategory === root.trendsId || root.activeCategory.indexOf("stock:") === 0)
            return []
        return root.catalog.filter(function(item) {
            return item.category === root.activeCategory
        })
    }

    Column {
        anchors.fill: parent
        spacing: 0
        AssetSearchBar {
            id: transitionSearch
            placeholderText: qsTr("Search transitions")

            IconButton {
                glyph: Theme.icons.download
                variant: "ghost"
                buttonSize: Theme.controlHeight
                tooltip: qsTr("Install a custom transition or effect from a .driftfx file made in Drift Forge")
                onClicked: root.Window.window.importUserPackage("")
            }
        }

        // AI transition (RIFE): the selected clip blends into the one after it.
        Rectangle {
            id: aiTransitionCard
            x: Theme.pagePadding
            width: parent.width - Theme.pagePadding * 2
            height: 40
            radius: Theme.radiusSm
            color: aiCardHover.hovered ? Theme.panelAccent : Theme.panelSecondaryBg
            border.width: Theme.borderWidth
            border.color: Theme.panelSecondaryBorder
            Row {
                anchors.left: parent.left
                anchors.leftMargin: Theme.spacingLg
                anchors.verticalCenter: parent.verticalCenter
                spacing: Theme.spacingMd
                IconGlyph {
                    anchors.verticalCenter: parent.verticalCenter
                    glyph: Theme.icons.sparkles
                    iconSize: Theme.iconSizeMd
                    iconColor: Theme.primary
                }
                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: qsTr("AI transition")
                    color: Theme.foreground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSm
                    font.weight: Font.Medium
                }
                AiBadge {
                    anchors.verticalCenter: parent.verticalCenter
                    info: qsTr("Select a clip: the AI draws the pictures between its last frame and the first frame of the next clip, and puts them in between.")
                }
            }
            HoverHandler { id: aiCardHover; cursorShape: Qt.PointingHandCursor }
            TapHandler {
                onTapped: {
                    if (!EditorState.aiTransitionAvailable())
                        root.Window.window.openAddonManager("interp-model")
                    else if (EditorState.selectedTrack < 0 || EditorState.selectedClip < 0)
                        Toasts.info(qsTr("Select the first of the two clips on the timeline."))
                    else
                        EditorState.addAiTransitionAfter(EditorState.selectedTrack, EditorState.selectedClip)
                }
            }
        }

        Item { width: 1; height: Theme.spacingSm }

        AssetCategoryChips {
            id: transitionCategoryChips
            width: parent.width
            categories: root.categories
            activeCategory: root.activeCategory
            showMine: true
            mineLabel: qsTr("My Transitions")
            searching: root.query.length > 0
            onCategoryActivated: (categoryId) => root.activeCategory = categoryId
        }

        Item {
            width: parent.width
            height: Math.max(0, parent.height - transitionSearch.height
                             - Theme.spacingSm - transitionCategoryChips.height - aiTransitionCard.height)

            // A category whose filter matches nothing used to leave a
            // blank scroll area with no explanation.
            EmptyState {
                anchors.centerIn: parent
                width: Math.min(parent.width - Theme.spacing3xl, 260)
                visible: root.ownCategories.length === 0 && !root.showingStockOnly
                glyph: Theme.icons.chevronsRight
                title: qsTr("No transitions available")
                hint: qsTr("Install a transitions pack to add more.")
                actionText: qsTr("Get extras")
                onActionTriggered: root.Window.window.openAddonManager()
            }

            // Trending, or a chip of Stock's own: Stock's cards only.
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
                    type: "transition"
                    categories: root.activeCategory === root.trendsId ? [] : root.stockCategoriesHere
                    glyph: Theme.icons.chevronsRight
                    isInstalled: function(item) { return root.stockInstalled(item) }
                    apply: function(item) { root.applyStock(item) }
                }
            }

            EmptyState {
                anchors.centerIn: parent
                width: Math.min(parent.width - Theme.spacing3xl, 260)
                visible: root.categories.length > 0
                         && root.visibleTransitions.length === 0 && !root.showingStockOnly && !root.stockFooter
                compact: true
                glyph: Theme.icons.search
                title: root.query.length > 0
                       ? qsTr("No transitions match “%1”").arg(transitionSearch.text.trim())
                       : (root.activeCategory === root.mineId
                          ? qsTr("No custom transitions yet")
                          : root.activeCategory === root.favoritesId
                          ? qsTr("No favorites yet")
                          : qsTr("Nothing in this category"))
                hint: root.query.length > 0
                      ? qsTr("Try a different name.")
                      : (root.activeCategory === root.mineId
                         ? qsTr("Import a .driftfx file made in Drift Forge to add your own.")
                         : root.activeCategory === root.favoritesId
                         ? qsTr("Star transitions to save them here.")
                         : qsTr("Pick another category."))
                actionText: root.activeCategory === root.mineId && root.query.length === 0
                            ? qsTr("Import") : ""
                onActionTriggered: root.Window.window.importUserPackage("")
            }

            FontMetrics {
                id: labelMetrics
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeCard
                font.weight: Font.Medium
            }

            // Past the end of a category, the wheel goes on into the next one (CapCut).
            CategoryScrollOn {
                anchors.fill: transitionGrid
                flickable: transitionGrid
                categories: root.categories
                activeCategory: root.activeCategory
                active: root.query.length === 0
                onCategoryActivated: (categoryId) => root.activeCategory = categoryId
            }

            GridView {
                id: transitionGrid
                // As many columns as fit at the nominal card size, rounded, with the cards stretched or
                // squeezed a little to fill the row — a fixed card left a column's worth of empty space.
                readonly property int columnCount: Math.max(1, Math.round(width / (Theme.assetCardWidth + Theme.assetCardGap)))
                readonly property real cardSize: Math.floor(width / columnCount) - Theme.assetCardGap
                // One trailing gap wider than the padded area, so the last column's gap
                // fits and the cards pack from the left exactly as the old Grid did.
                x: Theme.pagePadding
                width: parent.width - Theme.pagePadding * 2 + Theme.assetCardGap
                height: parent.height
                topMargin: Theme.pagePadding
                bottomMargin: Theme.spacing3xl
                visible: root.categories.length > 0
                         && (root.visibleTransitions.length > 0 || root.stockFooter)
                clip: true
                reuseItems: true
                boundsBehavior: Flickable.StopAtBounds
                acceptedButtons: Theme.touchUi ? Qt.LeftButton : Qt.NoButton
                ScrollBar.vertical: AppScrollBar { }
                cellWidth: Math.floor(width / columnCount)
                cellHeight: transitionGrid.cardSize + 4 + Math.ceil(labelMetrics.height) * 2 + Theme.assetCardGap
                model: root.visibleTransitions

                // The chip's Stock cards after its own (and the starred ones in Favorites).
                footer: StockPanelCards {
                    width: transitionGrid.width - Theme.assetCardGap
                    visible: root.stockFooter
                    height: visible ? implicitHeight : 0
                    bare: true
                    flickable: transitionGrid
                    type: "transition"
                    categories: root.stockCategoriesHere
                    items: root.activeCategory === root.favoritesId ? root.stockFavorites : null
                    isInstalled: function(item) { return root.stockInstalled(item) }
                    apply: function(item) { root.applyStock(item) }
                }

                delegate: Column {
                    id: transitionCard
                    required property var modelData
                    width: transitionGrid.cardSize
                    spacing: 4
                    // Lift on grab — matches the media and effect cards.
                    opacity: transitionDrag.active ? 0.85 : 1
                    scale: transitionDrag.active ? 1.04 : (transitionHover.hovered ? 1.02 : 1.0)

                    GridView.onPooled: transitionCard.scrub = 0.45

                    function applyToSelection() {
                        const kind = transitionCard.modelData.kind
                        if (EditorState.selectedTransitionTrack >= 0)
                            EditorState.addTransition(EditorState.selectedTransitionTrack,
                                                      EditorState.selectedTransitionLeftClip, kind, 0.5)
                        else if (EditorState.selectedClip >= 0)
                            EditorState.addTransition(EditorState.selectedTrack, EditorState.selectedClip, kind, 0.5)
                    }

                    Behavior on opacity {
                        NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                    }
                    Behavior on scale {
                        NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                    }

                    readonly property string strip: transitionCard.modelData.previewStripPath || ""
                    readonly property int frameCount: Math.max(1, transitionCard.modelData.previewFrames || 1)

                    // Cards rest on a frame partway through the transition; hovering
                    // scrubs the whole strip, which is the only way to tell many of
                    // these apart (a crossfade and a dip look the same at p = 0.5).
                    property real scrub: 0.45
                    readonly property int frameIndex:
                        Math.max(0, Math.min(frameCount - 1, Math.round(scrub * (frameCount - 1))))

                    // Without hover there is no way to tell a crossfade from a dip
                    // to black — both rest on the same middle frame — so on touch
                    // every card scrubs continuously instead.
                    NumberAnimation on scrub {
                        running: transitionCard.frameCount > 1
                                 && (Theme.touchUi || transitionHover.hovered)
                        from: 0
                        to: 1
                        duration: 1400
                        loops: Animation.Infinite
                    }

                    Connections {
                        target: transitionHover
                        function onHoveredChanged() {
                            if (!transitionHover.hovered)
                                transitionCard.scrub = 0.45
                        }
                    }

                    Drag.active: transitionDrag.active
                    Drag.dragType: Drag.Automatic
                    Drag.supportedActions: Qt.CopyAction
                    Drag.keys: ["application/x-drift-transition"]
                    Drag.mimeData: ({ "application/x-drift-transition": transitionCard.modelData.kind })
                    Drag.hotSpot.x: width / 2
                    Drag.hotSpot.y: transitionGrid.cardSize / 2

                    Rectangle {
                        width: transitionGrid.cardSize
                        height: transitionGrid.cardSize
                        radius: Theme.radiusSm
                        color: transitionHover.hovered ? Theme.panelSecondaryBg : Theme.panelAccent
                        border.width: transitionDrag.active ? Theme.borderWidth : 0
                        border.color: Theme.transitionOverlap
                        clip: true

                        // The card already had a considered hover
                        // scrub animation but no transition on its
                        // own colours.
                        Behavior on color {
                            ColorAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                        }
                        Behavior on border.width {
                            NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                        }

                        HoverHandler {
                            id: transitionHover
                            cursorShape: Qt.PointingHandCursor
                        }

                        ThemedToolTip {
                            text: qsTr("%1 — click to swap the selected transition for it, or drag it onto where two clips meet (on touch, hold then drag)").arg(transitionCard.modelData.label)
                            visible: transitionHover.hovered
                        }

                        TapHandler {
                            acceptedButtons: Qt.RightButton
                            onTapped: cardMenu.popup()
                        }

                        // Click: swaps the selected transition for this one (keeping its length),
                        // or adds it after the selected clip. Dragging still picks any join.
                        TapHandler {
                            acceptedButtons: Qt.LeftButton
                            acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad | PointerDevice.Stylus
                            onTapped: transitionCard.applyToSelection()
                        }

                        DragHandler {
                            id: transitionDrag
                            target: null
                            // A finger lifts through TouchDrag instead: a platform
                            // drag has no touch gesture and cannot leave the sheet.
                            acceptedButtons: Qt.LeftButton
                            acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad | PointerDevice.Stylus
                        }

                        // Hold to carry the transition onto the join between two
                        // clips. This used to be a tap that applied to whatever was
                        // selected, which gave no say over which boundary it landed on.
                        TouchLiftArea {
                            dragKind: "transition"
                            payload: transitionCard.modelData.kind
                            label: transitionCard.modelData.label
                            glyph: Theme.icons.chevronsRight
                            onLiftTapped: cardMenu.popup()
                        }

                        ThemedContextMenu {
                            id: cardMenu

                            property bool favorited: false

                            onAboutToShow: favorited = EditorState.isAssetFavorite("transitions", transitionCard.modelData.kind)

                            ThemedMenuItem {
                                text: EditorState.selectedTransitionTrack >= 0
                                      ? qsTr("Replace the selected transition")
                                      : qsTr("Add after the selected clip")
                                icon.name: Theme.icons.chevronsRight
                                enabled: EditorState.selectedTransitionTrack >= 0 || EditorState.selectedClip >= 0
                                onTriggered: transitionCard.applyToSelection()
                            }

                            ThemedMenuItem {
                                text: cardMenu.favorited ? qsTr("Remove from favorites") : qsTr("Add to favorites")
                                icon.name: Theme.icons.star
                                onTriggered: EditorState.toggleAssetFavorite("transitions", transitionCard.modelData.kind)
                            }
                        }

                        AssetFavoriteButton {
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.margins: 3
                            tabId: "transitions"
                            itemId: transitionCard.modelData.kind
                        }

                        SkeletonBox {
                            anchors.fill: parent
                            visible: transitionCard.strip.length > 0
                                     && transitionStrip.status === Image.Loading
                        }

                        // The strip is one row of square cells; slide it rather than
                        // re-decoding a sourceClipRect per frame.
                        Image {
                            id: transitionStrip
                            visible: transitionCard.strip.length > 0
                                     && status === Image.Ready
                            source: transitionCard.strip.length > 0
                                    ? EditorState.imageUrl(transitionCard.strip) : ""
                            height: parent.height
                            width: parent.height * transitionCard.frameCount
                            x: -transitionCard.frameIndex * parent.height
                            // Height only: the width follows the strip's aspect, so each
                            // frame stays a whole cell.
                            sourceSize.height: Math.ceil(parent.height * Screen.devicePixelRatio)
                            fillMode: Image.Stretch
                            asynchronous: true
                            smooth: true
                        }

                        IconGlyph {
                            anchors.centerIn: parent
                            visible: transitionCard.strip.length === 0
                                     || transitionStrip.status === Image.Error
                            glyph: Theme.icons.chevronsRight
                            iconSize: Theme.iconSizeXl
                            iconColor: Theme.transitionOverlap
                        }
                    }

                    Text {
                        width: parent.width
                        text: transitionCard.modelData.label
                        color: Theme.panelForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeCard
                        font.weight: Font.Medium
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                        maximumLineCount: 2
                        elide: Text.ElideRight
                    }
                }
            }
        }
    }
}
