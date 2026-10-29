import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import QtQuick.Dialogs
import Drift
import "components"
import "components/assets"

PanelFrame {
    id: root

    // When true (Android bottom sheet), hide the side tab rail — the phone
    // bottom rail already picks the active library tab.
    property bool sheetMode: false

    // One of the click-to-add tabs (text, subtitles, stickers, shapes) put a clip
    // on the timeline. The phone shell closes the sheet on this; desktop, where
    // the panel is docked, simply leaves it unconnected.
    signal addCompleted()
    border.width: sheetMode ? 0 : 1
    radius: sheetMode ? 0 : Theme.radiusSm
    color: sheetMode ? "transparent" : Theme.panelBackground

    Component.onCompleted: AssetLibrary.ensureAllMedia()

    // Imports and reports the outcome. `importUrls` skips anything it cannot
    // probe, so a bad file used to just never appear with no explanation at all.
    // Import policy lives in the MediaImport singleton so surfaces without an AssetsPanel —
    // the home screen, the Android share target — can import too. Kept as a wrapper because
    // several call sites and the DropArea below already speak this name.
    function importUrlsReporting(urls, fromDrop) {
        MediaImport.importUrls(urls, fromDrop)
    }

    // True while an import is running, so the panel can show progress. The folder walk counts:
    // it is the half that can take a while on a deep tree or a sandboxed (portal) mount.
    readonly property bool importing: AssetLibrary.importing || EditorState.bin.importingFolder

    // A single id goes through the existing single-asset add so that case is byte-for-byte the
    // behavior it always was; only an actual multi-selection goes through the batch add, which
    // places each clip back to back in selection order instead of stacking them all at the
    // playhead.
    function requestAddToTimeline(assetIds) {
        if (assetIds.length === 0)
            return

        function runAdd() {
            if (assetIds.length === 1)
                EditorState.addClipFromAsset(AssetLibrary.indexOfId(assetIds[0]))
            else
                EditorState.addClipsFromAssets(assetIds)
        }

        // On a pristine project, the first video/image clip offers to set up the canvas
        // (resolution/orientation) — same flow as dragging onto the timeline (see
        // TimelinePanel.qml/AndroidTimeline.qml). For a multi-selection, offer it from the
        // first asset that actually needs it, not always assetIds[0].
        if (typeof Window === "undefined" || !Window.window || !Window.window.configureAndAddAsset) {
            runAdd()
            return
        }
        for (const id of assetIds) {
            const index = AssetLibrary.indexOfId(id)
            if (index >= 0 && EditorState.shouldConfigureProjectForAsset(index)) {
                Window.window.configureAndAddAsset(index, runAdd)
                return
            }
        }
        runAdd()
    }

    // Asset ids awaiting confirmation in confirmAssetRemoval — a single-element array for a
    // plain right-click, or the whole multi-selection. The label is held separately because
    // the rows are gone by the time the toast reports on them.
    property var pendingRemovalIds: []
    property string pendingRemovalLabel: ""
    property int pendingRemovalClipCount: 0

    // Removing an asset a clip still points at would leave that clip playing but unable to
    // trim past its cut or merge, so refuse rather than confirm — for a bulk removal, refusing
    // the whole batch over one in-use item beats silently dropping it and surprising the user
    // with a smaller removal than they asked for.
    function requestRemoveAsset(assetIds) {
        const names = []
        let clipCount = 0

        for (const id of assetIds) {
            const index = AssetLibrary.indexOfId(id)
            if (index < 0)
                continue

            names.push(AssetLibrary.assetAt(index).name)
            clipCount += EditorState.clipCountForAsset(index)
        }

        if (names.length === 0)
            return

        root.pendingRemovalIds = assetIds
        root.pendingRemovalLabel =
            names.length === 1 ? names[0] : qsTr("%n items", "", names.length)
        root.pendingRemovalClipCount = clipCount
        confirmAssetRemoval.open()
    }

    ThemedDialog {
        id: confirmAssetRemoval
        title: root.pendingRemovalIds.length === 1 ? qsTr("Remove this media?") : qsTr("Remove these items?")
        acceptText: qsTr("Remove")
        acceptVariant: "destructive"
        preferredWidth: Theme.dialogWidthSm
        // Enter must not commit a destructive action.
        acceptOnReturn: false

        contentItem: ThemedLabel {
            width: parent ? parent.width : Theme.dialogWidthSm
            wrapMode: Text.WordWrap
            size: "sm"
            text: root.pendingRemovalClipCount > 0
                ? (root.pendingRemovalClipCount === 1
                    ? qsTr("“%1” is used by 1 clip on the timeline. Removing this media will also remove that clip and any transitions connected to it. The file on disk is not deleted.")
                        .arg(root.pendingRemovalLabel)
                    : qsTr("“%1” is used by %2 clips on the timeline. Removing this media will also remove those clips and any transitions connected to them. The files on disk are not deleted.")
                        .arg(root.pendingRemovalLabel)
                        .arg(root.pendingRemovalClipCount))
                : qsTr("“%1” will be removed from this project. The file on disk is not deleted.")
                    .arg(root.pendingRemovalLabel)
        }

        onAccepted: {
            const removed = root.pendingRemovalClipCount > 0
                ? EditorState.removeAssetsAndClips(root.pendingRemovalIds)
                : EditorState.removeAssets(root.pendingRemovalIds)
            if (removed > 0) {
                Toasts.success(removed === 1
                    ? qsTr("Removed “%1”.").arg(root.pendingRemovalLabel)
                    : qsTr("Removed %n items.", "", removed))
            }
            root.pendingRemovalIds = []
        }
        onRejected: root.pendingRemovalIds = []
    }

    property int pendingRenameIndex: -1

    function requestRenameAsset(assetIndex) {
        const asset = AssetLibrary.assetAt(assetIndex)
        if (!asset || Object.keys(asset).length === 0)
            return
        root.pendingRenameIndex = assetIndex
        assetRenameField.text = asset.name || ""
        assetRenameDialog.open()
    }

    ThemedDialog {
        id: assetRenameDialog
        title: qsTr("Rename media")
        acceptText: qsTr("Rename")
        preferredWidth: Theme.dialogWidthSm

        contentItem: Column {
            width: parent ? parent.width : Theme.dialogWidthSm
            spacing: Theme.spacingMd

            ThemedLabel {
                width: parent.width
                text: qsTr("Name")
                size: "sm"
            }
            ThemedTextField {
                id: assetRenameField
                width: parent.width
                placeholderText: qsTr("Media name")
            }
        }

        onOpened: {
            assetRenameField.forceActiveFocus()
            assetRenameField.selectAll()
        }
        onAccepted: {
            if (root.pendingRenameIndex < 0)
                return
            const label = assetRenameField.text.trim()
            if (label.length > 0)
                EditorState.renameAsset(root.pendingRenameIndex, label)
            root.pendingRenameIndex = -1
        }
        onRejected: root.pendingRenameIndex = -1
    }

    ThemedDialog {
        id: newFolderDialog
        title: qsTr("New folder")
        acceptText: qsTr("Create")
        preferredWidth: Theme.dialogWidthSm

        contentItem: Column {
            width: parent ? parent.width : Theme.dialogWidthSm
            spacing: Theme.spacingMd

            ThemedLabel {
                width: parent.width
                text: qsTr("Name")
                size: "sm"
            }
            ThemedTextField {
                id: newFolderNameField
                width: parent.width
                placeholderText: qsTr("Folder name")
            }
        }

        onOpened: {
            newFolderNameField.text = ""
            newFolderNameField.forceActiveFocus()
        }
        onAccepted: {
            const label = newFolderNameField.text.trim()
            if (label.length > 0)
                EditorState.bin.createFolder(label, EditorState.bin.currentFolderId)
        }
    }

    property string pendingFolderRenameId: ""

    function requestRenameFolder(folderId, folderName) {
        root.pendingFolderRenameId = folderId
        folderRenameField.text = folderName || ""
        folderRenameDialog.open()
    }

    ThemedDialog {
        id: folderRenameDialog
        title: qsTr("Rename folder")
        acceptText: qsTr("Rename")
        preferredWidth: Theme.dialogWidthSm

        contentItem: Column {
            width: parent ? parent.width : Theme.dialogWidthSm
            spacing: Theme.spacingMd

            ThemedLabel {
                width: parent.width
                text: qsTr("Name")
                size: "sm"
            }
            ThemedTextField {
                id: folderRenameField
                width: parent.width
                placeholderText: qsTr("Folder name")
            }
        }

        onOpened: {
            folderRenameField.forceActiveFocus()
            folderRenameField.selectAll()
        }
        onAccepted: {
            if (root.pendingFolderRenameId.length === 0)
                return
            const label = folderRenameField.text.trim()
            if (label.length > 0)
                EditorState.bin.renameFolder(root.pendingFolderRenameId, label)
            root.pendingFolderRenameId = ""
        }
        onRejected: root.pendingFolderRenameId = ""
    }

    // The "move to folder" path — right-click on a card (or a multi-selection), choose a
    // destination from a flat list. Also doubles as the folder-move picker (pendingMoveFolderId)
    // for reparenting a folder itself; the two are mutually exclusive, never both set.
    property var pendingMoveAssetIds: []
    // The folder every selected asset is in right now, so the picker can omit it — moving them
    // "into" the folder they're already in isn't a real destination. A single common value is
    // safe here (not a per-asset lookup): MediaAssetsTab's grid only ever shows one folder's
    // contents at a time, so anything selectable there already shares this folder.
    property string pendingMoveAssetCurrentFolderId: ""
    // Non-empty while the picker is choosing a new parent for this folder rather than a
    // destination for assets.
    property string pendingMoveFolderId: ""

    function requestMoveAssetToFolder(assetIds) {
        root.pendingMoveFolderId = ""
        root.pendingMoveAssetIds = assetIds
        root.pendingMoveAssetCurrentFolderId = EditorState.bin.currentFolderId
        folderPickerDialog.open()
    }

    function requestMoveFolder(folderId) {
        root.pendingMoveAssetIds = []
        root.pendingMoveFolderId = folderId
        folderPickerDialog.open()
    }

    // True if candidateId is folderId itself or nested anywhere inside it — walked the same
    // way BinBreadcrumb.qml walks a trail, with the same cycle guard folderPath() uses, since
    // this runs on the same possibly-malformed parentId chains.
    function isFolderOrDescendant(candidateId, folderId) {
        const visited = new Set()
        let id = candidateId
        while (id !== "" && !visited.has(id)) {
            if (id === folderId)
                return true
            visited.add(id)
            const folder = BinFolderModel.folderById(id)
            if (!folder || Object.keys(folder).length === 0)
                break
            id = folder.parentId
        }
        return false
    }

    // Matches BinBreadcrumb.qml's own separator glyph, so a folder's path reads the same way
    // here as it does in the "where you are" trail above the grid.
    readonly property string folderPathSeparator: ">"

    // Full path from the bin root down to folderId, e.g. "Interviews > B-Roll" — walks
    // parentId the same way BinBreadcrumb.qml does, since a flat name alone can't
    // distinguish two same-named folders nested under different parents.
    function folderPath(folderId) {
        const names = []
        const visited = new Set()
        let id = folderId
        // Project deserialization doesn't reject a self- or mutually-parented folder, and
        // this runs once per folder every time the picker opens — an undetected cycle would
        // spin this loop forever and hang the UI, so bail the moment an id repeats.
        while (id !== "" && !visited.has(id)) {
            visited.add(id)
            const folder = BinFolderModel.folderById(id)
            if (!folder || Object.keys(folder).length === 0)
                break
            names.unshift(folder.name)
            id = folder.parentId
        }
        return names.join(" " + root.folderPathSeparator + " ")
    }

    ThemedDialog {
        id: folderPickerDialog
        title: qsTr("Move to folder")
        showFooter: false
        preferredWidth: Theme.dialogWidthSm

        // Flat list, root first, minus destinations that aren't real moves. Each entry shows
        // its full path rather than just its own name, so two folders that happen to share a
        // name (nested under different parents) still read as distinct destinations.
        //
        // folderAt() is a plain invokable call, not a property read, so it isn't by itself
        // enough to make this binding re-evaluate after a rename (BinFolderModel.count doesn't
        // change either). Reading undoAvailable is a cheap way to add that dependency: its
        // NOTIFY is undoStackChanged, which fires after every project edit including a rename.
        readonly property var folderOptions: {
            void EditorState.undoAvailable
            const movingFolderId = root.pendingMoveFolderId
            const out = []
            if (movingFolderId !== "") {
                // Moving a folder itself: exclude the folder, anything already its parent (no-op),
                // and every one of its own descendants — landing there would create a cycle.
                const currentParentId = BinFolderModel.folderById(movingFolderId).parentId || ""
                if (currentParentId !== "")
                    out.push({ id: "", name: qsTr("Media"), path: qsTr("Media") })
                for (let i = 0; i < BinFolderModel.count; ++i) {
                    const folder = BinFolderModel.folderAt(i)
                    if (folder.id === currentParentId)
                        continue
                    if (root.isFolderOrDescendant(folder.id, movingFolderId))
                        continue
                    out.push({ id: folder.id, name: folder.name, path: root.folderPath(folder.id) })
                }
                return out
            }

            const currentFolderId = root.pendingMoveAssetCurrentFolderId
            if (currentFolderId !== "")
                out.push({ id: "", name: qsTr("Media"), path: qsTr("Media") })
            for (let i = 0; i < BinFolderModel.count; ++i) {
                const folder = BinFolderModel.folderAt(i)
                if (folder.id !== currentFolderId)
                    out.push({ id: folder.id, name: folder.name, path: root.folderPath(folder.id) })
            }
            return out
        }

        // A Rectangle used directly as contentItem never reports its explicit `height` as
        // `implicitHeight`, so the Dialog (which sizes off contentItem.implicitHeight) sees zero
        // and clips the list away entirely. Wrapping in a Column — which does propagate its
        // children's real heights into implicitHeight — is the same fix LanguageChooserDialog
        // already uses for the identical list-in-a-dialog shape.
        contentItem: Column {
            width: parent ? parent.width : Theme.dialogWidthSm

            Rectangle {
                width: parent.width
                height: Math.min(pickerList.contentHeight + 2, 280)
                radius: Theme.radiusSm
                color: Theme.appBackground
                border.width: Theme.borderWidth
                border.color: Theme.panelBorder
                clip: true

                ListView {
                    id: pickerList
                    anchors.fill: parent
                    anchors.margins: 1
                    clip: true
                    model: folderPickerDialog.folderOptions
                    interactive: contentHeight > height
                    boundsBehavior: Flickable.StopAtBounds
                    ScrollBar.vertical: AppScrollBar { }

                    delegate: ItemDelegate {
                        id: optionRow
                        required property var modelData
                        width: pickerList.width
                        height: 40
                        hoverEnabled: true

                        HoverHandler {
                            cursorShape: Qt.PointingHandCursor
                        }

                        background: Rectangle {
                            color: optionRow.hovered ? Theme.popoverHover : "transparent"
                        }

                        contentItem: Text {
                            anchors.fill: parent
                            anchors.leftMargin: 12
                            anchors.rightMargin: 12
                            verticalAlignment: Text.AlignVCenter
                            text: optionRow.modelData.path
                            elide: Text.ElideRight
                            color: Theme.panelForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeSm
                        }

                        onClicked: {
                            // Closed before the move runs, not after: moving a folder changes
                            // undoAvailable, which folderOptions depends on, which swaps the
                            // ListView's model out from under this very delegate — closing
                            // first avoids racing that live update instead of fighting it.
                            const targetId = optionRow.modelData.id
                            folderPickerDialog.close()
                            if (root.pendingMoveFolderId !== "") {
                                EditorState.bin.moveFolder(root.pendingMoveFolderId, targetId)
                                root.pendingMoveFolderId = ""
                            } else if (root.pendingMoveAssetIds.length > 0) {
                                EditorState.bin.moveAssetsToFolder(root.pendingMoveAssetIds, targetId)
                                root.pendingMoveAssetIds = []
                            }
                        }
                    }
                }
            }
        }
    }

    // A file deleted, renamed or moved since import: pick it where it is now. The clips keep
    // everything; the others missing from that same folder are found along with it.
    function findMissingAsset(assetId, path) {
        const fileName = String(path).split(/[\/]/).pop()
        const url = FileDialogs.openFile(qsTr("Where is %1 now?").arg(fileName),
                                         [qsTr("%1 (%1)").arg(fileName), AssetLibrary.mediaNameFilter(),
                                          qsTr("All files (*)")])
        if (!url || url.toString() === "")
            return
        const found = EditorState.bin.relinkMissing(assetId, url)
        if (found > 1)
            Toasts.success(qsTr("%n files found", "", found))
        else if (found === 1)
            Toasts.success(qsTr("File found"))
    }

    // Points a bin row at a different file while every clip using it stays put, so a project set
    // up once — music, outro, CTA — can be re-pointed at the next video instead of rebuilt.
    function requestReplaceAsset(assetIndex) {
        var url = FileDialogs.openFile(qsTr("Replace Media"), [AssetLibrary.mediaNameFilter()])
        if (!url || url.toString() === "")
            return
        EditorState.bin.replaceSource(assetIndex, url)
    }

    // Writes an image row back out to disk — the way a freeze frame captured in the preview
    // leaves the project. The format follows the name the user picks, not the filter.
    function requestExportAsset(assetIndex) {
        const asset = AssetLibrary.assetAt(assetIndex)
        if (!asset || asset.kind !== "image")
            return
        var url = FileDialogs.saveFile(qsTr("Export Image"), [
            qsTr("PNG image (*.png)"),
            qsTr("JPEG image (*.jpg *.jpeg)")
        ], asset.name, "png")
        if (!url || url.toString() === "")
            return
        if (EditorState.bin.exportImage(assetIndex, url))
            Toasts.success(qsTr("Exported “%1”.").arg(asset.name))
        else
            Toasts.error(qsTr("Couldn’t export that image."))
    }

    // Copies the file behind a bin row out to disk as is, no transcode.
    function requestSaveAssetAs(assetIndex) {
        const asset = AssetLibrary.assetAt(assetIndex)
        if (!asset || !asset.path)
            return
        const fileName = asset.path.substring(asset.path.lastIndexOf("/") + 1)
        const dot = fileName.lastIndexOf(".")
        const suffix = dot > 0 ? fileName.substring(dot + 1) : ""
        let baseName = asset.name || (dot > 0 ? fileName.substring(0, dot) : fileName)
        if (suffix && baseName.toLowerCase().endsWith("." + suffix.toLowerCase()))
            baseName = baseName.substring(0, baseName.length - suffix.length - 1)
        const filters = suffix ? [qsTr("%1 file (*.%2)").arg(suffix.toUpperCase()).arg(suffix)]
                               : [qsTr("All files (*)")]
        var url = FileDialogs.saveFile(qsTr("Save As"), filters, baseName, suffix)
        if (!url || url.toString() === "")
            return
        if (EditorState.bin.saveAs(assetIndex, url))
            Toasts.info(qsTr("Saving “%1”…").arg(asset.name))
        else
            Toasts.error(qsTr("Couldn’t save “%1”.").arg(asset.name))
    }

    Connections {
        target: EditorState.bin

        // Hitting the limit outranks the skipped count: the walk stopped early, so what it passed
        // over is only part of the story and saying both would suggest otherwise.
        function onFolderImportFinished(folders, files, skipped, truncated) {
            if (folders === 0) {
                Toasts.error(qsTr("Couldn’t import that folder."))
            } else if (truncated) {
                Toasts.warning(qsTr("Imported %n files into %1 folders — as many as one folder import takes. Import the remaining subfolders separately.", "", files).arg(folders))
            } else if (skipped > 0) {
                Toasts.warning(qsTr("Imported %n files into %1 folders. %2 files were skipped — Flip Studio does not recognize their format. Drag them onto the bin to try anyway.", "", files).arg(folders).arg(skipped))
            } else {
                Toasts.success(qsTr("Imported %n files into %1 folders.", "", files).arg(folders))
            }
        }

        function onSaveFinished(ok, name) {
            if (ok)
                Toasts.success(qsTr("Saved “%1”.").arg(name))
            else
                Toasts.error(qsTr("Couldn’t save “%1”.").arg(name))
        }

        // The probe runs off-thread, so the outcome comes back here rather than from the call.
        function onReplaceFinished(ok, message, adjustedClips) {
            if (!ok) {
                Toasts.warning(message)
            } else if (adjustedClips > 0) {
                Toasts.warning(qsTr("Replaced with “%1”. %n clips were shortened to fit the new file.",
                                    "", adjustedClips).arg(message))
            } else {
                Toasts.success(qsTr("Replaced with “%1”.").arg(message))
            }
        }

        function onEditFinished(ok, message) {
            if (!ok) {
                if (message && message.length > 0)
                    Toasts.warning(message)
            } else if (EditorState.bin.editIsConversion) {
                Toasts.success(qsTr("“%1” is now in an edit-friendly format.").arg(message))
            } else {
                Toasts.success(qsTr("Saved “%1”. Drag it onto the timeline.").arg(message))
            }
        }
    }

    function importMedia() {
        var urls = FileDialogs.openFiles(qsTr("Import Media"),
                                         [AssetLibrary.mediaNameFilter(),
                                          qsTr("All Files (*)")])
        root.importUrlsReporting(urls)
    }

    // Imports a whole directory: a new bin folder mirrors the picked folder (and everything
    // nested under it), and every media file lands in the bin folder matching its containing
    // directory. EditorState.bin.importFolder does the walk synchronously — probing and
    // thumbnailing each file still happens in the background the same as any other import.
    function importFolder() {
        var url = FileDialogs.openDirectory(qsTr("Import Folder"))
        if (!url || url.toString() === "")
            return
        // The walk runs off-thread, so the outcome arrives as onFolderImportFinished below.
        if (!EditorState.bin.importFolder(url))
            Toasts.error(qsTr("Couldn’t import that folder."))
    }

    function collectMedia() {
        var url = FileDialogs.openDirectory(qsTr("Collect Media to Folder"))
        if (!url || url.toString() === "")
            return
        collectMediaDialog.folder = url
        collectMediaDialog.open()
    }

    CollectMediaDialog {
        id: collectMediaDialog
    }

    // Selects a tab by id. Used by cross-panel jumps such as the properties
    // panel's "Browse effects" / "Browse audio effects" empty-state actions.
    // Titles › Text on one of its sections ("trends"), whether or not the tab is open already.
    signal textSectionRequested(string section)
    function showTextSection(section) {
        rememberTab("text", "section", section)
        showTab("text")
        textSectionRequested(section)
    }

    function showTab(tabId) {
        for (var i = 0; i < tabsModel.count; ++i) {
            if (tabsModel.get(i).tabId === tabId) {
                root.activeTab = i
                return
            }
        }
    }

    function tabLabel(tabId) {
        return tabLabels[tabId] || ""
    }

    // Tabs whose feature runs an AI model on this computer: the sidebar marks them "AI" with a "?"
    // that says what it does (AiBadge, Filmora's mark).
    readonly property var aiInfo: ({
        "subtitles": qsTr("Writes the subtitles from what is said in the video, word by word."),
        "speech": qsTr("Turns your text into a natural-sounding voice."),
        "scenes": qsTr("Finds where each shot starts and what is in it.")
    })

    function kindsForTab(tabId) {
        if (tabId === "media") return ["video", "image", "audio", "vector", "model3d", "pdf", "composite", "solid"]
        return []
    }

    function assetVisible(kind) {
        const tabId = tabsModel.get(activeTab).tabId
        if (tabId === "text" || tabId === "subtitles" || tabId === "speech" || tabId === "stickers" || tabId === "shapes"
                || tabId === "effects" || tabId === "templates" || tabId === "effectTemplates" || tabId === "adjustment"
                || tabId === "sounds" || tabId === "sfx" || tabId === "music" || tabId === "transitions" || tabId === "masks"
                || tabId === "shortcuts" || tabId === "scenes" || tabId === "market"
                || tabId === "filters" || tabId === "colorfx")
            return false
        const kinds = kindsForTab(tabId)
        return kinds.length === 0 || kinds.indexOf(kind) >= 0
    }

    // ListElement only accepts literal values; qsTr() calls are not
    // evaluated. Labels are translated via tabLabels below.
    property var tabLabels: ({
        "media": qsTr("Media"),
        "market": qsTr("Stock"),
        "text": qsTr("Text"),
        "subtitles": qsTr("Subtitles"),
        "speech": qsTr("Speech"),
        "stickers": qsTr("Stickers"),
        "shapes": qsTr("Shapes"),
        "scenes": qsTr("Scenes"),
        "masks": qsTr("Masks"),
        "effects": qsTr("Effects"),
        // Scene templates: the ones downloaded from Stock and the ones saved by the person.
        "templates": qsTr("My templates"),
        "effectTemplates": qsTr("Effect templates"),
        "transitions": qsTr("Transitions"),
        "sounds": qsTr("Audio FX"),
        "music": qsTr("Music"),
        "sfx": qsTr("Sound effects"),
        "filters": qsTr("LUTs"),
        "colorfx": qsTr("Color effects"),
        "shortcuts": qsTr("Shortcuts")
    })

    // Tab order follows the categories below (Filmora/CapCut): media → Stock → audio → titles →
    // transitions → effects → filters → stickers → templates, then shortcuts (Help › Shortcuts, F1).
    // tabId "sounds" is kept for favorites persistence (settings key).
    ListModel {
        id: tabsModel
        ListElement { tabId: "media"; icon: 0 }
        ListElement { tabId: "scenes"; icon: 10 }
        ListElement { tabId: "market"; icon: 12 }
        ListElement { tabId: "music"; icon: 14 }
        ListElement { tabId: "sfx"; icon: 15 }
        ListElement { tabId: "speech"; icon: 13 }
        ListElement { tabId: "sounds"; icon: 8 }
        ListElement { tabId: "text"; icon: 1 }
        ListElement { tabId: "subtitles"; icon: 2 }
        ListElement { tabId: "transitions"; icon: 7 }
        ListElement { tabId: "effects"; icon: 5 }
        ListElement { tabId: "filters"; icon: 16 }
        ListElement { tabId: "colorfx"; icon: 17 }
        ListElement { tabId: "stickers"; icon: 3 }
        ListElement { tabId: "shapes"; icon: 4 }
        ListElement { tabId: "masks"; icon: 11 }
        ListElement { tabId: "templates"; icon: 6 }
        ListElement { tabId: "effectTemplates"; icon: 18 }
        ListElement { tabId: "shortcuts"; icon: 9 }

        // A build without a marketplace service (Flip Studio has none yet) drops the tab rather
        // than showing an empty "unavailable" page — same as the Android home nav.
        function dropTab(tabId) {
            for (let i = 0; i < count; ++i) {
                if (get(i).tabId === tabId) {
                    remove(i)
                    return
                }
            }
        }

        Component.onCompleted: {
            if (!Market.configured)
                dropTab("market")
        }
    }
    property var tabIcons: [
        Theme.icons.film,
        Theme.icons.type,
        Theme.icons.captions,
        Theme.icons.smile,
        Theme.icons.shapes,
        Theme.icons.wand,
        Theme.icons.layers,
        Theme.icons.chevronsRight,
        Theme.icons.audioLines,
        Theme.icons.keyboard,
        Theme.icons.listVideo,
        Theme.icons.mask,
        Theme.icons.store,
        Theme.icons.micVocal,
        Theme.icons.music,
        Theme.icons.volumeHigh,
        Theme.icons.blend,
        Theme.icons.sliders,
        Theme.icons.sparkles
    ]
    property int activeTab: 0
    readonly property string currentTabId: tabsModel.get(activeTab).tabId

    function tabIcon(tabId) {
        for (let i = 0; i < tabsModel.count; ++i) {
            if (tabsModel.get(i).tabId === tabId)
                return root.tabIcons[tabsModel.get(i).icon]
        }
        return ""
    }

    // The row of categories along the top of the panel (Filmora/CapCut). Each one is a group of
    // tabs; the sidebar lists the tabs of the open category, and a category with a single tab
    // gives the sidebar's width to the content.
    readonly property var categories: [
        { id: "media", label: qsTr("Media"), icon: Theme.icons.film, tabs: ["media", "scenes"] },
        { id: "market", label: qsTr("Stock"), icon: Theme.icons.store, tabs: ["market"] },
        { id: "audio", label: qsTr("Audio"), icon: Theme.icons.music, tabs: ["music", "sfx", "speech", "sounds"] },
        { id: "titles", label: qsTr("Titles"), icon: Theme.icons.type, tabs: ["text", "subtitles"] },
        { id: "transitions", label: qsTr("Transitions"), icon: Theme.icons.chevronsRight, tabs: ["transitions"] },
        { id: "effects", label: qsTr("Effects"), icon: Theme.icons.wand, tabs: ["effects"] },
        { id: "filters", label: qsTr("Filters"), icon: Theme.icons.blend, tabs: ["filters", "colorfx"] },
        { id: "stickers", label: qsTr("Stickers", "category row"), icon: Theme.icons.smile, tabs: ["stickers", "shapes", "masks"] },
        { id: "templates", label: qsTr("Templates"), icon: Theme.icons.layers, tabs: ["templates", "effectTemplates"] }
    ].filter(category => category.id !== "market" || Market.configured)

    // La barra lateral es un árbol (0.23, como Filmora): cada pestaña con su flechita y, abierta,
    // sus subcategorías una por línea. Los navegadores ya no enseñan sus chips: el panel les lleva
    // la categoría (panelDriven) y la guardan como cualquier otra cosa de la pestaña.
    readonly property var tabLoaders: ({
        media: mediaLoader, text: textLoader, subtitles: subtitlesLoader, music: musicLoader,
        sfx: sfxLoader, speech: speechLoader, sounds: soundsLoader, stickers: stickersLoader,
        shapes: shapesLoader, scenes: scenesLoader, shortcuts: shortcutsLoader, masks: masksLoader,
        effects: effectsLoader, filters: filtersLoader, colorfx: colorfxLoader,
        templates: templatesLoader, effectTemplates: effectTemplatesLoader,
        transitions: transitionsLoader, market: marketLoader
    })
    // Los grupos abiertos en el árbol, por pestaña.
    property var expandedGroups: ({})

    function browserFor(tabId) {
        const loader = root.tabLoaders[tabId]
        return loader && loader.item ? loader.item : null
    }

    // Las subcategorías de una pestaña, tal y como las tiene su navegador ({id, label}).
    function subcategoriesFor(tabId) {
        const browser = root.browserFor(tabId)
        const categories = browser && browser.categories ? browser.categories : []
        if (categories.length === 0 || tabId === "market")
            return categories
        // The star and «Mine» lived on the chips row; with the chips gone they lead the tree.
        // Same texts (and catalog entries) as the chips that offered them.
        const lead = browser.favoritesId !== undefined
                     ? [{ id: "__favorites__", label: qsTranslate("AssetCategoryChips", "Favorites") }] : []
        const mine = root.mineLabels[tabId]
        if (mine)
            lead.push({ id: "__mine__", label: mine })
        return lead.concat(categories)
    }
    readonly property var mineLabels: ({
        effects: qsTranslate("EffectBrowser", "My Effects"),
        colorfx: qsTranslate("EffectBrowser", "My Effects"),
        transitions: qsTranslate("TransitionsTab", "My Transitions"),
        sounds: qsTranslate("AudioEffectBrowser", "My Audio Effects"),
        effectTemplates: qsTranslate("EffectTemplateBrowser", "My presets")
    })

    readonly property string currentSubcategoryId: {
        const browser = root.browserFor(root.currentTabId)
        return browser && browser.activeCategory !== undefined ? browser.activeCategory : ""
    }

    // El nombre de la subcategoría abierta, en mayúsculas sobre el contenido, como Filmora.
    readonly property string currentSubcategoryTitle: {
        const browser = root.browserFor(root.currentTabId)
        const categories = browser && browser.categories ? browser.categories : []
        const found = categories.find(function(c) { return c.id === root.currentSubcategoryId })
        return (found ? found.label : root.tabLabel(root.currentTabId)).toLocaleUpperCase()
    }

    // Las filas del árbol: una por pestaña y, si está abierta, una por subcategoría.
    readonly property var treeRows: {
        const rows = []
        const tabs = root.sideTabs
        for (let i = 0; i < tabs.length; ++i) {
            const tabId = tabs[i]
            rows.push({ kind: "tab", tabId: tabId, categoryId: "" })
            if (root.expandedGroups[tabId] !== true)
                continue
            const categories = root.subcategoriesFor(tabId)
            for (let j = 0; j < categories.length; ++j) {
                const category = categories[j]
                rows.push({ kind: "sub", tabId: tabId, categoryId: category.id, label: category.label })
            }
        }
        return rows
    }

    // Abrir una pestaña despliega su grupo, como Filmora.
    function expandGroup(tabId) {
        if (root.expandedGroups[tabId] === true)
            return
        const next = {}
        for (const key in root.expandedGroups)
            next[key] = root.expandedGroups[key]
        next[tabId] = true
        root.expandedGroups = next
    }

    function toggleGroup(tabId) {
        const next = {}
        for (const key in root.expandedGroups)
            next[key] = root.expandedGroups[key]
        next[tabId] = !next[tabId]
        root.expandedGroups = next
    }

    // Elegir una subcategoría: abre su pestaña y le pasa la categoría al navegador.
    function chooseSubcategory(tabId, categoryId) {
        root.showTab(tabId)
        const browser = root.browserFor(tabId)
        if (browser && categoryId.length > 0) {
            browser.activeCategory = categoryId
            root.rememberTab(tabId, "category", categoryId)
        }
    }

    // The category a tab belongs to; Shortcuts (Help menu, F1) belongs to none.
    function categoryOfTab(tabId) {
        for (const category of root.categories) {
            if (category.tabs.indexOf(tabId) >= 0)
                return category
        }
        return null
    }

    readonly property var currentCategory: categoryOfTab(currentTabId)
    readonly property var sideTabs: currentCategory ? currentCategory.tabs : [currentTabId]
    // El árbol se ve siempre que no sea el panel en hoja (celular/Android): hasta una categoría de
    // una sola pestaña enseña sus subcategorías, como Filmora.
    readonly property bool showSideList: !root.sheetMode
    // The whole category row, for the window's default panel width (Main.qml).
    readonly property real categoryRowWidth: categoryRow.width
    readonly property real sideListWidth: showSideList ? 168 : 0

    // Coming back to a category opens the tab last used in it (Audio → Sound effects).
    property var lastTabInCategory: ({})

    function showCategory(categoryId) {
        const category = root.categories.find(c => c.id === categoryId)
        if (!category)
            return
        const last = root.lastTabInCategory[categoryId]
        root.showTab(last && category.tabs.indexOf(last) >= 0 ? last : category.tabs[0])
    }

    onCurrentTabIdChanged: {
        root.expandGroup(currentTabId)
        if (currentCategory)
            root.lastTabInCategory[currentCategory.id] = currentTabId
        // Opening Stock is seeing what is new there: the badge on its tab goes.
        if (currentTabId === "market" && Market.configured)
            Market.markNewsSeen()
    }

    // Per-tab view state that outlives the tab being unloaded, keyed by tabId. Plain
    // storage: tabs read it once on creation and write each change back.
    property var tabState: ({})

    function rememberTab(tabId, key, value) {
        if (!root.tabState[tabId])
            root.tabState[tabId] = {}
        root.tabState[tabId][key] = value
    }

    // Search text and category for the catalog browsers. A category that went away
    // while the tab was unloaded (addon removed) falls back to the tab's default.
    function restoreBrowserTab(tab, tabId) {
        const saved = root.tabState[tabId] || {}
        if (saved.search)
            tab.searchText = saved.search
        if (saved.category === undefined || !tab.categories)
            return
        if (saved.category === "__favorites__" || saved.category === "__mine__"
                || tab.categories.some(category => category.id === saved.category))
            tab.activeCategory = saved.category
    }

    // Fades the tab body in on a tab change instead of hard-cutting to it. Driven
    // as one property the bodies share, rather than fading the whole content
    // Column, so the panel header does not flash along with it. Fade-in only, not
    // a crossfade: the bodies are Column siblings, and overlapping two would
    // double-count height and jump the layout mid-transition.
    property real tabOpacity: 1.0

    onActiveTabChanged: {
        root.tabOpacity = 0
        tabFadeIn.restart()
    }

    NumberAnimation {
        id: tabFadeIn
        target: root
        property: "tabOpacity"
        from: 0.0
        to: 1.0
        duration: Theme.durationBase
        easing.type: Theme.easing
    }

    DropArea {
        id: assetDropArea
        anchors.fill: parent
        keys: ["text/uri-list"]
        onDropped: (drop) => {
            if (drop.hasUrls)
                root.importUrlsReporting(drop.urls, true)
        }
    }

    // Drag feedback. Dropping files onto the panel used to give no visual
    // confirmation that it was even a valid target.
    Rectangle {
        anchors.fill: parent
        z: 50
        radius: Theme.radiusMd
        color: Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.08)
        border.width: Theme.borderWidthFocus
        border.color: Theme.primary
        visible: opacity > 0
        opacity: assetDropArea.containsDrag ? 1 : 0

        Behavior on opacity {
            NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
        }

        EmptyState {
            anchors.centerIn: parent
            glyph: Theme.icons.upload
            title: qsTr("Drop to import")
            hint: qsTr("Video, audio and image files")
        }
    }

    // Import progress. Probing and thumbnailing a large selection blocks for a
    // while; the panel used to simply appear frozen.
    Rectangle {
        anchors.fill: parent
        z: 60
        color: Theme.panelBackground
        opacity: root.importing ? 0.92 : 0
        visible: opacity > 0

        Behavior on opacity {
            NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
        }

        EmptyState {
            anchors.centerIn: parent
            glyph: Theme.icons.spinner
            glyphSpinning: root.importing
            title: qsTr("Importing…")
            hint: qsTr("Reading media and generating thumbnails.")
        }
    }

    // Category row (Filmora/CapCut): Media, Stock, Audio, Titles… Each opens its group of tabs,
    // listed in the sidebar below. Scrolls sideways when the panel is narrow.
    // Hidden in sheetMode — AndroidBottomRail drives showTab() instead.
    Flickable {
        id: categoryBar
        width: parent.width
        height: root.sheetMode ? 0 : 54
        visible: !root.sheetMode
        contentWidth: categoryRow.width
        contentHeight: height
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        interactive: contentWidth > width
        flickableDirection: Flickable.HorizontalFlick

        Accessible.role: Accessible.PageTabList

        WheelHandler {
            acceptedDevices: PointerDevice.Mouse
            onWheel: (event) => {
                categoryBar.contentX = Math.max(0, Math.min(categoryBar.contentWidth - categoryBar.width,
                                                            categoryBar.contentX - event.angleDelta.y))
            }
        }

        Row {
            id: categoryRow
            height: parent.height
            leftPadding: Theme.spacingXs
            rightPadding: Theme.spacingXs

            Repeater {
                model: root.categories
                delegate: AbstractButton {
                    id: categoryButton
                    required property var modelData
                    readonly property bool current: !!root.currentCategory && root.currentCategory.id === modelData.id
                    // Stock says what is new in it since it was last opened.
                    readonly property bool hasNews: modelData.id === "market" && Market.configured
                                                    && Market.newsCount > 0 && !current
                    width: Math.max(54, categoryLabel.implicitWidth + Theme.spacingLg * 2)
                    height: categoryRow.height
                    hoverEnabled: true
                    focusPolicy: Qt.StrongFocus
                    onClicked: root.showCategory(modelData.id)

                    Accessible.role: Accessible.PageTab
                    Accessible.name: modelData.label
                    Accessible.checked: current

                    background: Rectangle {
                        anchors.fill: parent
                        anchors.margins: 3
                        radius: Theme.radiusSm
                        color: categoryButton.down ? Theme.panelMuted
                                                   : (categoryButton.hovered && !categoryButton.current ? Theme.panelAccent
                                                                                                        : "transparent")
                        border.width: categoryButton.visualFocus ? Theme.borderWidthFocus : 0
                        border.color: Theme.focusRing
                    }

                    contentItem: Item {
                        IconGlyph {
                            id: categoryGlyph
                            anchors.horizontalCenter: parent.horizontalCenter
                            y: 9
                            glyph: categoryButton.modelData.icon
                            iconSize: Theme.iconSizeBase
                            iconColor: categoryButton.current ? Theme.primary : Theme.mutedForeground
                        }

                        Text {
                            id: categoryLabel
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.top: categoryGlyph.bottom
                            anchors.topMargin: 4
                            text: categoryButton.modelData.label
                            color: categoryButton.current ? Theme.primary : Theme.foreground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                            font.weight: categoryButton.current ? Font.DemiBold : Font.Normal
                        }

                        Rectangle {
                            visible: categoryButton.hasNews
                            x: categoryGlyph.x + categoryGlyph.width - 4
                            y: categoryGlyph.y - 6
                            height: Theme.fontSizeXs + 4
                            width: Math.max(height, newsLabel.implicitWidth + 6)
                            radius: height / 2
                            color: Theme.primary
                            Text {
                                id: newsLabel
                                anchors.centerIn: parent
                                text: Market.newsCount > 99 ? "99+" : String(Market.newsCount)
                                color: Theme.primaryForeground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeXs - 1
                                font.weight: Font.DemiBold
                            }
                        }
                    }

                    ThemedToolTip {
                        text: Market.newsSummary
                        visible: categoryButton.hasNews && categoryButton.hovered
                    }

                    MouseArea {
                        anchors.fill: parent
                        acceptedButtons: Qt.NoButton
                        cursorShape: Qt.PointingHandCursor
                    }
                }
            }
        }
    }

    Rectangle {
        y: categoryBar.height
        width: parent.width
        height: root.sheetMode ? 0 : Theme.borderWidth
        visible: !root.sheetMode
        color: Theme.panelBorder
    }

    Row {
        y: categoryBar.height + (root.sheetMode ? 0 : Theme.borderWidth)
        width: parent.width
        height: parent.height - y
        spacing: 0

        // The tabs of the open category, with their names (Audio → Music, Sound effects, Speech,
        // Audio FX). Up/Down move between them once it has focus.
        Flickable {
            id: tabRail
            width: root.sideListWidth
            height: parent.height
            visible: root.showSideList
            contentWidth: width
            contentHeight: tabRailColumn.height
            clip: true
            boundsBehavior: Flickable.StopAtBounds
            interactive: contentHeight > height
            ScrollBar.vertical: AppScrollBar {}

            Accessible.role: Accessible.PageTabList

            function step(delta) {
                const tabs = root.sideTabs
                const at = tabs.indexOf(root.currentTabId)
                root.showTab(tabs[(at + delta + tabs.length) % tabs.length])
            }
            Keys.onUpPressed: function(event) {
                step(-1)
                event.accepted = true
            }
            Keys.onDownPressed: function(event) {
                step(1)
                event.accepted = true
            }

            Column {
                id: tabRailColumn
                width: parent.width
                topPadding: Theme.spacingSm
                spacing: 2

                // Qué se está viendo, en mayúsculas: la subcategoría elegida (Filmora lo pone
                // sobre el contenido; aquí encabeza el árbol, que es donde se elige).
                Text {
                    x: Theme.spacingMd
                    width: tabRailColumn.width - Theme.spacingMd * 2
                    topPadding: Theme.spacingXs
                    bottomPadding: Theme.spacingSm
                    text: root.currentSubcategoryTitle
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                    font.letterSpacing: 0.6
                    elide: Text.ElideRight
                }

                Repeater {
                    model: root.treeRows
                    delegate: AbstractButton {
                        id: treeRow
                        required property var modelData
                        readonly property bool isSub: modelData.kind === "sub"
                        readonly property bool current: treeRow.isSub
                            ? (root.currentTabId === modelData.tabId
                               && root.currentSubcategoryId === modelData.categoryId)
                            : root.currentTabId === modelData.tabId
                        readonly property bool open: root.expandedGroups[modelData.tabId] === true
                        // Una subcategoría de la pestaña que no está abierta se marca a medias.
                        x: Theme.spacingXs
                        width: tabRailColumn.width - Theme.spacingXs * 2
                        height: treeRow.isSub ? 26 : 32
                        hoverEnabled: true
                        focusPolicy: Qt.StrongFocus
                        onClicked: treeRow.isSub
                                   ? root.chooseSubcategory(treeRow.modelData.tabId, treeRow.modelData.categoryId)
                                   : root.showTab(treeRow.modelData.tabId)

                        Accessible.role: treeRow.isSub ? Accessible.ListItem : Accessible.PageTab
                        Accessible.name: treeRow.isSub ? treeRow.modelData.label
                                                       : root.tabLabel(treeRow.modelData.tabId)
                        Accessible.checked: treeRow.current

                        background: Rectangle {
                            radius: Theme.radiusSm
                            color: treeRow.current ? Theme.panelSecondaryBg
                                                   : (treeRow.hovered ? Theme.panelAccent : "transparent")
                            border.width: treeRow.visualFocus ? Theme.borderWidthFocus : 0
                            border.color: Theme.focusRing
                        }

                        contentItem: Row {
                            leftPadding: treeRow.isSub ? Theme.spacing2xl : Theme.spacingMd
                            spacing: Theme.spacingMd

                            // La flechita del grupo: solo en las pestañas que tienen subcategorías.
                            Item {
                                visible: !treeRow.isSub && root.subcategoriesFor(treeRow.modelData.tabId).length > 0
                                width: visible ? Theme.iconSizeSm : 0
                                height: visible ? Theme.iconSizeSm : 0
                                anchors.verticalCenter: parent.verticalCenter

                                IconGlyph {
                                    anchors.centerIn: parent
                                    glyph: treeRow.open ? Theme.icons.chevronDown : Theme.icons.chevronRight
                                    iconSize: Theme.iconSizeSm
                                    iconColor: Theme.mutedForeground
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    // La flechita abre y cierra; el resto de la fila abre la pestaña.
                                    anchors.margins: -Theme.spacingXs
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.toggleGroup(treeRow.modelData.tabId)
                                }
                            }

                            IconGlyph {
                                visible: !treeRow.isSub
                                anchors.verticalCenter: parent.verticalCenter
                                glyph: root.tabIcon(treeRow.modelData.tabId)
                                iconSize: Theme.iconSizeSm
                                iconColor: treeRow.current ? Theme.primary : Theme.mutedForeground
                            }

                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                width: parent.width - x - Theme.spacingSm
                                       - (treeAi.visible ? treeAi.width + parent.spacing : 0)
                                elide: Text.ElideRight
                                text: treeRow.isSub ? treeRow.modelData.label : root.tabLabel(treeRow.modelData.tabId)
                                color: treeRow.current ? Theme.foreground : Theme.mutedForeground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeSm
                                font.weight: treeRow.current ? Font.Medium : Font.Normal
                            }

                            AiBadge {
                                id: treeAi
                                anchors.verticalCenter: parent.verticalCenter
                                visible: !treeRow.isSub && !!root.aiInfo[treeRow.modelData.tabId]
                                info: root.aiInfo[treeRow.modelData.tabId] || ""
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            acceptedButtons: Qt.NoButton
                            cursorShape: Qt.PointingHandCursor
                        }
                    }
                }

            }
        }

        Rectangle {
            width: root.showSideList ? Theme.borderWidth : 0
            height: parent.height
            visible: root.showSideList
            color: Theme.panelBorder
        }

        Column {
            id: assetsContent
            width: parent.width - (root.showSideList ? root.sideListWidth + Theme.borderWidth : 0)
            height: parent.height

            Rectangle {
                id: assetsHeader
                // In a sheet the title is the sheet's own, so this bar only earns its height when
                // the tab has actions to put in it (media import); otherwise it was an empty band
                // between the sheet title and the content. The catalog tabs never show it: their
                // search field names the tab and carries its actions.
                readonly property string tabId: tabsModel.get(root.activeTab).tabId
                readonly property bool hasActions: kindsForTab(tabId).length > 0
                readonly property bool searchBarTab: ["text", "stickers", "shapes", "effects", "templates", "effectTemplates",
                                                      "transitions", "sounds", "filters", "colorfx"].indexOf(tabId) >= 0
                width: parent.width
                height: searchBarTab || (root.sheetMode && !hasActions) ? 0 : Theme.panelHeaderHeight
                visible: height > 0
                // Matches the surrounding PanelFrame; it used to paint the app
                // background, so the header read as a different surface than the
                // panel it belongs to.
                color: Theme.panelBackground

                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: Theme.borderWidth
                    color: Theme.panelBorder
                }

                // Labels measured on their own so the compact switch does not depend on the row it
                // resizes (that would be a binding loop).
                TextMetrics {
                    id: newFolderLabelMetrics
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSm
                    text: qsTr("New Folder")
                }

                TextMetrics {
                    id: importLabelMetrics
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSm
                    text: qsTr("Import")
                }

                // Width the header needs to show the title and both labelled buttons. In a narrow
                // panel (or a language with longer labels) the buttons drop their text instead of
                // sliding over the title.
                readonly property real labelledButtonExtra: Theme.spacing2xl - Theme.spacingXs - Theme.spacingXl
                                                            + Theme.spacingMd
                readonly property real fullHeaderWidth: Theme.pagePadding + headerTitle.implicitWidth + Theme.spacingLg
                    + 2 * (Theme.spacingXl * 2 + Theme.iconSizeMd + labelledButtonExtra) + 6
                    + newFolderLabelMetrics.advanceWidth + importLabelMetrics.advanceWidth
                    + Theme.spacingXl * 2 + Theme.iconSizeMd + 6
                    + (Theme.touchUi ? 0 : Theme.borderWidth * 3 + Theme.spacingLg * 2 + Theme.iconSizeSm) + 8
                readonly property bool compactActions: width < fullHeaderWidth

                Text {
                    id: headerTitle
                    anchors.left: parent.left
                    anchors.leftMargin: Theme.pagePadding
                    anchors.verticalCenter: parent.verticalCenter
                    width: Math.max(0, Math.min(implicitWidth,
                                                (mediaActions.visible ? mediaActions.x : parent.width)
                                                - Theme.pagePadding - Theme.spacingLg))
                    elide: Text.ElideRight
                    // Sheet chrome already shows the tab title.
                    visible: !root.sheetMode
                    text: tabLabels[tabsModel.get(root.activeTab).tabId]
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSm
                }

                Row {
                    id: mediaActions
                    anchors.right: parent.right
                    anchors.rightMargin: 8
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 6
                    visible: kindsForTab(tabsModel.get(root.activeTab).tabId).length > 0

                    ThemedButton {
                        text: assetsHeader.compactActions ? "" : qsTr("New Folder")
                        rightPadding: assetsHeader.compactActions ? Theme.spacingXl : Theme.spacing2xl - Theme.spacingXs
                        variant: "ghost"
                        glyph: Theme.icons.folder
                        tooltip: qsTr("Create a new folder here")
                        anchors.verticalCenter: parent.verticalCenter
                        onClicked: newFolderDialog.open()
                    }

                    // After Effects' New Composition (0.26): a click makes an empty one and opens
                    // it; media dropped on it makes one holding that media.
                    ThemedButton {
                        id: newCompositionButton
                        text: ""
                        variant: newCompositionDrop.containsDrag ? "secondary" : "ghost"
                        glyph: Theme.icons.layers
                        tooltip: qsTr("New composition (drop media here to make one with it)")
                        anchors.verticalCenter: parent.verticalCenter
                        onClicked: EditorState.newComposition("")
                        DropArea {
                            id: newCompositionDrop
                            anchors.fill: parent
                            keys: ["text/plain"]
                            onDropped: drop => {
                                const index = parseInt(drop.text)
                                if (isNaN(index))
                                    return
                                const id = AssetLibrary.assetIdAt(index)
                                if (id.length > 0) {
                                    drop.accept()
                                    EditorState.newCompositionFromAssets([id])
                                }
                            }
                        }
                    }

                    // Split button: the left half imports files, the chevron opens the
                    // folder variant. Both halves share one bordered box so the header
                    // reads as two actions, not three competing buttons.
                    Rectangle {
                        id: importSplit
                        anchors.verticalCenter: parent.verticalCenter
                        width: importFilesHalf.width
                               + (importMenuHalf.visible ? importSplitDivider.width + importMenuHalf.width : 0)
                        height: Theme.controlHeight
                        radius: Theme.radiusSm
                        color: "transparent"
                        border.width: Theme.borderWidth
                        border.color: Theme.panelBorder
                        opacity: root.importing ? 0.6 : 1

                        Row {
                            anchors.fill: parent
                            spacing: 0

                            ThemedButton {
                                id: importFilesHalf
                                text: assetsHeader.compactActions ? "" : qsTr("Import")
                                rightPadding: assetsHeader.compactActions ? Theme.spacingXl : Theme.spacing2xl - Theme.spacingXs
                                variant: "ghost"
                                flat: true
                                radius: Theme.radiusXs
                                glyph: Theme.icons.upload
                                tooltip: qsTr("Import video, audio or image files")
                                enabled: !root.importing
                                height: parent.height - Theme.borderWidth * 2
                                anchors.verticalCenter: parent.verticalCenter
                                onClicked: root.importMedia()
                            }

                            Rectangle {
                                id: importSplitDivider
                                width: Theme.borderWidth
                                height: parent.height - Theme.spacingLg
                                anchors.verticalCenter: parent.verticalCenter
                                color: Theme.panelBorder
                                visible: importMenuHalf.visible
                            }

                            ThemedButton {
                                id: importMenuHalf
                                variant: "ghost"
                                flat: true
                                radius: Theme.radiusXs
                                glyph: Theme.icons.chevronDown
                                glyphSize: Theme.iconSizeSm
                                leftPadding: Theme.spacingLg
                                rightPadding: Theme.spacingLg
                                tooltip: qsTr("More import options")
                                enabled: !root.importing
                                visible: !Theme.touchUi
                                height: parent.height - Theme.borderWidth * 2
                                anchors.verticalCenter: parent.verticalCenter
                                onClicked: importMenu.popup(0, importSplit.height + Theme.spacingSm)
                            }
                        }

                        ThemedContextMenu {
                            id: importMenu
                            minimumWidth: 220

                            ThemedMenuItem {
                                text: qsTr("Import Files…")
                                icon.name: Theme.icons.upload
                                onTriggered: root.importMedia()
                            }

                            ThemedMenuItem {
                                visible: FileDialogs.supportsDirectoryPicker()
                                height: visible ? implicitHeight : 0
                                text: qsTr("Import Folder…")
                                icon.name: Theme.icons.folderInput
                                onTriggered: root.importFolder()
                            }

                            ThemedMenuSeparator {
                                visible: FileDialogs.supportsDirectoryPicker()
                                height: visible ? implicitHeight : 0
                            }

                            ThemedMenuItem {
                                visible: FileDialogs.supportsDirectoryPicker()
                                height: visible ? implicitHeight : 0
                                text: qsTr("Collect Media to Folder…")
                                icon.name: Theme.icons.folderOutput
                                enabled: !EditorState.projectFile.collectingMedia
                                onTriggered: root.collectMedia()
                            }
                        }
                    }
                }
            }

            EmojiPicker {
                id: emojiPicker
                // Hangs off the stickers search bar's + at the panel's right edge, and slides back
                // rather than running off-window when the panel is dragged narrow.
                x: Math.max(-root.sideListWidth, assetsContent.width - width - Theme.pagePadding)
                y: assetsHeader.height + Theme.pagePadding + Theme.controlHeight + 4
                onAddonManagerRequested: root.Window.window.openAddonManager("stickers")
                onAdded: root.addCompleted()
            }

            // Only the open tab is instantiated; what should outlive a switch is kept in
            // tabState below. Scroll position is not kept.
            Loader {
                id: textLoader
                active: root.currentTabId === "text"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    TextAssetsTab {
                        panelDriven: !root.sheetMode
                        id: textTab
                        Component.onCompleted: {
                            const saved = root.tabState["text"] || {}
                            if (saved.section)
                                section = saved.section
                        }
                        onSectionChanged: root.rememberTab("text", "section", section)
                        onAdded: root.addCompleted()
                        Connections {
                            target: root
                            function onTextSectionRequested(requested) { textTab.section = requested }
                        }
                    }
                }
            }

            Loader {
                id: subtitlesLoader
                active: root.currentTabId === "subtitles"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    SubtitlesTab {
                        panelDriven: !root.sheetMode
                        onAdded: root.addCompleted()
                    }
                }
            }

            Loader {
                id: musicLoader
                active: root.currentTabId === "music"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    SoundEffectsTab {
                        panelDriven: !root.sheetMode
                        music: true
                        onAdded: root.addCompleted()
                    }
                }
            }

            Loader {
                id: sfxLoader
                active: root.currentTabId === "sfx"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    SoundEffectsTab {
                        panelDriven: !root.sheetMode
                        onAdded: root.addCompleted()
                    }
                }
            }

            Loader {
                id: speechLoader
                active: root.currentTabId === "speech"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    SpeechTab {
                        panelDriven: !root.sheetMode
                    }
                }
            }

            Loader {
                id: soundsLoader
                active: root.currentTabId === "sounds"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    SoundsTab {
                        panelDriven: !root.sheetMode
                        Component.onCompleted: root.restoreBrowserTab(this, "sounds")
                        onSearchTextChanged: root.rememberTab("sounds", "search", searchText)
                        onActiveCategoryChanged: root.rememberTab("sounds", "category", activeCategory)
                    }
                }
            }

            Loader {
                id: stickersLoader
                active: root.currentTabId === "stickers"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    StickersTab {
                        panelDriven: !root.sheetMode
                        emojiPickerOpen: emojiPicker.opened
                        onEmojiPickerRequested: emojiPicker.opened ? emojiPicker.close() : emojiPicker.open()
                        onAdded: root.addCompleted()
                        Component.onCompleted: root.restoreBrowserTab(this, "stickers")
                        onSearchTextChanged: root.rememberTab("stickers", "search", searchText)
                        onActiveCategoryChanged: root.rememberTab("stickers", "category", activeCategory)
                    }
                }
            }

            Loader {
                id: shapesLoader
                active: root.currentTabId === "shapes"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    ShapesTab {
                        panelDriven: !root.sheetMode
                        onAdded: root.addCompleted()
                        Component.onCompleted: root.restoreBrowserTab(this, "shapes")
                        onSearchTextChanged: root.rememberTab("shapes", "search", searchText)
                        onActiveCategoryChanged: root.rememberTab("shapes", "category", activeCategory)
                    }
                }
            }

            Loader {
                id: scenesLoader
                active: root.currentTabId === "scenes"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    ScenesTab {
                        panelDriven: !root.sheetMode
                        Component.onCompleted: {
                            const saved = root.tabState["scenes"] || {}
                            if (saved.sortByScore !== undefined)
                                sortByScore = saved.sortByScore
                            if (saved.labelFilter !== undefined)
                                labelFilter = saved.labelFilter
                        }
                        onSortByScoreChanged: root.rememberTab("scenes", "sortByScore", sortByScore)
                        onLabelFilterChanged: root.rememberTab("scenes", "labelFilter", labelFilter)
                    }
                }
            }

            Loader {
                id: shortcutsLoader
                active: root.currentTabId === "shortcuts"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    ShortcutsTab {
                        panelDriven: !root.sheetMode
                        Component.onCompleted: root.restoreBrowserTab(this, "shortcuts")
                        onSearchTextChanged: root.rememberTab("shortcuts", "search", searchText)
                    }
                }
            }

            Loader {
                id: masksLoader
                active: root.currentTabId === "masks"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    MasksTab {
                        panelDriven: !root.sheetMode
                        onAdded: root.addCompleted()
                    }
                }
            }

            Loader {
                id: effectsLoader
                active: root.currentTabId === "effects"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    EffectBrowser {
                        panelDriven: !root.sheetMode
                        Component.onCompleted: root.restoreBrowserTab(this, "effects")
                        onSearchTextChanged: root.rememberTab("effects", "search", searchText)
                        onActiveCategoryChanged: root.rememberTab("effects", "category", activeCategory)
                    }
                }
            }

            Loader {
                id: filtersLoader
                active: root.currentTabId === "filters"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    FiltersTab {
                        panelDriven: !root.sheetMode
                        Component.onCompleted: {
                            const saved = root.tabState["filters"] || {}
                            if (saved.search)
                                searchText = saved.search
                            if (saved.category)
                                activeCategory = saved.category
                        }
                        onSearchTextChanged: root.rememberTab("filters", "search", searchText)
                        onActiveCategoryChanged: root.rememberTab("filters", "category", activeCategory)
                    }
                }
            }

            // Filters › Color effects: the Effects browser opened on its Color category.
            Loader {
                id: colorfxLoader
                active: root.currentTabId === "colorfx"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    EffectBrowser {
                        panelDriven: !root.sheetMode
                        // Stock's looks here: their Trending and their categories.
                        stockType: "look"
                        Component.onCompleted: {
                            const saved = root.tabState["colorfx"] || {}
                            activeCategory = saved.category !== undefined ? saved.category : "color"
                            if (saved.search)
                                searchText = saved.search
                        }
                        onSearchTextChanged: root.rememberTab("colorfx", "search", searchText)
                        onActiveCategoryChanged: root.rememberTab("colorfx", "category", activeCategory)
                    }
                }
            }

            Loader {
                id: templatesLoader
                active: root.currentTabId === "templates"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    TemplatesTab {
                        panelDriven: !root.sheetMode
                        // On the desktop this tab is only the scene templates; the effect ones
                        // are the next sidebar entry. The phone sheet keeps both behind chips.
                        showModeChips: root.sheetMode
                        Component.onCompleted: {
                            const saved = root.tabState["templates"] || {}
                            if (saved.mode && root.sheetMode)
                                mode = saved.mode
                            if (saved.search)
                                searchText = saved.search
                            if (saved.category)
                                activeCategory = saved.category
                        }
                        onModeChanged: if (root.sheetMode) root.rememberTab("templates", "mode", mode)
                        onSearchTextChanged: root.rememberTab("templates", "search", searchText)
                        onActiveCategoryChanged: root.rememberTab("templates", "category", activeCategory)
                    }
                }
            }

            // Templates › Effect templates (music-synced effects for a clip already there).
            Loader {
                id: effectTemplatesLoader
                active: root.currentTabId === "effectTemplates"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    TemplatesTab {
                        panelDriven: !root.sheetMode
                        mode: "effects"
                        showModeChips: false
                        Component.onCompleted: {
                            const saved = root.tabState["effectTemplates"] || {}
                            if (saved.search)
                                searchText = saved.search
                            if (saved.category)
                                activeCategory = saved.category
                        }
                        onSearchTextChanged: root.rememberTab("effectTemplates", "search", searchText)
                        onActiveCategoryChanged: root.rememberTab("effectTemplates", "category", activeCategory)
                    }
                }
            }

            Loader {
                id: transitionsLoader
                active: root.currentTabId === "transitions"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    TransitionsTab {
                        panelDriven: !root.sheetMode
                        Component.onCompleted: root.restoreBrowserTab(this, "transitions")
                        onSearchTextChanged: root.rememberTab("transitions", "search", searchText)
                        onActiveCategoryChanged: root.rememberTab("transitions", "category", activeCategory)
                    }
                }
            }

            // Shared media browser used by the Media tab.
            Loader {
                id: mediaLoader
                active: root.kindsForTab(root.currentTabId).length > 0
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    MediaAssetsTab {
                        importing: root.importing
                        assetVisibleFn: function(kind) { return root.assetVisible(kind) }
                        onPreviewRequested: (assetIndex) => {
                            if (typeof Window !== "undefined" && Window.window && Window.window.openMediaPreview)
                                Window.window.openMediaPreview(assetIndex)
                        }
                        onAddToTimelineRequested: (assetIds) => root.requestAddToTimeline(assetIds)
                        onRemoveRequested: (assetIds) => root.requestRemoveAsset(assetIds)
                        onReplaceRequested: (assetIndex) => root.requestReplaceAsset(assetIndex)
                        onFindMissingRequested: (assetId, path) => root.findMissingAsset(assetId, path)
                        onRenameRequested: (assetIndex) => root.requestRenameAsset(assetIndex)
                        onExportRequested: (assetIndex) => root.requestExportAsset(assetIndex)
                        onSaveAsRequested: (assetIndex) => root.requestSaveAssetAs(assetIndex)
                        onImportRequested: root.importMedia()
                        onImportFolderRequested: root.importFolder()
                        onMoveToFolderRequested: (assetIds) => root.requestMoveAssetToFolder(assetIds)
                        onFolderRenameRequested: (folderId, folderName) => root.requestRenameFolder(folderId, folderName)
                        onFolderMoveRequested: (folderId) => root.requestMoveFolder(folderId)

                        Component.onCompleted: {
                            const saved = root.tabState["media"] || {}
                            if (saved.search)
                                searchText = saved.search
                            if (saved.sortByKind !== undefined)
                                sortByKind = saved.sortByKind
                            if (saved.expandedFolderIds)
                                expandedFolderIds = saved.expandedFolderIds
                            if (saved.selectedAssetIds)
                                selectedAssetIds = saved.selectedAssetIds
                            if (saved.selectionAnchorId)
                                selectionAnchorId = saved.selectionAnchorId
                            // Assets removed while the tab was unloaded must not come back selected.
                            pruneSelection()
                        }
                        onSearchTextChanged: root.rememberTab("media", "search", searchText)
                        onSortByKindChanged: root.rememberTab("media", "sortByKind", sortByKind)
                        onExpandedFolderIdsChanged: root.rememberTab("media", "expandedFolderIds", expandedFolderIds)
                        onSelectedAssetIdsChanged: root.rememberTab("media", "selectedAssetIds", selectedAssetIds)
                        onSelectionAnchorIdChanged: root.rememberTab("media", "selectionAnchorId", selectionAnchorId)
                    }
                }
            }

            Loader {
                id: marketLoader
                active: root.currentTabId === "market"
                visible: active
                width: parent.width
                height: parent.height - assetsHeader.height
                opacity: root.tabOpacity
                sourceComponent: Component {
                    MarketTab {
                        panelDriven: !root.sheetMode
                        // Filter values are not restored: the filter fields and dropdowns
                        // don't read them back, so restored filters would be invisible.
                        Component.onCompleted: {
                            const saved = root.tabState["market"] || {}
                            if (saved.search)
                                searchText = saved.search
                            if (saved.submittedQuery)
                                submittedQuery = saved.submittedQuery
                            // "assets" is Drift's own pack, which Flip Studio does not have.
                            if (saved.section && saved.section !== "assets" && Market.authenticated)
                                section = saved.section
                        }
                        onSearchTextChanged: root.rememberTab("market", "search", searchText)
                        onSubmittedQueryChanged: root.rememberTab("market", "submittedQuery", submittedQuery)
                        onSectionChanged: root.rememberTab("market", "section", section)
                    }
                }
            }
        }
    }
}
