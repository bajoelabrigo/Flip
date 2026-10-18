import QtQuick
import Drift

// A look's card that, while `playing` (the pointer on it), wipes between the photo as it was
// ("before", on the left of the line) and with the look ("after"), back and forth, as Filmora
// previews its filters (Jorge, 2026-10-18). At rest it is the plain "after" picture.
Item {
    id: root

    property url beforeSource
    property url afterSource
    property bool playing: false
    property int fillMode: Image.PreserveAspectCrop

    // 0: all "after"; 1: all "before". The line sits at that fraction of the width.
    property real split: 0

    clip: true

    Image {
        id: after
        anchors.fill: parent
        source: root.afterSource
        fillMode: root.fillMode
        asynchronous: true
    }

    Item {
        width: Math.round(parent.width * root.split)
        height: parent.height
        clip: true
        visible: root.split > 0
        Image {
            width: root.width
            height: root.height
            source: root.playing || root.split > 0 ? root.beforeSource : ""
            fillMode: root.fillMode
            asynchronous: true
        }
    }

    Rectangle {
        visible: root.split > 0 && root.split < 1
        x: Math.round(parent.width * root.split) - 1
        width: 2
        height: parent.height
        color: "#ffffff"
        opacity: 0.9
    }

    SequentialAnimation {
        running: root.playing
        loops: Animation.Infinite
        NumberAnimation { target: root; property: "split"; from: 0; to: 1; duration: 900; easing.type: Easing.InOutQuad }
        PauseAnimation { duration: 350 }
        NumberAnimation { target: root; property: "split"; from: 1; to: 0; duration: 900; easing.type: Easing.InOutQuad }
        PauseAnimation { duration: 500 }
        onRunningChanged: if (!running) root.split = 0
    }
}
