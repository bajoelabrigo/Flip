import QtQuick
import QtCore

// The workspaces (0.26), as After Effects has them: the ones that come with Flip, the user's own,
// and the changes made to any of them (sizes dragged, panels moved or hidden), remembered until
// «Reset». Trees as WorkspaceView reads them. "landscape" and "portrait" keep the ids the two
// workspaces before 0.26 had, so a saved choice still means the same.
QtObject {
    id: root

    readonly property var presets: [
        { "id": "landscape", "label": qsTr("Standard"),
          "tree": { "d": "v", "c": [{ "d": "h", "f": 0.5, "c": [{ "p": "assets", "f": 0.25 }, { "p": "preview" },
                                                                  { "p": "properties", "f": 0.28 }] },
                                     { "p": "timeline" }] } },
        { "id": "portrait", "label": qsTr("Vertical"),
          "tree": { "d": "h", "c": [{ "d": "v", "c": [{ "d": "h", "f": 0.5, "c": [{ "p": "assets", "f": 0.5 }, { "p": "properties" }] },
                                                       { "p": "timeline" }] },
                                     { "p": "preview", "f": 0.38 }] } },
        { "id": "animation", "label": qsTr("Animation"),
          "tree": { "d": "v", "c": [{ "d": "h", "f": 0.42, "c": [{ "p": "assets", "f": 0.2 }, { "p": "preview" },
                                                                   { "p": "properties", "f": 0.3 }] },
                                     { "p": "timeline" }] } },
        { "id": "effects", "label": qsTr("Effects"),
          "tree": { "d": "h", "c": [{ "d": "v", "c": [{ "d": "h", "f": 0.56, "c": [{ "p": "assets", "f": 0.32 }, { "p": "preview" }] },
                                                       { "p": "timeline" }] },
                                     { "p": "properties", "f": 0.3 }] } },
        { "id": "graphics", "label": qsTr("Graphics and text"),
          "tree": { "d": "h", "c": [{ "p": "assets", "f": 0.22 },
                                     { "d": "v", "c": [{ "p": "preview", "f": 0.6 }, { "p": "timeline" }] },
                                     { "p": "properties", "f": 0.3 }] } },
        { "id": "color", "label": qsTr("Color"),
          "tree": { "d": "h", "c": [{ "d": "v", "c": [{ "p": "preview", "f": 0.64 }, { "p": "timeline" }] },
                                     { "p": "properties", "f": 0.34 }] } },
        { "id": "audio", "label": qsTr("Audio"),
          "tree": { "d": "v", "c": [{ "d": "h", "f": 0.38, "c": [{ "p": "assets", "f": 0.32 }, { "p": "preview" },
                                                                   { "p": "properties", "f": 0.26 }] },
                                     { "p": "timeline" }] } },
        { "id": "libraries", "label": qsTr("Libraries"),
          "tree": { "d": "h", "c": [{ "p": "assets", "f": 0.4 },
                                     { "d": "v", "c": [{ "d": "h", "f": 0.56, "c": [{ "p": "preview" }, { "p": "properties", "f": 0.42 }] },
                                                       { "p": "timeline" }] }] } },
        { "id": "small", "label": qsTr("Small screen"),
          "tree": { "d": "v", "c": [{ "d": "h", "f": 0.56, "c": [{ "p": "preview" }, { "p": "properties", "f": 0.4 }] },
                                     { "p": "timeline" }] } },
        { "id": "review", "label": qsTr("Review"),
          "tree": { "d": "v", "c": [{ "p": "preview" }, { "p": "timeline", "f": 0.26 }] } }
    ]

    property Settings store: Settings {
        category: "workspaces"
        property string user: "[]"
        property string edited: "{}"
    }
    function parse(text, fallback) {
        try {
            return JSON.parse(text) || fallback
        } catch (e) {
            return fallback
        }
    }
    readonly property var userWorkspaces: parse(store.user, [])
    readonly property var editedTrees: parse(store.edited, {})
    readonly property var all: presets.concat(userWorkspaces)

    function find(id) {
        return root.all.find(w => w.id === id) || null
    }
    function label(id) {
        const w = root.find(id)
        return w ? w.label : id
    }
    // The tree shown for a workspace: as the user left it, else as it comes.
    function treeFor(id) {
        const t = root.editedTrees[id]
        if (t)
            return t
        const w = root.find(id) || root.presets[0]
        return w.tree
    }
    function isEdited(id) {
        return !!root.editedTrees[id]
    }
    function edit(id, tree) {
        const e = root.parse(store.edited, {})
        e[id] = tree
        store.edited = JSON.stringify(e)
    }
    function reset(id) {
        const e = root.parse(store.edited, {})
        delete e[id]
        store.edited = JSON.stringify(e)
    }
    function isUser(id) {
        return id.indexOf("user:") === 0
    }
    // A new workspace of the user's from a tree; returns its id.
    function saveAs(label, tree) {
        const list = root.parse(store.user, [])
        let n = 1
        while (list.some(w => w.id === "user:" + n))
            ++n
        const id = "user:" + n
        list.push({ "id": id, "label": label, "tree": tree })
        store.user = JSON.stringify(list)
        return id
    }
    function remove(id) {
        if (!root.isUser(id))
            return
        store.user = JSON.stringify(root.parse(store.user, []).filter(w => w.id !== id))
        root.reset(id)
    }
}
