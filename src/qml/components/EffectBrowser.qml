import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift
import "assets"

// Browsable effect preset picker: category chips + card grid.
// Drag a card onto a timeline clip, or click / tap + to apply to the selection.
Column {
    id: root
    // The panel's sidebar drives the category (0.23): its chips are not shown.
    property bool panelDriven: false
    spacing: 0

    readonly property string favoritesId: "__favorites__"
    readonly property string mineId: "__mine__"
    // Effects › Trending (first, as in Filmora and CapCut): Stock's effects. Installed ones carry the
    // category "trending" and an id "stockfx_<item>", and are listed here instead of in a chip of their own.
    readonly property string trendsId: "__trends__"
    // The Stock type this browser shows as its own (0.22): Stock's effects in Effects, its looks in
    // Filters › Color effects. Its Trending is that type's most used, and the rest of it is spread
    // over these chips by category (or chips of its own, «stock:<category>»), after the local cards.
    property string stockType: "effect"
    // Effects › Overlays: Stock's overlays, a chip of their own after Trending.
    readonly property string overlaysId: "__stock_overlays__"
    readonly property bool showOverlays: root.stockType === "effect"
    // Bumped when an addon changes the effects on disk (an imported .driftfx, a pack install).
    property int catalogTick: 0
    // Bumped when Stock's categories come in, or the account changes.
    property int stockTick: 0
    readonly property var ownCategories: { void catalogTick; return EditorState.effectCategories().filter(c => c.id !== "trending") }
    readonly property var stockChips: {
        void root.stockTick
        return Market.authenticated ? Market.stockChips(root.stockType, root.ownCategories.map(c => ({ "id": c.id, "label": c.label })))
                                    : ({ extra: [], categoriesOf: {} })
    }
    readonly property var categories: {
        if (!Market.configured)
            return root.ownCategories
        const head = [{ "id": root.trendsId, "label": qsTr("Trending") }]
        if (root.showOverlays)
            head.push({ "id": root.overlaysId, "label": qsTr("Overlays") })
        return head.concat(root.ownCategories).concat(root.stockChips.extra || [])
    }
    // The Stock categories the open chip gathers (empty: none).
    readonly property var stockCategoriesHere: (root.stockChips.categoriesOf || {})[root.activeCategory] || []
    // A chip of Stock's own, or Overlays: only Stock cards, in their own view.
    readonly property bool showingStockOnly: root.query.length === 0
                                             && (root.activeCategory === root.overlaysId
                                                 || root.activeCategory.indexOf("stock:") === 0
                                                 || (root.activeCategory === root.trendsId && root.stockType !== "effect"))
    // Favorites: the starred Stock items too, drawn from what was kept when they were starred.
    readonly property var stockFavorites: {
        void root.favoritesTick
        void Market.favoriteItemsRevision
        if (root.activeCategory !== root.favoritesId || root.query.length > 0)
            return []
        if (root.stockType === "look")
            return Market.stockFavoriteItems(EditorState.assetFavoriteIds("looks"), ["look"], "looks")
        return Market.stockFavoriteItems(EditorState.assetFavoriteIds("effects"), ["effect", "overlay"], "effects")
            .concat(Market.stockFavoriteItems(EditorState.assetFavoriteIds("voices"), ["effect"], "voices"))
    }
    // After the local cards of a chip (or of Favorites): its Stock cards.
    readonly property bool stockFooter: root.query.length === 0 && !root.showingStockOnly
                                        && (root.stockFavorites.length > 0 || root.stockCategoriesHere.length > 0)
    readonly property var catalog: { void catalogTick; return EditorState.effectCatalog() }
    property string activeCategory: categories.length > 0 ? categories[0].id : ""
    property alias searchText: search.text
    readonly property string query: search.text.trim().toLowerCase()
    property int favoritesTick: 0

    Connections {
        target: Addons
        function onKindChanged(kind) {
            if (kind === "effects")
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
    readonly property var visiblePresets: {
        void root.favoritesTick
        const q = root.query
        if (q.length > 0) {
            return root.catalog.filter(function(preset) {
                const label = (preset.label || preset.displayName || "").toLowerCase()
                const id = (preset.id || "").toLowerCase()
                return label.indexOf(q) >= 0 || id.indexOf(q) >= 0
            })
        }
        if (root.activeCategory === root.favoritesId) {
            return root.catalog.filter(function(preset) {
                return EditorState.isAssetFavorite("effects", preset.id)
            })
        }
        if (root.activeCategory === root.mineId)
            return root.catalog.filter(function(preset) { return preset.user === true && !root.isStockEffect(preset.id) })
        if (root.activeCategory === root.trendsId || root.activeCategory === root.overlaysId
                || root.activeCategory.indexOf("stock:") === 0)
            return []
        return root.catalog.filter(function(preset) {
            return preset.category === root.activeCategory
        })
    }

    readonly property bool showingTrends: root.activeCategory === root.trendsId && root.query.length === 0
                                          && root.stockType === "effect"

    // What a Stock card does here once it is on this computer: an effect or a voice through
    // applyTrend, a look onto the selected clip, an overlay at the playhead.
    function stockInstalled(item) {
        if (Market.deliveryForItem(item) === "media") {
            const asset = Market.placedId(item.id)
            return asset.length > 0 && AssetLibrary.indexOfId(asset) >= 0
        }
        if (item.type === "look")
            return root.lookPresetId(item).length > 0
        return root.trendInstalled(item)
    }
    function lookPresetId(item) {
        void root.presetsTick
        const placed = Market.placedId(item.id)
        if (placed.length > 0 && EditorState.userEffectPresets().some(p => p.id === placed))
            return placed
        return root.voicePresetId(item)
    }
    function applyStock(item) {
        if (Market.deliveryForItem(item) === "media") {
            EditorState.addAssetClipWhenReady(Market.placedId(item.id))
            return
        }
        if (item.type === "look") {
            if (EditorState.selectedClip < 0) {
                EditorState.setLastMessage(qsTr("Select a clip to apply the look"), "info")
                return
            }
            EditorState.applyEffectPreset(EditorState.selectedTrack, EditorState.selectedClip, root.lookPresetId(item))
            return
        }
        root.applyTrend(item)
    }

    function isStockEffect(effectId) {
        return (effectId || "").indexOf("stockfx_") === 0
    }
    // The effect id a Stock item installs as ("flip:effect:luz-del-sol-05" -> stockfx_luz_del_sol_05).
    function stockEffectId(item) {
        const slug = String(item.id || "").split(":").pop().toLowerCase()
        return "stockfx_" + slug.replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "")
    }
    function trendInstalled(item) {
        void root.catalogTick
        if (Market.deliveryForItem(item) === "effect-preset")
            return root.voicePresetId(item).length > 0
        const id = root.stockEffectId(item)
        return root.catalog.some(p => p.id === id)
    }
    // Voice effects come as effect presets (audio only), labelled with their Spanish name, which is
    // also the item's id ("flip:effect:ardilla-listada" <- "Ardilla listada"): found again by it in
    // any UI language.
    property int presetsTick: 0
    function slugOf(text) {
        return String(text || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
            .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "")
    }
    function voicePresetId(item) {
        void root.presetsTick
        const slug = String(item.id || "").split(":").pop()
        const preset = EditorState.userEffectPresets().find(p => root.slugOf(p.label) === slug)
        return preset ? preset.id : ""
    }

    // Trending: fetched when first shown (and again after signing in). A click on one that is not
    // installed downloads it and applies it when it lands.
    property var pendingTrendIds: ({})
    // Market.effectTrends copied here so a next page is appended without the grid jumping back to
    // the top (a bound model resets on every change).
    property var trendItems: []
    function showTrends() {
        const before = root.trendItems
        const next = Market.effectTrends
        const appended = before.length > 0 && next.length > before.length && next[0].id === before[0].id
        const y = trendsGrid.contentY
        root.trendItems = next
        if (appended) {
            trendsGrid.forceLayout()
            trendsGrid.contentY = y
        }
    }
    function ensureTrends() {
        if (root.activeCategory === root.trendsId && root.stockType === "effect" && Market.authenticated
                && Market.effectTrends.length === 0
                && !Market.effectTrendsLoading)
            Market.fetchEffectTrends()
    }
    onActiveCategoryChanged: ensureTrends()
    Component.onCompleted: {
        trendItems = Market.effectTrends
        ensureTrends()
    }
    function applyTrend(item) {
        if (Market.deliveryForItem(item) === "effect-preset") {
            if (EditorState.selectedClip < 0) {
                EditorState.setLastMessage(qsTr("Select a clip with sound to change its voice"), "info")
                return
            }
            EditorState.applyEffectPreset(EditorState.selectedTrack, EditorState.selectedClip, root.voicePresetId(item))
            return
        }
        root.applyPreset(root.stockEffectId(item))
    }
    function useTrend(item) {
        if (root.trendInstalled(item)) {
            root.applyTrend(item)
            return
        }
        const job = Market.downloadInfo(item.id)
        if (["waiting", "queued", "processing", "downloading", "importing"].indexOf(job.status) >= 0)
            return
        const pending = Object.assign({}, root.pendingTrendIds)
        pending[item.id] = true
        root.pendingTrendIds = pending
        Market.download(item.id, "", "", item.title || "", item.media_kind || item.type || "")
    }
    function dropPending(itemId) {
        const pending = Object.assign({}, root.pendingTrendIds)
        delete pending[itemId]
        root.pendingTrendIds = pending
    }

    Connections {
        target: Market
        function onAuthChanged() {
            root.stockTick++
            root.ensureTrends()
        }
        function onCatalogChanged() { root.stockTick++ }
        function onEffectTrendsChanged() { root.showTrends() }
        function onDownloadInstalled(itemId, name, where) {
            if (!root.pendingTrendIds[itemId])
                return
            root.dropPending(itemId)
            root.catalogTick++
            root.presetsTick++
            const item = Market.itemById(itemId)
            if (item && item.id && root.trendInstalled(item))
                root.applyTrend(item)
        }
        function onDownloadFailed(itemId, code, message) {
            if (root.pendingTrendIds[itemId])
                root.dropPending(itemId)
        }
    }

    Connections {
        target: EditorState
        function onUserEffectPresetsChanged() { root.presetsTick++ }
    }

    function applyPreset(effectId) {
        if (EditorState.selectedClip < 0) {
            EditorState.addAdjustmentClipWithEffect(effectId, -1, -1)
            return
        }
        EditorState.addEffect(EditorState.selectedTrack, EditorState.selectedClip, effectId)
    }

    // With the effects pack uninstalled the catalog is empty, activeCategory falls
    // back to "" and the grid rendered nothing — a blank panel with a stray tip line,
    // while the sibling audio and transitions tabs both offered an install CTA.
    // Startup now prompts for these packs and users can decline, so uninstalled is a
    // normal first-run state rather than an edge case.
    EmptyState {
        width: parent.width
        height: visible ? root.height : 0
        visible: root.catalog.length === 0
        glyph: Theme.icons.wand
        title: qsTr("No effects")
        hint: qsTr("Install the Effects pack from Extras to browse presets here.")
        actionText: qsTr("Get extras")
        onActionTriggered: root.Window.window.openAddonManager()
    }

    Column {
        visible: root.catalog.length > 0
        width: parent.width
        height: parent.height
        spacing: 0

        AssetSearchBar {
            id: search
            placeholderText: qsTr("Search effects")

            // With its name, so it is found: the same layer the timeline bar adds.
            IconButton {
                glyph: "layers"
                text: qsTr("Adjustment layer")
                variant: "ghost"
                buttonSize: Theme.controlHeight
                tooltip: qsTr("Add adjustment layer — click, or drag it onto a track")
                down: adjustmentDrag.pressed

                // Tap adds at the playhead as before; drag places it on a track.
                AssetDragSource {
                    id: adjustmentDrag
                    anchors.fill: parent
                    kind: "adjustment"
                    payload: "videoEffects"
                    label: qsTr("Adjustment layer")
                    glyph: "layers"
                    onTapped: EditorState.addAdjustmentClip(-1, -1)
                }
            }

            IconButton {
                glyph: Theme.icons.download
                variant: "ghost"
                buttonSize: Theme.controlHeight
                tooltip: qsTr("Install a custom effect or transition from a .driftfx file made in Drift Forge")
                onClicked: root.Window.window.importUserPackage("")
            }
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
            showMine: true
            mineLabel: qsTr("My Effects")
            searching: root.query.length > 0
            onCategoryActivated: (categoryId) => root.activeCategory = categoryId
        }

        Item {
            width: parent.width
            height: Math.max(0, parent.height - search.height - Theme.spacingSm
                             - categoryChips.height)

            Text {
                id: emptySearchHint
                x: 12
                y: 12
                width: parent.width - 24
                visible: root.visiblePresets.length === 0 && !root.showingTrends && !root.showingStockOnly
                         && !root.stockFooter
                         && !(root.activeCategory === root.mineId && root.query.length === 0)
                text: root.query.length > 0
                      ? qsTr("No effects match “%1”.").arg(search.text.trim())
                      : (root.activeCategory === root.mineId
                         ? qsTr("Nothing here yet. Import a .driftfx file to add your own.")
                         : root.activeCategory === root.favoritesId
                         ? qsTr("No favorites yet. Star presets to save them here.")
                         : qsTr("Nothing in this category."))
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                wrapMode: Text.WordWrap
            }

            // Nothing imported yet: the Import call to action sits in the middle of the panel.
            EmptyState {
                anchors.centerIn: parent
                width: Math.min(parent.width - Theme.spacing3xl, 260)
                visible: root.activeCategory === root.mineId && root.visiblePresets.length === 0
                         && root.query.length === 0
                compact: true
                glyph: Theme.icons.download
                title: qsTr("%1 is empty").arg(qsTr("My Effects"))
                hint: qsTr("Import a .driftfx file made in Drift Forge to add your own.")
                actionText: qsTr("Import")
                onActionTriggered: root.Window.window.importUserPackage("")
            }

            GridView {
                id: trendsGrid
                // Wide cards: Stock's effect cards are 16:9, like Filmora's.
                readonly property int columnCount: Math.max(1, Math.round(width / (Theme.assetCardWidth * 1.35 + Theme.assetCardGap)))
                readonly property real cardWidth: Math.floor(width / columnCount) - Theme.assetCardGap
                x: 12
                width: parent.width - 24 + Theme.assetCardGap
                height: parent.height
                topMargin: 12
                bottomMargin: 12
                clip: true
                reuseItems: true
                boundsBehavior: Flickable.StopAtBounds
                acceptedButtons: Theme.touchUi ? Qt.LeftButton : Qt.NoButton
                ScrollBar.vertical: AppScrollBar { }
                cellWidth: Math.floor(width / columnCount)
                cellHeight: Math.round(cardWidth * 9 / 16) + 4 + Math.ceil(labelMetrics.height) + Theme.assetCardGap
                visible: root.showingTrends && Market.authenticated && root.trendItems.length > 0
                model: root.trendItems
                // The next page a little before the end, so scrolling does not stop at it.
                onContentYChanged: {
                    if (Market.effectTrendsHasMore && !Market.effectTrendsLoading
                            && contentY + height > contentHeight - cellHeight * 3)
                        Market.fetchEffectTrends(true)
                }

                delegate: Column {
                    id: trendCard
                    required property var modelData
                    readonly property bool installed: root.trendInstalled(modelData)
                    readonly property string effectId: root.stockEffectId(modelData)
                    readonly property bool voice: Market.deliveryForItem(modelData) === "effect-preset"
                    width: trendsGrid.cardWidth
                    spacing: 4

                    StockThumb {
                        id: trendThumb
                        width: parent.width
                        height: Math.round(width * 9 / 16)
                        item: trendCard.modelData
                        showDuration: false
                        onOpenRequested: root.useTrend(trendCard.modelData)

                        // Not downloaded yet (Filmora's mark).
                        Rectangle {
                            visible: !trendCard.installed && !trendThumb.busy
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom
                            anchors.margins: Theme.spacingXs
                            width: 20
                            height: 20
                            radius: width / 2
                            color: Theme.scrimStrong
                            IconGlyph {
                                anchors.centerIn: parent
                                glyph: Theme.icons.download
                                iconSize: 12
                                iconColor: Theme.onMedia
                            }
                        }

                        // Downloaded: drag it onto a clip like any other effect.
                        AssetDragSource {
                            anchors.fill: parent
                            enabled: trendCard.installed && !trendCard.voice
                            visible: enabled
                            kind: "effect"
                            payload: trendCard.effectId
                            label: trendCard.modelData.title || ""
                            glyph: Theme.icons.wand
                            onTapped: root.useTrend(trendCard.modelData)
                        }


                        HoverHandler { id: trendHover }
                        ThemedToolTip {
                            text: trendCard.voice
                                  ? qsTr("%1 — click to apply it to the selected clip's voice").arg(trendCard.modelData.title || "")
                                  : trendCard.installed
                                    ? (EditorState.selectedClip >= 0
                                       ? qsTr("%1 — click to apply to the selection, or drag onto a clip").arg(trendCard.modelData.title || "")
                                       : qsTr("%1 — click to add as an adjustment layer, or drag onto a clip").arg(trendCard.modelData.title || ""))
                                    : qsTr("%1 — click to download it and apply it").arg(trendCard.modelData.title || "")
                            visible: trendHover.hovered && !trendThumb.busy
                        }
                    }

                    Text {
                        width: parent.width
                        text: trendCard.modelData.title || ""
                        elide: Text.ElideRight
                        horizontalAlignment: Text.AlignHCenter
                        color: trendHover.hovered ? Theme.panelForeground : Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeCard
                        font.weight: Font.Medium
                    }
                }
            }

            // Trending before there is anything to show: signed out, loading, or the request failed.
            EmptyState {
                anchors.centerIn: parent
                width: Math.min(parent.width - Theme.spacing3xl, 260)
                visible: root.showingTrends && (!Market.authenticated || root.trendItems.length === 0)
                compact: true
                glyph: Theme.icons.wand
                title: !Market.authenticated ? qsTr("Sign in to see trending effects")
                                             : (Market.effectTrendsLoading ? qsTr("Loading trending effects…")
                                                                           : qsTr("Couldn’t load trending effects"))
                hint: !Market.authenticated ? qsTr("Trending effects come from Stock, which needs your free account.") : ""
                actionText: !Market.authenticated ? (Account.busy ? qsTr("Waiting for the browser…") : qsTr("Sign in"))
                                                  : (Market.effectTrendsLoading ? "" : qsTr("Retry"))
                onActionTriggered: {
                    if (!Market.authenticated)
                        Account.signIn()
                    else
                        Market.fetchEffectTrends()
                }
            }

            // Overlays, a chip of Stock's own, or the looks' Trending: Stock's cards only.
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
                    y: 12
                    width: stockView.width
                    sidePadding: 12
                    flickable: stockView
                    type: root.activeCategory === root.overlaysId ? "overlay" : root.stockType
                    categories: root.activeCategory === root.overlaysId ? [""]
                              : root.activeCategory === root.trendsId ? [] : root.stockCategoriesHere
                    glyph: Theme.icons.wand
                    isInstalled: function(item) { return root.stockInstalled(item) }
                    apply: function(item) { root.applyStock(item) }
                }
            }

            FontMetrics {
                id: labelMetrics
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeCard
                font.weight: Font.Medium
            }

            FontMetrics {
                id: badgeMetrics
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs - 1
            }

            // One trailing gap wider than the padded area, so the cards pack from the left
            // exactly as the old Grid did. Rows are a fixed height (two label lines plus the
            // "Built-in" line) since a GridView can't size each row to its tallest card.
            // Past the end of a category, the wheel goes on into the next one (CapCut).
            CategoryScrollOn {
                anchors.fill: presetGrid
                flickable: presetGrid
                categories: root.categories
                activeCategory: root.activeCategory
                active: root.query.length === 0
                onCategoryActivated: (categoryId) => root.activeCategory = categoryId
            }

            GridView {
                id: presetGrid
                // As many columns as fit at the nominal card size, rounded, with the cards stretched or
                // squeezed a little to fill the row — a fixed card left a column's worth of empty space.
                readonly property int columnCount: Math.max(1, Math.round(width / (Theme.assetCardWidth + Theme.assetCardGap)))
                readonly property real cardSize: Math.floor(width / columnCount) - Theme.assetCardGap
                x: 12
                width: parent.width - 24 + Theme.assetCardGap
                height: parent.height
                topMargin: 12
                bottomMargin: 12
                visible: root.visiblePresets.length > 0 || root.stockFooter
                clip: true
                reuseItems: true
                boundsBehavior: Flickable.StopAtBounds
                acceptedButtons: Theme.touchUi ? Qt.LeftButton : Qt.NoButton
                ScrollBar.vertical: AppScrollBar { }
                cellWidth: Math.floor(width / columnCount)
                cellHeight: presetGrid.cardSize + 4 + Math.ceil(labelMetrics.height) * 2
                            + 4 + Math.ceil(badgeMetrics.height) + Theme.assetCardGap
                model: root.visiblePresets

                // The chip's Stock cards after its own (and the starred ones in Favorites).
                footer: StockPanelCards {
                    width: presetGrid.width - Theme.assetCardGap
                    visible: root.stockFooter
                    height: visible ? implicitHeight : 0
                    bare: true
                    flickable: presetGrid
                    type: root.stockType
                    categories: root.stockCategoriesHere
                    items: root.activeCategory === root.favoritesId ? root.stockFavorites : null
                    isInstalled: function(item) { return root.stockInstalled(item) }
                    apply: function(item) { root.applyStock(item) }
                }

                delegate: Column {
                    id: presetCard
                    required property var modelData
                    width: presetGrid.cardSize
                    spacing: 4
                    // Lift on grab: the card dims and grows slightly, so it reads
                    // as picked up rather than merely faded.
                    opacity: presetDrag.active ? 0.85 : 1
                    scale: presetDrag.active ? 1.04 : 1.0

                    Behavior on opacity {
                        NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                    }
                    Behavior on scale {
                        NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                    }

                    readonly property string thumb: presetCard.modelData.thumbnailPath || ""
                    readonly property bool hasBefore: thumb.length > 0 && (presetCard.modelData.beforeImage || "").length > 0

                    Drag.active: presetDrag.active
                    Drag.dragType: Drag.Automatic
                    Drag.supportedActions: Qt.CopyAction
                    Drag.keys: ["application/x-drift-effect"]
                    Drag.mimeData: ({ "application/x-drift-effect": presetCard.modelData.id })
                    Drag.hotSpot.x: width / 2
                    Drag.hotSpot.y: presetGrid.cardSize / 2

                    Rectangle {
                        width: presetGrid.cardSize
                        height: presetGrid.cardSize
                        radius: Theme.radiusSm
                        color: cardHover.hovered ? Theme.panelSecondaryBg : Theme.panelAccent
                        border.width: presetDrag.active ? 1 : 0
                        border.color: Theme.primary
                        clip: true
                        // Matches the media cards in MediaAssetsTab, which already
                        // grow and animate on hover; these snapped.
                        scale: cardHover.hovered ? 1.03 : 1.0

                        Behavior on color {
                            ColorAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                        }
                        Behavior on scale {
                            NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                        }
                        Behavior on border.width {
                            NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                        }

                        HoverHandler { id: cardHover }

                        ThemedToolTip {
                            text: EditorState.selectedClip >= 0
                                  ? qsTr("%1 — click to apply to the selection, or drag onto a clip").arg(presetCard.modelData.label)
                                  : qsTr("%1 — click to add as an adjustment layer, or drag onto a clip").arg(presetCard.modelData.label)
                            visible: cardHover.hovered && !presetDrag.active
                        }

                        Image {
                            anchors.fill: parent
                            visible: presetCard.thumb.length > 0 && !presetCard.hasBefore
                            source: presetCard.thumb.length > 0 && !presetCard.hasBefore
                                    ? EditorState.imageUrl(presetCard.thumb) : ""
                            fillMode: Image.PreserveAspectCrop
                            asynchronous: true
                            sourceSize: Qt.size(Math.ceil(presetGrid.cardSize * Screen.devicePixelRatio), Math.ceil(presetGrid.cardSize * Screen.devicePixelRatio))
                            smooth: true
                        }

                        // Under the pointer: the photo the thumbnail was drawn on, wiping to the
                        // effect, as Filters does with the looks (0.18).
                        BeforeAfterImage {
                            anchors.fill: parent
                            visible: presetCard.hasBefore
                            beforeSource: presetCard.hasBefore ? presetCard.modelData.beforeImage : ""
                            afterSource: presetCard.hasBefore ? EditorState.imageUrl(presetCard.thumb) : ""
                            playing: cardHover.hovered && !presetDrag.active
                        }

                        // Fallback when no thumbnail is present yet.
                        Text {
                            anchors.centerIn: parent
                            visible: presetCard.thumb.length === 0
                            width: parent.width - 12
                            text: presetCard.modelData.label
                            color: Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeCard
                            font.weight: Font.Medium
                            wrapMode: Text.WordWrap
                            horizontalAlignment: Text.AlignHCenter
                            maximumLineCount: 3
                            elide: Text.ElideRight
                        }

                        TapHandler {
                            // Finger taps arrive through TouchLiftArea below, which
                            // holds the grab this one would need.
                            enabled: !presetDrag.active
                            acceptedButtons: Qt.LeftButton
                            acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad | PointerDevice.Stylus
                            onTapped: root.applyPreset(presetCard.modelData.id)
                        }

                        TapHandler {
                            acceptedButtons: Qt.RightButton
                            onTapped: cardMenu.popup()
                        }

                        DragHandler {
                            id: presetDrag
                            target: null
                            // A finger lifts through TouchDrag instead: a platform
                            // drag has no touch gesture and cannot leave the sheet.
                            acceptedButtons: Qt.LeftButton
                            acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad | PointerDevice.Stylus
                        }

                        // Hold to carry the preset onto a specific clip; tap still
                        // applies it to the selection.
                        TouchLiftArea {
                            dragKind: "effect"
                            payload: presetCard.modelData.id
                            label: presetCard.modelData.label
                            thumbnail: presetCard.thumb
                            glyph: Theme.icons.wand
                            onLiftTapped: cardMenu.popup()
                        }

                        ThemedContextMenu {
                            id: cardMenu

                            property bool favorited: false

                            onAboutToShow: favorited = EditorState.isAssetFavorite("effects", presetCard.modelData.id)

                            ThemedMenuItem {
                                text: qsTr("Apply to selected clip")
                                icon.name: Theme.icons.plus
                                enabled: EditorState.selectedClip >= 0
                                onTriggered: root.applyPreset(presetCard.modelData.id)
                            }
                            ThemedMenuItem {
                                text: cardMenu.favorited ? qsTr("Remove from favorites") : qsTr("Add to favorites")
                                icon.name: Theme.icons.star
                                onTriggered: EditorState.toggleAssetFavorite("effects", presetCard.modelData.id)
                            }
                            ThemedMenuSeparator { visible: presetCard.modelData.user === true }
                            ThemedMenuItem {
                                visible: presetCard.modelData.user === true
                                text: qsTr("Delete from My Effects")
                                icon.name: Theme.icons.trash
                                onTriggered: deleteEffectDialog.openFor(presetCard.modelData)
                            }
                        }

                        AssetFavoriteButton {
                            anchors.left: parent.left
                            anchors.top: parent.top
                            anchors.margins: 3
                            tabId: "effects"
                            itemId: presetCard.modelData.id
                        }

                        IconButton {
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.margins: 3
                            glyph: Theme.icons.plus
                            variant: "ghost"
                            buttonSize: 18
                            iconSize: 12
                            tooltip: qsTr("Apply to selected clip")
                            enabled: EditorState.selectedClip >= 0
                            onClicked: root.applyPreset(presetCard.modelData.id)
                        }

                        // Imported effects only: built-in and add-on ones aren't the user's to delete.
                        IconButton {
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom
                            anchors.margins: 3
                            visible: presetCard.modelData.user === true
                                     && (cardHover.hovered || Theme.touchUi)
                            glyph: Theme.icons.trash
                            variant: "ghost"
                            buttonSize: 18
                            iconSize: 12
                            tooltip: qsTr("Delete from My Effects")
                            onClicked: deleteEffectDialog.openFor(presetCard.modelData)
                        }
                    }

                    Text {
                        width: parent.width
                        text: presetCard.modelData.label
                        color: Theme.panelForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeCard
                        font.weight: Font.Medium
                        horizontalAlignment: Text.AlignHCenter
                        elide: Text.ElideRight
                        maximumLineCount: 2
                        wrapMode: Text.WordWrap
                    }

                    Text {
                        width: parent.width
                        visible: presetCard.modelData.compositorOnly === true
                        text: qsTr("Built-in")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs - 1
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
            }
        }
        }

    ThemedDialog {
        id: deleteEffectDialog

        property string effectId: ""
        property string effectLabel: ""
        property int uses: 0

        title: qsTr("Delete effect")
        acceptText: qsTr("Delete")
        acceptVariant: "destructive"
        preferredWidth: Theme.dialogWidthSm
        acceptOnReturn: false

        function openFor(preset) {
            effectId = preset.id
            effectLabel = preset.label
            uses = EditorState.userEffectUses(preset.id)
            open()
        }

        onAccepted: EditorState.deleteUserEffect(deleteEffectDialog.effectId)

        contentItem: Text {
            width: parent ? parent.width : 320
            wrapMode: Text.WordWrap
            text: deleteEffectDialog.uses > 0
                  ? qsTr("Delete “%1” from My Effects? It is used %n time(s) in this project, and those clips will play without it.", "", deleteEffectDialog.uses)
                        .arg(deleteEffectDialog.effectLabel)
                  : qsTr("Delete “%1” from My Effects? You can import its .driftfx file again later.")
                        .arg(deleteEffectDialog.effectLabel)
            color: Theme.panelForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSm
        }
    }
}
