import QtQuick
import QtQuick.Effects
import Drift
import ".."

// One preset in Video › Animation: a small landscape that moves the way the preset moves a clip,
// with the label under it, as Filmora's gallery shows it. The pose is the preset's own curves,
// sampled by the engine (EditorState.clipAnimationPreviewSample); it holds still at a telling
// moment and plays in a loop while `playing`. An empty presetId is the "None" tile; `kind` set
// (e.g. "fade") is one of the built-in kinds, which have no preset to sample.
Column {
    id: tile

    property string slot: "in"
    property string presetId: ""
    property string kind: ""
    property string label: qsTr("None")
    property real seconds: 0.6
    property bool selected: false
    property bool playing: false
    // A trending preset: the flame in the corner (signed out, picking it asks for the account).
    property bool trending: false
    property real tileWidth: 76
    readonly property alias hovered: tileHover.hovered
    readonly property bool isNone: presetId.length === 0 && kind.length === 0

    signal clicked()

    width: tileWidth
    spacing: 4

    // Where the still card is read: mid-way through the move, where it shows best.
    readonly property real stillProgress: slot === "in" ? 0.45 : slot === "out" ? 0.55 : 0.3
    property real progress: stillProgress
    readonly property var pose: {
        void tile.progress
        if (tile.presetId.length > 0)
            return EditorState.clipAnimationPreviewSample(tile.presetId, tile.progress)
        if (tile.kind === "fade") {
            const p = tile.slot === "out" ? 1 - tile.progress : tile.progress
            return { dx: 0, dy: 0, scaleX: 1, scaleY: 1, rotation: 0, rotationX: 0, rotationY: 0, opacity: p, blur: 0 }
        }
        return { dx: 0, dy: 0, scaleX: 1, scaleY: 1, rotation: 0, rotationX: 0, rotationY: 0, opacity: 1, blur: 0 }
    }

    SequentialAnimation {
        running: tile.playing && !tile.isNone
        loops: Animation.Infinite
        onRunningChanged: if (!running) tile.progress = tile.stillProgress
        NumberAnimation {
            target: tile
            property: "progress"
            from: 0
            to: 1
            duration: Math.round(1000 * Math.max(0.4, tile.slot === "combo" ? Math.max(1.6, tile.seconds) : tile.seconds))
        }
        PauseAnimation { duration: 450 }
    }

    Rectangle {
        id: frame
        width: tile.tileWidth
        height: tile.tileWidth
        radius: Theme.radiusSm
        color: "#0d0f12"
        border.width: tile.selected ? Theme.borderWidthFocus : Theme.borderWidth
        border.color: tile.selected ? Theme.primary
                                    : (tileHover.hovered ? Theme.panelMuted : Theme.textStylePreviewBorder)
        clip: true

        Behavior on border.color {
            ColorAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
        }

        // The clip: a little landscape that fills the card, as a full-frame video would.
        Item {
            id: scene
            visible: !tile.isNone
            x: 2
            y: 2
            width: frame.width - 4
            height: frame.height - 4
            opacity: Math.max(0, Math.min(1, tile.pose.opacity))
            layer.enabled: tile.pose.blur > 0.5
            layer.effect: MultiEffect {
                blurEnabled: true
                blur: Math.min(1, tile.pose.blur / 40)
                blurMax: 24
            }
            transform: [
                Scale {
                    origin.x: scene.width / 2
                    origin.y: scene.height / 2
                    xScale: tile.pose.scaleX
                    yScale: tile.pose.scaleY
                },
                Rotation {
                    origin.x: scene.width / 2
                    origin.y: scene.height / 2
                    axis { x: 1; y: 0; z: 0 }
                    angle: -tile.pose.rotationX
                },
                Rotation {
                    origin.x: scene.width / 2
                    origin.y: scene.height / 2
                    axis { x: 0; y: 1; z: 0 }
                    angle: tile.pose.rotationY
                },
                Rotation {
                    origin.x: scene.width / 2
                    origin.y: scene.height / 2
                    angle: tile.pose.rotation
                },
                Translate {
                    x: tile.pose.dx * scene.width
                    y: tile.pose.dy * scene.height
                }
            ]

            Rectangle {
                anchors.fill: parent
                radius: 3
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#3fb6d9" }
                    GradientStop { position: 0.55; color: "#bfe7ef" }
                    GradientStop { position: 0.56; color: "#2f8fb3" }
                    GradientStop { position: 1.0; color: "#1d5f82" }
                }
            }
            Rectangle {
                x: parent.width * 0.66
                y: parent.height * 0.14
                width: parent.width * 0.16
                height: width
                radius: width / 2
                color: "#fff3c4"
            }
            Rectangle {
                x: -parent.width * 0.1
                y: parent.height * 0.42
                width: parent.width * 0.7
                height: parent.height * 0.5
                radius: height / 2
                color: "#3d8a4a"
            }
            Rectangle {
                x: parent.width * 0.42
                y: parent.height * 0.48
                width: parent.width * 0.8
                height: parent.height * 0.5
                radius: height / 2
                color: "#57a85a"
            }
            // A small orange car, so turns and flips read at a glance.
            Rectangle {
                x: parent.width * 0.3
                y: parent.height * 0.6
                width: parent.width * 0.36
                height: parent.height * 0.13
                radius: 3
                color: "#e8692c"
                Rectangle {
                    x: parent.width * 0.22
                    y: -parent.height * 0.55
                    width: parent.width * 0.5
                    height: parent.height * 0.65
                    radius: 2
                    color: "#d9e9f2"
                    border.width: 1
                    border.color: "#e8692c"
                }
                Repeater {
                    model: 2
                    Rectangle {
                        required property int index
                        x: index === 0 ? parent.width * 0.12 : parent.width * 0.66
                        y: parent.height * 0.6
                        width: parent.height * 0.75
                        height: width
                        radius: width / 2
                        color: "#20232a"
                    }
                }
            }
        }

        IconGlyph {
            anchors.centerIn: parent
            visible: tile.isNone
            glyph: Theme.icons.ban
            iconSize: Math.round(tile.tileWidth * 0.36)
            iconColor: Theme.mutedForeground
        }

        // A tap synthesises hover on a phone, so hover only means anything with a pointer.
        TrendBadge {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.margins: 3
            visible: tile.trending
        }

        HoverHandler { id: tileHover; enabled: !Theme.touchUi }

        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: {
                Haptics.select()
                tile.clicked()
            }
        }
    }

    Text {
        width: parent.width
        text: tile.label
        elide: Text.ElideMiddle
        horizontalAlignment: Text.AlignHCenter
        color: tile.selected ? Theme.primary : Theme.panelForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }
}
