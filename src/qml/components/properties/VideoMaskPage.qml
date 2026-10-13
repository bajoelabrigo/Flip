import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Shapes
import Drift
import ".."

// Video > Mask, laid out like CapCut's: the clip's masks as chips with a "+" to add another, a
// grid of shape tiles that sets the shape of the mask being edited, and under it that mask's
// settings. Everything happens here with the video or photo still selected: the mask lives on an
// adjustment pinned to the clip, and this page edits it in place (EditorState.focusedMask) instead
// of moving the selection to the mask's lane, which used to swap the whole panel away.
Column {
    id: root

    spacing: Theme.spacingLg

    property int revision: 0
    Connections {
        target: EditorState
        function onSelectionChanged() { root.revision++ }
        function onSelectedClipDataChanged() { root.revision++ }
        function onTracksChanged() { root.revision++ }
        function onFocusedMaskChanged() { root.revision++ }
    }

    readonly property var clipData: {
        void revision
        return EditorState.selectedClipData || ({})
    }
    readonly property bool visual: clipData.kind === "video" || clipData.kind === "image"

    readonly property var masks: {
        void revision
        if (!visual)
            return []
        return EditorState.linkedMaskClips(EditorState.selectedTrack, EditorState.selectedClip) || []
    }
    // The mask being edited: the focused one, else the last added.
    readonly property var active: {
        void revision
        if (masks.length === 0)
            return null
        const focused = EditorState.focusedMask()
        for (const m of masks) {
            if (m.id === focused)
                return m
        }
        return masks[masks.length - 1]
    }
    readonly property var activeMask: {
        void revision
        if (!active)
            return ({})
        const d = EditorState.clipAt(active.track, active.index)
        return (d && d.mask) || ({})
    }
    readonly property string shape: activeMask.shape || "none"
    // The tile id of the mask: a smooth freeform is the Pen.
    readonly property string tileId: shape === "freeform" && activeMask.smooth ? "pen" : shape
    readonly property bool isMediaMask: shape === "media"

    // CapCut order. "none" removes the mask being edited.
    readonly property var tiles: [
        { id: "none", label: qsTr("None") },
        { id: "rectangle", label: qsTr("Rectangle") },
        { id: "ellipse", label: qsTr("Circle") },
        { id: "bars", label: qsTr("Film strip") },
        { id: "star", label: qsTr("Stars") },
        { id: "heart", label: qsTr("Heart") },
        { id: "text", label: qsTr("Text") },
        { id: "freeform", label: qsTr("Freeform") },
        { id: "pen", label: qsTr("Pen") },
        { id: "gradient", label: qsTr("Gradient") }
    ]

    function shapeName(id) {
        for (const t of tiles) {
            if (t.id === id)
                return t.label
        }
        return id === "media" ? qsTr("Cutout") : id
    }

    function writeMask(changes) {
        if (!active)
            return
        const mask = Object.assign({}, activeMask, changes)
        EditorState.setClipMask(active.track, active.index, mask)
    }

    // A tile sets the shape of the mask being edited, or adds the first one.
    function pickTile(id) {
        if (id === "none") {
            if (active)
                EditorState.removeLinkedMask(active.track, active.index)
            return
        }
        if (!active || isMediaMask) {
            EditorState.addMaskToClipInPlace(EditorState.selectedTrack, EditorState.selectedClip, id)
            return
        }
        if (id === tileId)
            return
        const changes = { shape: id === "pen" ? "freeform" : id, smooth: id === "pen" }
        // A new freeform starts from the seeded points of the mask's box, not stale ones.
        if (id === "pen" || id === "freeform")
            changes.points = []
        if (id === "text" && !activeMask.text) {
            changes.text = qsTr("TEXT")
            changes.w = 0.8
            changes.h = 0.35
        }
        if (id === "gradient") {
            changes.y = 0.5
            changes.h = 0.4
        }
        writeMask(changes)
    }

    // The preview shows the mask's handles while this page is open, as on CapCut.
    property bool raisedMaskEdit: false
    readonly property bool wantsHandles: visible && !!active && !isMediaMask
    onWantsHandlesChanged: {
        if (wantsHandles && !EditorState.preview.maskEditMode) {
            EditorState.preview.maskEditMode = true
            raisedMaskEdit = true
        } else if (!wantsHandles && raisedMaskEdit) {
            EditorState.preview.maskEditMode = false
            raisedMaskEdit = false
        }
    }
    Component.onDestruction: {
        if (raisedMaskEdit)
            EditorState.preview.maskEditMode = false
    }

    // --- Mask: the clip's masks, plus "+" ----------------------------------------------------
    Row {
        width: parent.width
        spacing: Theme.spacingSm

        IconGlyph {
            glyph: Theme.icons.shapes
            iconSize: 16
            iconColor: Theme.foreground
            anchors.verticalCenter: parent.verticalCenter
        }
        Text {
            text: qsTr("Mask")
            color: Theme.foreground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSm
            font.weight: Font.Medium
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    Flow {
        width: parent.width
        spacing: Theme.spacingSm
        visible: root.visual

        Repeater {
            model: root.masks
            delegate: Rectangle {
                id: chip
                required property var modelData
                required property int index
                readonly property bool current: root.active && root.active.id === modelData.id
                height: Theme.controlHeightSm
                width: chipRow.implicitWidth + Theme.spacingMd * 2
                radius: height / 2
                color: current ? Theme.popoverHover : Theme.panelAccent
                border.width: current ? 1 : 0
                border.color: Theme.primary

                Row {
                    id: chipRow
                    anchors.centerIn: parent
                    spacing: Theme.spacingXs

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: qsTr("Mask %1").arg(chip.index + 1) + "  "
                              + (chip.modelData.name && chip.modelData.name.length > 0
                                 ? chip.modelData.name
                                 : root.shapeName(chip.modelData.shape === "freeform" && chip.modelData.smooth
                                                  ? "pen" : chip.modelData.shape))
                        color: chip.current ? Theme.foreground : Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                        font.weight: chip.current ? Font.Medium : Font.Normal
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: EditorState.setFocusedMask(chip.modelData.id)
                }
            }
        }

        IconButton {
            glyph: Theme.icons.plus
            variant: "ghost"
            buttonSize: Theme.controlHeightSm
            iconSize: 14
            enabled: root.visual
            tooltip: qsTr("Add another mask")
            onClicked: EditorState.addMaskToClipInPlace(EditorState.selectedTrack,
                                                        EditorState.selectedClip,
                                                        root.tileId === "none" || root.isMediaMask
                                                        ? "rectangle" : root.tileId)
        }
    }

    Text {
        visible: !root.visual
        width: parent.width
        wrapMode: Text.WordWrap
        text: qsTr("Select a video or image clip to add a mask.")
        color: Theme.warning
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }

    // --- The shape tiles ------------------------------------------------------------------
    MaskShapeTiles {
        width: parent.width
        visible: root.visual
        tiles: root.tiles
        currentId: root.active ? root.tileId : "none"
        editing: !!root.active
        onPicked: (id) => root.pickTile(id)
    }

    // --- Mask settings --------------------------------------------------------------------
    Rectangle {
        visible: !!root.active
        width: parent.width
        height: Theme.borderWidth
        color: Theme.panelBorder
    }

    Text {
        visible: !!root.active
        text: qsTr("Mask settings")
        color: Theme.foreground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeSm
        font.weight: Font.Medium
    }

    // A cutout is a coverage map, not a shape: only invert and removal apply.
    Text {
        visible: root.isMediaMask
        width: parent.width
        wrapMode: Text.WordWrap
        text: qsTr("This mask is a cutout. Pick a shape above to add a shape mask next to it.")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }

    // Text mask: the words whose outline shows the clip.
    Column {
        visible: root.shape === "text"
        width: parent.width
        spacing: Theme.spacingSm

        Text {
            text: qsTr("Mask text")
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }
        ThemedTextField {
            width: parent.width
            placeholderText: qsTr("Write the text")
            text: root.activeMask.text || ""
            onEditingFinished: {
                if (text !== (root.activeMask.text || ""))
                    root.writeMask({ text: text })
            }
        }
    }

    // Pen and freeform: the points are the shape.
    Column {
        visible: root.shape === "freeform"
        width: parent.width
        spacing: Theme.spacingSm

        Text {
            width: parent.width
            wrapMode: Text.WordWrap
            text: qsTr("%1 points. Drag a point in the preview to move it, click a + on a side to add one there, and right-click a point (or select it and press Delete) to remove it.")
                  .arg((root.activeMask.points || []).length)
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }

        Row {
            width: parent.width
            spacing: Theme.spacingSm

            ThemedButton {
                width: (parent.width - parent.spacing) / 2
                glyph: Theme.icons.pointAdd
                text: qsTr("Add point")
                tooltip: qsTr("Adds a point in the middle of the longest side")
                onClicked: {
                    const pts = root.activeMask.points || []
                    if (pts.length < 2)
                        return
                    let best = 0
                    let bestLen = -1
                    for (let i = 0; i < pts.length; ++i) {
                        const a = pts[i]
                        const b = pts[(i + 1) % pts.length]
                        const len = Math.hypot(b.x - a.x, b.y - a.y)
                        if (len > bestLen) {
                            bestLen = len
                            best = i
                        }
                    }
                    const a = pts[best]
                    const b = pts[(best + 1) % pts.length]
                    EditorState.insertMaskPoint(root.active.track, root.active.index, best + 1,
                                                (a.x + b.x) / 2, (a.y + b.y) / 2)
                    EditorState.maskPointFocus = best + 1
                }
            }

            ThemedButton {
                width: (parent.width - parent.spacing) / 2
                glyph: Theme.icons.pointRemove
                text: qsTr("Delete point")
                enabled: (root.activeMask.points || []).length > 3
                tooltip: EditorState.maskPointFocus >= 0
                         ? qsTr("Removes the selected point")
                         : qsTr("Removes the last point. Click a point in the preview to choose another.")
                onClicked: {
                    const pts = root.activeMask.points || []
                    const at = EditorState.maskPointFocus >= 0 && EditorState.maskPointFocus < pts.length
                               ? EditorState.maskPointFocus : pts.length - 1
                    EditorState.removeMaskPoint(root.active.track, root.active.index, at)
                    EditorState.maskPointFocus = -1
                }
            }
        }

        Row {
            width: parent.width
            spacing: Theme.spacingSm

            IconGlyph {
                glyph: Theme.icons.penCurve
                iconSize: 16
                iconColor: Theme.mutedForeground
                anchors.verticalCenter: parent.verticalCenter
            }
            Text {
                text: qsTr("Smooth curves (pen)")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
                anchors.verticalCenter: parent.verticalCenter
            }
            ThemedSwitch {
                checked: !!root.activeMask.smooth
                onToggled: root.writeMask({ smooth: checked })
            }
        }
    }

    // Position, size, rotation and feather: the same keyframable rows as the Masks tab, reached
    // through the selected clip (redirectToKeyframeHost lands on the focused mask).
    Repeater {
        model: [
            { key: "mask.x", label: qsTr("Center X"), def: 0.5, decimals: 3, min: 0, max: 1,
              shapes: ["rectangle", "ellipse", "star", "heart", "text", "gradient"] },
            { key: "mask.y", label: qsTr("Center Y"), def: 0.5, decimals: 3, min: 0, max: 1,
              shapes: ["rectangle", "ellipse", "star", "heart", "text", "gradient"] },
            { key: "mask.w", label: qsTr("Width"), def: 0.6, decimals: 3, min: 0.05, max: 1,
              shapes: ["rectangle", "ellipse", "star", "heart", "text"] },
            { key: "mask.h", label: qsTr("Height"), def: 0.6, decimals: 3, min: 0.05, max: 1,
              shapes: ["rectangle", "ellipse", "star", "heart", "bars", "text"] },
            { key: "mask.h", label: qsTr("Fade length"), def: 0.4, decimals: 3, min: 0.01, max: 1,
              shapes: ["gradient"] },
            { key: "mask.rotation", label: qsTr("Rotation"), def: 0, decimals: 1,
              min: -180, max: 180, unit: "°",
              shapes: ["rectangle", "ellipse", "star", "heart", "text", "gradient"] },
            { key: "mask.feather", label: qsTr("Feather"), def: 0, decimals: 0,
              min: 0, max: 64, unit: "px",
              shapes: ["rectangle", "ellipse", "star", "heart", "bars", "freeform", "text"] },
            { key: "mask.expand", label: qsTr("Expand"), def: 0, decimals: 3, min: -0.3, max: 0.3,
              shapes: ["rectangle", "ellipse", "star", "heart", "bars", "freeform", "text", "gradient"] },
            { key: "mask.opacity", label: qsTr("Mask opacity"), def: 1, decimals: 2, min: 0, max: 1,
              percent: true,
              shapes: ["rectangle", "ellipse", "star", "heart", "bars", "freeform", "text", "gradient"] }
        ]
        delegate: PropertyKeyframeRow {
            required property var modelData
            width: root.width
            visible: !!root.active && modelData.shapes.indexOf(root.shape) >= 0
            propDef: {
                const own = root.activeMask[modelData.key.substring(5)]
                return Object.assign({}, modelData, { def: own !== undefined ? own : modelData.def })
            }
            keyframeList: {
                const keys = root.activeMask.keyframes
                const entry = keys && keys[modelData.key.substring(5)]
                return (entry && entry.points) || []
            }
            useSlider: true
            sliderFrom: modelData.min
            sliderTo: modelData.max
            unit: modelData.unit || ""
            percent: !!modelData.percent
        }
    }

    // What the masks do: cut the clip (CapCut's mask), or keep the clip whole and only limit
    // where its effects and colour show.
    Row {
        visible: root.masks.length > 0
        width: parent.width
        spacing: Theme.spacingSm
        Text {
            width: parent.width - limitSwitch.width - Theme.spacingSm
            anchors.verticalCenter: parent.verticalCenter
            wrapMode: Text.WordWrap
            text: limitSwitch.checked
                  ? qsTr("The masks limit the effects: inside, the clip's effects and colour; outside, the clip as it is")
                  : qsTr("Use the masks only for the effects (the clip stays whole)")
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }
        ThemedSwitch {
            id: limitSwitch
            checked: !!(EditorState.selectedClipData && EditorState.selectedClipData.masksLimitEffects)
            onToggled: EditorState.setMasksLimitEffects(EditorState.selectedTrack, EditorState.selectedClip, checked)
        }
    }

    // The focused mask on or off, kept with its settings.
    Row {
        visible: !!root.active
        width: parent.width
        spacing: Theme.spacingSm
        Text {
            text: qsTr("Mask on")
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
            anchors.verticalCenter: parent.verticalCenter
        }
        ThemedSwitch {
            checked: root.activeMask.enabled !== false
            onToggled: root.writeMask({ enabled: checked })
        }
    }

    // Invert, and how this mask folds into the ones before it.
    Row {
        visible: !!root.active
        width: parent.width
        spacing: Theme.spacingSm

        IconGlyph {
            glyph: Theme.icons.invert
            iconSize: 16
            iconColor: Theme.mutedForeground
            anchors.verticalCenter: parent.verticalCenter
        }
        Text {
            text: qsTr("Invert")
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
            anchors.verticalCenter: parent.verticalCenter
        }
        ThemedSwitch {
            checked: !!root.activeMask.invert
            onToggled: root.writeMask({ invert: checked })
        }
    }

    Column {
        visible: !!root.active && root.masks.length > 1 && !root.isMediaMask
        width: parent.width
        spacing: Theme.spacingSm

        Text {
            text: qsTr("Combine with the masks before it")
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }
        ThemedComboBox {
            width: parent.width
            model: ["add", "subtract", "intersect"]
            readonly property var labels: ({
                "add": qsTr("Add"),
                "subtract": qsTr("Subtract"),
                "intersect": qsTr("Intersect")
            })
            displayText: labels[model[currentIndex]] || model[currentIndex]
            currentIndex: Math.max(0, model.indexOf(root.activeMask.op || "add"))
            onActivated: root.writeMask({ op: model[currentIndex] })
        }
    }

    ThemedButton {
        visible: !!root.active
        width: parent.width
        text: root.isMediaMask ? qsTr("Remove cutout") : qsTr("Remove this mask")
        variant: "destructive"
        glyph: Theme.icons.trash
        onClicked: EditorState.removeLinkedMask(root.active.track, root.active.index)
    }
}
