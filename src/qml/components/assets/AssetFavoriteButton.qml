import QtQuick
import Drift
import ".."

// Star toggle for marking an asset-browser item as a favorite.
IconButton {
    id: root

    property string tabId: ""
    property string itemId: ""
    // A Stock card: what it looks like is kept with the star, so the panel's Favoritos shows it
    // before it is downloaded (MarketClient::keepFavoriteItem).
    property var stockItem: null

    // A binding rather than a one-shot read so a card recycled onto another item re-reads it.
    property int _favoritesTick: 0
    readonly property bool favorited: {
        void _favoritesTick
        return EditorState.isAssetFavorite(tabId, itemId)
    }

    glyph: Theme.icons.star
    variant: "ghost"
    buttonSize: 18
    iconSize: 12
    active: favorited
    tooltip: favorited ? qsTr("Remove from favorites") : qsTr("Add to favorites")

    Connections {
        target: EditorState
        function onAssetFavoritesChanged() {
            root._favoritesTick++
        }
    }

    onClicked: {
        if (stockItem && !favorited)
            Market.keepFavoriteItem(stockItem)
        EditorState.toggleAssetFavorite(tabId, itemId)
    }
}
