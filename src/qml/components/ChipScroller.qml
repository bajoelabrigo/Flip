import QtQuick
import Drift

// A row of chips on one line that scrolls sideways: a drag, the mouse wheel, or the arrows that
// show at a cut edge, which also fades so more chips read as waiting there. Chips go inside as
// children: ChipScroller { ThemedChip { … } Repeater { … } }.
Item {
    id: root

    default property alias chips: row.data
    readonly property bool cutLeft: flick.contentX > 1
    readonly property bool cutRight: flick.contentX + flick.width < flick.contentWidth - 1

    width: parent ? parent.width : 0
    implicitHeight: Theme.controlHeightSm

    function reset() { flick.contentX = 0 }

    function scrollBy(dx) {
        const target = Math.max(0, Math.min(flick.contentWidth - flick.width, flick.contentX + dx))
        slide.to = target
        slide.restart()
    }

    Flickable {
        id: flick
        anchors.fill: parent
        contentWidth: row.width
        contentHeight: height
        flickableDirection: Flickable.HorizontalFlick
        boundsBehavior: Flickable.StopAtBounds
        clip: true
        interactive: contentWidth > width

        NumberAnimation on contentX {
            id: slide
            running: false
            duration: 220
            easing.type: Easing.OutCubic
        }

        Row {
            id: row
            height: parent.height
            spacing: Theme.spacingSm
        }

        // A plain wheel turns into a sideways scroll while the chips overflow.
        WheelHandler {
            enabled: flick.contentWidth > flick.width
            orientation: Qt.Vertical
            acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
            onWheel: event => {
                const delta = event.angleDelta.y !== 0 ? event.angleDelta.y : event.angleDelta.x
                slide.stop()
                flick.contentX = Math.max(0, Math.min(flick.contentWidth - flick.width, flick.contentX - delta))
            }
        }
    }

    // The faded edges: the panel colour over the last chips on a cut side.
    Rectangle {
        visible: root.cutLeft
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: 44
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop { position: 0.35; color: Theme.panelBackground }
            GradientStop { position: 1.0; color: "transparent" }
        }
    }

    Rectangle {
        visible: root.cutRight
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: 44
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop { position: 0.0; color: "transparent" }
            GradientStop { position: 0.65; color: Theme.panelBackground }
        }
    }

    IconButton {
        visible: root.cutLeft
        anchors.left: parent.left
        anchors.verticalCenter: parent.verticalCenter
        glyph: Theme.icons.chevronLeft
        variant: "ghost"
        buttonSize: 22
        iconSize: 13
        tooltip: qsTr("Previous")
        onClicked: root.scrollBy(-flick.width * 0.7)
    }

    IconButton {
        visible: root.cutRight
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        glyph: Theme.icons.chevronRight
        variant: "ghost"
        buttonSize: 22
        iconSize: 13
        tooltip: qsTr("Next")
        onClicked: root.scrollBy(flick.width * 0.7)
    }
}
