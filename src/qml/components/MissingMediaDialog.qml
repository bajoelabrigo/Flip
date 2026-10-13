import QtQuick
import QtQuick.Controls.Basic
import Drift

// "Some files are missing", as Premiere and After Effects ask on opening a project whose media
// was deleted, renamed or moved. Each file can be found by hand, or a folder can be searched for
// all of them at once; finding one also relinks the others sitting next to it. The project is
// already open: what stays missing shows as "Missing file" in the media bin, where right-click
// offers the same search later.
ThemedDialog {
    id: root

    property var files: []

    title: qsTr("Some files are missing")
    acceptText: qsTr("Search a folder…")
    rejectText: qsTr("Later")
    preferredWidth: Theme.dialogWidthMd

    function refresh() {
        files = EditorState.bin.missingMedia()
        if (files.length === 0)
            close()
    }

    function openFor(list) {
        files = list
        open()
    }

    // Accept: one folder search for all of them. The dialog stays while some are still missing.
    onAccepted: {
        const url = FileDialogs.openDirectory(qsTr("Folder where the files are now"))
        if (!url || url.toString() === "")
            return
        const found = EditorState.bin.relinkMissingInFolder(url)
        if (found > 0)
            Toasts.success(qsTr("%n files found", "", found))
        else
            Toasts.error(qsTr("None of the missing files are in that folder."))
        Qt.callLater(() => {
            root.refresh()
            if (root.files.length > 0)
                root.open()
        })
    }

    contentItem: Column {
        spacing: Theme.spacingLg
        width: parent ? parent.width : 400

        ThemedLabel {
            width: parent.width
            size: "sm"
            text: qsTr("%n files of this project are not where they were: they were deleted, renamed or moved. "
                       + "Find each one, or search a folder for all of them. When you find one, the others "
                       + "in the same folder are found too.", "", root.files.length)
        }

        ListView {
            width: parent.width
            height: Math.min(contentHeight, 280)
            clip: true
            spacing: Theme.spacingSm
            model: root.files
            boundsBehavior: Flickable.StopAtBounds

            delegate: Rectangle {
                id: row
                required property var modelData
                width: ListView.view.width
                height: rowBody.implicitHeight + Theme.spacingLg
                radius: Theme.radiusMd
                color: Theme.panelSecondaryBg
                border.width: Theme.borderWidth
                border.color: Theme.panelSecondaryBorder

                Column {
                    id: rowBody
                    anchors.left: parent.left
                    anchors.right: findButton.left
                    anchors.leftMargin: Theme.spacingLg
                    anchors.rightMargin: Theme.spacingLg
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 2

                    Text {
                        width: parent.width
                        elide: Text.ElideRight
                        text: row.modelData.fileName || row.modelData.name
                        color: Theme.foreground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSm
                        font.weight: Font.Medium
                    }
                    Text {
                        width: parent.width
                        elide: Text.ElideMiddle
                        text: row.modelData.path
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                }

                ThemedButton {
                    id: findButton
                    anchors.right: parent.right
                    anchors.rightMargin: Theme.spacingLg
                    anchors.verticalCenter: parent.verticalCenter
                    glyph: "search"
                    text: qsTr("Find…")
                    onClicked: {
                        const url = FileDialogs.openFile(qsTr("Where is %1 now?").arg(row.modelData.fileName),
                                                         [qsTr("%1 (%1)").arg(row.modelData.fileName),
                                                          AssetLibrary.mediaNameFilter(),
                                                          qsTr("All files (*)")])
                        if (!url || url.toString() === "")
                            return
                        const found = EditorState.bin.relinkMissing(row.modelData.id, url)
                        if (found > 1)
                            Toasts.success(qsTr("%n files found", "", found))
                        root.refresh()
                    }
                }
            }
        }
    }
}
