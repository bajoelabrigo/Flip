import QtQuick
import Drift
import ".."

// What motion tracking shows on the preview, laid over the canvas rect like the other transform
// companions. Always: the box the selected element follows at the playhead, coloured by how sure
// the tracking was there (followed, lost, found again). While the Tracking tab offers a choice
// (MotionTrackController::chooser): the scanned faces, or the detected objects plus a box drawn
// by hand, picked with a click into MotionTrackController::pick.
//
// Coordinates come from the controller in canvas pixels; `scale` maps them onto this item.
Item {
    id: root

    readonly property var tracking: EditorState.motionTrack
    readonly property int trackIndex: EditorState.selectedTrack
    readonly property int clipIndex: EditorState.selectedClip
    // An invokable is not reactive: read again whenever the project changes (opening one, or a new
    // resolution), as CropOverlay does. Bound once, it kept the startup project's 1920 width.
    readonly property real projectW: {
        void EditorState.tracksRevision
        return Math.max(1, EditorState.projectFile.projectWidth())
    }
    readonly property real scale: width / projectW
    readonly property string chooser: root.tracking.chooser
    readonly property var pick: root.tracking.pick || ({})

    readonly property var target: {
        void EditorState.playheadSeconds
        void EditorState.tracksRevision
        void root.tracking.revision
        if (root.trackIndex < 0 || root.clipIndex < 0 || EditorState.playing)
            return ({})
        return root.tracking.targetAt(root.trackIndex, root.clipIndex)
    }
    readonly property var faces: {
        void EditorState.playheadSeconds
        void EditorState.tracksRevision
        void root.tracking.revision
        if (root.chooser !== "face" || EditorState.playing)
            return []
        return root.tracking.faceTargets(root.trackIndex, root.clipIndex)
    }

    function stateColor(state) {
        return state === "lost" ? Theme.warning : state === "recovered" ? Theme.constructive : Theme.primary
    }

    // A box drawn by hand around what to follow (Object). Below the picked boxes, so a click on
    // a detected object still picks it.
    MouseArea {
        id: drawArea
        anchors.fill: parent
        enabled: root.chooser === "object" && !root.tracking.busy
        visible: enabled
        cursorShape: Qt.CrossCursor
        property point origin
        property rect drawn
        property bool drawing: false
        onPressed: (mouse) => {
            origin = Qt.point(mouse.x, mouse.y)
            drawn = Qt.rect(mouse.x, mouse.y, 0, 0)
            drawing = true
        }
        onPositionChanged: (mouse) => {
            if (!drawing)
                return
            drawn = Qt.rect(Math.min(origin.x, mouse.x), Math.min(origin.y, mouse.y),
                            Math.abs(mouse.x - origin.x), Math.abs(mouse.y - origin.y))
        }
        onReleased: {
            drawing = false
            if (drawn.width < 6 || drawn.height < 6)
                return
            const c = Qt.rect(drawn.x / root.scale, drawn.y / root.scale,
                              drawn.width / root.scale, drawn.height / root.scale)
            const region = root.tracking.regionFromCanvas(root.trackIndex, root.clipIndex, c.x, c.y, c.width, c.height)
            if (!region.ok)
                return
            root.tracking.pick = {
                region: { x: region.x, y: region.y, w: region.w, h: region.h },
                classId: -1,
                canvas: { x: c.x, y: c.y, w: c.width, h: c.height }
            }
        }

        Rectangle {
            visible: drawArea.drawing
            x: drawArea.drawn.x
            y: drawArea.drawn.y
            width: drawArea.drawn.width
            height: drawArea.drawn.height
            color: "transparent"
            border.width: 2
            border.color: Theme.primary
        }
    }

    // The detected objects, to pick one.
    Repeater {
        model: root.chooser === "object" ? root.tracking.objectTargets : []
        delegate: Rectangle {
            required property var modelData
            readonly property bool picked: !!root.pick.region && root.pick.classId === modelData.classId
                                           && Math.abs(root.pick.region.x - modelData.region.x) < 1e-6
                                           && Math.abs(root.pick.region.y - modelData.region.y) < 1e-6
            x: modelData.x * root.scale
            y: modelData.y * root.scale
            width: modelData.w * root.scale
            height: modelData.h * root.scale
            color: objectArea.containsMouse || picked ? Qt.alpha(Theme.primary, 0.18) : "transparent"
            border.width: picked ? 3 : 2
            border.color: picked ? Theme.primary : Qt.alpha(Theme.onMedia, 0.85)
            radius: 4
            // A MouseArea, not a TapHandler: it keeps the press, so the click does not also reach the
            // preview below and select the video under the box.
            MouseArea {
                id: objectArea
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: root.tracking.pick = {
                    region: modelData.region,
                    classId: modelData.classId,
                    canvas: { x: modelData.x, y: modelData.y, w: modelData.w, h: modelData.h }
                }
            }
        }
    }

    // A drawn box once released: shown until something else is picked.
    Rectangle {
        visible: root.chooser === "object" && !!root.pick.canvas && root.pick.classId === -1
        x: visible ? root.pick.canvas.x * root.scale : 0
        y: visible ? root.pick.canvas.y * root.scale : 0
        width: visible ? root.pick.canvas.w * root.scale : 0
        height: visible ? root.pick.canvas.h * root.scale : 0
        color: Qt.alpha(Theme.primary, 0.18)
        border.width: 3
        border.color: Theme.primary
        radius: 4
    }

    // The scanned faces, to pick one. The selected one is the picked slot, else the controller's
    // choice (the stored one, or the face nearest the element).
    Repeater {
        model: root.faces
        delegate: Rectangle {
            required property var modelData
            readonly property bool picked: root.pick.faceSlot !== undefined ? root.pick.faceSlot === modelData.slot
                                                                         : !!modelData.selected
            x: modelData.x * root.scale
            y: modelData.y * root.scale
            width: modelData.w * root.scale
            height: modelData.h * root.scale
            radius: width / 2
            color: faceArea.containsMouse || picked ? Qt.alpha(Theme.primary, 0.15) : "transparent"
            border.width: picked ? 3 : 2
            border.color: picked ? Theme.primary : Qt.alpha(Theme.onMedia, 0.85)
            MouseArea {
                id: faceArea
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: root.tracking.pick = { faceSlot: modelData.slot }
            }
        }
    }

    // What the element follows at the playhead, with how sure the tracking was there.
    Rectangle {
        // Hidden while faces or objects are offered, so it does not hide them.
        visible: !!root.target.ok && root.faces.length === 0 && root.tracking.objectTargets.length === 0
        x: visible ? root.target.x * root.scale : 0
        y: visible ? root.target.y * root.scale : 0
        width: visible ? root.target.w * root.scale : 0
        height: visible ? root.target.h * root.scale : 0
        color: "transparent"
        border.width: 2
        border.color: root.stateColor(root.target.state)
        radius: 3

        Rectangle {
            visible: root.target.state === "lost"
            anchors.left: parent.left
            anchors.bottom: parent.top
            anchors.bottomMargin: 2
            width: lostLabel.implicitWidth + Theme.spacingMd
            height: lostLabel.implicitHeight + Theme.spacingXs
            radius: Theme.radiusXs
            color: Theme.warning
            Text {
                id: lostLabel
                anchors.centerIn: parent
                text: qsTr("Lost")
                color: Theme.onMedia
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
        }
    }
}
