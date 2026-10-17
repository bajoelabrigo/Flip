import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Shapes
import Drift
import ".."

// CapCut's mask shape tiles: each shape drawn as an outline from the path the compositor
// rasterizes, "None" as a no-entry sign, the current one outlined. Video > Mask and Adjust > Mask
// both use it; what a pick does (add a mask, change the one being edited, remove it) is theirs.
Grid {
    id: root

    // [{id, label}], in the order to show them.
    property var tiles: []
    // The tile of the mask being edited, or "none".
    property string currentId: "none"
    // A mask is being edited: a pick changes it (the tooltips say so) instead of adding one.
    property bool editing: false

    signal picked(string id)

    columns: Math.max(3, Math.floor((width + spacing) / (64 + spacing)))
    spacing: Theme.spacingSm
    readonly property real cell: (width - spacing * (columns - 1)) / columns

    Repeater {
        model: root.tiles
        delegate: Column {
            id: tile
            required property var modelData
            readonly property bool current: root.currentId === modelData.id
            width: root.cell
            spacing: 4

            Rectangle {
                width: parent.width
                height: width
                radius: Theme.radiusMd
                color: tileMouse.containsMouse ? Theme.popoverHover : Theme.panelAccent
                border.width: tile.current ? 2 : 1
                border.color: tile.current ? Theme.primary : Theme.panelBorder

                // "None": the no-entry sign.
                IconGlyph {
                    visible: tile.modelData.id === "none"
                    anchors.centerIn: parent
                    glyph: Theme.icons.ban
                    iconSize: parent.width * 0.42
                    iconColor: tile.current ? Theme.primary : Theme.mutedForeground
                }

                // The shape itself, from the path the compositor rasterizes, as an outline.
                Item {
                    visible: tile.modelData.id !== "none"
                    anchors.fill: parent
                    anchors.margins: parent.width * 0.2
                    readonly property real side: Math.min(width, height)

                    Item {
                        width: 100
                        height: 100
                        anchors.centerIn: parent
                        scale: parent.side / 100

                        Shape {
                            anchors.fill: parent
                            antialiasing: true
                            preferredRendererType: Shape.CurveRenderer

                            ShapePath {
                                strokeColor: tile.current ? Theme.primary : Theme.foreground
                                strokeWidth: 3.5
                                fillColor: tile.current ? Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.18) : "transparent"
                                joinStyle: ShapePath.RoundJoin
                                PathSvg { path: EditorState.maskShapeSvgPath(tile.modelData.id) }
                            }
                        }
                    }
                }

                scale: tileMouse.pressed ? 0.97 : (tileMouse.containsMouse ? 1.02 : 1.0)
                Behavior on scale {
                    NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                }

                MouseArea {
                    id: tileMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.picked(tile.modelData.id)
                }

                ThemedToolTip {
                    visible: tileMouse.containsMouse
                    text: tile.modelData.id === "none"
                          ? qsTr("Remove this mask")
                          : (root.editing ? qsTr("Change this mask to %1").arg(tile.modelData.label)
                                          : qsTr("Add a %1 mask").arg(tile.modelData.label))
                }
            }

            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
                text: tile.modelData.label
                color: tile.current ? Theme.foreground : Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
        }
    }
}
