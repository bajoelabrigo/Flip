import QtQuick
import QtQuick.Controls.Basic
import Drift

// Lower-third maker (0.29, Jorge): a style, the name and the role, three colours, and the editor puts the layers
// on the timeline at the playhead, animated and every one editable: the label fits the name and grows with it,
// the words show only inside their labels, everything comes in in a cascade.
ThemedDialog {
    id: root

    title: qsTr("Lower third")
    acceptText: qsTr("Add")
    preferredWidth: Theme.dialogWidthSm

    property string style: "line"
    property string labelColor: "#ffffffff"
    property string accentColor: "#fff5c518"
    property string textColor: "#ff1a1a1a"
    readonly property var styles: [
        { "id": "clean", "label": qsTr("Clean") },
        { "id": "line", "label": qsTr("With a line") },
        { "id": "slanted", "label": qsTr("Slanted") },
        { "id": "twoColour", "label": qsTr("Two colours") },
        { "id": "roleBar", "label": qsTr("Role on a bar") }
    ]

    function openFresh() {
        open()
        nameField.forceActiveFocus()
        nameField.selectAll()
    }

    onAccepted: EditorState.createLowerThird({
        "style": root.style,
        "name": nameField.text,
        "role": roleField.text,
        "labelColor": root.labelColor,
        "accentColor": root.accentColor,
        "textColor": root.textColor,
        "seconds": secondsField.value
    })

    contentItem: Column {
        spacing: Theme.spacingLg
        width: parent ? parent.width : 320

        ThemedLabel { text: qsTr("Style") }
        Flow {
            width: parent.width
            spacing: Theme.spacingSm
            Repeater {
                model: root.styles
                ThemedChip {
                    required property var modelData
                    text: modelData.label
                    selected: root.style === modelData.id
                    onClicked: root.style = modelData.id
                }
            }
        }

        ThemedLabel { text: qsTr("Name") }
        ThemedTextField {
            id: nameField
            width: parent.width
            text: qsTr("Your name")
        }
        ThemedLabel { text: qsTr("Role (optional)") }
        ThemedTextField {
            id: roleField
            width: parent.width
            placeholderText: qsTr("Presenter, guest, city…")
        }

        Row {
            width: parent.width
            spacing: Theme.spacingLg
            Column {
                spacing: Theme.spacingXs
                ThemedLabel { text: qsTr("Label") }
                ColorSwatchField { showHex: false; hex: root.labelColor; onEdited: value => root.labelColor = value }
            }
            Column {
                spacing: Theme.spacingXs
                ThemedLabel { text: qsTr("Accent") }
                ColorSwatchField { showHex: false; hex: root.accentColor; onEdited: value => root.accentColor = value }
            }
            Column {
                spacing: Theme.spacingXs
                ThemedLabel { text: qsTr("Text") }
                ColorSwatchField { showHex: false; hex: root.textColor; onEdited: value => root.textColor = value }
            }
            Column {
                spacing: Theme.spacingXs
                ThemedLabel { text: qsTr("On screen") }
                ThemedNumberField {
                    id: secondsField
                    width: 80
                    from: 1
                    to: 60
                    decimals: 1
                    unit: "s"
                    value: 5
                }
            }
        }
    }
}
