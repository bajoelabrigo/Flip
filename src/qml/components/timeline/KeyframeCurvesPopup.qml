import QtQuick
import QtQuick.Controls.Basic
import Drift

// Curvas, from a key's menu: the curves of the web editor's and the phone's (CapCut's Gráficos),
// for the stretches leaving the picked keys. A curve is a cubic-bezier (x1, y1, x2, y2, as CSS's);
// Salto is a hold.
Popup {
    id: root

    // Fired with the curve picked, or hold = true for Salto.
    signal curvePicked(real x1, real y1, real x2, real y2, bool hold)

    readonly property var presets: [
        { label: qsTr("Original"), curve: [1 / 3, 0, 2 / 3, 1] },
        { label: qsTr("Linear"), curve: [1 / 3, 1 / 3, 2 / 3, 2 / 3] },
        { label: qsTr("Ease in"), curve: [0.12, 0, 0.39, 0] },
        { label: qsTr("Ease out"), curve: [0.61, 1, 0.88, 1] },
        { label: qsTr("Ease in and out"), curve: [0.37, 0, 0.63, 1] },
        { label: qsTr("Cubic in"), curve: [0.32, 0, 0.67, 0] },
        { label: qsTr("Cubic out"), curve: [0.33, 1, 0.68, 1] },
        { label: qsTr("Cubic in and out"), curve: [0.65, 0, 0.35, 1] },
        { label: qsTr("Strong in"), curve: [0.64, 0, 0.78, 0] },
        { label: qsTr("Strong out"), curve: [0.22, 1, 0.36, 1] },
        { label: qsTr("Strong in and out"), curve: [0.83, 0, 0.17, 1] },
        { label: qsTr("Speed up"), curve: [0.7, 0, 0.84, 0] },
        { label: qsTr("Slow down"), curve: [0.16, 1, 0.3, 1] },
        { label: qsTr("Wind up"), curve: [0.36, 0, 0.66, -0.56] },
        { label: qsTr("Overshoot"), curve: [0.34, 1.56, 0.64, 1] },
        { label: qsTr("Bounce"), curve: [0.68, -0.6, 0.32, 1.6] },
        { label: qsTr("Hold"), hold: true }
    ]

    // How far along a curve is at time p, as CSS solves it (for drawing the tiles).
    function curveAt(c, p) {
        function cubic(p1, p2, s) {
            const u = 1 - s
            return 3 * u * u * s * p1 + 3 * u * s * s * p2 + s * s * s
        }
        let lo = 0
        let hi = 1
        for (let i = 0; i < 30; ++i) {
            const mid = (lo + hi) / 2
            if (cubic(c[0], c[2], mid) < p)
                lo = mid
            else
                hi = mid
        }
        return cubic(c[1], c[3], (lo + hi) / 2)
    }

    padding: Theme.spacingMd
    // Kept inside the window: opened low on the timeline it went off the bottom.
    margins: Theme.spacingMd
    modal: false
    focus: true
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

    background: Rectangle {
        color: Theme.panelBackground
        border.width: Theme.borderWidth
        border.color: Theme.panelBorder
        radius: Theme.radiusMd
    }

    contentItem: Column {
        spacing: Theme.spacingSm

        Text {
            text: qsTr("Curves")
            color: Theme.panelForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSm
            font.bold: true
        }

        Grid {
            columns: 4
            spacing: 6

            Repeater {
                model: root.presets
                delegate: Rectangle {
                    id: tile
                    required property var modelData
                    width: 74
                    height: 74
                    radius: 8
                    color: tileMouse.containsMouse ? Theme.popoverHover : Theme.panelSecondaryBg
                    border.width: 1
                    border.color: tileMouse.containsMouse ? Theme.primary : Theme.panelBorder

                    Canvas {
                        id: plot
                        x: 17
                        y: 6
                        width: 40
                        height: 40
                        onPaint: {
                            const ctx = getContext("2d")
                            ctx.reset()
                            ctx.strokeStyle = Qt.rgba(1, 1, 1, 0.25)
                            ctx.setLineDash([2, 2])
                            ctx.beginPath()
                            ctx.moveTo(4, 8); ctx.lineTo(36, 8)
                            ctx.moveTo(4, 32); ctx.lineTo(36, 32)
                            ctx.stroke()
                            ctx.setLineDash([])
                            ctx.strokeStyle = Theme.panelForeground
                            ctx.lineWidth = 2
                            ctx.beginPath()
                            for (let i = 0; i <= 24; ++i) {
                                const x = i / 24
                                const y = tile.modelData.hold ? (x < 1 ? 0 : 1)
                                                              : root.curveAt(tile.modelData.curve, x)
                                const px = 4 + x * 32
                                const py = 32 - y * 24
                                if (i === 0)
                                    ctx.moveTo(px, py)
                                else
                                    ctx.lineTo(px, py)
                            }
                            ctx.stroke()
                        }
                    }

                    Text {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        anchors.margins: 3
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                        maximumLineCount: 2
                        elide: Text.ElideRight
                        text: tile.modelData.label
                        color: Theme.panelForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: 10
                    }

                    MouseArea {
                        id: tileMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            const c = tile.modelData.curve || [0, 0, 1, 1]
                            root.curvePicked(c[0], c[1], c[2], c[3], !!tile.modelData.hold)
                            root.close()
                        }
                    }
                }
            }
        }
    }
}
