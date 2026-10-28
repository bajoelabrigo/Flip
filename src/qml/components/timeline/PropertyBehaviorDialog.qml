import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// After Effects' most used expressions as a behaviour of one property (0.26): loopOut (cycle,
// ping-pong, offset, continue), time × speed and wiggle, which add up in that order. Opened from a
// keyframe row's menu.
ThemedDialog {
    id: root

    property int trackIndex: -1
    property int clipIndex: -1
    // The props of the row (X and Y for Position); all of them take the same behaviour.
    property var props: []
    property string label: ""

    readonly property var loops: [
        { id: "none", label: qsTr("No loop") },
        { id: "cycle", label: qsTr("Cycle (repeat the keys)") },
        { id: "pingpong", label: qsTr("Ping-pong (back and forth)") },
        { id: "offset", label: qsTr("Offset (repeat, adding up)") },
        { id: "continue", label: qsTr("Continue (keep the last speed)") }
    ]

    title: qsTr("Behavior · %1").arg(label)
    acceptText: qsTr("Apply")
    preferredWidth: Theme.dialogWidthSm

    function openFor(track, clip, props, label) {
        root.trackIndex = track
        root.clipIndex = clip
        root.props = props
        root.label = label
        const b = EditorState.propertyBehavior(track, clip, props[0]) || {}
        let li = 0
        for (let i = 0; i < loops.length; ++i) {
            if (loops[i].id === (b.loop || "none"))
                li = i
        }
        loopBox.currentIndex = li
        wiggleSwitch.checked = (b.wiggleFrequency || 0) > 0 && (b.wiggleAmount || 0) !== 0
        frequencyField.value = b.wiggleFrequency > 0 ? b.wiggleFrequency : 2
        amountField.value = b.wiggleAmount ? b.wiggleAmount : 20
        seedField.value = b.wiggleSeed || 0
        speedField.value = b.speed || 0
        expressionField.text = b.expression || ""
        open()
    }

    function behavior() {
        return {
            loop: loops[loopBox.currentIndex].id,
            speed: speedField.value,
            wiggleFrequency: wiggleSwitch.checked ? frequencyField.value : 0,
            wiggleAmount: wiggleSwitch.checked ? amountField.value : 0,
            wiggleSeed: Math.round(seedField.value),
            expression: expressionField.text
        }
    }

    onAccepted: {
        for (const field of [frequencyField, amountField, seedField, speedField])
            field.parseAndCommit()
        const b = behavior()
        for (const prop of root.props)
            EditorState.setPropertyBehavior(root.trackIndex, root.clipIndex, prop, b)
    }

    contentItem: Column {
        width: root.preferredWidth
        spacing: Theme.spacingMd

        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            size: "sm"
            opacity: 0.85
            text: qsTr("What After Effects does with expressions, without writing code. They add up: the loop, then the constant speed, then the wiggle.")
        }

        ThemedLabel { text: qsTr("Loop after the last keyframe") }
        ThemedComboBox {
            id: loopBox
            width: parent.width
            model: root.loops.map(l => l.label)
        }

        ThemedSwitch {
            id: wiggleSwitch
            width: parent.width
            text: qsTr("Wiggle")
            tooltip: qsTr("A smooth random shake around the value, like wiggle(frequency, amount)")
        }
        Row {
            width: parent.width
            spacing: Theme.spacingMd
            visible: wiggleSwitch.checked
            Column {
                width: (parent.width - 2 * parent.spacing) / 3
                spacing: 2
                ThemedLabel { text: qsTr("Per second"); size: "sm" }
                ThemedNumberField { id: frequencyField; width: parent.width; from: 0.01; to: 60; step: 0.5; decimals: 2 }
            }
            Column {
                width: (parent.width - 2 * parent.spacing) / 3
                spacing: 2
                ThemedLabel { text: qsTr("Amount"); size: "sm" }
                ThemedNumberField { id: amountField; width: parent.width; from: -100000; to: 100000; step: 1; decimals: 2 }
            }
            Column {
                width: (parent.width - 2 * parent.spacing) / 3
                spacing: 2
                ThemedLabel { text: qsTr("Seed"); size: "sm" }
                ThemedNumberField { id: seedField; width: parent.width; from: 0; to: 9999; step: 1 }
            }
        }

        ThemedLabel { text: qsTr("Constant speed (per second)") }
        ThemedNumberField {
            id: speedField
            width: parent.width
            from: -100000
            to: 100000
            step: 1
            decimals: 2
        }
        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            size: "sm"
            opacity: 0.7
            text: qsTr("For example 90 on Rotation turns the layer a quarter turn every second, for as long as the clip lasts.")
        }

        // After Effects' expression, in JavaScript (0.26): run last, on the value with all the above.
        ThemedLabel { text: qsTr("Expression (JavaScript)") }
        ThemedTextArea {
            id: expressionField
            width: parent.width
            height: 72
            placeholderText: "value + wiggle(2, 10) - value  /  time * 90  /  thisComp.layer(\"Nulo 1\").transform.rotation"
            font.family: "Consolas"
        }
        ThemedLabel {
            readonly property string error: EditorState.checkExpression(expressionField.text)
            width: parent.width
            wrapMode: Text.WordWrap
            size: "sm"
            color: error.length > 0 ? "#e5484d" : Theme.mutedForeground
            text: error.length > 0 ? error
                                   : qsTr("value, time, wiggle(freq, amount), Math, and thisComp.layer(\"Name\").transform.position[0], .rotation, .scale[0], .opacity, .anchorPoint[0]. The last line is the result.")
        }
    }
}
