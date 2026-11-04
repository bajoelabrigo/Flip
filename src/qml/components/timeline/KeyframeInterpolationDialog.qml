import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// After Effects' Keyframe Interpolation (0.30, Ctrl+Alt+K there): for the picked keys at once, how the
// value moves in time (Temporal), the path Position takes between them (Spatial) and whether the
// keys in the middle rove so the whole path keeps one speed. "Current settings" leaves that part be.
ThemedDialog {
    id: root

    property int trackIndex: -1
    property int clipIndex: -1
    property var keys: []
    readonly property bool hasPosition: root.keys.some((k) => k.prop === "x" || k.prop === "y")

    // Each picks one of these, in order (mode "" = as it is).
    readonly property var temporal: [
        { label: qsTr("Current settings"), mode: "" },
        { label: qsTr("Linear"), mode: "linear" },
        { label: qsTr("Bezier (smooth)"), mode: "ease" },
        { label: qsTr("Continuous Bezier"), mode: "auto" },
        { label: qsTr("Auto Bezier"), mode: "auto" },
        { label: qsTr("Hold"), mode: "hold" }
    ]
    readonly property var spatial: [
        { label: qsTr("Current settings"), mode: "" },
        { label: qsTr("Linear"), mode: "linear" },
        { label: qsTr("Bezier"), mode: "auto" },
        { label: qsTr("Continuous Bezier"), mode: "auto" },
        { label: qsTr("Auto Bezier"), mode: "auto" }
    ]
    readonly property var roving: [
        { label: qsTr("Current settings"), mode: "" },
        { label: qsTr("Rove across time"), mode: "rove" },
        { label: qsTr("Lock to time"), mode: "lock" }
    ]

    title: qsTr("Keyframe interpolation")
    acceptText: qsTr("OK")
    preferredWidth: Theme.dialogWidthSm

    function openFor(track, clip, picked) {
        root.trackIndex = track
        root.clipIndex = clip
        root.keys = picked || []
        temporalBox.currentIndex = 0
        spatialBox.currentIndex = 0
        rovingBox.currentIndex = 0
        if (root.keys.length > 0)
            open()
    }

    onAccepted: {
        const t = root.temporal[temporalBox.currentIndex].mode
        const s = root.hasPosition ? root.spatial[spatialBox.currentIndex].mode : ""
        const r = root.hasPosition ? root.roving[rovingBox.currentIndex].mode : ""
        if (t === "" && s === "" && r === "")
            return
        // Read everything before the first edit: the rows rebuild under it.
        const track = root.trackIndex
        const keys = root.keys.slice()
        const clips = []
        for (const k of keys) {
            if (clips.indexOf(k.clip) < 0)
                clips.push(k.clip)
        }
        EditorState.beginEditSession(qsTr("Keyframe interpolation"))
        try {
            if (t !== "")
                EditorState.setKeyframesEasing(track, keys, t)
            for (const c of clips) {
                const times = keys.filter((k) => k.clip === c && (k.prop === "x" || k.prop === "y"))
                                  .map((k) => k.seconds)
                if (times.length === 0)
                    continue
                if (s !== "")
                    EditorState.setPositionPath(track, c, s, times)
                if (r !== "")
                    EditorState.setPositionRoving(track, c, r === "rove")
            }
        } finally {
            EditorState.endEditSession(true)
        }
    }

    contentItem: Column {
        width: root.preferredWidth
        spacing: Theme.spacingMd

        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            size: "sm"
            opacity: 0.85
            text: qsTr("Temporal is how the value changes in time; Spatial is the path Position draws between the keys.")
        }

        ThemedLabel { text: qsTr("Temporal interpolation") }
        ThemedComboBox {
            id: temporalBox
            width: parent.width
            model: root.temporal.map((o) => o.label)
        }

        ThemedLabel { text: qsTr("Spatial interpolation"); visible: root.hasPosition }
        ThemedComboBox {
            id: spatialBox
            width: parent.width
            visible: root.hasPosition
            model: root.spatial.map((o) => o.label)
        }

        ThemedLabel { text: qsTr("Roving"); visible: root.hasPosition }
        ThemedComboBox {
            id: rovingBox
            width: parent.width
            visible: root.hasPosition
            model: root.roving.map((o) => o.label)
        }
    }
}
