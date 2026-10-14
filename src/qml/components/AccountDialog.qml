import QtQuick
import QtQuick.Controls.Basic
import Drift

// "My account": the Flip Studio account at a glance (picture, name, email, since when), the
// user's favourites gathered from every panel, and the stock photos and videos downloaded on this
// computer. Opened from the picture in the editor header and on the start screen. Purchases and
// the user's store join it once the store exists.
ThemedDialog {
    id: root

    // Main jumps the assets panel to a tab ("music", "media", …) and closes this.
    signal assetsTabRequested(string tabId)
    signal settingsRequested()

    title: qsTr("My account")
    preferredWidth: 760
    showReject: false
    acceptText: qsTr("Done")

    property string section: "favorites"
    property int revision: 0

    // Favourite groups as the panels store them, with a name and the assets tab they live in.
    readonly property var favoriteGroups: [
        { id: "music", label: qsTr("Music"), tab: "music" },
        { id: "sounds", label: qsTr("Sounds"), tab: "sfx" },
        { id: "effects", label: qsTr("Effects"), tab: "effects" },
        { id: "transitions", label: qsTr("Transitions"), tab: "transitions" },
        { id: "templates", label: qsTr("Templates"), tab: "templates" },
        { id: "stickers", label: qsTr("Stickers"), tab: "stickers" },
        { id: "shapes", label: qsTr("Shapes"), tab: "shapes" },
        { id: "textStyles", label: qsTr("Text styles"), tab: "text" },
        { id: "textEffects", label: qsTr("Text effects"), tab: "text" },
        { id: "textBubbles", label: qsTr("Text bubbles"), tab: "text" },
        { id: "textAnimations", label: qsTr("Text animations"), tab: "text" },
        { id: "fonts", label: qsTr("Fonts"), tab: "text" },
        { id: "captionStyles", label: qsTr("Caption styles"), tab: "subtitles" },
        { id: "voices", label: qsTr("Voices"), tab: "speech" },
        { id: "retouch", label: qsTr("Retouch"), tab: "" }
    ]

    readonly property var favorites: {
        void root.revision
        const counts = EditorState.assetFavoriteCounts()
        const out = []
        for (const g of root.favoriteGroups) {
            if (counts[g.id])
                out.push(Object.assign({ count: counts[g.id] }, g))
        }
        // Groups this list does not know yet still show, under their stored name.
        for (const id in counts) {
            if (!root.favoriteGroups.some(g => g.id === id))
                out.push({ id: id, label: id, tab: "", count: counts[id] })
        }
        return out
    }

    readonly property var downloads: {
        void root.revision
        return Market.configured ? Market.downloadHistory() : []
    }

    readonly property int projectCount: EditorState.projectFile.recentProjects.length

    onOpened: root.revision++

    Connections {
        target: Market
        function onDownloadHistoryChanged() { root.revision++ }
    }

    contentItem: Column {
        spacing: Theme.spacingXl
        width: parent ? parent.width : 700

        // --- Who ---------------------------------------------------------------------------
        Row {
            width: parent.width
            spacing: Theme.spacingXl

            Rectangle {
                id: profileCard
                width: parent.width - planCard.width - parent.spacing
                height: 112
                radius: Theme.radiusMd
                color: Theme.panelSecondaryBg

                Row {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingXl
                    spacing: Theme.spacingXl

                    AccountAvatar {
                        size: 72
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Column {
                        width: parent.width - 72 - parent.spacing
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: Theme.spacingXs

                        ThemedLabel {
                            width: parent.width
                            size: "base"
                            tone: "default"
                            font.weight: Font.DemiBold
                            elide: Text.ElideRight
                            wrapMode: Text.NoWrap
                            text: Account.signedIn
                                  ? (Account.name.length > 0 ? Account.name : Account.email)
                                  : qsTr("Not signed in")
                        }
                        ThemedLabel {
                            width: parent.width
                            elide: Text.ElideRight
                            wrapMode: Text.NoWrap
                            visible: Account.signedIn && Account.name.length > 0
                            text: Account.email
                        }
                        ThemedLabel {
                            width: parent.width
                            text: {
                                const parts = []
                                if (Account.signedIn && !isNaN(Account.memberSince.getTime()))
                                    parts.push(qsTr("In Flip Studio since %1")
                                               .arg(Account.memberSince.toLocaleDateString(Qt.locale(), "MMMM yyyy")))
                                parts.push(qsTr("%n project(s)", "", root.projectCount))
                                return parts.join("  ·  ")
                            }
                        }
                        ThemedButton {
                            visible: !Account.signedIn && Account.available
                            variant: "primary"
                            glyph: Account.busy ? Theme.icons.spinner : Theme.icons.brandGoogle
                            text: Account.busy ? qsTr("Waiting for the browser…") : qsTr("Sign in with Google")
                            enabled: !Account.busy
                            onClicked: Account.signIn()
                        }
                    }
                }
            }

            Rectangle {
                id: planCard
                width: 220
                height: profileCard.height
                radius: Theme.radiusMd
                color: Theme.panelSecondaryBg

                Column {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingXl
                    spacing: Theme.spacingSm

                    ThemedLabel {
                        size: "sm"
                        tone: "default"
                        font.weight: Font.DemiBold
                        text: qsTr("Free plan")
                    }
                    ThemedLabel {
                        width: parent.width
                        text: qsTr("The whole editor, with no watermark.")
                    }
                }
            }
        }

        // --- Sections ----------------------------------------------------------------------
        Row {
            spacing: Theme.spacing2xl

            Repeater {
                model: [
                    { id: "favorites", label: qsTr("Favorites") },
                    { id: "downloads", label: qsTr("Stock downloads") }
                ]
                delegate: Item {
                    required property var modelData
                    readonly property bool active: root.section === modelData.id
                    width: sectionLabel.implicitWidth
                    height: sectionLabel.implicitHeight + Theme.spacingLg + 2
                    Accessible.role: Accessible.PageTab
                    Accessible.name: sectionLabel.text

                    Text {
                        id: sectionLabel
                        text: parent.modelData.label
                        color: parent.active || sectionHover.hovered ? Theme.panelForeground : Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSm
                        font.weight: parent.active ? Font.DemiBold : Font.Medium
                    }
                    Rectangle {
                        anchors.bottom: parent.bottom
                        width: parent.width
                        height: 2
                        radius: 1
                        color: Theme.primary
                        visible: parent.active
                    }
                    HoverHandler { id: sectionHover; cursorShape: Qt.PointingHandCursor }
                    TapHandler { onTapped: root.section = parent.modelData.id }
                }
            }
        }

        // Favourites: one row per group, with a jump to the panel that shows them.
        Column {
            width: parent.width
            spacing: Theme.spacingSm
            visible: root.section === "favorites"

            ThemedLabel {
                width: parent.width
                visible: root.favorites.length === 0
                text: qsTr("No favorites yet. Mark music, effects, text styles and more with the star in each panel and they gather here.")
            }

            Repeater {
                model: root.favorites
                delegate: Rectangle {
                    required property var modelData
                    width: parent.width
                    height: 44
                    radius: Theme.radiusSm
                    color: rowHover.hovered ? Theme.popoverHover : Theme.panelSecondaryBg

                    HoverHandler { id: rowHover }

                    IconGlyph {
                        id: star
                        anchors.left: parent.left
                        anchors.leftMargin: Theme.spacingLg
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: Theme.icons.star
                        iconSize: 16
                        iconColor: Theme.primary
                    }
                    ThemedLabel {
                        anchors.left: star.right
                        anchors.leftMargin: Theme.spacingMd
                        anchors.verticalCenter: parent.verticalCenter
                        size: "sm"
                        tone: "default"
                        text: parent.modelData.label
                    }
                    ThemedLabel {
                        anchors.right: openButton.left
                        anchors.rightMargin: Theme.spacingLg
                        anchors.verticalCenter: parent.verticalCenter
                        text: qsTr("%n favorite(s)", "", parent.modelData.count)
                    }
                    ThemedButton {
                        id: openButton
                        anchors.right: parent.right
                        anchors.rightMargin: Theme.spacingSm
                        anchors.verticalCenter: parent.verticalCenter
                        variant: "ghost"
                        visible: parent.modelData.tab.length > 0
                        text: qsTr("Open")
                        tooltip: qsTr("Opens the panel; pick ★ Favorites there")
                        onClicked: root.assetsTabRequested(parent.modelData.tab)
                    }
                }
            }
        }

        // Stock downloads: what came from Pexels and Pixabay onto this computer.
        Column {
            width: parent.width
            spacing: Theme.spacingMd
            visible: root.section === "downloads"

            ThemedLabel {
                width: parent.width
                visible: root.downloads.length === 0
                text: qsTr("Nothing downloaded from Stock yet. Free photos and videos you download there are listed here.")
            }

            Flickable {
                width: parent.width
                height: Math.min(downloadGrid.implicitHeight, 300)
                contentHeight: downloadGrid.implicitHeight
                clip: true
                visible: root.downloads.length > 0
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: AppScrollBar { }

                Flow {
                    id: downloadGrid
                    width: parent.width
                    spacing: Theme.spacingLg

                    Repeater {
                        model: root.downloads
                        delegate: Column {
                            required property var modelData
                            width: 132
                            spacing: Theme.spacingXs

                            Rectangle {
                                width: 132
                                height: 84
                                radius: Theme.radiusSm
                                color: Theme.panelSecondaryBg
                                clip: true

                                Image {
                                    anchors.fill: parent
                                    source: parent.parent.modelData.thumb || ""
                                    fillMode: Image.PreserveAspectCrop
                                    asynchronous: true
                                    opacity: parent.parent.modelData.exists ? 1 : 0.35
                                }
                                HoverHandler { cursorShape: Qt.PointingHandCursor }
                                TapHandler {
                                    onTapped: if (parent.parent.modelData.exists) root.assetsTabRequested("media")
                                }
                            }
                            ThemedLabel {
                                width: parent.width
                                elide: Text.ElideRight
                                wrapMode: Text.NoWrap
                                tone: "default"
                                text: parent.modelData.title
                            }
                            ThemedLabel {
                                width: parent.width
                                elide: Text.ElideRight
                                wrapMode: Text.NoWrap
                                text: parent.modelData.exists
                                      ? [parent.modelData.provider === "pixabay" ? "Pixabay" : "Pexels",
                                         Qt.formatDate(parent.modelData.at, Qt.locale().dateFormat(Locale.ShortFormat))].join(" · ")
                                      : qsTr("File moved or deleted")
                            }
                        }
                    }
                }
            }

            ThemedButton {
                visible: root.downloads.length > 0
                variant: "ghost"
                text: qsTr("Clear the list")
                tooltip: qsTr("Forgets this list; the downloaded files stay where they are")
                onClicked: Market.clearDownloadHistory()
            }
        }

        // --- Account actions ---------------------------------------------------------------
        Row {
            spacing: Theme.spacingMd

            ThemedButton {
                variant: "secondary"
                glyph: Theme.icons.settings
                text: qsTr("Account settings")
                onClicked: root.settingsRequested()
            }
            ThemedButton {
                visible: Account.signedIn
                variant: "ghost"
                glyph: Theme.icons.signOut
                text: qsTr("Sign out")
                onClicked: Account.signOut()
            }
        }
    }
}
