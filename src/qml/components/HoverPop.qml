import QtQuick
import Drift

// The small hover flourish on asset cards: `target` pops up a touch when the pointer arrives
// and, with `sway`, rocks gently from side to side while it stays. Leaving settles it back.
// Off on touch screens, where a tap synthesises hover and the card would twitch on every press.
Item {
    id: root

    property Item target
    property bool active: false
    property bool sway: true
    property real popScale: 1.12
    property real swayDegrees: 6

    readonly property bool running: active && !Theme.touchUi && target !== null

    onRunningChanged: {
        if (running) {
            settle.stop()
            pop.restart()
        } else {
            pop.stop()
            rock.stop()
            settle.restart()
        }
    }

    SequentialAnimation {
        id: pop
        NumberAnimation {
            target: root.target; property: "scale"
            to: root.popScale; duration: 160; easing.type: Easing.OutBack
        }
        ScriptAction { script: if (root.sway) rock.restart() }
    }

    SequentialAnimation {
        id: rock
        loops: Animation.Infinite
        NumberAnimation {
            target: root.target; property: "rotation"
            to: root.swayDegrees; duration: 260; easing.type: Easing.InOutSine
        }
        NumberAnimation {
            target: root.target; property: "rotation"
            to: -root.swayDegrees; duration: 520; easing.type: Easing.InOutSine
        }
        NumberAnimation {
            target: root.target; property: "rotation"
            to: 0; duration: 260; easing.type: Easing.InOutSine
        }
        PauseAnimation { duration: 500 }
    }

    ParallelAnimation {
        id: settle
        NumberAnimation {
            target: root.target; property: "scale"
            to: 1.0; duration: Theme.durationBase; easing.type: Easing.OutCubic
        }
        NumberAnimation {
            target: root.target; property: "rotation"
            to: 0; duration: Theme.durationBase; easing.type: Easing.OutCubic
        }
    }
}
