import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// What an adjustment or mask layer applies to, as Photoshop's adjustment layers: everything under
// it, or clipped to one photo, video or text below (the others stay untouched). Shared by the
// Adjustment layer tab and the Masks tab of a mask layer.
Column {
    id: root

    property int revision: 0
    readonly property var state: {
        void revision
        return EditorState.adjustmentTargetState(EditorState.selectedTrack, EditorState.selectedClip) || {}
    }
    readonly property bool available: !!state.mode
    readonly property bool isMaskLayer: state.kind === "mask"

    function kindLabel(kind) {
        switch (kind) {
        case "video": return qsTr("Video")
        case "image": return qsTr("Photo")
        case "text": return qsTr("Text")
        case "subtitle": return qsTr("Subtitles")
        case "shape": return qsTr("Shape")
        case "composite": return qsTr("Group")
        case "vector": return qsTr("Animation")
        default: return qsTr("Clip")
        }
    }

    // One entry per choice: everything below, the whole track it already sits on (only while that
    // is the case, so it can be kept), then each clip below it, nearest first.
    readonly property var choices: {
        const list = [{ text: qsTr("Everything below it"), track: -1, clip: -1 }]
        if (!available)
            return list
        const targets = state.targets || []
        if (state.mode === "track") {
            let label = qsTr("The whole track below")
            for (let i = 0; i < targets.length; ++i) {
                if (targets[i].track === state.targetTrack && targets[i].trackName) {
                    label = qsTr("The whole track «%1»").arg(targets[i].trackName)
                    break
                }
            }
            list.push({ text: label, track: state.targetTrack, clip: -1 })
        }
        for (let i = 0; i < targets.length; ++i) {
            const t = targets[i]
            list.push({ text: qsTr("Only %1: %2").arg(root.kindLabel(t.kind)).arg(t.name || qsTr("untitled")),
                        track: t.track, clip: t.clip, id: t.id })
        }
        return list
    }
    readonly property int currentChoice: {
        if (!available || state.mode === "allBelow")
            return 0
        for (let i = 1; i < choices.length; ++i) {
            const c = choices[i]
            if (state.mode === "track" && c.clip < 0 && c.track === state.targetTrack)
                return i
            if (state.mode === "clip" && c.id === state.targetClipId)
                return i
        }
        return 0
    }

    visible: available
    spacing: Theme.spacingSm

    Connections {
        target: EditorState
        function onSelectionChanged() { root.revision++ }
        function onSelectedClipDataChanged() { root.revision++ }
        function onTracksChanged() { root.revision++ }
    }

    Text {
        text: qsTr("Applies to")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }

    ThemedComboBox {
        id: targetBox
        width: parent.width
        model: root.choices
        textRole: "text"
        currentIndex: root.currentChoice
        tooltip: qsTr("Like an adjustment layer in Photoshop: over everything under it, or clipped to one clip")
        onActivated: function(index) {
            const c = root.choices[index]
            if (!c || index === root.currentChoice)
                return
            EditorState.setAdjustmentTarget(EditorState.selectedTrack, EditorState.selectedClip, c.track, c.clip)
        }
    }

    Text {
        width: parent.width
        wrapMode: Text.WordWrap
        text: root.currentChoice === 0
              ? (root.isMaskLayer
                 ? qsTr("The mask cuts everything under it while it lasts.")
                 : qsTr("Changes everything under it while it lasts."))
              : (root.isMaskLayer
                 ? qsTr("The mask cuts only that clip; the rest is untouched. It is drawn inside the clip's row on the timeline.")
                 : qsTr("Changes only that clip; the rest is untouched. It is drawn inside the clip's row on the timeline."))
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
        opacity: 0.8
    }
}
