import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift

// Picks a scene template for something already chosen: "Use with my photos" (the photos come
// first, the template that fits them after) or "Change template" (another template for the same
// photos and texts). The installed templates that fit best come first, then Stock's.
ThemedDialog {
    id: root

    // "photos" | "swap"
    property string mode: "photos"
    property var urls: []
    property string swapAssetId: ""
    property var suggestion: ({})
    readonly property var installed: suggestion.installed || []
    readonly property var stock: {
        const out = []
        const items = Market.templateSuggestions || []
        for (let i = 0; i < items.length; ++i) {
            const it = items[i]
            const id = Market.sceneTemplateIdForItem(it.id || "")
            if (id === "" || id === root.suggestion.currentId || Market.sceneTemplateInstalled(it.id))
                continue
            out.push(it)
        }
        return out
    }

    title: mode === "swap" ? qsTr("Change template") : qsTr("Use with my photos")
    showAccept: false
    rejectText: qsTr("Close")
    preferredWidth: Theme.dialogWidthLg

    function shapeLabel(shape) {
        if (shape === "vertical")
            return qsTr("vertical")
        if (shape === "horizontal")
            return qsTr("horizontal")
        if (shape === "square")
            return qsTr("square")
        return ""
    }

    function openForMedia(chosen) {
        mode = "photos"
        urls = chosen
        swapAssetId = ""
        suggestion = EditorState.suggestSceneTemplatesForMedia(chosen)
        Market.fetchTemplateSuggestions(suggestion.bucket || "", suggestion.nextBucket || "", suggestion.stockShape || "")
        open()
    }

    function openForSwap(assetId) {
        mode = "swap"
        urls = []
        swapAssetId = assetId
        suggestion = EditorState.suggestSceneTemplatesForSwap(assetId)
        Market.fetchTemplateSuggestions(suggestion.bucket || "", suggestion.nextBucket || "", suggestion.stockShape || "")
        open()
    }

    function pickInstalled(t) {
        close()
        if (mode === "swap")
            EditorState.swapSceneTemplate(swapAssetId, t.id)
        else
            EditorState.insertSceneTemplateWithMedia(t.id, urls)
    }

    function pickStock(item) {
        close()
        EditorState.useStockSceneTemplate(item.id, item.title || "", mode === "swap" ? [] : urls,
                                          mode === "swap" ? swapAssetId : "")
    }

    component Card: Column {
        id: card
        property string name: ""
        property string thumbnail: ""
        property int slots: 0
        property bool fits: false
        property bool cloud: false
        signal picked()
        width: 104
        spacing: 4

        Rectangle {
            width: card.width
            height: Math.round(card.width * 16 / 9)
            radius: Theme.radiusSm
            color: Theme.panelAccent
            border.width: cardHover.hovered ? 2 : 1
            border.color: cardHover.hovered ? Theme.primary : Theme.panelBorder
            clip: true

            HoverHandler { id: cardHover; cursorShape: Qt.PointingHandCursor }
            TapHandler { onTapped: card.picked() }

            Image {
                anchors.fill: parent
                anchors.margins: 1
                source: card.thumbnail
                fillMode: Image.PreserveAspectCrop
                asynchronous: true
                sourceSize: Qt.size(Math.ceil(width * Screen.devicePixelRatio), Math.ceil(height * Screen.devicePixelRatio))
            }

            Rectangle {
                anchors.left: parent.left
                anchors.bottom: parent.bottom
                anchors.margins: 5
                visible: card.slots > 0
                width: slotRow.implicitWidth + 10
                height: 20
                radius: 10
                color: card.fits ? Theme.primary : Qt.rgba(0, 0, 0, 0.72)
                Row {
                    id: slotRow
                    anchors.centerIn: parent
                    spacing: 3
                    IconGlyph {
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: Theme.icons.image
                        iconSize: 11
                        iconColor: card.fits ? Theme.primaryForeground : "white"
                    }
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: card.slots
                        color: card.fits ? Theme.primaryForeground : "white"
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                        font.weight: Font.DemiBold
                    }
                }
            }

            Rectangle {
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 5
                visible: card.cloud
                width: 24
                height: 24
                radius: 12
                color: Qt.rgba(0, 0, 0, 0.62)
                IconGlyph {
                    anchors.centerIn: parent
                    glyph: Theme.icons.download
                    iconSize: 13
                    iconColor: "white"
                }
            }

            ThemedToolTip {
                visible: cardHover.hovered
                text: card.cloud ? qsTr("%1 — from Stock: it downloads and goes in with your photos").arg(card.name)
                                 : qsTr("%1 — %n slot(s)", "", card.slots).arg(card.name)
            }
        }

        Text {
            width: parent.width
            text: card.name
            color: Theme.panelForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
            maximumLineCount: 2
            wrapMode: Text.WordWrap
        }
    }

    contentItem: Flickable {
        implicitHeight: Math.min(body.implicitHeight, root.availableContentHeight)
        contentHeight: body.implicitHeight
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: AppScrollBar { }

        Column {
            id: body
            width: parent.width
            spacing: Theme.spacingMd

            ThemedLabel {
                width: parent.width
                wrapMode: Text.WordWrap
                size: "sm"
                text: {
                    const n = root.suggestion.count || 0
                    const shape = root.shapeLabel(root.suggestion.shape || "")
                    if (root.mode === "swap")
                        return qsTr("Templates for your %n photo(s). Your photos and the texts you changed go into the one you choose, in order; one undo puts the old one back.", "", n)
                    if (shape.length > 0)
                        return qsTr("%n photo(s) or video(s), most of them %1. These templates fit them best; the highlighted count takes them all.", "", n).arg(shape)
                    return qsTr("%n photo(s) or video(s). These templates fit them best; the highlighted count takes them all.", "", n)
                }
            }

            ThemedLabel {
                text: qsTr("In Templates")
                tone: "default"
                size: "sm"
                font.weight: Font.DemiBold
            }
            ThemedLabel {
                visible: root.installed.length === 0
                width: parent.width
                wrapMode: Text.WordWrap
                size: "sm"
                text: qsTr("No installed template takes photos yet.")
            }
            Flow {
                width: parent.width
                spacing: Theme.spacingSm
                Repeater {
                    model: root.installed
                    delegate: Card {
                        required property var modelData
                        name: modelData.name || ""
                        thumbnail: modelData.thumbnail || ""
                        slots: modelData.slots || 0
                        fits: (modelData.slots || 0) >= (root.suggestion.count || 0)
                        onPicked: root.pickInstalled(modelData)
                    }
                }
            }

            ThemedLabel {
                text: qsTr("From Stock")
                tone: "default"
                size: "sm"
                font.weight: Font.DemiBold
            }
            ThemedLabel {
                width: parent.width
                wrapMode: Text.WordWrap
                size: "sm"
                visible: !Market.authenticated || Market.templateSuggestionsLoading || root.stock.length === 0
                text: !Market.authenticated
                      ? qsTr("Sign in (My account) to see the Stock templates that fit too.")
                      : (Market.templateSuggestionsLoading ? qsTr("Looking in Stock…")
                                                           : qsTr("Nothing else in Stock for this many photos."))
            }
            Flow {
                width: parent.width
                spacing: Theme.spacingSm
                Repeater {
                    model: root.stock
                    delegate: Card {
                        required property var modelData
                        name: modelData.title || ""
                        thumbnail: modelData.thumb_url || ""
                        slots: modelData.slots || 0
                        fits: (modelData.slots || 0) >= (root.suggestion.count || 0)
                        cloud: true
                        onPicked: root.pickStock(modelData)
                    }
                }
            }
        }
    }
}
