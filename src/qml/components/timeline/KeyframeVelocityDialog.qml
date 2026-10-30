import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// After Effects' Keyframe Velocity (0.26): the speed the curve arrives and leaves a key with, in the
// property's units per second, and how far each handle reaches (influence, percent of the gap to
// the neighbouring key). "Continuous" keeps both sides at one speed.
ThemedDialog {
    id: root

    property int trackIndex: -1
    property int clipIndex: -1
    property string prop: ""
    property real seconds: 0
    property var vel: ({})

    title: qsTr("Keyframe velocity")
    acceptText: qsTr("Apply")
    preferredWidth: Theme.dialogWidthSm

    function openFor(track, clip, prop, seconds) {
        root.trackIndex = track
        root.clipIndex = clip
        root.prop = prop
        root.seconds = seconds
        root.vel = EditorState.keyVelocity(track, clip, prop, seconds) || {}
        if (!root.vel.valid)
            return
        inSpeed.value = root.vel.inSpeed || 0
        inInfluence.value = root.vel.inInfluence || 33.333
        outSpeed.value = root.vel.outSpeed || 0
        outInfluence.value = root.vel.outInfluence || 33.333
        continuous.checked = !!root.vel.hasIn && !!root.vel.hasOut
                             && Math.abs((root.vel.inSpeed || 0) - (root.vel.outSpeed || 0)) < 1e-6
        open()
    }

    onAccepted: {
        for (const field of [inSpeed, inInfluence, outSpeed, outInfluence])
            field.parseAndCommit()
        const v = {}
        if (root.vel.hasIn) {
            v.inSpeed = inSpeed.value
            v.inInfluence = inInfluence.value
        }
        if (root.vel.hasOut) {
            v.outSpeed = continuous.checked && root.vel.hasIn ? inSpeed.value : outSpeed.value
            v.outInfluence = outInfluence.value
        }
        EditorState.setKeyVelocity(root.trackIndex, root.clipIndex, root.prop, root.seconds, v)
    }

    contentItem: Column {
        width: root.preferredWidth
        spacing: Theme.spacingMd

        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            size: "sm"
            opacity: 0.85
            text: qsTr("Speed in units per second. Influence is how far the handle reaches towards the next key: more is a softer ease.")
        }

        ThemedLabel { text: qsTr("Incoming velocity"); visible: !!root.vel.hasIn }
        Row {
            width: parent.width
            spacing: Theme.spacingMd
            visible: !!root.vel.hasIn
            Column {
                width: (parent.width - parent.spacing) / 2
                spacing: 2
                ThemedLabel { text: qsTr("Speed"); size: "sm" }
                ThemedNumberField { id: inSpeed; width: parent.width; from: -1e7; to: 1e7; decimals: 2 }
            }
            Column {
                width: (parent.width - parent.spacing) / 2
                spacing: 2
                ThemedLabel { text: qsTr("Influence"); size: "sm" }
                ThemedNumberField { id: inInfluence; width: parent.width; from: 0.1; to: 100; decimals: 2; unit: "%" }
            }
        }

        ThemedLabel { text: qsTr("Outgoing velocity"); visible: !!root.vel.hasOut }
        Row {
            width: parent.width
            spacing: Theme.spacingMd
            visible: !!root.vel.hasOut
            Column {
                width: (parent.width - parent.spacing) / 2
                spacing: 2
                ThemedLabel { text: qsTr("Speed"); size: "sm" }
                ThemedNumberField {
                    id: outSpeed
                    width: parent.width
                    from: -1e7
                    to: 1e7
                    decimals: 2
                    enabled: !continuous.checked
                }
            }
            Column {
                width: (parent.width - parent.spacing) / 2
                spacing: 2
                ThemedLabel { text: qsTr("Influence"); size: "sm" }
                ThemedNumberField { id: outInfluence; width: parent.width; from: 0.1; to: 100; decimals: 2; unit: "%" }
            }
        }

        ThemedCheckBox {
            id: continuous
            visible: !!root.vel.hasIn && !!root.vel.hasOut
            text: qsTr("Continuous (the same speed on both sides)")
        }
    }
}
