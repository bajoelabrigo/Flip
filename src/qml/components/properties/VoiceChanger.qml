import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift
import ".."

// The Audio tab's "Voice changer": a grid of voice filters, characters and singing styles (the
// "voz.*" audio effects of the Modificador de voz pack), CapCut-style. One voice per clip; a click
// swaps it in one undo step, "None" takes it off, and "Apply to all" does it on every clip with
// sound. Favourites (the star) are kept like the other asset favourites.
Item {
    id: root

    property int clipDataRevision: 0
    property int catalogTick: 0
    property int favoritesTick: 0
    property string category: "voz-filtros"
    property bool applyToAll: false
    readonly property string query: search.text.trim().toLowerCase()
    readonly property string favoritesId: "__favorites__"

    readonly property var voices: {
        void catalogTick
        return EditorState.audioEffectCatalog().filter(e => e.id.startsWith("voz."))
    }
    readonly property string current: {
        void clipDataRevision
        if (EditorState.selectedTrack < 0 || EditorState.selectedClip < 0)
            return ""
        return EditorState.voiceFilterOf(EditorState.selectedTrack, EditorState.selectedClip)
    }
    readonly property real intensity: {
        void clipDataRevision
        if (root.current === "")
            return 1
        return EditorState.voiceFilterIntensity(EditorState.selectedTrack, EditorState.selectedClip)
    }
    readonly property var shown: {
        void favoritesTick
        const q = root.query
        return root.voices.filter(v => {
            if (q.length > 0)
                return v.label.toLowerCase().indexOf(q) >= 0
            if (root.category === root.favoritesId)
                return EditorState.isAssetFavorite("voices", v.id)
            return v.category === root.category
        })
    }

    implicitHeight: column.implicitHeight
    height: implicitHeight

    function apply(id) {
        EditorState.setVoiceFilter(EditorState.selectedTrack, EditorState.selectedClip, id, root.applyToAll)
    }

    Connections {
        target: EditorState
        function onSelectionChanged() { root.clipDataRevision++ }
        function onSelectedClipDataChanged() { root.clipDataRevision++ }
        function onTracksChanged() { root.clipDataRevision++ }
        function onAssetFavoritesChanged() { root.favoritesTick++ }
    }

    Connections {
        target: Addons
        function onKindChanged(kind) {
            if (kind === "audio-effects")
                root.catalogTick++
        }
    }

    Column {
        id: column
        width: root.width
        spacing: Theme.spacingMd

        // Without the pack there is nothing to choose from: offer it.
        Column {
            width: parent.width
            spacing: Theme.spacingSm
            visible: root.voices.length === 0

            Text {
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("Change your voice with more than a hundred filters: telephone, radio, cave, robot, monster, chipmunk, harmonies and more. Install the Voice changer pack from Extras.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            ThemedButton {
                width: parent.width
                variant: "primary"
                text: qsTr("Get the Voice changer")
                onClicked: root.Window.window.openAddonManager("audio-effects")
            }
        }

        Column {
            width: parent.width
            spacing: Theme.spacingMd
            visible: root.voices.length > 0

            ThemedCheckBox {
                width: parent.width
                text: qsTr("Apply to all")
                checked: root.applyToAll
                onToggled: root.applyToAll = checked
                ToolTip.visible: hovered
                ToolTip.text: qsTr("The next voice you pick goes on every clip with sound")
            }

            ThemedTextField {
                id: search
                width: parent.width
                placeholderText: qsTr("Search voices")
            }

            Flow {
                width: parent.width
                spacing: Theme.spacingXs
                visible: root.query.length === 0

                Repeater {
                    model: [
                        { "id": root.favoritesId, "label": "★" },
                        { "id": "voz-filtros", "label": qsTr("Voice filters") },
                        { "id": "voz-personajes", "label": qsTr("Voice characters") },
                        { "id": "voz-cancion", "label": qsTr("Voice to song") }
                    ]
                    delegate: ThemedChip {
                        required property var modelData
                        text: modelData.label
                        variant: "outline"
                        selected: root.category === modelData.id
                        onClicked: root.category = modelData.id
                    }
                }
            }

            Text {
                width: parent.width
                visible: root.shown.length === 0
                wrapMode: Text.WordWrap
                text: root.category === root.favoritesId && root.query.length === 0
                      ? qsTr("Right-click a voice to keep it here.")
                      : qsTr("No voice matches.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            Grid {
                id: grid
                width: parent.width
                readonly property int cols: Math.max(3, Math.floor((width + spacing) / (76 + spacing)))
                readonly property real tile: (width - spacing * (cols - 1)) / cols
                columns: cols
                spacing: Theme.spacingXs

                // "None" first, as in CapCut.
                Repeater {
                    model: [{ "id": "", "label": qsTr("None") }].concat(root.shown)
                    delegate: Rectangle {
                        id: tile
                        required property var modelData
                        readonly property bool isCurrent: root.current === modelData.id
                        readonly property bool favorite: {
                            void root.favoritesTick
                            return modelData.id !== "" && EditorState.isAssetFavorite("voices", modelData.id)
                        }
                        width: grid.tile
                        height: grid.tile * 0.8
                        radius: Theme.radiusSm
                        color: mouse.containsMouse ? Theme.panelAccent : Theme.panelSecondaryBg
                        border.width: isCurrent ? 2 : 1
                        border.color: isCurrent ? Theme.primary : Theme.panelBorder

                        Text {
                            anchors.fill: parent
                            anchors.margins: 4
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            wrapMode: Text.WordWrap
                            maximumLineCount: 2
                            elide: Text.ElideRight
                            text: tile.modelData.label
                            color: tile.isCurrent ? Theme.primary : Theme.panelForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }

                        Text {
                            visible: tile.favorite
                            anchors.top: parent.top
                            anchors.right: parent.right
                            anchors.margins: 3
                            text: "★"
                            color: Theme.primary
                            font.pixelSize: 9
                        }

                        MouseArea {
                            id: mouse
                            anchors.fill: parent
                            hoverEnabled: true
                            acceptedButtons: Qt.LeftButton | Qt.RightButton
                            cursorShape: Qt.PointingHandCursor
                            onClicked: mouseEvent => {
                                if (mouseEvent.button === Qt.RightButton) {
                                    if (tile.modelData.id !== "")
                                        EditorState.toggleAssetFavorite("voices", tile.modelData.id)
                                    return
                                }
                                root.apply(tile.modelData.id)
                            }
                        }

                        ThemedToolTip {
                            visible: mouse.containsMouse && tile.modelData.id !== ""
                            text: qsTr("%1 — click to apply, right-click to add to favorites").arg(tile.modelData.label)
                        }
                    }
                }
            }

            // How strongly the chosen voice replaces the original.
            Column {
                width: parent.width
                spacing: Theme.spacingXs
                visible: root.current !== ""

                Row {
                    width: parent.width
                    Text {
                        width: parent.width / 2
                        text: qsTr("Intensity")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                    Text {
                        width: parent.width / 2
                        horizontalAlignment: Text.AlignRight
                        text: Math.round(intensitySlider.value * 100) + " %"
                        color: Theme.panelForeground
                        font.family: Theme.monoFontFamily
                        font.pixelSize: Theme.fontSizeSm
                    }
                }

                ThemedSlider {
                    id: intensitySlider
                    width: parent.width
                    label: qsTr("Intensity")
                    from: 0
                    to: 1
                    Binding on value {
                        when: !intensitySlider.pressed
                        value: root.intensity
                    }
                    onPressedChanged: {
                        if (!pressed)
                            EditorState.setVoiceFilterIntensity(EditorState.selectedTrack, EditorState.selectedClip, value)
                    }
                }
            }
        }
    }
}
