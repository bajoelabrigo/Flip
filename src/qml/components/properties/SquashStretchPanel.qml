import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// Animation › Squash & Stretch (0.26, Jorge): rubbery cartoon motions in the manner of After Effects'
// Squash & Stretch Pro, designed by us. A click writes the animation as keyframes on the selected
// clip — In at its start, Out at its end, the rest at the playhead — so it can be edited, moved or
// stacked with another one later on the same layer. Intensity bends it harder or softer, Scale makes
// the travel and the turns bigger or smaller, Speed shortens or lengthens it.
Column {
    id: root

    property string category: ""
    readonly property var animations: EditorState.squashAnimations()
    readonly property var categories: [
        { id: "in", label: qsTr("In") },
        { id: "out", label: qsTr("Out") },
        { id: "moves", label: qsTr("Moves") },
        { id: "jumps", label: qsTr("Jumps") },
        { id: "highlights", label: qsTr("Highlights") },
        { id: "rotations", label: qsTr("Rotations") },
        { id: "wiggles", label: qsTr("Wiggles") },
        { id: "glitch", label: qsTr("Glitch") }
    ]
    readonly property var shown: category.length === 0 ? animations
                                                       : animations.filter(a => a.category === category)

    spacing: Theme.spacingMd

    ThemedLabel {
        width: parent.width
        wrapMode: Text.WordWrap
        size: "sm"
        opacity: 0.8
        text: qsTr("Pick one to see it, then Apply: it is written as keyframes on every selected layer, starting (or ending) at the playhead. Put another one further on to keep animating the same layer.")
    }

    ChipScroller {
        width: parent.width

        ThemedChip {
            anchors.verticalCenter: parent.verticalCenter
            text: qsTr("All")
            variant: "secondary"
            selected: root.category.length === 0
            onClicked: root.category = ""
        }
        Repeater {
            model: root.categories
            delegate: ThemedChip {
                required property var modelData
                required property int index
                anchors.verticalCenter: parent.verticalCenter
                text: modelData.label
                variant: "secondary"
                accentColor: Theme.categoryColor(index)
                selected: root.category === modelData.id
                onClicked: root.category = modelData.id
            }
        }
    }

    // Intensity, Scale and Speed, as Squash & Stretch Pro offers them.
    Repeater {
        model: [
            { key: "intensity", label: qsTr("Squash & Stretch"), from: 0, to: 150, value: 100,
              tip: qsTr("How hard it squashes, stretches and bends") },
            { key: "scale", label: qsTr("Oomph"), from: 0, to: 200, value: 100,
              tip: qsTr("How far it travels, jumps and turns") },
            { key: "speed", label: qsTr("Speed"), from: 25, to: 300, value: 100,
              tip: qsTr("Faster makes it shorter, slower makes it longer") }
        ]
        delegate: Row {
            id: optionRow
            required property var modelData
            width: root.width
            spacing: Theme.spacingSm
            ThemedLabel {
                width: 96
                anchors.verticalCenter: parent.verticalCenter
                text: optionRow.modelData.label
            }
            ThemedSlider {
                id: optionSlider
                width: parent.width - 96 - valueText.width - 2 * parent.spacing
                anchors.verticalCenter: parent.verticalCenter
                from: optionRow.modelData.from
                to: optionRow.modelData.to
                stepSize: 1
                value: options[optionRow.modelData.key]
                valueFormatter: v => Math.round(v) + " %"
                ToolTip.text: optionRow.modelData.tip
                ToolTip.visible: hovered
                ToolTip.delay: 600
                onMoved: options[optionRow.modelData.key] = Math.round(value)
            }
            ThemedLabel {
                id: valueText
                width: 44
                anchors.verticalCenter: parent.verticalCenter
                horizontalAlignment: Text.AlignRight
                text: Math.round(optionSlider.value) + " %"
            }
        }
    }
    QtObject {
        id: options
        property real intensity: 100
        property real scale: 100
        property real speed: 100
    }

    // Timing, as Squash & Stretch Pro V2: the animation starts at the playhead, or ends there.
    Row {
        width: root.width
        spacing: Theme.spacingSm
        ThemedLabel { width: 96; anchors.verticalCenter: parent.verticalCenter; text: qsTr("Timing") }
        ThemedComboBox {
            id: timingBox
            width: parent.width - 96 - parent.spacing
            model: [qsTr("Start of behavior (at the playhead)"), qsTr("End of behavior (at the playhead)")]
        }
    }
    // Several layers picked: each one starts this many frames after the one before.
    Row {
        width: root.width
        spacing: Theme.spacingSm
        ThemedLabel { width: 96; anchors.verticalCenter: parent.verticalCenter; text: qsTr("Stagger") }
        ThemedNumberField {
            id: staggerField
            width: 72
            from: 0; to: 60; step: 1
            value: 3
            unit: qsTr(" fr")
        }
        ThemedLabel {
            anchors.verticalCenter: parent.verticalCenter
            opacity: 0.7
            size: "sm"
            text: qsTr("between layers")
        }
    }

    // The one picked, playing big, and Apply.
    property string picked: ""
    readonly property var pickedAnim: {
        for (const a of root.animations)
            if (a.id === root.picked)
                return a
        return null
    }
    Row {
        visible: root.pickedAnim !== null
        width: root.width
        spacing: Theme.spacingMd
        SquashAnimTile {
            animId: root.picked
            label: root.pickedAnim ? root.pickedAnim.label : ""
            seconds: root.pickedAnim ? root.pickedAnim.duration * 100 / Math.max(25, options.speed) : 1
            tileWidth: 120
            playing: root.visible && !EditorState.playing
        }
        Column {
            width: parent.width - 120 - parent.spacing
            spacing: Theme.spacingSm
            anchors.verticalCenter: parent.verticalCenter
            ThemedButton {
                width: parent.width
                variant: "primary"
                text: qsTr("Apply")
                onClicked: EditorState.applySquashToSelection(root.picked, options.intensity, options.scale,
                                                              options.speed,
                                                              timingBox.currentIndex === 1 ? "end" : "start",
                                                              Math.round(staggerField.value))
            }
            ThemedLabel {
                width: parent.width
                wrapMode: Text.WordWrap
                size: "sm"
                opacity: 0.7
                text: qsTr("Applies to every selected layer. The keys stay editable on the timeline.")
            }
        }
    }

    Grid {
        id: grid
        width: parent.width
        readonly property real gap: Theme.spacingMd
        columns: Math.max(3, Math.floor((width + gap) / (76 + gap)))
        columnSpacing: gap
        rowSpacing: gap
        readonly property real tileWidth: Math.floor((width - gap * (columns - 1)) / columns)

        Repeater {
            model: root.shown
            delegate: SquashAnimTile {
                required property var modelData
                animId: modelData.id
                label: modelData.label
                seconds: modelData.duration * 100 / Math.max(25, options.speed)
                tileWidth: grid.tileWidth
                playing: root.visible && !EditorState.playing && (Theme.touchUi ? false : hovered)
                onClicked: {
                    root.picked = modelData.id
                    // The animation's own timing: an Out ends at the playhead.
                    timingBox.currentIndex = modelData.place === "end" ? 1 : 0
                }
            }
        }
    }
}
