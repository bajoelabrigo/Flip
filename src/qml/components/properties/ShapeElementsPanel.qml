import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// Motion Tools › Elements (0.26, Jorge: as Super Morphings, Super Liquids and Liquid Line, studied
// frame by frame in their demos). Three tools that work on the person's own layers:
//   Morph        — the selected layers fly on arcs into the last one picked and cut to it, which
//                  settles with a bounce; trails follow.
//   Liquid trail — a moving layer throws drops behind it, frame by frame, melted like liquid.
//   Liquid line  — a shape's outline becomes a stream of liquid running along it.
Column {
    id: root

    property string tool: "morph"
    property real morphSeconds: 0.5
    property int morphTrails: 0
    property real morphArc: 0.25
    property real morphSpin: 90
    property int liquidPerFrame: 4
    property int liquidSkip: 2
    property real liquidThreshold: 250
    property bool liquidHorizontal: false
    property real liquidInherit: 0.6
    property real liquidRandom: 0.5
    property real liquidSize: 18
    property real lineSeconds: 1.2
    property real lineWidth: 40
    property real lineLength: 0.35
    property real lineRough: 0.6
    property string liquidColor: ""
    readonly property var colors: ["", "#1f7bff", "#ff9a1f", "#ff3b6b", "#2ee6a8", "#9b5cff", "#ffffff", "#ffd23f"]

    spacing: Theme.spacingMd

    AnimSlotTabs {
        width: parent.width
        model: [
            { "id": "morph", "label": qsTr("Morph") },
            { "id": "trail", "label": qsTr("Liquid trail") },
            { "id": "line", "label": qsTr("Liquid line") }
        ]
        current: root.tool
        onActivated: id => root.tool = id
    }

    // One labelled slider with its value.
    component Knob: Row {
        id: knob
        property string label: ""
        property real from: 0
        property real to: 1
        property real step: 0.01
        property real value: 0
        property int decimals: 2
        property string unit: ""
        signal moved(real v)
        width: root.width
        spacing: Theme.spacingSm
        ThemedLabel { width: 96; anchors.verticalCenter: parent.verticalCenter; text: knob.label }
        ThemedSlider {
            width: parent.width - 96 - 52 - 2 * parent.spacing
            anchors.verticalCenter: parent.verticalCenter
            from: knob.from
            to: knob.to
            stepSize: knob.step
            value: knob.value
            valueFormatter: v => Number(v).toFixed(knob.decimals) + knob.unit
            onMoved: knob.moved(value)
        }
        ThemedLabel {
            width: 52
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: Text.AlignRight
            text: Number(knob.value).toFixed(knob.decimals) + knob.unit
        }
    }

    // ----- Morph ---------------------------------------------------------------------------
    Column {
        visible: root.tool === "morph"
        width: parent.width
        spacing: Theme.spacingSm
        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            size: "sm"
            opacity: 0.8
            text: qsTr("Select the layers with Ctrl+click in order: the last one is what they turn into. From the playhead, they fly into it and the picture cuts to it, as Super Morphings does.")
        }
        Knob { label: qsTr("Duration"); from: 0.2; to: 2; step: 0.05; value: root.morphSeconds; unit: " s"; onMoved: v => root.morphSeconds = v }
        Knob { label: qsTr("Arc"); from: 0; to: 0.8; step: 0.05; value: root.morphArc; onMoved: v => root.morphArc = v }
        Knob { label: qsTr("Spin"); from: -360; to: 360; step: 5; decimals: 0; value: root.morphSpin; unit: "°"; onMoved: v => root.morphSpin = v }
        Knob { label: qsTr("Trails"); from: 0; to: 8; step: 1; decimals: 0; value: root.morphTrails; onMoved: v => root.morphTrails = Math.round(v) }
        ThemedButton {
            width: parent.width
            variant: "primary"
            text: qsTr("Morph it")
            onClicked: EditorState.morphLayers(root.morphSeconds, root.morphTrails, root.morphArc, root.morphSpin)
        }
    }

    // ----- Liquid trail ----------------------------------------------------------------------
    Column {
        visible: root.tool === "trail"
        width: parent.width
        spacing: Theme.spacingSm
        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            size: "sm"
            opacity: 0.8
            text: qsTr("Select a layer that moves. Wherever it goes fast it throws liquid behind it, frame by frame, as Super Liquids does.")
        }
        Knob { label: qsTr("Drops a frame"); from: 1; to: 12; step: 1; decimals: 0; value: root.liquidPerFrame; onMoved: v => root.liquidPerFrame = Math.round(v) }
        Knob { label: qsTr("Frame skipping"); from: 1; to: 4; step: 1; decimals: 0; value: root.liquidSkip; onMoved: v => root.liquidSkip = Math.round(v) }
        Knob { label: qsTr("Speed threshold"); from: 0; to: 2000; step: 10; decimals: 0; value: root.liquidThreshold; onMoved: v => root.liquidThreshold = v }
        Knob { label: qsTr("Size"); from: 4; to: 80; step: 1; decimals: 0; value: root.liquidSize; unit: " px"; onMoved: v => root.liquidSize = v }
        Knob { label: qsTr("Velocity"); from: 0; to: 1.5; step: 0.05; value: root.liquidInherit; onMoved: v => root.liquidInherit = v }
        Knob { label: qsTr("Velocity random"); from: 0; to: 1.5; step: 0.05; value: root.liquidRandom; onMoved: v => root.liquidRandom = v }
        ThemedSwitch {
            width: parent.width
            text: qsTr("Horizontal (no gravity)")
            checked: root.liquidHorizontal
            onToggled: root.liquidHorizontal = checked
        }
    }

    // ----- Liquid line -----------------------------------------------------------------------
    Column {
        visible: root.tool === "line"
        width: parent.width
        spacing: Theme.spacingSm
        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            size: "sm"
            opacity: 0.8
            text: qsTr("Select a shape or a line drawn with the pen. A stream of liquid runs along it from the playhead.")
        }
        Knob { label: qsTr("Duration"); from: 0.3; to: 5; step: 0.1; value: root.lineSeconds; unit: " s"; onMoved: v => root.lineSeconds = v }
        Knob { label: qsTr("Thickness"); from: 4; to: 200; step: 1; decimals: 0; value: root.lineWidth; unit: " px"; onMoved: v => root.lineWidth = v }
        Knob { label: qsTr("Length"); from: 0.05; to: 1; step: 0.05; value: root.lineLength; onMoved: v => root.lineLength = v }
        Knob { label: qsTr("Roughness"); from: 0; to: 1; step: 0.05; value: root.lineRough; onMoved: v => root.lineRough = v }
    }

    // The liquid's colour (the first: the layer's own, when it is a shape).
    Row {
        visible: root.tool !== "morph"
        spacing: Theme.spacingSm
        ThemedLabel { anchors.verticalCenter: parent.verticalCenter; text: qsTr("Colour") }
        Repeater {
            model: root.colors
            delegate: Rectangle {
                id: swatch
                required property var modelData
                width: 22
                height: 22
                radius: 11
                color: swatch.modelData.length > 0 ? swatch.modelData : "transparent"
                border.width: root.liquidColor === swatch.modelData ? 2 : 1
                border.color: root.liquidColor === swatch.modelData ? Theme.primary : Theme.panelBorder
                Text {
                    anchors.centerIn: parent
                    visible: swatch.modelData.length === 0
                    text: "A"
                    color: Theme.panelForeground
                    font.pixelSize: Theme.fontSizeXs
                }
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.liquidColor = swatch.modelData
                }
            }
        }
    }
    ThemedButton {
        visible: root.tool !== "morph"
        width: parent.width
        variant: "primary"
        text: root.tool === "trail" ? qsTr("Generate liquid trail") : qsTr("Generate liquid line")
        onClicked: {
            if (root.tool === "trail")
                EditorState.generateLiquidTrail(root.liquidPerFrame, root.liquidSkip, root.liquidThreshold,
                                                root.liquidHorizontal, root.liquidInherit, root.liquidRandom,
                                                root.liquidSize, root.liquidColor)
            else
                EditorState.generateLiquidLine(root.lineSeconds, root.lineWidth, root.lineLength, root.lineRough,
                                               root.liquidColor)
        }
    }
}
