import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift

// The home screen, laid out like Filmora's (Jorge, 2026-10-18): a side bar with the way in to the
// account at its foot; the format and "Open project" along the top; one wide "Create project"
// button with a carousel of what is new beside it; a row of quick tools; and the local projects
// (a frame, the length and the date, from ProjectFileController's recent-project cards), as a grid
// or a list. Shown at startup when "Reopen last project on startup" is off, from the editor's Home
// button, and when the editor window is closed.
Rectangle {
    id: root

    signal newProjectRequested()
    // A new project already in this canvas (0×0: decide from the first clip) and, for the tool
    // shortcuts, the assets tab to land on.
    signal newProjectWithSetupRequested(int width, int height, string tabId)
    signal openProjectRequested()
    signal openRecentRequested(string path)
    // "Try an example" (0.27): a short ready-made video to play with.
    signal sampleRequested()

    color: Theme.homeBackground

    component NavItem: Rectangle {
        id: navItem
        property string glyph
        property string label
        property bool current: false
        signal activated()
        width: parent ? parent.width : 0
        height: 40
        radius: Theme.radiusMd
        color: current ? Theme.homeActive : (navMouse.containsMouse ? Theme.popoverHover : "transparent")
        Row {
            anchors.left: parent.left
            anchors.leftMargin: Theme.spacingXl
            anchors.verticalCenter: parent.verticalCenter
            spacing: Theme.spacingLg
            IconGlyph {
                anchors.verticalCenter: parent.verticalCenter
                glyph: navItem.glyph
                iconSize: 17
                iconColor: navItem.current ? Theme.primary : Theme.foreground
            }
            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: navItem.label
                color: Theme.foreground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                font.weight: navItem.current ? Font.DemiBold : Font.Normal
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
    property bool searching: false
    // Grid of frames (Filmora's default) or a list with the details.
    property bool listView: false
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

    // Quick tools under the Create button, icon over the name as in Filmora. Each opens a new
    // project on that tab (or in that format).
    readonly property var tools: [
        { label: qsTr("Auto captions"), glyph: Theme.icons.captions, tab: "subtitles", w: 0, h: 0 },
        { label: qsTr("Text to speech"), glyph: Theme.icons.micVocal, tab: "speech", w: 0, h: 0 },
        // Stock › Templates when there is a Stock: "My templates" is empty for someone new.
        { label: qsTr("Templates"), glyph: Theme.icons.layers, tab: Market.configured ? "market:template" : "templates", w: 0, h: 0 },
        { label: qsTr("Filters"), glyph: Theme.icons.blend, tab: "filters", w: 0, h: 0 },
        { label: qsTr("Stickers"), glyph: Theme.icons.smile, tab: "stickers", w: 0, h: 0 },
        { label: qsTr("Vertical video"), glyph: Theme.icons.smartphone, tab: "", w: 1080, h: 1920 },
        { label: qsTr("Stock"), glyph: Theme.icons.store, tab: "market", w: 0, h: 0 }
    ].filter(t => t.tab.indexOf("market") !== 0 || Market.configured)

    // The carousel beside Create: what is new, each slide a way in.
    readonly property var slides: {
        const out = []
        if (Market.configured && Market.newsCount > 0)
            out.push({ title: qsTr("New in Stock"), detail: Market.newsSummary, glyph: Theme.icons.store,
                       tab: "market", from: "#25ecd5", to: "#3b6cf6" })
        out.push({ title: qsTr("300 YouTuber-style templates"), detail: qsTr("Challenges, top 10s, podcasts, intros and end screens, free in Stock"),
                   glyph: Theme.icons.layers, tab: Market.configured ? "market" : "templates", from: "#ff7a59", to: "#c2185b" })
        out.push({ title: qsTr("Filters"), detail: qsTr("LUTs and colour effects, one click on the clip"),
                   glyph: Theme.icons.blend, tab: "filters", from: "#8b5cf6", to: "#3b6cf6" })
        out.push({ title: qsTr("Auto captions"), detail: qsTr("Subtitles from the voice, on your computer, without internet"),
                   glyph: Theme.icons.captions, tab: "subtitles", from: "#2cb0f0", to: "#25ecd5" })
        return out
    }
    property int slideIndex: 0

    Timer {
        interval: 5000
        repeat: true
        running: root.visible && root.slides.length > 1 && !bannerHover.hovered
        onTriggered: root.slideIndex = (root.slideIndex + 1) % root.slides.length
    }

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

    function create() {
        const f = root.formats[root.formatIndex]
        if (f.w > 0)
            root.newProjectWithSetupRequested(f.w, f.h, "")
        else
            root.newProjectRequested()
    }

    // --- Side bar ----------------------------------------------------------------------------
    Item {
        id: side
        width: 232
        anchors.top: parent.top
        anchors.bottom: parent.bottom

        Column {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: Theme.spacingXl
            spacing: 28

            Row {
                x: Theme.spacingMd
                spacing: Theme.spacingLg
                Image {
                    source: "qrc:/app/drift.png"
                    width: 40
                    height: 40
                    sourceSize: Qt.size(80, 80)
                }
                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    Text {
                        text: "Flip"
                        color: Theme.foreground
                        font.family: Theme.fontFamily
                        font.pixelSize: 13
                    }
                    Text {
                        text: "Studio"
                        color: Theme.foreground
                        font.family: Theme.fontFamily
                        font.pixelSize: 20
                        font.weight: Font.Bold
                    }
                }
            }

            Column {
                width: parent.width
                spacing: Theme.spacingSm

                NavItem { glyph: Theme.icons.plus; label: qsTr("Create project"); current: true; onActivated: root.create() }
                NavItem {
                    visible: Market.configured
                    glyph: Theme.icons.store
                    label: qsTr("Stock")
                    onActivated: root.newProjectWithSetupRequested(0, 0, "market")
                }
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
                NavItem {
                    glyph: Theme.icons.monitor
                    label: qsTr("Edit online")
                    onActivated: Qt.openUrlExternally("https://getflipstudio.com/editor/")
                }
            }
        }

        // The account at the foot, as in Filmora: picture and name, or the way in.
        Rectangle {
            visible: Account.available
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: Theme.spacingXl
            height: 64
            radius: Theme.radiusMd
            color: accountHover.hovered ? Theme.homeActive : Theme.homeCard
            Accessible.role: Accessible.Button
            Accessible.name: qsTr("My account")

            Row {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingLg
                anchors.rightMargin: Theme.spacingLg
                spacing: Theme.spacingLg

                AccountAvatar {
                    size: 38
                    anchors.verticalCenter: parent.verticalCenter
                }
                Column {
                    width: parent.width - 38 - parent.spacing
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 3
                    Text {
                        width: parent.width
                        elide: Text.ElideRight
                        text: Account.signedIn
                              ? (Account.name.length > 0 ? Account.name : Account.email)
                              : qsTr("Click to sign in")
                        color: Account.signedIn ? Theme.foreground : Theme.primary
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                        font.weight: Account.signedIn ? Font.DemiBold : Font.Normal
                        font.underline: !Account.signedIn
                    }
                    Text {
                        width: parent.width
                        elide: Text.ElideRight
                        text: Account.signedIn ? Account.email : qsTr("Everything is free")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                }
            }
            HoverHandler { id: accountHover; cursorShape: Qt.PointingHandCursor }
            TapHandler { onTapped: root.Window.window.openAccount() }
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
            x: 8
            y: 20
            width: flick.width - 36
            spacing: 22

            // Format on the left, Open project on the right.
            Item {
                width: parent.width
                height: 32

                Rectangle {
                    id: formatButton
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    width: formatRow.implicitWidth + Theme.spacingXl * 2
                    height: 32
                    radius: Theme.radiusSm
                    color: formatHover.hovered || formatMenu.opened ? Theme.homeActive : Theme.homeCard
                    Row {
                        id: formatRow
                        anchors.centerIn: parent
                        spacing: Theme.spacingMd
                        IconGlyph {
                            anchors.verticalCenter: parent.verticalCenter
                            glyph: Theme.icons.ratio
                            iconSize: 14
                            iconColor: Theme.foreground
                        }
                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: root.formats[root.formatIndex].label
                            color: Theme.foreground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                        IconGlyph {
                            anchors.verticalCenter: parent.verticalCenter
                            glyph: Theme.icons.chevronDown
                            iconSize: 14
                            iconColor: Theme.mutedForeground
                        }
                    }
                    HoverHandler { id: formatHover; cursorShape: Qt.PointingHandCursor }
                    TapHandler { onTapped: formatMenu.popup(formatButton, 0, formatButton.height + 4) }

                    ThemedContextMenu {
                        id: formatMenu
                        minimumWidth: 220
                        Instantiator {
                            model: root.formats
                            delegate: ThemedMenuItem {
                                required property var modelData
                                required property int index
                                text: modelData.label + " · " + modelData.hint
                                icon.name: root.formatIndex === index ? Theme.icons.check : ""
                                onTriggered: root.formatIndex = index
                            }
                            onObjectAdded: (index, object) => formatMenu.insertItem(index, object)
                            onObjectRemoved: (index, object) => formatMenu.removeItem(object)
                        }
                    }
                }

                ThemedButton {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    variant: "secondary"
                    glyph: Theme.icons.folder
                    text: qsTr("Open project")
                    onClicked: root.openProjectRequested()
                }
            }

            // Create project, with the carousel beside it.
            Item {
                id: heroRow
                width: parent.width
                height: 150
                readonly property bool showBanner: width >= 720
                readonly property real bannerWidth: showBanner ? Math.min(300, width * 0.28) : 0

                Rectangle {
                    id: createButton
                    width: parent.width - heroRow.bannerWidth - (heroRow.showBanner ? Theme.spacingXl : 0)
                    height: parent.height
                    radius: 10
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: Theme.exportGradientTop }
                        GradientStop { position: 0.75; color: Theme.exportGradientBottom }
                        GradientStop { position: 1.0; color: Theme.exportGlow }
                    }
                    scale: createMouse.pressed ? 0.99 : 1.0
                    Behavior on scale {
                        NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                    }

                    Row {
                        anchors.centerIn: parent
                        spacing: 12
                        IconGlyph {
                            anchors.verticalCenter: parent.verticalCenter
                            glyph: Theme.icons.plus
                            iconSize: 30
                            iconColor: "#0a0d0f"
                        }
                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: qsTr("Create project")
                            color: "#0a0d0f"
                            font.family: Theme.fontFamily
                            font.pixelSize: 28
                            font.weight: Font.Medium
                        }
                    }
                    MouseArea {
                        id: createMouse
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.create()
                    }
                }

                Item {
                    id: banner
                    visible: heroRow.showBanner
                    anchors.right: parent.right
                    width: heroRow.bannerWidth
                    height: parent.height
                    readonly property var slide: root.slides[Math.min(root.slideIndex, root.slides.length - 1)]

                    Rectangle {
                        id: slideArt
                        width: parent.width
                        height: parent.height - 52
                        radius: 8
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: banner.slide.from }
                            GradientStop { position: 1.0; color: banner.slide.to }
                        }
                        IconGlyph {
                            anchors.centerIn: parent
                            glyph: banner.slide.glyph
                            iconSize: 40
                            iconColor: "#ffffff"
                        }
                        Behavior on opacity {
                            NumberAnimation { duration: Theme.durationBase }
                        }
                    }

                    Row {
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: slideArt.bottom
                        anchors.topMargin: 6
                        spacing: 4
                        Repeater {
                            model: root.slides.length
                            delegate: Rectangle {
                                required property int index
                                width: index === root.slideIndex ? 14 : 5
                                height: 3
                                radius: 1.5
                                color: index === root.slideIndex ? Theme.primary : Theme.panelMuted
                                TapHandler { onTapped: root.slideIndex = parent.index }
                            }
                        }
                    }

                    Column {
                        anchors.bottom: parent.bottom
                        width: parent.width
                        spacing: 2
                        Text {
                            width: parent.width
                            elide: Text.ElideRight
                            text: banner.slide.title
                            color: Theme.foreground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeSm
                            font.weight: Font.DemiBold
                        }
                        Text {
                            width: parent.width
                            elide: Text.ElideRight
                            maximumLineCount: 2
                            wrapMode: Text.WordWrap
                            text: banner.slide.detail
                            color: Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                    }

                    HoverHandler { id: bannerHover; cursorShape: Qt.PointingHandCursor }
                    TapHandler { onTapped: root.newProjectWithSetupRequested(0, 0, banner.slide.tab) }
                }
            }

            // Quick tools: an icon over its name, in one row.
            Row {
                id: toolRow
                width: parent.width
                readonly property real cellW: width / Math.max(1, root.tools.length)
                Repeater {
                    model: root.tools
                    delegate: Item {
                        id: toolCell
                        required property var modelData
                        width: toolRow.cellW
                        height: 72
                        Column {
                            anchors.centerIn: parent
                            spacing: 8
                            IconGlyph {
                                anchors.horizontalCenter: parent.horizontalCenter
                                glyph: toolCell.modelData.glyph
                                iconSize: 22
                                iconColor: toolHover.hovered ? Theme.primary : Theme.foreground
                            }
                            Text {
                                anchors.horizontalCenter: parent.horizontalCenter
                                width: Math.min(implicitWidth, toolCell.width - 8)
                                horizontalAlignment: Text.AlignHCenter
                                elide: Text.ElideRight
                                text: toolCell.modelData.label
                                color: toolHover.hovered ? Theme.foreground : Theme.mutedForeground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeXs
                            }
                        }
                        HoverHandler { id: toolHover; cursorShape: Qt.PointingHandCursor }
                        TapHandler {
                            onTapped: root.newProjectWithSetupRequested(toolCell.modelData.w, toolCell.modelData.h,
                                                                        toolCell.modelData.tab)
                        }
                    }
                }
            }

            // Try an example (0.27, Jorge): for someone with no projects yet, a short video already
            // put together (a wave, a motocross jump, a dog, neon and fireworks) to touch and learn.
            Rectangle {
                id: sampleCard
                width: Math.min(parent.width, 560)
                height: 120
                visible: root.items.length === 0
                radius: Theme.radiusLg
                color: sampleHover.hovered ? Theme.panelAccent : Theme.panelBackground
                border.width: Theme.borderWidth
                border.color: sampleHover.hovered ? Theme.primary : Theme.panelBorder

                Image {
                    id: sampleThumb
                    x: 10
                    y: 10
                    width: 56
                    height: 100
                    fillMode: Image.PreserveAspectCrop
                    source: "https://getflipstudio.com/modelos/ejemplo/ejemplo-1.jpg"
                    sourceSize: Qt.size(112, 200)
                    asynchronous: true
                }
                Column {
                    anchors.left: sampleThumb.right
                    anchors.leftMargin: 16
                    anchors.right: parent.right
                    anchors.rightMargin: 16
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 6
                    Text {
                        width: parent.width
                        text: qsTr("Try an example")
                        color: Theme.foreground
                        font.family: Theme.fontFamily
                        font.pixelSize: 16
                        font.weight: Font.DemiBold
                    }
                    Text {
                        width: parent.width
                        text: EditorState.projectFile.sampleDownloading
                              ? qsTr("Downloading…")
                              : qsTr("A 15-second video ready to edit: change it, cut it and export it to learn how it works.")
                        wrapMode: Text.WordWrap
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSm
                    }
                }
                HoverHandler { id: sampleHover; cursorShape: Qt.PointingHandCursor }
                TapHandler {
                    enabled: !EditorState.projectFile.sampleDownloading
                    onTapped: root.sampleRequested()
                }
            }

            // Local projects: search, grid or list.
            Item {
                width: parent.width
                height: 32
                Text {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    text: qsTr("Local projects")
                    color: Theme.foreground
                    font.family: Theme.fontFamily
                    font.pixelSize: 15
                    font.weight: Font.DemiBold
                }
                Row {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: Theme.spacingSm
                    ThemedTextField {
                        id: searchField
                        visible: root.searching
                        width: 200
                        placeholderText: qsTr("Search projects")
                        font.family: Theme.fontFamily
                        onTextChanged: root.query = text
                    }
                    IconButton {
                        glyph: Theme.icons.search
                        variant: "ghost"
                        active: root.searching
                        tooltip: qsTr("Search projects")
                        onClicked: {
                            root.searching = !root.searching
                            if (!root.searching)
                                searchField.text = ""
                            else
                                searchField.forceActiveFocus()
                        }
                    }
                    IconButton {
                        glyph: root.listView ? Theme.icons.layoutGrid : Theme.icons.list
                        variant: "ghost"
                        tooltip: root.listView ? qsTr("Show as a grid") : qsTr("Show as a list")
                        onClicked: root.listView = !root.listView
                    }
                }
            }

            // Nothing yet: the empty tray, as in Filmora.
            Column {
                width: parent.width
                visible: root.shownItems.length === 0
                topPadding: 48
                spacing: Theme.spacingLg
                IconGlyph {
                    anchors.horizontalCenter: parent.horizontalCenter
                    glyph: root.items.length === 0 ? Theme.icons.folder : Theme.icons.search
                    iconSize: 48
                    iconColor: Theme.panelMuted
                }
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: root.items.length === 0
                          ? qsTr("Your projects will show up here once you save them.")
                          : qsTr("No project matches “%1”.").arg(root.query.trim())
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSm
                }
            }

            // The list: one row a project.
            Column {
                width: parent.width
                visible: root.listView && root.shownItems.length > 0
                spacing: 2
                Repeater {
                    model: root.listView ? root.shownItems : []
                    delegate: Rectangle {
                        id: row
                        required property var modelData
                        readonly property bool exists: modelData.exists !== false
                        width: parent.width
                        height: 52
                        radius: Theme.radiusSm
                        color: rowHover.hovered ? Theme.homeActive : "transparent"
                        opacity: exists ? 1 : 0.55
                        Row {
                            anchors.fill: parent
                            anchors.leftMargin: Theme.spacingLg
                            spacing: Theme.spacingLg
                            Rectangle {
                                anchors.verticalCenter: parent.verticalCenter
                                width: 64
                                height: 40
                                radius: 4
                                color: "#050506"
                                clip: true
                                Image {
                                    anchors.fill: parent
                                    visible: !!row.modelData.thumbnail
                                    source: row.modelData.thumbnail || ""
                                    fillMode: Image.PreserveAspectCrop
                                    asynchronous: true
                                    sourceSize: Qt.size(128, 80)
                                }
                            }
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                width: parent.width * 0.4
                                elide: Text.ElideRight
                                text: (row.modelData.name || "").replace(/\.(flip|drift)$/i, "")
                                      + (row.exists ? "" : qsTr(" (missing)"))
                                color: Theme.foreground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeSm
                            }
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                width: parent.width * 0.2
                                text: root.when(row.modelData.modified)
                                color: Theme.mutedForeground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeXs
                            }
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: ((row.modelData.width || 0) > 0
                                       ? row.modelData.width + "×" + row.modelData.height + " · " : "")
                                      + root.clock(row.modelData.duration)
                                color: Theme.mutedForeground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeXs
                            }
                        }
                        HoverHandler { id: rowHover; cursorShape: row.exists ? Qt.PointingHandCursor : Qt.ArrowCursor }
                        TapHandler {
                            onTapped: if (row.exists) root.openRecentRequested(row.modelData.path)
                        }
                        IconButton {
                            anchors.right: parent.right
                            anchors.rightMargin: Theme.spacingMd
                            anchors.verticalCenter: parent.verticalCenter
                            visible: rowHover.hovered
                            glyph: Theme.icons.x
                            variant: "ghost"
                            buttonSize: 24
                            iconSize: 12
                            tooltip: qsTr("Remove from recents")
                            onClicked: EditorState.projectFile.removeRecentProject(row.modelData.path)
                        }
                        ThemedToolTip {
                            text: row.exists ? row.modelData.path
                                             : qsTr("This file has been moved or deleted:\n%1").arg(row.modelData.path)
                            visible: rowHover.hovered
                        }
                    }
                }
            }

            // The grid: a frame a project.
            Flow {
                id: grid
                width: parent.width
                spacing: 16
                visible: !root.listView && root.shownItems.length > 0

                Repeater {
                    model: root.listView ? [] : root.shownItems
                    delegate: Item {
                        id: card
                        required property var modelData
                        readonly property bool exists: modelData.exists !== false
                        readonly property bool hovered: cardHover.hovered
                        width: 168
                        height: 112 + 44
                        opacity: exists ? 1 : 0.55

                        HoverHandler { id: cardHover }

                        Rectangle {
                            id: thumbBox
                            width: 168
                            height: 112
                            radius: 8
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
                                sourceSize: Qt.size(336, 224)
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
                                text: (card.modelData.name || "").replace(/\.(flip|drift)$/i, "")
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
