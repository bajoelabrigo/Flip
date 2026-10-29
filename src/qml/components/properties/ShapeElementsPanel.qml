import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// Motion Tools › Elements (0.26, Jorge: as the Super Morphings and Super Liquids scripts): animated
// shape elements of our own — shapes that turn into one another, and liquids (drops, splashes,
// drips, liquid transitions). A click puts one at the playhead as shape layers with an animated
// path, painted with the palette picked here; each layer can be recoloured or edited afterwards.
Column {
    id: root

    property string category: "morph"
    property int paletteIndex: 0
    readonly property var palettes: [
        ["#1fd1b8", "#ff7a3d", "#7a5cff"],
        ["#ff4d6d", "#ffd23f", "#3bceac"],
        ["#3a86ff", "#8338ec", "#ff006e"],
        ["#06d6a0", "#118ab2", "#073b4c"],
        ["#f72585", "#b5179e", "#4cc9f0"],
        ["#ffbe0b", "#fb5607", "#ff006e"],
        ["#ffffff", "#c9c9c9", "#1b1b1b"],
        ["#2ec4b6", "#e71d36", "#ff9f1c"]
    ]
    readonly property var colors: palettes[paletteIndex]
    readonly property var elements: EditorState.shapeElements(category)

    spacing: Theme.spacingMd

    AnimSlotTabs {
        width: parent.width
        model: [
            { "id": "morph", "label": qsTr("Morphings") },
            { "id": "liquid", "label": qsTr("Liquids") }
        ]
        current: root.category
        onActivated: id => root.category = id
    }

    ThemedLabel {
        width: parent.width
        wrapMode: Text.WordWrap
        size: "sm"
        opacity: 0.8
        text: qsTr("Click one to put it at the playhead. The transitions cover the whole screen.")
    }

    // The palettes: three colours each, the element's layers take them in order.
    Flow {
        width: parent.width
        spacing: Theme.spacingSm
        Repeater {
            model: root.palettes
            delegate: Rectangle {
                id: swatch
                required property var modelData
                required property int index
                width: 46
                height: 22
                radius: Theme.radiusSm
                color: "transparent"
                border.width: root.paletteIndex === index ? Theme.borderWidthFocus : Theme.borderWidth
                border.color: root.paletteIndex === index ? Theme.primary : Theme.panelBorder
                Row {
                    anchors.centerIn: parent
                    spacing: 2
                    Repeater {
                        model: swatch.modelData
                        Rectangle {
                            required property var modelData
                            width: 12
                            height: 14
                            radius: 2
                            color: modelData
                        }
                    }
                }
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.paletteIndex = swatch.index
                }
            }
        }
    }

    Grid {
        id: grid
        width: parent.width
        readonly property real gap: Theme.spacingMd
        columns: Math.max(3, Math.floor((width + gap) / (76 + gap)))
        columnSpacing: gap
        rowSpacing: gap
        readonly property real tileWidth: Math.floor((width - gap * (columns - 1)) / columns)

        Repeater {
            model: root.elements
            delegate: Column {
                id: tile
                required property var modelData
                width: grid.tileWidth
                spacing: 4
                property real progress: 0.45
                readonly property var frame: {
                    void tile.progress
                    return EditorState.shapeElementFrame(tile.modelData.id, tile.progress) || []
                }
                onFrameChanged: drawing.requestPaint()

                SequentialAnimation {
                    running: root.visible && !EditorState.playing && hover.hovered
                    loops: Animation.Infinite
                    onRunningChanged: if (!running) tile.progress = 0.45
                    NumberAnimation {
                        target: tile
                        property: "progress"
                        from: 0
                        to: 1
                        duration: Math.round(1000 * tile.modelData.duration)
                    }
                    PauseAnimation { duration: 300 }
                }

                Rectangle {
                    width: grid.tileWidth
                    height: grid.tileWidth
                    radius: Theme.radiusSm
                    color: "#0d0f12"
                    border.width: Theme.borderWidth
                    border.color: hover.hovered ? Theme.primary : Theme.textStylePreviewBorder
                    clip: true
                    Canvas {
                        id: drawing
                        anchors.fill: parent
                        // Another palette: the cards repaint in it.
                        Connections {
                            target: root
                            function onColorsChanged() { drawing.requestPaint() }
                        }
                        onPaint: {
                            const ctx = getContext("2d")
                            ctx.reset()
                            // The element's square fills the card; a transition's square (as big as the
                            // screen's diagonal) is shown smaller, so its growth reads.
                            const s = width / 100 * (tile.modelData.cover ? 0.55 : 1.0)
                            const off = tile.modelData.cover ? width * 0.225 : 0
                            for (const layer of tile.frame) {
                                ctx.save()
                                ctx.translate(off, off)
                                ctx.scale(s, s)
                                ctx.fillStyle = root.colors[layer.color % root.colors.length]
                                ctx.path = layer.svg
                                ctx.fill()
                                ctx.restore()
                            }
                        }
                    }
                    HoverHandler {
                        id: hover
                        cursorShape: Qt.PointingHandCursor
                    }
                    TapHandler {
                        onTapped: EditorState.insertShapeElement(tile.modelData.id, root.colors)
                    }
                }
                ThemedLabel {
                    width: grid.tileWidth
                    horizontalAlignment: Text.AlignHCenter
                    elide: Text.ElideRight
                    text: tile.modelData.label
                }
            }
        }
    }
}
