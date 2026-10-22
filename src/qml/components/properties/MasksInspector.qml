import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

Item {
    id: root

    property int clipDataRevision: 0
    readonly property var clipData: {
        void clipDataRevision
        return EditorState.selectedClipData
    }
    readonly property bool hasSelection: !!clipData && Object.keys(clipData).length > 0
    readonly property string clipKind: hasSelection ? (clipData.kind || "") : ""
    // The tab is only offered for a mask adjustment (this is its payload) or a video-effects one
    // (where a mask scopes where the chain lands). Masks are added from the assets panel and
    // edited by selecting the mask clip, so a media clip never reaches here.
    readonly property string maskShape: (clipData.mask && clipData.mask.shape) || "none"
    // Media is a raster mask whose pixels are the coverage map (see core/Mask.h). The parametric
    // geometry does place it, but a segmentation matte is full-frame by construction and nudging
    // its rect only ever crops the subject, so the sliders stay hidden and invert plus removal
    // are what is offered.
    readonly property bool isMedia: maskShape === "media"
    // A standalone adjustment layer carries a stack of masks of its own; the fields below edit the
    // one in focus.
    readonly property var layerMasks: (hasSelection && clipData.layerMasks) || []
    readonly property bool isLayer: hasSelection && clipKind === "adjustment" && clipData.adjustmentKind === "videoEffects"
    readonly property int layerFocus: hasSelection ? (clipData.layerMaskFocus || 0) : 0
    // Adjust > Mask sets the shape with its tiles right above this, so the combo would only repeat
    // them there.
    property bool showShapeCombo: true
    function setMask(patch) {
        const mask = Object.assign({}, root.clipData.mask || {}, patch)
        EditorState.setClipMask(EditorState.selectedTrack, EditorState.selectedClip, mask)
    }

    // The preview shows the focused mask's handles while this tab is open on a layer.
    Binding {
        target: EditorState.preview
        property: "maskEditMode"
        value: true
        when: root.visible && root.isLayer && root.maskShape !== "none"
        restoreMode: Binding.RestoreBindingOrValue
    }

    // A media clip carries no mask of its own: its masks are mask adjustments pinned to it in one
    // of its track's lanes. Listing them here is the whole point — otherwise the only way to reach
    // a mask you just applied is to know to click its card on the timeline.
    readonly property bool isMediaClip: clipKind === "video" || clipKind === "image"
    readonly property var linkedMasks: {
        void clipDataRevision
        if (!isMediaClip || !hasSelection)
            return []
        return EditorState.linkedMaskClips(EditorState.selectedTrack, EditorState.selectedClip) || []
    }
    // "media" is not a shape the combo below lists, so an applied cutout would read as "None".
    readonly property bool showsCutout: {
        if (!isMediaClip)
            return false
        const list = linkedMasks
        for (let i = 0; i < list.length; ++i) {
            if (list[i].media === true)
                return true
        }
        return false
    }

    height: contentCol.height
    implicitHeight: contentCol.height

    function refreshFields() {}

    Connections {
        target: EditorState
        function onSelectionChanged() { root.clipDataRevision++ }
        function onSelectedClipDataChanged() { root.clipDataRevision++ }
        function onTracksChanged() { root.clipDataRevision++ }
    }

    Column {
        id: contentCol
        width: root.width
        spacing: Theme.spacingXl

        // A mask layer, like an adjustment layer: over everything under it, or clipped to one clip.
        // An effects layer has this in its own tab.
        AdjustmentTargetSection {
            width: parent.width
            visible: available && root.clipKind === "adjustment" && root.clipData.adjustmentKind === "mask"
        }

        // Which masks this clip carries. A media clip's masks are adjustments pinned to it, so
        // this row is the way in: pick one and it becomes the selection the fields below edit.
        Column {
            visible: root.isMediaClip && root.linkedMasks.length > 0
            width: parent.width
            spacing: Theme.spacingSm

            Text {
                width: parent.width
                text: root.linkedMasks.length === 1
                      ? qsTr("1 mask on this clip")
                      : qsTr("%1 masks on this clip").arg(root.linkedMasks.length)
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            Repeater {
                model: root.linkedMasks
                delegate: ThemedButton {
                    required property var modelData
                    width: contentCol.width
                    // The cutout's own name is the clearest label; a shape falls back to its
                    // translated name so it never shows a raw id like "freeform".
                    text: modelData.name && modelData.name.length > 0
                          ? modelData.name
                          : (modelData.shape === "media" ? qsTr("Cutout")
                                                         : (maskShapeBox.labels[modelData.shape]
                                                            || modelData.shape))
                    tooltip: qsTr("Edit this mask")
                    onClicked: EditorState.selectClip(modelData.track, modelData.index)
                }
            }
        }

        // An adjustment layer's masks: one chip each, the focused one lit, and + for another.
        // Inside the masks the layer's effects and colour show; outside, what is under it.
        Column {
            visible: root.isLayer
            width: parent.width
            spacing: Theme.spacingSm

            Text {
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("Masks choose where this layer's effects, colour and LUT show: inside, the layer; outside, what is under it, untouched.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            Flow {
                width: parent.width
                spacing: Theme.spacingSm
                Repeater {
                    model: root.layerMasks
                    delegate: ThemedToggleButton {
                        required property var modelData
                        text: modelData.name && modelData.name.length > 0
                              ? modelData.name : qsTr("Mask %1").arg(modelData.index + 1)
                        checked: modelData.index === root.layerFocus
                        opacity: modelData.enabled ? 1 : 0.5
                        onClicked: EditorState.setLayerMaskFocus(EditorState.selectedTrack,
                                                                 EditorState.selectedClip, modelData.index)
                    }
                }
                ThemedButton {
                    text: root.layerMasks.length === 0 ? qsTr("Add mask") : "+"
                    glyph: root.layerMasks.length === 0 ? "circle-plus" : ""
                    variant: "ghost"
                    tooltip: qsTr("Add a mask to this layer")
                    onClicked: EditorState.addLayerMask(EditorState.selectedTrack, EditorState.selectedClip, "ellipse")
                }
            }
        }

        // The focused mask's name and switch.
        Row {
            visible: root.isLayer && root.maskShape !== "none"
            width: parent.width
            spacing: Theme.spacingSm
            ThemedTextField {
                width: parent.width - maskOnSwitch.width - Theme.spacingSm
                placeholderText: qsTr("Mask %1").arg(root.layerFocus + 1)
                text: (root.clipData.mask && root.clipData.mask.name) || ""
                onEditingFinished: {
                    if (((root.clipData.mask && root.clipData.mask.name) || "") !== text)
                        root.setMask({ name: text })
                }
            }
            ThemedSwitch {
                id: maskOnSwitch
                checked: !root.clipData.mask || root.clipData.mask.enabled !== false
                tooltip: qsTr("Turn this mask off without removing it")
                onToggled: root.setMask({ enabled: checked })
            }
        }

        // A media clip with no mask yet: say what the panel is for instead of showing inert
        // shape controls that would create a second mask without saying so.
        Text {
            visible: root.isMediaClip && root.linkedMasks.length === 0
            width: parent.width
            wrapMode: Text.WordWrap
            text: qsTr("This clip has no mask yet. Add one from the Masks tab in the assets panel, or drop a mask onto the clip on the timeline.")
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }

        // The tab used to open with a lone unlabelled combo box
        // and no explanation of what a mask does.
        Text {
            visible: maskShapeBox.visible
            width: parent.width
            text: qsTr("Shape")
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }

        ThemedComboBox {
            id: maskShapeBox
            // Hidden for a media mask: "media" is not one of the shapes below, so currentIndex
            // would clamp to 0 and the control would read "None" next to an applied cutout.
            // Also hidden while a media clip is selected: the mask being edited is one of the
            // adjustments listed above, not a shape on the clip, so a shape combo here would be
            // writing to the wrong object.
            visible: root.showShapeCombo && !root.isMedia && !root.isMediaClip
            width: parent.width
            // A library shape (Stock › Shapes) is listed only while it is the one applied: it is
            // picked from the Masks tab, which knows which outline it means.
            model: ["none", "rectangle", "ellipse", "star", "heart", "bars", "freeform", "text", "gradient"]
                   .concat(root.maskShape === "path" ? ["path"] : [])
            // Human labels — the raw ids were shown to the user.
            readonly property var labels: ({
                "none": qsTr("None"),
                "rectangle": qsTr("Rectangle"),
                "ellipse": qsTr("Ellipse"),
                "star": qsTr("Star"),
                "heart": qsTr("Heart"),
                "bars": qsTr("Bars"),
                "freeform": qsTr("Freeform"),
                "text": qsTr("Text"),
                "gradient": qsTr("Linear gradient"),
                "path": (root.clipData.mask && root.clipData.mask.name) || qsTr("Library shape")
            })
            displayText: labels[model[currentIndex]] || model[currentIndex]
            currentIndex: Math.max(0, model.indexOf((root.clipData.mask && root.clipData.mask.shape) || "none"))
            onActivated: {
                const mask = Object.assign({}, root.clipData.mask || {})
                mask.shape = model[currentIndex]
                if (mask.shape === "text" && !mask.text)
                    mask.text = qsTr("TEXT")
                if (mask.shape === "gradient" && root.maskShape !== "gradient") {
                    mask.y = 0.5
                    mask.h = 0.4
                }
                EditorState.setClipMask(EditorState.selectedTrack, EditorState.selectedClip, mask)
            }
        }

        // Text mask: the words whose outline shows the clip.
        Column {
            visible: root.maskShape === "text" && !root.isMediaClip
            width: parent.width
            spacing: Theme.spacingSm

            Text {
                width: parent.width
                text: qsTr("Mask text")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            ThemedTextField {
                id: maskTextField
                width: parent.width
                placeholderText: qsTr("Write the text")
                text: (root.clipData.mask && root.clipData.mask.text) || ""
                onEditingFinished: {
                    const mask = Object.assign({}, root.clipData.mask || {})
                    if (mask.text === text)
                        return
                    mask.text = text
                    EditorState.setClipMask(EditorState.selectedTrack, EditorState.selectedClip, mask)
                }
            }
        }

        // Pen: a freeform drawn as a smooth curve through its points.
        Row {
            width: parent.width
            spacing: 8
            visible: root.maskShape === "freeform" && !root.isMediaClip
            Text {
                text: qsTr("Smooth curves (pen)")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
                anchors.verticalCenter: parent.verticalCenter
            }
            ThemedSwitch {
                checked: !!(root.clipData.mask && root.clipData.mask.smooth)
                onToggled: {
                    const mask = Object.assign({}, root.clipData.mask || {})
                    mask.smooth = checked
                    EditorState.setClipMask(EditorState.selectedTrack, EditorState.selectedClip, mask)
                }
            }
        }

        // How this mask folds into the ones stacked before it on the same track. Only meaningful
        // once there is more than one: the compositor ignores the first enabled entry's op and
        // lets it seed the coverage, because a lone Subtract or Intersect would blank the layer.
        Column {
            visible: root.maskShape !== "none" && !root.isMediaClip
                     && (!root.isLayer || root.layerFocus > 0)
            width: parent.width
            spacing: Theme.spacingSm

            Text {
                width: parent.width
                text: qsTr("Combine")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            ThemedComboBox {
                id: maskOpBox
                width: parent.width
                model: ["add", "subtract", "intersect"]
                readonly property var labels: ({
                    "add": qsTr("Add"),
                    "subtract": qsTr("Subtract"),
                    "intersect": qsTr("Intersect")
                })
                displayText: labels[model[currentIndex]] || model[currentIndex]
                currentIndex: Math.max(0, model.indexOf((root.clipData.mask && root.clipData.mask.op) || "add"))
                onActivated: {
                    const mask = Object.assign({}, root.clipData.mask || {})
                    mask.op = model[currentIndex]
                    EditorState.setClipMask(EditorState.selectedTrack, EditorState.selectedClip, mask)
                }
            }
        }

        // Clearing a mask previously required knowing to reselect
        // "none" in the combo above.
        ThemedButton {
            visible: root.maskShape !== "none" && !root.isMediaClip
            text: root.isMedia ? qsTr("Remove cutout layer") : qsTr("Remove mask")
            variant: "destructive"
            glyph: Theme.icons.trash
            onClicked: {
                if (root.isLayer) {
                    EditorState.removeLayerMask(EditorState.selectedTrack, EditorState.selectedClip, root.layerFocus)
                    return
                }
                const mask = Object.assign({}, root.clipData.mask || {})
                mask.shape = "none"
                EditorState.setClipMask(EditorState.selectedTrack, EditorState.selectedClip, mask)
            }
        }

        // Back to the shape's starting place and size, keeping the shape, name and how it combines.
        ThemedButton {
            visible: root.maskShape !== "none" && !root.isMediaClip && !root.isMedia
            text: qsTr("Reset mask")
            variant: "ghost"
            glyph: Theme.icons.reset
            onClicked: root.setMask({ x: 0.5, y: 0.5, w: root.maskShape === "gradient" ? 0.6 : 0.6,
                                      h: root.maskShape === "gradient" ? 0.4 : 0.6, rotation: 0,
                                      feather: 0, expand: 0, opacity: 1, invert: false })
        }

        // Mask scalars animate through the same generic keyframe API as a clip's transform, so
        // they get the same row: diamond, prev/next key navigation, easing chips. The prop ids are
        // "mask.<key>"; redirectToKeyframeHost is what walks from the selected media clip to the
        // adjustment actually carrying the mask.
        Repeater {
            // `shapes` is what the rasterizer actually reads for each shape (see
            // MaskApplier::maskPath): Bars derives both bands from `h` alone and ignores the
            // rest, and a Freeform's vertices *are* the shape, so its rect and rotation do
            // nothing. Offering those sliders anyway just invites dragging something inert.
            model: [
                { key: "mask.x", label: qsTr("Center X"), def: 0.5, decimals: 3, min: 0, max: 1,
                  shapes: ["rectangle", "ellipse", "star", "heart", "text", "gradient"] },
                { key: "mask.y", label: qsTr("Center Y"), def: 0.5, decimals: 3, min: 0, max: 1,
                  shapes: ["rectangle", "ellipse", "star", "heart", "text", "gradient"] },
                { key: "mask.w", label: qsTr("Width"), def: 0.6, decimals: 3, min: 0.05, max: 1,
                  shapes: ["rectangle", "ellipse", "star", "heart", "text"] },
                { key: "mask.h", label: qsTr("Height"), def: 0.6, decimals: 3, min: 0.05, max: 1,
                  shapes: ["rectangle", "ellipse", "star", "heart", "bars", "text"] },
                // A gradient's height is the depth of its fade.
                { key: "mask.h", label: qsTr("Fade length"), def: 0.4, decimals: 3, min: 0.01, max: 1,
                  shapes: ["gradient"] },
                { key: "mask.rotation", label: qsTr("Rotation"), def: 0, decimals: 1,
                  min: -180, max: 180, unit: "°",
                  shapes: ["rectangle", "ellipse", "star", "heart", "text", "gradient"] },
                // Feather blurs the finished coverage map, so it applies to every shape.
                { key: "mask.feather", label: qsTr("Feather"), def: 0, decimals: 0,
                  min: 0, max: 64, unit: "px",
                  shapes: ["rectangle", "ellipse", "star", "heart", "bars", "freeform", "text"] },
                // Grows or shrinks the outline (a share of the frame's shorter side).
                { key: "mask.expand", label: qsTr("Expand"), def: 0, decimals: 3,
                  min: -0.3, max: 0.3,
                  shapes: ["rectangle", "ellipse", "star", "heart", "bars", "freeform", "text", "gradient"] },
                { key: "mask.opacity", label: qsTr("Mask opacity"), def: 1, decimals: 2,
                  min: 0, max: 1, percent: true,
                  shapes: ["rectangle", "ellipse", "star", "heart", "bars", "freeform", "text", "gradient"] }
            ]
            delegate: PropertyKeyframeRow {
                required property var modelData
                width: parent.width
                visible: !root.isMedia
                         && !root.isMediaClip
                         // A library shape fills its rect like the heart does.
                         && modelData.shapes.indexOf(root.maskShape === "path" ? "heart" : root.maskShape) >= 0
                // `def` is what an unkeyed row shows, so it carries the mask's own value (as the
                // effect rows do); the fixed default made a resized mask read 0.600.
                propDef: {
                    const mask = root.clipData.mask || {}
                    const own = mask[modelData.key.substring(5)]
                    return Object.assign({}, modelData, { def: own !== undefined ? own : modelData.def })
                }
                // Key times come back on the timeline already, keyed by the bare scalar name.
                keyframeList: {
                    const keys = root.clipData.mask && root.clipData.mask.keyframes
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

        Row {
            width: parent.width
            spacing: 8
            visible: root.maskShape !== "none" && !root.isMediaClip
            Text {
                text: qsTr("Invert")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
                anchors.verticalCenter: parent.verticalCenter
            }
            ThemedSwitch {
                checked: !!(root.clipData.mask && root.clipData.mask.invert)
                onToggled: {
                    const mask = Object.assign({}, root.clipData.mask || {})
                    mask.invert = checked
                    EditorState.setClipMask(EditorState.selectedTrack, EditorState.selectedClip, mask)
                }
            }
        }

        // CapCut's mask tracking: the mask follows what it covers in the video it cuts, keyed from
        // the playhead to both ends of its clip.
        Column {
            id: followColumn
            readonly property var tracking: EditorState.motionTrack
            readonly property var source: {
                void root.clipDataRevision
                void EditorState.playheadSeconds
                return followColumn.tracking.maskFollowSource(EditorState.selectedTrack, EditorState.selectedClip)
            }
            property bool followScale: false
            width: parent.width
            spacing: Theme.spacingSm
            visible: root.hasSelection && root.clipKind === "adjustment" && root.maskShape !== "none" && !root.isMedia

            Text {
                text: qsTr("Follow")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
                font.weight: Font.Medium
            }
            Text {
                width: parent.width
                visible: !followColumn.source.ok
                wrapMode: Text.WordWrap
                text: followColumn.source.reason || ""
                color: Theme.warning
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
            ThemedSwitch {
                width: parent.width
                visible: followColumn.source.ok && !followColumn.tracking.busy
                text: qsTr("Scale too — grow and shrink with what it covers")
                checked: followColumn.followScale
                onToggled: followColumn.followScale = checked
            }
            ThemedButton {
                visible: followColumn.source.ok && !followColumn.tracking.busy
                text: qsTr("Mask follows what it covers")
                glyph: Theme.icons.locateFixed
                tooltip: qsTr("Place the mask over what it should follow, then start: it is keyed from the playhead to both ends of the mask")
                onClicked: followColumn.tracking.maskFollow(EditorState.selectedTrack, EditorState.selectedClip,
                                                            followColumn.followScale)
            }
            Row {
                width: parent.width
                spacing: Theme.spacingSm
                visible: followColumn.tracking.busy
                ThemedProgressBar {
                    width: parent.width - maskFollowCancel.width - parent.spacing
                    anchors.verticalCenter: parent.verticalCenter
                    value: followColumn.tracking.progress
                }
                ThemedButton {
                    id: maskFollowCancel
                    variant: "ghost"
                    text: qsTr("Cancel")
                    onClicked: followColumn.tracking.cancel()
                }
            }
        }
    }
}
