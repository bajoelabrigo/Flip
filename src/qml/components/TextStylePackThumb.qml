import QtQuick
import Drift

// Shared style-pack thumbnail: dark canvas so light glyphs stay legible in both themes.
Item {
    id: root

    property string presetId: ""
    property bool selected: false
    property bool hovered: false
    // Play only on a pointer hover, after a short rest, so sweeping across the grid stays cheap.
    property bool playing: false
    onHoveredChanged: {
        if (hovered && presetId.length > 0 && !Theme.touchUi)
            playDelay.restart()
        else {
            playDelay.stop()
            playing = false
        }
    }

    Timer {
        id: playDelay
        interval: 350
        onTriggered: root.playing = root.hovered
    }

    // Landscape cards match the properties picker; assets can size freely.
    implicitWidth: 120
    implicitHeight: Math.round(implicitWidth * 0.5)

    Rectangle {
        anchors.fill: parent
        radius: Theme.radiusSm
        color: Theme.textStylePreviewBg
        border.width: root.selected ? Theme.borderWidthFocus : Theme.borderWidth
        border.color: root.selected ? Theme.primary
                                    : (root.hovered ? Theme.panelMuted : Theme.textStylePreviewBorder)
        clip: true

        Behavior on border.color {
            ColorAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
        }

        // Hovering plays the style: its entrance and, for karaoke, the word moving along.
        AnimatedSprite {
            id: motion
            anchors.fill: parent
            anchors.margins: 4
            readonly property int frameW: Math.max(16, Math.round(width))
            readonly property int frameH: Math.max(16, Math.round(height))
            visible: root.playing
            source: root.playing ? "image://textstyle/" + root.presetId + "?frames=24&w=" + frameW + "&h=" + frameH : ""
            frameCount: 24
            frameWidth: frameW
            frameHeight: frameH
            frameRate: 10
            loops: AnimatedSprite.Infinite
            interpolate: false
            running: root.playing
        }

        Image {
            anchors.fill: parent
            anchors.margins: 4
            visible: root.presetId.length > 0 && !root.playing
            asynchronous: true
            fillMode: Image.Pad
            source: root.presetId.length > 0 ? ("image://textstyle/" + root.presetId) : ""
            sourceSize.width: Math.max(1, Math.round(width))
            sourceSize.height: Math.max(1, Math.round(height))
        }

        Text {
            anchors.centerIn: parent
            visible: root.presetId.length === 0
            text: qsTr("Custom")
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }
    }
}
