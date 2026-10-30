import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift

// Window › Workspace (0.26), as After Effects: the workspaces (Auto follows the canvas), Arrange
// panels (drag a panel onto another to swap them or onto an edge to dock it), the panels to show or
// hide, and saving, resetting or deleting a workspace. `win` is the editor window (Main.qml).
ThemedContextMenu {
    id: menu
    property var win: null
    readonly property var spaces: win && win.workspaceLayout !== undefined ? win.workspacesModel : []
    readonly property string current: win ? win.workspaceLayout : ""

    title: qsTr("Workspace")

    ThemedMenuItem {
        text: qsTr("Auto (follow canvas)")
        icon.name: EditorState.preferences.workspaceLayoutOverridden ? "" : Theme.icons.check
        onTriggered: EditorState.preferences.clearWorkspaceLayoutPreference()
    }
    ThemedMenuSeparator {}

    Instantiator {
        model: menu.spaces
        delegate: ThemedMenuItem {
            required property var modelData
            text: modelData.label + (menu && menu.win && menu.win.workspaceEdited(modelData.id) ? "  •" : "")
            icon.name: EditorState.preferences.workspaceLayoutOverridden && !!menu && menu.current === modelData.id
                       ? Theme.icons.check : ""
            onTriggered: menu.win.chooseWorkspace(modelData.id)
        }
        onObjectAdded: (index, object) => menu.insertItem(2 + index, object)
        onObjectRemoved: (index, object) => menu.removeItem(object)
    }

    ThemedMenuSeparator {}
    ThemedMenuItem {
        text: menu.win && menu.win.arrangingPanels ? qsTr("Done arranging") : qsTr("Arrange panels")
        icon.name: Theme.icons.grid
        onTriggered: menu.win.arrangingPanels = !menu.win.arrangingPanels
    }
    ThemedMenuItem {
        text: qsTr("Library")
        icon.name: menu.win && menu.win.panelShown("assets") ? Theme.icons.check : ""
        onTriggered: menu.win.togglePanel("assets")
    }
    ThemedMenuItem {
        text: qsTr("Preview")
        icon.name: menu.win && menu.win.panelShown("preview") ? Theme.icons.check : ""
        onTriggered: menu.win.togglePanel("preview")
    }
    ThemedMenuItem {
        text: qsTr("Properties")
        icon.name: menu.win && menu.win.panelShown("properties") ? Theme.icons.check : ""
        onTriggered: menu.win.togglePanel("properties")
    }
    ThemedMenuItem {
        text: qsTr("Timeline")
        icon.name: menu.win && menu.win.panelShown("timeline") ? Theme.icons.check : ""
        onTriggered: menu.win.togglePanel("timeline")
    }
    ThemedMenuSeparator {}
    ThemedMenuItem {
        text: qsTr("Save as new workspace…")
        onTriggered: menu.win.askWorkspaceName()
    }
    ThemedMenuItem {
        text: qsTr("Reset «%1»").arg(menu.win ? menu.win.workspaceLabel(menu.current) : "")
        enabled: !!menu.win && menu.win.workspaceEdited(menu.current)
        onTriggered: menu.win.resetWorkspace(menu.current)
    }
    ThemedMenuItem {
        text: qsTr("Delete «%1»").arg(menu.win ? menu.win.workspaceLabel(menu.current) : "")
        visible: menu.current.indexOf("user:") === 0
        height: visible ? implicitHeight : 0
        onTriggered: menu.win.deleteWorkspace(menu.current)
    }
}
