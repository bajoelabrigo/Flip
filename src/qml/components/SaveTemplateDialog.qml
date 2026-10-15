import QtQuick
import QtQuick.Controls.Basic
import Drift

// Save as template: a composition becomes a scene template of one's own, in Templates › Scenes.
// Its photos and videos marked as slots go out empty; everything else is copied in.
ThemedDialog {
    id: root

    property string assetId: ""
    property var summary: ({})
    readonly property var categories: [
        { id: "mine", label: qsTr("My templates") },
        { id: "reels", label: qsTr("Photo reels") },
        { id: "intro", label: qsTr("Intros and titles") },
        { id: "text", label: qsTr("Text") },
        { id: "collage", label: qsTr("Collages") },
        { id: "beforeafter", label: qsTr("Before and after") },
        { id: "product", label: qsTr("Products") },
        { id: "celebration", label: qsTr("Celebrations") },
        { id: "countdown", label: qsTr("Countdowns") },
        { id: "outro", label: qsTr("Endings") }
    ]

    title: qsTr("Save as template")
    acceptText: qsTr("Save")
    preferredWidth: Theme.dialogWidthSm

    function openFor(compositeAssetId, name) {
        assetId = compositeAssetId
        summary = EditorState.compositeTemplateSummary(compositeAssetId)
        nameField.text = name || summary.name || ""
        categoryCombo.currentIndex = 0
        open()
    }

    contentItem: Column {
        width: parent ? parent.width : Theme.dialogWidthSm
        spacing: Theme.spacingMd

        ThemedLabel {
            text: qsTr("Name")
        }
        ThemedTextField {
            id: nameField
            width: parent.width
            placeholderText: qsTr("My template")
        }
        ThemedLabel {
            text: qsTr("Category")
        }
        ThemedComboBox {
            id: categoryCombo
            width: parent.width
            textRole: "label"
            valueRole: "id"
            model: root.categories
        }
        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            size: "sm"
            text: (root.summary.slots || 0) > 0
                  ? qsTr("%n slot(s) for photos and videos, and %1 editable text(s). The rest of the composition is saved as it is.",
                         "", root.summary.slots || 0).arg(root.summary.texts || 0)
                  : qsTr("It has no slots yet. To leave room for other people's photos, open the composition and right-click a photo or video › Make template slot.")
        }
    }

    onOpened: {
        nameField.forceActiveFocus()
        nameField.selectAll()
    }
    onAccepted: EditorState.saveCompositeAsTemplate(root.assetId, nameField.text, categoryCombo.currentValue)
}
