import QtQuick
import QtQuick.Controls.Basic
import Drift

// The Templates tab: scene templates (a whole edit with photo slots, CapCut's "Templates") and
// effect templates (music-synced effects for a clip you already have), one at a time.
Column {
    id: root
    spacing: 0

    // "scenes" | "effects"; the panel remembers it with the tab.
    property string mode: "scenes"
    // Passed through to the effect browser, which the panel restores.
    property string searchText: ""
    property string activeCategory: ""

    Row {
        id: modeRow
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
        width: parent.width
        height: parent.height - modeRow.height
        sourceComponent: root.mode === "scenes" ? scenes : effects
    }

    Component {
        id: scenes
        SceneTemplateBrowser { }
    }

    Component {
        id: effects
        EffectTemplateBrowser {
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
