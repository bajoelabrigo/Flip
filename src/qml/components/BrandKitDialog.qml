import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift

// My brand: a logo, two to four colours and a font, kept on this computer. Business templates
// (and any with a logo slot) take them when they go in; any template can from its Template panel.
ThemedDialog {
    id: root

    property string logo: ""
    property var colors: []
    property string fontFamily: ""
    property bool autoApply: true
    readonly property var roleLabels: [qsTr("Main colour"), qsTr("Second colour"), qsTr("Accent"), qsTr("Text colour")]

    title: qsTr("My brand")
    acceptText: qsTr("Save")
    preferredWidth: Theme.dialogWidthMd

    function openKit() {
        const kit = EditorState.brandKit()
        logo = kit.logo || ""
        colors = (kit.colors || []).slice()
        fontFamily = kit.font || ""
        autoApply = kit.autoApply !== false
        open()
    }

    function setColor(index, value) {
        const next = colors.slice()
        next[index] = value
        colors = next
    }

    function removeColor(index) {
        const next = colors.slice()
        next.splice(index, 1)
        colors = next
    }

    contentItem: Flickable {
        implicitHeight: Math.min(body.implicitHeight, root.availableContentHeight)
        contentHeight: body.implicitHeight
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: AppScrollBar { }

        Column {
            id: body
            width: parent.width
            spacing: Theme.spacingMd

            ThemedLabel {
                width: parent.width
                size: "sm"
                text: qsTr("Your logo, colours and font. Business templates use them when you add one; any other template takes them with “Apply my brand” in its Template panel.")
            }

            ThemedLabel { text: qsTr("Logo") }
            Row {
                spacing: Theme.spacingMd
                Rectangle {
                    width: 72
                    height: 72
                    radius: Theme.radiusSm
                    color: Theme.panelAccent
                    border.width: 1
                    border.color: Theme.panelBorder
                    Image {
                        anchors.fill: parent
                        anchors.margins: 6
                        visible: root.logo.length > 0
                        source: root.logo
                        fillMode: Image.PreserveAspectFit
                        asynchronous: true
                        sourceSize: Qt.size(Math.ceil(width * Screen.devicePixelRatio), Math.ceil(height * Screen.devicePixelRatio))
                    }
                    IconGlyph {
                        anchors.centerIn: parent
                        visible: root.logo.length === 0
                        glyph: Theme.icons.image
                        iconSize: 22
                        iconColor: Theme.mutedForeground
                    }
                }
                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: Theme.spacingSm
                    ThemedButton {
                        text: root.logo.length > 0 ? qsTr("Change logo…") : qsTr("Choose logo…")
                        glyph: Theme.icons.image
                        onClicked: {
                            const url = FileDialogs.openFile(qsTr("Choose your logo"),
                                                             [qsTr("Pictures (*.png *.jpg *.jpeg *.webp)")])
                            if (url.toString().length > 0)
                                root.logo = url.toString()
                        }
                    }
                    ThemedButton {
                        visible: root.logo.length > 0
                        variant: "ghost"
                        text: qsTr("Remove logo")
                        onClicked: root.logo = ""
                    }
                }
            }

            ThemedLabel { text: qsTr("Colours (2 to 4)") }
            Repeater {
                model: root.colors.length
                delegate: Row {
                    id: colorRow
                    required property int index
                    spacing: Theme.spacingSm
                    ColorSwatchField {
                        anchors.verticalCenter: parent.verticalCenter
                        hex: root.colors[colorRow.index] || "#ffffffff"
                        tooltip: root.roleLabels[colorRow.index]
                        onEdited: v => root.setColor(colorRow.index, v)
                    }
                    ThemedLabel {
                        anchors.verticalCenter: parent.verticalCenter
                        text: root.roleLabels[colorRow.index]
                    }
                    IconButton {
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: Theme.icons.trash
                        tooltip: qsTr("Remove colour")
                        onClicked: root.removeColor(colorRow.index)
                    }
                }
            }
            ThemedButton {
                visible: root.colors.length < 4
                variant: "ghost"
                glyph: Theme.icons.plus
                text: qsTr("Add colour")
                onClicked: {
                    const defaults = ["#ff1f6feb", "#ffffc528", "#ffff4d6d", "#ffffffff"]
                    const next = root.colors.slice()
                    next.push(defaults[next.length] || "#ffffffff")
                    root.colors = next
                }
            }

            ThemedLabel { text: qsTr("Font") }
            FontPicker {
                width: parent.width
                family: root.fontFamily
                onFamilyPicked: (family) => root.fontFamily = family
            }

            ThemedCheckBox {
                width: parent.width
                text: qsTr("Use it in Business templates when I add them")
                checked: root.autoApply
                onToggled: root.autoApply = checked
            }
        }
    }

    onAccepted: EditorState.setBrandKit({ logo: root.logo, colors: root.colors, font: root.fontFamily,
                                          autoApply: root.autoApply })
}
