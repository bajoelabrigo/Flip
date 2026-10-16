import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift
import "assets"

// Scene templates (CapCut-style): tall cards showing the finished look; a tap puts the template at
// the playhead as one composition, whose slots the inspector's Fill template panel fills.
Column {
    id: root
    spacing: 0

    readonly property string favoritesId: "__favorites__"
    property var installed: EditorState.sceneTemplates()
    // Templates this account got from Stock that are not on this machine (another computer, a
    // reinstall): shown with a download badge, a tap fetches and uses them.
    readonly property var cloud: {
        const out = []
        const lib = Market.library || []
        for (let i = 0; i < lib.length; ++i) {
            const it = lib[i]
            const id = Market.sceneTemplateIdForItem(it.id || "")
            if (id === "" || it.downloadable === false || root.installed.some(t => t.id === id))
                continue
            out.push({ id: id, itemId: it.id, name: it.title || id, thumbnail: it.thumb_url || "",
                       category: it.category || "", categoryLabel: EditorState.sceneTemplateCategoryLabelFor(it.category || ""),
                       slots: it.slots || 0, durationSec: (it.duration_ms || 0) / 1000, tags: [], cloud: true })
        }
        return out
    }
    readonly property var catalog: installed.concat(cloud)
    readonly property var categories: {
        const out = EditorState.sceneTemplateCategoryList()
        for (let i = 0; i < cloud.length; ++i) {
            if (cloud[i].category && !out.some(c => c.id === cloud[i].category))
                out.push({ id: cloud[i].category, label: cloud[i].categoryLabel })
        }
        return out
    }
    property string activeCategory: categories.length > 0 ? categories[0].id : ""
    property alias searchText: search.text
    readonly property string query: search.text.trim().toLowerCase()
    property int favoritesTick: 0

    // Installing from Stock or Extras adds packages while the tab is open.
    function reload() {
        installed = EditorState.sceneTemplates()
        if (categories.length > 0 && activeCategory !== favoritesId
                && !categories.some(c => c.id === activeCategory))
            activeCategory = categories[0].id
    }

    Connections {
        target: EditorState
        function onAssetFavoritesChanged() { root.favoritesTick++ }
        function onSceneTemplatesChanged() { root.reload() }
    }

    function use(t) {
        if (t.cloud)
            Market.useSceneTemplate(t.itemId, t.name)
        else
            EditorState.insertSceneTemplate(t.id)
    }

    readonly property var visibleTemplates: {
        void root.favoritesTick
        const q = root.query
        if (q.length > 0) {
            return root.catalog.filter(function(t) {
                const hay = ((t.name || "") + " " + (t.categoryLabel || "") + " " + (t.tags || []).join(" ")).toLowerCase()
                return hay.indexOf(q) >= 0
            })
        }
        if (root.activeCategory === root.favoritesId)
            return root.catalog.filter(t => EditorState.isAssetFavorite("sceneTemplates", t.id))
        return root.catalog.filter(t => t.category === root.activeCategory)
    }

    function formatDuration(seconds) {
        const s = Math.max(0, Math.round(seconds))
        return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0")
    }

    AssetSearchBar {
        id: search
        placeholderText: qsTr("Search templates")
    }

    // The other way round: photos first, then the templates that fit them.
    Flow {
        id: quickRow
        x: 12
        width: parent.width - 24
        topPadding: Theme.spacingSm
        spacing: Theme.spacingSm

        ThemedButton {
            variant: "primary"
            glyph: Theme.icons.image
            text: qsTr("Use with my photos…")
            tooltip: qsTr("Choose your photos and videos first: Flip suggests the templates that fit them and fills them in")
            onClicked: {
                const urls = FileDialogs.openFiles(qsTr("Choose photos and videos"), [AssetLibrary.mediaNameFilter()])
                const chosen = urls.filter(u => u.toString().length > 0)
                if (chosen.length > 0)
                    EditorState.requestTemplatePicker("photos", "", chosen)
            }
        }
        ThemedButton {
            variant: "ghost"
            glyph: Theme.icons.store
            text: qsTr("My brand")
            tooltip: qsTr("Your logo, colours and font for Business templates")
            onClicked: EditorState.requestBrandKitDialog()
        }
    }

    Item {
        width: 1
        height: Theme.spacingSm
    }

    AssetCategoryChips {
        id: categoryChips
        width: parent.width
        categories: root.categories
        activeCategory: root.activeCategory
        searching: root.query.length > 0
        onCategoryActivated: (categoryId) => root.activeCategory = categoryId
    }

    Item {
        width: parent.width
        height: Math.max(0, parent.height - search.height - quickRow.height - Theme.spacingSm - categoryChips.height)

        EmptyState {
            anchors.centerIn: parent
            width: Math.min(parent.width - Theme.spacing3xl, 260)
            visible: root.catalog.length === 0
            compact: true
            glyph: Theme.icons.layers
            title: qsTr("No scene templates yet")
            hint: Market.authenticated
                  ? qsTr("Get them from Stock › Templates: they install here and stay in your account.")
                  : qsTr("Sign in and get them from Stock › Templates: they install here and stay in your account.")
        }

        Text {
            x: 12
            y: 12
            width: parent.width - 24
            visible: root.catalog.length > 0 && root.visibleTemplates.length === 0
            text: root.query.length > 0
                  ? qsTr("No templates match “%1”.").arg(search.text.trim())
                  : (root.activeCategory === root.favoritesId
                     ? qsTr("No favorites yet. Star templates to save them here.")
                     : qsTr("Nothing in this category."))
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSm
            wrapMode: Text.WordWrap
        }

        FontMetrics {
            id: labelMetrics
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeCard
            font.weight: Font.Medium
        }

        CategoryScrollOn {
            anchors.fill: grid
            flickable: grid
            categories: root.categories
            activeCategory: root.activeCategory
            active: root.query.length === 0
            onCategoryActivated: (categoryId) => root.activeCategory = categoryId
        }

        GridView {
            id: grid
            // Tall cards: a phone-shaped template wants a phone-shaped card.
            readonly property int columnCount: Math.max(2, Math.round(width / (Theme.assetCardWidth * 1.1 + Theme.assetCardGap)))
            readonly property real cardWidth: Math.floor(width / columnCount) - Theme.assetCardGap
            readonly property real cardHeight: Math.round(cardWidth * 16 / 9)
            x: 12
            width: parent.width - 24 + Theme.assetCardGap
            height: parent.height
            topMargin: 12
            bottomMargin: 12
            visible: root.visibleTemplates.length > 0
            clip: true
            reuseItems: true
            boundsBehavior: Flickable.StopAtBounds
            acceptedButtons: Theme.touchUi ? Qt.LeftButton : Qt.NoButton
            ScrollBar.vertical: AppScrollBar { }
            cellWidth: Math.floor(width / columnCount)
            cellHeight: cardHeight + 4 + Math.ceil(labelMetrics.height) * 2 + Theme.assetCardGap
            model: root.visibleTemplates

            delegate: Column {
                id: card
                required property var modelData
                width: grid.cardWidth
                spacing: 4

                Rectangle {
                    width: grid.cardWidth
                    height: grid.cardHeight
                    radius: Theme.radiusSm
                    color: Theme.panelAccent
                    border.width: cardHover.hovered ? 2 : 1
                    border.color: cardHover.hovered ? Theme.primary : Theme.panelBorder
                    clip: true

                    HoverHandler { id: cardHover }

                    Image {
                        anchors.fill: parent
                        anchors.margins: 1
                        source: card.modelData.thumbnail || ""
                        fillMode: Image.PreserveAspectCrop
                        asynchronous: true
                        sourceSize: Qt.size(Math.ceil(grid.cardWidth * Screen.devicePixelRatio),
                                            Math.ceil(grid.cardHeight * Screen.devicePixelRatio))
                        smooth: true
                    }

                    ThemedToolTip {
                        visible: cardHover.hovered && !dragSource.active
                        text: qsTr("%1 — click to add it at the playhead, then fill its photos in the panel on the right")
                              .arg(card.modelData.name)
                    }

                    AssetDragSource {
                        id: dragSource
                        anchors.fill: parent
                        hasContextMenu: true
                        onContextMenuRequested: cardMenu.popup()
                        kind: "sceneTemplate"
                        payload: card.modelData.id
                        label: card.modelData.name
                        glyph: Theme.icons.layers
                        onTapped: root.use(card.modelData)
                    }

                    ThemedContextMenu {
                        id: cardMenu
                        property bool favorited: false
                        onAboutToShow: favorited = EditorState.isAssetFavorite("sceneTemplates", card.modelData.id)

                        ThemedMenuItem {
                            text: qsTr("Add at the playhead")
                            icon.name: Theme.icons.plus
                            onTriggered: root.use(card.modelData)
                        }
                        ThemedMenuItem {
                            text: cardMenu.favorited ? qsTr("Remove from favorites") : qsTr("Add to favorites")
                            icon.name: Theme.icons.star
                            onTriggered: EditorState.toggleAssetFavorite("sceneTemplates", card.modelData.id)
                        }
                        ThemedMenuItem {
                            // Only one's own: ours come back from Stock, these would not.
                            visible: card.modelData.mine === true
                            text: qsTr("Delete template")
                            icon.name: Theme.icons.trash
                            onTriggered: EditorState.deleteUserSceneTemplate(card.modelData.id)
                        }
                    }

                    // How many photos it takes: the first thing anyone choosing a template asks.
                    Rectangle {
                        anchors.left: parent.left
                        anchors.bottom: parent.bottom
                        anchors.margins: 5
                        visible: card.modelData.slots > 0
                        width: slotRow.implicitWidth + 10
                        height: 20
                        radius: 10
                        color: Qt.rgba(0, 0, 0, 0.72)

                        Row {
                            id: slotRow
                            anchors.centerIn: parent
                            spacing: 3
                            IconGlyph {
                                anchors.verticalCenter: parent.verticalCenter
                                glyph: Theme.icons.image
                                iconSize: 11
                                iconColor: "white"
                            }
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: card.modelData.slots
                                color: "white"
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeXs
                                font.weight: Font.DemiBold
                            }
                        }
                    }

                    Rectangle {
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.margins: 5
                        visible: card.modelData.durationSec > 0
                        width: durationText.implicitWidth + 10
                        height: 18
                        radius: 9
                        color: Qt.rgba(0, 0, 0, 0.72)

                        Text {
                            id: durationText
                            anchors.centerIn: parent
                            text: root.formatDuration(card.modelData.durationSec)
                            color: "white"
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                            font.weight: Font.Medium
                        }
                    }

                    Rectangle {
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.margins: 5
                        width: 26
                        height: 26
                        radius: 13
                        z: 2
                        color: addMouse.pressed ? Qt.darker(Theme.primary, 1.15) : Theme.primary
                        border.width: 1
                        border.color: Qt.rgba(0, 0, 0, 0.35)
                        scale: addMouse.containsMouse ? 1.12 : 1.0

                        Behavior on scale {
                            NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                        }

                        IconGlyph {
                            anchors.centerIn: parent
                            glyph: Theme.icons.plus
                            iconSize: 15
                            iconColor: Theme.primaryForeground
                        }

                        Accessible.role: Accessible.Button
                        Accessible.name: qsTr("Use template")

                        ThemedToolTip {
                            visible: addMouse.containsMouse
                            text: qsTr("Use this template")
                        }

                        MouseArea {
                            id: addMouse
                            anchors.fill: parent
                            anchors.margins: -3
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.use(card.modelData)
                        }
                    }

                    // From the account, not on this machine yet: the first use downloads it.
                    Rectangle {
                        anchors.centerIn: parent
                        visible: card.modelData.cloud === true
                        width: 44
                        height: 44
                        radius: 22
                        color: Qt.rgba(0, 0, 0, 0.62)
                        IconGlyph {
                            anchors.centerIn: parent
                            glyph: Theme.icons.download
                            iconSize: 22
                            iconColor: "white"
                        }
                        HoverHandler { id: cloudHover }
                        ThemedToolTip {
                            visible: cloudHover.hovered
                            text: qsTr("In your account, not on this computer yet: using it downloads it")
                        }
                    }

                    Rectangle {
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        anchors.margins: 4
                        width: 22
                        height: 22
                        radius: 11
                        z: 2
                        color: Qt.rgba(Theme.panelBackground.r, Theme.panelBackground.g, Theme.panelBackground.b, 0.88)
                        border.width: 1
                        border.color: Theme.panelBorder

                        AssetFavoriteButton {
                            anchors.centerIn: parent
                            tabId: "sceneTemplates"
                            itemId: card.modelData.id
                        }
                    }
                }

                Text {
                    width: parent.width
                    text: card.modelData.name
                    color: Theme.panelForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeCard
                    font.weight: Font.Medium
                    horizontalAlignment: Text.AlignHCenter
                    elide: Text.ElideRight
                    maximumLineCount: 2
                    wrapMode: Text.WordWrap
                }
            }
        }
    }
}
