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
            visible: !root.isMedia && !root.isMediaClip
            width: parent.width
            model: ["none", "rectangle", "ellipse", "star", "heart", "bars", "freeform", "text"]
            // Human labels — the raw ids were shown to the user.
            readonly property var labels: ({
                "none": qsTr("None"),
                "rectangle": qsTr("Rectangle"),
                "ellipse": qsTr("Ellipse"),
                "star": qsTr("Star"),
                "heart": qsTr("Heart"),
                "bars": qsTr("Bars"),
                "freeform": qsTr("Freeform"),
                "text": qsTr("Text")
            })
            displayText: labels[model[currentIndex]] || model[currentIndex]
            currentIndex: Math.max(0, model.indexOf((root.clipData.mask && root.clipData.mask.shape) || "none"))
            onActivated: {
                const mask = Object.assign({}, root.clipData.mask || {})
                mask.shape = model[currentIndex]
                if (mask.shape === "text" && !mask.text)
                    mask.text = qsTr("TEXT")
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
                const mask = Object.assign({}, root.clipData.mask || {})
                mask.shape = "none"
                EditorState.setClipMask(EditorState.selectedTrack, EditorState.selectedClip, mask)
            }
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
                  shapes: ["rectangle", "ellipse", "star", "heart", "text"] },
                { key: "mask.y", label: qsTr("Center Y"), def: 0.5, decimals: 3, min: 0, max: 1,
                  shapes: ["rectangle", "ellipse", "star", "heart", "text"] },
                { key: "mask.w", label: qsTr("Width"), def: 0.6, decimals: 3, min: 0.05, max: 1,
                  shapes: ["rectangle", "ellipse", "star", "heart", "text"] },
                { key: "mask.h", label: qsTr("Height"), def: 0.6, decimals: 3, min: 0.05, max: 1,
                  shapes: ["rectangle", "ellipse", "star", "heart", "bars", "text"] },
                { key: "mask.rotation", label: qsTr("Rotation"), def: 0, decimals: 1,
                  min: -180, max: 180, unit: "°",
                  shapes: ["rectangle", "ellipse", "star", "heart", "text"] },
                // Feather blurs the finished coverage map, so it applies to every shape.
                { key: "mask.feather", label: qsTr("Feather"), def: 0, decimals: 0,
                  min: 0, max: 64, unit: "px",
                  shapes: ["rectangle", "ellipse", "star", "heart", "bars", "freeform", "text"] }
            ]
            delegate: PropertyKeyframeRow {
                required property var modelData
                width: parent.width
                visible: !root.isMedia
                         && !root.isMediaClip
                         && modelData.shapes.indexOf(root.maskShape) >= 0
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
    }
}
