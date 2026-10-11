import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift

// The home screen, laid out like CapCut's: create a project in the format you publish in, jump
// straight to a tool, or pick up one of your projects (a frame, the length and the date, from
// ProjectFileController's recent-project cards). Shown at startup when "Reopen last project on
// startup" is off, and from the editor's Home button.
Rectangle {
    id: root

    signal newProjectRequested()
    // A new project already in this canvas (0×0: decide from the first clip) and, for the tool
    // shortcuts, the assets tab to land on.
    signal newProjectWithSetupRequested(int width, int height, string tabId)
    signal openProjectRequested()
    signal openRecentRequested(string path)

    color: Theme.appBackground

    component NavItem: Rectangle {
        id: navItem
        property string glyph
        property string label
        property bool current: false
        signal activated()
        width: parent ? parent.width : 0
        height: 36
        radius: Theme.radiusSm
        color: current ? Theme.panelAccent : (navMouse.containsMouse ? Theme.popoverHover : "transparent")
        Row {
            anchors.left: parent.left
            anchors.leftMargin: Theme.spacingLg
            anchors.verticalCenter: parent.verticalCenter
            spacing: Theme.spacingLg
            IconGlyph {
                anchors.verticalCenter: parent.verticalCenter
                glyph: navItem.glyph
                iconSize: 16
                iconColor: navItem.current ? Theme.foreground : Theme.mutedForeground
            }
            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: navItem.label
                color: navItem.current ? Theme.foreground : Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
            }
        }
        MouseArea {
            id: navMouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: navItem.activated()
        }
    }

    readonly property var items: EditorState.projectFile.recentProjects
    property int formatIndex: 0
    property string query: ""
    readonly property var shownItems: {
        const q = root.query.trim().toLowerCase()
        return q.length === 0 ? root.items
                              : root.items.filter(p => (p.name || "").toLowerCase().indexOf(q) >= 0)
    }

    readonly property var formats: [
        { label: qsTr("Automatic"), hint: qsTr("Like your first video"), w: 0, h: 0 },
        { label: "16:9", hint: "YouTube", w: 1920, h: 1080 },
        { label: "9:16", hint: qsTr("TikTok, Reels, Shorts"), w: 1080, h: 1920 },
        { label: "1:1", hint: qsTr("Square"), w: 1080, h: 1080 },
        { label: "4:5", hint: "Instagram", w: 1080, h: 1350 }
    ]

    readonly property var tools: [
        { label: qsTr("Auto captions"), detail: qsTr("Subtitles from the voice, offline"),
          glyph: Theme.icons.captions, tab: "subtitles", w: 0, h: 0 },
        { label: qsTr("Text templates"), detail: qsTr("Titles, verses, lower thirds"),
          glyph: Theme.icons.type, tab: "text", w: 0, h: 0 },
        { label: qsTr("Stickers"), detail: qsTr("3D and animated emojis"),
          glyph: Theme.icons.smile, tab: "stickers", w: 0, h: 0 },
        { label: qsTr("Vertical video"), detail: qsTr("For TikTok, Reels and Shorts"),
          glyph: Theme.icons.smartphone, tab: "", w: 1080, h: 1920 }
    ]

    function clock(seconds) {
        const s = Math.round(seconds || 0)
        return String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0")
    }

    function when(ms) {
        if (!ms)
            return ""
        const d = new Date(ms)
        const days = Math.floor((Date.now() - ms) / 86400000)
        if (days === 0)
            return qsTr("Today, %1").arg(Qt.formatTime(d, "hh:mm"))
        if (days === 1)
            return qsTr("Yesterday")
        return Qt.formatDate(d, Qt.locale().dateFormat(Locale.ShortFormat))
    }

    // --- Side bar ----------------------------------------------------------------------------
    Rectangle {
        id: side
        width: 220
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        color: Theme.panelBackground

        Rectangle {
            anchors.right: parent.right
            width: Theme.borderWidth
            height: parent.height
            color: Theme.panelBorder
        }

        Column {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: Theme.spacingXl
            spacing: Theme.spacingXl

            Row {
                spacing: Theme.spacingMd
                Image {
                    source: "qrc:/app/drift.png"
                    width: 28
                    height: 28
                    sourceSize: Qt.size(56, 56)
                }
                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Flip Studio"
                    color: Theme.foreground
                    font.family: Theme.fontFamily
                    font.pixelSize: 16
                    font.weight: Font.Bold
                }
            }

            Column {
                width: parent.width
                spacing: Theme.spacingXs

                NavItem { glyph: "house"; label: qsTr("Home"); current: true }
                NavItem {
                    glyph: Theme.icons.package
                    label: qsTr("Extras")
                    onActivated: root.Window.window.openAddonManager("")
                }
                NavItem {
                    glyph: Theme.icons.settings
                    label: qsTr("Settings")
                    onActivated: root.Window.window.openSettings()
                }
            }
        }

        // The web editor, for when you are not at this computer.
        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: Theme.spacingXl
            height: promo.implicitHeight + Theme.spacingXl * 2
            radius: Theme.radiusMd
            color: Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.12)
            border.width: Theme.borderWidth
            border.color: Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.4)

            Column {
                id: promo
                anchors.fill: parent
                anchors.margins: Theme.spacingXl
                spacing: 2
                Text {
                    width: parent.width
                    text: qsTr("Edit online")
                    color: Theme.foreground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSm
                    font.weight: Font.Medium
                }
                Text {
                    width: parent.width
                    wrapMode: Text.WordWrap
                    text: qsTr("Flip Studio in your browser, at getflipstudio.com/editor")
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                }
            }
            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: Qt.openUrlExternally("https://getflipstudio.com/editor/")
            }
        }
    }

    // --- Main column -------------------------------------------------------------------------
    Flickable {
        id: flick
        anchors.left: side.right
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        contentWidth: width
        contentHeight: main.implicitHeight + 48
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: AppScrollBar { }

        Column {
            id: main
            x: 28
            y: 24
            width: flick.width - 56
            spacing: 24

            // Create project, in a format.
            Rectangle {
                width: parent.width
                height: createColumn.implicitHeight + 48
                radius: 16
                gradient: Gradient {
                    orientation: Gradient.Horizontal
                    GradientStop { position: 0.0; color: "#2a2108" }
                    GradientStop { position: 0.7; color: Theme.panelBackground }
                }
                border.width: Theme.borderWidth
                border.color: Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.3)

                Column {
                    id: createColumn
                    x: 24
                    y: 24
                    width: parent.width - 48
                    spacing: Theme.spacingXl

                    Rectangle {
                        id: createButton
                        width: parent.width
                        height: 92
                        radius: 12
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: Theme.exportGradientTop }
                            GradientStop { position: 1.0; color: Theme.exportGradientBottom }
                        }
                        scale: createMouse.pressed ? 0.99 : 1.0

                        Row {
                            anchors.centerIn: parent
                            spacing: 14
                            Rectangle {
                                anchors.verticalCenter: parent.verticalCenter
                                width: 36
                                height: 36
                                radius: 8
                                color: Theme.primaryForeground
                                IconGlyph {
                                    anchors.centerIn: parent
                                    glyph: Theme.icons.plus
                                    iconSize: 22
                                    iconColor: Theme.primary
                                }
                            }
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: qsTr("Create project")
                                color: Theme.primaryForeground
                                font.family: Theme.fontFamily
                                font.pixelSize: 26
                                font.weight: Font.Bold
                            }
                        }
                        MouseArea {
                            id: createMouse
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                const f = root.formats[root.formatIndex]
                                if (f.w > 0)
                                    root.newProjectWithSetupRequested(f.w, f.h, "")
                                else
                                    root.newProjectRequested()
                            }
                        }
                    }

                    Flow {
                        width: parent.width
                        spacing: Theme.spacingMd
                        Repeater {
                            model: root.formats
                            delegate: Rectangle {
                                required property var modelData
                                required property int index
                                readonly property bool on: root.formatIndex === index
                                width: Math.max(110, formatText.implicitWidth + 24)
                                height: 44
                                radius: Theme.radiusSm
                                color: on ? Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.12)
                                          : Qt.rgba(0, 0, 0, 0.25)
                                border.width: Theme.borderWidth
                                border.color: on ? Theme.primary : Theme.panelMuted
                                Column {
                                    id: formatText
                                    anchors.left: parent.left
                                    anchors.leftMargin: 12
                                    anchors.verticalCenter: parent.verticalCenter
                                    Text {
                                        text: modelData.label
                                        color: Theme.foreground
                                        font.family: Theme.fontFamily
                                        font.pixelSize: Theme.fontSizeXs
                                        font.weight: Font.Bold
                                    }
                                    Text {
                                        text: modelData.hint
                                        color: Theme.mutedForeground
                                        font.family: Theme.fontFamily
                                        font.pixelSize: Theme.fontSizeXs
                                    }
                                }
                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.formatIndex = index
                                }
                            }
                        }
                    }
                }
            }

            // Start with a tool.
            Grid {
                id: toolGrid
                width: parent.width
                columns: Math.max(1, Math.floor((width + spacing) / (220 + spacing)))
                spacing: 12
                readonly property real cellW: (width - spacing * (columns - 1)) / columns
                Repeater {
                    model: root.tools
                    delegate: Rectangle {
                        id: toolCard
                        required property var modelData
                        width: toolGrid.cellW
                        height: 112
                        radius: 12
                        color: toolMouse.containsMouse ? Theme.panelAccent : Theme.panelBackground
                        border.width: Theme.borderWidth
                        border.color: toolMouse.containsMouse ? Theme.panelMuted : Theme.panelBorder
                        Column {
                            x: 16
                            y: 16
                            width: parent.width - 32
                            spacing: 4
                            Rectangle {
                                width: 34
                                height: 34
                                radius: 8
                                color: Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.12)
                                IconGlyph {
                                    anchors.centerIn: parent
                                    glyph: toolCard.modelData.glyph
                                    iconSize: 18
                                    iconColor: Theme.primary
                                }
                            }
                            Item { width: 1; height: 4 }
                            Text {
                                width: parent.width
                                text: toolCard.modelData.label
                                color: Theme.foreground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeSm
                                font.weight: Font.Bold
                                elide: Text.ElideRight
                            }
                            Text {
                                width: parent.width
                                text: toolCard.modelData.detail
                                color: Theme.mutedForeground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeXs
                                elide: Text.ElideRight
                            }
                        }
                        MouseArea {
                            id: toolMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.newProjectWithSetupRequested(toolCard.modelData.w, toolCard.modelData.h,
                                                                         toolCard.modelData.tab)
                        }
                    }
                }
            }

            // Projects.
            Item {
                width: parent.width
                height: 32
                Text {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    text: qsTr("Projects")
                    color: Theme.foreground
                    font.family: Theme.fontFamily
                    font.pixelSize: 16
                    font.weight: Font.Bold
                }
                Row {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: Theme.spacingMd
                    ThemedTextField {
                        width: 200
                        placeholderText: qsTr("Search projects")
                        font.family: Theme.fontFamily
                        onTextChanged: root.query = text
                    }
                    ThemedButton {
                        variant: "secondary"
                        glyph: Theme.icons.folder
                        text: qsTr("Open project…")
                        onClicked: root.openProjectRequested()
                    }
                }
            }

            ThemedLabel {
                width: parent.width
                visible: root.shownItems.length === 0
                wrapMode: Text.WordWrap
                text: root.items.length === 0
                      ? qsTr("Your projects will show up here once you save them.")
                      : qsTr("No project matches “%1”.").arg(root.query.trim())
            }

            Flow {
                id: grid
                width: parent.width
                spacing: 16
                visible: root.shownItems.length > 0

                Repeater {
                    model: root.shownItems
                    delegate: Item {
                        id: card
                        required property var modelData
                        readonly property bool exists: modelData.exists !== false
                        readonly property bool hovered: cardHover.hovered
                        width: 150
                        height: 150 + 44
                        opacity: exists ? 1 : 0.55

                        HoverHandler { id: cardHover }

                        Rectangle {
                            id: thumbBox
                            width: 150
                            height: 150
                            radius: 10
                            color: "#050506"
                            border.width: card.hovered && card.exists ? 2 : Theme.borderWidth
                            border.color: card.hovered && card.exists ? Theme.primary : Theme.panelBorder
                            clip: true

                            Image {
                                anchors.fill: parent
                                anchors.margins: 1
                                visible: !!card.modelData.thumbnail
                                source: card.modelData.thumbnail || ""
                                fillMode: Image.PreserveAspectCrop
                                asynchronous: true
                                sourceSize: Qt.size(300, 300)
                            }
                            IconGlyph {
                                anchors.centerIn: parent
                                visible: !card.modelData.thumbnail
                                glyph: Theme.icons.film
                                iconSize: 24
                                iconColor: Theme.mutedForeground
                            }
                            Rectangle {
                                visible: (card.modelData.duration || 0) > 0
                                anchors.right: parent.right
                                anchors.bottom: parent.bottom
                                anchors.margins: 6
                                width: durText.implicitWidth + 10
                                height: 18
                                radius: 4
                                color: Qt.rgba(0, 0, 0, 0.7)
                                Text {
                                    id: durText
                                    anchors.centerIn: parent
                                    text: root.clock(card.modelData.duration)
                                    color: "#ffffff"
                                    font.family: Theme.monoFontFamily
                                    font.pixelSize: 11
                                }
                            }
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: card.exists ? Qt.PointingHandCursor : Qt.ArrowCursor
                                onClicked: {
                                    if (card.exists)
                                        root.openRecentRequested(card.modelData.path)
                                }
                            }
                            IconButton {
                                anchors.top: parent.top
                                anchors.right: parent.right
                                anchors.margins: 4
                                visible: card.hovered
                                glyph: Theme.icons.x
                                variant: "ghost"
                                buttonSize: 22
                                iconSize: 12
                                tooltip: qsTr("Remove from recents")
                                onClicked: EditorState.projectFile.removeRecentProject(card.modelData.path)
                            }
                        }

                        Column {
                            anchors.top: thumbBox.bottom
                            anchors.topMargin: 6
                            width: parent.width
                            spacing: 1
                            Text {
                                width: parent.width
                                text: (card.modelData.name || "").replace(/\.drift$/i, "")
                                      + (card.exists ? "" : qsTr(" (missing)"))
                                color: Theme.foreground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeSm
                                font.weight: Font.Medium
                                elide: Text.ElideRight
                            }
                            Text {
                                width: parent.width
                                text: root.when(card.modelData.modified)
                                      + ((card.modelData.width || 0) > 0
                                         ? " · " + card.modelData.width + "×" + card.modelData.height : "")
                                color: Theme.mutedForeground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeXs
                                elide: Text.ElideRight
                            }
                        }

                        ThemedToolTip {
                            text: card.exists ? card.modelData.path
                                              : qsTr("This file has been moved or deleted:\n%1").arg(card.modelData.path)
                            visible: card.hovered
                        }
                    }
                }
            }
        }
    }
}
