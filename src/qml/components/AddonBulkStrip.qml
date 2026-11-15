import QtQuick
import QtQuick.Controls.Basic
import Drift

// «Install all» progress (0.32): a small card at the bottom left of the window, so editing goes on
// while the extras install. A click opens Extras for the details; Cancel stops the queue.
Rectangle {
    id: root

    readonly property var bulk: Addons.bulk
    signal openRequested()

    visible: bulk.active === true
    width: Math.min(420, parent ? parent.width - Theme.spacing3xl * 2 : 420)
    height: body.implicitHeight + Theme.spacingLg * 2
    radius: Theme.radiusMd
    color: Theme.panelBackground
    border.width: Theme.borderWidth
    border.color: Theme.panelBorder

    function formatSize(bytes) {
        if (bytes >= 1e9)
            return (bytes / 1e9).toFixed(1) + " GB"
        return Math.round(bytes / 1e6) + " MB"
    }

    // Under the Cancel button (declared first), so a click on it never also opens Extras.
    MouseArea {
        id: hover
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.openRequested()
    }

    ThemedToolTip {
        visible: hover.containsMouse
        text: qsTr("Click to see the extras")
    }

    Column {
        id: body
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.leftMargin: Theme.spacingLg
        anchors.rightMargin: Theme.spacingLg
        spacing: Theme.spacingSm

        Item {
            width: parent.width
            height: Math.max(title.implicitHeight, cancelButton.height)

            ThemedLabel {
                id: title
                anchors.left: parent.left
                anchors.right: cancelButton.left
                anchors.rightMargin: Theme.spacingMd
                anchors.verticalCenter: parent.verticalCenter
                size: "sm"
                tone: "default"
                font.weight: Font.Medium
                elide: Text.ElideRight
                text: qsTr("Installing extras: %1 of %2")
                          .arg(Math.min((root.bulk.done || 0) + 1, root.bulk.total || 0)).arg(root.bulk.total || 0)
            }

            ThemedButton {
                id: cancelButton
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                variant: "ghost"
                text: qsTr("Cancel")
                tooltip: qsTr("Stop installing the extras that are left")
                onClicked: Addons.cancelInstallAll()
            }
        }

        ThemedLabel {
            width: parent.width
            size: "sm"
            elide: Text.ElideRight
            text: {
                const sizes = qsTr("%1 of %2").arg(root.formatSize(root.bulk.bytesDone || 0))
                                              .arg(root.formatSize(root.bulk.bytesTotal || 0))
                return (root.bulk.current || "").length > 0 ? root.bulk.current + " · " + sizes : sizes
            }
        }

        ThemedProgressBar {
            width: parent.width
            barHeight: 4
            value: (root.bulk.bytesTotal || 0) > 0 ? root.bulk.bytesDone / root.bulk.bytesTotal : 0
        }
    }
}
