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
    // The timeline's picked keys (KeyframeKeyTools): a click on a line's name picks its keys.
    property var keyframeTools: null
    // Scale's chain (0.25): its two values move together while on, as After Effects' default.
    property bool scaleLinked: true

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
            // are where a clip gets its first key. An audio track too, for Volume and Pan (0.25).
            readonly property bool hasKeyframes: !root.compact
                                                 && (["video", "text", "shape", "audio"].indexOf(root.tracks[index].type) !== -1
                                                     || (root.tracks.length, EditorState.trackHasKeyframes(index)))
            readonly property var keyframeRows: keyframesExpanded && !root.compact
                                                ? (root.tracks.length, EditorState.trackKeyframeRows(index)) : []
            // The unfolded rows, and the curve editor under them when it is this track's (0.24).
            // The curve editor takes the lines' place on its track (0.25).
            readonly property real keyframeRowsHeight: Math.max(keyframeRows.length * Theme.keyframeRowHeight,
                                                                index === root.curveEditorTrack ? root.curveEditorHeight : 0)
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
                // What the expression dialog's "Apply to" offers (0.26): the layer's usual properties,
                // whether their line is showing or not, then every other line of the track.
                function expressionTargets() {
                    const rows = trackLabelRow.keyframeRows || []
                    const audio = rows.some(r => r.group === "volume" || r.group === "pan")
                    const T = (s) => qsTranslate("TrackKeyframeRows", s)
                    const list = audio
                        ? [{ label: T("Volume"), props: ["volume"] }, { label: T("Pan"), props: ["pan"] }]
                        : [{ label: T("Position"), props: ["x", "y"] },
                           { label: T("X Position"), props: ["x"] },
                           { label: T("Y Position"), props: ["y"] },
                           { label: T("Scale"), props: ["width", "height"] },
                           { label: T("Width"), props: ["width"] },
                           { label: T("Height"), props: ["height"] },
                           { label: T("Rotation"), props: ["rotation"] },
                           { label: T("Opacity"), props: ["opacity"] },
                           { label: T("Anchor point"), props: ["anchorX", "anchorY"] }]
                    const known = new Set(list.map(t => JSON.stringify(t.props)))
                    for (const row of rows) {
                        if (row.group || row.kind === "heading")
                            continue
                        const props = [row.prop]
                        if (known.has(JSON.stringify(props)))
                            continue
                        known.add(JSON.stringify(props))
                        list.push({ label: keyRowsNames.rowLabel(row), props: props })
                    }
                    return list
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
                        // After Effects' expression pick whip (0.26) lands here: the line names the
                        // layer's property as an expression reads it, or "" when expressions cannot.
                        readonly property bool exprWhipTarget: true
                        function exprWhipReference(targetProp) {
                            if (keyLine.clip < 0)
                                return ""
                            const name = (EditorState.clipAt(keyLines.trackIndex, keyLine.clip) || {}).name || ""
                            if (name.length === 0)
                                return ""
                            // A joined line gives the axis matching the property being edited.
                            const second = targetProp === "y" || targetProp === "height" || targetProp === "anchorY"
                            const axis = keyLine.joined ? (second ? 1 : 0) : -1
                            const paths = {
                                "x": "transform.position[0]", "y": "transform.position[1]",
                                "position": "transform.position[" + Math.max(0, axis) + "]",
                                "rotation": "transform.rotation", "opacity": "transform.opacity",
                                "width": "transform.scale[0]", "height": "transform.scale[1]",
                                "scale": "transform.scale[" + Math.max(0, axis) + "]",
                                "anchorX": "transform.anchorPoint[0]", "anchorY": "transform.anchorPoint[1]",
                                "anchor": "transform.anchorPoint[" + Math.max(0, axis) + "]"
                            }
                            const key = keyLine.joined ? keyLine.modelData.group : keyLine.modelData.prop
                            const path = paths[key]
                            return path ? "thisComp.layer(" + JSON.stringify(name) + ")." + path : ""
                        }
                        // Position, Rotation, Scale and Opacity (and their axes) can go back to the
                        // clip's reset; other animated properties have no reset of their own.
                        readonly property bool resettable: !!modelData.group
                                                           && modelData.group !== "volume" && modelData.group !== "pan"
                                                           && modelData.group !== "color"
                        // A behaviour (0.26) on the row's property: marked with ≈ after its name.
                        readonly property bool hasBehavior: {
                            void EditorState.tracksRevision
                            if (keyLine.clip < 0)
                                return false
                            const b = EditorState.propertyBehavior(keyLines.trackIndex, keyLine.clip, keyLine.props[0])
                            return !!b && b.active === true
                        }
                        HoverHandler { id: lineHover }
                        // After Effects' Contents (0.28): a heading line (Contents, a part, its
                        // path, a fill or stroke, «Transform: …») drawn over the value line, with
                        // its twirl, eye and name, as AE's tree. A click on a part's name picks it,
                        // the same pick as the right column's list and the preview.
                        readonly property bool heading: modelData.kind === "heading"
                        readonly property int depth: modelData.depth || 0
                        Rectangle {
                            id: headingLine
                            visible: keyLine.heading
                            anchors.fill: parent
                            z: 50
                            color: keyLine.modelData.picked ? Theme.panelAccent : Qt.rgba(0.07, 0.08, 0.09, 1.0)
                            readonly property string partId: keyLine.modelData.partId || ""
                            function pickClip() {
                                if (EditorState.selectedTrack !== keyLines.trackIndex || EditorState.selectedClip !== keyLine.clip)
                                    EditorState.selectClip(keyLines.trackIndex, keyLine.clip)
                            }
                            function pick() {
                                if (keyLine.clip < 0)
                                    return
                                headingLine.pickClip()
                                if (headingLine.partId.length > 0)
                                    EditorState.selectShapePart(keyLines.trackIndex, keyLine.clip, headingLine.partId)
                            }
                            // Click anywhere on the line: a part is picked; any other heading folds or opens.
                            MouseArea {
                                anchors.fill: parent
                                acceptedButtons: Qt.LeftButton | Qt.RightButton
                                onClicked: mouse => {
                                    if (mouse.button === Qt.RightButton && headingLine.partId.length > 0) {
                                        // The menu keeps its ids (not «clip»: a Popup's clip is FINAL and the app did not start): picking here rebuilt this row (the menu with it).
                                        partLineMenu.menuTrack = keyLines.trackIndex
                                        partLineMenu.menuClip = keyLine.clip
                                        partLineMenu.menuPartId = headingLine.partId
                                        partLineMenu.popup(headingLine, mouse.x, mouse.y)
                                        return
                                    }
                                    if (headingLine.partId.length > 0)
                                        headingLine.pick()
                                    else if (keyLine.modelData.expandable)
                                        EditorState.setKeyframeGroupExpanded(keyLines.trackIndex, keyLine.modelData.key,
                                                                             !keyLine.modelData.expanded)
                                }
                            }
                            Row {
                                anchors.fill: parent
                                anchors.leftMargin: 4 + keyLine.depth * 12
                                spacing: 3
                                IconButton {
                                    anchors.verticalCenter: parent.verticalCenter
                                    visible: keyLine.modelData.expandable === true
                                    glyph: keyLine.modelData.expanded ? Theme.icons.chevronDown : Theme.icons.chevronRight
                                    variant: "text"
                                    buttonSize: 16
                                    iconSize: 11
                                    onClicked: EditorState.setKeyframeGroupExpanded(keyLines.trackIndex, keyLine.modelData.key,
                                                                                    !keyLine.modelData.expanded)
                                }
                                // A part's eye, or a fill's or stroke's: hides it from the picture.
                                IconButton {
                                    anchors.verticalCenter: parent.verticalCenter
                                    visible: headingLine.partId.length > 0 || !!keyLine.modelData.layerId
                                    readonly property bool shown: headingLine.partId.length > 0 ? keyLine.modelData.partVisible !== false
                                                                                                : keyLine.modelData.layerEnabled !== false
                                    glyph: shown ? Theme.icons.eye : Theme.icons.eyeOff
                                    variant: "text"
                                    buttonSize: 16
                                    iconSize: 11
                                    tooltip: shown ? qsTr("Hide") : qsTr("Show")
                                    onClicked: {
                                        // Read first: picking the clip or the part rebuilds this row.
                                        const track = keyLines.trackIndex
                                        const clip = keyLine.clip
                                        const partId = headingLine.partId
                                        const layerOf = keyLine.modelData.layerOf
                                        const layerId = keyLine.modelData.layerId
                                        const on = !shown
                                        if (clip < 0)
                                            return
                                        if (partId.length > 0) {
                                            EditorState.setShapePartVisible(track, clip, partId, on)
                                            return
                                        }
                                        // A fill or stroke belongs to a part: that part becomes the one edited.
                                        if (EditorState.selectedTrack !== track || EditorState.selectedClip !== clip)
                                            EditorState.selectClip(track, clip)
                                        EditorState.selectShapePart(track, clip, layerOf)
                                        EditorState.setStyleLayer(track, clip, layerId, { "enabled": on })
                                    }
                                }
                                IconGlyph {
                                    anchors.verticalCenter: parent.verticalCenter
                                    visible: keyLine.modelData.isGroup === true
                                    glyph: Theme.icons.folder
                                    iconSize: 11
                                    iconColor: Theme.mutedForeground
                                }
                                Text {
                                    anchors.verticalCenter: parent.verticalCenter
                                    width: Math.max(10, headingLine.width - x - (addPartButton.visible ? addPartButton.width + 6 : 0)
                                                    - (blendButton.visible ? blendButton.width + 6 : 0) - 8)
                                    text: keyLine.modelData.label || ""
                                    elide: Text.ElideRight
                                    color: Theme.panelForeground
                                    opacity: keyLine.modelData.partVisible === false ? 0.5 : 1.0
                                    font.family: Theme.fontFamily
                                    font.pixelSize: Theme.fontSizeXs
                                    font.weight: keyLine.depth <= 1 ? Font.DemiBold : Font.Normal
                                }
                            }
                            // «Add ▸» on Contents, as AE.
                            ThemedButton {
                                id: addPartButton
                                visible: keyLine.modelData.contents === true
                                anchors.right: parent.right
                                anchors.rightMargin: 4
                                anchors.verticalCenter: parent.verticalCenter
                                height: Theme.keyframeRowHeight - 4
                                variant: "secondary"
                                text: qsTr("Add") + " ▸"
                                tooltip: qsTr("Add a shape or a group to this layer")
                                onClicked: addPartMenu.popup(addPartButton, 0, addPartButton.height)
                                ThemedContextMenu {
                                    id: addPartMenu
                                    function add(kind) {
                                        headingLine.pickClip()
                                        EditorState.addShapePart(keyLines.trackIndex, keyLine.clip, kind)
                                    }
                                    ThemedMenuItem { text: qsTr("Rectangle"); onTriggered: addPartMenu.add("rectangle") }
                                    ThemedMenuItem { text: qsTr("Ellipse"); onTriggered: addPartMenu.add("ellipse") }
                                    ThemedMenuItem { text: qsTr("Star"); onTriggered: addPartMenu.add("star") }
                                    ThemedMenuItem { text: qsTr("Polygon"); onTriggered: addPartMenu.add("polygon") }
                                    ThemedMenuSeparator { }
                                    ThemedMenuItem { text: qsTr("Empty group"); onTriggered: addPartMenu.add("group") }
                                }
                            }
                            // A part's blend mode, as AE's Normal ▾ beside each group.
                            ThemedButton {
                                id: blendButton
                                visible: headingLine.partId.length > 0
                                anchors.right: parent.right
                                anchors.rightMargin: 4
                                anchors.verticalCenter: parent.verticalCenter
                                height: Theme.keyframeRowHeight - 4
                                variant: "ghost"
                                readonly property var modes: ["normal", "multiply", "screen", "overlay", "add", "darken", "lighten"]
                                readonly property var labels: [qsTr("Normal"), qsTr("Multiply"), qsTr("Screen"), qsTr("Overlay"),
                                                               qsTr("Add"), qsTr("Darken"), qsTr("Lighten")]
                                text: labels[Math.max(0, modes.indexOf(keyLine.modelData.blend || "normal"))] + " ▾"
                                tooltip: qsTr("Blend mode")
                                onClicked: blendMenu.popup(blendButton, 0, blendButton.height)
                                ThemedContextMenu {
                                    id: blendMenu
                                    Repeater {
                                        model: blendButton.modes.length
                                        delegate: ThemedMenuItem {
                                            required property int index
                                            text: blendButton.labels[index]
                                            onTriggered: EditorState.setShapePartBlend(keyLines.trackIndex, keyLine.clip,
                                                                                       headingLine.partId, blendButton.modes[index])
                                        }
                                    }
                                }
                            }
                            ThemedContextMenu {
                                id: partLineMenu
                                property int menuTrack: -1
                                property int menuClip: -1
                                property string menuPartId: ""
                                ThemedMenuItem {
                                    text: qsTr("Duplicate") + "\tCtrl+D"
                                    onTriggered: EditorState.duplicateShapePart(partLineMenu.menuTrack, partLineMenu.menuClip, partLineMenu.menuPartId)
                                }
                                ThemedMenuItem {
                                    text: qsTr("Group") + "\tCtrl+G"
                                    onTriggered: EditorState.groupShapePart(partLineMenu.menuTrack, partLineMenu.menuClip, partLineMenu.menuPartId)
                                }
                                ThemedMenuItem {
                                    visible: keyLine.modelData.isGroup === true
                                    height: visible ? implicitHeight : 0
                                    text: qsTr("Ungroup")
                                    onTriggered: EditorState.ungroupShapePart(partLineMenu.menuTrack, partLineMenu.menuClip, partLineMenu.menuPartId)
                                }
                                ThemedMenuSeparator { }
                                ThemedMenuItem {
                                    text: qsTr("Delete")
                                    onTriggered: EditorState.removeShapePart(partLineMenu.menuTrack, partLineMenu.menuClip, partLineMenu.menuPartId)
                                }
                            }
                        }
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
                        // 100 % fills the canvas on its tighter axis, as the inspector reads it.
                        readonly property real scaleNow: {
                            const cw = Math.max(1, EditorState.projectFile.projectWidth())
                            const ch = Math.max(1, EditorState.projectFile.projectHeight())
                            return Math.max(valueOf("width") / cw, valueOf("height") / ch)
                        }
                        property var scaleStart: null
                        // 100 % on each axis: the box Reset gives the clip (After Effects' two values).
                        readonly property var naturalSize: {
                            void EditorState.tracksRevision
                            return keyLine.clip >= 0 ? EditorState.clipNaturalSize(keyLines.trackIndex, keyLine.clip) : ({})
                        }
                        function beginScale() {
                            const track = keyLines.trackIndex
                            const c = EditorState.clipAt(track, keyLine.clip) || {}
                            keyLine.scaleStart = {
                                "x": valueOf("x"), "y": valueOf("y"),
                                "w": valueOf("width"), "h": valueOf("height"), "s": keyLine.scaleNow,
                                "fx": valueOf("anchorX"), "fy": valueOf("anchorY"),
                                "text": c.kind === "text",
                                "px": (c.textStyle && c.textStyle.pixelSize) || 64,
                                "moving": EditorState.clipAnimatedProperties(track, keyLine.clip).some(
                                              (p) => p === "x" || p === "y"),
                                "sized": EditorState.clipAnimatedProperties(track, keyLine.clip).some(
                                             (p) => p === "width" || p === "height")
                            }
                        }
                        // Scale grows the box around its centre, as the inspector's slider; with
                        // Position animated only the size changes (no stray Position keys).
                        function writeScale(stored) {
                            const st = keyLine.scaleStart
                            if (!st || st.s <= 0)
                                return
                            const k = Math.max(0.01, stored) / st.s
                            keyLine.writeSize(st.w * k, st.h * k)
                        }
                        // One axis's % (of the natural box); with the chain on, the other follows.
                        function writeScaleAxis(horizontal, fraction) {
                            const st = keyLine.scaleStart
                            const nat = keyLine.naturalSize
                            if (!st || !nat.w || !nat.h)
                                return
                            const f = Math.max(0.0001, fraction)
                            if (horizontal) {
                                const w = f * nat.w
                                keyLine.writeSize(w, root.scaleLinked ? st.h * (w / Math.max(1, st.w)) : st.h)
                            } else {
                                const h = f * nat.h
                                keyLine.writeSize(root.scaleLinked ? st.w * (h / Math.max(1, st.h)) : st.w, h)
                            }
                        }
                        function writeSize(newW, newH) {
                            const st = keyLine.scaleStart
                            if (!st)
                                return
                            const w = Math.max(1, newW)
                            const h = Math.max(1, newH)
                            const k = h / Math.max(1, st.h)
                            // The anchor point stays put (the centre when it is not moved).
                            const x = st.x + (st.w - w) * (isNaN(st.fx) ? 0.5 : st.fx)
                            const y = st.y + (st.h - h) * (isNaN(st.fy) ? 0.5 : st.fy)
                            const track = keyLines.trackIndex
                            const clip = keyLine.clip
                            if (!st.sized && !st.moving) {
                                if (st.text)
                                    EditorState.previewSetTextRect(track, clip, x, y, w, h, Math.round(st.px * k))
                                else
                                    EditorState.previewSetClipRect(track, clip, x, y, w, h)
                                return
                            }
                            const at = EditorState.playheadSeconds
                            EditorState.previewSetPropertyValue(track, clip, "width", at, w)
                            EditorState.previewSetPropertyValue(track, clip, "height", at, h)
                            if (!st.moving) {
                                EditorState.previewSetPropertyValue(track, clip, "x", at, x)
                                EditorState.previewSetPropertyValue(track, clip, "y", at, y)
                            }
                        }
                        // The values the line shows and edits: [{prop, tag, toDisplay, fromDisplay,
                        // min, max, step, decimals, suffix}].
                        readonly property var hotValues: {
                            const id = (v) => v
                            const pct = (v) => v * 100
                            const unPct = (d) => d / 100
                            const plain = (prop, tag, step, decimals, suffix) => ({
                                "prop": prop, "tag": tag, "toDisplay": id, "fromDisplay": id,
                                "min": -1e9, "max": 1e9, "step": step, "decimals": decimals, "suffix": suffix })
                            const group = keyLine.joined ? keyLine.modelData.group : ""
                            // A colour line (0.28) shows a swatch, not numbers.
                            if (group === "color")
                                return []
                            if (group === "position")
                                return [plain("x", "X", 1, 0, ""), plain("y", "Y", 1, 0, "")]
                            if (group === "anchor") {
                                // In the box's own pixels, as After Effects; stored as fractions.
                                const w = Math.max(1, valueOf("width"))
                                const h = Math.max(1, valueOf("height"))
                                return [{ "prop": "anchorX", "tag": "X", "toDisplay": (f) => f * w, "fromDisplay": (d) => d / w,
                                          "min": -1e6, "max": 1e6, "step": 1, "decimals": 0, "suffix": "" },
                                        { "prop": "anchorY", "tag": "Y", "toDisplay": (f) => f * h, "fromDisplay": (d) => d / h,
                                          "min": -1e6, "max": 1e6, "step": 1, "decimals": 0, "suffix": "" }]
                            }
                            if (group === "rotation")
                                return [plain("rotation", "", 0.5, 1, "°")]
                            if (group === "scale") {
                                // After Effects' two values (width, height %) and the chain between.
                                const nat = keyLine.naturalSize
                                const nw = Math.max(1, nat.w || 1)
                                const nh = Math.max(1, nat.h || 1)
                                return [{ "link": true },
                                        { "prop": "width", "value": valueOf("width") / nw, "toDisplay": pct,
                                          "fromDisplay": unPct, "min": 1, "max": 5000, "step": 0.5, "decimals": 1,
                                          "suffix": "", "begin": keyLine.beginScale,
                                          "write": (f) => keyLine.writeScaleAxis(true, f) },
                                        { "prop": "height", "value": valueOf("height") / nh, "toDisplay": pct,
                                          "fromDisplay": unPct, "min": 1, "max": 5000, "step": 0.5, "decimals": 1,
                                          "suffix": " %", "begin": keyLine.beginScale,
                                          "write": (f) => keyLine.writeScaleAxis(false, f) }]
                            }
                            if (group === "opacity")
                                return [{ "prop": "opacity", "tag": "", "toDisplay": pct, "fromDisplay": unPct,
                                          "min": 0, "max": 100, "step": 0.5, "decimals": 0, "suffix": " %" }]
                            if (group === "volume")
                                return [{ "prop": "volume", "tag": "",
                                          "toDisplay": (g) => g <= 0.001 ? -60 : 20 * Math.log10(g),
                                          "fromDisplay": (d) => d <= -59.9 ? 0 : Math.min(2, Math.pow(10, d / 20)),
                                          "min": -60, "max": 6, "step": 0.25, "decimals": 1, "suffix": " dB" }]
                            if (group === "pan")
                                return [{ "prop": "pan", "tag": "", "toDisplay": pct, "fromDisplay": unPct,
                                          "min": -100, "max": 100, "step": 0.5, "decimals": 0, "suffix": "" }]
                            const prop = keyLine.modelData.prop
                            if (prop === "width" || prop === "height" || prop === "x" || prop === "y")
                                return [plain(prop, "", 1, 0, "")]
                            if (prop === "anchorX" || prop === "anchorY") {
                                const side = Math.max(1, valueOf(prop === "anchorX" ? "width" : "height"))
                                return [{ "prop": prop, "tag": "", "toDisplay": (f) => f * side, "fromDisplay": (d) => d / side,
                                          "min": -1e6, "max": 1e6, "step": 1, "decimals": 0, "suffix": "" }]
                            }
                            // Contents (0.28): a fill's or stroke's opacity is stored 0..1 and reads as a
                            // percentage; a part's scale and opacity are already percentages, its angles degrees.
                            if (/\.layer\.[^.]+\.opacity$/.test(prop))
                                return [{ "prop": prop, "tag": "", "toDisplay": pct, "fromDisplay": unPct,
                                          "min": 0, "max": 100, "step": 0.5, "decimals": 0, "suffix": " %" }]
                            if (/^part\.[^.]+\.(scaleX|scaleY|opacity)$/.test(prop))
                                return [plain(prop, "", 0.5, 1, " %")]
                            if (/^part\.[^.]+\.(rotation|skew|skewAxis)$/.test(prop))
                                return [plain(prop, "", 0.5, 1, "°")]
                            const v = valueOf(prop)
                            return [plain(prop, "", Math.abs(v) >= 10 ? 1 : 0.01, Math.abs(v) >= 10 ? 0 : 2, "")]
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
                            if (group === "volume") {
                                // In dB, as the audio inspector reads it.
                                const g = valueOf("volume")
                                return isNaN(g) ? "—" : (g <= 0.0001 ? "-∞ dB"
                                                                      : (20 * Math.log10(g)).toFixed(1) + " dB")
                            }
                            if (group === "pan") {
                                const p = valueOf("pan")
                                if (isNaN(p))
                                    return "—"
                                if (Math.abs(p) < 0.005)
                                    return qsTranslate("AudioInspector", "C")
                                return (p < 0 ? qsTranslate("AudioInspector", "L %1")
                                              : qsTranslate("AudioInspector", "R %1")).arg(Math.round(Math.abs(p) * 100))
                            }
                            const v = valueOf(keyLine.modelData.prop)
                            return isNaN(v) ? "—" : (Math.abs(v) >= 10 ? String(Math.round(v)) : v.toFixed(2))
                        }
                        readonly property string iconName: {
                            switch (keyLine.joined ? keyLine.modelData.group : "") {
                            case "anchor": return "locate-fixed"
                            case "position": return "move"
                            case "rotation": return "rotate-cw"
                            case "scale": return "scaling"
                            case "opacity": return Theme.icons.blend
                            case "volume": return "volume-2"
                            case "pan": return "arrow-right-left"
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
                        // After Effects' stopwatch (0.25): lit while the property is animated. A
                        // click starts the animation with a key at the playhead, or, lit, takes
                        // every key away and leaves the value it has now.
                        readonly property bool animated: {
                            void EditorState.tracksRevision
                            if (keyLine.clip < 0)
                                return false
                            const animatedProps = EditorState.clipAnimatedProperties(keyLines.trackIndex, keyLine.clip)
                            return keyLine.props.some((p) => animatedProps.indexOf(p) >= 0)
                        }
                        IconButton {
                            id: lineIcon
                            x: 16
                            anchors.verticalCenter: parent.verticalCenter
                            enabled: keyLine.clip >= 0
                            glyph: "clock"
                            variant: "text"
                            buttonSize: 20
                            iconSize: 13
                            active: keyLine.animated
                            tooltip: keyLine.animated ? qsTr("Stop animating (removes its keyframes)")
                                                      : qsTr("Animate: a keyframe at the playhead")
                            onClicked: {
                                if (keyLine.animated)
                                    EditorState.stopAnimating(keyLines.trackIndex, keyLine.clip, keyLine.props.slice(),
                                                              EditorState.playheadSeconds)
                                else if (keyLine.keysHere.length === 0)
                                    keyLine.toggleKeyHere()
                            }
                        }
                        // A click on the name picks every key of the line on its clip, as a click
                        // on a property's name does in After Effects; Shift or Ctrl add them.
                        function pickAllKeys(modifiers) {
                            const tools = root.keyframeTools
                            if (!tools || keyLine.clip < 0)
                                return
                            const track = keyLines.trackIndex
                            const clip = keyLine.clip
                            const animated = EditorState.clipAnimatedProperties(track, clip)
                            const add = !!(modifiers & (Qt.ShiftModifier | Qt.ControlModifier))
                            const out = add && tools.track === track ? tools.keys.slice() : []
                            for (const prop of keyLine.props) {
                                if (animated.indexOf(prop) < 0)
                                    continue
                                for (const k of (EditorState.clipKeyframes(track, clip, prop) || [])) {
                                    const ref = { clip: clip, prop: prop, seconds: k.seconds }
                                    if (!out.some((o) => tools.sameKey(o, ref)))
                                        out.push(ref)
                                }
                            }
                            if (EditorState.selectedTrack !== track || EditorState.selectedClip !== clip)
                                EditorState.selectClip(track, clip)
                            tools.pick(track, out)
                            // In the curve editor, its curve is the one shaped.
                            tools.focusProp = ""
                            tools.focusProp = keyLine.props[0]
                        }
                        MouseArea {
                            anchors.left: parent.left
                            anchors.leftMargin: 36
                            anchors.right: resetButton.visible ? resetButton.left : prevKeyButton.left
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: (mouse) => keyLine.pickAllKeys(mouse.modifiers)
                            ThemedToolTip {
                                visible: parent.containsMouse
                                text: qsTr("Click to pick all its keyframes")
                            }
                        }
                        Column {
                            anchors.left: parent.left
                            // Contents' lines (0.28) step in under their heading.
                            anchors.leftMargin: 40 + Math.max(0, keyLine.depth - 2) * 12
                            anchors.right: prevKeyButton.left
                            anchors.rightMargin: 2
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 0
                            Text {
                                width: parent.width
                                text: (keyLine.modelData.axis && !keyLine.modelData.separated ? "· " : "")
                                      + keyRowsNames.rowLabel(keyLine.modelData)
                                      + (keyLine.hasBehavior ? "  ≈" : "")
                                color: Theme.panelForeground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeXs
                                elide: Text.ElideRight
                            }
                            // The values, as After Effects' blue numbers (0.25): dragged sideways or
                            // clicked to type; animated, the change is a key at the playhead.
                            Row {
                                spacing: 6
                                visible: keyLine.clip >= 0
                                // «Color» (0.28): the colour at the playhead; picking one writes the four
                                // channels in one undo step (a key at the playhead when it is animated).
                                ColorSwatchField {
                                    visible: keyLine.modelData.group === "color"
                                    anchors.verticalCenter: parent.verticalCenter
                                    showHex: false
                                    swatchSize: 14
                                    readonly property var channels: keyLine.modelData.group === "color" ? keyLine.props : []
                                    hex: {
                                        if (channels.length < 4)
                                            return "#ffffffff"
                                        const h = (v) => ("0" + Math.round(Math.max(0, Math.min(1, v)) * 255).toString(16)).slice(-2)
                                        return "#" + h(keyLine.valueOf(channels[3])) + h(keyLine.valueOf(channels[0]))
                                               + h(keyLine.valueOf(channels[1])) + h(keyLine.valueOf(channels[2]))
                                    }
                                    tooltip: qsTr("Colour")
                                    onEdited: value => {
                                        // Read first (selecting the clip rebuilds this row), and the drag always closes.
                                        const c = Qt.color(value)
                                        const track = keyLines.trackIndex
                                        const clip = keyLine.clip
                                        const ch = channels.slice()
                                        if (ch.length < 4)
                                            return
                                        if (EditorState.selectedTrack !== track || EditorState.selectedClip !== clip)
                                            EditorState.selectClip(track, clip)
                                        const values = [c.r, c.g, c.b, c.a]
                                        EditorState.beginPreviewDrag(qsTr("Colour"))
                                        try {
                                            for (let i = 0; i < 4; ++i)
                                                EditorState.previewSetPropertyValue(track, clip, ch[i], EditorState.playheadSeconds,
                                                                                    values[i])
                                        } finally {
                                            EditorState.commitPreviewDrag()
                                        }
                                    }
                                }
                                Repeater {
                                    model: keyLine.hotValues
                                    delegate: Row {
                                        required property var modelData
                                        spacing: 2
                                        // Scale's chain: both values together, or each on its own.
                                        IconButton {
                                            visible: !!modelData.link
                                            anchors.verticalCenter: parent.verticalCenter
                                            glyph: root.scaleLinked ? Theme.icons.link : Theme.icons.unlink
                                            variant: "text"
                                            buttonSize: 16
                                            iconSize: 11
                                            active: root.scaleLinked
                                            tooltip: root.scaleLinked ? qsTr("Constrain proportions: on")
                                                                      : qsTr("Constrain proportions: off")
                                            onClicked: root.scaleLinked = !root.scaleLinked
                                        }
                                        Text {
                                            visible: !!modelData.tag
                                            anchors.verticalCenter: parent.verticalCenter
                                            text: modelData.tag || ""
                                            color: Theme.mutedForeground
                                            font.family: Theme.fontFamily
                                            font.pixelSize: Theme.fontSizeTiny
                                        }
                                        ScrubValue {
                                            visible: !modelData.link
                                            trackIndex: keyLines.trackIndex
                                            clipIndex: keyLine.clip
                                            prop: modelData.prop || ""
                                            value: modelData.value !== undefined ? modelData.value
                                                                                 : keyLine.valueOf(modelData.prop)
                                            // The chain between the two Scale values has none.
                                            toDisplay: modelData.toDisplay || ((v) => v)
                                            fromDisplay: modelData.fromDisplay || ((d) => d)
                                            // The chain's entry has no numbers: defaults, so nothing undefined is assigned.
                                            displayMin: modelData.min ?? -1e9
                                            displayMax: modelData.max ?? 1e9
                                            step: modelData.step ?? 1
                                            decimals: modelData.decimals ?? 0
                                            suffix: modelData.suffix ?? ""
                                            write: modelData.write || null
                                            onBegun: if (modelData.begin) modelData.begin()
                                        }
                                    }
                                }
                            }
                            Text {
                                visible: keyLine.clip < 0
                                width: parent.width
                                text: "—"
                                color: Theme.mutedForeground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeTiny
                            }
                        }
                        IconButton {
                            id: resetButton
                            anchors.right: prevKeyButton.left
                            anchors.verticalCenter: parent.verticalCenter
                            visible: keyLine.resettable && keyLine.clip >= 0 && lineHover.hovered
                            glyph: Theme.icons.reset
                            variant: "text"
                            buttonSize: 18
                            iconSize: 12
                            tooltip: qsTr("Reset")
                            onClicked: EditorState.resetClipProperties(keyLines.trackIndex, keyLine.clip, keyLine.props)
                        }
                        // After Effects' keyframe navigator: ◀ previous, ◆ add/remove here, ▶ next.
                        IconButton {
                            id: prevKeyButton
                            anchors.right: keyButton.left
                            anchors.verticalCenter: parent.verticalCenter
                            visible: keyLine.animated
                            width: visible ? implicitWidth : 0
                            glyph: Theme.icons.chevronLeft
                            variant: "text"
                            buttonSize: 16
                            iconSize: 11
                            tooltip: qsTr("Previous keyframe")
                            onClicked: keyLine.stepKey(false)
                        }
                        IconButton {
                            id: nextKeyButton
                            anchors.right: moreButton.left
                            anchors.verticalCenter: parent.verticalCenter
                            visible: keyLine.animated
                            width: visible ? implicitWidth : 0
                            glyph: Theme.icons.chevronRight
                            variant: "text"
                            buttonSize: 16
                            iconSize: 11
                            tooltip: qsTr("Next keyframe")
                            onClicked: keyLine.stepKey(true)
                        }
                        IconButton {
                            id: keyButton
                            anchors.right: nextKeyButton.left
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
                            ThemedMenuItem {
                                // After Effects' Separate Dimensions: X and Y with keys of their own.
                                visible: keyLine.modelData.group === "position"
                                height: visible ? implicitHeight : 0
                                text: qsTr("Separate dimensions")
                                icon.name: EditorState.positionLinked ? "" : Theme.icons.check
                                onTriggered: EditorState.positionLinked = !EditorState.positionLinked
                            }
                            ThemedMenuSeparator {}
                            ThemedMenuItem {
                                // After Effects' expressions without code (0.26): loop, wiggle, speed.
                                text: qsTr("Behavior…")
                                icon.name: keyLine.hasBehavior ? Theme.icons.check : ""
                                onTriggered: behaviorDialog.openFor(keyLines.trackIndex, keyLine.clip, keyLine.props,
                                                                    keyRowsNames.rowLabel(keyLine.modelData),
                                                                    keyLines.expressionTargets())
                            }
                        }

                        PropertyBehaviorDialog {
                            id: behaviorDialog
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
