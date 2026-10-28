import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// After Effects' Parent column and Motion Blur switch (0.26), with the project's shutter. Sits under
// the blend mode wherever a drawn clip shows it.
Column {
    id: root

    property int revision: 0
    readonly property int trackIndex: EditorState.selectedTrack
    readonly property int clipIndex: EditorState.selectedClip
    readonly property var info: {
        void root.revision
        return EditorState.clipMotionInfo(root.trackIndex, root.clipIndex)
    }
    readonly property var options: {
        void root.revision
        return EditorState.clipParentOptions(root.trackIndex, root.clipIndex)
    }
    readonly property var blur: {
        void root.revision
        return EditorState.motionBlurSettings()
    }

    // Adjustments and sound have no picture of their own to move or blur.
    visible: {
        void root.revision
        const data = EditorState.selectedClipData
        return !!info && info.nullObject !== undefined && !!data && data.kind !== "adjustment"
               && data.kind !== "audio"
    }
    spacing: Theme.spacingMd

    Connections {
        target: EditorState
        function onSelectionChanged() { root.revision++ }
        function onTracksChanged() { root.revision++ }
    }

    // ----- After Effects' Layer Styles (0.26), on any layer ------------------------------------
    Text {
        text: qsTr("Layer styles")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }
    Text {
        width: parent.width
        wrapMode: Text.WordWrap
        text: qsTr("Added as effects, so each one is adjusted, animated or removed in the Effects tab.")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
        opacity: 0.8
    }
    Flow {
        width: parent.width
        spacing: Theme.spacingSm
        Repeater {
            model: [
                { id: "layer_drop_shadow", label: qsTr("Drop shadow") },
                { id: "layer_outer_glow", label: qsTr("Outer glow") },
                { id: "layer_stroke", label: qsTr("Stroke") },
                { id: "layer_bevel", label: qsTr("Bevel and emboss") },
                { id: "layer_color_overlay", label: qsTr("Color overlay") }
            ]
            ThemedButton {
                required property var modelData
                text: modelData.label
                variant: "secondary"
                onClicked: EditorState.addEffect(root.trackIndex, root.clipIndex, modelData.id)
            }
        }
    }

    Text {
        text: qsTr("Parent")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }

    Text {
        width: parent.width
        wrapMode: Text.WordWrap
        text: qsTr("The layer follows the parent's position, rotation and scale from the moment you link it, as in After Effects. A null object is a handle that is never drawn.")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
        opacity: 0.8
    }

    ThemedComboBox {
        id: parentBox
        width: parent.width
        // "None" first, then every clip this one can follow.
        readonly property var entries: [{ id: "", name: qsTr("None"), track: -1, clip: -1 }].concat(root.options || [])
        model: entries.map(e => e.name)
        currentIndex: {
            const want = root.info ? (root.info.parentId || "") : ""
            for (let i = 0; i < entries.length; ++i) {
                if (entries[i].id === want)
                    return i
            }
            return 0
        }
        tooltip: qsTr("The layer this one follows")
        onActivated: index => {
            const e = entries[index]
            EditorState.setClipParent(root.trackIndex, root.clipIndex, e.track, e.clip)
        }
    }

    // ----- Track matte -----------------------------------------------------------------------
    readonly property var matteOptions: {
        void root.revision
        return EditorState.clipMatteOptions(root.trackIndex, root.clipIndex)
    }
    readonly property var matteModes: [
        { id: "none", label: qsTr("No track matte") },
        { id: "alpha", label: qsTr("Alpha matte") },
        { id: "alphaInverted", label: qsTr("Alpha inverted matte") },
        { id: "luma", label: qsTr("Luma matte") },
        { id: "lumaInverted", label: qsTr("Luma inverted matte") }
    ]

    Text {
        text: qsTr("Track matte")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }
    Text {
        width: parent.width
        wrapMode: Text.WordWrap
        text: qsTr("Shows this layer only where another one covers it (alpha) or is bright (luma). The matte layer is hidden, as in After Effects.")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
        opacity: 0.8
    }
    ThemedComboBox {
        width: parent.width
        model: root.matteModes.map(m => m.label)
        currentIndex: {
            const want = root.info ? (root.info.matteMode || "none") : "none"
            for (let i = 0; i < root.matteModes.length; ++i) {
                if (root.matteModes[i].id === want)
                    return i
            }
            return 0
        }
        onActivated: index => EditorState.setClipTrackMatte(root.trackIndex, root.clipIndex,
                                                            root.matteModes[index].id, -1, -1)
    }
    ThemedComboBox {
        width: parent.width
        visible: !!root.info && (root.info.matteMode || "none") !== "none"
        model: (root.matteOptions || []).map(o => o.name)
        currentIndex: {
            const want = root.info ? (root.info.matteId || "") : ""
            const list = root.matteOptions || []
            for (let i = 0; i < list.length; ++i) {
                if (list[i].id === want)
                    return i
            }
            return -1
        }
        tooltip: qsTr("The layer used as the matte")
        onActivated: index => {
            const o = root.matteOptions[index]
            EditorState.setClipTrackMatte(root.trackIndex, root.clipIndex, root.info.matteMode, o.track, o.clip)
        }
    }

    ThemedSwitch {
        width: parent.width
        text: qsTr("Motion blur")
        tooltip: qsTr("Blurs the layer along its movement, as a camera shutter would")
        checked: !!root.info && !!root.info.motionBlur
        onToggled: EditorState.setClipMotionBlur(root.trackIndex, root.clipIndex, checked)
    }

    Text {
        width: parent.width
        wrapMode: Text.WordWrap
        visible: !!root.info && !!root.info.motionBlur
        text: qsTr("Shutter angle and samples, for the whole project: 180° blurs over half a frame; more samples are smoother and slower.")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
        opacity: 0.8
    }

    Row {
        width: parent.width
        spacing: Theme.spacingMd
        visible: !!root.info && !!root.info.motionBlur

        ThemedNumberField {
            width: (parent.width - parent.spacing) / 2
            from: 0
            to: 720
            step: 15
            unit: "°"
            value: root.blur.shutterDeg || 180
            placeholderText: qsTr("Shutter")
            onEdited: v => EditorState.setMotionBlurSettings(v, root.blur.samples || 16)
        }
        ThemedNumberField {
            width: (parent.width - parent.spacing) / 2
            from: 2
            to: 64
            step: 1
            value: root.blur.samples || 16
            placeholderText: qsTr("Samples")
            onEdited: v => EditorState.setMotionBlurSettings(root.blur.shutterDeg || 180, Math.round(v))
        }
    }
}
