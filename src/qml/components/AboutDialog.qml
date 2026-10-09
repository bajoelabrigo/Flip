import QtQuick
import QtQuick.Controls.Basic
import Drift

ThemedDialog {
    id: root

    title: qsTr("About Flip Studio")
    preferredWidth: 420
    showFooter: true
    showReject: false
    acceptText: qsTr("Close")

    contentItem: Column {
        spacing: Theme.spacingXl
        width: parent ? parent.width : 420

        Row {
            spacing: Theme.spacingXl
            anchors.horizontalCenter: parent.horizontalCenter

            Image {
                source: "qrc:/app/drift.png"
                width: 64
                height: 64
                fillMode: Image.PreserveAspectFit
                mipmap: true
            }

            Column {
                spacing: Theme.spacingXs
                anchors.verticalCenter: parent.verticalCenter

                ThemedLabel {
                    text: qsTr("Flip Studio")
                    size: "xl"
                    font.weight: Font.DemiBold
                }

                ThemedLabel {
                    text: qsTr("Version %1").arg(Updates.currentVersion)
                    tone: "muted"
                    size: "sm"
                }
            }
        }

        ThemedLabel {
            width: parent.width
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            size: "sm"
            text: qsTr("Open-source video editor based on Drift by CutWire Studios.")
        }

        ThemedLabel {
            width: parent.width
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            size: "xs"
            tone: "muted"
            textFormat: Text.StyledText
            // GPLv3 (and the AGPLv3 JUCE it links) require the source to be offered to users.
            text: qsTr("Licensed under GPLv3. Copyright © CutWire Studios and Flip Studio contributors.")
                  + "<br><a href=\"https://github.com/bajoelabrigo/Flip\">" + qsTr("Source code") + "</a>"
            onLinkActivated: link => Qt.openUrlExternally(link)
        }
    }
}
