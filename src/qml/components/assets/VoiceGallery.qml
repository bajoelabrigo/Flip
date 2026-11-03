import QtQuick
import QtQuick.Controls.Basic
import Drift

// The voices to choose from, as CapCut's text to speech shows them (0.30, Jorge): a face for each
// ready voice (a made-up person), its name and kind, ▷ to hear it and the star; chips to narrow
// them down. Folded, it shows the chosen one and a row or two; «See all» opens the rest.
Column {
    id: root

    // The voice in use (VoiceLibrary id); the gallery only asks for a new one.
    property string currentId: ""
    property string playingId: ""
    signal picked(string id)
    signal playRequested(string id)

    property string filter: "all"
    property bool open: false
    property int revision: 0
    readonly property int columns: 3
    readonly property int foldedCount: 6

    spacing: Theme.spacingSm

    Connections {
        target: EditorState.voices
        function onModelReset() { root.revision++ }
        function onRowsInserted() { root.revision++ }
        function onRowsRemoved() { root.revision++ }
        function onDataChanged() { root.revision++ }
    }

    function styleLabel(style) {
        switch (style) {
        case "narration": return qsTr("Narration")
        case "young": return qsTr("Young")
        case "deep": return qsTr("Deep")
        case "lively": return qsTr("Lively")
        case "soft": return qsTr("Soft")
        case "mature": return qsTr("Mature")
        }
        return ""
    }

    readonly property var filters: [
        { "id": "all", "label": qsTr("All") },
        { "id": "favorites", "label": qsTr("Favorites") },
        { "id": "mine", "label": qsTr("Mine") },
        { "id": "f", "label": qsTr("Women") },
        { "id": "m", "label": qsTr("Men") },
        { "id": "narration", "label": qsTr("Narration") },
        { "id": "young", "label": qsTr("Young") },
        { "id": "deep", "label": qsTr("Deep") },
        { "id": "lively", "label": qsTr("Lively") },
        { "id": "soft", "label": qsTr("Soft") },
        { "id": "mature", "label": qsTr("Mature") }
    ]

    // Every voice the chip lets through; folded, the gallery shows a few of them.
    readonly property var matching: {
        void root.revision
        void favoritesWatch.tick
        const all = EditorState.voices.allVoices()
        const f = root.filter
        return all.filter(v => {
            if (f === "all")
                return true
            if (f === "favorites")
                return EditorState.isAssetFavorite("ttsVoices", v.id)
            if (f === "mine")
                return !v.builtIn
            if (f === "f" || f === "m")
                return v.gender === f
            return v.style === f
        })
    }
    // Folded, the chosen one first, so it is always in sight; the panel's Generate stays near.
    readonly property var shown: {
        if (root.open)
            return root.matching
        const current = root.matching.filter(v => v.id === root.currentId)
        const rest = root.matching.filter(v => v.id !== root.currentId)
        return current.concat(rest).slice(0, root.foldedCount)
    }

    QtObject {
        id: favoritesWatch
        property int tick: 0
    }
    Connections {
        target: EditorState
        ignoreUnknownSignals: true
        function onAssetFavoritesChanged() { favoritesWatch.tick++ }
    }

    ChipScroller {
        width: parent.width
        Repeater {
            model: root.filters
            delegate: ThemedChip {
                required property var modelData
                text: modelData.label
                selected: root.filter === modelData.id
                variant: "outline"
                onClicked: {
                    root.filter = modelData.id
                    root.open = false
                }
            }
        }
    }

    Grid {
        id: grid
        width: parent.width
        columns: root.columns
        columnSpacing: Theme.spacingSm
        rowSpacing: Theme.spacingSm
        readonly property real cardWidth: (width - columnSpacing * (columns - 1)) / columns

        Repeater {
            model: root.shown
            delegate: Item {
                id: card
                required property var modelData
                readonly property bool chosen: modelData.id === root.currentId
                width: grid.cardWidth
                height: face.height + nameText.height + kindText.height + 6

                Rectangle {
                    id: face
                    width: parent.width
                    height: width
                    radius: Theme.radiusMd
                    color: card.modelData.gender === "f" ? Qt.rgba(0.85, 0.45, 0.6, 0.35)
                          : card.modelData.gender === "m" ? Qt.rgba(0.35, 0.55, 0.9, 0.35)
                          : Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.3)
                    border.width: card.chosen ? 2 : (cardMouse.containsMouse ? 1 : 0)
                    border.color: card.chosen ? Theme.primary : Theme.border
                    clip: true

                    Image {
                        anchors.fill: parent
                        anchors.margins: card.chosen ? 2 : 0
                        source: card.modelData.photo || ""
                        visible: status === Image.Ready
                        fillMode: Image.PreserveAspectCrop
                        asynchronous: true
                        sourceSize.width: 192
                        sourceSize.height: 192
                    }
                    Text {
                        anchors.centerIn: parent
                        visible: !card.modelData.photo
                        text: (card.modelData.name || "?").charAt(0).toUpperCase()
                        color: Theme.foreground
                        font.family: Theme.fontFamily
                        font.pixelSize: Math.round(parent.height * 0.4)
                        font.weight: Font.DemiBold
                    }

                    MouseArea {
                        id: cardMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.picked(card.modelData.id)
                    }

                    // ▷ to hear it, bottom left, on hover (and while it plays).
                    IconButton {
                        anchors.left: parent.left
                        anchors.bottom: parent.bottom
                        anchors.margins: 3
                        visible: cardMouse.containsMouse || hovered || root.playingId === card.modelData.id
                        glyph: root.playingId === card.modelData.id ? Theme.icons.pause : Theme.icons.play
                        variant: "ghost"
                        buttonSize: 22
                        iconSize: 12
                        tooltip: qsTr("Hear this voice")
                        onClicked: root.playRequested(card.modelData.id)
                    }

                    AssetFavoriteButton {
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.margins: 3
                        tabId: "ttsVoices"
                        itemId: card.modelData.id
                    }
                }

                Text {
                    id: nameText
                    anchors.top: face.bottom
                    anchors.topMargin: 3
                    width: parent.width
                    horizontalAlignment: Text.AlignHCenter
                    elide: Text.ElideRight
                    text: card.modelData.name
                    color: card.chosen ? Theme.primary : Theme.foreground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                    font.weight: card.chosen ? Font.DemiBold : Font.Normal
                }
                Text {
                    id: kindText
                    anchors.top: nameText.bottom
                    width: parent.width
                    horizontalAlignment: Text.AlignHCenter
                    elide: Text.ElideRight
                    text: card.modelData.builtIn ? root.styleLabel(card.modelData.style) : qsTr("My voice")
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeTiny
                }
            }
        }
    }

    Text {
        visible: root.shown.length === 0
        width: parent.width
        wrapMode: Text.WordWrap
        horizontalAlignment: Text.AlignHCenter
        text: root.filter === "favorites" ? qsTr("Mark voices with the star to find them here")
              : root.filter === "mine" ? qsTr("Your own voices appear here: «New voice» in Options")
              : qsTr("No voices of this kind")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }

    ThemedButton {
        visible: root.matching.length > root.foldedCount
        width: parent.width
        variant: "ghost"
        text: root.open ? qsTr("Show fewer") : qsTr("See all voices (%1)").arg(root.matching.length)
        onClicked: root.open = !root.open
    }
}
