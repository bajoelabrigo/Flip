import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift
import ".."

// Fill template: a scene template's photo slots and texts, as CapCut asks for them after you pick
// a template. A slot takes a file (click, or several at once), a drop from the file manager or a
// drag from Media; the picture is cut to fill the slot's box and keeps the template's motion.
Item {
    id: root

    property string assetId: ""
    property int revision: 0
    property int localRevision: 0
    readonly property var info: {
        void revision
        void localRevision
        return assetId.length > 0 ? EditorState.sceneTemplateInfo(assetId) : ({})
    }
    readonly property var slots: info.slots || []
    readonly property var texts: info.texts || []
    readonly property int filled: slots.length - (info.emptySlots || 0)

    height: contentCol.height
    implicitHeight: contentCol.height

    function refreshFields() {}

    Connections {
        target: EditorState
        function onTracksChanged() { root.localRevision++ }
        function onSelectedClipDataChanged() { root.localRevision++ }
    }

    function pickFiles(firstSlotClipId, many) {
        const filters = [AssetLibrary.mediaNameFilter()]
        const urls = many ? FileDialogs.openFiles(qsTr("Choose photos and videos"), filters)
                          : [FileDialogs.openFile(qsTr("Choose a photo or video"), filters)]
        const chosen = urls.filter(u => u.toString().length > 0)
        if (chosen.length > 0)
            EditorState.fillTemplateSlotsFromUrls(root.assetId, firstSlotClipId, chosen)
    }

    Column {
        id: contentCol
        width: root.width
        spacing: Theme.spacingLg

        Column {
            width: parent.width
            spacing: 2

            Text {
                width: parent.width
                text: root.info.name || ""
                color: Theme.panelForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeBase
                font.weight: Font.DemiBold
                elide: Text.ElideRight
            }
            Text {
                width: parent.width
                visible: root.slots.length > 0
                text: root.filled === root.slots.length
                      ? qsTr("All %n slot(s) filled. Click one to change it.", "", root.slots.length)
                      : qsTr("%1 of %2 filled. Click a slot, or drop photos and videos on it.")
                            .arg(root.filled).arg(root.slots.length)
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
                wrapMode: Text.WordWrap
            }
        }

        ThemedButton {
            width: parent.width
            visible: root.slots.length > 1
            variant: root.filled === 0 ? "primary" : "secondary"
            glyph: Theme.icons.image
            text: root.filled === 0 ? qsTr("Fill with several photos…") : qsTr("Fill the empty slots…")
            tooltip: qsTr("Pick several files at once: they go in order into the empty slots")
            onClicked: root.pickFiles("", true)
        }

        Flow {
            id: slotFlow
            width: parent.width
            spacing: Theme.spacingSm
            readonly property int columns: Math.max(3, Math.floor((width + spacing) / (78 + spacing)))
            readonly property real tile: Math.floor((width - spacing * (columns - 1)) / columns)

            Repeater {
                model: root.slots

                delegate: Rectangle {
                    id: tile
                    required property var modelData
                    readonly property bool empty: modelData.empty === true
                    width: slotFlow.tile
                    height: Math.round(slotFlow.tile * 1.33)
                    radius: Theme.radiusSm
                    color: Theme.panelAccent
                    border.width: drop.containsDrag || tileHover.hovered ? 2 : 1
                    border.color: drop.containsDrag ? Theme.primary
                                  : (tile.empty ? Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.6)
                                                : Theme.panelBorder)
                    clip: true

                    HoverHandler { id: tileHover; cursorShape: Qt.PointingHandCursor }

                    Image {
                        anchors.fill: parent
                        anchors.margins: 1
                        visible: !tile.empty
                        source: tile.empty ? "" : (tile.modelData.thumbnail || "")
                        fillMode: Image.PreserveAspectCrop
                        asynchronous: true
                        sourceSize: Qt.size(Math.ceil(width * Screen.devicePixelRatio), Math.ceil(height * Screen.devicePixelRatio))
                    }

                    Column {
                        anchors.centerIn: parent
                        visible: tile.empty
                        spacing: 4
                        IconGlyph {
                            anchors.horizontalCenter: parent.horizontalCenter
                            glyph: Theme.icons.plus
                            iconSize: 18
                            iconColor: Theme.primary
                        }
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: qsTr("Add")
                            color: Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                    }

                    Rectangle {
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.margins: 4
                        width: 18
                        height: 18
                        radius: 9
                        color: Qt.rgba(0, 0, 0, 0.72)
                        Text {
                            anchors.centerIn: parent
                            text: tile.modelData.number
                            color: "white"
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                            font.weight: Font.DemiBold
                        }
                    }

                    Rectangle {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        height: 16
                        color: Qt.rgba(0, 0, 0, 0.6)
                        Text {
                            anchors.centerIn: parent
                            text: tile.modelData.durationSec.toFixed(1) + " s"
                            color: "white"
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                    }

                    ThemedToolTip {
                        visible: tileHover.hovered && !drop.containsDrag
                        text: tile.empty
                              ? qsTr("Slot %1 (%2 s): click to choose a photo or video, or drop one here")
                                    .arg(tile.modelData.number).arg(tile.modelData.durationSec.toFixed(1))
                              : qsTr("%1 — click to change it").arg(tile.modelData.mediaName || tile.modelData.label)
                    }

                    TapHandler {
                        onTapped: root.pickFiles(tile.modelData.clipId, false)
                    }

                    // Files from the file manager, or a card dragged from Media.
                    DropArea {
                        id: drop
                        anchors.fill: parent
                        keys: ["text/uri-list", "text/plain"]
                        onDropped: (event) => {
                            if (event.hasUrls && event.urls.length > 0) {
                                EditorState.fillTemplateSlotsFromUrls(root.assetId, tile.modelData.clipId, event.urls)
                            } else {
                                const payload = AssetDrag.current.kind === "media" ? AssetDrag.current.payload : event.text
                                const assetId = AssetLibrary.assetIdAt(parseInt(payload))
                                if (assetId)
                                    EditorState.fillTemplateSlot(tile.modelData.clipId, assetId)
                            }
                            event.acceptProposedAction()
                        }
                    }
                }
            }
        }

        Column {
            width: parent.width
            spacing: Theme.spacingSm
            visible: root.texts.length > 0

            Text {
                text: qsTr("Texts")
                color: Theme.panelForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                font.weight: Font.DemiBold
            }

            Repeater {
                model: root.texts

                delegate: Column {
                    id: textRow
                    required property var modelData
                    width: parent.width
                    spacing: 2

                    Text {
                        text: textRow.modelData.label || qsTr("Text")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                    ThemedTextField {
                        width: parent.width
                        text: textRow.modelData.text
                        // On every keystroke would put one undo step per letter.
                        onEditingFinished: EditorState.setTemplateText(textRow.modelData.clipId, text)
                    }
                }
            }
        }

        ThemedButton {
            width: parent.width
            variant: "ghost"
            glyph: Theme.icons.layers
            text: qsTr("Open the composition")
            tooltip: qsTr("Edit the template inside: move, retime or restyle any of its layers")
            onClicked: EditorState.openCompositeAsset(root.assetId)
        }
    }
}
