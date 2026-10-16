import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// Stock's home, shown by the "All" type while nothing is searched: shelves the service picks
// (for this date, trending this week, new, collections, most used), each a row of cards in the
// shape of what they hold — tall for a story template, wide for a 16:9 overlay, square for a
// sticker or a sound. Tapping a card opens its detail like a search result.
Item {
    id: root

    property bool compact: Theme.compact
    readonly property real sidePadding: compact ? Theme.androidPagePadding : Theme.pagePadding
    // Every card on a shelf is this tall; the width follows the item's own shape.
    readonly property real cardHeight: compact ? 150 : 132

    signal openRequested(var item)
    signal askRequested()

    function aspectOf(item) {
        const kind = item.media_kind || item.type || ""
        if (kind === "audio")
            return 1
        const w = Number(item.width || 0), h = Number(item.height || 0)
        if (w > 0 && h > 0)
            return Math.max(0.5, Math.min(2, w / h))
        if (item.orientation === "vertical") return 9 / 16
        if (item.orientation === "horizontal") return 16 / 9
        return 1
    }

    onVisibleChanged: if (visible && Market.home.length === 0 && !Market.homeLoading) Market.refreshHome()
    Component.onCompleted: if (visible && Market.home.length === 0 && !Market.homeLoading) Market.refreshHome()

    Column {
        anchors.fill: parent
        anchors.topMargin: Theme.spacingXl
        visible: Market.homeLoading && Market.home.length === 0
        spacing: Theme.spacing3xl
        Repeater {
            model: 3
            delegate: Column {
                x: root.sidePadding
                spacing: Theme.spacingLg
                SkeletonBox { width: 120; height: Theme.fontSizeBase }
                Row {
                    spacing: Theme.spacingLg
                    Repeater {
                        model: 4
                        delegate: SkeletonBox { width: root.cardHeight * 0.75; height: root.cardHeight; radius: Theme.radiusMd }
                    }
                }
            }
        }
    }

    EmptyState {
        anchors.centerIn: parent
        width: parent.width
        visible: !Market.homeLoading && Market.home.length === 0
        glyph: Theme.icons.sparkles
        compact: true
        title: qsTr("Search all of Stock")
        hint: qsTr("Templates, music, sounds, stickers, LUTs, text styles, shapes and more. Type above and press Enter.")
        actionText: qsTr("Refresh")
        onActionTriggered: Market.refreshHome()
    }

    ListView {
        id: shelves
        anchors.fill: parent
        visible: Market.home.length > 0
        model: Market.home
        spacing: Theme.spacing2xl
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        cacheBuffer: Math.max(0, Math.round(height))
        ScrollBar.vertical: AppScrollBar { }
        header: Item {
            width: shelves.width
            height: askRow.height + Theme.spacingXl

            // «Ask for a template»: what people miss in Stock, voted by everyone.
            Row {
                id: askRow
                x: root.sidePadding
                y: Theme.spacingLg
                width: parent.width - root.sidePadding * 2
                spacing: Theme.spacingMd
                Text {
                    width: parent.width - askButton.width - parent.spacing
                    anchors.verticalCenter: askButton.verticalCenter
                    text: qsTr("Can’t find it? Ask for it and vote for other people’s ideas.")
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
                    onClicked: root.askRequested()
                }
            }
        }
        footer: Item { width: 1; height: Theme.spacing3xl }

        delegate: Column {
            id: shelf
            required property var modelData
            width: shelves.width
            spacing: Theme.spacingMd

            Text {
                x: root.sidePadding
                width: parent.width - root.sidePadding * 2
                text: shelf.modelData.title || ""
                color: Theme.panelForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeBase
                font.weight: Font.DemiBold
                elide: Text.ElideRight
            }

            ListView {
                id: shelfRow
                width: parent.width
                height: root.cardHeight + Theme.fontSizeXs * 3.2 + Theme.spacingSm
                orientation: ListView.Horizontal
                spacing: Theme.spacingLg
                leftMargin: root.sidePadding
                rightMargin: root.sidePadding
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                model: shelf.modelData.items || []
                ScrollBar.horizontal: AppScrollBar { }

                delegate: Column {
                    id: card
                    required property var modelData
                    readonly property int uses: Number(modelData.uses || 0)
                    width: Math.round(root.cardHeight * root.aspectOf(modelData))
                    spacing: 2

                    StockThumb {
                        width: parent.width
                        height: root.cardHeight
                        item: card.modelData
                        compact: root.compact
                        onOpenRequested: root.openRequested(card.modelData)
                    }
                    Text {
                        width: parent.width
                        text: card.modelData.title || ""
                        color: Theme.panelForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                        elide: Text.ElideRight
                    }
                    Text {
                        width: parent.width
                        visible: card.uses > 0
                        text: card.uses === 1 ? qsTr("Used once")
                                              : qsTr("Used %1 times").arg(Market.compactCount(card.uses))
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                        elide: Text.ElideRight
                    }
                }
            }
        }
    }
}
