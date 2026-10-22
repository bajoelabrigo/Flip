import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift
import ".."

// CapCut's Tracking tab: the selected text, sticker or picture follows an object or a face in the
// video under it. None / Object / Face, then Direction, Scale and Distance. While the tab is open
// the preview offers what can be followed (TrackingOverlay): the scanned faces, or the objects the
// detector finds and a box drawn by hand. The result is ordinary keyframes; Scale and Distance
// re-bake it without analysing again.
Item {
    id: root

    property int clipDataRevision: 0
    readonly property var tracking: EditorState.motionTrack
    readonly property int trackIndex: EditorState.selectedTrack
    readonly property int clipIndex: EditorState.selectedClip

    readonly property var source: {
        void root.clipDataRevision
        void EditorState.playheadSeconds
        return root.tracking.sourceFor(root.trackIndex, root.clipIndex)
    }
    readonly property var stored: {
        void root.clipDataRevision
        void root.tracking.revision
        return root.tracking.info(root.trackIndex, root.clipIndex)
    }
    readonly property bool hasTrack: !!root.stored.has
    readonly property string clipKind: {
        void root.clipDataRevision
        return (EditorState.selectedClipData && EditorState.selectedClipData.kind) || ""
    }
    readonly property bool isMedia: root.clipKind === "video" || root.clipKind === "image"

    // "none", "object" or "face": what the cards show. Follows the stored track until changed.
    property string mode: "none"
    // Hiding something in this clip instead ("face" or "object"): its own pickers on the preview.
    property string hideMode: ""
    property bool followScale: true
    property bool keepDistance: true
    property int directionIndex: 0
    readonly property var directions: ["both", "forward", "backward"]

    function syncFromStored() {
        root.hideMode = ""
        root.tracking.pick = ({})
        root.tracking.clearObjectTargets()
        if (root.hasTrack) {
            root.mode = root.stored.mode
            root.followScale = !!root.stored.followScale
            root.keepDistance = !!root.stored.keepDistance
            root.directionIndex = Math.max(0, root.directions.indexOf(root.stored.direction))
        } else {
            root.mode = "none"
        }
    }
    Component.onCompleted: syncFromStored()
    onVisibleChanged: if (!visible) root.tracking.clearObjectTargets()

    Connections {
        target: EditorState
        function onSelectionChanged() {
            root.clipDataRevision++
            root.syncFromStored()
        }
        function onSelectedClipDataChanged() { root.clipDataRevision++ }
        function onTracksChanged() { root.clipDataRevision++ }
    }

    // The preview shows the faces or the objects to pick while this tab is open.
    Binding {
        target: root.tracking
        property: "chooser"
        value: root.tracking.busy ? "" : root.hideMode !== "" ? "hide-" + root.hideMode
                                                       : root.mode === "none" ? "" : root.mode
        when: root.visible
        restoreMode: Binding.RestoreValue
    }

    function start() {
        const pick = root.tracking.pick || {}
        const options = {
            mode: root.mode,
            followScale: root.followScale,
            keepDistance: root.keepDistance,
            direction: root.directions[root.directionIndex]
        }
        if (root.mode === "face" && pick.faceSlot !== undefined)
            options.faceSlot = pick.faceSlot
        if (root.mode === "object" && pick.region) {
            options.region = pick.region
            options.classId = pick.classId !== undefined ? pick.classId : -1
        }
        root.tracking.trackWith(root.trackIndex, root.clipIndex, options)
    }

    height: contentCol.height
    implicitHeight: contentCol.height

    Column {
        id: contentCol
        width: root.width
        spacing: Theme.spacingLg

        Item {
            width: parent.width
            height: titleText.implicitHeight
            Text {
                id: titleText
                text: qsTr("Tracking")
                color: Theme.panelForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                font.weight: Font.DemiBold
            }
            IconButton {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                visible: root.hasTrack && !root.tracking.busy
                glyph: Theme.icons.refresh
                variant: "ghost"
                buttonSize: Theme.controlHeightSm
                iconSize: 14
                tooltip: qsTr("Remove tracking")
                onClicked: {
                    root.tracking.clear(root.trackIndex, root.clipIndex)
                    root.mode = "none"
                }
            }
        }

        // None / Object / Face, as cards.
        Row {
            spacing: Theme.spacingMd
            enabled: !root.tracking.busy
            Repeater {
                model: [
                    { id: "none", label: qsTr("None"), glyph: Theme.icons.ban },
                    { id: "object", label: qsTr("Object"), glyph: Theme.icons.locateFixed },
                    { id: "face", label: qsTr("Face"), glyph: Theme.icons.smile }
                ]
                delegate: Column {
                    id: card
                    required property var modelData
                    readonly property bool selected: root.mode === modelData.id
                    spacing: Theme.spacingXs
                    Rectangle {
                        width: 64
                        height: 64
                        radius: Theme.radiusMd
                        color: cardHover.hovered ? Theme.popoverHover : Theme.panelAccent
                        border.width: card.selected ? Theme.borderWidthFocus : Theme.borderWidth
                        border.color: card.selected ? Theme.primary : Theme.panelSecondaryBorder
                        IconGlyph {
                            anchors.centerIn: parent
                            glyph: card.modelData.glyph
                            iconSize: Theme.iconSizeLg
                            iconColor: card.selected ? Theme.primary : Theme.panelForeground
                        }
                        HoverHandler { id: cardHover; cursorShape: Qt.PointingHandCursor }
                        TapHandler {
                            onTapped: {
                                if (card.modelData.id === "none" && root.hasTrack)
                                    root.tracking.clear(root.trackIndex, root.clipIndex)
                                root.tracking.pick = ({})
                                root.tracking.clearObjectTargets()
                                root.hideMode = ""
                                root.mode = card.modelData.id
                            }
                        }
                    }
                    Text {
                        width: 64
                        horizontalAlignment: Text.AlignHCenter
                        text: card.modelData.label
                        elide: Text.ElideRight
                        color: card.selected ? Theme.panelForeground : Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                }
            }
        }

        // Why it cannot follow anything here (no video under it), or what it will follow.
        Text {
            width: parent.width
            visible: root.mode !== "none"
            wrapMode: Text.WordWrap
            text: !root.source.ok ? (root.source.reason || "")
                  : root.mode === "face"
                    ? (root.source.hasFaces
                       ? qsTr("Click the face to follow on the preview (by default, the one nearest the element).")
                       : qsTr("The faces in “%1” are scanned first, then it follows the one nearest the element.").arg(root.source.source))
                    : qsTr("Pick an object on the preview or draw a box around it. With nothing picked, it follows what the element covers in “%1”.").arg(root.source.source)
            color: root.source.ok ? Theme.mutedForeground : Theme.warning
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }

        // Objects: find them with the detector (an extra), or draw a box on the preview.
        Row {
            spacing: Theme.spacingSm
            visible: root.mode === "object" && root.source.ok && !root.tracking.busy
            ThemedButton {
                visible: root.tracking.objectModelReady()
                text: root.tracking.detectingObjects ? qsTr("Looking…") : qsTr("Detect objects")
                glyph: Theme.icons.sparkles
                enabled: !root.tracking.detectingObjects
                tooltip: qsTr("Find people, animals, vehicles and other things at the playhead")
                onClicked: root.tracking.detectObjects(root.trackIndex, root.clipIndex)
            }
            ThemedButton {
                visible: !root.tracking.objectModelReady()
                variant: "ghost"
                text: qsTr("Get object detection")
                glyph: Theme.icons.download
                tooltip: qsTr("Install the “Object tracking” extra to find objects automatically")
                onClicked: root.Window.window.openAddonManager("object-model")
            }
            ThemedButton {
                visible: !!(root.tracking.pick && root.tracking.pick.region)
                variant: "ghost"
                text: qsTr("Clear pick")
                onClicked: root.tracking.pick = ({})
            }
        }

        // Direction, Scale and Distance.
        Column {
            width: parent.width
            spacing: Theme.spacingMd
            visible: root.mode !== "none"
            enabled: !root.tracking.busy

            Row {
                width: parent.width
                spacing: Theme.spacingMd
                Text {
                    width: 80
                    anchors.verticalCenter: parent.verticalCenter
                    text: qsTr("Direction")
                    color: Theme.panelForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                }
                ThemedComboBox {
                    width: parent.width - 80 - parent.spacing
                    model: [qsTr("Both"), qsTr("Forward"), qsTr("Backward")]
                    currentIndex: root.directionIndex
                    tooltip: qsTr("Follow from the playhead to both ends of the clip, or only one way")
                    onActivated: (index) => root.directionIndex = index
                }
            }

            ThemedSwitch {
                width: parent.width
                text: qsTr("Scale — grow and shrink with what it follows")
                checked: root.followScale
                onToggled: {
                    root.followScale = checked
                    if (root.hasTrack)
                        root.tracking.setOption(root.trackIndex, root.clipIndex, "followScale", checked)
                }
            }
            ThemedSwitch {
                width: parent.width
                text: qsTr("Distance — keep where it is next to what it follows")
                checked: root.keepDistance
                tooltip: qsTr("Off: the element sits right on top of what it follows")
                onToggled: {
                    root.keepDistance = checked
                    if (root.hasTrack)
                        root.tracking.setOption(root.trackIndex, root.clipIndex, "keepDistance", checked)
                }
            }
        }

        // The job's progress while it runs, with a way out.
        Column {
            width: parent.width
            spacing: Theme.spacingXs
            visible: root.tracking.busy
            Row {
                width: parent.width
                spacing: Theme.spacingSm
                ThemedProgressBar {
                    width: parent.width - cancelButton.width - parent.spacing
                    anchors.verticalCenter: parent.verticalCenter
                    value: root.tracking.progress
                }
                ThemedButton {
                    id: cancelButton
                    variant: "ghost"
                    text: qsTr("Cancel")
                    onClicked: root.tracking.cancel()
                }
            }
            Text {
                width: parent.width
                text: root.tracking.status
                elide: Text.ElideRight
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
        }

        Row {
            spacing: Theme.spacingSm
            visible: root.mode !== "none" && !root.tracking.busy
            ThemedButton {
                variant: "primary"
                text: root.hasTrack ? qsTr("Track again from here") : qsTr("Start tracking")
                glyph: Theme.icons.locateFixed
                enabled: root.source.ok
                tooltip: qsTr("Follows from the playhead; the element keeps its place against what it follows")
                onClicked: root.start()
            }
            ThemedButton {
                visible: root.hasTrack
                variant: "ghost"
                text: qsTr("Realign")
                tooltip: qsTr("After moving, trimming or speeding up the video: put the path back on it without analysing again")
                onClicked: root.tracking.realign(root.trackIndex, root.clipIndex)
            }
        }

        // CapCut's Mosaic: hide a face of this clip, the mask following it through the clip.
        Column {
            width: parent.width
            spacing: Theme.spacingSm
            visible: root.isMedia && !root.tracking.busy
            Text {
                text: qsTr("Hide")
                color: Theme.panelForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                font.weight: Font.DemiBold
            }
            // A face (from the face scan) or an object (picked, or a box drawn on the preview).
            Row {
                spacing: Theme.spacingSm
                ThemedChip {
                    text: qsTr("A face")
                    variant: "outline"
                    selected: root.hideMode === "face"
                    onClicked: {
                        root.tracking.pick = ({})
                        root.tracking.clearObjectTargets()
                        root.mode = "none"
                        root.hideMode = "face"
                    }
                }
                ThemedChip {
                    text: qsTr("An object")
                    variant: "outline"
                    selected: root.hideMode === "object"
                    onClicked: {
                        root.tracking.pick = ({})
                        root.mode = "none"
                        root.hideMode = "object"
                    }
                }
            }
            Text {
                width: parent.width
                visible: root.hideMode !== ""
                wrapMode: Text.WordWrap
                text: root.hideMode === "face"
                      ? qsTr("Click the face to hide on the preview (by default, the one nearest the middle). It is covered for the whole clip, following it; the layer goes right above the clip.")
                      : qsTr("Pick an object on the preview or draw a box around it. It is covered for the whole clip, following it; the layer goes right above the clip.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
            ThemedButton {
                visible: root.hideMode === "object" && root.tracking.objectModelReady()
                text: root.tracking.detectingObjects ? qsTr("Looking…") : qsTr("Detect objects")
                glyph: Theme.icons.sparkles
                enabled: !root.tracking.detectingObjects
                onClicked: root.tracking.detectObjects(root.trackIndex, root.clipIndex)
            }
            Row {
                spacing: Theme.spacingSm
                visible: root.hideMode !== ""
                Repeater {
                    model: [{ style: "pixelate", label: qsTr("Pixelate") }, { style: "blur", label: qsTr("Blur") }]
                    delegate: ThemedButton {
                        required property var modelData
                        text: modelData.label
                        glyph: root.hideMode === "face" ? Theme.icons.smile : Theme.icons.locateFixed
                        enabled: root.hideMode === "face" || !!(root.tracking.pick && root.tracking.pick.region)
                        onClicked: {
                            const pick = root.tracking.pick || {}
                            if (root.hideMode === "face")
                                root.tracking.blurFace(root.trackIndex, root.clipIndex, modelData.style,
                                                       pick.faceSlot !== undefined ? pick.faceSlot : -1)
                            else
                                root.tracking.hideObject(root.trackIndex, root.clipIndex, modelData.style, pick.region,
                                                         pick.classId !== undefined ? pick.classId : -1)
                        }
                    }
                }
            }
        }

        // What the stored tracking found.
        Text {
            width: parent.width
            visible: root.hasTrack && !root.tracking.busy
            wrapMode: Text.WordWrap
            text: root.stored.sourceMissing
                  ? qsTr("The video it followed is no longer in the project.")
                  : root.stored.sourceChanged
                    ? qsTr("The video it followed was replaced: track again so the path fits it.")
                    : root.stored.lost > 0
                      ? qsTr("Followed in %1 frames; lost in %2. Where it was lost, the element glides between the frames it was found in.").arg(root.stored.samples - root.stored.lost).arg(root.stored.lost)
                      : qsTr("Followed in all %1 frames.").arg(root.stored.samples)
            color: root.stored.sourceMissing || root.stored.sourceChanged ? Theme.warning : Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }
    }
}
