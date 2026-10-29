import QtQuick
import Drift
import ".."

// One Squash & Stretch animation (0.26): a little rubber block on the ground that moves, squashes
// and stretches the way the animation does, with the label under it. The block is bent with the
// same map as the "squash.deform" shader (stretch from the ground keeping the volume, bend growing
// with the square of the height, bulge halfway), from EditorState.squashAnimationPose. Plays in a
// loop while `playing`; still, it shows a telling moment.
Column {
    id: tile

    property string animId: ""
    property string label: ""
    property real seconds: 1.0
    property bool playing: false
    property real tileWidth: 76
    readonly property alias hovered: tileHover.hovered

    signal clicked()

    width: tileWidth
    spacing: 4

    property real progress: 0.35
    readonly property var pose: {
        void tile.progress
        return EditorState.squashAnimationPose(tile.animId, tile.progress) || {}
    }
    onPoseChanged: block.requestPaint()

    SequentialAnimation {
        running: tile.playing
        loops: Animation.Infinite
        onRunningChanged: if (!running) tile.progress = 0.35
        NumberAnimation {
            target: tile
            property: "progress"
            from: 0
            to: 1
            duration: Math.round(1000 * Math.max(0.5, tile.seconds))
        }
        PauseAnimation { duration: 400 }
    }

    Rectangle {
        width: tile.tileWidth
        height: tile.tileWidth
        radius: Theme.radiusSm
        color: "#0d0f12"
        border.width: Theme.borderWidth
        border.color: tileHover.hovered ? Theme.primary : Theme.textStylePreviewBorder
        clip: true

        // The ground line.
        Rectangle {
            x: parent.width * 0.1
            width: parent.width * 0.8
            y: parent.height * 0.78
            height: 1
            color: Theme.panelMuted
        }

        Canvas {
            id: block
            anchors.fill: parent
            onPaint: {
                const ctx = getContext("2d")
                ctx.reset()
                const p = tile.pose
                const W = width
                const H = height
                // The block's box on the card: a square standing on the ground line.
                const bw = W * 0.34
                const bh = W * 0.34
                const bx = W / 2 - bw / 2 + (p.x || 0) * W
                const by = H * 0.78 - bh + (p.y || 0) * H
                const sy = Math.max(0.05, 1 + (p.stretch || 0) / 100)
                const sx = Math.pow(sy, -1)
                const gy = (p.ground === undefined ? 100 : p.ground) / 100
                const z = Math.max(0, 1 + (p.zoom || 0) / 100)
                const bend = (p.bend || 0) / 100
                const bulge = (p.bulge || 0) / 100
                // The shader's map, forward: (u, v) of the box -> where it is drawn.
                const map = (u, v) => {
                    const far = v < gy ? Math.max(gy, 1e-4) : Math.max(1 - gy, 1e-4)
                    const t = Math.min(1, Math.abs(v - gy) / far)
                    const swell = 1 + bulge * 4 * t * (1 - t)
                    let x = 0.5 + (u - 0.5) * sx * swell + bend * t * t
                    let y = gy + (v - gy) * sy
                    x = 0.5 + (x - 0.5) * z
                    y = 0.5 + (y - 0.5) * z
                    return [bx + x * bw, by + y * bh]
                }
                const outline = []
                const n = 10
                for (let i = 0; i <= n; ++i) outline.push(map(i / n, 0))
                for (let i = 1; i <= n; ++i) outline.push(map(1, i / n))
                for (let i = n - 1; i >= 0; --i) outline.push(map(i / n, 1))
                for (let i = n - 1; i > 0; --i) outline.push(map(0, i / n))
                const cx = bx + bw / 2
                const cy = by + bh / 2
                ctx.save()
                ctx.globalAlpha = Math.max(0, Math.min(1, (p.opacity === undefined ? 100 : p.opacity) / 100))
                ctx.translate(cx, cy)
                ctx.rotate((p.rotation || 0) * Math.PI / 180)
                ctx.translate(-cx, -cy)
                ctx.beginPath()
                ctx.moveTo(outline[0][0], outline[0][1])
                for (let i = 1; i < outline.length; ++i)
                    ctx.lineTo(outline[i][0], outline[i][1])
                ctx.closePath()
                ctx.fillStyle = Theme.primary
                ctx.fill()
                // Two eyes, so which way it leans reads at a glance.
                ctx.fillStyle = "#0d0f12"
                for (const u of [0.35, 0.65]) {
                    const e = map(u, 0.35)
                    ctx.beginPath()
                    ctx.arc(e[0], e[1], Math.max(1.5, bw * 0.06), 0, Math.PI * 2)
                    ctx.fill()
                }
                ctx.restore()
            }
        }

        HoverHandler {
            id: tileHover
            cursorShape: Qt.PointingHandCursor
        }
        TapHandler {
            onTapped: tile.clicked()
        }
    }

    ThemedLabel {
        width: tile.tileWidth
        horizontalAlignment: Text.AlignHCenter
        elide: Text.ElideRight
        size: "xs"
        text: tile.label
    }
}
