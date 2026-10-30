import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift
import ".."

// Text tab: click a style pack to drop a styled text clip on the timeline
// (placeholder copy + inline edit). Timed captions live under Subtitles.
// Trending (first, as in CapCut) lists every text style in Stock: one click downloads it and puts
// it at the playhead, and once downloaded it stays here. Styles the user saved from the
// properties Text tab sit behind the "My styles" chip.
Item {
    id: root
    // The panel's sidebar drives the category (0.23): its chips are not shown.
    property bool panelDriven: false

    // A clip landed on the timeline. The phone shell closes the sheet on this —
    // the thing you came for is behind it.
    signal added()

    // "trends", "builtin", "mine", or the id of a template category from Extras.
    // Trending needs an account: signed out it opened on a "Sign in" wall, so Basic comes first.
    property string section: Market.authenticated ? "trends" : "builtin"
    // For the panel's tree (0.23): the chips below as a list, and the one picked.
    property alias activeCategory: root.section
    readonly property var categories: [{ "id": "favorites", "label": qsTr("Favorites") },
                                       { "id": "trends", "label": qsTr("Trending") },
                                       { "id": "builtin", "label": qsTr("Basic") }]
        .concat(root.addonCategories.map(c => ({ "id": c.id, "label": c.label })))
        .concat((root.stockChips.extra || []).map(c => ({ "id": c.id, "label": c.label })))
        .concat([{ "id": "mine", "label": root.userPresets.length > 0 ? qsTr("My styles · %1").arg(root.userPresets.length)
                                                                     : qsTr("My styles") }])

    // Card label height, for the grids' cell heights.
    FontMetrics {
        id: labelMetrics
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeCard
        font.weight: Font.Medium
    }

    readonly property var presets: EditorState.textPresets()

    // Template packs from Extras, by category, each behind its own chip.
    property var addonPresets: EditorState.addonTextPresets()
    property var addonCategories: EditorState.addonTextPresetCategories()
    // Starred styles, from the built-in set and every template pack.
    property int favoritesTick: 0
    // A search (0.22.1) looks through every style on this computer, whatever the section.
    readonly property string query: titleSearch.text.trim()
    readonly property bool searching: query.length > 0
    function foldText(text) {
        return String(text).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
    }
    readonly property var gridPresets: {
        if (root.searching) {
            void root.userPresetsTick
            const q = root.foldText(root.query)
            return root.presets.concat(root.addonPresets).concat(EditorState.userTextPresets())
                .filter(p => root.foldText(p.label || "").indexOf(q) >= 0)
        }
        if (section === "builtin")
            return root.presets
        if (section === "favorites") {
            void root.favoritesTick
            return root.presets.concat(root.addonPresets).filter(p => EditorState.isAssetFavorite("textStyles", p.id))
        }
        if (root.section.indexOf("stock:") === 0)
            return []
        return root.addonPresets.filter(p => p.category === root.section)
    }

    // Stock's text styles also in these chips by category (0.22), after the local cards; the ones
    // with no chip here in chips of their own («stock:<category>», named as Stock names them).
    // Trending keeps the most used.
    property int stockTick: 0
    // A text or subtitle is selected: the cards' menus can put their look on it.
    readonly property bool selectedTextClip: EditorState.selectedClip >= 0
                                             && (EditorState.selectedClipData.kind === "text"
                                                 || EditorState.selectedClipData.kind === "subtitle")
    readonly property var stockChips: {
        void root.stockTick
        return Market.authenticated
               ? Market.stockChips("text-style", [{ "id": "builtin", "label": qsTr("Basic") }].concat(root.addonCategories.map(c => ({ "id": c.id, "label": c.label }))))
               : ({ extra: [], categoriesOf: {} })
    }
    readonly property var stockCategoriesHere: (root.stockChips.categoriesOf || {})[root.section] || []
    readonly property bool showingStockOnly: root.section.indexOf("stock:") === 0
    readonly property var stockFavorites: {
        void root.favoritesTick
        void Market.favoriteItemsRevision
        return root.section === "favorites"
               ? Market.stockFavoriteItems(EditorState.assetFavoriteIds("textStyles"), ["text-style"], "textStyles")
               : []
    }
    readonly property bool stockFooter: !root.showingStockOnly
                                        && (root.stockFavorites.length > 0 || root.stockCategoriesHere.length > 0)
    function stockInstalled(item) {
        void root.userPresetsTick
        return EditorState.stockTextPresetId(item.id).length > 0
    }
    function applyStock(item) {
        const presetId = EditorState.stockTextPresetId(item.id)
        if (presetId.length === 0)
            return
        EditorState.addTextClip("", -1, presetId)
        root.added()
    }

    Connections {
        target: Addons
        function onKindChanged(kind) {
            if (kind !== "text-styles")
                return
            root.addonPresets = EditorState.addonTextPresets()
            root.addonCategories = EditorState.addonTextPresetCategories()
            if (root.section !== "builtin" && root.section !== "mine" && root.section !== "trends"
                    && root.section !== "favorites" && !root.addonCategories.some(c => c.id === root.section))
                root.section = "builtin"
        }
    }

    // A QVariantList from an invokable is not reactive, so the section is refreshed by poking
    // this counter from the controller's signal.
    property int userPresetsTick: 0
    // Styles installed from Stock are listed under Trending, not here.
    readonly property var userPresets: {
        void root.userPresetsTick
        return EditorState.userTextPresets().filter(p => !p.stockId)
    }

    // Trending: Stock's text styles, fetched when the section is first shown (and again after
    // signing in). Clicking one that is not installed downloads it and, when it lands, adds it.
    property var pendingTrendIds: ({})
    // Market.textTrends copied here so a next page is appended without the grid jumping back to
    // the top (a bound model resets on every change).
    property var trendItems: []
    function showTrends() {
        const before = root.trendItems
        const next = Market.textTrends
        const appended = before.length > 0 && next.length > before.length && next[0].id === before[0].id
        const y = trendsGrid.contentY
        root.trendItems = next
        if (appended) {
            trendsGrid.forceLayout()
            trendsGrid.contentY = y
        }
    }
    function ensureTrends() {
        if (root.section === "trends" && Market.authenticated && Market.textTrends.length === 0
                && !Market.textTrendsLoading)
            Market.fetchTextTrends()
    }
    onSectionChanged: ensureTrends()
    Component.onCompleted: {
        trendItems = Market.textTrends
        ensureTrends()
    }
    function installedTrendId(item) {
        void root.userPresetsTick
        return EditorState.stockTextPresetId(item.id)
    }
    function useTrend(item) {
        const presetId = root.installedTrendId(item)
        if (presetId.length > 0) {
            EditorState.addTextClip("", -1, presetId)
            root.added()
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
        function onTextTrendsChanged() { root.showTrends() }
        function onDownloadInstalled(itemId, name, where) {
            if (!root.pendingTrendIds[itemId])
                return
            root.dropPending(itemId)
            const presetId = EditorState.stockTextPresetId(itemId)
            if (presetId.length > 0) {
                EditorState.addTextClip("", -1, presetId)
                root.added()
            }
        }
        function onDownloadFailed(itemId, code, message) {
            if (root.pendingTrendIds[itemId])
                root.dropPending(itemId)
        }
    }

    Connections {
        target: EditorState
        function onUserTextPresetsChanged() { root.userPresetsTick++ }
        function onAssetFavoritesChanged() { root.favoritesTick++ }
    }

    readonly property string styleFileFilter: qsTr("Flip Studio text style (*.drifttextstyle)")

    function importStyle() {
        const url = FileDialogs.openFile(qsTr("Import text style"), [root.styleFileFilter])
        if (url.toString().length > 0) {
            EditorState.importUserTextPreset(url)
            root.section = "mine"
        }
    }

    function exportStyle(preset) {
        const url = FileDialogs.saveFile(qsTr("Export text style"), [root.styleFileFilter],
                                         preset.label, "drifttextstyle")
        if (url.toString().length > 0)
            EditorState.exportUserTextPreset(preset.id, url)
    }

    Item {
        id: toolbar
        width: parent.width
        height: Theme.pagePadding + titleSearch.height + Theme.spacingSm + (chips.visible ? chips.height : 0)
                + Theme.spacingMd + aiText.height

        ThemedTextField {
            id: titleSearch
            x: Theme.pagePadding
            y: Theme.pagePadding
            width: parent.width - Theme.pagePadding * 2 - Theme.controlHeight - Theme.spacingSm
            placeholderText: qsTr("Search text styles")
        }

        // Wraps: with template packs installed there is a chip per category.
        Flow {
            id: chips
            x: Theme.pagePadding
            y: titleSearch.y + titleSearch.height + Theme.spacingSm
            visible: !root.searching
            width: parent.width - Theme.pagePadding * 2 - Theme.controlHeight - Theme.spacingSm
            spacing: Theme.spacingSm

            IconButton {
                visible: !root.panelDriven
                glyph: Theme.icons.star
                variant: "ghost"
                buttonSize: Theme.controlHeightSm
                iconSize: 14
                active: root.section === "favorites"
                tooltip: qsTr("Favorites")
                onClicked: root.section = "favorites"
            }

            ThemedChip {
                visible: !root.panelDriven
                text: qsTr("Trending")
                variant: "outline"
                selected: root.section === "trends"
                onClicked: root.section = "trends"
            }

            ThemedChip {
                visible: !root.panelDriven
                text: qsTr("Basic")
                variant: "outline"
                selected: root.section === "builtin"
                onClicked: root.section = "builtin"
            }

            Repeater {
                model: root.panelDriven ? [] : root.addonCategories
                delegate: ThemedChip {
                    required property var modelData
                    text: modelData.label
                    variant: "outline"
                    selected: root.section === modelData.id
                    onClicked: root.section = modelData.id
                }
            }

            Repeater {
                model: root.panelDriven ? [] : (root.stockChips.extra || [])
                delegate: ThemedChip {
                    required property var modelData
                    text: modelData.label
                    variant: "outline"
                    selected: root.section === modelData.id
                    onClicked: root.section = modelData.id
                }
            }

            ThemedChip {
                visible: !root.panelDriven
                text: root.userPresets.length > 0 ? qsTr("My styles · %1").arg(root.userPresets.length)
                                                  : qsTr("My styles")
                variant: "outline"
                selected: root.section === "mine"
                onClicked: root.section = "mine"
            }

            ThemedChip {
                text: root.addonCategories.length > 0 ? qsTr("More…") : qsTr("Get more templates")
                variant: "outline"
                onClicked: root.Window.window.openAddonManager("text-styles")
            }
        }

        IconButton {
            anchors.right: parent.right
            anchors.rightMargin: Theme.pagePadding
            y: Theme.pagePadding
            buttonSize: Theme.controlHeight
            glyph: Theme.icons.folderInput
            variant: "ghost"
            tooltip: qsTr("Import a text style…")
            onClicked: root.importStyle()
        }

        // AI text: write the words and the idea; the closest style is chosen on this computer.
        Rectangle {
            id: aiText
            property bool open: false
            x: Theme.pagePadding
            y: (chips.visible ? chips.y + chips.height : titleSearch.y + titleSearch.height) + Theme.spacingMd
            width: parent.width - Theme.pagePadding * 2
            height: aiColumn.implicitHeight + Theme.spacingMd * 2
            radius: Theme.radiusSm
            color: Theme.panelSecondaryBg
            border.width: Theme.borderWidth
            border.color: Theme.panelSecondaryBorder

            Column {
                id: aiColumn
                x: Theme.spacingLg
                y: Theme.spacingMd
                width: parent.width - Theme.spacingLg * 2
                spacing: Theme.spacingMd

                Item {
                    width: parent.width
                    height: 22
                    Row {
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
                            text: qsTr("AI text")
                            color: Theme.foreground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeSm
                            font.weight: Font.Medium
                        }
                        AiBadge {
                            anchors.verticalCenter: parent.verticalCenter
                            info: qsTr("Describe the style in your own words (horror title, neon sale, wedding…) and the AI picks the closest of your text styles.")
                        }
                    }
                    IconGlyph {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: aiText.open ? Theme.icons.chevronUp : Theme.icons.chevronDown
                        iconSize: 14
                        iconColor: Theme.mutedForeground
                    }
                    TapHandler { onTapped: aiText.open = !aiText.open }
                    HoverHandler { cursorShape: Qt.PointingHandCursor }
                }

                ThemedTextField {
                    id: aiWords
                    visible: aiText.open
                    width: parent.width
                    placeholderText: qsTr("Your text (optional)")
                }
                ThemedTextField {
                    id: aiIdea
                    visible: aiText.open
                    width: parent.width
                    placeholderText: qsTr("The style, in your words: horror title, neon sale…")
                    onAccepted: aiCreate.clicked()
                }
                ThemedButton {
                    id: aiCreate
                    visible: aiText.open
                    width: parent.width
                    variant: "primary"
                    glyph: Theme.icons.sparkles
                    text: qsTr("Create with AI")
                    enabled: aiWords.text.trim().length > 0 || aiIdea.text.trim().length > 0
                    onClicked: {
                        if (!EditorState.aiTextAvailable()) {
                            root.Window.window.openAddonManager("text-embed-model")
                            return
                        }
                        EditorState.addAiText(aiWords.text, aiIdea.text)
                        root.added()
                    }
                }
            }
        }
    }

    // Past the end of a category, the wheel goes on into the next one (CapCut): Básicos, the
    // template packs, then My styles.
    CategoryScrollOn {
        anchors.fill: packGrid
        flickable: root.section === "mine" ? userGrid : (root.section === "trends" ? trendsGrid : packGrid)
        categories: [{ "id": "trends", "label": qsTr("Trending") }, { "id": "builtin", "label": qsTr("Basic") }]
            .concat(root.addonCategories.map(c => ({ "id": c.id, "label": c.label })))
            .concat(root.stockChips.extra || [])
            .concat([{ "id": "mine", "label": qsTr("My styles") }])
        activeCategory: root.section
        // Trending loads page by page: its end is not the end until the last page is in.
        active: root.section !== "trends" || (!Market.textTrendsHasMore && !Market.textTrendsLoading)
        onCategoryActivated: (categoryId) => root.section = categoryId
    }

    // Template packs and the user's own styles are separate grids, switched from the toolbar.
    GridView {
        id: packGrid
        // As many columns as fit at the nominal card size, rounded, with the cards stretched or
        // squeezed a little to fill the row — a fixed card left a column's worth of empty space.
        readonly property int columnCount: Math.max(1, Math.round(width / (Theme.assetCardWidth + Theme.assetCardGap)))
        readonly property real cardSize: Math.floor(width / columnCount) - Theme.assetCardGap
        x: Theme.pagePadding
        y: toolbar.height + Theme.spacingSm
        width: parent.width - Theme.pagePadding * 2 + Theme.assetCardGap
        height: parent.height - y
        bottomMargin: Theme.spacing3xl
        clip: true
        reuseItems: true
        boundsBehavior: Flickable.StopAtBounds
        acceptedButtons: Theme.touchUi ? Qt.LeftButton : Qt.NoButton
        ScrollBar.vertical: AppScrollBar { }
        cellWidth: Math.floor(width / columnCount)
        cellHeight: Math.round(cardSize * 0.55) + Theme.spacingSm
                    + Math.ceil(labelMetrics.height) + Theme.assetCardGap
        visible: root.searching
                 || (root.section !== "mine" && root.section !== "trends" && !root.showingStockOnly)
        model: root.gridPresets

        // The chip's Stock styles after its own (and the starred ones in Favorites).
        footer: StockPanelCards {
            width: packGrid.width - Theme.assetCardGap
            visible: root.stockFooter
            height: visible ? implicitHeight : 0
            bare: true
            layout: "square"
            flickable: packGrid
            type: "text-style"
            categories: root.stockCategoriesHere
            items: root.section === "favorites" ? root.stockFavorites : null
            glyph: Theme.icons.type
            isInstalled: function(item) { return root.stockInstalled(item) }
            apply: function(item) { root.applyStock(item) }
        }

        delegate: Column {
            id: packCard
            required property var modelData
            width: packGrid.cardSize
            spacing: Theme.spacingSm

            opacity: packDrag.active ? 0.85 : 1
            scale: packDrag.active ? 1.04 : packDrag.pressed ? 0.97 : (packDrag.hovered ? 1.02 : 1.0)
            Behavior on scale {
                NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
            }

            TextStylePackThumb {
                width: parent.width
                height: Math.round(width * 0.55)
                presetId: packCard.modelData.id
                hovered: packDrag.hovered

                AssetDragSource {
                    id: packDrag
                    hasContextMenu: true
                    onContextMenuRequested: cardMenu.popup()
                    anchors.fill: parent
                    kind: "textStyle"
                    payload: packCard.modelData.id
                    label: packCard.modelData.label
                    glyph: Theme.icons.type
                    onTapped: {
                        EditorState.addTextClip("", -1, packCard.modelData.id)
                        root.added()
                    }
                }

                ThemedToolTip {
                    text: qsTr("%1 — click to add at the playhead, or drag to the timeline. Double-click it on the preview to edit.").arg(packCard.modelData.label)
                    visible: packDrag.hovered && !packDrag.active
                }

                AssetFavoriteButton {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 3
                    tabId: "textStyles"
                    itemId: packCard.modelData.id
                }

                ThemedContextMenu {
                    id: cardMenu

                    ThemedMenuItem {
                        text: qsTr("Add at playhead")
                        icon.name: Theme.icons.plus
                        onTriggered: packDrag.tapped()
                    }
                    // Its look on the text that is selected; the text keeps its words and motion.
                    ThemedMenuItem {
                        text: qsTr("Apply to the selected text")
                        icon.name: Theme.icons.type
                        enabled: root.selectedTextClip
                        onTriggered: EditorState.applyTextPreset(EditorState.selectedTrack, EditorState.selectedClip,
                                                                 packCard.modelData.id)
                    }
                }
            }

            Text {
                width: parent.width
                text: packCard.modelData.label
                elide: Text.ElideRight
                horizontalAlignment: Text.AlignHCenter
                color: packDrag.hovered ? Theme.panelForeground : Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs

                Behavior on color {
                    ColorAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                }
            }
        }
    }

    GridView {
        id: trendsGrid
        // Square cards: Stock's text style thumbnails are square.
        readonly property int columnCount: Math.max(1, Math.round(width / (Theme.assetCardWidth + Theme.assetCardGap)))
        readonly property real cardSize: Math.floor(width / columnCount) - Theme.assetCardGap
        x: Theme.pagePadding
        y: toolbar.height + Theme.spacingSm
        width: parent.width - Theme.pagePadding * 2 + Theme.assetCardGap
        height: parent.height - y
        bottomMargin: Theme.spacing3xl
        clip: true
        reuseItems: true
        boundsBehavior: Flickable.StopAtBounds
        acceptedButtons: Theme.touchUi ? Qt.LeftButton : Qt.NoButton
        ScrollBar.vertical: AppScrollBar { }
        cellWidth: Math.floor(width / columnCount)
        cellHeight: cardSize + Theme.spacingSm + Math.ceil(labelMetrics.height) + Theme.assetCardGap
        visible: root.section === "trends" && Market.authenticated && root.trendItems.length > 0 && !root.searching
        model: root.trendItems
        // The next page a little before the end, so scrolling does not stop at it.
        onContentYChanged: {
            if (Market.textTrendsHasMore && !Market.textTrendsLoading
                    && contentY + height > contentHeight - cellHeight * 3)
                Market.fetchTextTrends(true)
        }

        delegate: Column {
            id: trendCard
            required property var modelData
            readonly property string installedId: root.installedTrendId(modelData)
            width: trendsGrid.cardSize
            spacing: Theme.spacingSm

            StockThumb {
                id: trendThumb
                width: parent.width
                height: width
                item: trendCard.modelData
                showDuration: false
                // Descargado, el que responde es el AssetDragSource de encima: si responden los
                // dos, el clic agrega el texto dos veces.
                onOpenRequested: if (trendCard.installedId.length === 0) root.useTrend(trendCard.modelData)

                // CapCut's mark: not downloaded yet.
                Rectangle {
                    visible: trendCard.installedId.length === 0 && !trendThumb.busy
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

                // Downloaded: drag it to the timeline like any other style.
                AssetDragSource {
                    anchors.fill: parent
                    enabled: trendCard.installedId.length > 0
                    visible: enabled
                    kind: "textStyle"
                    payload: trendCard.installedId
                    label: trendCard.modelData.title || ""
                    glyph: Theme.icons.type
                    onTapped: root.useTrend(trendCard.modelData)
                }

                HoverHandler { id: trendHover }
                ThemedToolTip {
                    text: trendCard.installedId.length > 0
                          ? qsTr("%1 — click to add at the playhead, or drag to the timeline. Double-click it on the preview to edit.").arg(trendCard.modelData.title || "")
                          : qsTr("%1 — click to download it and add it at the playhead").arg(trendCard.modelData.title || "")
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
                font.pixelSize: Theme.fontSizeXs
            }
        }
    }

    // A chip of Stock's own: its styles only.
    Flickable {
        id: stockView
        y: toolbar.height + Theme.spacingSm
        width: parent.width
        height: parent.height - y
        visible: root.showingStockOnly && !root.searching
        clip: true
        contentHeight: stockOnlyCards.height + Theme.spacing3xl
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: AppScrollBar { }

        StockPanelCards {
            id: stockOnlyCards
            width: stockView.width
            sidePadding: Theme.pagePadding
            layout: "square"
            flickable: stockView
            type: "text-style"
            categories: root.stockCategoriesHere
            glyph: Theme.icons.type
            isInstalled: function(item) { return root.stockInstalled(item) }
            apply: function(item) { root.applyStock(item) }
        }
    }

    // Trending before there is anything to show: signed out, loading, or the request failed.
    EmptyState {
        anchors.horizontalCenter: parent.horizontalCenter
        y: toolbar.height + Math.max(0, (parent.height - toolbar.height - height) / 2)
        width: Math.min(parent.width - Theme.spacing3xl, 260)
        visible: root.section === "trends" && (!Market.authenticated || Market.textTrends.length === 0) && !root.searching
        compact: true
        glyph: Theme.icons.type
        title: !Market.authenticated ? qsTr("Sign in to see trending texts")
                                     : (Market.textTrendsLoading ? qsTr("Loading trending texts…")
                                                                 : qsTr("Couldn’t load trending texts"))
        hint: !Market.authenticated ? qsTr("Trending titles come from Stock, which needs your free account.") : ""
        actionText: !Market.authenticated ? qsTr("Sign in")
                                          : (Market.textTrendsLoading ? "" : qsTr("Retry"))
        onActionTriggered: {
            if (!Market.authenticated)
                Account.signIn()
            else
                Market.fetchTextTrends()
        }
    }

    GridView {
        id: userGrid
        // As many columns as fit at the nominal card size, rounded, with the cards stretched or
        // squeezed a little to fill the row — a fixed card left a column's worth of empty space.
        readonly property int columnCount: Math.max(1, Math.round(width / (Theme.assetCardWidth + Theme.assetCardGap)))
        readonly property real cardSize: Math.floor(width / columnCount) - Theme.assetCardGap
        x: Theme.pagePadding
        y: toolbar.height + Theme.spacingSm
        width: parent.width - Theme.pagePadding * 2 + Theme.assetCardGap
        height: parent.height - y
        bottomMargin: Theme.spacing3xl
        clip: true
        reuseItems: true
        boundsBehavior: Flickable.StopAtBounds
        acceptedButtons: Theme.touchUi ? Qt.LeftButton : Qt.NoButton
        ScrollBar.vertical: AppScrollBar { }
        cellWidth: Math.floor(width / columnCount)
        cellHeight: Math.round(cardSize * 0.55) + Theme.spacingSm
                    + Math.ceil(labelMetrics.height) + Theme.assetCardGap
        visible: root.section === "mine" && root.userPresets.length > 0 && !root.searching
        model: root.userPresets

        delegate: Column {
            id: userCard
            required property var modelData
            width: userGrid.cardSize
            spacing: Theme.spacingSm

            opacity: userDrag.active ? 0.85 : 1
            scale: userDrag.active ? 1.04 : userDrag.pressed ? 0.97 : (userDrag.hovered ? 1.02 : 1.0)
            Behavior on scale {
                NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
            }

            TextStylePackThumb {
                width: parent.width
                height: Math.round(width * 0.55)
                presetId: userCard.modelData.id
                hovered: userDrag.hovered

                AssetDragSource {
                    id: userDrag
                    anchors.fill: parent
                    kind: "textStyle"
                    payload: userCard.modelData.id
                    label: userCard.modelData.label
                    glyph: Theme.icons.type
                    hasContextMenu: true
                    onContextMenuRequested: cardMenu.popup()
                    onTapped: {
                        EditorState.addTextClip("", -1, userCard.modelData.id)
                        root.added()
                    }
                }

                ThemedToolTip {
                    text: qsTr("%1 — click to add at the playhead, or drag to the timeline. Double-click it on the preview to edit.").arg(userCard.modelData.label)
                    visible: userDrag.hovered && !userDrag.active
                }

                IconButton {
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.margins: 2
                    visible: userDrag.hovered || cardMenu.visible
                    glyph: Theme.icons.ellipsis
                    variant: "ghost"
                    buttonSize: 20
                    iconSize: 12
                    tooltip: qsTr("Style options")
                    onClicked: cardMenu.popup()
                }

                ThemedContextMenu {
                    id: cardMenu

                    ThemedMenuItem {
                        text: qsTr("Apply to the selected text")
                        icon.name: Theme.icons.type
                        enabled: root.selectedTextClip
                        onTriggered: EditorState.applyTextPreset(EditorState.selectedTrack, EditorState.selectedClip,
                                                                 userCard.modelData.id)
                    }
                    ThemedMenuItem {
                        text: qsTr("Rename…")
                        icon.name: Theme.icons.pencil
                        onTriggered: renameDialog.openFor(userCard.modelData)
                    }
                    // Refine a style in place: edit a text that uses it, then save the look over it.
                    ThemedMenuItem {
                        readonly property bool hasText: EditorState.selectedClip >= 0
                            && (EditorState.selectedClipData.kind === "text"
                                || EditorState.selectedClipData.kind === "subtitle")
                        text: qsTr("Update from the selected text")
                        icon.name: Theme.icons.refresh
                        enabled: hasText
                        onTriggered: EditorState.updateUserTextPreset(userCard.modelData.id,
                                                                      EditorState.selectedTrack,
                                                                      EditorState.selectedClip)
                    }
                    ThemedMenuItem {
                        text: qsTr("Export…")
                        icon.name: Theme.icons.folderOutput
                        onTriggered: root.exportStyle(userCard.modelData)
                    }
                    ThemedMenuSeparator { }
                    ThemedMenuItem {
                        text: qsTr("Delete")
                        icon.name: Theme.icons.trash
                        onTriggered: deleteDialog.openFor(userCard.modelData)
                    }
                }
            }

            Text {
                width: parent.width
                text: userCard.modelData.label
                elide: Text.ElideRight
                horizontalAlignment: Text.AlignHCenter
                color: userDrag.hovered ? Theme.panelForeground : Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs

                Behavior on color {
                    ColorAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                }
            }
        }
    }

    EmptyState {
        anchors.horizontalCenter: parent.horizontalCenter
        y: toolbar.height + Math.max(0, (parent.height - toolbar.height - height) / 2)
        width: Math.min(parent.width - Theme.spacing3xl, 260)
        visible: root.section === "mine" && root.userPresets.length === 0 && !root.searching
        compact: true
        glyph: Theme.icons.type
        title: qsTr("No saved styles")
        hint: qsTr("Style some text, then use “Save style…” in the properties Text tab to keep it here.")
        actionText: qsTr("Import")
        onActionTriggered: root.importStyle()
    }

    NameDialog {
        id: renameDialog

        property string presetId: ""

        function openFor(preset) {
            presetId = preset.id
            openWith(qsTr("Rename text style"), preset.label)
        }

        onSubmitted: name => EditorState.renameUserTextPreset(renameDialog.presetId, name)
    }

    ThemedDialog {
        id: deleteDialog

        property string presetId: ""
        property string presetLabel: ""

        title: qsTr("Delete text style")
        acceptText: qsTr("Delete")
        acceptVariant: "destructive"
        preferredWidth: Theme.dialogWidthSm
        acceptOnReturn: false

        function openFor(preset) {
            presetId = preset.id
            presetLabel = preset.label
            open()
        }

        onAccepted: EditorState.deleteUserTextPreset(deleteDialog.presetId)

        contentItem: Text {
            width: parent ? parent.width : 320
            wrapMode: Text.WordWrap
            text: qsTr("Remove “%1” from your saved styles? Clips already using it keep their look.")
                      .arg(deleteDialog.presetLabel)
            color: Theme.panelForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSm
        }
    }
}