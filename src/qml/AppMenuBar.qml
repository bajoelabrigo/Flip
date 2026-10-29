import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift
import "components"

// The menu bar in the editor header, as in Filmora and CapCut: File, Edit, Tools, View, Advanced
// and Help, each a themed drop-down with the shortcuts at the right. Every entry runs something the
// app already has (the same calls as the header buttons, the shortcuts and the clip menu); macOS
// has its native menu bar instead (Main.qml).
Row {
    id: root

    // The EditorHeader: save, export, project dialogs.
    required property var header
    readonly property var win: root.Window.window
    readonly property bool editing: !!win && !win.showStartScreen

    spacing: 0

    // The key of an action as the person set it, for the right edge of an entry.
    function keys(actionId) {
        return Theme.shortcutDisplay(EditorState.shortcutFor(actionId))
    }

    function dispatch(actionId) {
        root.win.dispatchAction(actionId)
    }

    readonly property var menus: [fileMenu, editMenu, toolsMenu, viewMenu, advancedMenu, helpMenu]
    readonly property bool anyOpen: menus.some(m => m.opened)

    component MenuButton: AbstractButton {
        id: menuButton
        required property var menu
        readonly property bool open: menu.opened
        height: Theme.iconButtonSize
        anchors.verticalCenter: parent ? parent.verticalCenter : undefined
        leftPadding: Theme.spacingLg
        rightPadding: Theme.spacingLg
        hoverEnabled: true
        focusPolicy: Qt.StrongFocus

        Accessible.role: Accessible.MenuItem

        function openMenu() {
            for (const m of root.menus) {
                if (m !== menuButton.menu && m.opened)
                    m.close()
            }
            menuButton.menu.popup(menuButton, 0, menuButton.height + Theme.spacingXs)
        }

        onClicked: open ? menu.close() : openMenu()
        // Moving along the bar with a menu open opens the next one, as in a desktop menu bar.
        onHoveredChanged: if (hovered && root.anyOpen && !open) openMenu()

        background: Rectangle {
            radius: Theme.radiusSm
            color: menuButton.open ? Theme.panelSecondaryBg
                                   : (menuButton.hovered ? Theme.popoverHover : "transparent")
            border.width: menuButton.visualFocus ? Theme.borderWidthFocus : 0
            border.color: Theme.focusRing
        }

        contentItem: Text {
            text: menuButton.text
            color: Theme.foreground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSm
            verticalAlignment: Text.AlignVCenter
        }

        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.NoButton
            cursorShape: Qt.PointingHandCursor
        }
    }

    // --- File ---------------------------------------------------------------------------------
    MenuButton {
        text: qsTr("File")
        menu: fileMenu

        ThemedContextMenu {
            id: fileMenu
            minimumWidth: 280

            ThemedMenuItem {
                text: qsTr("New Project")
                shortcutText: root.keys("newProject")
                onTriggered: root.header.requestNewProject()
            }
            ThemedMenuItem {
                text: qsTr("Open Project…")
                shortcutText: root.keys("open")
                onTriggered: root.header.openProject()
            }
            ThemedContextMenu {
                id: recentMenu
                title: qsTr("Open Recent")

                Instantiator {
                    model: EditorState.projectFile.recentProjects
                    delegate: ThemedMenuItem {
                        required property var modelData
                        text: modelData.name || modelData.path
                        enabled: modelData.exists !== false
                                 && modelData.path !== (EditorState.projectFile.currentProjectPath || "")
                        onTriggered: root.header.openRecent(modelData.path)
                    }
                    onObjectAdded: (index, object) => recentMenu.insertItem(index, object)
                    onObjectRemoved: (index, object) => recentMenu.removeItem(object)
                }
            }
            ThemedMenuSeparator {}
            ThemedMenuItem {
                text: qsTr("Import Media…")
                enabled: root.editing
                onTriggered: root.win.importMediaFiles()
            }
            ThemedMenuSeparator {}
            ThemedMenuItem {
                text: qsTr("Save Project")
                shortcutText: root.keys("save")
                enabled: root.editing
                onTriggered: root.header.saveProject()
            }
            ThemedMenuItem {
                text: qsTr("Save Project As…")
                shortcutText: root.keys("saveAs")
                enabled: root.editing
                onTriggered: root.header.saveProjectAs()
            }
            ThemedMenuItem {
                text: qsTr("Save Shareable Copy…")
                enabled: root.editing
                onTriggered: root.header.packageProject()
            }
            ThemedMenuSeparator {}
            ThemedMenuItem {
                text: qsTr("Export Video…")
                enabled: root.editing && !EditorState.exportInProgress
                onTriggered: root.header.exportVideo()
            }
            ThemedMenuSeparator {}
            ThemedMenuItem {
                text: qsTr("Video Size and Layout…")
                enabled: root.editing
                onTriggered: root.header.openVideoSize()
            }
            ThemedMenuItem {
                text: qsTr("Project Properties…")
                enabled: root.editing
                onTriggered: root.header.openProjectProperties()
            }
            ThemedMenuSeparator {}
            ThemedMenuItem {
                text: qsTr("Preferences…")
                onTriggered: root.win.openSettings()
            }
            ThemedMenuItem {
                text: qsTr("Keyboard Shortcuts")
                shortcutText: "F1"
                onTriggered: root.win.showAssetsTab("shortcuts")
            }
            ThemedMenuSeparator {}
            ThemedMenuItem {
                text: qsTr("Back to Home")
                onTriggered: root.header.closeProject()
            }
            ThemedMenuItem {
                text: qsTr("Quit")
                onTriggered: root.win.quitApp()
            }
        }
    }

    // --- Edit ---------------------------------------------------------------------------------
    MenuButton {
        text: qsTr("Edit")
        menu: editMenu

        ThemedContextMenu {
            id: editMenu
            minimumWidth: 260

            ThemedMenuItem {
                text: qsTr("Undo")
                shortcutText: root.keys("undo")
                enabled: root.editing && EditorState.undoAvailable
                onTriggered: root.dispatch("undo")
            }
            ThemedMenuItem {
                text: qsTr("Redo")
                shortcutText: root.keys("redo")
                enabled: root.editing && EditorState.redoAvailable
                onTriggered: root.dispatch("redo")
            }
            ThemedMenuSeparator {}
            ThemedMenuItem {
                text: qsTr("Cut")
                shortcutText: root.keys("cut")
                enabled: root.editing
                onTriggered: root.dispatch("cut")
            }
            ThemedMenuItem {
                text: qsTr("Copy")
                shortcutText: root.keys("copy")
                enabled: root.editing
                onTriggered: root.dispatch("copy")
            }
            ThemedMenuItem {
                text: qsTr("Paste")
                shortcutText: root.keys("paste")
                enabled: root.editing
                onTriggered: root.dispatch("paste")
            }
            ThemedMenuItem {
                text: qsTr("Duplicate")
                shortcutText: root.keys("duplicate")
                enabled: root.editing
                onTriggered: root.dispatch("duplicate")
            }
            ThemedMenuSeparator {}
            ThemedMenuItem {
                text: qsTr("Delete")
                shortcutText: root.keys("delete")
                enabled: root.editing
                onTriggered: root.dispatch("delete")
            }
            ThemedMenuSeparator {}
            ThemedMenuItem {
                text: qsTr("Copy Effects")
                shortcutText: root.keys("copyEffects")
                enabled: root.editing
                onTriggered: root.dispatch("copyEffects")
            }
            ThemedMenuItem {
                text: qsTr("Paste Effects")
                shortcutText: root.keys("pasteEffects")
                enabled: root.editing
                onTriggered: root.dispatch("pasteEffects")
            }
            ThemedMenuItem {
                text: qsTr("Paste Attributes…")
                shortcutText: root.keys("pasteAttributes")
                enabled: root.editing
                onTriggered: root.win.openPasteAttributes()
            }
            ThemedMenuSeparator {}
            ThemedMenuItem {
                text: qsTr("Find and Replace…")
                shortcutText: root.keys("findReplace")
                enabled: root.editing
                onTriggered: root.win.openFindReplace()
            }
            ThemedMenuSeparator {}
            ThemedMenuItem {
                text: qsTr("Select All")
                shortcutText: root.keys("selectAll")
                enabled: root.editing
                onTriggered: root.dispatch("selectAll")
            }
            ThemedMenuItem {
                text: qsTr("Deselect All")
                shortcutText: root.keys("clearSelection")
                enabled: root.editing
                onTriggered: root.dispatch("clearSelection")
            }
        }
    }

    // --- Tools --------------------------------------------------------------------------------
    MenuButton {
        text: qsTr("Tools")
        menu: toolsMenu

        ThemedContextMenu {
            id: toolsMenu
            minimumWidth: 280

            readonly property bool compositeSelected: EditorState.selectedClipData
                                                      && EditorState.selectedClipData.kind === "composite"

            ThemedMenuItem {
                text: qsTr("Split")
                shortcutText: root.keys("split")
                enabled: root.editing
                onTriggered: root.dispatch("split")
            }
            ThemedMenuItem {
                text: qsTr("Merge Clips")
                shortcutText: root.keys("merge")
                enabled: root.editing
                onTriggered: root.dispatch("merge")
            }
            ThemedMenuItem {
                text: qsTr("Separate Audio")
                shortcutText: root.keys("separateAudio")
                enabled: root.editing
                onTriggered: root.dispatch("separateAudio")
            }
            ThemedMenuItem {
                text: qsTr("Link Clips")
                shortcutText: root.keys("link")
                enabled: root.editing
                onTriggered: root.dispatch("link")
            }
            ThemedMenuItem {
                text: qsTr("Unlink Clips")
                shortcutText: root.keys("unlink")
                enabled: root.editing
                onTriggered: root.dispatch("unlink")
            }
            ThemedMenuSeparator {}
            ThemedMenuItem {
                text: qsTr("Group (Compound Clip)")
                enabled: root.editing && EditorState.makeCompositeAvailable
                onTriggered: EditorState.makeCompositeFromSelection()
            }
            ThemedMenuItem {
                text: qsTr("Ungroup")
                enabled: root.editing && toolsMenu.compositeSelected
                onTriggered: EditorState.ungroupComposite(EditorState.selectedTrack, EditorState.selectedClip)
            }
            ThemedMenuItem {
                text: qsTr("Save as Template…")
                enabled: root.editing && toolsMenu.compositeSelected
                onTriggered: EditorState.requestSaveTemplate(EditorState.clipAssetId(EditorState.selectedTrack,
                                                                                     EditorState.selectedClip))
            }
            ThemedMenuItem {
                text: qsTr("AI Transition to the Next Clip")
                enabled: root.editing && EditorState.selectedTrack >= 0 && EditorState.selectedClip >= 0
                onTriggered: {
                    if (EditorState.aiTransitionAvailable())
                        EditorState.addAiTransitionAfter(EditorState.selectedTrack, EditorState.selectedClip)
                    else
                        root.win.openAddonManager("interp-model")
                }
            }
            ThemedMenuItem {
                text: qsTr("Transform Together")
                shortcutText: root.keys("transformTogether")
                enabled: root.editing && EditorState.transformTogetherAvailable
                onTriggered: root.dispatch("transformTogether")
            }
            ThemedMenuSeparator {}
            ThemedMenuItem {
                text: qsTr("Auto Subtitles")
                enabled: root.editing
                onTriggered: root.win.showAssetsTab("subtitles")
            }
            ThemedMenuItem {
                text: qsTr("Text to Speech")
                enabled: root.editing
                onTriggered: root.win.showAssetsTab("speech")
            }
            ThemedMenuItem {
                text: qsTr("Scene Detection")
                enabled: root.editing
                onTriggered: root.win.showAssetsTab("scenes")
            }
            ThemedMenuItem {
                text: qsTr("Multicam")
                shortcutText: root.keys("multicam")
                enabled: root.editing
                onTriggered: root.win.openMulticam()
            }
        }
    }

    // --- View ---------------------------------------------------------------------------------
    MenuButton {
        text: qsTr("View")
        menu: viewMenu

        ThemedContextMenu {
            id: viewMenu
            minimumWidth: 290

            ThemedMenuItem {
                text: qsTr("Play / Pause")
                shortcutText: root.keys("playPause")
                enabled: root.editing
                onTriggered: root.dispatch("playPause")
            }
            ThemedMenuItem {
                text: qsTr("Go to Start")
                shortcutText: root.keys("goToStart")
                enabled: root.editing
                onTriggered: root.dispatch("goToStart")
            }
            ThemedMenuItem {
                text: qsTr("Previous Frame")
                shortcutText: root.keys("stepBack")
                enabled: root.editing
                onTriggered: root.dispatch("stepBack")
            }
            ThemedMenuItem {
                text: qsTr("Next Frame")
                shortcutText: root.keys("stepForward")
                enabled: root.editing
                onTriggered: root.dispatch("stepForward")
            }
            ThemedMenuItem {
                text: qsTr("Loop Playback")
                shortcutText: root.keys("toggleLoop")
                enabled: root.editing
                onTriggered: root.dispatch("toggleLoop")
            }
            ThemedMenuItem {
                text: EditorState.playback.ramPreviewBuilding ? qsTr("Stop RAM Preview") : qsTr("RAM Preview")
                shortcutText: root.keys("ramPreview")
                enabled: root.editing
                onTriggered: root.dispatch("ramPreview")
            }
            ThemedContextMenu {
                title: qsTr("Bookmarks")

                ThemedMenuItem {
                    text: qsTr("Add or Remove Bookmark")
                    shortcutText: root.keys("toggleBookmark")
                    enabled: root.editing
                    onTriggered: root.dispatch("toggleBookmark")
                }
                ThemedMenuItem {
                    text: qsTr("Next Bookmark")
                    shortcutText: root.keys("nextBookmark")
                    enabled: root.editing
                    onTriggered: root.dispatch("nextBookmark")
                }
                ThemedMenuItem {
                    text: qsTr("Previous Bookmark")
                    shortcutText: root.keys("previousBookmark")
                    enabled: root.editing
                    onTriggered: root.dispatch("previousBookmark")
                }
            }
            ThemedMenuSeparator {}
            ThemedMenuItem {
                text: qsTr("Zoom In")
                shortcutText: root.keys("zoomIn")
                enabled: root.editing
                onTriggered: root.dispatch("zoomIn")
            }
            ThemedMenuItem {
                text: qsTr("Zoom Out")
                shortcutText: root.keys("zoomOut")
                enabled: root.editing
                onTriggered: root.dispatch("zoomOut")
            }
            ThemedMenuItem {
                text: qsTr("Fullscreen Preview")
                enabled: root.editing
                onTriggered: root.win.togglePreviewFullscreen()
            }
            ThemedMenuItem {
                text: qsTr("Guides")
                shortcutText: root.keys("toggleGuides")
                enabled: root.editing
                onTriggered: root.dispatch("toggleGuides")
            }
            ThemedMenuItem {
                text: qsTr("Rulers")
                icon.name: EditorState.preview.rulersVisible ? Theme.icons.check : ""
                shortcutText: root.keys("toggleRulers")
                enabled: root.editing
                onTriggered: root.dispatch("toggleRulers")
            }
            ThemedMenuSeparator {}
            ThemedContextMenu {
                title: qsTr("Workspace")

                ThemedMenuItem {
                    text: qsTr("Auto (follow canvas)")
                    icon.name: EditorState.preferences.workspaceLayoutOverridden ? "" : Theme.icons.check
                    onTriggered: EditorState.preferences.clearWorkspaceLayoutPreference()
                }
                ThemedMenuItem {
                    text: qsTr("Landscape")
                    icon.name: EditorState.preferences.workspaceLayoutOverridden
                               && EditorState.preferences.workspaceLayoutPreferred === "landscape" ? Theme.icons.check : ""
                    onTriggered: EditorState.preferences.setWorkspaceLayoutPreference("landscape")
                }
                ThemedMenuItem {
                    text: qsTr("Portrait")
                    icon.name: EditorState.preferences.workspaceLayoutOverridden
                               && EditorState.preferences.workspaceLayoutPreferred === "portrait" ? Theme.icons.check : ""
                    onTriggered: EditorState.preferences.setWorkspaceLayoutPreference("portrait")
                }
            }
            ThemedContextMenu {
                title: qsTr("Theme")

                ThemedMenuItem {
                    text: qsTr("Light")
                    icon.name: Theme.darkMode ? "" : Theme.icons.check
                    onTriggered: Theme.setDarkMode(false)
                }
                ThemedMenuItem {
                    text: qsTr("Dark")
                    icon.name: Theme.darkMode ? Theme.icons.check : ""
                    onTriggered: Theme.setDarkMode(true)
                }
            }
            ThemedMenuItem {
                text: qsTr("Language…")
                onTriggered: root.header.openLanguageChooser()
            }
            ThemedMenuItem {
                text: qsTr("Switch to Mobile Layout…")
                onTriggered: root.win.switchShell("mobile")
            }
        }
    }

    // --- Advanced -----------------------------------------------------------------------------
    MenuButton {
        text: qsTr("Advanced")
        menu: advancedMenu

        ThemedContextMenu {
            id: advancedMenu
            minimumWidth: 240

            ThemedMenuItem {
                text: qsTr("Extras…")
                onTriggered: root.win.openExtras()
            }
            ThemedMenuItem {
                text: qsTr("Agent Access…")
                onTriggered: root.header.openAgentAccess()
            }
            ThemedMenuItem {
                text: qsTr("Downloads")
                onTriggered: root.header.downloadsRequested()
            }
            ThemedMenuSeparator {}
            ThemedMenuItem {
                text: qsTr("Debug Info…")
                onTriggered: root.win.openDebugInfo()
            }
        }
    }

    // --- Help ---------------------------------------------------------------------------------
    MenuButton {
        text: qsTr("Help")
        menu: helpMenu

        ThemedContextMenu {
            id: helpMenu
            minimumWidth: 260

            ThemedMenuItem {
                text: qsTr("Keyboard Shortcuts")
                shortcutText: "F1"
                onTriggered: root.win.showAssetsTab("shortcuts")
            }
            ThemedMenuItem {
                text: qsTr("What's New")
                onTriggered: Qt.openUrlExternally("https://getflipstudio.com/novedades.html")
            }
            ThemedMenuItem {
                text: qsTr("Flip Studio Website")
                onTriggered: Qt.openUrlExternally("https://getflipstudio.com")
            }
            ThemedMenuSeparator {}
            ThemedMenuItem {
                text: qsTr("Check for Updates…")
                visible: Qt.platform.os !== "android"
                onTriggered: root.header.checkUpdates()
            }
            ThemedMenuItem {
                text: qsTr("My Account")
                visible: Account.available
                onTriggered: root.header.accountRequested()
            }
            ThemedMenuSeparator {}
            ThemedMenuItem {
                text: qsTr("About Flip Studio")
                onTriggered: root.win.openAboutDialog()
            }
        }
    }
}
