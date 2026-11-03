import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// The picked keys, shared by the curve editor above the tracks (KeyframeGraph) and the rows a
// track unfolds into (TrackKeyframeRows): a key picked in one is picked in the other, and the
// menu, the Curves popup and After Effects' keys (F9 Suave, Shift+F9 Suave al llegar,
// Ctrl+Shift+F9 Suave al salir, Ctrl+Alt+H Salto, Ctrl+Alt+K Recto) are the same in both.
// Keys of several tracks can be picked at once (0.30, as After Effects picks keys of several
// layers): Ctrl or Shift on another track's key, or a box across them; a plain pick starts over.
Item {
    id: root

    width: 0
    height: 0

    // The track picked on last, and the keys themselves, each {track, clip, prop, seconds}.
    property int track: -1
    property var keys: []
    // A box dragged over the rows of one track reaches the others' (0.30): `box` in scene
    // coordinates while it lasts, `boxBase` what was picked before it (Shift or Ctrl), and each
    // track's rows hand in the keys under it.
    property var box: null
    property var boxBase: []
    property var boxParts: ({})
    function boxPart(trackIndex, list) {
        const parts = Object.assign({}, root.boxParts)
        parts[trackIndex] = list.map((k) => ({ track: trackIndex, clip: k.clip, prop: k.prop, seconds: k.seconds }))
        root.boxParts = parts
        let out = root.boxBase.slice()
        for (const t in parts) {
            for (const k of parts[t]) {
                if (!out.some((o) => o.track === k.track && root.sameKey(o, k)))
                    out.push(k)
            }
        }
        root.keys = out
        if (list.length > 0)
            root.track = trackIndex
    }
    function beginBox(additive) {
        root.boxBase = additive ? root.keys.slice() : []
        root.boxParts = ({})
    }
    function endBox() {
        root.box = null
        root.boxParts = ({})
        root.selectPickedClips()
    }

    function keyTrack(k) {
        return k.track !== undefined ? k.track : root.track
    }
    function pickedOn(trackIndex) {
        return root.keys.filter((k) => root.keyTrack(k) === trackIndex)
    }
    function pickedTracks() {
        const out = []
        for (const k of root.keys) {
            const t = root.keyTrack(k)
            if (out.indexOf(t) < 0)
                out.push(t)
        }
        return out
    }
    // `fn(track, keys)` for each track with picked keys, as one undo step when there are several.
    function eachTrack(label, fn) {
        const tracks = root.pickedTracks()
        if (tracks.length === 1) {
            fn(tracks[0], root.pickedOn(tracks[0]))
            return
        }
        if (tracks.length === 0)
            return
        EditorState.beginEditSession(label)
        try {
            for (const t of tracks)
                fn(t, root.pickedOn(t))
        } finally {
            EditorState.endEditSession(true)
        }
    }
    // The clips with picked keys become the selected ones, so the inspector and Delete act on
    // them (the pick follows the selection: see onSelectionChanged).
    function selectPickedClips() {
        const out = []
        for (const k of root.keys) {
            const t = root.keyTrack(k)
            if (!out.some((p) => p.track === t && p.clip === k.clip))
                out.push({ "track": t, "clip": k.clip })
        }
        if (out.length === 0)
            return
        const sel = EditorState.selection || []
        const same = sel.length === out.length
                     && out.every((p) => sel.some((q) => q.track === p.track && q.clip === p.clip))
        if (!same)
            EditorState.setSelection(out)
    }
    // A run with Shift starts here: {clip, prop, seconds}.
    property var runFrom: null
    readonly property bool hasPick: track >= 0 && keys.length > 0
    // The property whose curve the graph shapes, set from a line's name in a track (0.25).
    property string focusProp: ""
    // The prop of the key the menu was opened on (0.26: Keyframe velocity).
    property string menuProp: ""

    // The pick, for the Motion Tools panel (0.26), which works on these keys.
    function publishPick() {
        EditorState.pickedKeyframes = ({ track: root.track, keys: root.keys })
    }
    onKeysChanged: publishPick()
    onTrackChanged: publishPick()

    // The key the menu was opened on: how it arrives and leaves, and whether it holds.
    property var menuHalves: ({ "in": "linear", "out": "linear" })
    property bool menuHold: false
    property bool menuFromGraph: false
    property int menuClip: -1
    property real menuSeconds: 0

    function sameKey(a, b) {
        return a.clip === b.clip && a.prop === b.prop && Math.abs(a.seconds - b.seconds) < 1e-4
    }

    function isPicked(trackIndex, key) {
        for (let i = 0; i < root.keys.length; ++i) {
            if (root.keyTrack(root.keys[i]) === trackIndex && sameKey(root.keys[i], key))
                return true
        }
        return false
    }

    // The keys picked now; ones given without a track are on `trackIndex`.
    function pick(trackIndex, list) {
        root.track = trackIndex
        root.keys = list.map((k) => ({ track: k.track !== undefined ? k.track : trackIndex,
                                      clip: k.clip, prop: k.prop, seconds: k.seconds }))
    }

    function clear() {
        root.keys = []
        root.runFrom = null
    }

    // A press on a key, as After Effects picks: plain picks it (unless it already is one of the
    // picked, so a drag moves them all), Ctrl adds or takes it away, Shift picks the run on that
    // property between the last key picked and this one. `siblings` are the keys of its property
    // on that clip, for the run.
    // `ref` is one key, or every axis key of a joined diamond (Scale's width and height, Position's
    // X and Y): Ctrl and Shift take them all, or a copy carried only the first (bounce exercise #18).
    function press(trackIndex, ref, modifiers, siblings) {
        const refs = Array.isArray(ref) ? ref : [ref]
        const first = refs[0]
        const ctrl = modifiers & Qt.ControlModifier
        const shift = modifiers & Qt.ShiftModifier
        const here = (k) => root.keyTrack(k) === trackIndex
        if (ctrl) {
            // Added to (or taken from) what is picked, on any track.
            pick(trackIndex, isPicked(trackIndex, first)
                 ? root.keys.filter((k) => !(here(k) && refs.some((r) => sameKey(k, r))))
                 : root.keys.concat(refs.filter((r) => !root.keys.some((k) => here(k) && sameKey(k, r)))
                                        .map((r) => ({ track: trackIndex, clip: r.clip, prop: r.prop, seconds: r.seconds }))))
            root.selectPickedClips()
        } else if (shift && root.runFrom && root.keyTrack(root.runFrom) === trackIndex
                   && root.runFrom.clip === first.clip && root.runFrom.prop === first.prop) {
            const lo = Math.min(root.runFrom.seconds, first.seconds) - 1e-4
            const hi = Math.max(root.runFrom.seconds, first.seconds) + 1e-4
            // The run joins the keys picked on the other tracks.
            const out = root.keys.filter((k) => !here(k))
            for (const k of (siblings || [])) {
                if (k.seconds < lo || k.seconds > hi)
                    continue
                if (k.refs && k.refs.length > 0) {
                    for (const r of k.refs)
                        out.push({ track: trackIndex, clip: first.clip, prop: r.prop, seconds: r.seconds })
                } else {
                    out.push({ track: trackIndex, clip: first.clip, prop: first.prop, seconds: k.seconds })
                }
            }
            pick(trackIndex, out)
        } else if (shift && !isPicked(trackIndex, first)) {
            // Shift with no run to make here: added, as Ctrl adds.
            pick(trackIndex, root.keys.concat(refs.map((r) => ({ track: trackIndex, clip: r.clip, prop: r.prop,
                                                                 seconds: r.seconds }))))
            root.selectPickedClips()
        } else if (!isPicked(trackIndex, first)) {
            pick(trackIndex, refs)
        }
        if (!shift)
            root.runFrom = ({ track: trackIndex, clip: first.clip, prop: first.prop, seconds: first.seconds })
    }

    // How a key arrives and leaves, from its handles: none is straight, a flat one eased, any
    // other a shape of its own; a hold on the key before squares the way in.
    function halfOf(dx, dy) {
        if (Math.abs(dx || 0) < 1e-9 && Math.abs(dy || 0) < 1e-9)
            return "linear"
        return Math.abs(dy || 0) < 1e-6 ? "ease" : "bezier"
    }
    function keyHalves(keys, i) {
        const k = keys[i]
        const prev = i > 0 ? keys[i - 1] : null
        const next = i < keys.length - 1 ? keys[i + 1] : null
        const inHalf = prev ? (prev.hold ? "hold" : halfOf(k.inDx, k.inDy)) : null
        const outHalf = next ? (k.hold ? "hold" : halfOf(k.outDx, k.outDy)) : null
        return {
            "in": inHalf !== null ? inHalf : (outHalf !== null ? outHalf : (k.hold ? "hold" : "linear")),
            "out": outHalf !== null ? outHalf : (k.hold ? "hold" : (inHalf !== null ? inHalf : "linear"))
        }
    }

    // A drag of every picked key at once, as the web's: they all move by the same time, none past
    // a neighbour that is not picked nor out of its clip. `shifting` while it lasts; `dragDelta`
    // is how far they have gone, which the frozen rows and the graph add to the picked keys.
    property bool shifting: false
    property real dragDelta: 0
    // An Alt-drag of the first or last picked key stretches them instead (0.25): each picked key
    // sits at stretchPivot + (start − stretchPivot) × stretchFactor.
    property bool stretching: false
    property real stretchPivot: 0
    property real stretchFactor: 1
    property real stretchGrab: 0
    property real stretchLo: 0
    property real stretchHi: 1
    property var dragBase: []
    property real dragLo: 0
    property real dragHi: 0

    // Whether `key`, as it sat when the drag began, is one of those being dragged.
    function isShifted(trackIndex, key) {
        if (!(root.shifting || root.stretching))
            return false
        for (let i = 0; i < root.dragBase.length; ++i) {
            if (root.keyTrack(root.dragBase[i]) === trackIndex && sameKey(root.dragBase[i], key))
                return true
        }
        return false
    }

    // How far a picked key that started at `seconds` has gone in the drag that is on.
    function offsetFor(seconds) {
        if (root.stretching)
            return (root.stretchPivot + (seconds - root.stretchPivot) * root.stretchFactor) - seconds
        return root.shifting ? root.dragDelta : 0
    }
    // Where a key now at `seconds` started (the live series during a drag of the rows).
    function startOf(seconds) {
        if (root.stretching)
            return root.stretchPivot + (seconds - root.stretchPivot) / Math.max(1e-6, root.stretchFactor)
        return root.shifting ? seconds - root.dragDelta : seconds
    }
    // Whether an Alt-press on `ref` can stretch: several picked, and it is the first or the last.
    function canStretch(trackIndex, ref) {
        if (root.keys.length < 2 || !isPicked(trackIndex, ref))
            return false
        const times = root.keys.map((k) => k.seconds)
        const lo = Math.min.apply(null, times)
        const hi = Math.max.apply(null, times)
        return hi - lo > 1e-4 && (Math.abs(ref.seconds - lo) < 1e-4 || Math.abs(ref.seconds - hi) < 1e-4)
    }

    // The picked keys between their unpicked neighbours and inside their clip, as the bounds a
    // drag of them keeps to: [{key, before, after}].
    function pickedBounds() {
        const frame = 1 / 60
        const out = []
        for (let i = 0; i < root.keys.length; ++i) {
            const k = root.keys[i]
            const kt = root.keyTrack(k)
            const clip = EditorState.clipAt(kt, k.clip)
            const start = clip.start || 0
            const end = start + (clip.duration || 0)
            const all = (EditorState.clipKeyframes(kt, k.clip, k.prop) || [])
                        .map((p) => p.seconds).sort((a, b) => a - b)
            let before = start
            let after = end
            for (let j = 0; j < all.length; ++j) {
                const s = all[j]
                if (isPicked(kt, { clip: k.clip, prop: k.prop, seconds: s }))
                    continue
                if (s < k.seconds - 1e-4)
                    before = Math.max(before, s + frame)
                else if (s > k.seconds + 1e-4)
                    after = Math.min(after, s - frame)
            }
            out.push({ key: k, before: before, after: after })
        }
        return out
    }

    // `grabbed` is the first or last picked key; the other end stays put.
    function beginStretch(grabbed) {
        const times = root.keys.map((k) => k.seconds)
        const lo = Math.min.apply(null, times)
        const hi = Math.max.apply(null, times)
        root.stretchGrab = grabbed.seconds
        root.stretchPivot = Math.abs(grabbed.seconds - lo) < 1e-4 ? hi : lo
        // The factor keeps every key in its room, and the keys a frame apart at the least.
        const span = Math.abs(root.stretchGrab - root.stretchPivot)
        let fLo = (1 / 60) * (root.keys.length - 1) / Math.max(1e-6, span)
        let fHi = Infinity
        for (const b of pickedBounds()) {
            const d = b.key.seconds - root.stretchPivot
            if (Math.abs(d) < 1e-6)
                continue
            const a = (b.before - root.stretchPivot) / d
            const c = (b.after - root.stretchPivot) / d
            fHi = Math.min(fHi, Math.max(a, c))
            fLo = Math.max(fLo, Math.min(a, c))
        }
        root.stretchLo = Math.min(1, fLo)
        root.stretchHi = Math.max(1, fHi)
        root.stretchFactor = 1
        root.dragBase = root.keys.slice()
        root.stretching = true
        EditorState.beginPreviewDrag(qsTr("Stretch keyframes"))
    }

    // The grabbed key wants to go to `seconds`; returns where it lands.
    function stretchTo(seconds) {
        const span = root.stretchGrab - root.stretchPivot
        let f = (seconds - root.stretchPivot) / span
        f = Math.max(root.stretchLo, Math.min(root.stretchHi, f))
        if (Math.abs(f - root.stretchFactor) > 1e-6) {
            for (const t of root.baseTracks())
                EditorState.previewStretchKeyframes(t, root.dragBase.filter((k) => root.keyTrack(k) === t),
                                                    root.stretchPivot, root.stretchFactor, f)
            root.stretchFactor = f
        }
        return root.stretchPivot + span * root.stretchFactor
    }

    function endStretch() {
        if (!root.stretching)
            return
        EditorState.commitPreviewDrag()
        const f = root.stretchFactor
        const p = root.stretchPivot
        root.keys = root.dragBase.map((k) => ({ track: root.keyTrack(k), clip: k.clip, prop: k.prop,
                                                seconds: p + (k.seconds - p) * f }))
        root.runFrom = null
        root.stretching = false
        root.stretchFactor = 1
        root.dragBase = []
    }

    function beginShift() {
        const frame = 1 / 60
        let lo = -Infinity
        let hi = Infinity
        for (let i = 0; i < root.keys.length; ++i) {
            const k = root.keys[i]
            const kt = root.keyTrack(k)
            const clip = EditorState.clipAt(kt, k.clip)
            const start = clip.start || 0
            const end = start + (clip.duration || 0)
            const all = (EditorState.clipKeyframes(kt, k.clip, k.prop) || [])
                        .map((p) => p.seconds).sort((a, b) => a - b)
            let before = start
            let after = end
            for (let j = 0; j < all.length; ++j) {
                const s = all[j]
                if (isPicked(kt, { clip: k.clip, prop: k.prop, seconds: s }))
                    continue
                if (s < k.seconds - 1e-4)
                    before = Math.max(before, s + frame)
                else if (s > k.seconds + 1e-4)
                    after = Math.min(after, s - frame)
            }
            lo = Math.max(lo, before - k.seconds)
            hi = Math.min(hi, after - k.seconds)
        }
        root.dragLo = Math.min(0, lo)
        root.dragHi = Math.max(0, hi)
        root.dragBase = root.keys.slice()
        root.dragDelta = 0
        root.shifting = true
        EditorState.beginPreviewDrag(qsTr("Move keyframes"))
    }

    // `delta` is the time the key under the pointer wants to move; the rest follow it.
    function shiftTo(delta) {
        const d = Math.max(root.dragLo, Math.min(root.dragHi, delta))
        if (Math.abs(d - root.dragDelta) < 1e-6)
            return root.dragDelta
        for (const t of root.baseTracks())
            EditorState.previewShiftKeyframes(t, root.dragBase.filter((k) => root.keyTrack(k) === t), root.dragDelta, d)
        root.dragDelta = d
        return d
    }
    function baseTracks() {
        const out = []
        for (const k of root.dragBase) {
            const t = root.keyTrack(k)
            if (out.indexOf(t) < 0)
                out.push(t)
        }
        return out
    }

    function endShift() {
        if (!root.shifting)
            return
        EditorState.commitPreviewDrag()
        const d = root.dragDelta
        root.keys = root.dragBase.map((k) => ({ track: root.keyTrack(k), clip: k.clip, prop: k.prop,
                                                seconds: k.seconds + d }))
        root.runFrom = null
        root.shifting = false
        root.dragDelta = 0
        root.dragBase = []
    }

    function applyEasing(mode) {
        if (root.hasPick)
            root.eachTrack(qsTr("Keyframe easing changed"), (t, ks) => EditorState.setKeyframesEasing(t, ks, mode))
    }

    // Ctrl+C on picked keys copies them (not the clip); Ctrl+V pastes them on the selected clip
    // at the playhead while keys were the last thing copied.
    property bool keysCopiedLast: false
    function copyPicked() {
        if (!root.hasPick)
            return false
        // The clipboard holds one layer's keys: those of the track picked on last.
        root.keysCopiedLast = EditorState.copyKeyframes(root.track, root.pickedOn(root.track)) > 0
        return root.keysCopiedLast
    }
    function pasteCopied() {
        if (!root.keysCopiedLast || !EditorState.hasCopiedKeyframes()
                || EditorState.selectedTrack < 0 || EditorState.selectedClip < 0)
            return false
        // With several layers picked, each gets the keys (0.30, as After Effects pastes into every
        // selected layer's same property), in one undo step.
        const picked = EditorState.selection || []
        const several = picked.length > 1
        if (several) {
            EditorState.beginEditSession(qsTr("Paste keyframes"))
            let any = false
            try {
                for (const p of picked)
                    any = EditorState.pasteKeyframes(p.track, p.clip) || any
            } finally {
                EditorState.endEditSession(any)
            }
            return any
        }
        if (!EditorState.pasteKeyframes(EditorState.selectedTrack, EditorState.selectedClip))
            return false
        // The pasted keys are the picked ones now (0.30, as After Effects): the next nudge, ease or
        // copy works on them, not on the keys they were copied from.
        const pasted = EditorState.lastPastedKeyframes()
        if (pasted.length > 0)
            root.pick(EditorState.selectedTrack, pasted)
        return true
    }

    // Ctrl+A while keys are picked: every key of the clip they are on (the selected one), on all
    // its lines, as After Effects picks all the keys of a layer.
    function pickAllOfClip() {
        if (!root.hasPick)
            return false
        const track = root.track
        const clip = EditorState.selectedTrack === track && EditorState.selectedClip >= 0
                     ? EditorState.selectedClip : root.keys[0].clip
        const out = []
        for (const prop of (EditorState.clipAnimatedProperties(track, clip) || [])) {
            for (const k of (EditorState.clipKeyframes(track, clip, prop) || []))
                out.push({ clip: clip, prop: prop, seconds: k.seconds })
        }
        if (out.length > 0)
            pick(track, out)
        return true
    }

    function removePicked() {
        if (!root.hasPick)
            return false
        root.eachTrack(qsTr("Remove keyframes"), (t, ks) => EditorState.removeKeyframes(t, ks))
        clear()
        return true
    }

    // The menu for the key `ref` on `trackIndex`, opened at the pointer. `at` is the point in
    // `item` the Curves popup opens from.
    function openMenu(trackIndex, ref, halves, hold, fromGraph, item, at) {
        if (!isPicked(trackIndex, ref))
            pick(trackIndex, [ref])
        root.menuHalves = halves
        root.menuHold = hold
        root.menuFromGraph = fromGraph
        root.menuClip = ref.clip
        root.menuProp = ref.prop
        root.menuSeconds = ref.seconds
        const p = item.mapToItem(curvesPopup.parent, at.x, at.y)
        curvesPopup.x = p.x
        curvesPopup.y = p.y
        keyMenu.popup()
    }

    // A key picked on a clip that is no longer the selected one would be deleted by Delete while
    // the clip is what the user means: the pick follows the selection.
    Connections {
        target: EditorState
        function onSelectionChanged() {
            if (!root.hasPick)
                return
            const sel = EditorState.selection || []
            const kept = root.keys.filter((k) => sel.some((p) => p.track === root.keyTrack(k) && p.clip === k.clip))
            if (kept.length === 0)
                root.clear()
            else if (kept.length !== root.keys.length)
                root.keys = kept
        }
    }

    Shortcut {
        sequence: "F9"
        enabled: root.hasPick
        onActivated: root.applyEasing("ease")
    }
    Shortcut {
        sequence: "Shift+F9"
        enabled: root.hasPick
        onActivated: root.applyEasing("easeIn")
    }
    Shortcut {
        sequence: "Ctrl+Shift+F9"
        enabled: root.hasPick
        onActivated: root.applyEasing("easeOut")
    }
    Shortcut {
        sequence: "Ctrl+Alt+H"
        enabled: root.hasPick
        onActivated: root.applyEasing("hold")
    }
    Shortcut {
        sequence: "Ctrl+Alt+K"
        enabled: root.hasPick
        onActivated: root.applyEasing("linear")
    }

    KeyframeVelocityDialog {
        id: velocityDialog
    }

    // Time Stretch of the picked keys by percent, from the first one (0.26).
    ThemedDialog {
        id: stretchDialog
        title: qsTr("Stretch keyframes")
        acceptText: qsTr("Apply")
        preferredWidth: Theme.dialogWidthSm
        onAccepted: {
            stretchField.parseAndCommit()
            root.eachTrack(qsTr("Stretch keyframes"), (t, ks) => EditorState.stretchKeyframes(t, ks, stretchField.value))
        }
        contentItem: Column {
            width: stretchDialog.preferredWidth
            spacing: Theme.spacingMd
            ThemedLabel {
                width: parent.width
                wrapMode: Text.WordWrap
                size: "sm"
                opacity: 0.85
                text: qsTr("50% packs the picked keys into half the time, 200% spreads them over twice. The first one stays where it is. Alt + dragging the first or last key does the same by hand.")
            }
            ThemedNumberField {
                id: stretchField
                width: parent.width
                from: 1
                to: 1000
                value: 100
                unit: "%"
            }
        }
    }

    KeyframeCurvesPopup {
        id: curvesPopup
        onCurvePicked: (x1, y1, x2, y2, hold) => {
            if (hold)
                root.applyEasing("hold")
            else if (root.hasPick)
                root.eachTrack(qsTr("Keyframe easing changed"),
                               (t, ks) => EditorState.setKeyframesCurve(t, ks, x1, y1, x2, y2))
        }
    }

    ThemedContextMenu {
        id: keyMenu

        readonly property bool one: root.keys.length <= 1
        function check(inHalf, outHalf) {
            return keyMenu.one && root.menuHalves["in"] === inHalf
                   && root.menuHalves["out"] === outHalf ? Theme.icons.check : ""
        }

        ThemedMenuItem {
            text: qsTr("Straight")
            shortcutText: "Ctrl+Alt+K"
            icon.name: keyMenu.check("linear", "linear")
            onTriggered: root.applyEasing("linear")
        }
        ThemedMenuItem {
            text: qsTr("Smooth")
            shortcutText: "F9"
            icon.name: keyMenu.check("ease", "ease")
            onTriggered: root.applyEasing("ease")
        }
        ThemedMenuItem {
            text: qsTr("Smooth in")
            shortcutText: "Shift+F9"
            icon.name: keyMenu.check("ease", "linear")
            onTriggered: root.applyEasing("easeIn")
        }
        ThemedMenuItem {
            text: qsTr("Smooth out")
            shortcutText: "Ctrl+Shift+F9"
            icon.name: keyMenu.check("linear", "ease")
            onTriggered: root.applyEasing("easeOut")
        }
        ThemedMenuItem {
            text: qsTr("Hold")
            shortcutText: "Ctrl+Alt+H"
            icon.name: keyMenu.one && root.menuHold ? Theme.icons.check : ""
            onTriggered: root.applyEasing("hold")
        }
        ThemedMenuItem {
            text: qsTr("Curves…")
            icon.name: Theme.icons.penCurve
            onTriggered: curvesPopup.open()
        }
        ThemedMenuSeparator {}
        ThemedMenuItem {
            // The curve editor is where this menu was opened from when it came from the graph.
            visible: !root.menuFromGraph
            height: visible ? implicitHeight : 0
            text: qsTr("Edit curve…")
            icon.name: Theme.icons.penCurve
            onTriggered: {
                EditorState.selectClip(root.track, root.menuClip)
                EditorState.playheadSeconds = root.menuSeconds
                // The curve of the key's own property (0.30: a Position Y key opened Position X's).
                root.focusProp = ""
                root.focusProp = root.menuProp
                EditorState.preferences.curveEditorVisible = true
            }
        }
        // After Effects' spatial interpolation and roving keys (0.30), for Position.
        ThemedMenuSeparator {
            visible: root.menuProp === "x" || root.menuProp === "y"
        }
        ThemedMenuItem {
            visible: root.menuProp === "x" || root.menuProp === "y"
            height: visible ? implicitHeight : 0
            text: qsTr("Curved path (auto Bezier)")
            onTriggered: EditorState.setPositionPath(root.track, root.menuClip, "auto",
                                                     root.pickedOn(root.track).filter((k) => k.prop === "x" || k.prop === "y").map((k) => k.seconds))
        }
        ThemedMenuItem {
            visible: root.menuProp === "x" || root.menuProp === "y"
            height: visible ? implicitHeight : 0
            text: qsTr("Straight path")
            onTriggered: EditorState.setPositionPath(root.track, root.menuClip, "linear",
                                                     root.pickedOn(root.track).filter((k) => k.prop === "x" || k.prop === "y").map((k) => k.seconds))
        }
        ThemedMenuItem {
            visible: root.menuProp === "x" || root.menuProp === "y"
            height: visible ? implicitHeight : 0
            text: qsTr("Roving (one speed along the path)")
            onTriggered: EditorState.roveKeyframes(root.track, root.menuClip)
        }
        ThemedMenuItem {
            // After Effects' Separate Dimensions: X and Y with their own curves, or one Position
            // whose path and speed are shaped apart.
            readonly property bool joined: {
                void EditorState.tracksRevision
                return EditorState.positionJoined(root.track, root.menuClip)
            }
            visible: root.menuProp === "x" || root.menuProp === "y"
            height: visible ? implicitHeight : 0
            text: joined ? qsTr("Separate dimensions (X and Y apart)") : qsTr("Join Position (one path)")
            onTriggered: EditorState.setPositionJoined(root.track, root.menuClip, !joined)
        }
        ThemedMenuItem {
            // After Effects' Time-Reverse Keyframes (0.26).
            text: qsTr("Reverse keyframes")
            visible: root.keys.length > 1
            height: visible ? implicitHeight : 0
            onTriggered: root.eachTrack(qsTr("Reverse keyframes"), (t, ks) => EditorState.reverseKeyframes(t, ks))
        }
        ThemedMenuItem {
            // Also Alt + dragging the first or last picked key, as in After Effects.
            text: qsTr("Stretch keyframes…")
            visible: root.keys.length > 1
            height: visible ? implicitHeight : 0
            onTriggered: stretchDialog.open()
        }
        ThemedMenuItem {
            // After Effects' Keyframe Velocity (Ctrl+Shift+K there), for the key the menu is on.
            text: qsTr("Keyframe velocity…")
            onTriggered: velocityDialog.openFor(root.track, root.menuClip, root.menuProp, root.menuSeconds,
                                                root.pickedOn(root.track))
        }
        ThemedMenuItem {
            text: keyMenu.one ? qsTr("Delete keyframe") : qsTr("Delete keyframes")
            icon.name: Theme.icons.trash
            onTriggered: root.removePicked()
        }
    }
}
