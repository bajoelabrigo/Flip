import QtQuick
import QtQuick.Controls.Basic
import Drift

// Name prompt shared by every "save this as a preset" and "rename a preset" flow — text styles
// and effect stacks alike. All of them are a single short field, so they are one dialog rather
// than a family of near-identical ones.
ThemedDialog {
    id: root

    // Emitted with the trimmed name; never fires empty.
    signal submitted(string name)

    property alias placeholder: nameField.placeholderText

    acceptText: qsTr("Save")
    preferredWidth: Theme.dialogWidthSm

    function openWith(dialogTitle, initialName) {
        root.title = dialogTitle
        nameField.text = initialName
        open()
    }

    // The field takes the keyboard once the dialog is up (ThemedDialog's own onOpened gives it to the accept button first), with
    // the name selected so typing replaces it.
    onOpened: Qt.callLater(() => {
        nameField.forceActiveFocus()
        nameField.selectAll()
    })

    onAccepted: {
        const name = nameField.text.trim()
        if (name.length > 0)
            root.submitted(name)
    }

    contentItem: Column {
        spacing: Theme.spacingLg
        width: parent ? parent.width : 320

        ThemedLabel {
            text: qsTr("Name")
        }

        ThemedTextField {
            id: nameField
            width: parent.width
            placeholderText: qsTr("My style")
        }
    }
}
