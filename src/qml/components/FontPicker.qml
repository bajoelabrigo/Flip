import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift
import "assets"

// A font selector that previews each family in its own face. The popup filters by search,
// favorites, recently used and catalog category, and can import the user's own font files.
// ThemedComboBox cannot do this: its delegate binds a single `root.font` for every row.
Item {
    id: root

    property string family: ""
    signal familyPicked(string family)

    readonly property string displayFamily: family === "" ? qsTr("Select a font") : family
    readonly property string allId: "__all__"
    readonly property string recentId: "__recent__"
    readonly property string favoritesId: "__favorites__"

    implicitHeight: 30
    implicitWidth: 200

    // Every family once, in catalog order: { name, previewFamily, category, group }.
    property var allFamilies: []
    // Chips: categories that have at least one family.
    property var categories: []
    property string activeCategory: allId
    property int favoritesTick: 0
    property int recentTick: 0

    // True while no font addon is installed, which is the state of a fresh install.
    property bool usingSystemFonts: false

    readonly property string query: search.text.trim().toLowerCase()

    // One model shape whatever the source, so the delegate has a single contract: name is what the
    // user picks, previewFamily is the face to render it in, group is the section header.
    ListModel {
        id: familyModel
    }

    function rebuild() {
        const catalog = EditorState.fontCatalog()
        const families = []
        const seen = {}
        const cats = []
        for (let i = 0; i < catalog.length; ++i) {
            const c = catalog[i]
            families.push({ "name": c.family, "previewFamily": c.qtFamily,
                            "category": c.category, "group": c.categoryLabel })
            if (!seen[c.category]) {
                seen[c.category] = true
                cats.push({ "id": c.category, "label": c.categoryLabel })
            }
        }
        root.usingSystemFonts = families.length === 0
        if (root.usingSystemFonts) {
            // Fonts are an addon, so an empty catalog is the normal starting state — fall back to
            // whatever the system has and offer the pack.
            const system = Qt.fontFamilies()
            for (let i = 0; i < system.length; ++i)
                families.push({ "name": system[i], "previewFamily": system[i],
                                "category": "system", "group": qsTr("System fonts") })
        }
        root.allFamilies = families
        root.categories = cats
        root.refilter()
    }

    function refilter() {
        void root.favoritesTick
        familyModel.clear()
        const q = root.query
        const cat = root.activeCategory
        let list = root.allFamilies
        if (q.length > 0) {
            list = list.filter(f => f.name.toLowerCase().indexOf(q) >= 0)
        } else if (cat === root.favoritesId) {
            list = list.filter(f => EditorState.isAssetFavorite("fonts", f.name))
        } else if (cat === root.recentId) {
            const recent = EditorState.recentFonts()
            const byName = {}
            for (let i = 0; i < list.length; ++i)
                byName[list[i].name] = list[i]
            list = recent.filter(n => byName[n] !== undefined).map(n => byName[n])
        } else if (cat !== root.allId) {
            list = list.filter(f => f.category === cat)
        }
        for (let i = 0; i < list.length; ++i)
            familyModel.append(list[i])
    }

    function pick(name) {
        EditorState.noteRecentFont(name)
        root.familyPicked(name)
    }

    function importFonts() {
        const urls = FileDialogs.openFiles(qsTr("Import fonts"),
                                           [qsTr("Fonts (*.ttf *.otf)")])
        if (!urls || urls.length === 0)
            return
        const result = EditorState.importFonts(urls)
        if (result.ok && result.families.length > 0) {
            root.activeCategory = "mine"
            search.text = ""
            root.pick(result.families[0])
        }
    }

    onActiveCategoryChanged: refilter()
    onQueryChanged: refilter()
    Component.onCompleted: root.rebuild()

    Connections {
        target: Addons
        function onKindChanged(kind) {
            if (kind === "fonts")
                root.rebuild()
        }
    }

    Connections {
        target: EditorState
        function onFontCatalogChanged() { root.rebuild() }
        function onAssetFavoritesChanged() {
            root.favoritesTick++
            if (root.activeCategory === root.favoritesId)
                root.refilter()
        }
    }

    function changeFontDelta(delta) {
        if (familyModel.count === 0)
            return;

        let currentIndex = -1;
        for (let i = 0; i < familyModel.count; ++i) {
            if (familyModel.get(i).name === root.family) {
                currentIndex = i;
                break;
            }
        }

        let nextIndex = 0;
        if (currentIndex === -1) {
            nextIndex = delta > 0 ? 0 : familyModel.count - 1;
        } else {
            nextIndex = currentIndex + delta;
            nextIndex = Math.max(0, Math.min(familyModel.count - 1, nextIndex));
        }

        if (nextIndex !== currentIndex) {
            const nextFamily = familyModel.get(nextIndex).name;
            root.familyPicked(nextFamily);
            list.currentIndex = nextIndex;
            list.positionViewAtIndex(nextIndex, ListView.Contain);
        }
    }

    Keys.onUpPressed: (event) => {
        changeFontDelta(-1)
        event.accepted = true
    }
    Keys.onDownPressed: (event) => {
        changeFontDelta(1)
        event.accepted = true
    }
    Keys.onReturnPressed: (event) => {
        if (popup.visible) {
            popup.close()
            event.accepted = true
        }
    }
    Keys.onEnterPressed: (event) => {
        if (popup.visible) {
            popup.close()
            event.accepted = true
        }
    }
    Keys.onEscapePressed: (event) => {
        if (popup.visible) {
            popup.close()
            event.accepted = true
        }
    }

    Rectangle {
        id: trigger
        anchors.fill: parent
        radius: Theme.radiusSm
        color: Theme.panelAccent
        border.width: (popup.visible || root.activeFocus) ? 1 : 0
        border.color: root.activeFocus ? Theme.primary : Theme.panelSecondaryBorder

        Text {
            anchors.left: parent.left
            anchors.leftMargin: 8
            anchors.right: chevron.left
            anchors.rightMargin: 4
            anchors.verticalCenter: parent.verticalCenter
            text: root.displayFamily
            // Preview the current selection in the face it actually is.
            font.family: root.family === "" ? Theme.fontFamily : root.family
            font.pixelSize: Theme.fontSizeSm
            color: Theme.panelForeground
            elide: Text.ElideRight
        }

        IconGlyph {
            id: chevron
            anchors.right: parent.right
            anchors.rightMargin: 8
            anchors.verticalCenter: parent.verticalCenter
            glyph: Theme.icons.chevronDown
            iconSize: 12
            iconColor: Theme.mutedForeground
        }

        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: {
                root.forceActiveFocus()
                if (popup.visible) {
                    popup.close()
                } else {
                    popup.open()
                }
            }
        }
    }

    Popup {
        id: popup

        onOpened: {
            root.refilter()
            let idx = -1;
            for (let i = 0; i < familyModel.count; ++i) {
                if (familyModel.get(i).name === root.family) {
                    idx = i;
                    break;
                }
            }
            list.currentIndex = idx;
            if (idx >= 0) {
                list.positionViewAtIndex(idx, ListView.Center);
            }
        }
        y: root.height + 2
        width: Math.max(root.width, 300)
        implicitHeight: 440
        padding: 1

        contentItem: Column {
            spacing: 0

            Item {
                width: parent.width
                height: Theme.spacingSm
            }

            ThemedTextField {
                id: search
                x: Theme.spacingSm
                width: parent.width - Theme.spacingSm * 2
                placeholderText: qsTr("Search fonts")
                font.family: Theme.fontFamily
            }

            Item {
                width: parent.width
                height: Theme.spacingSm
            }

            Flickable {
                id: chipFlick
                width: parent.width
                height: Theme.controlHeightSm
                visible: root.query.length === 0
                contentWidth: chipRow.width + Theme.spacingSm * 2
                flickableDirection: Flickable.HorizontalFlick
                boundsBehavior: Flickable.StopAtBounds
                clip: true

                Row {
                    id: chipRow
                    x: Theme.spacingSm
                    height: parent.height
                    spacing: Theme.spacingXs

                    IconButton {
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: Theme.icons.star
                        variant: "ghost"
                        buttonSize: Theme.controlHeightSm
                        iconSize: 14
                        active: root.activeCategory === root.favoritesId
                        tooltip: qsTr("Favorites")
                        onClicked: root.activeCategory = root.favoritesId
                    }

                    Repeater {
                        model: [{ "id": root.allId, "label": qsTr("All") },
                                { "id": root.recentId, "label": qsTr("Recent") }].concat(root.categories)
                        delegate: ThemedChip {
                            required property var modelData
                            anchors.verticalCenter: parent.verticalCenter
                            text: modelData.label
                            variant: "outline"
                            selected: root.activeCategory === modelData.id
                            onClicked: root.activeCategory = modelData.id
                        }
                    }
                }
            }

            Item {
                width: parent.width
                height: chipFlick.visible ? Theme.spacingXs : 0
            }

            ListView {
                id: list
                width: parent.width
                height: popup.availableHeight - search.height - Theme.spacingSm * 2
                        - (chipFlick.visible ? chipFlick.height + Theme.spacingXs : 0) - footer.height
                clip: true
                reuseItems: true
                model: familyModel
                currentIndex: -1
                ScrollBar.vertical: AppScrollBar {}

                header: Rectangle {
                    width: list.width
                    height: root.usingSystemFonts ? 40 : 0
                    visible: root.usingSystemFonts
                    color: Theme.panelSecondaryBg

                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 8
                        anchors.right: parent.right
                        anchors.rightMargin: 8
                        anchors.verticalCenter: parent.verticalCenter
                        text: qsTr("Install the font pack for curated families →")
                        color: Theme.primary
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSm
                        elide: Text.ElideRight
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            popup.close()
                            root.Window.window.openAddonManager("fonts")
                        }
                    }
                }

                // Section headers only where the list mixes categories.
                section.property: root.query.length === 0 && root.activeCategory === root.allId ? "group" : ""
                section.delegate: Rectangle {
                    required property string section
                    width: list.width
                    height: 24
                    color: Theme.panelSecondaryBg

                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 8
                        anchors.verticalCenter: parent.verticalCenter
                        text: parent.section
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                }

                Text {
                    anchors.centerIn: parent
                    width: parent.width - 32
                    visible: familyModel.count === 0
                    horizontalAlignment: Text.AlignHCenter
                    wrapMode: Text.WordWrap
                    text: root.query.length > 0 ? qsTr("No fonts match “%1”").arg(search.text.trim())
                          : root.activeCategory === root.favoritesId ? qsTr("Star fonts to keep them here.")
                          : root.activeCategory === root.recentId ? qsTr("Fonts you use will appear here.")
                          : qsTr("Nothing in this category")
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSm
                }

                // Roles come in as required properties. Declaring any required property puts the
                // delegate in required-properties mode, where the `model` context object is not
                // injected — so every role the delegate reads has to be declared here.
                delegate: Rectangle {
                    id: row
                    required property string name
                    required property string previewFamily

                    width: list.width
                    height: 36
                    color: rowMouse.containsMouse ? Theme.panelAccent
                                                  : (row.name === root.family ? Theme.panelSecondaryBg
                                                                              : "transparent")

                    Behavior on color {
                        ColorAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                    }

                    MouseArea {
                        id: rowMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            root.forceActiveFocus()
                            root.pick(row.name)
                            popup.close()
                        }
                    }

                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 8
                        anchors.right: star.left
                        anchors.rightMargin: 4
                        anchors.verticalCenter: parent.verticalCenter
                        text: row.name
                        font.family: row.previewFamily
                        font.pixelSize: 18
                        color: Theme.panelForeground
                        elide: Text.ElideRight
                    }

                    AssetFavoriteButton {
                        id: star
                        anchors.right: parent.right
                        anchors.rightMargin: 6
                        anchors.verticalCenter: parent.verticalCenter
                        visible: rowMouse.containsMouse || hovered || favorited
                        tabId: "fonts"
                        itemId: row.name
                    }
                }
            }

            Rectangle {
                id: footer
                width: parent.width
                height: 36
                color: Theme.panelSecondaryBg

                Row {
                    anchors.left: parent.left
                    anchors.leftMargin: Theme.spacingSm
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: Theme.spacingSm

                    ThemedButton {
                        text: qsTr("Import font…")
                        variant: "ghost"
                        onClicked: {
                            popup.close()
                            root.importFonts()
                        }
                    }

                    ThemedButton {
                        text: qsTr("More fonts")
                        variant: "ghost"
                        onClicked: {
                            popup.close()
                            root.Window.window.openAddonManager("fonts")
                        }
                    }
                }
            }
        }

        background: Rectangle {
            radius: Theme.radiusSm
            color: Theme.panelBackground
            border.width: 1
            border.color: Theme.panelBorder
        }
    }
}
