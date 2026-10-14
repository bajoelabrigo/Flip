import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// The marketplace opt-in. Shown by the Market tab and by the shared-link sheet, which are the
// two ways into a store download — one component so the wording cannot drift apart between them.
//
// The tick is deliberate friction. Nothing here is a normal in-app download: the daily cap, the
// third-party sources and the failure modes are all things a user has to have been told about
// before the first attempt, not after it fails.
Item {
    id: root

    property real sideMargin: Theme.pagePadding
    signal accepted()

    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: column.implicitHeight + Theme.spacing3xl * 2
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: AppScrollBar { }

        Column {
            id: column
            x: root.sideMargin
            y: Theme.spacing3xl
            width: Math.min(parent.width - root.sideMargin * 2, 420)
            spacing: Theme.spacingXl

            Rectangle {
                width: 48
                height: 48
                radius: Theme.radiusMd
                color: Theme.panelAccent

                IconGlyph {
                    anchors.centerIn: parent
                    glyph: Theme.icons.store
                    iconSize: Theme.iconSizeXl
                    iconColor: Theme.primary
                }
            }

            ThemedLabel {
                width: parent.width
                tone: "default"
                size: "base"
                text: qsTr("Free photos and videos")
            }

            ThemedLabel {
                width: parent.width
                text: qsTr("Search free photos and videos from Pexels and Pixabay and download them straight into your project. Before you start:")
            }

            Column {
                width: parent.width
                spacing: Theme.spacingLg

                Repeater {
                    model: [
                        qsTr("Everything comes from Pexels and Pixabay, under their own licenses: you can use it in your videos for free, including commercial ones, and crediting the author is appreciated but not required."),
                        qsTr("Do not resell the photos or videos as they are, or offer them as your own stock collection. People and brands that appear in them may need their own permission."),
                        qsTr("Flip Studio does not own or review this material: check that each item suits your use. Searches go through Flip Studio's server; the files download straight from Pexels and Pixabay.")
                    ]

                    delegate: Row {
                        required property string modelData
                        width: column.width
                        spacing: Theme.spacingLg

                        Rectangle {
                            width: Theme.spacingMd
                            height: width
                            radius: width / 2
                            y: Theme.spacingLg
                            color: Theme.mutedForeground
                        }

                        ThemedLabel {
                            width: parent.width - Theme.spacingMd - Theme.spacingLg
                            text: parent.modelData
                        }
                    }
                }
            }

            Item { width: 1; height: Theme.spacingSm }

            ThemedCheckBox {
                id: understood
                text: qsTr("I understand")
            }

            ThemedButton {
                variant: "primary"
                text: qsTr("Continue")
                enabled: understood.checked
                onClicked: {
                    Market.acceptTerms()
                    root.accepted()
                }
            }
        }
    }
}
