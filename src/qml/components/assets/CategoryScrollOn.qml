import QtQuick
import Drift
import ".."

// CapCut-style continuous browsing of a categorised catalog: rolling the wheel on past the end of
// one category opens the next, and past the top the previous one (at its end). It lies over the
// category's grid or list and only takes the wheel at an end; every other wheel step and every
// click goes through to the grid. At the end a pill says which category comes next and fills up
// as the wheel keeps rolling, so the switch never comes as a surprise.
MouseArea {
    id: root

    property Flickable flickable
    // The chips' categories, [{id, label}]. Favorites and "mine" are not in it: from either, the
    // wheel leads into the first category.
    property var categories: []
    property string activeCategory: ""
    // Off while searching: the results are not a category.
    property bool active: true

    signal categoryActivated(string categoryId)

    acceptedButtons: Qt.NoButton
    z: 5

    property real overscroll: 0
    readonly property real threshold: 240

    readonly property int currentIndex: {
        for (let i = 0; i < categories.length; ++i) {
            if (categories[i].id === activeCategory)
                return i
        }
        return -1
    }
    readonly property var nextCategory: currentIndex + 1 < categories.length
                                        ? categories[currentIndex + 1] : null
    readonly property var previousCategory: currentIndex > 0 ? categories[currentIndex - 1] : null

    readonly property bool fits: !!flickable
                                 && flickable.contentHeight <= flickable.height + 1
    readonly property bool atEnd: !!flickable
                                  && (fits || flickable.contentY + flickable.height
                                      >= flickable.originY + flickable.contentHeight
                                         + flickable.bottomMargin - 2)
    readonly property bool atStart: !!flickable
                                    && (fits || flickable.contentY
                                        <= flickable.originY - flickable.topMargin + 2)

    function toStart() {
        if (flickable)
            flickable.contentY = flickable.originY - flickable.topMargin
    }
    function toEnd() {
        if (!flickable)
            return
        flickable.contentY = Math.max(flickable.originY - flickable.topMargin,
                                      flickable.originY + flickable.contentHeight
                                      + flickable.bottomMargin - flickable.height)
    }

    onActiveCategoryChanged: overscroll = 0

    onWheel: (wheel) => {
        const dy = wheel.angleDelta.y !== 0 ? wheel.angleDelta.y : wheel.pixelDelta.y
        const forward = dy < 0
        const target = forward ? root.nextCategory : root.previousCategory
        if (root.active && root.flickable && root.flickable.visible && dy !== 0 && target
                && ((forward && root.atEnd) || (!forward && root.atStart))) {
            // The other direction starts the count again.
            if ((root.overscroll > 0) !== forward)
                root.overscroll = 0
            root.overscroll += -dy
            if (Math.abs(root.overscroll) >= root.threshold) {
                root.overscroll = 0
                root.categoryActivated(target.id)
                // The grid swaps its model on the next pass; land at the top of the next category,
                // or the bottom of the previous one, once it has.
                Qt.callLater(() => { if (forward) root.toStart(); else root.toEnd() })
            }
            wheel.accepted = true
            return
        }
        root.overscroll = 0
        wheel.accepted = false
    }

    // "Keep scrolling for …", over the bottom of the grid once it is at its end.
    Rectangle {
        id: pill
        readonly property bool shown: root.active && !!root.nextCategory && root.atEnd
                                      && !!root.flickable && root.flickable.visible
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: Theme.spacingSm
        width: Math.min(parent.width - Theme.spacingLg * 2, pillText.implicitWidth + Theme.spacingLg * 2)
        height: pillText.implicitHeight + Theme.spacingSm * 2
        radius: height / 2
        color: Theme.panelSecondaryBg
        border.width: Theme.borderWidth
        border.color: Theme.panelBorder
        opacity: shown ? 0.96 : 0
        visible: opacity > 0
        clip: true

        Behavior on opacity {
            NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
        }

        // Fills as the wheel keeps rolling past the end.
        Rectangle {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: parent.width * Math.max(0, Math.min(1, root.overscroll / root.threshold))
            color: Theme.primary
            opacity: 0.25
        }

        Text {
            id: pillText
            anchors.centerIn: parent
            width: Math.min(implicitWidth, pill.width - Theme.spacingLg * 2)
            elide: Text.ElideRight
            text: root.nextCategory ? qsTr("Keep scrolling for %1").arg(root.nextCategory.label) : ""
            color: Theme.panelForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSm
        }
    }
}
