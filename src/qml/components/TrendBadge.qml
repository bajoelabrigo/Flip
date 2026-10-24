import QtQuick
import Drift

// The flame on a trending card (Jorge, 2026-10-23: not a crown). Trending is for signed-in users
// today and premium later, so the card says so before the click. The owner anchors it to a corner.
Rectangle {
    id: root

    implicitWidth: 20
    implicitHeight: 20
    radius: width / 2
    color: Theme.warning

    IconGlyph {
        anchors.centerIn: parent
        glyph: Theme.icons.trending
        iconSize: 13
        iconColor: "white"
    }
}
