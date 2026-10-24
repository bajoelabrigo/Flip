import QtQuick
import QtQuick.Shapes
import Drift

// A key drawn as After Effects draws it: the left half is how the value arrives at the key, the
// right half how it leaves — "linear" a point, "ease" a notch, "hold" a square side, "bezier" (a
// shape of its own) a round side. The same shapes as the web editor's (keyTypes.ts › keyIconPaths),
// in a 12×12 box.
Item {
    id: root

    property string inHalf: "linear"
    property string outHalf: "linear"
    property color color: Theme.primary
    property bool picked: false
    property bool lit: false // hovered or under the playhead
    property real size: 11

    width: size
    height: size

    readonly property var leftPaths: ({
        "linear": "M6 0 L0 6 L6 12 Z",
        "ease": "M6 0 L1 0 L4 6 L1 12 L6 12 Z",
        "hold": "M6 0 L1 0 Q0 0 0 1 L0 11 Q0 12 1 12 L6 12 Z",
        "bezier": "M6 0 A6 6 0 0 0 6 12 Z"
    })
    readonly property var rightPaths: ({
        "linear": "M6 0 L12 6 L6 12 Z",
        "ease": "M6 0 L11 0 L8 6 L11 12 L6 12 Z",
        "hold": "M6 0 L11 0 Q12 0 12 1 L12 11 Q12 12 11 12 L6 12 Z",
        "bezier": "M6 0 A6 6 0 0 1 6 12 Z"
    })
    // Picked keys turn red and grow (Jorge: easier to see than After Effects' yellow).
    readonly property color face: picked ? "#ff3b45" : (lit ? Qt.lighter(color, 1.35) : color)

    Shape {
        anchors.centerIn: parent
        width: 12
        height: 12
        scale: root.size / 12
        preferredRendererType: Shape.CurveRenderer

        ShapePath {
            fillColor: Qt.darker(root.face, 1.28)
            strokeColor: root.picked || root.lit ? "#ffffff" : Qt.rgba(0, 0, 0, 0.6)
            strokeWidth: root.picked ? 1.4 : 1
            joinStyle: ShapePath.RoundJoin
            PathSvg { path: root.leftPaths[root.inHalf] || root.leftPaths["linear"] }
        }
        ShapePath {
            fillColor: root.face
            strokeColor: root.picked || root.lit ? "#ffffff" : Qt.rgba(0, 0, 0, 0.6)
            strokeWidth: root.picked ? 1.4 : 1
            joinStyle: ShapePath.RoundJoin
            PathSvg { path: root.rightPaths[root.outHalf] || root.rightPaths["linear"] }
        }
    }
}
