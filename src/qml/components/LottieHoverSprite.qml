import QtQuick
import QtQuick.Window
import Drift

// Plays an animated sticker (a Lottie file) while its card is hovered, from the sprite grid
// image://lottie renders. Waits a moment first so sweeping the pointer across the grid does not
// render a sheet for every card it crosses; the image cache keeps a sheet for the next hover.
Item {
    id: root

    property string path: ""
    property bool hovered: false
    property int frames: 24
    property bool playing: false

    // AnimatedSprite has no load status of its own, so the same sheet goes through an Image
    // first: the still thumbnail stays up until the sheet is actually there to play.
    visible: playing && sheet.status === Image.Ready

    readonly property string sheetUrl: playing ? "image://lottie/" + encodeURIComponent(path)
                                                 + "?frames=" + frames + "&w=" + motion.cell + "&h=" + motion.cell : ""

    Image {
        id: sheet
        visible: false
        asynchronous: true
        source: root.sheetUrl
    }

    onHoveredChanged: {
        if (hovered && path.length > 0 && !Theme.touchUi)
            playDelay.restart()
        else {
            playDelay.stop()
            playing = false
        }
    }

    Timer {
        id: playDelay
        interval: 250
        onTriggered: root.playing = root.hovered
    }

    AnimatedSprite {
        id: motion
        anchors.centerIn: parent
        readonly property int cell: Math.max(16, Math.round(Math.min(root.width, root.height) * Screen.devicePixelRatio))
        width: Math.min(root.width, root.height)
        height: width
        source: sheet.status === Image.Ready ? root.sheetUrl : ""
        frameCount: root.frames
        frameWidth: cell
        frameHeight: cell
        frameRate: 20
        loops: AnimatedSprite.Infinite
        interpolate: false
        running: root.playing
    }
}
