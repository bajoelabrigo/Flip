import QtQuick
import QtQuick.Controls.Basic
import Drift

// After Effects' Solid Settings (0.25): name, size and colour of a new solid. «Project size»
// puts the frame's own width and height back.
ThemedDialog {
    id: root

    title: qsTr("Solid settings")
    acceptText: qsTr("Add")
    preferredWidth: Theme.dialogWidthSm

    property string colorHex: "#ff28282e"

    function openFresh() {
        nameField.text = qsTr("Solid")
        widthField.value = EditorState.projectFile.projectWidth()
        heightField.value = EditorState.projectFile.projectHeight()
        widthField.text = widthField.format(widthField.value)
        heightField.text = heightField.format(heightField.value)
        open()
        nameField.forceActiveFocus()
        nameField.selectAll()
    }

    onAccepted: EditorState.addSolidClip(root.colorHex, nameField.text.trim(),
                                         widthField.value, heightField.value)

    contentItem: Column {
        spacing: Theme.spacingLg
        width: parent ? parent.width : 320

        ThemedLabel { text: qsTr("Name") }
        ThemedTextField {
            id: nameField
            width: parent.width
        }

        Row {
            width: parent.width
            spacing: Theme.spacingLg
            Column {
                width: (parent.width - parent.spacing) / 2
                spacing: Theme.spacingXs
                ThemedLabel { text: qsTr("Width") }
                ThemedNumberField {
                    id: widthField
                    width: parent.width
                    from: 1
                    to: 16384
                    unit: "px"
                }
            }
            Column {
                width: (parent.width - parent.spacing) / 2
                spacing: Theme.spacingXs
                ThemedLabel { text: qsTr("Height") }
                ThemedNumberField {
                    id: heightField
                    width: parent.width
                    from: 1
                    to: 16384
                    unit: "px"
                }
            }
        }

        ThemedButton {
            text: qsTr("Project size")
            onClicked: {
                widthField.value = EditorState.projectFile.projectWidth()
                heightField.value = EditorState.projectFile.projectHeight()
                widthField.text = widthField.format(widthField.value)
                heightField.text = heightField.format(heightField.value)
            }
        }

        ThemedLabel { text: qsTr("Colour") }
        ColorSwatchField {
            width: parent.width
            hex: root.colorHex
            onEdited: (value) => root.colorHex = value
        }
    }
}
