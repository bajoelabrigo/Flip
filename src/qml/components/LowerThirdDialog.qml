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
    property bool useAccent2: false
    property bool useAccent3: false
    property string accent2Color: "#ff2a9df4"
    property string accent3Color: "#ffe63946"
    property string textAlign: "left"
    readonly property var aligns: [
        { "id": "left", "label": qsTr("Left") },
        { "id": "center", "label": qsTr("Centre") },
        { "id": "right", "label": qsTr("Right") }
    ]
    property string motionIn: "auto"
    property string motionOut: "auto"
    // How it comes in and goes out (Jorge, 0.29): Automatic is each style's own motion.
    readonly property var motions: [
        { "id": "auto", "label": qsTr("Automatic") },
        { "id": "wipe", "label": qsTr("Wipe") },
        { "id": "slide", "label": qsTr("Slide") },
        { "id": "pop", "label": qsTr("Pop") },
        { "id": "zoom", "label": qsTr("Zoom") },
        { "id": "fade", "label": qsTr("Fade") },
        { "id": "none", "label": qsTr("None") }
    ]
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
        "accent2Color": root.useAccent2 ? root.accent2Color : "",
        "accent3Color": root.useAccent2 && root.useAccent3 ? root.accent3Color : "",
        "align": root.textAlign,
        "entrance": root.motionIn,
        "exit": root.motionOut,
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

        // Two more accents, optional: the label comes in after them in a colour wipe.
        Row {
            width: parent.width
            spacing: Theme.spacingSm
            ThemedSwitch {
                anchors.verticalCenter: parent.verticalCenter
                text: qsTr("Second accent")
                checked: root.useAccent2
                onToggled: {
                    root.useAccent2 = checked
                    if (!checked)
                        root.useAccent3 = false
                }
            }
            ColorSwatchField {
                anchors.verticalCenter: parent.verticalCenter
                visible: root.useAccent2
                showHex: false
                hex: root.accent2Color
                onEdited: value => root.accent2Color = value
            }
            ThemedSwitch {
                anchors.verticalCenter: parent.verticalCenter
                visible: root.useAccent2
                text: qsTr("Third accent")
                checked: root.useAccent3
                onToggled: root.useAccent3 = checked
            }
            ColorSwatchField {
                anchors.verticalCenter: parent.verticalCenter
                visible: root.useAccent2 && root.useAccent3
                showHex: false
                hex: root.accent3Color
                onEdited: value => root.accent3Color = value
            }
        }

        ThemedLabel { text: qsTr("Entrance") }
        Flow {
            width: parent.width
            spacing: Theme.spacingSm
            Repeater {
                model: root.motions
                ThemedChip {
                    required property var modelData
                    text: modelData.label
                    selected: root.motionIn === modelData.id
                    onClicked: root.motionIn = modelData.id
                }
            }
        }
        ThemedLabel { text: qsTr("Exit") }
        Flow {
            width: parent.width
            spacing: Theme.spacingSm
            Repeater {
                model: root.motions
                ThemedChip {
                    required property var modelData
                    text: modelData.label
                    selected: root.motionOut === modelData.id
                    onClicked: root.motionOut = modelData.id
                }
            }
        }

        ThemedLabel { text: qsTr("Alignment") }
        Flow {
            width: parent.width
            spacing: Theme.spacingSm
            Repeater {
                model: root.aligns
                ThemedChip {
                    required property var modelData
                    text: modelData.label
                    selected: root.textAlign === modelData.id
                    onClicked: root.textAlign = modelData.id
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
