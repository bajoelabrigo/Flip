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

    // ----- After Effects' lights (0.26) ----------------------------------------------------------
    readonly property var light: {
        void root.revision
        return EditorState.lightSettings(root.trackIndex, root.clipIndex)
    }
    readonly property bool isLight: !!light && light.kind !== undefined
    // Lights and null objects never paint, so layer styles would do nothing on them.
    readonly property bool paints: !isLight && !(!!info && info.nullObject === true)
    function setLight(key, value) {
        const m = {}
        m[key] = value
        EditorState.setLightSettings(root.trackIndex, root.clipIndex, m)
    }
    // Inline components do not see this file's ids: the settings come in, the change goes out.
    component LightSlider: Column {
        id: ls
        property string label: ""
        property string key: ""
        property real from: 0
        property real to: 100
        property string suffix: ""
        property var settings: ({})
        signal committed(string key, real value)
        width: parent ? parent.width : 0
        spacing: 2
        Text {
            text: ls.label + "  " + Math.round(Number(ls.settings[ls.key]) || 0) + ls.suffix
            color: Theme.panelForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSm
        }
        ThemedSlider {
            width: parent.width
            from: ls.from
            to: ls.to
            value: Number(ls.settings[ls.key]) || 0
            onPressedChanged: if (!pressed) ls.committed(ls.key, Math.round(value))
        }
    }
    Text {
        visible: root.isLight
        text: qsTr("Light")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }
    Text {
        visible: root.isLight
        width: parent.width
        wrapMode: Text.WordWrap
        text: qsTr("It lights the 3D layers that accept lights. Move it, take it nearer (depth) or tilt it like any layer; its opacity is its strength over time.")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
        opacity: 0.8
    }
    ThemedComboBox {
        visible: root.isLight
        width: parent.width
        model: [qsTr("Point"), qsTr("Spot"), qsTr("Parallel"), qsTr("Ambient")]
        currentIndex: root.isLight ? root.light.kind - 1 : 0
        onActivated: index => root.setLight("kind", index + 1)
    }
    Row {
        visible: root.isLight
        spacing: Theme.spacingSm
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: qsTr("Colour")
            color: Theme.panelForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSm
        }
        ColorSwatchField {
            hex: root.isLight ? root.light.color : "#ffffffff"
            onEdited: value => root.setLight("color", value)
        }
    }
    LightSlider {
        settings: root.light
        onCommitted: (key, value) => root.setLight(key, value)
        visible: root.isLight
        label: qsTr("Intensity")
        key: "intensity"
        to: 300
        suffix: " %"
    }
    LightSlider {
        settings: root.light
        onCommitted: (key, value) => root.setLight(key, value)
        visible: root.isLight && root.light.kind === 2
        label: qsTr("Cone angle")
        key: "coneAngle"
        from: 1
        to: 179
        suffix: "°"
    }
    LightSlider {
        settings: root.light
        onCommitted: (key, value) => root.setLight(key, value)
        visible: root.isLight && root.light.kind === 2
        label: qsTr("Cone feather")
        key: "coneFeather"
        suffix: " %"
    }
    LightSlider {
        settings: root.light
        onCommitted: (key, value) => root.setLight(key, value)
        visible: root.isLight && (root.light.kind === 1 || root.light.kind === 2)
        label: qsTr("Falloff radius")
        key: "falloffRadius"
        to: 3000
        suffix: " px"
    }
    LightSlider {
        settings: root.light
        onCommitted: (key, value) => root.setLight(key, value)
        visible: root.isLight && (root.light.kind === 1 || root.light.kind === 2)
        label: qsTr("Falloff distance (0 = none)")
        key: "falloffDistance"
        to: 3000
        suffix: " px"
    }
    // A 3D layer's material option.
    ThemedSwitch {
        visible: !root.isLight && !!root.info && root.info.layer3d === true
        width: parent.width
        text: qsTr("Accepts lights")
        tooltip: qsTr("Lights change this 3D layer (when there is at least one light)")
        checked: !!root.info && root.info.acceptsLights !== false
        onToggled: EditorState.setAcceptsLights(root.trackIndex, root.clipIndex, checked)
    }

    // ----- After Effects' Essential Graphics (0.26) --------------------------------------------
    // On a composition: the controls its clips offer, edited from outside.
    readonly property var essentials: {
        void root.revision
        return EditorState.essentialControls(root.trackIndex, root.clipIndex)
    }
    readonly property bool insideComposition: EditorState.activeSequenceId.length > 0
    readonly property bool textClip: {
        void root.revision
        const data = EditorState.selectedClipData
        return !!data && (data.kind === "text" || data.kind === "subtitle")
    }
    Text {
        visible: root.essentials.length > 0
        text: qsTr("Essential Graphics")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }
    Repeater {
        model: root.essentials
        Column {
            id: control
            required property var modelData
            width: root.width
            spacing: 2
            Text {
                text: control.modelData.label
                color: Theme.panelForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                elide: Text.ElideRight
                width: parent.width
            }
            ThemedTextField {
                visible: control.modelData.kind === "text"
                width: parent.width
                text: control.modelData.kind === "text" ? control.modelData.value : ""
                onEditingFinished: if (text !== control.modelData.value)
                    EditorState.setEssentialValue(control.modelData.clipId, control.modelData.prop, text)
            }
            ColorSwatchField {
                visible: control.modelData.kind === "color"
                hex: control.modelData.kind === "color" ? control.modelData.value : "#ffffffff"
                onEdited: value => EditorState.setEssentialValue(control.modelData.clipId, control.modelData.prop, value)
            }
            ThemedSlider {
                visible: control.modelData.kind === "number"
                width: parent.width
                from: control.modelData.min !== undefined ? control.modelData.min : 0
                to: control.modelData.max !== undefined ? control.modelData.max : 100
                value: control.modelData.kind === "number" ? control.modelData.value : 0
                onPressedChanged: if (!pressed)
                    EditorState.setEssentialValue(control.modelData.clipId, control.modelData.prop, Math.round(value * 10) / 10)
            }
        }
    }

    // Inside a composition: offer this clip's properties to the composition's controls.
    Text {
        visible: root.insideComposition
        text: qsTr("Add to Essential Graphics")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }
    Flow {
        visible: root.insideComposition
        width: parent.width
        spacing: Theme.spacingSm
        Repeater {
            model: (root.textClip ? [
                        { id: "content", label: qsTr("Text") },
                        { id: "textColor", label: qsTr("Text colour") },
                        { id: "text.pixelSize", label: qsTr("Text size") }
                    ] : []).concat([
                        { id: "x", label: qsTr("Position X") },
                        { id: "y", label: qsTr("Position Y") },
                        { id: "rotation", label: qsTr("Rotation") },
                        { id: "opacity", label: qsTr("Opacity") }
                    ])
            ThemedButton {
                required property var modelData
                readonly property bool on: {
                    void root.revision
                    return EditorState.isEssentialProperty(root.trackIndex, root.clipIndex, modelData.id)
                }
                text: modelData.label
                variant: on ? "primary" : "secondary"
                tooltip: on ? qsTr("Offered as a control of the composition: click to take it out")
                            : qsTr("Offer it as a control of the composition, editable from outside")
                onClicked: EditorState.toggleEssentialProperty(root.trackIndex, root.clipIndex, modelData.id)
            }
        }
    }

    // ----- After Effects' Layer Styles (0.26), on any layer ------------------------------------
    Text {
        visible: root.paints
        text: qsTr("Layer styles")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }
    Text {
        visible: root.paints
        width: parent.width
        wrapMode: Text.WordWrap
        text: qsTr("Added as effects, so each one is adjusted, animated or removed in the Effects tab.")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
        opacity: 0.8
    }
    Flow {
        visible: root.paints
        width: parent.width
        spacing: Theme.spacingSm
        Repeater {
            model: [
                { id: "layer.drop_shadow", label: qsTr("Drop shadow") },
                { id: "layer.outer_glow", label: qsTr("Outer glow") },
                { id: "layer.stroke", label: qsTr("Stroke") },
                { id: "layer.bevel", label: qsTr("Bevel and emboss") },
                { id: "layer.color_overlay", label: qsTr("Color overlay") }
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
