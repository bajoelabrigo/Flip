import QtQuick
import QtQuick.Effects
import Drift

// The Flip Studio account's picture in a circle: the Google photo once it loads, the person icon
// before that or when signed out. A plain clip would cut the photo square, hence the mask.
Item {
    id: root

    property real size: 28

    width: size
    height: size

    Rectangle {
        anchors.fill: parent
        radius: width / 2
        color: Theme.panelMuted
    }

    IconGlyph {
        anchors.centerIn: parent
        glyph: Theme.icons.account
        iconSize: Math.round(root.size * 0.62)
        iconColor: Theme.mutedForeground
        visible: photo.status !== Image.Ready
    }

    Image {
        id: photo
        anchors.fill: parent
        source: Account.signedIn ? Account.avatarUrl : ""
        sourceSize: Qt.size(root.size * 2, root.size * 2)
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        visible: false
    }

    Rectangle {
        id: circle
        anchors.fill: parent
        radius: width / 2
        visible: false
        layer.enabled: true
    }

    MultiEffect {
        anchors.fill: parent
        source: photo
        visible: photo.status === Image.Ready
        maskEnabled: true
        maskSource: circle
        maskThresholdMin: 0.5
        maskSpreadAtMin: 1.0
    }
}
