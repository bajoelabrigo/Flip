import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import QtMultimedia
import Drift
import ".."
import "."

// Sound effects tab: the "sound-effects" extras by category. Play a sound to hear it; add puts it
// on an audio track at the playhead.
Item {
    id: root

    signal added()

    property var categories: EditorState.soundEffectCategories()
    property var allSounds: EditorState.soundEffects()
    readonly property bool hasSounds: allSounds.length > 0
    property string activeCategory: categories.length > 0 ? categories[0].id : ""
    readonly property string query: search.text.trim().toLowerCase()
    readonly property var currentSounds: {
        const q = root.query
        if (q.length > 0)
            return root.allSounds.filter(s => (s.label || "").toLowerCase().indexOf(q) >= 0)
        return root.allSounds.filter(s => s.category === root.activeCategory)
    }

    Connections {
        target: Addons
        function onKindChanged(kind) {
            if (kind !== "sound-effects")
                return
            root.categories = EditorState.soundEffectCategories()
            root.allSounds = EditorState.soundEffects()
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
            placeholderText: qsTr("Search sounds")
            font.family: Theme.fontFamily
        }

        Item { width: 1; height: root.hasSounds ? Theme.spacingMd : 0 }

        AssetCategoryChips {
            id: chips
            width: parent.width
            categories: root.hasSounds ? root.categories : []
            activeCategory: root.activeCategory
            searching: root.query.length > 0
            onCategoryActivated: (categoryId) => root.activeCategory = categoryId
        }

        Item {
            width: parent.width
            height: Math.max(0, parent.height - Theme.pagePadding - search.height
                             - (root.hasSounds ? Theme.spacingMd : 0) - chips.height)

            EmptyState {
                visible: !root.hasSounds
                x: Theme.pagePadding
                y: Theme.pagePadding
                width: parent.width - Theme.pagePadding * 2
                compact: true
                glyph: Theme.icons.music
                title: qsTr("No sound effects installed")
                hint: qsTr("Install the sound effects pack: whooshes, pops, bells, impacts and more.")
                actionText: qsTr("Get extras")
                actionVariant: "primary"
                onActionTriggered: root.Window.window.openAddonManager("sound-effects")
            }

            ListView {
                id: list
                x: Theme.pagePadding
                width: parent.width - Theme.pagePadding * 2
                height: parent.height
                topMargin: Theme.pagePadding
                bottomMargin: Theme.pagePadding
                visible: root.currentSounds.length > 0
                clip: true
                spacing: Theme.spacingSm
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: AppScrollBar { }
                model: root.currentSounds

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
                        anchors.right: addButton.left
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
                            text: Number(row.modelData.duration || 0).toFixed(1) + " s"
                            color: Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
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
