import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import Drift
import ".."

// Motion Tools (0.26, Jorge): the panel motion designers keep docked next to After Effects, in the
// inspector's rail. Eases for the keys picked on the timeline, the anchor grid, Elastic / Bounce /
// Clone, Sequence with offset and step, Extract / Merge / Add null, Convert to shape and Centre.
Item {
    id: root

    readonly property var picked: EditorState.pickedKeyframes || ({})
    readonly property int pickedCount: (picked.keys || []).length
    readonly property var selection: EditorState.selection || []
    readonly property bool hasClip: EditorState.selectedTrack >= 0 && EditorState.selectedClip >= 0
    property real easeIn: 33
    property real easeOut: 33
    property real easeIn: 33
    property real easeOut: 33
    // Motion Tools' third row: the speed the picked keys pass through (0 = they rest there).
    property real easeVelocity: 0
    // As Motion Tools: the picked keys take the handles as they move, one undo step per drag.
    function applyEaseLive() {
        if (root.pickedCount > 0)
            EditorState.easePickedKeyframes("ease", root.easeIn, root.easeOut, root.easeVelocity)
    }

    height: col.height
    implicitHeight: col.height

    component ToolButton: Rectangle {
        id: tb
        property string label: ""
        property string glyph: ""
        property string tip: ""
        property bool enabledTool: true
        signal activated()
        implicitHeight: 36
        radius: Theme.radiusSm
        color: area.pressed ? Theme.panelMuted : (area.containsMouse ? Theme.panelAccent : Theme.panelBackground)
        border.width: Theme.borderWidth
        border.color: Theme.panelBorder
        opacity: enabledTool ? 1 : 0.45
        Row {
            anchors.centerIn: parent
            spacing: 6
            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: tb.label
                color: Theme.panelForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
                font.weight: Font.DemiBold
                font.capitalization: Font.AllUppercase
            }
            IconGlyph {
                visible: tb.glyph.length > 0
                anchors.verticalCenter: parent.verticalCenter
                glyph: tb.glyph
                iconSize: 14
                iconColor: Theme.primary
            }
        }
        MouseArea {
            id: area
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            enabled: tb.enabledTool
            onClicked: tb.activated()
        }
        ThemedToolTip { visible: area.containsMouse && tb.tip.length > 0; text: tb.tip }
    }

    component Card: Rectangle {
        default property alias content: inner.data
        width: parent ? parent.width : 0
        implicitHeight: inner.implicitHeight + 2 * Theme.spacingMd
        height: implicitHeight
        radius: Theme.radiusMd
        color: Theme.darkMode ? Theme.panelAccent : Theme.appBackground
        border.width: Theme.borderWidth
        border.color: Theme.panelBorder
        Column {
            id: inner
            x: Theme.spacingMd
            y: Theme.spacingMd
            width: parent.width - 2 * Theme.spacingMd
            spacing: Theme.spacingSm
        }
    }

    Column {
        id: col
        width: root.width
        spacing: Theme.spacingMd

        Text {
            text: "MOTION TOOLS"
            color: Theme.primary
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeLg
            font.weight: Font.Bold
        }
        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            opacity: 0.8
            size: "sm"
            text: root.pickedCount > 0 ? qsTr("%n keyframe(s) picked on the timeline.", "", root.pickedCount)
                                       : qsTr("Pick keyframes on the timeline (drag a box over them) to ease, clone or settle them.")
        }

        // ----- Eases: in, out, and the three ways to apply them ---------------------------------
        Card {
            Repeater {
                model: [
                    { id: "in", glyph: Theme.icons.chevronLeft, from: 0.1, to: 100,
                      tip: qsTr("Ease in: how far the curve slows down arriving at the key") },
                    { id: "out", glyph: Theme.icons.chevronRight, from: 0.1, to: 100,
                      tip: qsTr("Ease out: how far it starts slowly leaving the key") },
                    { id: "velocity", glyph: "x", from: -2000, to: 2000,
                      tip: qsTr("Speed at the keys, in units a second: 0 stops there, more keeps it moving through") }
                ]
                RowLayout {
                    id: easeRow
                    required property var modelData
                    width: parent.width
                    spacing: Theme.spacingSm
                    readonly property real current: modelData.id === "in" ? root.easeIn
                                                    : modelData.id === "out" ? root.easeOut : root.easeVelocity
                    function setValue(v) {
                        if (modelData.id === "in")
                            root.easeIn = v
                        else if (modelData.id === "out")
                            root.easeOut = v
                        else
                            root.easeVelocity = v
                        root.applyEaseLive()
                    }
                    IconGlyph { glyph: modelData.glyph; iconSize: 16 }
                    ThemedSlider {
                        Layout.fillWidth: true
                        label: easeRow.modelData.tip
                        from: easeRow.modelData.from
                        to: easeRow.modelData.to
                        value: easeRow.current
                        onPressedChanged: {
                            if (pressed && root.pickedCount > 0)
                                EditorState.beginEditSession(qsTr("Easy ease"))
                            else if (!pressed)
                                EditorState.endEditSession(true)
                        }
                        onMoved: easeRow.setValue(value)
                    }
                    ThemedNumberField {
                        Layout.preferredWidth: 58
                        from: easeRow.modelData.from
                        to: easeRow.modelData.to
                        decimals: 0
                        value: easeRow.current
                        onEdited: v => easeRow.setValue(v)
                    }
                }
            }
            Row {
                width: parent.width
                spacing: Theme.spacingSm
                ToolButton {
                    width: (parent.width - 2 * parent.spacing) / 3
                    label: qsTr("Ease")
                    glyph: "circle"
                    tip: qsTr("Easy ease with these influences on the picked keys")
                    enabledTool: root.pickedCount > 0
                    onActivated: EditorState.easePickedKeyframes("ease", root.easeIn, root.easeOut, root.easeVelocity)
                }
                ToolButton {
                    width: (parent.width - 2 * parent.spacing) / 3
                    label: qsTr("Linear")
                    tip: qsTr("Straight, constant speed")
                    enabledTool: root.pickedCount > 0
                    onActivated: EditorState.easePickedKeyframes("linear", 0, 0)
                }
                ToolButton {
                    width: (parent.width - 2 * parent.spacing) / 3
                    label: qsTr("Hold")
                    glyph: Theme.icons.square
                    tip: qsTr("Jump to the next key instead of moving")
                    enabledTool: root.pickedCount > 0
                    onActivated: EditorState.easePickedKeyframes("hold", 0, 0)
                }
            }
        }

        // ----- Anchor grid and Elastic / Bounce / Clone -------------------------------------------
        Row {
            width: parent.width
            spacing: Theme.spacingMd

            Card {
                width: (parent.width - parent.spacing) / 2
                Grid {
                    id: grid
                    columns: 3
                    spacing: 4
                    readonly property real cell: (parent.width - 2 * spacing) / 3
                    Repeater {
                        model: 9
                        Rectangle {
                            required property int index
                            readonly property real fx: (index % 3) / 2
                            readonly property real fy: Math.floor(index / 3) / 2
                            width: grid.cell
                            height: grid.cell * 0.8
                            radius: 3
                            color: cellArea.containsMouse ? Theme.primary : Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.55)
                            opacity: root.hasClip ? 1 : 0.4
                            Rectangle {
                                anchors.centerIn: parent
                                visible: index === 4
                                width: parent.height * 0.45
                                height: width
                                color: "transparent"
                                border.width: 2
                                border.color: Theme.panelBackground
                            }
                            MouseArea {
                                id: cellArea
                                anchors.fill: parent
                                hoverEnabled: true
                                enabled: root.hasClip
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    // Every selected layer; the anchor moves, the layer stays put.
                                    const list = root.selection.length > 0 ? root.selection
                                                                           : [{ track: EditorState.selectedTrack, clip: EditorState.selectedClip }]
                                    for (const s of list)
                                        EditorState.setAnchorKeepingPlace(s.track, s.clip, parent.fx, parent.fy)
                                }
                            }
                            ThemedToolTip { visible: cellArea.containsMouse; text: qsTr("Anchor point here (the layer stays where it is)") }
                        }
                    }
                }
            }

            Column {
                width: (parent.width - parent.spacing) / 2
                spacing: Theme.spacingSm
                ToolButton {
                    width: parent.width
                    label: qsTr("Elastic")
                    glyph: "activity"
                    tip: qsTr("Overshoots and settles where the movement stops")
                    onActivated: EditorState.applySettleToPicked("elastic")
                }
                ToolButton {
                    width: parent.width
                    label: qsTr("Bounce")
                    glyph: Theme.icons.chevronDown
                    tip: qsTr("Bounces back off the last position, like a ball")
                    onActivated: EditorState.applySettleToPicked("bounce")
                }
                ToolButton {
                    width: parent.width
                    label: qsTr("Clone")
                    glyph: Theme.icons.copy
                    tip: qsTr("Copies the picked keys to the playhead")
                    enabledTool: root.pickedCount > 0
                    onActivated: EditorState.clonePickedKeyframes()
                }
            }
        }

        // ----- Bounce / Elastic controls (0.26), as After Effects lists them under the layer -------
        Repeater {
            model: {
                void EditorState.tracksRevision
                return root.hasClip ? EditorState.settleBehaviors(EditorState.selectedTrack, EditorState.selectedClip) : []
            }
            Card {
                id: settleCard
                required property var modelData
                readonly property bool bounce: modelData.kind === "bounce"
                function set(key, value) {
                    const p = {}
                    p[key] = value
                    EditorState.setSettleParams(EditorState.selectedTrack, EditorState.selectedClip, modelData.props, p)
                }
                RowLayout {
                    width: parent.width
                    Text {
                        Layout.fillWidth: true
                        text: (settleCard.bounce ? qsTr("Bounce: %1") : qsTr("Elastic: %1")).arg(settleCard.modelData.label)
                        color: Theme.panelForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSm
                        font.weight: Font.DemiBold
                        elide: Text.ElideRight
                    }
                    ThemedButton {
                        text: qsTr("Reset")
                        variant: "ghost"
                        tooltip: qsTr("Take the behaviour off this property")
                        onClicked: EditorState.setSettleParams(EditorState.selectedTrack, EditorState.selectedClip,
                                                               settleCard.modelData.props, ({}))
                    }
                }
                Repeater {
                    model: settleCard.bounce
                           ? [ { key: "amplitude", label: qsTr("Amplitude"), from: 0, to: 80, decimals: 1 },
                               { key: "gravity", label: qsTr("Gravity"), from: 1, to: 100, decimals: 1 },
                               { key: "maxJumps", label: qsTr("Max jumps"), from: 0, to: 20, decimals: 0 } ]
                           : [ { key: "amplitude", label: qsTr("Amplitude"), from: 0, to: 100, decimals: 1 },
                               { key: "frequency", label: qsTr("Frequency"), from: 1, to: 120, decimals: 1 },
                               { key: "decay", label: qsTr("Decay"), from: 1, to: 200, decimals: 1 } ]
                    RowLayout {
                        required property var modelData
                        width: parent.width
                        spacing: Theme.spacingSm
                        Text {
                            Layout.preferredWidth: 92
                            text: modelData.label
                            color: Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                            elide: Text.ElideRight
                        }
                        ThemedSlider {
                            id: settleSlider
                            Layout.fillWidth: true
                            label: modelData.label
                            from: modelData.from
                            to: modelData.to
                            stepSize: modelData.decimals === 0 ? 1 : 0
                            value: settleCard.modelData[modelData.key]
                            onMoved: settleCard.set(modelData.key, modelData.decimals === 0 ? Math.round(value) : value)
                        }
                        Text {
                            Layout.preferredWidth: 38
                            horizontalAlignment: Text.AlignRight
                            text: Number(settleSlider.value).toFixed(modelData.decimals)
                            color: Theme.primary
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeSm
                        }
                    }
                }
                ThemedSwitch {
                    visible: settleCard.bounce
                    width: parent.width
                    text: qsTr("Jump In/Out")
                    tooltip: qsTr("Hops on the far side of the key, as if it went through, instead of back off it")
                    checked: settleCard.modelData.jumpOut === true
                    onToggled: settleCard.set("jumpOut", checked)
                }
            }
        }

        // ----- Sequence -------------------------------------------------------------------------        // ----- Sequence -------------------------------------------------------------------------
        Card {
            RowLayout {
                width: parent.width
                spacing: Theme.spacingSm
                ToolButton {
                    Layout.fillWidth: true
                    label: qsTr("Sequence")
                    tip: qsTr("Staggers the selected layers in time, top to bottom")
                    enabledTool: root.selection.length > 1
                    onActivated: EditorState.sequenceSelectedClips(Math.round(offsetField.value), Math.round(stepField.value), false)
                }
                ToolButton {
                    Layout.preferredWidth: 40
                    glyph: "arrow-down-wide-narrow"
                    tip: qsTr("Sequence from the bottom up")
                    enabledTool: root.selection.length > 1
                    onActivated: EditorState.sequenceSelectedClips(Math.round(offsetField.value), Math.round(stepField.value), true)
                }
                Column {
                    spacing: 2
                    ThemedLabel { text: qsTr("Offset"); size: "sm" }
                    ThemedNumberField { id: offsetField; width: 54; from: -999; to: 999; value: 5 }
                }
                Column {
                    spacing: 2
                    ThemedLabel { text: qsTr("Step"); size: "sm" }
                    ThemedNumberField { id: stepField; width: 54; from: 1; to: 99; value: 1 }
                }
            }
            ThemedLabel {
                width: parent.width
                wrapMode: Text.WordWrap
                size: "sm"
                opacity: 0.7
                text: qsTr("Offset in frames between layers; Step = how many layers start together.")
            }
        }

        // ----- Layers -----------------------------------------------------------------------------
        Row {
            width: parent.width
            spacing: Theme.spacingSm
            ToolButton {
                width: (parent.width - 2 * parent.spacing) / 3
                label: qsTr("Extract")
                tip: qsTr("Takes the layers out of the selected composition")
                enabledTool: root.hasClip && EditorState.selectedClipData && EditorState.selectedClipData.kind === "composite"
                onActivated: EditorState.ungroupComposite(EditorState.selectedTrack, EditorState.selectedClip)
            }
            ToolButton {
                width: (parent.width - 2 * parent.spacing) / 3
                label: qsTr("Merge")
                tip: qsTr("Puts the selected layers in one composition")
                enabledTool: root.selection.length > 1
                onActivated: EditorState.makeCompositeFromSelection()
            }
            ToolButton {
                width: (parent.width - 2 * parent.spacing) / 3
                label: qsTr("Add null")
                tip: qsTr("A null in the middle of the selected layers, which follow it")
                onActivated: EditorState.addNullForSelection()
            }
        }
        Row {
            width: parent.width
            spacing: Theme.spacingSm
            ToolButton {
                width: (parent.width - parent.spacing) / 2
                label: qsTr("Convert to shape")
                tip: qsTr("A text's letters or a shape become an editable path")
                enabledTool: root.hasClip && EditorState.selectedClipData
                             && (EditorState.selectedClipData.kind === "text" || EditorState.selectedClipData.kind === "shape")
                onActivated: EditorState.convertSelectionToShape()
            }
            ToolButton {
                width: (parent.width - parent.spacing) / 2
                label: qsTr("Centre")
                tip: qsTr("Puts the selected layers in the middle of the frame")
                enabledTool: root.hasClip
                onActivated: EditorState.centerSelectionInFrame()
            }
        }
        // After Effects' lights (0.26): they light the 3D layers that accept lights.
        Row {
            width: parent.width
            spacing: Theme.spacingSm
            Repeater {
                model: [
                    { kind: 1, label: qsTr("Point light"), tip: qsTr("Shines all round from one point, like a bulb") },
                    { kind: 2, label: qsTr("Spot light"), tip: qsTr("A cone of light, like a stage spot") },
                    { kind: 3, label: qsTr("Parallel light"), tip: qsTr("Even light from one direction, like the sun") },
                    { kind: 4, label: qsTr("Ambient light"), tip: qsTr("Lights every side evenly, without direction") }
                ]
                ToolButton {
                    required property var modelData
                    width: (parent.width - 3 * parent.spacing) / 4
                    label: modelData.label
                    tip: modelData.tip
                    onActivated: EditorState.addLight(modelData.kind)
                }
            }
        }
    }
}
