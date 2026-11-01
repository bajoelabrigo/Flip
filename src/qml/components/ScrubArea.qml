import QtQuick
import Drift

// After Effects' scrubby values (0.29, Jorge): over a number the pointer turns into ↔, dragging sideways
// raises or lowers it (Shift ten times faster, Ctrl ten times finer) and a click without a drag hands the
// field the keyboard to type. The owner listens to started / scrubbed / finished / clickedWithoutDrag.
MouseArea {
    id: root

    property real value: 0             // the value when the drag starts
    property real stepPerPixel: 1
    property real from: -1e9
    property real to: 1e9
    readonly property bool scrubbing: _active

    signal started()
    signal scrubbed(real value)
    signal finished()
    signal clickedWithoutDrag()

    property real _startX: 0
    property real _startValue: 0
    property bool _active: false

    hoverEnabled: true
    cursorShape: Qt.SizeHorCursor
    preventStealing: true
    // The wheel scrolls the panel underneath, as before the fields could be dragged.
    onWheel: wheel => { wheel.accepted = false }

    onPressed: mouse => {
        _startX = mouse.x
        _startValue = root.value
        _active = false
    }
    onPositionChanged: mouse => {
        if (!pressed)
            return
        const dx = mouse.x - _startX
        if (!_active) {
            if (Math.abs(dx) < 3)
                return
            _active = true
            root.started()
        }
        let factor = 1
        if (mouse.modifiers & Qt.ShiftModifier)
            factor = 10
        else if (mouse.modifiers & Qt.ControlModifier)
            factor = 0.1
        const v = Math.max(root.from, Math.min(root.to, _startValue + dx * root.stepPerPixel * factor))
        root.scrubbed(v)
    }
    onReleased: {
        if (_active) {
            _active = false
            root.finished()
        } else {
            root.clickedWithoutDrag()
        }
    }
    onCanceled: if (_active) {
        _active = false
        root.finished()
    }
}
