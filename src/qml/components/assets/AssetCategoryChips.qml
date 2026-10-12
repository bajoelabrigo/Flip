import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// Category filter: favorites star, then the category chips wrapped over as many rows as they
// need, the way the Text tab lays out its sections. A chevron folds the chips down to their
// first row when they would take too much of the panel; they start unfolded.
// ⭐ | [Color] [Glitch] [Blur] …   ⌃
//     [Retro] [Light] …
Item {
    id: root

    readonly property string favoritesId: "__favorites__"
    // "My effects": what the user imported or dropped in by hand. Off for pickers with no such notion.
    readonly property string mineId: "__mine__"
    property bool showMine: false
    property string mineLabel: qsTr("My Effects")

    property var categories: []
    property string activeCategory: ""
    property bool searching: false
    property bool expanded: true
    // Off where there is no favourites notion (the emoji groups).
    property bool showFavorites: true
    property real sidePadding: Theme.pagePadding

    signal categoryActivated(string categoryId)

    readonly property real rowHeight: Theme.controlHeightSm
    // Only offer the fold when there is a second row to fold away.
    readonly property bool wraps: chips.implicitHeight > rowHeight + 1

    width: parent ? parent.width : 0
    height: visible ? (expanded || !wraps ? chips.implicitHeight : rowHeight) : 0
    visible: !searching && (categories.length > 0 || showMine)
    clip: true

    Behavior on height {
        NumberAnimation { duration: Theme.durationSlow; easing.type: Easing.OutCubic }
    }

    Flow {
        id: chips
        x: root.sidePadding
        // The fold button's slot is always reserved: sizing around it only when it shows would
        // feed the wrap test back into the width it measures.
        width: root.width - root.sidePadding * 2 - root.rowHeight - Theme.spacingSm
        spacing: Theme.spacingSm

        IconButton {
            id: favButton
            visible: root.showFavorites
            glyph: Theme.icons.star
            variant: "ghost"
            buttonSize: root.rowHeight
            iconSize: 14
            active: root.activeCategory === root.favoritesId
            tooltip: qsTr("Favorites")
            onClicked: root.categoryActivated(root.favoritesId)
        }

        ThemedChip {
            id: mineButton
            visible: root.showMine
            text: root.mineLabel
            variant: "outline"
            selected: root.activeCategory === root.mineId
            onClicked: root.categoryActivated(root.mineId)
        }

        Item {
            visible: root.showFavorites || root.showMine
            width: Theme.borderWidth
            height: root.rowHeight

            Rectangle {
                anchors.centerIn: parent
                width: parent.width
                height: root.rowHeight - 6
                color: Theme.panelBorder
            }
        }

        Repeater {
            model: root.categories
            delegate: ThemedChip {
                required property var modelData
                required property int index
                text: modelData.label
                variant: "secondary"
                accentColor: Theme.categoryColor(index)
                selected: root.activeCategory === modelData.id
                onClicked: root.categoryActivated(modelData.id)
            }
        }
    }

    IconButton {
        id: foldButton
        anchors.right: parent.right
        anchors.rightMargin: root.sidePadding
        y: 0
        visible: root.wraps
        width: root.rowHeight
        glyph: root.expanded ? Theme.icons.chevronUp : Theme.icons.chevronDown
        variant: "ghost"
        buttonSize: root.rowHeight
        iconSize: 14
        tooltip: root.expanded ? qsTr("Show fewer categories") : qsTr("Show all categories")
        onClicked: root.expanded = !root.expanded
    }
}
