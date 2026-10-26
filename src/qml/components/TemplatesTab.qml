import QtQuick
import QtQuick.Controls.Basic
import Drift

// The Templates tab: scene templates (a whole edit with photo slots, CapCut's "Templates") and
// effect templates (music-synced effects for a clip you already have), one at a time.
Column {
    id: root
    // The panel's sidebar drives the category (0.23): its chips are not shown.
    property bool panelDriven: false
    spacing: 0

    // "scenes" | "effects"; the panel remembers it with the tab.
    property string mode: "scenes"
    // Passed through to the effect browser, which the panel restores.
    property string searchText: ""
    property string activeCategory: ""
    // The Scenes / Effects chips. Off on the desktop, where the sidebar lists the two as
    // Templates › My templates and Effect templates (AssetsPanel).
    property bool showModeChips: true
    readonly property string favoritesId: "__favorites__"
    // The open browser's categories, for the panel's tree (0.23).
    readonly property var categories: modeLoader.item && modeLoader.item.categories ? modeLoader.item.categories : []
    // The tree sets activeCategory here; it goes on to the open browser.
    onActiveCategoryChanged: {
        if (modeLoader.item && modeLoader.item.activeCategory !== root.activeCategory)
            modeLoader.item.activeCategory = root.activeCategory
    }

    Row {
        id: modeRow
        visible: root.showModeChips
        height: visible ? implicitHeight : 0
        x: Theme.pagePadding
        topPadding: Theme.spacingSm
        bottomPadding: Theme.spacingSm
        spacing: Theme.spacingSm

        ThemedChip {
            text: qsTr("Scenes")
            selected: root.mode === "scenes"
            tooltip: qsTr("Whole edits with slots for your photos and videos")
            onClicked: root.mode = "scenes"
        }
        ThemedChip {
            text: qsTr("Effects")
            selected: root.mode === "effects"
            tooltip: qsTr("Music-synced effects for a clip you already have")
            onClicked: root.mode = "effects"
        }
    }

    Loader {
        id: modeLoader
        width: parent.width
        height: parent.height - modeRow.height
        sourceComponent: root.mode === "scenes" ? scenes : effects
    }

    Component {
        id: scenes
        SceneTemplateBrowser {
            panelDriven: root.panelDriven
            onActiveCategoryChanged: root.activeCategory = activeCategory
        }
    }

    Component {
        id: effects
        EffectTemplateBrowser {
            panelDriven: root.panelDriven
            Component.onCompleted: {
                if (root.searchText.length > 0)
                    searchText = root.searchText
                if (root.activeCategory.length > 0)
                    activeCategory = root.activeCategory
            }
            onSearchTextChanged: root.searchText = searchText
            onActiveCategoryChanged: root.activeCategory = activeCategory
        }
    }
}
