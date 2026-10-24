import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import QtMultimedia
import Drift
import ".."
import "."

// Sound effects tab: the "sound-effects" extras by category. Play a sound to hear it; add puts it
// on an audio track at the playhead. With `music` it is the Music tab instead: the free music
// pack ships in the same format (pack id "musica"), and each tab shows only its own sounds and
// the categories that have any.
Item {
    id: root

    signal added()

    property bool music: false
    readonly property string musicPrefix: "musica/"
    // Favorites are kept per tab, so a starred song never shows up among the sound effects.
    readonly property string favoritesTab: root.music ? "music" : "sounds"
    readonly property string favoritesId: "__favorites__"
    property int favoritesTick: 0
    Connections {
        target: EditorState
        function onAssetFavoritesChanged() { root.favoritesTick++ }
    }

    function ownSounds() {
        return EditorState.soundEffects().filter(s => (s.id || "").startsWith(root.musicPrefix) === root.music)
    }
    function ownCategories(sounds) {
        return EditorState.soundEffectCategories().filter(c => sounds.some(s => s.category === c.id))
    }

    property var allSounds: ownSounds()
    property var localCategories: ownCategories(allSounds)
    readonly property bool hasSounds: allSounds.length > 0
    // Stock's music or sounds here too (0.22): Trending first (the most used), the rest spread over
    // these chips by mood or kind after the local ones, or in chips of their own («stock:<category>»).
    readonly property string stockType: root.music ? "music" : "sound"
    readonly property string trendsId: "__trends__"
    property int stockTick: 0
    readonly property var stockChips: {
        void root.stockTick
        return Market.authenticated ? Market.stockChips(root.stockType, root.localCategories)
                                    : ({ extra: [], categoriesOf: {} })
    }
    readonly property var categories: Market.configured
        ? [{ "id": root.trendsId, "label": qsTr("Trending") }].concat(root.localCategories).concat(root.stockChips.extra || [])
        : root.localCategories
    readonly property var stockCategoriesHere: (root.stockChips.categoriesOf || {})[root.activeCategory] || []
    readonly property bool showingStockOnly: root.query.length === 0
                                             && (root.activeCategory === root.trendsId
                                                 || root.activeCategory.indexOf("stock:") === 0)
    readonly property var stockFavorites: {
        void root.favoritesTick
        void Market.favoriteItemsRevision
        return root.activeCategory === root.favoritesId && root.query.length === 0
               ? Market.stockFavoriteItems(EditorState.assetFavoriteIds(root.favoritesTab), [root.stockType], root.favoritesTab)
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

    // A Stock song or sound is a file in Media: put at the playhead.
    function stockInstalled(item) {
        const asset = Market.placedId(item.id)
        return asset.length > 0 && AssetLibrary.indexOfId(asset) >= 0
    }
    function applyStock(item) {
        player.stop()
        EditorState.addAssetClipWhenReady(Market.placedId(item.id))
        root.added()
    }
    readonly property string query: search.text.trim().toLowerCase()
    readonly property var currentSounds: {
        const q = root.query
        if (q.length > 0)
            return root.allSounds.filter(s => (s.label || "").toLowerCase().indexOf(q) >= 0)
        if (root.activeCategory === root.favoritesId) {
            void root.favoritesTick
            return root.allSounds.filter(s => EditorState.isAssetFavorite(root.favoritesTab, s.id))
        }
        if (root.showingStockOnly)
            return []
        return root.allSounds.filter(s => s.category === root.activeCategory)
    }

    Connections {
        target: Addons
        function onKindChanged(kind) {
            if (kind !== "sound-effects")
                return
            root.allSounds = root.ownSounds()
            root.localCategories = root.ownCategories(root.allSounds)
            root.activeCategory = root.categories.length > 0 ? root.categories[0].id : ""
        }
    }

    onVisibleChanged: {
        if (!visible)
            player.stop()
    }

    MediaPlayer {
        id: player
        property string soundId: ""
        audioOutput: AudioOutput { }
    }

    Column {
        anchors.fill: parent
        spacing: 0

        Item { width: 1; height: Theme.pagePadding }

        ThemedTextField {
            id: search
            width: parent.width - Theme.pagePadding * 2
            x: Theme.pagePadding
            visible: root.hasSounds
            height: visible ? implicitHeight : 0
            placeholderText: root.music ? qsTr("Search music") : qsTr("Search sounds")
            font.family: Theme.fontFamily
        }

        Item { width: 1; height: root.hasSounds ? Theme.spacingMd : 0 }

        AssetCategoryChips {
            id: chips
            width: parent.width
            categories: root.hasSounds || Market.configured ? root.categories : []
            activeCategory: root.activeCategory
            searching: root.query.length > 0
            onCategoryActivated: (categoryId) => root.activeCategory = categoryId
        }

        Item {
            width: parent.width
            height: Math.max(0, parent.height - Theme.pagePadding - search.height
                             - (root.hasSounds ? Theme.spacingMd : 0) - chips.height)

            EmptyState {
                visible: !root.hasSounds && !root.showingStockOnly
                x: Theme.pagePadding
                y: Theme.pagePadding
                width: parent.width - Theme.pagePadding * 2
                compact: true
                glyph: Theme.icons.music
                title: root.music ? qsTr("No music installed") : qsTr("No sound effects installed")
                hint: root.music
                      ? qsTr("Install the free music pack: 65 public-domain songs, happy, calm, epic, cinematic and more, free for your videos.")
                      : qsTr("Install the sound effects pack: whooshes, pops, bells, impacts and more.")
                actionText: qsTr("Get extras")
                actionVariant: "primary"
                onActionTriggered: root.Window.window.openAddonManager("sound-effects")
            }

            Text {
                visible: root.hasSounds && root.query.length === 0 && root.activeCategory === root.favoritesId
                         && root.currentSounds.length === 0 && root.stockFavorites.length === 0
                x: Theme.pagePadding
                y: Theme.pagePadding
                width: parent.width - Theme.pagePadding * 2
                wrapMode: Text.WordWrap
                text: qsTr("No favorites yet. Tap the star on a sound to keep it here.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            // Trending, or a chip of Stock's own: Stock's rows only.
            Flickable {
                id: stockView
                anchors.fill: parent
                visible: root.showingStockOnly
                clip: true
                contentHeight: stockOnlyRows.height + Theme.spacingXl
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: AppScrollBar { }

                StockPanelCards {
                    id: stockOnlyRows
                    y: Theme.pagePadding
                    width: stockView.width
                    sidePadding: Theme.pagePadding
                    flickable: stockView
                    type: root.stockType
                    layout: "audio"
                    categories: root.activeCategory === root.trendsId ? [] : root.stockCategoriesHere
                    glyph: Theme.icons.music
                    isInstalled: function(item) { return root.stockInstalled(item) }
                    apply: function(item) { root.applyStock(item) }
                }
            }

            // Past the end of a category, the wheel goes on into the next one (CapCut).
            CategoryScrollOn {
                anchors.fill: list
                flickable: list
                categories: root.categories
                activeCategory: root.activeCategory
                active: root.query.length === 0
                onCategoryActivated: (categoryId) => root.activeCategory = categoryId
            }

            ListView {
                id: list
                x: Theme.pagePadding
                width: parent.width - Theme.pagePadding * 2
                height: parent.height
                topMargin: Theme.pagePadding
                bottomMargin: Theme.pagePadding
                visible: root.currentSounds.length > 0 || root.stockFooter
                clip: true
                spacing: Theme.spacingSm
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: AppScrollBar { }
                model: root.currentSounds

                // The chip's Stock rows after its own (and the starred ones in Favorites).
                footer: StockPanelCards {
                    width: list.width - Theme.spacingMd
                    visible: root.stockFooter
                    height: visible ? implicitHeight + Theme.spacingSm : 0
                    topPadding: Theme.spacingSm
                    bare: true
                    layout: "audio"
                    flickable: list
                    type: root.stockType
                    categories: root.stockCategoriesHere
                    items: root.activeCategory === root.favoritesId ? root.stockFavorites : null
                    isInstalled: function(item) { return root.stockInstalled(item) }
                    apply: function(item) { root.applyStock(item) }
                }

                delegate: Rectangle {
                    id: row
                    required property var modelData
                    readonly property bool playing: player.soundId === modelData.id
                                                    && player.playbackState === MediaPlayer.PlayingState
                    width: list.width - Theme.spacingMd
                    height: 44
                    radius: Theme.radiusSm
                    color: rowHover.hovered ? Theme.popoverHover : Theme.panelAccent

                    HoverHandler { id: rowHover }

                    IconButton {
                        id: playButton
                        anchors.left: parent.left
                        anchors.leftMargin: Theme.spacingSm
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: row.playing ? Theme.icons.pause : Theme.icons.play
                        variant: "ghost"
                        tooltip: row.playing ? qsTr("Stop") : qsTr("Listen")
                        onClicked: {
                            if (row.playing) {
                                player.stop()
                                return
                            }
                            player.stop()
                            player.soundId = row.modelData.id
                            player.source = row.modelData.url
                            player.play()
                        }
                    }

                    Column {
                        anchors.left: playButton.right
                        anchors.leftMargin: Theme.spacingMd
                        anchors.right: favoriteButton.left
                        anchors.rightMargin: Theme.spacingMd
                        anchors.verticalCenter: parent.verticalCenter
                        Text {
                            width: parent.width
                            text: row.modelData.label
                            color: Theme.panelForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeSm
                            elide: Text.ElideRight
                        }
                        Text {
                            width: parent.width
                            // A song reads as 2:14; a short effect keeps its tenths.
                            text: {
                                const d = Number(row.modelData.duration || 0)
                                if (d < 60)
                                    return d.toFixed(1) + " s"
                                const s = Math.round(d)
                                return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0")
                            }
                            color: Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                    }

                    AssetFavoriteButton {
                        id: favoriteButton
                        anchors.right: addButton.left
                        anchors.rightMargin: Theme.spacingXs
                        anchors.verticalCenter: parent.verticalCenter
                        tabId: root.favoritesTab
                        itemId: row.modelData.id
                    }

                    IconButton {
                        id: addButton
                        anchors.right: parent.right
                        anchors.rightMargin: Theme.spacingSm
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: Theme.icons.plus
                        variant: "ghost"
                        tooltip: qsTr("Add at the playhead")
                        onClicked: {
                            EditorState.addSoundEffect(row.modelData.id)
                            root.added()
                        }
                    }
                }
            }
        }
    }
}
