import QtQuick
import QtQuick.Controls.Basic
import Drift

// Host for SettingsPane. Opened from Edit › Preferences… and the header's Settings menu on the
// desktop, and from the phone's overflow menu. On the desktop it is After Effects' Preferences
// (0.26): the pages on the left, the page on the right; the phone keeps the one long list.
ThemedDialog {
    id: root

    readonly property bool mobile: Qt.platform.os === "android" || Qt.platform.os === "ios"
    property string page: "general"
    readonly property var pages: [
        { id: "general", label: qsTr("General") },
        { id: "appearance", label: qsTr("Appearance and language") },
        { id: "newproject", label: qsTr("New layers") },
        { id: "timeline", label: qsTr("Timeline and keyframes") },
        { id: "tools", label: qsTr("Preview tools") },
        { id: "preview", label: qsTr("Preview and performance") },
        { id: "audio", label: qsTr("Audio") },
        { id: "saving", label: qsTr("Saving and undo") },
        { id: "shortcuts", label: qsTr("Keyboard shortcuts") },
        { id: "account", label: qsTr("Account and privacy") },
        { id: "cloud", label: qsTr("AI in the cloud") }
    ]

    title: root.mobile ? qsTr("Settings") : qsTr("Preferences")
    preferredWidth: root.mobile ? Theme.dialogWidthLg : Theme.dialogWidthLg + 200
    acceptText: qsTr("Done")
    showReject: false

    contentItem: Item {
        implicitWidth: root.preferredWidth
        implicitHeight: root.mobile ? Math.min(pane.contentHeight, root.availableContentHeight)
                                    : Math.min(560, root.availableContentHeight)

        Column {
            id: nav
            visible: !root.mobile
            width: visible ? 190 : 0
            height: parent.height
            spacing: 2
            Repeater {
                model: root.pages
                delegate: Rectangle {
                    required property var modelData
                    width: nav.width
                    height: 30
                    radius: Theme.radiusSm
                    color: root.page === modelData.id ? Theme.panelAccent
                                                      : (navHover.hovered ? Theme.panelMuted : "transparent")
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        x: Theme.spacingMd
                        width: parent.width - 2 * Theme.spacingMd
                        elide: Text.ElideRight
                        text: modelData.label
                        color: root.page === modelData.id ? Theme.primary : Theme.panelForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSm
                        font.weight: root.page === modelData.id ? Font.DemiBold : Font.Normal
                    }
                    HoverHandler { id: navHover }
                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.page = modelData.id
                    }
                }
            }
        }

        Rectangle {
            visible: !root.mobile
            x: nav.width + Theme.spacingMd
            width: 1
            height: parent.height
            color: Theme.panelBorder
        }

        SettingsPane {
            id: pane
            x: root.mobile ? 0 : nav.width + 2 * Theme.spacingMd
            width: parent.width - x
            height: parent.height
            page: root.mobile ? "" : root.page
        }
    }
}
