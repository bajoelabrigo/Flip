import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// Fixed left-hand track header column: per-track mute/hide/clip-display toggles,
// name, reorder-by-drag handle and the track context menu. Owns the
// track-drag state; the panel only supplies the track list and vertical scroll.
Item {
    id: root

    // Track model (EditorState.tracks) and the timeline's live vertical scroll,
    // so headers stay aligned with their rows.
    property var tracks: []
    property real contentY: 0
    // Desktop passes EditorState.preferences.trackLabelsWidth; Android a narrower fixed value.
    property real labelsWidth: Theme.trackLabelsWidth
    // Phone: grip + mute/hide only (no type glyph / waveform / name band).
    property bool compact: false
    // Touch shell: reorder has to be asked for, and the context menu needs a
    // route that is not the right mouse button.
    property bool touchMode: false
    // The hold-to-reorder / hold-for-menu gestures, which a touchscreen needs even when
    // the desktop layout is showing.
    readonly property bool touchHold: touchMode || Theme.touchInput
    // Desktop: a handle on the right edge drags EditorState.preferences.trackLabelsWidth.
    property bool resizable: false

    // Transform layer brackets. Desktop reserves a gutter on the left for them (one indent per
    // nesting level); the compact header draws them over the grip instead.
    readonly property int bracketLevels: {
        let levels = 0
        for (let i = 0; i < tracks.length; ++i) {
            if (tracks[i].isTransformLayer)
                levels = Math.max(levels, (tracks[i].spanDepth || 0) + 1)
        }
        return levels
    }
    readonly property real bracketIndent: compact ? 4 : 8
    property real bracketGutter: compact ? 0 : bracketLevels * bracketIndent
    Behavior on bracketGutter {
        NumberAnimation { duration: Theme.durationBase; easing.type: Theme.easing }
    }
    // A foot being dragged: the layer and the end it would snap to, for the header tint.
    property int spanPreviewLayer: -1
    property int spanPreviewEnd: -1
    signal scrollRequested(real dy)

    // Track-header reorder: source index and live drop target while dragging,
    // plus the insertion boundary the indicator line is drawn at.
    property int draggingTrackFrom: -1
    property int draggingTrackTo: -1
    property int draggingTrackSlot: -1

    onDraggingTrackToChanged: Haptics.lane(draggingTrackTo)

    // Pending delete confirmation — index kept until Accept/Reject so the menu
    // can close without wiping the track immediately.
    property int pendingDeleteTrack: -1
    // Same idea for the rename dialog.
    property int pendingRenameTrack: -1
    // Tracks picked from their headers (Shift for a range, Ctrl for one more), as in Premiere.
    readonly property var selectedTrackIds: EditorState.selectedTrackIds
    function trackPicked(index) {
        return index >= 0 && index < tracks.length
               && selectedTrackIds.indexOf(tracks[index].id) !== -1
    }

    clip: true

    ThemedDialog {
        id: renameTrackDialog
        title: qsTr("Rename track")
        acceptText: qsTr("Rename")
        preferredWidth: Theme.dialogWidthSm

        contentItem: Column {
            width: parent ? parent.width : Theme.dialogWidthSm
            spacing: Theme.spacingMd

            ThemedTextField {
                id: renameTrackField
                width: parent.width
                placeholderText: qsTr("Track name")
            }
        }

        onOpened: {
            renameTrackField.forceActiveFocus()
            renameTrackField.selectAll()
        }
        onAccepted: {
            if (root.pendingRenameTrack >= 0)
                EditorState.renameTrack(root.pendingRenameTrack, renameTrackField.text)
            root.pendingRenameTrack = -1
        }
        onRejected: root.pendingRenameTrack = -1
    }

    ThemedDialog {
        id: confirmDeleteTrack
        title: qsTr("Delete this track?")
        acceptText: qsTr("Delete track")
        acceptVariant: "destructive"
        preferredWidth: Theme.dialogWidthSm
        acceptOnReturn: false

        readonly property int clipCount: {
            if (root.pendingDeleteTrack < 0 || root.pendingDeleteTrack >= root.tracks.length)
                return 0
            const clips = root.tracks[root.pendingDeleteTrack].clips
            return clips ? clips.length : 0
        }

        contentItem: ThemedLabel {
            width: parent ? parent.width : Theme.dialogWidthSm
            wrapMode: Text.WordWrap
            size: "sm"
            text: confirmDeleteTrack.clipCount > 0
                  ? qsTr("This removes the track and its %n clips. You can undo afterwards.",
                         "", confirmDeleteTrack.clipCount)
                  : qsTr("This removes the empty track. You can undo afterwards.")
        }

        onAccepted: {
            if (root.pendingDeleteTrack >= 0)
                EditorState.removeTrack(root.pendingDeleteTrack)
            root.pendingDeleteTrack = -1
        }
        onRejected: root.pendingDeleteTrack = -1
    }

    ThemedDialog {
        id: confirmDeleteTracks
        title: qsTr("Delete %n track(s)?", "", root.selectedTrackIds.length)
        acceptText: qsTr("Delete tracks")
        acceptVariant: "destructive"
        preferredWidth: Theme.dialogWidthSm
        acceptOnReturn: false

        property int clipCount: 0
        onAboutToShow: clipCount = EditorState.selectedTracksClipCount()

        contentItem: ThemedLabel {
            width: parent ? parent.width : Theme.dialogWidthSm
            wrapMode: Text.WordWrap
            size: "sm"
            text: confirmDeleteTracks.clipCount > 0
                  ? qsTr("This removes the selected tracks and their %n clips. You can undo afterwards.",
                         "", confirmDeleteTracks.clipCount)
                  : qsTr("This removes the selected tracks, which are empty. You can undo afterwards.")
        }

        onAccepted: EditorState.removeSelectedTracks()
    }

    Connections {
        target: EditorState
        function onTrackDeletionRequested() {
            if (root.selectedTrackIds.length > 0 && !root.compact)
                confirmDeleteTracks.open()
        }
    }

    // The one definition of a row's height, shared with TimelinePanel and AndroidTimeline. It
    // used to be duplicated in all three, which had to agree or the headers slid out of line
    // with their rows; the nested-lane rule made keeping three copies in step untenable.
    // Names the unfolded lines the same way the timeline's rows do.
    TrackKeyframeRows {
        id: keyRowsNames
        visible: false
        width: 0
    }

    // The track the curve editor opens under, and its height (0.24; TimelinePanel says).
    property int curveEditorTrack: -1
    property real curveEditorHeight: 0

    function trackHeight(index) {
        // Reading `tracks` is what gives callers' bindings a dependency to re-evaluate on —
        // EditorState.trackRowHeight is a plain call and carries none of its own.
        const dep = tracks.length
        const curveTrack = root.curveEditorTrack
        const curveHeight = root.curveEditorHeight
        return EditorState.trackRowHeight(index, {
            "video": Theme.trackHeightVideo,
            "audio": Theme.trackHeightAudio,
            "text": Theme.trackHeightText,
            "subtitle": Theme.trackHeightSubtitle,
            "shape": Theme.trackHeightShape,
            "adjustment": Theme.trackHeightAdjustment,
            "lane": Theme.adjustmentLaneHeight,
            "keyframeRow": root.compact ? 0 : Theme.keyframeRowHeight,
            "curveTrack": curveTrack,
            "curveEditor": curveHeight
        })
    }

    // Raise a row so N channel lanes each get a workable height. Only ever grows, and only
    // on enable: silently shrinking a row the user has already tuned is worse than leaving it
    // tall, and on disable they may well want the height they now have.
    //
    // Computed here rather than in C++ because the row-height metrics are owned by Theme and
    // passed *into* trackRowHeight — C++ deliberately hardcodes none of them.
    function growRowForChannelLanes(index, channels) {
        if (channels < 2)
            return
        const base = tracks[index].type === "audio" ? Theme.trackHeightAudio
                                                    : Theme.trackHeightVideo
        // The waveform sits below the header band, inside the selection ring.
        const chrome = Theme.clipHeaderBandHeight + 2 * Theme.clipSelectionRingWidth
        const wanted = (16 * channels + chrome) / base
        if (wanted > (tracks[index].heightScale || 1))
            EditorState.setTrackHeightScale(index, wanted)
    }

    // A nested lane has no header of its own: it belongs to the row above it, whose header
    // already names it.
    function trackOccupiesARow(index) {
        return index >= 0 && index < tracks.length && !tracks[index].isAdjustmentLane
    }

    // Video-track clip display modes, matching Track::ClipDisplay.
    function clipDisplayGlyph(mode) {
        if (mode === 0) return Theme.icons.film
        if (mode === 2) return Theme.icons.audioLines
        return Theme.icons.panelBottomDashed
    }

    function clipDisplayLabel(mode) {
        if (mode === 0) return qsTr("Video")
        if (mode === 2) return qsTr("Waveform")
        return qsTr("Video + waveform")
    }

    function isHeightPreset(index, scale) {
        return Math.abs((tracks[index].heightScale || 1) - scale) < 0.01
    }

    function isWaveformPreset(index, scale) {
        const current = tracks[index].waveformScale !== undefined ? tracks[index].waveformScale : 1
        return Math.abs(current - scale) < 0.01
    }

    // Header button order: Video -> Video + waveform -> Waveform -> Video.
    function nextClipDisplay(mode) {
        return mode === 0 ? 1 : (mode === 1 ? 2 : 0)
    }

    // Single-letter stand-in for the type glyph plus name band, which do not fit a 72px
    // compact header. "V1"/"A2" is the fallback identification a phone gets until the track
    // has a custom name — see trackCompactLabel, which prefers that name when it's set.
    function trackTypeShortLabel(type, isTransform, isCamera) {
        if (isCamera) return qsTr("CAM");
        if (isTransform) return qsTr("TF");
        if (type === "adjustment") return qsTr("FX");
        if (type === "audio") return qsTr("A");
        if (type === "text") return qsTr("T");
        if (type === "subtitle") return qsTr("S");
        if (type === "shape") return qsTr("G");
        return qsTr("V");
    }

    // Human label for a track type.
    function trackTypeLabel(type, isTransform, isCamera) {
        if (isCamera) return qsTr("Camera");
        if (isTransform) return qsTr("Transform");
        if (type === "adjustment") return qsTr("Adjustment");
        if (type === "audio") return qsTr("Audio");
        if (type === "text") return qsTr("Text");
        if (type === "subtitle") return qsTr("Subtitle");
        if (type === "shape") return qsTr("Graphic");
        return qsTr("Video");
    }

    // Track numbers are scoped to their media type rather than the absolute row.
    // A project with Video 1 followed by its first extracted audio lane should read
    // Audio 1, not Audio 2. Reordering mixed track types keeps each sequence natural.
    function trackTypeOrdinal(index) {
        if (index < 0 || index >= tracks.length)
            return 1
        // Transform layers are adjustment tracks by type but count on their own, so an
        // adjustment and a transform layer never share a number.
        const type = tracks[index].type
        const transform = tracks[index].isTransformLayer === true
        var ordinal = 0
        for (var i = 0; i <= index; i++) {
            if (tracks[i].type === type && (tracks[i].isTransformLayer === true) === transform)
                ordinal++
        }
        return Math.max(1, ordinal)
    }

    function trackRowTop(index) {
        var cursor = 0
        for (var i = 0; i < index && i < tracks.length; i++) {
            if (!trackOccupiesARow(i))
                continue
            cursor += trackHeight(i) + Theme.trackGap
        }
        return cursor
    }

    // Boundary the dragged row would be inserted at, 0..tracks.length. Note the
    // open upper end: the old version clamped to tracks.length - 1, so "after
    // the last track" was not expressible and a downward drag could not reach
    // the bottom slot.
    function trackInsertSlotAtY(y) {
        var cursor = 0
        for (var i = 0; i < tracks.length; i++) {
            if (!trackOccupiesARow(i))
                continue
            const th = trackHeight(i)
            if (y < cursor + th / 2)
                return i
            cursor += th + Theme.trackGap
        }
        return tracks.length
    }

    // QList::move() destination for dragging `from` into that slot. Removing the
    // row first shifts everything after it up by one, so a downward move lands a
    // slot earlier than the raw boundary — without this the drag committed a
    // move after a single pixel, because a row's own grip already sits past its
    // own midpoint.
    function trackMoveTargetForSlot(from, slot) {
        const to = slot > from ? slot - 1 : slot
        return Math.max(0, Math.min(tracks.length - 1, to))
    }

    // "Video 1 only", "Video 1 to Text 2", "Everything below" — built here so the track names
    // match the headers.
    function spanOptionLabel(option) {
        if (option.kind === "all")
            return qsTr("Everything below")
        const last = trackNameAt(option.endIndex)
        if (option.kind === "only")
            return qsTr("%1 only").arg(last)
        return qsTr("%1 to %2").arg(trackNameAt(option.firstIndex)).arg(last)
    }

    function trackNameAt(i) {
        if (i < 0 || i >= tracks.length)
            return ""
        if (tracks[i].name && tracks[i].name.length > 0)
            return tracks[i].name
        if (tracks[i].isCameraLayer === true)
            return trackTypeLabel(tracks[i].type, false, true)
        return trackTypeLabel(tracks[i].type, tracks[i].isTransformLayer) + " " + trackTypeOrdinal(i)
    }

    function selectCoveredClips(layerIndex) {
        const clips = tracks[layerIndex].clips || []
        const picked = []
        const seen = {}
        for (let c = 0; c < clips.length; ++c) {
            const covered = EditorState.transformLayerCoveredClips(layerIndex, c)
            for (let k = 0; k < covered.length; ++k) {
                const key = covered[k].track + ":" + covered[k].clip
                if (!seen[key]) {
                    seen[key] = true
                    picked.push(covered[k])
                }
            }
        }
        if (picked.length > 0)
            EditorState.setSelection(picked)
    }

    function clearTrackDrag() {
        draggingTrackFrom = -1
        draggingTrackTo = -1
        draggingTrackSlot = -1
    }

    Repeater {
        model: root.tracks.length
        delegate: Item {
            id: trackLabelRow

            Accessible.role: Accessible.Row
            Accessible.name: trackLabelRow.trackDisplayName
            // Read through root.tracks (not the EditorState
            // getters) so the toggles rebind on tracksChanged.
            readonly property bool trackMuted: root.tracks[index].muted === true
            readonly property bool trackHidden: root.tracks[index].hidden === true
            readonly property bool trackLocked: root.tracks[index].locked === true
            readonly property int clipDisplay: root.tracks[index].clipDisplay !== undefined
                                               ? root.tracks[index].clipDisplay : 1
            readonly property bool trackWaveform: clipDisplay === 2
            // Falls back to the type+position label until a custom name is set.
            readonly property string trackDisplayName:
                root.tracks[index].name && root.tracks[index].name.length > 0
                ? root.tracks[index].name
                : root.tracks[index].isCameraLayer === true
                  ? root.trackTypeLabel(root.tracks[index].type, false, true)
                  : root.trackTypeLabel(root.tracks[index].type, root.tracks[index].isTransformLayer)
                    + " " + root.trackTypeOrdinal(index)
            // Same, but falling back to the short "V1"/"A2" form the compact header uses when
            // there's no custom name to show instead.
            readonly property string trackCompactLabel:
                root.tracks[index].name && root.tracks[index].name.length > 0
                ? root.tracks[index].name
                : root.tracks[index].isCameraLayer === true
                  ? root.trackTypeShortLabel(root.tracks[index].type, false, true)
                  : root.trackTypeShortLabel(root.tracks[index].type, root.tracks[index].isTransformLayer)
                    + root.trackTypeOrdinal(index)
            readonly property bool isTransformLayer: root.tracks[index].isTransformLayer === true
            readonly property bool picked: root.trackPicked(index)
            // Right-clicked on one of several picked tracks: the menu acts on all of them.
            readonly property bool actsOnPicked: picked && root.selectedTrackIds.length > 1
            readonly property bool isCameraLayer: root.tracks[index].isCameraLayer === true
            readonly property bool transformable: ["video", "text", "subtitle", "shape"]
                                                  .indexOf(root.tracks[index].type) !== -1
            readonly property bool insideBracket: (root.tracks[index].transformCoveredBy || []).length > 0
            // The After Effects twirl: unfolds one line per animated property under the clips.
            readonly property bool keyframesExpanded: root.tracks[index].keyframesExpanded === true
            // A picture track always opens (0.24): its Position, Rotation, Scale and Opacity lines
            // are where a clip gets its first key.
            readonly property bool hasKeyframes: !root.compact
                                                 && (["video", "text", "shape"].indexOf(root.tracks[index].type) !== -1
                                                     || (root.tracks.length, EditorState.trackHasKeyframes(index)))
            readonly property var keyframeRows: keyframesExpanded && !root.compact
                                                ? (root.tracks.length, EditorState.trackKeyframeRows(index)) : []
            // The unfolded rows, and the curve editor under them when it is this track's (0.24).
            readonly property real keyframeRowsHeight: keyframeRows.length * Theme.keyframeRowHeight
                                                       + (index === root.curveEditorTrack ? root.curveEditorHeight : 0)
            // The row without its property lines: what the name band and the icons lay out in.
            readonly property real baseHeight: root.trackHeight(index) - keyframeRowsHeight
            // The name moves right to make room for the twirl.
            readonly property real nameInset: hasKeyframes ? 14 : 0
            // Tinted while a bracket foot is dragged over it: this is what the span would cover.
            readonly property bool spanPreviewed: root.spanPreviewLayer >= 0
                                                  && index > root.spanPreviewLayer
                                                  && index <= root.spanPreviewEnd
            x: root.bracketGutter
            width: root.labelsWidth - root.bracketGutter
            // A lane draws inside its parent's row, so it gets no header of its own.
            visible: root.trackOccupiesARow(index)
            height: root.trackHeight(index)
                    + (index < root.tracks.length - 1 ? Theme.trackGap : 0)
            // Split deliberately: trackRowTop() walks every track ahead of this one, so binding
            // it straight into `y` re-ran that walk for every header on every scroll frame. The
            // walk now depends only on the track model; the per-frame part is one subtraction.
            readonly property real rowTop: root.trackRowTop(index)
            // Follows the timeline's vertical scroll so labels stay
            // aligned with their rows.
            y: rowTop - root.contentY
            opacity: root.draggingTrackFrom === index ? 0.45 : 1.0

            // Reorder drag. Covers the whole header rather than just the grip:
            // reaching for the header body is the instinctive gesture, and the
            // grip alone was a ~22px target that was easy to miss entirely.
            // Declared first so it sits below the toggle buttons and the
            // right-click menu, which keep their own presses.
            MouseArea {
                id: trackHeaderDrag
                anchors.fill: parent
                hoverEnabled: true
                acceptedButtons: Qt.LeftButton
                cursorShape: root.draggingTrackFrom === index ? Qt.SizeAllCursor
                                                              : Qt.ArrowCursor

                // A press is not yet a reorder: without a threshold, clicking a
                // header committed a move, because a row's grip already sits
                // past its own midpoint.
                property real pressY: 0
                property bool moved: false
                // Touch only: the hold was recognised, so this row is now draggable.
                // Letting go without moving asks for the context menu instead.
                property bool armed: false
                // Latched per press: the device that pressed decides, not Theme.touchInput.
                property bool pressedByTouch: false
                readonly property bool touchHold: root.touchMode || pressedByTouch
                readonly property real threshold: 4

                // On touch the reorder waits for a hold. Arming on press meant any 4px
                // of finger travel reordered the tracks, and the header column could
                // never be used to scroll the timeline vertically.
                pressAndHoldInterval: 400
                preventStealing: touchHold ? armed : true

                onPressed: (mouse) => {
                    pressedByTouch = mouse.source !== Qt.MouseEventNotSynthesized
                    pressY = mouse.y
                    moved = false
                    armed = false
                    if (touchHold)
                        return
                    root.draggingTrackFrom = index
                    root.draggingTrackTo = index
                    root.draggingTrackSlot = -1
                }
                onPressAndHold: (mouse) => {
                    if (!touchHold || moved)
                        return
                    pressY = mouse.y
                    armed = true
                    root.draggingTrackFrom = index
                    root.draggingTrackTo = index
                    root.draggingTrackSlot = -1
                    Haptics.pickUp()
                }
                onPositionChanged: (mouse) => {
                    if (root.draggingTrackFrom < 0)
                        return
                    if (!moved && Math.abs(mouse.y - pressY) < threshold)
                        return
                    moved = true
                    const local = mapToItem(root, mouse.x, mouse.y)
                    // Rows are drawn at trackRowTop(i) - contentY, so `local` is view
                    // space while trackInsertSlotAtY walks content offsets. Scrolled, the
                    // drop landed on whichever row happened to sit at that screen y.
                    root.draggingTrackSlot = root.trackInsertSlotAtY(local.y + root.contentY)
                    root.draggingTrackTo = root.trackMoveTargetForSlot(
                                               root.draggingTrackFrom,
                                               root.draggingTrackSlot)
                }
                onReleased: (mouse) => {
                    // A plain click (no reorder) picks the track; Shift and Ctrl as in Premiere.
                    if (!touchHold && !moved && !root.compact)
                        EditorState.selectTrackHeader(index,
                                                      (mouse.modifiers & Qt.ShiftModifier) !== 0,
                                                      (mouse.modifiers & Qt.ControlModifier) !== 0)
                    const wantsMenu = touchHold && armed && !moved
                    armed = false
                    if (wantsMenu) {
                        root.clearTrackDrag()
                        trackContextMenu.popup(trackHeaderDrag, trackHeaderDrag.mouseX, trackHeaderDrag.mouseY)
                        return
                    }
                    if (moved && root.draggingTrackFrom >= 0
                            && root.draggingTrackTo >= 0
                            && root.draggingTrackFrom !== root.draggingTrackTo) {
                        Haptics.confirm()
                        EditorState.moveTrack(root.draggingTrackFrom,
                                              root.draggingTrackTo)
                    } else {
                        Haptics.drop()
                    }
                    root.clearTrackDrag()
                }
                onCanceled: {
                    armed = false
                    root.clearTrackDrag()
                }
            }

            Rectangle {
                anchors.right: parent.right
                width: 1
                height: root.trackHeight(index)
                color: Theme.panelBorder
            }

            Rectangle {
                width: parent.width
                height: root.trackHeight(index)
                color: Theme.clipTransform
                opacity: trackLabelRow.spanPreviewed ? 0.18
                         : (trackLabelRow.isTransformLayer ? 0.08 : 0)

                Behavior on opacity {
                    NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                }
            }

            // Picked from the header: tinted, with a bar on the left edge.
            Rectangle {
                width: parent.width
                height: root.trackHeight(index)
                visible: trackLabelRow.picked
                color: Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.18)

                Rectangle {
                    width: 3
                    height: parent.height
                    color: Theme.primary
                }
            }

            // Drag affordance — left-aligned reorder grip. The compact header draws brackets
            // where the grip sits, so rows inside one leave it out.
            IconGlyph {
                visible: !(root.compact && trackLabelRow.insideBracket)
                anchors.left: parent.left
                anchors.leftMargin: root.compact ? 4 : 8
                anchors.verticalCenter: parent.verticalCenter
                anchors.verticalCenterOffset: (index < root.tracks.length - 1 ? -Theme.trackGap / 2 : 0) - trackLabelRow.keyframeRowsHeight / 2
                glyph: Theme.icons.gripVertical
                iconSize: root.compact ? 12 : 14
                iconColor: trackDragMouse.hovered || root.draggingTrackFrom === index
                           ? Theme.panelForeground : Theme.mutedForeground

                Behavior on iconColor {
                    ColorAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                }

                ThemedToolTip {
                    visible: trackHeaderDrag.containsMouse && root.draggingTrackFrom < 0
                    text: qsTr("Drag the header to reorder this track")
                }

                // Hover affordance only — the drag lives on the whole header
                // row below, so the grab target is not a 14px icon.
                HoverHandler { id: trackDragMouse }
            }

            // One eye per nested adjustment lane, level with its strip at the top of the row.
            // The lane has no header of its own, so its switch lives on its parent's.
            Column {
                anchors.right: parent.right
                anchors.rightMargin: root.compact ? 4 : 12
                y: 0
                Repeater {
                    model: EditorState.clipsModel(index).adjustmentLanes
                    delegate: Item {
                        id: laneEye
                        required property var modelData
                        readonly property bool laneHidden: !!root.tracks[modelData] && root.tracks[modelData].hidden === true
                        width: 16
                        height: Theme.adjustmentLaneHeight

                        IconGlyph {
                            anchors.centerIn: parent
                            glyph: laneEye.laneHidden ? Theme.icons.eyeOff : Theme.icons.eye
                            iconSize: 14
                            iconColor: laneEye.laneHidden ? Theme.destructive : Theme.mutedForeground

                            ThemedToolTip {
                                visible: laneEyeMouse.containsMouse
                                text: laneEye.laneHidden ? qsTr("Turn adjustment on") : qsTr("Turn adjustment off")
                            }

                            Accessible.role: Accessible.CheckBox
                            Accessible.name: laneEye.laneHidden ? qsTr("Turn adjustment on") : qsTr("Turn adjustment off")
                            Accessible.checked: laneEye.laneHidden
                            Accessible.onToggleAction: laneEyeMouse.clicked(null)
                        }

                        MouseArea {
                            id: laneEyeMouse
                            anchors.fill: parent
                            anchors.margins: -2
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                Haptics.toggle(!laneEye.laneHidden)
                                EditorState.setTrackHidden(laneEye.modelData, !laneEye.laneHidden)
                            }
                        }
                    }
                }
            }

            Row {
                id: trackIconRow
                anchors.right: parent.right
                anchors.rightMargin: root.compact ? 4 : 12
                anchors.verticalCenter: parent.verticalCenter
                anchors.verticalCenterOffset: (index < root.tracks.length - 1 ? -Theme.trackGap / 2 : 0) - trackLabelRow.keyframeRowsHeight / 2
                // Each toggle's hit area overhangs its glyph by 4 either side, so a 4px
                // gap left the mute and hide targets touching: half the visible gap fired
                // the wrong one, and both silently drop the track from render and export.
                // 12 leaves a 4px dead band between them.
                spacing: root.touchMode ? 12 : (root.compact ? 4 : 8)

                // Voiceover record button on audio tracks
                IconGlyph {
                    id: micIcon
                    readonly property bool isRecordingHere:
                        EditorState.isRecordingAudio && EditorState.recordingTrackIndex === index

                    visible: root.tracks[index].type === "audio" && root.tracks[index].isAdjustmentLane !== true
                    glyph: Theme.icons.mic
                    iconSize: 16
                    anchors.verticalCenter: parent.verticalCenter
                    iconColor: micIcon.isRecordingHere
                               ? (EditorState.isAudioRecordingPaused ? "#eab308" : Theme.destructive)
                               : (micMouse.containsMouse ? Theme.panelForeground : Theme.mutedForeground)

                    Accessible.role: Accessible.Button
                    Accessible.name: micIcon.isRecordingHere ? qsTr("Stop recording") : qsTr("Record voiceover")

                    ThemedToolTip {
                        visible: micMouse.containsMouse
                        text: micIcon.isRecordingHere
                              ? (EditorState.isAudioRecordingPaused ? qsTr("Paused — click to finish recording") : qsTr("Recording — click to finish recording"))
                              : qsTr("Record voiceover (mic)")
                    }

                    MouseArea {
                        id: micMouse
                        anchors.fill: parent
                        anchors.margins: -4
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (EditorState.isRecordingAudio) {
                                EditorState.stopAudioRecording()
                            } else {
                                EditorState.startAudioRecording(index)
                            }
                        }
                    }

                    SequentialAnimation on opacity {
                        running: micIcon.isRecordingHere && !EditorState.isAudioRecordingPaused
                        loops: Animation.Infinite
                        NumberAnimation { to: 0.3; duration: 450 }
                        NumberAnimation { to: 1.0; duration: 450 }
                    }
                }

                // The padlock, as on CapCut: a locked track's clips cannot be picked, moved,
                // trimmed, split or dropped on. A lane follows its track, so it has none.
                IconGlyph {
                    id: lockGlyph
                    visible: root.tracks[index].isAdjustmentLane !== true
                    glyph: trackLabelRow.trackLocked ? Theme.icons.lock : Theme.icons.lockOpen
                    iconSize: 16
                    iconColor: trackLabelRow.trackLocked ? Theme.primary : Theme.mutedForeground
                    anchors.verticalCenter: parent.verticalCenter

                    Accessible.role: Accessible.CheckBox
                    Accessible.name: trackLabelRow.trackLocked ? qsTr("Unlock track") : qsTr("Lock track")
                    Accessible.checked: trackLabelRow.trackLocked
                    Accessible.onToggleAction: lockMouse.clicked(null)

                    ThemedToolTip {
                        visible: lockMouse.containsMouse
                        text: trackLabelRow.trackLocked
                              ? qsTr("Unlock track")
                              : qsTr("Lock track: its clips cannot be moved or edited")
                    }

                    MouseArea {
                        id: lockMouse
                        anchors.fill: parent
                        anchors.margins: -4
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            Haptics.toggle(!trackLabelRow.trackLocked)
                            EditorState.setTrackLocked(index, !trackLabelRow.trackLocked)
                        }
                    }
                }

                IconGlyph {
                    // A graphic track gets one once a video with sound lands on it.
                    visible: root.tracks[index].type === "video"
                             || root.tracks[index].type === "audio"
                             || (root.tracks[index].type === "shape" && root.tracks[index].hasAudio === true)
                    glyph: trackLabelRow.trackMuted ? Theme.icons.volumeOff : Theme.icons.volumeHigh
                    iconSize: 16
                    iconColor: trackLabelRow.trackMuted ? Theme.destructive : Theme.mutedForeground
                    anchors.verticalCenter: parent.verticalCenter

                    // The tooltip above never renders on touch, so the same string has to
                    // reach tooling and screen readers through the accessible name instead.
                    Accessible.role: Accessible.CheckBox
                    Accessible.name: trackLabelRow.trackMuted ? qsTr("Unmute track") : qsTr("Mute track")
                    Accessible.checked: trackLabelRow.trackMuted
                    Accessible.onToggleAction: muteMouse.clicked(null)

                    ThemedToolTip {
                        visible: muteMouse.containsMouse
                        text: trackLabelRow.trackMuted ? qsTr("Unmute track") : qsTr("Mute track")
                    }

                    MouseArea {
                        id: muteMouse
                        anchors.fill: parent
                        anchors.margins: -4
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            Haptics.toggle(!trackLabelRow.trackMuted)
                            EditorState.setTrackMuted(index, !trackLabelRow.trackMuted)
                        }
                    }
                }

                // Stacked per-channel waveforms. Offered only where there is something to
                // split: mono and stereo-downmix material has one lane either way, and the
                // channel count is known because an on-screen track has decoded a block.
                IconGlyph {
                    id: channelLanesToggle
                    // trackMaxChannelCount has no notify of its own and the count only lands
                    // once a block has decoded, so depend on `tracks` to re-evaluate then.
                    readonly property int laneChannels: {
                        const dep = root.tracks.length
                        return EditorState.trackMaxChannelCount(index)
                    }
                    readonly property bool lanesOn:
                        root.tracks[index].showChannelWaveforms === true

                    visible: (root.tracks[index].type === "audio"
                              || (root.tracks[index].type === "video"
                                  && trackLabelRow.trackWaveform))
                             && laneChannels > 1
                    glyph: Theme.icons.split
                    iconSize: 16
                    iconColor: lanesOn ? Theme.primary : Theme.mutedForeground
                    anchors.verticalCenter: parent.verticalCenter

                    Behavior on iconColor {
                        ColorAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                    }

                    ThemedToolTip {
                        visible: channelLanesMouse.containsMouse
                        text: channelLanesToggle.lanesOn
                              ? qsTr("Show one combined waveform")
                              : qsTr("Show each channel separately (%1)")
                                    .arg(channelLanesToggle.laneChannels)
                    }

                    MouseArea {
                        id: channelLanesMouse
                        anchors.fill: parent
                        anchors.margins: -4
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            const on = !channelLanesToggle.lanesOn
                            Haptics.toggle(on)
                            EditorState.setTrackShowChannelWaveforms(index, on)
                            if (on)
                                root.growRowForChannelLanes(
                                    index, channelLanesToggle.laneChannels)
                        }
                    }
                }

                IconGlyph {
                    id: hideGlyph
                    // On a transform layer the eye bypasses it: the tracks it covers stay visible,
                    // just unmoved.
                    readonly property string hideLabel: trackLabelRow.isTransformLayer
                        ? (trackLabelRow.trackHidden ? qsTr("Turn transform on") : qsTr("Turn transform off"))
                        : root.tracks[index].type === "adjustment"
                          ? (trackLabelRow.trackHidden ? qsTr("Turn adjustment on") : qsTr("Turn adjustment off"))
                          : (trackLabelRow.trackHidden ? qsTr("Show track") : qsTr("Hide track"))
                    visible: root.tracks[index].type === "video"
                             || root.tracks[index].type === "adjustment"
                             || root.tracks[index].type === "text"
                             || root.tracks[index].type === "subtitle"
                             || root.tracks[index].type === "shape"
                             || trackLabelRow.isTransformLayer
                    glyph: trackLabelRow.trackHidden ? Theme.icons.eyeOff : Theme.icons.eye
                    iconSize: 16
                    iconColor: trackLabelRow.trackHidden ? Theme.destructive : Theme.mutedForeground
                    anchors.verticalCenter: parent.verticalCenter

                    ThemedToolTip {
                        visible: hideMouse.containsMouse
                        text: hideGlyph.hideLabel
                    }

                    Accessible.role: Accessible.CheckBox
                    Accessible.name: hideLabel
                    Accessible.checked: trackLabelRow.trackHidden
                    Accessible.onToggleAction: hideMouse.clicked(null)

                    MouseArea {
                        id: hideMouse
                        anchors.fill: parent
                        anchors.margins: -4
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            Haptics.toggle(!trackLabelRow.trackHidden)
                            EditorState.setTrackHidden(index, !trackLabelRow.trackHidden)
                        }
                    }
                }

                // Cycles the track's clips through filmstrip / filmstrip + waveform bar /
                // waveform.
                IconGlyph {
                    id: clipDisplayToggle
                    visible: !root.compact && root.tracks[index].type === "video"
                    glyph: root.clipDisplayGlyph(trackLabelRow.clipDisplay)
                    iconSize: 16
                    iconColor: trackLabelRow.clipDisplay === 0 ? Theme.mutedForeground : Theme.primary
                    anchors.verticalCenter: parent.verticalCenter

                    ThemedToolTip {
                        visible: waveMouse.containsMouse
                        text: qsTr("Clips show: %1 (click to change)")
                                  .arg(root.clipDisplayLabel(trackLabelRow.clipDisplay))
                    }

                    MouseArea {
                        id: waveMouse
                        anchors.fill: parent
                        anchors.margins: -4
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            Haptics.press()
                            EditorState.setTrackClipDisplay(
                                index, root.nextClipDisplay(trackLabelRow.clipDisplay))
                        }
                    }
                }

                // CapCut's "..." at the end of an audio track: row height and waveform size.
                IconGlyph {
                    id: audioMoreIcon
                    visible: root.tracks[index].type === "audio" && root.tracks[index].isAdjustmentLane !== true
                    glyph: Theme.icons.ellipsis
                    iconSize: 16
                    iconColor: audioMoreMouse.containsMouse || audioMoreMenu.visible
                               ? Theme.panelForeground : Theme.mutedForeground
                    anchors.verticalCenter: parent.verticalCenter

                    Accessible.role: Accessible.Button
                    Accessible.name: qsTr("Track options")

                    ThemedToolTip {
                        visible: audioMoreMouse.containsMouse && !audioMoreMenu.visible
                        text: qsTr("Track options")
                    }

                    MouseArea {
                        id: audioMoreMouse
                        anchors.fill: parent
                        anchors.margins: -4
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: audioMoreMenu.popup(audioMoreIcon, 0, audioMoreIcon.height + 4)
                    }

                    ThemedContextMenu {
                        id: audioMoreMenu

                        ThemedContextMenu {
                            title: qsTr("Track height")

                            ThemedMenuItem {
                                text: qsTr("Short")
                                icon.name: root.isHeightPreset(index, 0.6) ? Theme.icons.check : ""
                                onTriggered: EditorState.setTrackHeightScale(index, 0.6)
                            }
                            ThemedMenuItem {
                                text: qsTr("Default")
                                icon.name: root.isHeightPreset(index, 1.0) ? Theme.icons.check : ""
                                onTriggered: EditorState.setTrackHeightScale(index, 1.0)
                            }
                            ThemedMenuItem {
                                text: qsTr("High")
                                icon.name: root.isHeightPreset(index, 1.6) ? Theme.icons.check : ""
                                onTriggered: EditorState.setTrackHeightScale(index, 1.6)
                            }
                        }

                        ThemedContextMenu {
                            title: qsTr("Audio waveform size")

                            ThemedMenuItem {
                                text: "30%"
                                icon.name: root.isWaveformPreset(index, 0.3) ? Theme.icons.check : ""
                                onTriggered: EditorState.setTrackWaveformScale(index, 0.3)
                            }
                            ThemedMenuItem {
                                text: "60%"
                                icon.name: root.isWaveformPreset(index, 0.6) ? Theme.icons.check : ""
                                onTriggered: EditorState.setTrackWaveformScale(index, 0.6)
                            }
                            ThemedMenuItem {
                                text: "100%"
                                icon.name: root.isWaveformPreset(index, 1.0) ? Theme.icons.check : ""
                                onTriggered: EditorState.setTrackWaveformScale(index, 1.0)
                            }
                        }
                    }
                }
            }

            // Text/subtitle rows are too short for the name band above (it needs both a
            // top-anchored name and a vertically centered icon row without the two
            // overlapping), so the name sits inline here instead, between the grip and the
            // type/toggle icons.
            Text {
                id: inlineTrackName
                visible: !root.compact && trackLabelRow.baseHeight < 40
                anchors.left: parent.left
                anchors.leftMargin: Theme.spacing3xl + Theme.spacingSm + trackLabelRow.nameInset
                anchors.right: trackIconRow.left
                anchors.rightMargin: Theme.spacingSm
                anchors.verticalCenter: parent.verticalCenter
                anchors.verticalCenterOffset: (index < root.tracks.length - 1 ? -Theme.trackGap / 2 : 0) - trackLabelRow.keyframeRowsHeight / 2
                text: trackLabelRow.trackDisplayName
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeTiny
                elide: Text.ElideRight
            }

            // Compact stand-in for the glyph and the name band: sits in the gap
            // between the grip and the mute/hide pair, which is the only free
            // horizontal space the compact header has. Shows the custom name (elided) once
            // one is set — the context menu's Rename is reachable here too (long-press),
            // and a rename that changes nothing visible would look like it silently failed.
            Text {
                visible: root.compact
                anchors.left: parent.left
                anchors.leftMargin: 18
                anchors.right: trackIconRow.left
                anchors.rightMargin: Theme.spacingSm
                anchors.verticalCenter: parent.verticalCenter
                anchors.verticalCenterOffset: (index < root.tracks.length - 1 ? -Theme.trackGap / 2 : 0) - trackLabelRow.keyframeRowsHeight / 2
                text: trackLabelRow.trackCompactLabel
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeTiny
                elide: Text.ElideRight
            }

            // Clip display toggle for compact headers. Parked in the bottom-left
            // corner rather than in the icon row, which a video track has no room left
            // in — and only video rows (65px) are tall enough for a second corner.
            IconGlyph {
                visible: root.compact && root.tracks[index].type === "video"
                anchors.left: parent.left
                anchors.leftMargin: 4
                anchors.bottom: parent.bottom
                anchors.bottomMargin: (index < root.tracks.length - 1 ? Theme.trackGap : 0) + 4
                glyph: root.clipDisplayGlyph(trackLabelRow.clipDisplay)
                iconSize: Theme.iconSizeMd
                iconColor: trackLabelRow.clipDisplay === 0 ? Theme.mutedForeground : Theme.primary

                MouseArea {
                    anchors.fill: parent
                    anchors.margins: -8
                    onClicked: {
                        Haptics.press()
                        EditorState.setTrackClipDisplay(
                            index, root.nextClipDisplay(trackLabelRow.clipDisplay))
                    }
                }
            }

            // Track name. Nothing in the header used to say which
            // track this was beyond the type glyph.
            Text {
                id: bandTrackName
                anchors.left: parent.left
                anchors.leftMargin: Theme.spacing3xl + Theme.spacingSm + trackLabelRow.nameInset
                anchors.right: parent.right
                anchors.rightMargin: Theme.spacingLg
                anchors.top: parent.top
                anchors.topMargin: Theme.spacingMd
                text: trackLabelRow.trackDisplayName
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeTiny
                elide: Text.ElideRight
                visible: !root.compact && trackLabelRow.baseHeight >= 40
            }

            // The twirl, level with the track name: open, the row grows one line per animated
            // property of its clips, keys drawn on each (TrackKeyframeRows in the timeline).
            IconGlyph {
                id: keyframeTwirl
                readonly property Item nameItem: bandTrackName.visible ? bandTrackName : inlineTrackName
                visible: trackLabelRow.hasKeyframes
                x: Theme.spacing3xl + Theme.spacingSm - 2
                y: nameItem.y + (nameItem.height - height) / 2
                z: 3
                glyph: trackLabelRow.keyframesExpanded ? Theme.icons.chevronDown : Theme.icons.chevronRight
                iconSize: 12
                iconColor: twirlMouse.containsMouse || trackLabelRow.keyframesExpanded
                           ? Theme.panelForeground : Theme.mutedForeground

                Accessible.role: Accessible.Button
                Accessible.name: trackLabelRow.keyframesExpanded ? qsTr("Hide keyframes")
                                                                 : qsTr("Show keyframes")

                ThemedToolTip {
                    visible: twirlMouse.containsMouse
                    text: trackLabelRow.keyframesExpanded ? qsTr("Hide keyframes")
                                                          : qsTr("Show keyframes")
                }

                MouseArea {
                    id: twirlMouse
                    anchors.fill: parent
                    anchors.margins: -5
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: EditorState.setTrackKeyframesExpanded(index, !trackLabelRow.keyframesExpanded)
                }
            }

            // The unfolded property lines, level with their keys in the timeline (0.24): icon, name,
            // the value at the playhead, a diamond that adds or removes the key there, and a menu.
            Column {
                id: keyLines
                visible: trackLabelRow.keyframeRows.length > 0
                y: trackLabelRow.baseHeight
                z: 2
                width: parent.width - 1
                readonly property int trackIndex: index
                // The clip the lines act on: the selected one on this track, else the one under
                // the playhead.
                readonly property int targetClip: {
                    void EditorState.playheadSeconds
                    void EditorState.selectedClip
                    void EditorState.tracksRevision
                    return EditorState.keyframeTargetClip(keyLines.trackIndex)
                }
                Repeater {
                    model: trackLabelRow.keyframeRows
                    delegate: Rectangle {
                        id: keyLine
                        required property var modelData
                        required property int index
                        readonly property bool joined: !!modelData.group && !modelData.axis
                        readonly property var props: joined ? modelData.groupProps : [modelData.prop]
                        readonly property int clip: keyLines.targetClip
                        // Position, Rotation, Scale and Opacity (and their axes) can go back to the
                        // clip's reset; other animated properties have no reset of their own.
                        readonly property bool resettable: !!modelData.group
                        HoverHandler { id: lineHover }
                        width: parent.width
                        height: Theme.keyframeRowHeight
                        color: Qt.rgba(0, 0, 0, index % 2 === 0 ? 0.16 : 0.08)

                        function valueOf(prop) {
                            void EditorState.playheadSeconds
                            void EditorState.tracksRevision
                            if (keyLine.clip < 0)
                                return NaN
                            const base = EditorState.propertyBaseValue(keyLines.trackIndex, keyLine.clip, prop, 0)
                            return EditorState.propertyValueAt(keyLines.trackIndex, keyLine.clip, prop,
                                                               EditorState.playheadSeconds, base)
                        }
                        // The key of each of this line's properties under the playhead, if any.
                        readonly property var keysHere: {
                            void EditorState.playheadSeconds
                            void EditorState.tracksRevision
                            const out = []
                            if (keyLine.clip < 0)
                                return out
                            for (const prop of keyLine.props) {
                                if (EditorState.clipAnimatedProperties(keyLines.trackIndex, keyLine.clip).indexOf(prop) < 0)
                                    continue
                                const keys = EditorState.clipKeyframes(keyLines.trackIndex, keyLine.clip, prop) || []
                                for (const k of keys) {
                                    if (Math.abs(k.seconds - EditorState.playheadSeconds) < 1 / 120)
                                        out.push({ prop: prop, seconds: k.seconds })
                                }
                            }
                            return out
                        }
                        readonly property string summary: {
                            if (keyLine.clip < 0)
                                return "—"
                            const n = v => isNaN(v) ? "—" : String(Math.round(v))
                            const group = keyLine.joined ? keyLine.modelData.group : ""
                            if (group === "position")
                                return "X: " + n(valueOf("x")) + " · Y: " + n(valueOf("y"))
                            if (group === "rotation")
                                return Number(valueOf("rotation")).toFixed(1) + "°"
                            if (group === "scale") {
                                // As the inspector: 100 % fills the canvas on its tighter axis.
                                const cw = Math.max(1, EditorState.projectFile.projectWidth())
                                const ch = Math.max(1, EditorState.projectFile.projectHeight())
                                return Math.round(Math.max(valueOf("width") / cw, valueOf("height") / ch) * 100) + " %"
                            }
                            if (group === "opacity")
                                return Math.round(valueOf("opacity") * 100) + " %"
                            const v = valueOf(keyLine.modelData.prop)
                            return isNaN(v) ? "—" : (Math.abs(v) >= 10 ? String(Math.round(v)) : v.toFixed(2))
                        }
                        readonly property string iconName: {
                            switch (keyLine.joined ? keyLine.modelData.group : "") {
                            case "position": return "move"
                            case "rotation": return "rotate-cw"
                            case "scale": return "scaling"
                            case "opacity": return Theme.icons.blend
                            }
                            return ""
                        }

                        // A key here and now on these properties, or take it away (one undo step).
                        // Everything is read before the first edit: that edit rebuilds the rows and
                        // this delegate with them, and a session left open would make the next
                        // Cancel (Texto avanzado) undo all the work since.
                        function toggleKeyHere() {
                            if (keyLine.clip < 0)
                                return
                            const track = keyLines.trackIndex
                            const clip = keyLine.clip
                            const keys = keyLine.keysHere.slice()
                            const props = keyLine.props.slice()
                            const at = EditorState.playheadSeconds
                            const several = keys.length > 1 || (keys.length === 0 && props.length > 1)
                            if (several)
                                EditorState.beginEditSession(keys.length > 0 ? qsTr("Remove keyframe")
                                                                             : qsTr("Add keyframe"))
                            try {
                                if (keys.length > 0) {
                                    for (const k of keys)
                                        EditorState.removeClipKeyframe(track, clip, k.prop, k.seconds)
                                } else {
                                    for (const prop of props)
                                        EditorState.addClipKeyframeAt(track, clip, prop, at)
                                }
                            } finally {
                                if (several)
                                    EditorState.endEditSession(true)
                            }
                        }
                        function removeAllKeys() {
                            if (keyLine.clip < 0)
                                return
                            const track = keyLines.trackIndex
                            const clip = keyLine.clip
                            const props = keyLine.props.slice()
                            const animated = EditorState.clipAnimatedProperties(track, clip)
                            const doomed = []
                            for (const prop of props) {
                                if (animated.indexOf(prop) < 0)
                                    continue
                                for (const k of (EditorState.clipKeyframes(track, clip, prop) || []))
                                    doomed.push({ prop: prop, seconds: k.seconds })
                            }
                            EditorState.beginEditSession(qsTr("Remove keyframes"))
                            try {
                                for (const k of doomed)
                                    EditorState.removeClipKeyframe(track, clip, k.prop, k.seconds)
                            } finally {
                                EditorState.endEditSession(true)
                            }
                        }
                        // Playhead to the key before or after it on this line.
                        function stepKey(forward) {
                            if (keyLine.clip < 0)
                                return
                            const now = EditorState.playheadSeconds
                            let best = NaN
                            for (const prop of keyLine.props) {
                                const keys = EditorState.clipKeyframes(keyLines.trackIndex, keyLine.clip, prop) || []
                                for (const k of keys) {
                                    const ahead = forward ? k.seconds > now + 1 / 120 : k.seconds < now - 1 / 120
                                    if (ahead && (isNaN(best) || (forward ? k.seconds < best : k.seconds > best)))
                                        best = k.seconds
                                }
                            }
                            if (!isNaN(best))
                                EditorState.playheadSeconds = best
                        }

                        // Open a joined line into its axes.
                        IconGlyph {
                            id: axisTwirl
                            visible: keyLine.modelData.expandable === true
                            x: 6
                            anchors.verticalCenter: parent.verticalCenter
                            glyph: keyLine.modelData.expanded ? Theme.icons.chevronDown : Theme.icons.chevronRight
                            iconSize: 11
                            iconColor: axisMouse.containsMouse ? Theme.panelForeground : Theme.mutedForeground
                            MouseArea {
                                id: axisMouse
                                anchors.fill: parent
                                anchors.margins: -5
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: EditorState.setKeyframeGroupExpanded(keyLines.trackIndex, keyLine.modelData.group,
                                                                                !keyLine.modelData.expanded)
                            }
                        }
                        IconGlyph {
                            id: lineIcon
                            visible: keyLine.iconName.length > 0
                            x: 20
                            anchors.verticalCenter: parent.verticalCenter
                            glyph: keyLine.iconName
                            iconSize: 14
                            iconColor: Theme.mutedForeground
                        }
                        Column {
                            anchors.left: parent.left
                            anchors.leftMargin: keyLine.modelData.axis ? 40 : 40
                            anchors.right: keyButton.left
                            anchors.rightMargin: 2
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 0
                            Text {
                                width: parent.width
                                text: (keyLine.modelData.axis ? "· " : "") + keyRowsNames.rowLabel(keyLine.modelData)
                                color: Theme.panelForeground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeXs
                                elide: Text.ElideRight
                            }
                            Text {
                                width: parent.width
                                text: keyLine.summary
                                color: Theme.mutedForeground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeTiny
                                elide: Text.ElideRight
                            }
                        }
                        IconButton {
                            id: resetButton
                            anchors.right: keyButton.left
                            anchors.verticalCenter: parent.verticalCenter
                            visible: keyLine.resettable && keyLine.clip >= 0 && lineHover.hovered
                            glyph: Theme.icons.reset
                            variant: "text"
                            buttonSize: 18
                            iconSize: 12
                            tooltip: qsTr("Reset")
                            onClicked: EditorState.resetClipProperties(keyLines.trackIndex, keyLine.clip, keyLine.props)
                        }
                        IconButton {
                            id: keyButton
                            anchors.right: moreButton.left
                            anchors.verticalCenter: parent.verticalCenter
                            enabled: keyLine.clip >= 0
                            glyph: keyLine.keysHere.length > 0 ? Theme.icons.diamondMinus : Theme.icons.diamondPlus
                            variant: "text"
                            buttonSize: 20
                            iconSize: 13
                            active: keyLine.keysHere.length > 0
                            tooltip: keyLine.keysHere.length > 0 ? qsTr("Remove the keyframe at the playhead")
                                                                 : qsTr("Add a keyframe at the playhead")
                            onClicked: keyLine.toggleKeyHere()
                        }
                        IconButton {
                            id: moreButton
                            anchors.right: parent.right
                            anchors.rightMargin: 2
                            anchors.verticalCenter: parent.verticalCenter
                            enabled: keyLine.clip >= 0
                            glyph: Theme.icons.ellipsis
                            variant: "text"
                            buttonSize: 18
                            iconSize: 13
                            tooltip: qsTr("More")
                            onClicked: lineMenu.popup()
                        }

                        ThemedContextMenu {
                            id: lineMenu
                            ThemedMenuItem {
                                text: keyLine.keysHere.length > 0 ? qsTr("Remove the keyframe at the playhead")
                                                                  : qsTr("Add a keyframe at the playhead")
                                onTriggered: keyLine.toggleKeyHere()
                            }
                            ThemedMenuItem {
                                text: qsTr("Previous keyframe")
                                onTriggered: keyLine.stepKey(false)
                            }
                            ThemedMenuItem {
                                text: qsTr("Next keyframe")
                                onTriggered: keyLine.stepKey(true)
                            }
                            ThemedMenuSeparator {}
                            ThemedMenuItem {
                                visible: keyLine.resettable
                                height: visible ? implicitHeight : 0
                                text: qsTr("Reset")
                                onTriggered: EditorState.resetClipProperties(keyLines.trackIndex, keyLine.clip,
                                                                             keyLine.props)
                            }
                            ThemedMenuItem {
                                text: qsTr("Remove all keyframes…")
                                onTriggered: removeAllDialog.open()
                            }
                        }

                        ThemedDialog {
                            id: removeAllDialog
                            title: qsTr("Remove every keyframe of %1?").arg(keyRowsNames.rowLabel(keyLine.modelData))
                            acceptText: qsTr("Remove")
                            acceptVariant: "destructive"
                            preferredWidth: Theme.dialogWidthSm
                            acceptOnReturn: false
                            contentItem: ThemedLabel {
                                width: parent ? parent.width : Theme.dialogWidthSm
                                wrapMode: Text.WordWrap
                                size: "sm"
                                text: qsTr("The clip keeps the value it has at the playhead. You can undo afterwards.")
                            }
                            onAccepted: keyLine.removeAllKeys()
                        }

                        // Right-click on the line: the same menu.
                        MouseArea {
                            anchors.fill: parent
                            z: -1
                            acceptedButtons: Qt.RightButton
                            onClicked: if (keyLine.clip >= 0) lineMenu.popup()
                        }
                    }
                }
            }

            // Track context menu. Right-click on desktop; on touch it is opened from the
            // reorder area below, which sits under the mute/hide toggles so those keep
            // their own presses. Accepting LeftButton here would put this on top of
            // everything and swallow the lot.
            MouseArea {
                id: trackMenuArea
                anchors.fill: parent
                acceptedButtons: Qt.RightButton
                onClicked: trackContextMenu.popup()

                ThemedContextMenu {
                    id: trackContextMenu

                    ThemedMenuItem {
                        visible: trackLabelRow.actsOnPicked
                        text: qsTr("Group %n tracks", "", root.selectedTrackIds.length)
                        icon.name: Theme.icons.layers
                        onTriggered: EditorState.groupSelectedTracks()
                    }
                    ThemedMenuItem {
                        visible: trackLabelRow.actsOnPicked
                        text: qsTr("Delete %n tracks", "", root.selectedTrackIds.length)
                        icon.name: Theme.icons.trash
                        onTriggered: confirmDeleteTracks.open()
                    }
                    ThemedMenuSeparator {
                        visible: trackLabelRow.actsOnPicked
                    }
                    ThemedMenuItem {
                        text: qsTr("Rename…")
                        icon.name: Theme.icons.pencil
                        onTriggered: {
                            root.pendingRenameTrack = index
                            // Custom name only — pre-filling the type+position fallback
                            // ("Video 1") would persist it as a real name on an unchanged
                            // confirm, then stick after the track is reordered.
                            renameTrackField.text = root.tracks[index].name || ""
                            renameTrackDialog.open()
                        }
                    }
                    ThemedMenuSeparator {}
                    ThemedMenuItem {
                        text: trackLabelRow.trackMuted ? qsTr("Unmute track")
                                                       : qsTr("Mute track")
                        icon.name: trackLabelRow.trackMuted ? Theme.icons.volumeHigh
                                                            : Theme.icons.volumeOff
                        onTriggered: EditorState.setTrackMuted(index, !trackLabelRow.trackMuted)
                    }
                    ThemedMenuItem {
                        text: trackLabelRow.trackHidden ? qsTr("Show track")
                                                        : qsTr("Hide track")
                        icon.name: trackLabelRow.trackHidden ? Theme.icons.eye
                                                             : Theme.icons.eyeOff
                        onTriggered: EditorState.setTrackHidden(index, !trackLabelRow.trackHidden)
                    }
                    ThemedMenuSeparator {
                        visible: trackLabelRow.isTransformLayer || trackLabelRow.transformable
                                 || trackLabelRow.isCameraLayer
                    }
                    // Back-to-back camera clips are cuts between framings; each new one starts at rest.
                    ThemedMenuItem {
                        visible: trackLabelRow.isCameraLayer
                        text: qsTr("Add camera clip at playhead")
                        icon.name: Theme.icons.video
                        onTriggered: EditorState.addCameraClip()
                    }
                    // A submenu cannot be hidden per row, so the span choices open as their
                    // own menu from here.
                    ThemedMenuItem {
                        visible: trackLabelRow.isTransformLayer
                        text: qsTr("Covers…")
                        icon.name: Theme.icons.layers
                        onTriggered: coversMenu.popup()
                    }
                    ThemedMenuItem {
                        visible: trackLabelRow.isTransformLayer
                        text: qsTr("Select covered clips")
                        icon.name: Theme.icons.maximize
                        onTriggered: root.selectCoveredClips(index)
                    }
                    ThemedMenuItem {
                        visible: trackLabelRow.transformable
                        text: qsTr("Add transform layer above")
                        icon.name: Theme.icons.maximize
                        onTriggered: EditorState.addTransformLayerAbove(index)
                    }
                    ThemedMenuSeparator {
                        visible: root.tracks[index].type === "video"
                    }
                    // The active entry swaps its icon for a tick, like the header's
                    // Settings menu.
                    ThemedMenuItem {
                        visible: root.tracks[index].type === "video"
                        text: root.clipDisplayLabel(0)
                        icon.name: trackLabelRow.clipDisplay === 0 ? Theme.icons.check
                                                                   : root.clipDisplayGlyph(0)
                        onTriggered: EditorState.setTrackClipDisplay(index, 0)
                    }
                    ThemedMenuItem {
                        visible: root.tracks[index].type === "video"
                        text: root.clipDisplayLabel(1)
                        icon.name: trackLabelRow.clipDisplay === 1 ? Theme.icons.check
                                                                   : root.clipDisplayGlyph(1)
                        onTriggered: EditorState.setTrackClipDisplay(index, 1)
                    }
                    ThemedMenuItem {
                        visible: root.tracks[index].type === "video"
                        text: root.clipDisplayLabel(2)
                        icon.name: trackLabelRow.clipDisplay === 2 ? Theme.icons.check
                                                                   : root.clipDisplayGlyph(2)
                        onTriggered: EditorState.setTrackClipDisplay(index, 2)
                    }
                    ThemedMenuSeparator {}
                    ThemedContextMenu {
                        title: qsTr("Track height")

                        ThemedMenuItem {
                            text: qsTr("Short")
                            icon.name: root.isHeightPreset(index, 0.6)
                                       ? Theme.icons.check : Theme.icons.listChevronsDownUp
                            onTriggered: EditorState.setTrackHeightScale(index, 0.6)
                        }
                        ThemedMenuItem {
                            text: qsTr("Default")
                            icon.name: root.isHeightPreset(index, 1.0)
                                       ? Theme.icons.check : Theme.icons.list
                            onTriggered: EditorState.setTrackHeightScale(index, 1.0)
                        }
                        ThemedMenuItem {
                            text: qsTr("High")
                            icon.name: root.isHeightPreset(index, 1.6)
                                       ? Theme.icons.check : Theme.icons.listChevronsUpDown
                            onTriggered: EditorState.setTrackHeightScale(index, 1.6)
                        }
                        ThemedMenuSeparator {
                            visible: !root.touchHold
                        }
                        ThemedMenuItem {
                            visible: !root.touchHold
                            enabled: false
                            text: qsTr("Drag the line under the track to fine-tune")
                            icon.name: Theme.icons.info
                        }
                    }
                    // Desktop fine-tunes a lane by wheeling over its header. Touch has no
                    // wheel, so the same nudge is offered explicitly.
                    ThemedMenuItem {
                        visible: root.touchHold
                        text: qsTr("Taller row")
                        icon.name: Theme.icons.chevronUp
                        enabled: root.tracks[index].heightScale < EditorState.trackHeightScaleMax()
                        onTriggered: EditorState.nudgeTrackHeightScale(index, 1)
                    }
                    ThemedMenuItem {
                        visible: root.touchHold
                        text: qsTr("Shorter row")
                        icon.name: Theme.icons.chevronDown
                        enabled: root.tracks[index].heightScale > EditorState.trackHeightScaleMin()
                        onTriggered: EditorState.nudgeTrackHeightScale(index, -1)
                    }
                    ThemedMenuSeparator {}
                    ThemedMenuItem {
                        text: qsTr("Delete track")
                        icon.name: Theme.icons.trash
                        onTriggered: {
                            root.pendingDeleteTrack = index
                            confirmDeleteTrack.open()
                        }
                    }
                }

                ThemedContextMenu {
                    id: coversMenu
                    title: qsTr("Covers")
                    enabled: trackLabelRow.isTransformLayer
                    readonly property int layerIndex: index
                    property var options: []
                    onAboutToShow: options = EditorState.transformSpanOptions(layerIndex)

                    Instantiator {
                        model: coversMenu.options
                        delegate: ThemedMenuItem {
                            required property var modelData
                            text: root.spanOptionLabel(modelData)
                            icon.name: modelData.current ? Theme.icons.check : ""
                            onTriggered: EditorState.setTransformSpan(coversMenu.layerIndex,
                                                                      modelData.endId)
                        }
                        onObjectAdded: (i, object) => coversMenu.insertItem(i, object)
                        onObjectRemoved: (i, object) => coversMenu.removeItem(object)
                    }
                }
            }

            // The row's bottom line resizes it, as in CapCut: drag it, or roll the wheel while on
            // it. Only the line, not the whole header -- wheeling over a header used to grow the
            // track for anyone who only wanted to scroll the timeline down.
            MouseArea {
                id: rowResizeLine
                readonly property real lineY: root.trackHeight(index)
                x: 0
                width: parent.width
                y: lineY - 3
                height: (index < root.tracks.length - 1 ? Theme.trackGap : 0) + 6
                z: 40
                visible: !root.touchHold
                hoverEnabled: true
                cursorShape: Qt.SizeVerCursor
                preventStealing: true

                property real pressY: 0
                property real startScale: 1
                property real startHeight: 1

                onPressed: (mouse) => {
                    pressY = mapToItem(root, mouse.x, mouse.y).y
                    startScale = root.tracks[index].heightScale || 1
                    startHeight = Math.max(1, root.trackHeight(index))
                }
                onPositionChanged: (mouse) => {
                    if (!pressed)
                        return
                    const dy = mapToItem(root, mouse.x, mouse.y).y - pressY
                    EditorState.setTrackHeightScale(index, startScale * (startHeight + dy) / startHeight)
                }
                onWheel: (wheel) => {
                    // Modified wheel belongs to the timeline's zoom/pan.
                    if (wheel.modifiers & (Qt.ControlModifier | Qt.ShiftModifier)) {
                        wheel.accepted = false
                        return
                    }
                    const dy = wheel.angleDelta.y !== 0 ? wheel.angleDelta.y
                                                        : wheel.pixelDelta.y
                    if (dy === 0)
                        return
                    EditorState.nudgeTrackHeightScale(index, dy > 0 ? 1 : -1)
                }

                // The line lights up under the pointer, so it reads as something to grab.
                Rectangle {
                    anchors.horizontalCenter: parent.horizontalCenter
                    y: 2
                    width: parent.width - 8
                    height: 2
                    radius: 1
                    color: Theme.primary
                    opacity: rowResizeLine.containsMouse || rowResizeLine.pressed ? 0.8 : 0
                }

                ThemedToolTip {
                    visible: rowResizeLine.containsMouse && !rowResizeLine.pressed
                    text: qsTr("Drag to change the track height")
                }
            }
        }
    }

    // One bracket per transform layer, over the rows and in the gutter they leave.
    Repeater {
        model: root.tracks.length
        delegate: TransformSpanBracket {
            required property int index
            width: root.width
            height: root.height
            z: 20
            tracks: root.tracks
            layerIndex: root.tracks[index].isTransformLayer ? index : -1
            contentY: root.contentY
            indentStep: root.bracketIndent
            touchMode: root.touchMode
            rowTop: root.trackRowTop
            rowHeight: root.trackHeight
            onPreviewEndChanged: {
                if (previewEnd >= 0) {
                    root.spanPreviewLayer = index
                    root.spanPreviewEnd = previewEnd
                } else if (root.spanPreviewLayer === index) {
                    root.spanPreviewLayer = -1
                    root.spanPreviewEnd = -1
                }
            }
            onScrollRequested: (dy) => root.scrollRequested(dy)
        }
    }

    // Insertion line while reordering tracks.
    Rectangle {
        visible: root.draggingTrackSlot >= 0 && root.draggingTrackTo >= 0
                 && root.draggingTrackFrom !== root.draggingTrackTo
        width: parent.width - 8
        height: 2
        radius: 1
        x: 4
        color: Theme.primary
        z: 10
        // Drawn at the insertion boundary itself, in the same frame as the
        // header rows — without -contentY it drifts off the boundary as soon as
        // the tracks are scrolled.
        y: {
            const slot = root.draggingTrackSlot
            if (slot < 0)
                return 0
            if (slot >= root.tracks.length) {
                var last = root.tracks.length - 1
                while (last > 0 && !root.trackOccupiesARow(last))
                    last--
                return root.trackRowTop(last) + root.trackHeight(last)
                       - root.contentY - 1
            }
            return root.trackRowTop(slot) - root.contentY - 1
        }
    }

    // Drag to widen the header column; double-click restores the default.
    MouseArea {
        id: widthHandle
        visible: root.resizable
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: 6
        z: 50
        hoverEnabled: true
        cursorShape: Qt.SplitHCursor
        preventStealing: true
        onPositionChanged: (mouse) => {
            if (pressed)
                EditorState.preferences.trackLabelsWidth = x + mouse.x + width / 2
        }
        onDoubleClicked: EditorState.preferences.trackLabelsWidth = Theme.trackLabelsWidth

        Rectangle {
            anchors.right: parent.right
            width: 2
            height: parent.height
            color: Theme.primary
            opacity: widthHandle.pressed || widthHandle.containsMouse ? 1 : 0

            Behavior on opacity {
                NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
            }
        }
    }
}
