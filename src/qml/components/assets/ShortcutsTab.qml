import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// Shortcuts tab. Split out of Settings, which had grown long
// enough that the binding list was permanently below the fold.
Item {
    id: root
    // The panel's sidebar drives the category (0.23): its chips are not shown.
    property bool panelDriven: false

    property alias searchText: search.text
    readonly property string query: search.text.trim().toLowerCase()
    readonly property var visibleActions: {
        const actions = EditorState.actions || []
        const q = root.query
        if (q.length === 0)
            return actions
        return actions.filter(function(action) {
            const label = (action.label || "").toLowerCase()
            const id = (action.id || "").toLowerCase()
            const shortcut = (action.shortcut || "").toLowerCase()
            return label.indexOf(q) >= 0 || id.indexOf(q) >= 0 || shortcut.indexOf(q) >= 0
        })
    }

    ThemedTextField {
        id: search
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: Theme.pagePadding
        placeholderText: qsTr("Search shortcuts")
        font.family: Theme.fontFamily
    }

    ListView {
        id: shortcutList
        anchors.top: search.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.topMargin: Theme.spacingMd
        bottomMargin: Theme.spacing3xl
        spacing: Theme.spacingMd
        clip: true
        reuseItems: true
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: AppScrollBar { }
        model: root.visibleActions

        header: Column {
            x: Theme.pagePadding
            width: shortcutList.width - Theme.pagePadding * 2
            spacing: Theme.spacingMd
            topPadding: Theme.pagePadding
            bottomPadding: Theme.spacingMd

            // The set of defaults (0.30, Jorge): Flip's own, or After Effects' keys for the
            // keyframe lines and the layers (J/K, P/S/R/T/A, U/UU, B/N, I/O, [ ] and Alt+[ ]).
            // Shortcuts the user changed stay as they are.
            Row {
                spacing: Theme.spacingSm
                ThemedLabel {
                    anchors.verticalCenter: parent.verticalCenter
                    text: qsTr("Shortcut set")
                    size: "sm"
                }
                ThemedChip {
                    readonly property bool isSet: { void EditorState.actions; return EditorState.shortcutPreset() !== "afterEffects" }
                    text: qsTr("Flip")
                    selected: isSet
                    tooltip: qsTr("Flip's own shortcuts")
                    onClicked: EditorState.setShortcutPreset("flip")
                }
                ThemedChip {
                    readonly property bool isSet: { void EditorState.actions; return EditorState.shortcutPreset() === "afterEffects" }
                    text: qsTr("After Effects")
                    selected: isSet
                    tooltip: qsTr("As in After Effects: J/K go between keyframes, P/S/R/T/A show one property, U/UU, B/N the work area, I/O the layer's ends, [ ] and Alt+[ ] move and trim the layer at the playhead")
                    onClicked: EditorState.setShortcutPreset("afterEffects")
                }
            }

            Text {
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("Click a shortcut, then press the keys. Esc cancels, Backspace clears.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
                bottomPadding: Theme.spacingSm
            }

            EmptyState {
                visible: !EditorState.actions || EditorState.actions.length === 0
                width: parent.width
                compact: true
                glyph: Theme.icons.keyboard
                title: qsTr("No shortcuts available")
            }

            EmptyState {
                visible: EditorState.actions && EditorState.actions.length > 0
                         && root.visibleActions.length === 0
                width: parent.width
                compact: true
                glyph: Theme.icons.search
                title: qsTr("No shortcuts match “%1”").arg(search.text.trim())
                hint: qsTr("Try a different name or key.")
            }
        }

        delegate: Row {
            required property var modelData
            x: Theme.pagePadding
            width: shortcutList.width - Theme.pagePadding * 2
            spacing: Theme.spacingLg

            ListView.onPooled: captureField.capturing = false

            Text {
                width: Math.max(90, parent.width - 128)
                text: modelData.label
                color: Theme.panelForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
                wrapMode: Text.WordWrap
                anchors.verticalCenter: parent.verticalCenter
            }
            ShortcutCaptureField {
                id: captureField
                width: 120
                actionId: modelData.id
                shortcut: modelData.shortcut
            }
        }

        // Clearing a binding persists the empty string, so without this there was
        // no way back from having cleared one.
        footer: Item {
            width: shortcutList.width
            height: resetButton.height + Theme.spacingMd

            ThemedButton {
                id: resetButton
                x: Theme.pagePadding
                y: Theme.spacingMd
                text: qsTr("Reset to defaults")
                variant: "secondary"
                glyph: Theme.icons.undo
                topPadding: Theme.spacingMd + 1
                onClicked: {
                    EditorState.resetShortcuts()
                    Toasts.success(qsTr("Shortcuts reset to defaults."))
                }
            }
        }
    }
}
