import QtQuick
import Drift

// In / Out / Loop (or Combo) of an animation gallery as underlined tabs, so they read as a level
// below the segmented page tabs above them (Filmora's Titles › Animation). `marked` puts a dot on
// a slot that has an animation set.
Item {
    id: root

    property var model: [] // [{ id, label }]
    property string current: ""
    property var marked: function(id) { return false }

    signal activated(string id)

    implicitHeight: Theme.controlHeightSm + 6
    width: parent ? parent.width : 0

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 1
        color: Theme.panelBorder
    }

    Row {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        spacing: Theme.spacingLg * 1.5

        Repeater {
            model: root.model
            delegate: Item {
                id: tab
                required property var modelData
                readonly property bool on: root.current === modelData.id
                width: tabRow.implicitWidth + 4
                height: parent.height

                Row {
                    id: tabRow
                    anchors.centerIn: parent
                    anchors.verticalCenterOffset: -2
                    spacing: 5

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: tab.modelData.label
                        color: tab.on || tabHover.hovered ? Theme.panelForeground : Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSm + 1
                        font.weight: Font.DemiBold
                    }

                    Rectangle {
                        visible: root.marked(tab.modelData.id)
                        anchors.verticalCenter: parent.verticalCenter
                        width: 5
                        height: 5
                        radius: 2.5
                        color: Theme.primary
                    }
                }

                Rectangle {
                    visible: tab.on
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    height: 2
                    radius: 1
                    color: Theme.primary
                }

                HoverHandler { id: tabHover; enabled: !Theme.touchUi }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.activated(tab.modelData.id)
                }
            }
        }
    }
}
