import QtQuick
import QtQuick.Controls.Basic
import Drift

// After Effects-style workspaces (0.26, Jorge: «sería bueno tener variaciones como After Effects,
// y que las ventanas se puedan distribuir»). A workspace is a tree of splits whose leaves are the
// editor's four panels:
//
//   { "d": "h" | "v", "c": [child, …] }   a split (horizontal: side by side; vertical: stacked)
//   { "p": "assets" | "preview" | "properties" | "timeline" }   a panel
//
// and any node may carry "f", its share of the split it sits in; the one child without "f" takes
// what is left. The panels are the editor's live instances: they are only ever re-parented into
// the leaves, never rebuilt (the preview owns the video sink and the GL runtime).
//
// In layout mode (Window › Arrange panels) every panel shows its name; drag it onto another panel
// to swap the two, or onto that panel's edge to dock it there. Panels can be hidden and shown.
// After a handle drag the new sizes are reported through layoutEdited(tree).
Item {
    id: root

    // panel id → Item (the live instances).
    property var panels: ({})
    // The tree being shown.
    property var tree: null
    // Layout mode: names over the panels, drag to rearrange.
    property bool arranging: false

    signal layoutEdited(var tree)

    readonly property var panelLabels: ({
        "assets": qsTr("Library"),
        "preview": qsTr("Preview"),
        "properties": qsTr("Properties"),
        "timeline": qsTr("Timeline")
    })
    // The smallest a panel can be shrunk to, along each direction.
    readonly property var minimums: ({
        "assets": { "w": 200, "h": 120 },
        "preview": { "w": 260, "h": 160 },
        "properties": { "w": 340, "h": 140 },
        "timeline": { "w": 300, "h": 140 }
    })

    // Panels the tree does not show wait here, alive and hidden.
    Item {
        id: stash
        visible: false
        width: 1
        height: 1
    }

    // ----- Tree helpers (pure) ------------------------------------------------------------------
    function clone(v) { return JSON.parse(JSON.stringify(v)) }
    function panelsIn(node) {
        if (!node)
            return []
        if (node.p)
            return [node.p]
        let out = []
        for (const c of node.c || [])
            out = out.concat(root.panelsIn(c))
        return out
    }
    // The tree without panel `p`; a split left with one child is replaced by it.
    function without(node, p) {
        if (!node)
            return null
        if (node.p)
            return node.p === p ? null : node
        const kept = []
        for (const c of node.c) {
            const n = root.without(c, p)
            if (n)
                kept.push(n)
        }
        if (kept.length === 0)
            return null
        if (kept.length === 1) {
            const only = kept[0]
            if (node.f !== undefined)
                only.f = node.f
            else
                delete only.f
            return only
        }
        // Keep one child filling the split.
        if (!kept.some(c => c.f === undefined))
            delete kept[kept.length - 1].f
        return { "d": node.d, "c": kept, "f": node.f }
    }
    // The tree with the leaf of panel `target` replaced by what `make(leaf)` returns.
    function replacing(node, target, make) {
        if (node.p)
            return node.p === target ? make(node) : node
        return { "d": node.d, "c": node.c.map(c => root.replacing(c, target, make)), "f": node.f }
    }
    // Panel `p` docked on `side` ("left", "right", "top", "bottom") of panel `target`.
    function docked(tree, p, target, side) {
        let t = root.without(root.clone(tree), p)
        if (!t)
            return { "p": p }
        const horizontal = side === "left" || side === "right"
        return root.replacing(t, target, leaf => {
            const moved = { "p": p, "f": horizontal ? 0.3 : 0.35 }
            const stay = { "p": leaf.p }
            const c = side === "left" || side === "top" ? [moved, stay] : [stay, moved]
            return { "d": horizontal ? "h" : "v", "c": c, "f": leaf.f }
        })
    }
    function swapped(tree, a, b) {
        const t = root.clone(tree)
        const walk = n => {
            if (n.p === a)
                n.p = b
            else if (n.p === b)
                n.p = a
            else
                for (const c of n.c || [])
                    walk(c)
        }
        walk(t)
        return t
    }
    // Panel `p` brought back in its usual place: the library left of the preview, the properties
    // right of it, the timeline under everything, the preview right of everything.
    function shown(tree, p) {
        const present = root.panelsIn(tree)
        if (present.indexOf(p) >= 0)
            return tree
        if (!tree)
            return { "p": p }
        if (p === "timeline")
            return { "d": "v", "c": [Object.assign(root.clone(tree), { "f": undefined }), { "p": "timeline", "f": 0.4 }] }
        if (present.indexOf("preview") < 0 || p === "preview")
            return { "d": "h", "c": [Object.assign(root.clone(tree), { "f": undefined }), { "p": p, "f": 0.35 }] }
        return root.docked(root.clone(tree), p, "preview", p === "assets" ? "left" : "right")
    }

    // ----- Building -----------------------------------------------------------------------------
    property Item built: null
    property var leaves: ({})

    Component {
        id: splitComponent
        SplitView {
            id: split
            property var node
            handle: PanelSplitHandle { view: split }
            spacing: Theme.panelGap
            onResizingChanged: if (!resizing) root.capture()
        }
    }
    Component {
        id: leafComponent
        Item {
            id: leaf
            property string panelId
            clip: true

            // Layout mode: the panel's name, to drag elsewhere.
            Rectangle {
                id: badge
                z: 1000
                visible: root.arranging
                anchors.fill: parent
                color: Qt.rgba(0, 0, 0, root.dropTarget === leaf.panelId ? 0.15 : 0.35)
                border.width: root.dragging === leaf.panelId ? 3 : 2
                border.color: Theme.primary
                radius: Theme.radiusMd

                Rectangle {
                    anchors.centerIn: parent
                    width: label.implicitWidth + 32
                    height: label.implicitHeight + 16
                    radius: height / 2
                    color: Theme.primary
                    Text {
                        id: label
                        anchors.centerIn: parent
                        text: "⠿  " + (root.panelLabels[leaf.panelId] || leaf.panelId)
                        color: Theme.primaryForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeBase
                        font.bold: true
                    }
                }
                // Where it would land, while another panel is dragged over this one.
                Rectangle {
                    visible: root.dropTarget === leaf.panelId && root.dropSide.length > 0
                    color: Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.45)
                    radius: Theme.radiusSm
                    x: root.dropSide === "right" ? parent.width * 0.6 : 0
                    y: root.dropSide === "bottom" ? parent.height * 0.6 : 0
                    width: root.dropSide === "left" || root.dropSide === "right" ? parent.width * 0.4 : parent.width
                    height: root.dropSide === "top" || root.dropSide === "bottom" ? parent.height * 0.4 : parent.height
                }
                IconButton {
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.margins: 8
                    glyph: Theme.icons.x
                    variant: "ghost"
                    tooltip: qsTr("Hide this panel")
                    visible: root.panelsIn(root.tree).length > 1
                    onClicked: root.layoutEdited(root.without(root.clone(root.tree), leaf.panelId))
                }
                MouseArea {
                    anchors.fill: parent
                    anchors.topMargin: 44
                    cursorShape: pressed ? Qt.ClosedHandCursor : Qt.OpenHandCursor
                    preventStealing: true
                    onPressed: root.dragging = leaf.panelId
                    onPositionChanged: mouse => {
                        const p = mapToItem(root, mouse.x, mouse.y)
                        root.track(p.x, p.y)
                    }
                    onReleased: root.drop()
                    onCanceled: { root.dragging = ""; root.dropTarget = "" }
                }
            }
        }
    }

    function build() {
        for (const id in root.panels) {
            const item = root.panels[id]
            if (item) {
                item.parent = stash
                item.anchors.fill = undefined
            }
        }
        if (root.built) {
            root.built.visible = false
            root.built.destroy()
            root.built = null
        }
        root.leaves = {}
        if (!root.tree)
            return
        root.built = root.make(root.tree, root, "")
        if (root.built) {
            root.built.anchors.fill = root
        }
    }

    // One node, inside `parentSplit` (or the root): returns the Item.
    function make(node, host, parentDir) {
        let item
        if (node.p) {
            item = leafComponent.createObject(host, { "panelId": node.p })
            const panel = root.panels[node.p]
            if (panel) {
                panel.parent = item
                panel.anchors.fill = item
                panel.visible = true
            }
            const l = root.leaves
            l[node.p] = item
            root.leaves = l
        } else {
            item = splitComponent.createObject(host, { "node": node,
                                                       "orientation": node.d === "h" ? Qt.Horizontal : Qt.Vertical })
            const fills = node.c.filter(c => c.f === undefined)
            const filler = fills.length > 0 ? fills[0] : node.c[node.c.length - 1]
            for (const c of node.c) {
                // Created outside the split and handed to it with addItem: a Container only
                // takes items it is given that way.
                const child = root.make(c, root, node.d)
                if (node.d === "h") {
                    if (c === filler)
                        child.SplitView.fillWidth = true
                    else
                        child.SplitView.preferredWidth = Qt.binding(() => Math.max(0, item.width * c.f))
                    child.SplitView.minimumWidth = Qt.binding(() => Math.min(root.minAlong(c, "w"), Math.max(0, item.width * 0.25)))
                } else {
                    if (c === filler)
                        child.SplitView.fillHeight = true
                    else
                        child.SplitView.preferredHeight = Qt.binding(() => Math.max(0, item.height * c.f))
                    child.SplitView.minimumHeight = Qt.binding(() => Math.min(root.minAlong(c, "h"), Math.max(0, item.height * 0.25)))
                }
                item.addItem(child)
            }
        }
        return item
    }
    // A node's minimum along "w" or "h": a panel's own, or the sum / largest of its children's.
    function minAlong(node, axis) {
        if (node.p)
            return (root.minimums[node.p] || { "w": 120, "h": 100 })[axis]
        const along = (node.d === "h") === (axis === "w")
        let total = 0
        for (const c of node.c)
            total = along ? total + root.minAlong(c, axis) : Math.max(total, root.minAlong(c, axis))
        return total
    }

    // The tree as it is on screen now: every node's share from its real size.
    function measured(node, item) {
        if (node.p)
            return { "p": node.p }
        const out = { "d": node.d, "c": [] }
        const fills = node.c.filter(c => c.f === undefined)
        const filler = fills.length > 0 ? fills[0] : node.c[node.c.length - 1]
        const total = node.d === "h" ? item.width : item.height
        for (let i = 0; i < node.c.length; ++i) {
            const c = node.c[i]
            const childItem = item.itemAt(i)
            const m = root.measured(c, childItem)
            if (c !== filler && total > 0)
                m.f = Math.round((node.d === "h" ? childItem.width : childItem.height) / total * 1000) / 1000
            out.c.push(m)
        }
        return out
    }
    function capture() {
        if (!root.built || !root.tree || root.tree.p)
            return
        const t = root.measured(root.tree, root.built)
        if (root.tree.f !== undefined)
            t.f = root.tree.f
        root.captured = JSON.stringify(t)
        root.layoutEdited(t)
    }

    // ----- Dragging panels in layout mode ---------------------------------------------------------
    property string dragging: ""
    property string dropTarget: ""
    property string dropSide: ""
    function track(x, y) {
        root.dropTarget = ""
        root.dropSide = ""
        for (const id in root.leaves) {
            const l = root.leaves[id]
            if (!l || id === root.dragging)
                continue
            const p = l.mapFromItem(root, x, y)
            if (p.x < 0 || p.y < 0 || p.x > l.width || p.y > l.height)
                continue
            root.dropTarget = id
            const fx = p.x / l.width, fy = p.y / l.height
            const edge = Math.min(fx, 1 - fx, fy, 1 - fy)
            if (edge > 0.25)
                root.dropSide = "center"
            else if (edge === fx)
                root.dropSide = "left"
            else if (edge === 1 - fx)
                root.dropSide = "right"
            else if (edge === fy)
                root.dropSide = "top"
            else
                root.dropSide = "bottom"
            return
        }
    }
    function drop() {
        const from = root.dragging, to = root.dropTarget, side = root.dropSide
        root.dragging = ""
        root.dropTarget = ""
        root.dropSide = ""
        if (!from || !to || from === to)
            return
        root.layoutEdited(side === "center" ? root.swapped(root.tree, from, to) : root.docked(root.tree, from, to, side))
    }

    // The tree a handle drag just reported is already on screen: rebuilding it would flash the
    // panels for nothing. Any other tree (another workspace, a reset, a panel moved) is built.
    property string captured: ""
    onTreeChanged: {
        if (root.built && root.captured.length > 0 && JSON.stringify(root.tree) === root.captured)
            return
        Qt.callLater(root.build)
    }
    onPanelsChanged: Qt.callLater(root.build)
}
