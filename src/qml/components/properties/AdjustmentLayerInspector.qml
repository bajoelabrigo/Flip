import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// An adjustment layer's own tab, as Premiere's and CapCut's: what it applies to (everything under
// it, or clipped to one clip as in Photoshop), its name, an on/off switch that keeps every setting,
// and for one over everything below how strongly it applies (its opacity, keyframeable: 0 % leaves
// what is under it untouched, 100 % applies the whole layer, in between mixes the two) and how it
// blends. Clipped to a clip it joins that clip's chain, where neither means anything.
// Its effects, colour and masks are edited in the Adjust, Effects and Masks tabs as on any clip.
Item {
    id: root

    property int clipDataRevision: 0
    readonly property var clipData: {
        void clipDataRevision
        return EditorState.selectedClipData
    }
    readonly property bool hasSelection: !!clipData && Object.keys(clipData).length > 0
    readonly property bool layerOn: hasSelection && !clipData.disabled
    readonly property bool inLane: hasSelection && clipData.inLane === true
    readonly property int effectCount: {
        void clipDataRevision
        const list = EditorState.selectedClipEffects
        return list ? list.length : 0
    }
    readonly property var propOpacity: { "key": "opacity", "label": qsTr("Strength"), "def": 1.0, "decimals": 2 }

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

        Text {
            width: parent.width
            wrapMode: Text.WordWrap
            text: qsTr("Everything you put on this layer (effects, colour, masks) applies while it lasts, without touching the clips themselves. Stretch or move it on the timeline to change when it acts.")
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }

        AdjustmentTargetSection {
            width: parent.width
        }

        // Without an effect the layer passes what is under it through unchanged, mask or not.
        Rectangle {
            visible: root.hasSelection && root.effectCount === 0
            width: parent.width
            height: emptyText.implicitHeight + Theme.spacingLg * 2
            radius: Theme.radiusSm
            color: "transparent"
            border.width: Theme.borderWidth
            border.color: Theme.panelBorder

            Text {
                id: emptyText
                anchors.fill: parent
                anchors.margins: Theme.spacingLg
                wrapMode: Text.WordWrap
                text: qsTr("It does not change anything yet: give it an effect (Effects tab) or a colour adjustment (Adjust tab). A mask only marks where they act.")
                color: Theme.foreground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
        }

        Column {
            width: parent.width
            spacing: Theme.spacingSm

            Text {
                text: qsTr("Name")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            ThemedTextField {
                id: nameField
                width: parent.width
                text: root.hasSelection ? (root.clipData.name || "") : ""
                placeholderText: qsTr("Adjustment layer")
                onEditingFinished: {
                    if (root.hasSelection && text.trim().length > 0 && text !== root.clipData.name)
                        EditorState.setClipName(EditorState.selectedTrack, EditorState.selectedClip, text)
                }
            }
        }

        ThemedSwitch {
            width: parent.width
            text: root.layerOn ? qsTr("On") : qsTr("Off: not applied, but keeps all its settings")
            checked: root.layerOn
            tooltip: qsTr("Turn the layer off to compare with and without it")
            onToggled: EditorState.setClipDisabled(EditorState.selectedTrack, EditorState.selectedClip, !checked)
        }

        PropertyKeyframeRow {
            visible: !root.inLane
            width: parent.width
            propDef: root.propOpacity
            keyframeList: (root.clipData.keyframes && root.clipData.keyframes.opacity
                           && root.clipData.keyframes.opacity.points) || []
            useSlider: true
            sliderFrom: 0
            sliderTo: 1
            percent: true
        }

        Text {
            visible: !root.inLane
            width: parent.width
            wrapMode: Text.WordWrap
            text: qsTr("0 %: what is under it, untouched. 100 %: the whole layer. In between, a mix of the two.")
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
            opacity: 0.8
        }

        BlendingInspector {
            visible: !root.inLane
            width: parent.width
        }
    }
}
