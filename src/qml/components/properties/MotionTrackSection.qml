import QtQuick
import Drift
import ".."

// CapCut's and Filmora's Tracking: the selected text, sticker or picture follows something in the
// video under it. Object follows what the element covers at the playhead; Face follows the
// video's scanned face (scanned on the way if it has not been). The path becomes ordinary
// position (and size) keyframes, so it can be retouched afterwards.
Column {
    id: root

    property int clipDataRevision: 0
    property string mode: "object"
    property bool followScale: true

    readonly property var tracking: EditorState.motionTrack
    readonly property var info: {
        void root.clipDataRevision
        void EditorState.tracksRevision
        void EditorState.playheadSeconds
        return root.tracking.sourceFor(EditorState.selectedTrack, EditorState.selectedClip)
    }

    spacing: Theme.spacingSm

    Text {
        text: qsTr("Tracking")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
        font.weight: Font.Medium
    }

    Text {
        width: parent.width
        wrapMode: Text.WordWrap
        text: root.info.ok
              ? (root.mode === "object"
                 ? qsTr("Place it over what it should follow in “%1”, then start.").arg(root.info.source)
                 : qsTr("It will follow the face in “%1”.").arg(root.info.source))
              : (root.info.reason || "")
        color: root.info.ok ? Theme.mutedForeground : Theme.warning
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }

    Flow {
        width: parent.width
        spacing: 6
        enabled: root.info.ok && !root.tracking.busy
        ThemedChip {
            text: qsTr("Object")
            selected: root.mode === "object"
            onClicked: root.mode = "object"
        }
        ThemedChip {
            text: qsTr("Face")
            selected: root.mode === "face"
            onClicked: root.mode = "face"
        }
        ThemedChip {
            visible: !!root.info.canScale
            text: qsTr("Follow size too")
            selected: root.followScale
            onClicked: root.followScale = !root.followScale
        }
    }

    // The job's progress while it runs, with a way out.
    Row {
        width: parent.width
        spacing: Theme.spacingSm
        visible: root.tracking.busy
        ThemedProgressBar {
            width: parent.width - cancelButton.width - parent.spacing
            anchors.verticalCenter: parent.verticalCenter
            value: root.tracking.progress
        }
        ThemedButton {
            id: cancelButton
            variant: "ghost"
            text: qsTr("Cancel")
            onClicked: root.tracking.cancel()
        }
    }
    Text {
        width: parent.width
        visible: root.tracking.busy
        text: root.tracking.status
        elide: Text.ElideRight
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }

    Row {
        spacing: Theme.spacingSm
        visible: !root.tracking.busy
        ThemedButton {
            text: qsTr("Start tracking")
            glyph: Theme.icons.locateFixed
            enabled: root.info.ok
            tooltip: qsTr("Follow from the playhead to both ends of the clip")
            onClicked: root.tracking.track(EditorState.selectedTrack, EditorState.selectedClip, root.mode,
                                           root.followScale)
        }
        ThemedButton {
            variant: "ghost"
            text: qsTr("Remove tracking")
            tooltip: qsTr("Remove the position and size animation, leaving it where it is now")
            onClicked: root.tracking.clear(EditorState.selectedTrack, EditorState.selectedClip)
        }
    }
}
