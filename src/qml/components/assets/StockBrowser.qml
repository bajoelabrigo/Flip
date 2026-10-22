import QtQuick
import QtQuick.Controls.Basic
import QtMultimedia
import Drift
import ".."

// Stock footage, photos and audio for the active Market type. The query comes from the
// Market field above; Enter there calls submitQuery(). Sources are a quiet line of names
// rather than a dropdown, led by "All" (every source with no download limit, searched
// together). Results take the shape of the medium: 16:9 tiles for video, justified rows at
// each photo's own aspect for photos, and a list with inline playback for audio.
Item {
    id: root

    property string query: ""
    property bool compact: Theme.compact
    property var filterValues: ({})
    property bool filtersExpanded: false
    property bool lastRequestWasResolve: false
    // What was actually sent, so "No results for X" only speaks for a query that ran.
    property string submittedQuery: ""
    property var detailItem: ({})
    property bool detailShown: false
    // Our own kinds as [{id, label}], in the chips' order: past the end of one, the wheel opens
    // the next (CategoryScrollOn).
    property var categories: []

    signal categoryActivated(string categoryId)

    readonly property real sidePadding: compact ? Theme.androidPagePadding : Theme.pagePadding
    readonly property int activeFilterCount: Object.keys(filterValues).length
    // What the grids show: Market.items, copied here so a next page can be appended without the
    // view jumping back to the top (a bound model is reset on every change, and loading more at
    // the bottom of the list then threw the user back to its start).
    property var shownItems: []
    function showItems() {
        const before = root.shownItems
        const next = Market.items
        const appended = before.length > 0 && next.length > before.length && next[0].id === before[0].id
        const view = !appended ? null
                   : audioList.visible ? audioList : justified.visible ? justified : grid.visible ? grid : null
        const y = view ? view.contentY : 0
        root.shownItems = next
        if (view) {
            view.forceLayout()
            view.contentY = y
        }
    }
    // Our own catalogues sort by category; it is shown as a row of chips, not only behind Filters.
    readonly property var categoryFilter: {
        const f = Market.filters.find(f => f.id === "category" && f.type === "enum")
        return f && (f.options || []).length > 1 ? f : null
    }
    // Text styles open on Trending, the titles people are using now (Jorge, 2026-10-21).
    function applyDefaultCategory() {
        if (Market.activeTypeId !== "text-style" || root.filterValues.category || !root.categoryFilter)
            return
        if (root.categoryFilter.options.some(o => o.id === "tendencias"))
            root.filterValues = Object.assign({}, root.filterValues, { category: "tendencias" })
    }
    readonly property string mediaKind: {
        const types = Market.types
        for (let i = 0; i < types.length; ++i) {
            if (types[i].id === Market.activeTypeId)
                return types[i].media_kind || types[i].id
        }
        return ""
    }
    // Stock › Templates: phone-shaped cards, and "Use" instead of a download.
    readonly property bool templates: mediaKind === "template"
    // Stock › Animaciones: our own Lottie stickers, square cards.
    readonly property bool animations: mediaKind === "animation"
    // Stock › All: every kind of our own at once. With nothing searched it shows the home
    // shelves instead of a grid.
    readonly property bool allTypes: Market.activeTypeId === "all"
    readonly property bool showHome: allTypes && query.trim().length === 0 && submittedQuery.trim().length === 0
    // The tile height over its width for one item, from its own size: 9:16 stories, 16:9
    // overlays, square stickers and sounds.
    function aspectOf(item) {
        const kind = item.media_kind || item.type || ""
        if (kind === "audio" || kind === "music" || kind === "sound")
            return 1
        const w = Number(item.width || 0), h = Number(item.height || 0)
        if (w > 0 && h > 0)
            return Math.max(0.5, Math.min(2, h / w))
        if (item.orientation === "vertical") return 16 / 9
        if (item.orientation === "horizontal") return 9 / 16
        if (item.orientation === "square") return 1
        return templates ? 16 / 9 : (animations ? 1 : 9 / 16)
    }
    // The grid's cell: the shape every result shares, or, when they differ (All, a template
    // search across formats), a box each card is fitted into at its own shape.
    readonly property real tileAspect: {
        const items = Market.items
        if (items.length === 0)
            return templates ? 16 / 9 : (animations ? 1 : 9 / 16)
        let lo = 99, hi = 0
        for (let i = 0; i < items.length; ++i) {
            const a = aspectOf(items[i])
            lo = Math.min(lo, a)
            hi = Math.max(hi, a)
        }
        return Math.abs(hi - lo) < 0.01 ? hi : Math.min(hi, 16 / 9)
    }
    function usesText(n) {
        n = Number(n || 0)
        if (n <= 0)
            return ""
        return n === 1 ? qsTr("Used once") : qsTr("Used %1 times").arg(Market.compactCount(n))
    }
    readonly property bool queryIsLink: Market.canResolve && /^(https?:\/\/|www\.)\S+$/i.test(query)
    readonly property var linkSource: {
        const q = query.toLowerCase()
        if (/youtu\.?be/.test(q)) return { label: "YouTube", glyph: Theme.icons.brandYoutube }
        if (q.indexOf("instagram.") >= 0) return { label: "Instagram", glyph: Theme.icons.brandInstagram }
        if (q.indexOf("facebook.") >= 0 || q.indexOf("fb.watch") >= 0) return { label: "Facebook", glyph: Theme.icons.brandFacebook }
        if (q.indexOf("tiktok.") >= 0) return { label: "TikTok", glyph: Theme.icons.brandTiktok }
        if (/(^|\/\/|\.)(x|twitter)\.com/.test(q)) return { label: "X", glyph: Theme.icons.brandX }
        return { label: "", glyph: Theme.icons.linkTwo }
    }

    function runSearch() {
        if (!Market.configured || !Market.activeTypeId || !Market.activeProviderId || !Market.canSearch)
            return
        // All, with nothing typed: the home shelves, not a grid of everything.
        if (allTypes && query.trim().length === 0) {
            submittedQuery = ""
            if (Market.home.length === 0 && !Market.homeLoading)
                Market.refreshHome()
            return
        }
        lastRequestWasResolve = false
        submittedQuery = query
        Market.search(query, filterValues)
    }

    function runResolve() {
        if (!query)
            return
        lastRequestWasResolve = true
        submittedQuery = query
        Market.resolveUrl(query)
    }

    function submitQuery() {
        if (queryIsLink)
            runResolve()
        else if (Market.canSearch)
            runSearch()
    }

    function setFilter(id, value, rerun) {
        const next = Object.assign({}, filterValues)
        if (value === undefined || value === null || value === "" || value === false)
            delete next[id]
        else
            next[id] = value === true ? "1" : String(value)
        filterValues = next
        if (rerun !== false)
            searchDebounce.restart()
    }

    function openDetail(item) {
        detailItem = item
        detailShown = true
    }

    function handleBack() {
        if (detailShown) {
            detailShown = false
            return true
        }
        return false
    }

    // Asks for a folder once, then keeps using it; the detail view offers "Change".
    function download(item) {
        if (!item.id || item.downloadable === false)
            return
        if (Market.sceneTemplateIdForItem(item.id) !== "") {
            Market.useSceneTemplate(item.id, item.title || "")
            return
        }
        const title = item.title || ""
        const kind = item.media_kind || item.type || ""
        // A LUT, look, text style or animation, transition or shape installs where the editor
        // keeps it: no folder to ask for.
        const delivery = Market.deliveryForItem(item)
        if (["lut", "effect-preset", "text-style", "text-animation", "transition", "shape"].indexOf(delivery) >= 0) {
            Market.download(item.id, "", "", title, kind)
            return
        }
        if (!FileDialogs.supportsDirectoryPicker()) {
            Market.download(item.id, "", "", title, kind)
            return
        }
        let dir = Market.lastDownloadDir
        if (!dir || dir.toString() === "") {
            dir = FileDialogs.openDirectory(qsTr("Save downloads to"), "")
            if (!dir || dir.toString() === "")
                return
            Market.lastDownloadDir = dir
        }
        Market.download(item.id, "", dir, title, kind)
    }

    function changeFolder() {
        const dir = FileDialogs.openDirectory(qsTr("Save downloads to"), Market.lastDownloadDir)
        if (dir && dir.toString() !== "")
            Market.lastDownloadDir = dir
    }

    onVisibleChanged: ensureResults()
    Component.onCompleted: {
        shownItems = Market.items
        ensureResults()
    }
    function ensureResults() {
        if (!visible || !Market.configured || !Market.consented)
            return
        if (Market.types.length === 0 && !Market.catalogLoading)
            Market.refreshCatalog()
        else if (Market.canSearch && Market.items.length === 0 && !Market.searching)
            searchDebounce.restart()
    }

    // Clearing the field on All goes back to the home shelves.
    onQueryChanged: {
        if (allTypes && query.trim().length === 0)
            submittedQuery = ""
    }

    StockRequestsDialog {
        id: requestsDialog
    }

    Connections {
        target: Market
        function onActiveProviderIdChanged() {
            root.filterValues = ({})
            root.applyDefaultCategory()
            root.filtersExpanded = false
            root.detailShown = false
            if (Market.canSearch && Market.items.length === 0)
                searchDebounce.restart()
        }
        function onActiveTypeIdChanged() {
            root.detailShown = false
            audioPlayer.stop()
            audioPlayer.hoverStarted = false
        }
        function onCatalogChanged() {
            if (root.visible && Market.canSearch && Market.items.length === 0 && !Market.searching)
                searchDebounce.restart()
        }
        // A link resolves to one item; open it straight away rather than showing a grid of one.
        function onItemsChanged() {
            root.showItems()
            if (root.lastRequestWasResolve && Market.items.length === 1)
                root.openDetail(Market.items[0])
        }
    }

    // Defers the one-shot search that a source switch, filter click or first showing kicks off,
    // so several landing together cost one request.
    Timer {
        id: searchDebounce
        interval: 280
        onTriggered: root.runSearch()
    }

    MediaPlayer {
        id: audioPlayer
        property string itemId: ""
        // Started by hovering a row rather than by its play button: leaving the row stops it.
        property bool hoverStarted: false
        audioOutput: AudioOutput {}
    }

    // Hovering an audio row plays its preview after a moment, like a video tile does.
    Timer {
        id: hoverPreview
        property var item: null
        interval: 350
        onTriggered: {
            if (!item || !item.preview_url || root.compact)
                return
            if (audioPlayer.itemId === item.id && audioPlayer.playbackState === MediaPlayer.PlayingState)
                return
            audioPlayer.itemId = item.id
            audioPlayer.source = item.preview_url
            audioPlayer.hoverStarted = true
            audioPlayer.play()
        }
    }

    Column {
        id: header
        width: parent.width
        spacing: Theme.spacingMd
        topPadding: Theme.spacingSm

        // Sources. "All" first when there is more than one unmetered source.
        Item {
            x: root.sidePadding
            width: parent.width - root.sidePadding * 2
            height: Math.max(sourceFlick.height, filterButton.height)

            Flickable {
                id: sourceFlick
                anchors.left: parent.left
                anchors.right: filterButton.visible ? filterButton.left : parent.right
                anchors.verticalCenter: parent.verticalCenter
                height: sourceRow.height
                contentWidth: sourceRow.width
                flickableDirection: Flickable.HorizontalFlick
                boundsBehavior: Flickable.StopAtBounds
                clip: true

                Row {
                    id: sourceRow
                    spacing: Theme.spacingXl

                    Repeater {
                        model: (Market.canSearchAll ? [{ id: "*", label: qsTr("All") }] : []).concat(Market.providers)
                        delegate: Text {
                            required property var modelData
                            readonly property bool active: Market.activeProviderId === modelData.id
                            readonly property var q: modelData.quota
                            height: Theme.touchUi ? Theme.androidMinTouchTarget : Theme.controlHeightSm
                            verticalAlignment: Text.AlignVCenter
                            text: q && q.remaining !== undefined
                                  ? qsTr("%1 (%2 left)").arg(modelData.label).arg(q.remaining)
                                  : modelData.label
                            color: active || sourceHover.hovered ? Theme.panelForeground : Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeSm
                            font.weight: active ? Font.DemiBold : Font.Normal
                            Accessible.role: Accessible.RadioButton
                            Accessible.checked: active
                            Accessible.name: text
                            HoverHandler { id: sourceHover; cursorShape: Qt.PointingHandCursor }
                            TapHandler { onTapped: Market.activeProviderId = modelData.id }
                        }
                    }
                }
            }

            IconButton {
                id: filterButton
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                visible: Market.filters.length > 0 && Market.canSearch
                glyph: Theme.icons.sliders
                active: root.filtersExpanded
                tooltip: root.activeFilterCount > 0
                         ? qsTr("Filters — %n applied", "", root.activeFilterCount)
                         : qsTr("Filters")
                onClicked: root.filtersExpanded = !root.filtersExpanded

                // The row collapses, so an applied filter needs a mark that it is narrowing results.
                Rectangle {
                    visible: root.activeFilterCount > 0
                    anchors.right: parent.right
                    anchors.top: parent.top
                    width: Theme.spacingXl
                    height: width
                    radius: width / 2
                    color: Theme.primary
                    Text {
                        anchors.centerIn: parent
                        text: String(root.activeFilterCount)
                        color: Theme.primaryForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                }
            }
        }

        // Categories of our own catalogue: "All", then each one ("Trending", "Subtitles"…).
        Flickable {
            x: root.sidePadding
            width: parent.width - root.sidePadding * 2
            height: categoryRow.height
            visible: !!root.categoryFilter && Market.canSearch && !root.allTypes
            contentWidth: categoryRow.width
            flickableDirection: Flickable.HorizontalFlick
            boundsBehavior: Flickable.StopAtBounds
            clip: true

            Row {
                id: categoryRow
                spacing: Theme.spacingSm
                Repeater {
                    model: root.categoryFilter
                           ? [{ id: "", label: qsTr("All") }].concat(root.categoryFilter.options) : []
                    delegate: ThemedChip {
                        required property var modelData
                        text: modelData.label
                        variant: "outline"
                        selected: (root.filterValues.category || "") === modelData.id
                        onClicked: root.setFilter("category", modelData.id)
                    }
                }
            }
        }

        Flow {
            x: root.sidePadding
            width: parent.width - root.sidePadding * 2
            spacing: Theme.spacingSm
            visible: Market.filters.length > 0 && Market.canSearch && root.filtersExpanded

            Repeater {
                model: Market.filters
                delegate: Item {
                    id: filterRoot
                    required property var modelData
                    width: filterLoader.width
                    height: filterLoader.height

                    Loader {
                        id: filterLoader
                        sourceComponent: filterRoot.modelData.type === "toggle" ? toggleFilter
                                         : (filterRoot.modelData.type === "text" ? textFilter : enumFilter)
                    }
                    Component {
                        id: enumFilter
                        ThemedComboBox {
                            readonly property var filter: filterRoot.modelData
                            textRole: "label"
                            valueRole: "id"
                            model: [{ id: "", label: filter.label }].concat(filter.options || [])
                            onActivated: {
                                if (currentIndex >= 0 && currentIndex < model.length)
                                    root.setFilter(filter.id, model[currentIndex].id)
                            }
                        }
                    }
                    Component {
                        id: toggleFilter
                        ThemedChip {
                            readonly property var filter: filterRoot.modelData
                            text: filter.label
                            selected: !!root.filterValues[filter.id]
                            variant: "outline"
                            onClicked: root.setFilter(filter.id, !selected)
                        }
                    }
                    Component {
                        id: textFilter
                        ThemedTextField {
                            readonly property var filter: filterRoot.modelData
                            width: 140
                            placeholderText: filter.label
                            onTextChanged: root.setFilter(filter.id, text.trim(), false)
                        }
                    }
                }
            }
        }

        // A pasted link becomes this card instead of a second button next to the field.
        Rectangle {
            x: root.sidePadding
            width: parent.width - root.sidePadding * 2
            height: Theme.touchUi ? Theme.androidMinTouchTarget + Theme.spacingLg : Theme.controlHeight * 1.6
            radius: Theme.radiusMd
            color: linkHover.hovered ? Theme.popoverHover : Theme.panelAccent
            visible: root.queryIsLink && !(root.lastRequestWasResolve && root.submittedQuery === root.query
                                           && (Market.searching || Market.items.length > 0))

            IconGlyph {
                id: linkGlyph
                anchors.left: parent.left
                anchors.leftMargin: Theme.spacingXl
                anchors.verticalCenter: parent.verticalCenter
                glyph: root.linkSource.glyph
                iconSize: Theme.iconSizeLg
                iconColor: Theme.panelForeground
            }
            Column {
                anchors.left: linkGlyph.right
                anchors.right: parent.right
                anchors.leftMargin: Theme.spacingLg
                anchors.rightMargin: Theme.spacingXl
                anchors.verticalCenter: parent.verticalCenter
                spacing: 2
                Text {
                    width: parent.width
                    text: root.linkSource.label.length > 0 ? qsTr("Get from %1").arg(root.linkSource.label)
                                                           : qsTr("Get from this link")
                    color: Theme.panelForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSm
                    font.weight: Font.Medium
                    elide: Text.ElideRight
                }
                Text {
                    width: parent.width
                    text: root.query
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                    elide: Text.ElideMiddle
                }
            }
            HoverHandler { id: linkHover; cursorShape: Qt.PointingHandCursor }
            TapHandler { onTapped: root.runResolve() }
        }

        // «Ask for a template»: on the templates tab, for what the search did not find.
        Row {
            visible: root.templates
            x: root.sidePadding
            width: parent.width - root.sidePadding * 2
            spacing: Theme.spacingMd

            Text {
                width: parent.width - askButton.width - parent.spacing
                anchors.verticalCenter: askButton.verticalCenter
                text: qsTr("Missing a template? Ask for it, or vote for other people’s ideas.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
                wrapMode: Text.WordWrap
            }
            ThemedButton {
                id: askButton
                variant: "secondary"
                glyph: Theme.icons.plus
                text: qsTr("Ask for a template")
                onClicked: requestsDialog.openFor(Market.activeTypeId)
            }
        }

        // LottieFiles has no API we may search for the user, but its free animations can be used:
        // the user downloads one there and drops the file here.
        Row {
            visible: root.animations
            x: root.sidePadding
            width: parent.width - root.sidePadding * 2
            spacing: Theme.spacingMd
            topPadding: Theme.spacingSm

            Text {
                width: parent.width - lottieButton.width - parent.spacing
                anchors.verticalCenter: lottieButton.verticalCenter
                text: qsTr("Want more? Download a free animation from LottieFiles (.json or .lottie) and drop it into Media.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
                wrapMode: Text.WordWrap
            }
            ThemedButton {
                id: lottieButton
                variant: "secondary"
                glyph: Theme.icons.search
                text: qsTr("LottieFiles")
                tooltip: qsTr("Opens lottiefiles.com in your browser")
                onClicked: Qt.openUrlExternally("https://lottiefiles.com/free-animations")
            }
        }

        // Templates the other way round: the photos first, then the templates that fit them.
        Row {
            visible: root.templates
            x: root.sidePadding
            width: parent.width - root.sidePadding * 2
            spacing: Theme.spacingMd
            topPadding: Theme.spacingSm

            Text {
                width: parent.width - withPhotosButton.width - parent.spacing
                anchors.verticalCenter: withPhotosButton.verticalCenter
                text: qsTr("Have your photos already? Choose them and Flip suggests the templates that fit.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
                wrapMode: Text.WordWrap
            }
            ThemedButton {
                id: withPhotosButton
                variant: "secondary"
                glyph: Theme.icons.image
                text: qsTr("Use with my photos…")
                onClicked: {
                    const urls = FileDialogs.openFiles(qsTr("Choose photos and videos"), [AssetLibrary.mediaNameFilter()])
                    const chosen = urls.filter(u => u.toString().length > 0)
                    if (chosen.length > 0)
                        EditorState.requestTemplatePicker("photos", "", chosen)
                }
            }
        }
    }

    Item {
        id: results
        anchors.top: header.bottom
        anchors.topMargin: Theme.spacingMd
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        // Only once a kind has no more pages to load, and not over search results.
        CategoryScrollOn {
            anchors.fill: parent
            flickable: root.showHome ? home.flickable
                       : root.mediaKind === "audio" ? audioList
                       : root.mediaKind === "image" ? justified : grid
            categories: root.categories
            activeCategory: Market.activeTypeId
            active: root.categories.length > 0 && !root.detailShown
                    && root.query.trim().length === 0 && root.submittedQuery.trim().length === 0
                    && (root.showHome || (!Market.hasMore && !Market.searching))
            onCategoryActivated: (categoryId) => root.categoryActivated(categoryId)
        }

        StockHome {
            id: home
            anchors.fill: parent
            visible: root.showHome
            compact: root.compact
            onOpenRequested: (item) => root.openDetail(item)
            onAskRequested: requestsDialog.openFor("template")
        }

        EmptyState {
            anchors.centerIn: parent
            width: parent.width
            visible: Market.searching && Market.items.length === 0 && root.lastRequestWasResolve
            glyph: Theme.icons.spinner
            glyphSpinning: true
            compact: true
            title: qsTr("Looking up that link…")
        }

        Grid {
            anchors.fill: parent
            anchors.leftMargin: root.sidePadding
            visible: Market.searching && Market.items.length === 0 && !root.lastRequestWasResolve && !root.showHome
            columns: Math.max(1, Math.floor((width + Theme.assetCardGap) / (Theme.assetCardWidth + Theme.assetCardGap)))
            spacing: Theme.assetCardGap
            Repeater {
                model: 9
                delegate: SkeletonBox {
                    width: Theme.assetCardWidth
                    height: root.mediaKind === "audio" ? Theme.controlHeight : Theme.assetCardWidth * 9 / 16
                    animated: parent.visible
                }
            }
        }

        EmptyState {
            anchors.centerIn: parent
            width: parent.width
            visible: !Market.searching && Market.searchError.length > 0 && Market.items.length === 0 && !root.showHome
            glyph: Theme.icons.error
            compact: true
            title: root.lastRequestWasResolve ? qsTr("Couldn’t open that link") : qsTr("Search failed")
            hint: Market.searchError
            actionText: Market.searchErrorRetryable ? qsTr("Try again") : ""
            onActionTriggered: root.lastRequestWasResolve ? root.runResolve() : root.runSearch()
        }

        EmptyState {
            anchors.centerIn: parent
            width: parent.width
            visible: !Market.searching && Market.searchError.length === 0 && Market.items.length === 0
                     && !root.queryIsLink && !root.showHome
            glyph: Market.canSearch ? Theme.icons.search : Theme.icons.linkTwo
            compact: true
            title: root.submittedQuery.length > 0
                   ? qsTr("No results for “%1”").arg(root.submittedQuery)
                   : (Market.canSearch ? qsTr("Search this source") : qsTr("Paste a link"))
            hint: root.submittedQuery.length > 0
                  ? qsTr("Try different words, another source, or clear a filter.")
                  : (Market.canSearch ? qsTr("Type above and press Enter.") : qsTr("Paste a page link above and press Enter."))
        }

        // Video and green screen: 16:9 tiles.
        GridView {
            id: grid
            readonly property int columnCount: Math.max(1, Math.round(width / (Theme.assetCardWidth * 1.3 + Theme.assetCardGap)))
            readonly property real tileWidth: Math.floor(width / columnCount) - Theme.assetCardGap
            anchors.fill: parent
            anchors.leftMargin: root.sidePadding
            anchors.rightMargin: root.sidePadding - Theme.assetCardGap
            visible: Market.items.length > 0 && root.mediaKind !== "audio" && root.mediaKind !== "image" && !root.showHome
            cellWidth: Math.floor(width / columnCount)
            cellHeight: tileWidth * root.tileAspect + Theme.fontSizeXs * 4 + Theme.assetCardGap
            cacheBuffer: Math.max(0, Math.round(height))
            clip: true
            model: visible ? root.shownItems : []
            ScrollBar.vertical: AppScrollBar { }
            activeFocusOnTab: true
            keyNavigationEnabled: true
            Keys.onReturnPressed: if (currentIndex >= 0) root.openDetail(Market.items[currentIndex])
            onAtYEndChanged: if (atYEnd && Market.hasMore && !Market.searching) Market.loadMore()

            delegate: Column {
                required property var modelData
                required property int index
                width: grid.tileWidth
                spacing: Theme.spacingXs

                // The cell's box, with the card at the item's own shape, bottom-aligned so the
                // titles of a row line up.
                Item {
                    width: parent.width
                    height: width * root.tileAspect

                    StockThumb {
                        readonly property real own: root.aspectOf(modelData)
                        readonly property real fit: Math.min(1, root.tileAspect / own)
                        width: Math.round(parent.width * fit)
                        height: Math.round(width * own)
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottom: parent.bottom
                        item: modelData
                        compact: root.compact
                        current: grid.activeFocus && index === grid.currentIndex
                        onOpenRequested: {
                            grid.currentIndex = index
                            root.openDetail(modelData)
                        }
                    }
                }
                Text {
                    width: parent.width
                    text: modelData.title || ""
                    color: Theme.panelForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                    elide: Text.ElideRight
                    maximumLineCount: 1
                }
                Text {
                    width: parent.width
                    visible: text.length > 0
                    text: root.usesText(modelData.uses)
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                    elide: Text.ElideRight
                }
            }
        }

        // Photos: justified rows at each photo's own aspect, so a portrait shot is not cropped
        // to a landscape tile.
        ListView {
            id: justified
            readonly property real targetHeight: root.compact ? 120 : 96
            readonly property real gap: Theme.spacingSm
            readonly property var rows: {
                const items = root.shownItems
                const width = justified.width
                if (!visible || width <= 0)
                    return []
                const out = []
                let row = []
                let sum = 0
                for (let i = 0; i < items.length; ++i) {
                    const w = Number(items[i].width || 0), h = Number(items[i].height || 0)
                    const ar = w > 0 && h > 0 ? Math.min(3, Math.max(0.5, w / h)) : 1.5
                    row.push({ index: i, ar: ar })
                    sum += ar
                    if (sum * targetHeight + gap * (row.length - 1) >= width) {
                        const hh = (width - gap * (row.length - 1)) / sum
                        out.push({ h: hh, cells: row.map(c => ({ index: c.index, w: c.ar * hh })) })
                        row = []
                        sum = 0
                    }
                }
                // The last row keeps its natural size rather than being stretched to fill.
                if (row.length > 0)
                    out.push({ h: targetHeight, cells: row.map(c => ({ index: c.index, w: c.ar * targetHeight })) })
                return out
            }
            anchors.fill: parent
            anchors.leftMargin: root.sidePadding
            anchors.rightMargin: root.sidePadding
            visible: Market.items.length > 0 && root.mediaKind === "image" && !root.showHome
            model: rows
            spacing: gap
            clip: true
            cacheBuffer: Math.max(0, Math.round(height))
            ScrollBar.vertical: AppScrollBar { }
            onAtYEndChanged: if (atYEnd && Market.hasMore && !Market.searching) Market.loadMore()

            delegate: Row {
                required property var modelData
                spacing: justified.gap
                height: modelData.h

                Repeater {
                    model: modelData.cells
                    delegate: StockThumb {
                        required property var modelData
                        width: Math.floor(modelData.w)
                        height: parent.height
                        item: root.shownItems[modelData.index] || ({})
                        compact: root.compact
                        onOpenRequested: root.openDetail(item)
                    }
                }
            }
        }

        // Audio: rows with inline playback. A tile of a waveform-less thumbnail says nothing
        // about a sound.
        ListView {
            id: audioList
            anchors.fill: parent
            anchors.leftMargin: root.sidePadding
            anchors.rightMargin: root.sidePadding
            visible: Market.items.length > 0 && root.mediaKind === "audio" && !root.showHome
            model: visible ? root.shownItems : []
            clip: true
            ScrollBar.vertical: AppScrollBar { }
            onAtYEndChanged: if (atYEnd && Market.hasMore && !Market.searching) Market.loadMore()

            delegate: Rectangle {
                id: audioRow
                required property var modelData
                readonly property bool isPlaying: audioPlayer.itemId === modelData.id
                                                  && audioPlayer.playbackState === MediaPlayer.PlayingState
                readonly property var job: {
                    void Market.downloadsRevision
                    return Market.downloadInfo(modelData.id)
                }
                width: audioList.width
                height: Theme.touchUi ? Theme.androidMinTouchTarget + Theme.spacingLg : Theme.controlHeight + Theme.spacingLg
                radius: Theme.radiusSm
                color: rowHover.hovered ? Theme.popoverHover : "transparent"

                HoverHandler {
                    id: rowHover
                    cursorShape: Qt.PointingHandCursor
                    onHoveredChanged: {
                        if (hovered) {
                            hoverPreview.item = audioRow.modelData
                            hoverPreview.restart()
                            return
                        }
                        if (hoverPreview.item && hoverPreview.item.id === audioRow.modelData.id)
                            hoverPreview.stop()
                        if (audioPlayer.hoverStarted && audioPlayer.itemId === audioRow.modelData.id) {
                            audioPlayer.stop()
                            audioPlayer.hoverStarted = false
                        }
                    }
                }
                TapHandler { onTapped: root.openDetail(audioRow.modelData) }

                IconButton {
                    id: playButton
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    glyph: audioRow.isPlaying ? Theme.icons.pause : Theme.icons.play
                    enabled: !!audioRow.modelData.preview_url
                    tooltip: audioRow.isPlaying ? qsTr("Pause") : qsTr("Play preview")
                    onClicked: {
                        if (audioRow.isPlaying && !audioPlayer.hoverStarted) {
                            audioPlayer.pause()
                            return
                        }
                        // A click keeps playing what hovering started.
                        audioPlayer.hoverStarted = false
                        if (audioRow.isPlaying)
                            return
                        if (audioPlayer.itemId !== audioRow.modelData.id) {
                            audioPlayer.itemId = audioRow.modelData.id
                            audioPlayer.source = audioRow.modelData.preview_url
                        }
                        audioPlayer.play()
                    }
                }

                Column {
                    anchors.left: playButton.right
                    anchors.right: trailing.left
                    anchors.leftMargin: Theme.spacingMd
                    anchors.rightMargin: Theme.spacingMd
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 2
                    Text {
                        width: parent.width
                        text: audioRow.modelData.title || ""
                        color: Theme.panelForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSm
                        elide: Text.ElideRight
                    }
                    Text {
                        width: parent.width
                        visible: text.length > 0
                        text: {
                            const parts = []
                            const by = audioRow.modelData.creator ? (audioRow.modelData.creator.name || "") : ""
                            if (by.length > 0)
                                parts.push(by)
                            const uses = root.usesText(audioRow.modelData.uses)
                            if (uses.length > 0)
                                parts.push(uses)
                            return parts.join(" · ")
                        }
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                        elide: Text.ElideRight
                    }
                    // Playback position of the row that is playing.
                    Rectangle {
                        width: parent.width
                        height: 2
                        radius: 1
                        color: Theme.panelMuted
                        visible: audioPlayer.itemId === audioRow.modelData.id && audioPlayer.duration > 0
                        Rectangle {
                            width: parent.width * Math.min(1, audioPlayer.position / Math.max(1, audioPlayer.duration))
                            height: parent.height
                            radius: 1
                            color: Theme.primary
                        }
                    }
                }

                Item {
                    id: trailing
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    width: Math.max(durationText.implicitWidth, ring.width)
                    height: parent.height

                    Text {
                        id: durationText
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        visible: !ring.visible
                        text: {
                            const n = Math.round(Number(audioRow.modelData.duration_ms || 0) / 1000)
                            return n > 0 ? Math.floor(n / 60) + ":" + (n % 60 < 10 ? "0" : "") + (n % 60) : ""
                        }
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                    CircularProgress {
                        id: ring
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        visible: ["waiting", "queued", "processing", "downloading", "importing"].indexOf(audioRow.job.status) >= 0
                        value: Number(audioRow.job.progress || 0)
                        indeterminate: Number(audioRow.job.progress || 0) <= 0
                        size: Theme.spacing2xl + Theme.spacingSm
                    }
                }
            }
        }
    }

    // --- Detail -------------------------------------------------------------------------------

    Rectangle {
        anchors.fill: parent
        color: Theme.scrimColor
        visible: root.compact && opacity > 0
        opacity: root.detailShown ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: Theme.durationSlow; easing.type: Theme.easing } }
        // A MouseArea rather than a TapHandler, so the tap stops here instead of also landing
        // on the card behind the scrim.
        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            onClicked: root.detailShown = false
        }
    }

    StockItemDetail {
        width: parent.width
        height: root.compact ? parent.height * 0.85 : parent.height
        x: root.compact ? 0 : (root.detailShown ? 0 : parent.width)
        y: root.compact ? (root.detailShown ? parent.height - height : parent.height) : 0
        visible: root.compact ? y < parent.height : x < parent.width
        radius: root.compact ? Theme.radiusLg : 0
        compact: root.compact
        shown: root.detailShown
        item: root.detailItem

        Behavior on x { NumberAnimation { duration: Theme.durationSlow; easing.type: Theme.easing } }
        Behavior on y { NumberAnimation { duration: Theme.durationSlow; easing.type: Theme.easing } }

        onBackRequested: root.detailShown = false
        onDownloadRequested: root.download(root.detailItem)
        onChangeFolderRequested: root.changeFolder()
    }
}
