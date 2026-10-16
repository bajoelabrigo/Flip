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

    function timeLabel(seconds) {
        const s = Math.max(0, seconds)
        return Math.floor(s / 60) + ":" + (s % 60).toFixed(1).padStart(4, "0")
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
                        // When it shows up in the template: what tells the slots of a pile apart.
                        Text {
                            anchors.centerIn: parent
                            text: root.timeLabel(tile.modelData.startSec)
                            color: "white"
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                    }

                    ThemedToolTip {
                        visible: tileHover.hovered && !drop.containsDrag
                        text: tile.empty
                              ? qsTr("Slot %1 (from %2): click to choose a photo or video, or drop one here")
                                    .arg(tile.modelData.number).arg(root.timeLabel(tile.modelData.startSec))
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

        // The text form: every editable text at once, named by what it is for (business name,
        // phone, price…), applied together as one undo step.
        Column {
            id: textForm
            width: parent.width
            spacing: Theme.spacingSm
            visible: root.texts.length > 0

            property var drafts: ({})
            property int draftCount: 0

            function edit(clipId, value, original) {
                const next = Object.assign({}, drafts)
                if (value === original)
                    delete next[clipId]
                else
                    next[clipId] = value
                drafts = next
                draftCount = Object.keys(next).length
            }
            function apply() {
                if (draftCount === 0)
                    return
                const pending = drafts
                drafts = ({})
                draftCount = 0
                EditorState.setTemplateTexts(pending)
            }

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
                        text: textRow.modelData.fieldLabel || textRow.modelData.label || qsTr("Text")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                    ThemedTextField {
                        width: parent.width
                        text: textRow.modelData.text
                        placeholderText: textRow.modelData.original || ""
                        onTextEdited: textForm.edit(textRow.modelData.clipId, text, textRow.modelData.text)
                        onAccepted: textForm.apply()
                    }
                }
            }

            ThemedButton {
                width: parent.width
                variant: textForm.draftCount > 0 ? "primary" : "secondary"
                enabled: textForm.draftCount > 0
                glyph: Theme.icons.check
                text: textForm.draftCount > 0 ? qsTr("Apply %n text(s)", "", textForm.draftCount) : qsTr("Apply texts")
                tooltip: qsTr("Changes every text you edited at once (one undo step)")
                onClicked: textForm.apply()
            }
        }

        // Music: another song, and the cuts between the photos moved to its beat.
        Column {
            width: parent.width
            spacing: Theme.spacingSm

            Text {
                text: qsTr("Music")
                color: Theme.panelForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                font.weight: Font.DemiBold
            }
            Text {
                width: parent.width
                text: root.info.hasMusic ? (root.info.musicName || qsTr("The template's music"))
                                         : qsTr("No music in this template")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
                elide: Text.ElideRight
            }
            ThemedCheckBox {
                id: fitOnChange
                width: parent.width
                text: qsTr("Fit the cuts to the beat of the new song")
                checked: true
            }
            ThemedButton {
                width: parent.width
                variant: "secondary"
                glyph: Theme.icons.music
                text: root.info.hasMusic ? qsTr("Change the music…") : qsTr("Add music…")
                tooltip: qsTr("A song from your computer, cut to the template's length")
                onClicked: {
                    const url = FileDialogs.openFile(qsTr("Choose a song"), [AssetLibrary.mediaNameFilter()])
                    if (url.toString().length > 0)
                        EditorState.replaceTemplateMusic(root.assetId, url, fitOnChange.checked)
                }
            }
            ThemedButton {
                width: parent.width
                variant: "ghost"
                glyph: Theme.icons.audioLines
                enabled: !EditorState.templateBeatFitRunning && root.slots.length > 1
                text: EditorState.templateBeatFitRunning ? qsTr("Listening to the music…") : qsTr("Fit the cuts to the beat")
                tooltip: qsTr("Moves the change from one photo to the next onto the nearest beat, keeping their order (one undo step). Without a beat, a steady 120 BPM.")
                onClicked: EditorState.fitTemplateCutsToBeat(root.assetId)
            }
        }

        ThemedButton {
            width: parent.width
            visible: root.info.inside !== true
            variant: "secondary"
            glyph: Theme.icons.shuffle
            text: qsTr("Change template…")
            tooltip: qsTr("Another template with the same photos and texts")
            onClicked: EditorState.requestTemplatePicker("swap", root.assetId, [])
        }

        ThemedButton {
            id: brandButton
            width: parent.width
            property bool hasKit: !EditorState.brandKit().empty
            visible: hasKit
            variant: "ghost"
            glyph: Theme.icons.store
            text: qsTr("Apply my brand")
            tooltip: qsTr("Your logo, colours and font (Templates › My brand)")
            onClicked: EditorState.applyBrandKitToTemplate(root.assetId)
            Connections {
                target: EditorState
                function onBrandKitChanged() { brandButton.hasKit = !EditorState.brandKit().empty }
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

        ThemedButton {
            width: parent.width
            variant: "ghost"
            glyph: Theme.icons.download
            text: qsTr("Save as my template…")
            tooltip: qsTr("Keep this version, with your changes, in Templates › Scenes")
            onClicked: EditorState.requestSaveTemplate(root.assetId)
        }
    }
}
