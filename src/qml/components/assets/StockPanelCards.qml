import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// Stock's items of one type inside its own panel (0.22, the web's StockTrends.tsx): a type's
// «Trending» (all of it, page by page: MarketClient::fetchPanelList with no categories) or, after the panel's
// own cards in a chip, Stock's items of the categories that chip gathers, page by page. Each card
// is Stock's (StockThumb: the flame on what is trending, the star, the download state), with
// Filmora's mark until it is on this computer; one click downloads it and hands it to the panel's
// `apply`. Trending needs the account: signed out, a chip of its own says so instead of its cards,
// and one after the panel's own cards (`bare`) shows nothing.
//
// It sizes itself to its cards, so it goes as the footer of the panel's grid or under its list.
Column {
    id: root

    property string type: ""
    // The server categories to list; empty: the type's Trending.
    property var categories: []
    // These instead of a list from the server (a panel's Favorites): shown signed out too.
    property var items: null
    // After the panel's own cards in a chip: no sign-in card and no "nothing here".
    property bool bare: false
    // "wide" (16:9), "square", "tall" (9:16) or "audio" (rows to listen to).
    property string layout: "wide"
    // The scrolling view this sits in: the next page comes a little before its end.
    property Flickable flickable: null
    property real sidePadding: 0
    property string glyph: Theme.icons.trending
    // Whether the panel already has this item (no download needed), and what it does with it.
    property var isInstalled: function(item) { return Market.placedId(item.id).length > 0 }
    property var apply: function(item) {}

    // Bumped when something lands, so `installed` is read again.
    property int installTick: 0
    property var pending: ({})

    readonly property string listKey: Market.panelListKey(root.type, root.categories || [])
    property var list: ({})
    readonly property var shown: root.items !== null && root.items !== undefined ? root.items : (root.list.items || [])
    readonly property bool signedOut: !Market.authenticated
    readonly property bool loading: root.items === null && root.list.loading === true
    readonly property bool failed: root.items === null && !!root.list.error && root.list.error !== "auth"

    spacing: Theme.spacingSm
    width: parent ? parent.width : 0

    function refresh() {
        root.list = Market.panelList(root.listKey)
    }
    function ensure() {
        if (root.type.length === 0 || (root.items !== null && root.items !== undefined))
            return
        root.refresh()
        if (Market.authenticated)
            Market.fetchPanelList(root.type, root.categories || [], false)
    }
    onListKeyChanged: ensure()
    onItemsChanged: ensure()
    Component.onCompleted: ensure()

    function maybeMore() {
        const f = root.flickable
        if (!f || !root.list.hasMore || root.list.loading || root.items !== null)
            return
        if (f.contentY + f.height > f.contentHeight - Math.max(400, f.height))
            Market.fetchPanelList(root.type, root.categories || [], true)
    }

    Connections {
        target: root.flickable
        ignoreUnknownSignals: true
        function onContentYChanged() { root.maybeMore() }
        function onContentHeightChanged() { root.maybeMore() }
    }

    function installed(item) {
        void root.installTick
        return root.isInstalled(item)
    }

    function use(item) {
        if (!Market.authenticated) {
            signInLoader.active = true
            signInLoader.item.openFor(() => root.use(item))
            return
        }
        if (root.installed(item)) {
            root.apply(item)
            return
        }
        const job = Market.downloadInfo(item.id)
        if (["waiting", "queued", "processing", "downloading", "importing"].indexOf(job.status) >= 0)
            return
        if (Market.deliveryForItem(item) === "scene-template") {
            // Templates install and go on the timeline by themselves.
            Market.useSceneTemplate(item.id, item.title || "")
            return
        }
        const next = Object.assign({}, root.pending)
        next[item.id] = true
        root.pending = next
        Market.download(item.id, "", "", item.title || "", item.media_kind || item.type || "")
    }
    function landed(itemId) {
        if (!root.pending[itemId])
            return
        const next = Object.assign({}, root.pending)
        delete next[itemId]
        root.pending = next
        root.installTick++
        const item = Market.itemById(itemId)
        // After the panel has read its catalogue again (an installed effect, a new LUT file…).
        if (item && item.id)
            Qt.callLater(() => root.apply(item))
    }

    Connections {
        target: Market
        function onPanelListChanged(key) {
            if (key === root.listKey)
                root.refresh()
        }
        function onAuthChanged() { root.ensure() }
        function onDownloadInstalled(itemId, name, where) { root.landed(itemId) }
        function onDownloadImported(itemId, name) { root.landed(itemId) }
        function onDownloadFailed(itemId, code, message) {
            if (!root.pending[itemId])
                return
            const next = Object.assign({}, root.pending)
            delete next[itemId]
            root.pending = next
        }
    }

    Loader {
        id: signInLoader
        active: false
        sourceComponent: Component { SignInRequiredDialog { reason: "trends" } }
    }

    // Trending before there is anything to show: signed out, loading, or the request failed.
    EmptyState {
        x: root.sidePadding
        width: root.width - root.sidePadding * 2
        visible: !root.bare && (root.items === null || root.items === undefined) && root.shown.length === 0
        compact: true
        glyph: root.glyph
        title: root.signedOut ? qsTr("Sign in to see what's trending")
                              : root.failed ? qsTr("Couldn’t load what's trending")
                                            : root.loading || !root.list.loaded ? qsTr("Loading what's trending…")
                                                                                : qsTr("Nothing here yet.")
        hint: root.signedOut ? qsTr("Trending comes from Stock, which needs your free account.") : ""
        actionText: root.signedOut ? (Account.busy ? qsTr("Waiting for the browser…") : qsTr("Sign in"))
                                   : root.failed ? qsTr("Retry") : ""
        onActionTriggered: {
            if (root.signedOut)
                Account.signIn()
            else
                Market.fetchPanelList(root.type, root.categories || [], false)
        }
    }

    FontMetrics {
        id: labelMetrics
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeCard
        font.weight: Font.Medium
    }

    // Cards: as many columns as fit at the nominal size, stretched a little to fill the row.
    Flow {
        id: cards
        visible: root.layout !== "audio" && root.shown.length > 0
        x: root.sidePadding
        width: root.width - root.sidePadding * 2 + Theme.assetCardGap
        spacing: 0
        readonly property real nominal: root.layout === "wide" ? Theme.assetCardWidth * 1.35 : Theme.assetCardWidth
        readonly property int columnCount: Math.max(1, Math.round(width / (nominal + Theme.assetCardGap)))
        readonly property real cardWidth: Math.floor(width / columnCount) - Theme.assetCardGap
        readonly property real aspect: root.layout === "wide" ? 9 / 16 : root.layout === "tall" ? 16 / 9 : 1

        Repeater {
            model: cards.visible ? root.shown : []
            delegate: Item {
                id: card
                required property var modelData
                readonly property bool have: root.installed(modelData)
                width: cards.cardWidth + Theme.assetCardGap
                height: thumbBox.height + 4 + Math.ceil(labelMetrics.height) + Theme.assetCardGap

                StockThumb {
                    id: thumbBox
                    width: cards.cardWidth
                    height: Math.round(cards.cardWidth * cards.aspect)
                    item: card.modelData
                    showDuration: false
                    onOpenRequested: root.use(card.modelData)

                    // Not downloaded yet (Filmora's mark).
                    Rectangle {
                        visible: !card.have && !thumbBox.busy
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

                    HoverHandler { id: cardHover }
                    ThemedToolTip {
                        text: card.have ? qsTr("%1 — click to use it").arg(card.modelData.title || "")
                                        : qsTr("%1 — click to download it and use it").arg(card.modelData.title || "")
                        visible: cardHover.hovered && !thumbBox.busy
                    }
                }

                Text {
                    y: thumbBox.height + 4
                    width: cards.cardWidth
                    text: card.modelData.title || ""
                    elide: Text.ElideRight
                    horizontalAlignment: Text.AlignHCenter
                    color: cardHover.hovered ? Theme.panelForeground : Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeCard
                    font.weight: Font.Medium
                }
            }
        }
    }

    // Music and sounds: rows to listen to, «+» puts one at the playhead.
    Column {
        visible: root.layout === "audio" && root.shown.length > 0
        x: root.sidePadding
        width: root.width - root.sidePadding * 2
        spacing: 2

        Repeater {
            model: root.layout === "audio" ? root.shown : []
            delegate: Rectangle {
                id: row
                required property var modelData
                readonly property bool trending: {
                    void Market.weeklyTrendingIds
                    return Market.isTrendingItem(modelData)
                }
                width: parent.width
                height: Theme.controlHeight + Theme.spacingXs
                radius: Theme.radiusSm
                color: rowHover.hovered ? Theme.panelAccent : "transparent"

                HoverHandler { id: rowHover }

                StockThumb {
                    id: rowThumb
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    width: height
                    height: parent.height - 4
                    item: row.modelData
                    compact: true
                    showDuration: false
                    showTrend: false
                    showFavorite: false
                    onOpenRequested: root.use(row.modelData)
                }

                TrendBadge {
                    id: rowFlame
                    visible: row.trending
                    anchors.left: rowThumb.right
                    anchors.leftMargin: Theme.spacingSm
                    anchors.verticalCenter: parent.verticalCenter
                    implicitWidth: 16
                    implicitHeight: 16
                }

                Text {
                    anchors.left: row.trending ? rowFlame.right : rowThumb.right
                    anchors.leftMargin: Theme.spacingSm
                    anchors.right: rowDuration.left
                    anchors.rightMargin: Theme.spacingSm
                    anchors.verticalCenter: parent.verticalCenter
                    text: row.modelData.title || ""
                    elide: Text.ElideRight
                    color: Theme.panelForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSm
                }

                Text {
                    id: rowDuration
                    anchors.right: rowStar.left
                    anchors.rightMargin: Theme.spacingXs
                    anchors.verticalCenter: parent.verticalCenter
                    text: rowThumb.formatDuration(row.modelData.duration_ms)
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                }

                AssetFavoriteButton {
                    id: rowStar
                    anchors.right: rowAdd.left
                    anchors.verticalCenter: parent.verticalCenter
                    tabId: Market.stockFavoriteGroup(row.modelData)
                    itemId: Market.stockFavoriteKey(row.modelData.id || "")
                    stockItem: row.modelData
                }

                IconButton {
                    id: rowAdd
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    glyph: rowThumb.busy ? Theme.icons.download : Theme.icons.plus
                    variant: "ghost"
                    buttonSize: 22
                    iconSize: 14
                    enabled: !rowThumb.busy
                    tooltip: qsTr("Add at the playhead")
                    onClicked: root.use(row.modelData)
                }
            }
        }
    }

    // The next page on its way, or one that failed.
    Item {
        width: root.width
        height: visible ? Theme.controlHeight : 0
        visible: root.shown.length > 0 && (root.loading || root.failed)
        Text {
            anchors.centerIn: parent
            visible: root.loading
            text: qsTr("Loading…")
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }
        ThemedButton {
            anchors.centerIn: parent
            visible: root.failed && !root.loading
            text: qsTr("Retry")
            onClicked: Market.fetchPanelList(root.type, root.categories || [], true)
        }
    }
}
