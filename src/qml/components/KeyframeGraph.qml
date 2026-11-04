import QtQuick
import QtQuick.Controls.Basic
import Drift
import "timeline"

// Keyframe strip aligned with the timeline: left gutter matches track labels,
// graph scroll + playhead share the timeline's contentX / pxPerSecond.
//
// Every animated property of the selected clip earns a chip here — the strip is a view of the
// clip, not of the inspector's selection. A chip toggles whether that curve is drawn: it is a
// display filter and nothing more, so a hidden curve keeps animating and keeps its chip. Switching
// an animation *off* is the inspector row's job, not this strip's.
Item {
    id: root

    // One side of the transform box (0.30), below.
    component BoxSide: MouseArea {
        property string side: "left"
        property Item box: null
        property point origin
        property real startSpan: 1
        preventStealing: true
        hoverEnabled: true
        cursorShape: side === "left" || side === "right" ? Qt.SizeHorCursor : Qt.SizeVerCursor
        onPressed: (mouse) => {
            origin = mapToItem(null, mouse.x, mouse.y)
            startSpan = side === "left" || side === "right"
                ? Math.max(1, box.width - 16) : Math.max(1, box.height - 16)
            box.begin()
        }
        onPositionChanged: (mouse) => {
            if (!pressed)
                return
            const p = mapToItem(null, mouse.x, mouse.y)
            const d = side === "right" ? p.x - origin.x : side === "left" ? origin.x - p.x
                    : side === "top" ? origin.y - p.y : p.y - origin.y
            box.apply(side, Math.max(0.02, (startSpan + d) / startSpan))
        }
        onReleased: EditorState.commitPreviewDrag()
        onCanceled: EditorState.commitPreviewDrag()
    }

    property real pxPerSecond: 50
    property real contentX: 0
    // The canvases below cover the viewport plus a chunk either side, parked on a chunk boundary,
    // so scrolling (and playback's auto-scroll) only repaints them when a boundary is crossed
    // rather than on every frame.
    readonly property real paintChunk: 256
    readonly property real paintOriginX: Math.floor(contentX / paintChunk) * paintChunk - paintChunk
    property real contentWidth: 800
    property real labelsWidth: Theme.trackLabelsWidth
    // Inside a track's keyframe lines (0.25, After Effects' Graph Editor): no gutter of its own,
    // the track's lines on the left name the properties; its buttons float over the graph.
    readonly property bool inline: labelsWidth <= 0
    // Whether the open properties tab edits keyframeable properties (PropertiesPanel `keyframes`).
    property bool keyframesTab: false
    // The picked keys, the key menu and the Curves popup, shared with the tracks' keyframe rows
    // (KeyframeKeyTools): a key picked here is picked there, and the other way round. Null where
    // the timeline has no rows (the phone's).
    property var tools: null

    // The clip whose curves are open (0.24). It follows the selection to a clip with animation, and
    // stays when the selection goes (a click on the timeline to move the playhead) or moves to a
    // clip without any: the editor is open until it is closed, as Jorge asked.
    property string pinnedClipId: ""
    function followSelection() {
        if (EditorState.selectedTrack < 0 || EditorState.selectedClip < 0)
            return
        const data = EditorState.clipAt(EditorState.selectedTrack, EditorState.selectedClip)
        if (!data || !data.id)
            return
        const animated = EditorState.clipAnimatedProperties(EditorState.selectedTrack, EditorState.selectedClip)
        if (animated.length > 0 || root.trackIndex < 0)
            root.pinnedClipId = data.id
    }
    Connections {
        target: EditorState
        function onSelectionChanged() { root.followSelection() }
        function onSelectedClipDataChanged() { root.followSelection() }
    }
    Component.onCompleted: {
        root.followSelection()
        // Opened by a key's «Edit curve…», the graph starts on that key's property.
        if (root.tools && root.tools.focusProp && root.tools.focusProp.length > 0)
            root.focusedProp = root.tools.focusProp
    }

    readonly property var pinnedAt: {
        void EditorState.tracksRevision
        return root.pinnedClipId.length > 0 ? EditorState.clipLocation(root.pinnedClipId) : ({ "track": -1, "clip": -1 })
    }
    readonly property int trackIndex: pinnedAt.track
    readonly property int clipIndex: pinnedAt.clip
    readonly property bool hasClip: trackIndex >= 0 && clipIndex >= 0
    readonly property var clip: {
        void EditorState.selectedClipData
        void EditorState.tracksRevision
        return hasClip ? EditorState.clipAt(trackIndex, clipIndex) : ({})
    }

    // Effect parameters are addressed as "fx.<effectIndex>.<paramKey>", and audio effect ones as
    // "afx.<effectIndex>.<paramKey>"; the label, range and color all come from the effect's own
    // param spec on the selected clip.
    function effectParam(id) {
        if (!clip)
            return null
        const audio = id.substring(0, 4) === "afx."
        if (!audio && id.substring(0, 3) !== "fx.")
            return null
        const stack = audio ? clip.audioEffects : clip.effects
        const start = audio ? 4 : 3
        if (!stack)
            return null
        const dot = id.indexOf(".", start)
        if (dot < 0)
            return null
        const effectIndex = parseInt(id.substring(start, dot))
        const key = id.substring(dot + 1)
        if (isNaN(effectIndex) || effectIndex < 0 || effectIndex >= stack.length)
            return null
        const effect = stack[effectIndex]
        const params = effect.params || []
        for (let i = 0; i < params.length; ++i) {
            if (params[i].key === key)
                return { effect: effect, param: params[i] }
        }
        return null
    }

    // Spelled-out names for the one-to-three character property chips.
    function propertyLabel(id) {
        switch (id) {
        case "x": return qsTr("X position")
        case "y": return qsTr("Y position")
        case "width": return qsTr("Width")
        case "height": return qsTr("Height")
        case "rotation": return qsTr("Rotation")
        case "rotationX": return qsTr("Tilt X")
        case "rotationY": return qsTr("Tilt Y")
        case "z": return qsTr("Depth")
        case "perspective": return qsTr("Perspective")
        case "opacity": return qsTr("Opacity")
        case "volume": return qsTr("Volume")
        case "pan": return qsTranslate("TrackKeyframeRows", "Pan")
        case "mask.x": return qsTr("Mask X")
        case "mask.y": return qsTr("Mask Y")
        case "mask.w": return qsTr("Mask width")
        case "mask.h": return qsTr("Mask height")
        case "mask.rotation": return qsTr("Mask rotation")
        case "mask.feather": return qsTr("Mask feather")
        }
        // Text and shape properties are named by the engine ("Shadow · Blur"): the layer stack
        // is per clip, so no static table could spell them.
        if (id.substring(0, 5) === "text." || id.substring(0, 6) === "shape.") {
            const label = EditorState.keyframePropertyLabel(
                            root.trackIndex, root.clipIndex, id)
            if (label.length > 0)
                return label
        }
        const fx = effectParam(id)
        if (fx)
            return fx.effect.label + " · " + fx.param.label
        return id
    }
    // Joined Position's speed curve picks and eases X's keys: they hold its timing, and Y follows.
    function refProp(prop) {
        return prop === "position" ? "x" : prop
    }
    function chipLabel(id) {
        switch (id) {
        case "x": return "X"
        case "y": return "Y"
        case "position": return qsTr("Pos")
        case "width": return "W"
        case "height": return "H"
        case "rotation": return "°"
        case "rotationX": return "X°"
        case "rotationY": return "Y°"
        case "z": return "Z"
        case "perspective": return "Per"
        case "opacity": return "Op"
        case "volume": return "Vol"
        case "pan": return "Pan"
        case "mask.x": return "MX"
        case "mask.y": return "MY"
        case "mask.w": return "MW"
        case "mask.h": return "MH"
        case "mask.rotation": return "M°"
        case "mask.feather": return "MFe"
        }
        const fx = effectParam(id)
        if (fx)
            return fx.param.label.substring(0, 3)
        // A text or shape key (a layer's, or some letters' own, 0.25) by the name the engine gives
        // it, never the raw key ("text.run.r42….rotation").
        if (id.substring(0, 5) === "text." || id.substring(0, 6) === "shape.")
            return root.propertyLabel(id)
        return id
    }
    // Volume and audio effects only exist on clips that carry audio; the rest are visual.
    function supportsProperty(id) {
        if (!clip)
            return false
        if (id === "volume")
            return clip.kind === "audio" || clip.kind === "video"
        if (id.substring(0, 3) === "fx.")
            return clip.kind !== "audio" && effectParam(id) !== null
        if (id.substring(0, 4) === "afx.")
            return effectParam(id) !== null
        // A mask lives on the clip's lane, so the strip offers it for the same clips the Masks
        // tab does. There is no per-id validation to do: the id set is fixed and closed.
        if (id.substring(0, 5) === "mask.")
            return clip.kind !== "audio"
        return clip.kind !== "audio"
    }

    // Each series is normalized against its own value range, so curves in wildly
    // different units (px vs. 0–1 opacity) stay comparable when overlaid.
    function valueRangeFor(id, pts, base) {
        if (id === "opacity")
            return { min: 0, max: 1 }
        if (id === "volume")
            return { min: 0, max: 2 }
        // Rotation fits its keys like the rest (0.25): a turn to 320° or 720° stays in the graph;
        // a small swing still gets a readable span.
        const turn = id === "rotation" || id === "mask.rotation"
        // Mask geometry is normalized to the clip frame, so a fixed 0..1 axis is meaningful and
        // keeps the four curves comparable. Feather is in px and auto-fits like anything else.
        if (id === "mask.x" || id === "mask.y" || id === "mask.w" || id === "mask.h")
            return { min: 0, max: 1 }
        const fx = effectParam(id)
        if (fx)
            return { min: fx.param.min, max: fx.param.max }
        let lo = Infinity
        let hi = -Infinity
        for (let i = 0; i < pts.length; ++i) {
            const v = Number(pts[i].value)
            lo = Math.min(lo, v)
            hi = Math.max(hi, v)
            // The handles too: a curve bends out to them, and must not leave the graph.
            for (const d of [Number(pts[i].inDy) || 0, Number(pts[i].outDy) || 0]) {
                lo = Math.min(lo, v + d)
                hi = Math.max(hi, v + d)
            }
        }
        // With no keys there is nothing to fit, so centre the axis on the value the property
        // actually holds — otherwise a 1920px width would be drawn far off the top of a 0..100 lane.
        if (!isFinite(lo))
            lo = base
        if (!isFinite(hi))
            hi = base
        if (turn && hi - lo < 90) {
            const mid = (hi + lo) / 2
            lo = mid - 45
            hi = mid + 45
        }
        const pad = Math.max(1, (hi - lo) * 0.08)
        return { min: lo - pad, max: hi + pad }
    }

    // A preview move emits tracksChanged, which would re-evaluate `series` and
    // make the Repeater destroy the delegate owning the active DragHandler —
    // killing the grab on the first mouse move. Freeze the model while dragging
    // and track the in-flight key separately.
    property bool draggingKey: false
    // The time the picked keys have moved in a drag of several (KeyframeKeyTools.shifting): the
    // frozen series draws them there.
    readonly property real shiftDelta: tools && tools.shifting ? tools.dragDelta : 0
    // How far a key that started at `seconds` has gone (a stretch moves each by its own).
    function shiftOf(seconds) {
        if (!root.tools)
            return 0
        void root.tools.dragDelta
        void root.tools.stretchFactor
        return root.tools.offsetFor(seconds)
    }
    function shifted(prop, seconds) {
        return !!tools && (tools.shifting || tools.stretching)
               && tools.isShifted(root.trackIndex,
                                  { clip: root.clipIndex, prop: root.refProp(prop), seconds: seconds })
    }
    property var frozenSeries: []
    // After Effects' Graph Editor (0.30). The graph type: "value", "speed" or "auto" (AE's auto-select:
    // the speed graph for a Position with its dimensions joined, the value graph for the rest).
    property string graphType: "value"
    // After Effects' Speed Graph (0.25): the focused curve's speed instead of its values.
    readonly property bool speedGraph: graphType === "speed"
        || (graphType === "auto" && EditorState.positionLinked && (focusedProp === "x" || focusedProp === "y"))
    // The part of each curve's range on show, as fractions of it (0..1 is all of it): Ctrl+wheel zooms
    // it, the wheel moves it, «Fit» and «Zoom to selection» set it. Speed has its own axis.
    property real viewLo: 0
    property real viewHi: 1
    // Over all the tracks instead of under its own (AE's Graph Editor in place of the layer bars).
    property bool fullView: false
    signal fullViewToggleRequested()
    // Time is the timeline's: these ask it to zoom (around a time) or to scroll, or to fit a range.
    signal timeZoomRequested(real factor, real anchorSeconds)
    signal timeScrollRequested(real pixels)
    signal timeFitRequested(real startSeconds, real endSeconds)
    // Only the curve being shaped, or the others faint behind it too (AE's Show Selected Properties).
    property bool othersShown: true
    function setView(lo, hi) {
        const span = Math.max(0.0005, hi - lo)
        root.viewLo = lo
        root.viewHi = lo + span
    }
    // The curves in view, as After Effects' «Fit all graphs»: their values, and in time the stretch
    // from the first key to the last (with a little air), not the whole clip (0.30: keys in the first
    // second of a 17 s clip stayed squeezed at its left, test #21).
    function fitView() {
        root.setView(0, 1)
        let t0 = Infinity, t1 = -Infinity
        for (const entry of root.series) {
            for (const p of entry.points) {
                t0 = Math.min(t0, p.seconds)
                t1 = Math.max(t1, p.seconds)
            }
        }
        if (!(t1 > t0)) {
            root.timeFitRequested(root.clipStart, root.clipStart + root.clipDuration)
            return
        }
        const air = (t1 - t0) * 0.08
        root.timeFitRequested(Math.max(root.clipStart, t0 - air), Math.min(root.clipStart + root.clipDuration, t1 + air))
    }
    // The picked keys of the focused curve, their values and handles in view, and their times.
    function zoomToPicked() {
        if (!root.tools || root.focusedIndex < 0 || root.focusedIndex >= root.series.length)
            return
        const entry = root.series[root.focusedIndex]
        const span = Math.max(1e-6, entry.valueMax - entry.valueMin)
        let lo = Infinity, hi = -Infinity, t0 = Infinity, t1 = -Infinity
        for (const p of entry.points) {
            if (!root.tools.isPicked(root.trackIndex, { clip: root.clipIndex, prop: root.refProp(entry.prop), seconds: p.seconds }))
                continue
            for (const v of [p.value, p.value + (p.inDy || 0), p.value + (p.outDy || 0)]) {
                lo = Math.min(lo, (v - entry.valueMin) / span)
                hi = Math.max(hi, (v - entry.valueMin) / span)
            }
            t0 = Math.min(t0, p.seconds)
            t1 = Math.max(t1, p.seconds)
        }
        if (!isFinite(lo))
            return
        const pad = Math.max(0.02, (hi - lo) * 0.12)
        root.setView(lo - pad, hi + pad)
        if (t1 > t0)
            root.timeFitRequested(t0 - (t1 - t0) * 0.1, t1 + (t1 - t0) * 0.1)
    }
    // Its fastest moment, in the property's units per second (the axis top while on).
    property real speedPeak: 0

    // The axis numbers down the graph's left edge (0.25, After Effects): the focused curve's
    // values, or its speed in Speed Graph. [{y, label}]
    readonly property var axisTicks: {
        void root.laneHeight
        void root.speedPeak
        const h = graph.height
        if (h <= 0 || root.focusedIndex < 0 || root.focusedIndex >= root.series.length)
            return []
        const fmt = (v) => Math.abs(v) >= 100 ? String(Math.round(v))
                          : Math.abs(v) >= 10 ? v.toFixed(1) : v.toFixed(2)
        const focused = root.series[root.focusedIndex]
        // Scale reads in % of the layer's own size, as its line does and as After Effects (0.30 tests
        // E48: the axis said 371…595, the width in pixels).
        const percent = root.percentOf(focused.prop)
        const unit = percent > 0 ? " %" : ""
        const scaled = (v) => percent > 0 ? v / percent * 100 : v
        if (root.speedGraph) {
            const top = root.speedPeak
            if (!(top > 0))
                return []
            return [0, 0.5, 1].map((f) => ({ "y": h - 4 - f * (h - 8), "label": fmt(scaled(top * f)) + unit + "/s" }))
        }
        const entry = focused
        void root.viewLo
        void root.viewHi
        const lo = root.valueForY(h, entry)
        const hi = root.valueForY(0, entry)
        const out = []
        const n = h >= 140 ? 4 : 2
        const shown = root.displayOffset(entry.prop)
        for (let i = 0; i <= n; ++i) {
            const v = lo + (hi - lo) * i / n
            out.push({ "y": root.yForValue(v, entry), "label": fmt(scaled(v + shown)) + unit })
        }
        return out
    }
    // A width or height is shown as a percentage of the layer's own size (Scale 100 %): that size,
    // or 0 for any other property.
    function percentOf(prop) {
        if ((prop !== "width" && prop !== "height") || root.trackIndex < 0 || root.clipIndex < 0)
            return 0
        void EditorState.tracksRevision
        const nat = EditorState.clipNaturalSize(root.trackIndex, root.clipIndex) || {}
        const side = prop === "width" ? nat.w : nat.h
        return side > 0 ? side : 0
    }
    // Position reads where the anchor point is (0.30), as the track's lines show it: the stored
    // value is the box's corner, so the axis adds the anchor's place in the layer (bounce #20).
    function displayOffset(prop) {
        if ((prop !== "x" && prop !== "y") || root.trackIndex < 0 || root.clipIndex < 0)
            return 0
        void EditorState.tracksRevision
        const horizontal = prop === "x"
        const sizeProp = horizontal ? "width" : "height"
        const anchorProp = horizontal ? "anchorX" : "anchorY"
        const t = EditorState.playheadSeconds
        const value = (p) => EditorState.propertyValueAt(root.trackIndex, root.clipIndex, p, t,
                                                         EditorState.propertyBaseValue(root.trackIndex, root.clipIndex, p, 0))
        const animated = EditorState.clipAnimatedProperties(root.trackIndex, root.clipIndex).indexOf(sizeProp) >= 0
        const keys = animated ? (EditorState.clipKeyframes(root.trackIndex, root.clipIndex, sizeProp) || []) : []
        // The size a keyed size grows from, as the renderer and the track's lines (0.30 tests E40).
        const pivot = keys.length > 0 ? (horizontal ? root.clip.sizePivotW : root.clip.sizePivotH) : 0
        const side = pivot > 0 ? pivot : keys.length >= 2 ? keys[0].value : value(sizeProp)
        const f = value(anchorProp)
        return (isNaN(f) ? 0.5 : f) * (isNaN(side) ? 0 : side)
    }
    // A drag of several picked keys also moves their values (0.25, After Effects): the pointer's
    // height in pixels, which each curve reads in its own range. Shift keeps the values.
    property real groupDy: 0
    property var groupValueBase: []
    function groupValue(value, entry) {
        if (Math.abs(root.groupDy) < 1e-6)
            return value
        return Math.max(entry.valueMin, Math.min(entry.valueMax,
                        root.valueForY(root.yForValue(value, entry) + root.groupDy, entry)))
    }
    // The box a drag on empty graph space draws: picks every key dot inside it.
    property bool marqueeActive: false
    property real marqueeX0: 0
    property real marqueeY0: 0
    property real marqueeX1: 0
    property real marqueeY1: 0
    property var marqueeBase: []
    function marqueeApply() {
        if (!root.tools)
            return
        const left = Math.min(root.marqueeX0, root.marqueeX1) - 6
        const right = Math.max(root.marqueeX0, root.marqueeX1) + 6
        const top = Math.min(root.marqueeY0, root.marqueeY1) - 6
        const bottom = Math.max(root.marqueeY0, root.marqueeY1) + 6
        const out = root.marqueeBase.slice()
        // Only the curve being shaped, as After Effects' Graph Editor (Jorge, 0.30): a box over
        // Position's keys also took Scale's, faint as they are.
        const onlyIndex = root.focusedIndex >= 0 && root.focusedIndex < root.series.length ? root.focusedIndex : -1
        for (const h of root.keyHandles) {
            if (onlyIndex >= 0 && h.seriesIndex !== onlyIndex)
                continue
            const entry = root.series[h.seriesIndex]
            const x = root.xForSeconds(h.seconds)
            const y = root.speedGraph
                ? root.speedY(root.keySideSpeed(entry, h.seconds, h.pointIndex < entry.points.length - 1))
                : root.yForValue(h.value, entry)
            if (x < left || x > right || y < top || y > bottom)
                continue
            const ref = { clip: root.clipIndex, prop: root.refProp(h.prop), seconds: h.seconds }
            if (!out.some((k) => root.tools.keyTrack(k) === root.trackIndex && root.tools.sameKey(k, ref)))
                out.push(ref)
        }
        // And the other layers' (0.30), each on its own track.
        if (onlyIndex < 0 || root.othersShown) {
            for (const o of root.otherKeyHandles) {
                const x = root.xForSeconds(o.seconds)
                const y = root.yForValue(o.value, o.entry)
                if (x < left || x > right || y < top || y > bottom)
                    continue
                const ref = { track: o.track, clip: o.clip, prop: o.prop, seconds: o.seconds }
                if (!out.some((k) => root.tools.keyTrack(k) === o.track && root.tools.sameKey(k, ref)))
                    out.push(ref)
            }
        }
        root.tools.pick(root.trackIndex, out)
    }
    property string dragProp: ""
    property int dragIndex: -1
    property real dragSeconds: 0
    property real dragValue: 0

    // The in-flight tangent, for the same reason: the canvas paints from the frozen series,
    // so without this the curve would not reshape until the handle was released.
    property int dragTangentIndex: -1
    property real dragTangentInDx: 0
    property real dragTangentInDy: 0
    property real dragTangentOutDx: 0
    property real dragTangentOutDy: 0

    // One entry per animated property of the clip — the chip row's model, hidden curves included.
    // [{ prop, label, color, points, enabled, shown, valueMin, valueMax }, ...]
    readonly property var allSeries: {
        void root.clip
        void EditorState.tracksRevision
        void EditorState.keyframeGraphHiddenProperties
        if (!hasClip)
            return []
        const out = []
        const animated = EditorState.clipAnimatedProperties(
                           root.trackIndex, root.clipIndex)
        const hidden = EditorState.keyframeGraphHiddenProperties
        // After Effects' Position as one property (0.30): in the Speed Graph it is one curve, the
        // speed along the path (X's and Y's own speeds say nothing there).
        const joined = root.speedGraph && EditorState.positionJoined(root.trackIndex, root.clipIndex)
        // Only the properties whose lines are on show (0.30 tests E42, as After Effects' Graph Editor
        // shows the properties in view): after S or Alt+Shift+S the graph kept drawing Position.
        const rows = root.inline ? (EditorState.trackKeyframeRows(root.trackIndex) || []) : []
        const onShow = {}
        let filtered = false
        for (const r of rows) {
            if (!r || !r.group)
                continue
            filtered = true
            for (const p of (r.groupProps && r.groupProps.length > 0 ? r.groupProps : [r.prop]))
                onShow[p] = true
        }
        let pathShown = false
        for (let i = 0; i < animated.length; ++i) {
            let id = animated[i]
            if (filtered && !onShow[id])
                continue
            if (joined && (id === "x" || id === "y")) {
                if (pathShown)
                    continue
                pathShown = true
                id = "position"
            } else if (!supportsProperty(id))
                continue
            const pts = EditorState.clipKeyframes(
                          root.trackIndex, root.clipIndex, id) || []
            // What the curve reads as when the property has no keys at all — the level of the
            // flat line drawn across the clip in that case.
            const base = EditorState.propertyBaseValue(
                           root.trackIndex, root.clipIndex, id, 0)
            const range = root.valueRangeFor(id, pts, base)
            // A behaviour (Bounce, Elastic, loop, wiggle, an expression) changes what plays: its
            // result is drawn over the keys' curve, as After Effects' post-expression graph (0.30
            // tests #19), and the range takes it in.
            let result = []
            if (id !== "position") {
                const b = EditorState.propertyBehavior(root.trackIndex, root.clipIndex, id)
                if (b && b.active === true) {
                    const t0 = root.clipStart
                    const steps = 160
                    const dt = root.clipDuration / steps
                    for (let k = 0; k <= steps; ++k) {
                        const v = EditorState.propertyValueAt(root.trackIndex, root.clipIndex, id, t0 + dt * k, base)
                        if (!isFinite(v))
                            continue
                        result.push({ seconds: t0 + dt * k, value: v })
                        range.min = Math.min(range.min, v)
                        range.max = Math.max(range.max, v)
                    }
                }
            }
            out.push({
                prop: id,
                label: root.chipLabel(id),
                color: Theme.keyframeCurveColor(id),
                points: pts,
                result: result,
                baseValue: base,
                enabled: EditorState.clipPropertyKeyframesEnabled(
                             root.trackIndex, root.clipIndex, id),
                shown: hidden.indexOf(id) < 0,
                valueMin: range.min,
                valueMax: range.max
            })
        }
        return out
    }

    // After Effects' Graph Editor shows every selected layer's curves at once (0.26): the other
    // selected clips' curves are drawn faded and dashed as a reference, in their own value range,
    // and a click on a layer's name makes it the one being edited.
    property bool showOtherLayers: true
    // The other layers' keys, to pick and move (0.30, as After Effects edits every selected
    // layer's curves at once): each {track, clip, id, prop, seconds, value, entry, points}.
    // Held as they were while such a drag lasts: rebuilt, the handle being dragged would go.
    property var frozenOtherKeys: []
    readonly property var otherKeyHandles: {
        const out = []
        if (!root.tools || root.speedGraph)
            return out
        if (root.frozenOtherKeys.length > 0)
            return root.frozenOtherKeys
        for (const layer of root.otherLayers) {
            const at = EditorState.clipLocation(layer.id)
            if (at.track < 0)
                continue
            for (const entry of layer.curves) {
                for (const p of entry.points)
                    out.push({ track: at.track, clip: at.clip, id: layer.id, prop: entry.prop, seconds: p.seconds,
                               value: p.value, entry: entry, points: entry.points })
            }
        }
        return out
    }
    // That layer's curves become the edited ones, as After Effects: it is the last of the
    // selection, so its track's lines and this graph follow it; the rest stay picked.
    function editLayer(id) {
        const at = EditorState.clipLocation(id)
        if (at.track < 0)
            return
        const picked = (EditorState.selection || []).filter(p => p.track !== at.track || p.clip !== at.clip)
        picked.push({ "track": at.track, "clip": at.clip })
        root.pinnedClipId = id
        EditorState.setSelection(picked)
        EditorState.setTrackKeyframesExpanded(at.track, true)
    }
    readonly property var otherLayers: {
        void EditorState.selectionRevision
        void EditorState.tracksRevision
        const out = []
        if (!hasClip || !showOtherLayers)
            return out
        const picked = EditorState.selection || []
        for (let k = 0; k < picked.length; ++k) {
            const t = picked[k].track
            const c = picked[k].clip
            if (t === root.trackIndex && c === root.clipIndex)
                continue
            const data = EditorState.clipAt(t, c)
            if (!data || !data.id)
                continue
            const animated = EditorState.clipAnimatedProperties(t, c) || []
            const curves = []
            for (let i = 0; i < animated.length; ++i) {
                const id = animated[i]
                const pts = EditorState.clipKeyframes(t, c, id) || []
                if (pts.length < 2)
                    continue
                const base = EditorState.propertyBaseValue(t, c, id, 0)
                const range = root.valueRangeFor(id, pts, base)
                curves.push({ prop: id, color: Theme.keyframeCurveColor(id), points: pts,
                              valueMin: range.min, valueMax: range.max })
            }
            if (curves.length > 0)
                out.push({ id: data.id, name: data.name || qsTr("Layer"), start: data.start || 0,
                           duration: data.duration || 0, curves: curves })
        }
        return out
    }

    // The curves actually drawn: everything the chips have left visible.
    readonly property var series: {
        if (draggingKey)
            return frozenSeries
        const out = []
        for (let i = 0; i < allSeries.length; ++i) {
            if (allSeries[i].shown)
                out.push(allSeries[i])
        }
        return out
    }

    // Flattened key dots so a single Repeater can own every series' handles.
    readonly property var keyHandles: {
        const out = []
        // Only the focused curve's keys are there to see and grab (0.30), as in After Effects' Graph
        // Editor: the other properties' diamonds took the clicks meant for a handle (bounce #13) and
        // a box over Position's keys picked Scale's too (Jorge). The row's name or the chips switch.
        const onlyFocused = focusedIndex >= 0 && focusedIndex < series.length
        for (let s = 0; s < series.length; ++s) {
            if (onlyFocused && s !== focusedIndex)
                continue
            const entry = series[s]
            for (let i = 0; i < entry.points.length; ++i) {
                out.push({
                    seriesIndex: s,
                    pointIndex: i,
                    prop: entry.prop,
                    color: entry.color,
                    seconds: entry.points[i].seconds,
                    value: entry.points[i].value,
                    hold: !!entry.points[i].hold,
                    halves: root.tools ? root.tools.keyHalves(entry.points, i)
                                       : { "in": "linear", "out": "linear" }
                })
            }
        }
        return out
    }
    readonly property int keyCount: keyHandles.length

    // Tangent grips for the focused series only: two per key (in / out), minus the ones that
    // would dangle off the ends of the curve where there is no neighbouring segment.
    readonly property var tangentHandles: {
        const out = []
        if (!curveEditing || focusedIndex < 0 || focusedIndex >= series.length)
            return out
        const entry = series[focusedIndex]
        const pts = entry.points
        // Joined Position's X and Y in the Value Graph: their shape is the path's, bent on the
        // motion path in the preview; the timing is shaped in the Speed Graph (as After Effects).
        if ((entry.prop === "x" || entry.prop === "y") && pts.length > 0 && pts[0].spatial)
            return out
        for (let i = 0; i < pts.length; ++i) {
            if (pts[i].hold)
                continue // a step has no tangents to shape
            if (i > 0)
                out.push({ pointIndex: i, outgoing: false, color: entry.color, point: pts[i], neighbour: pts[i - 1] })
            if (i < pts.length - 1)
                out.push({ pointIndex: i, outgoing: true, color: entry.color, point: pts[i], neighbour: pts[i + 1] })
        }
        return out
    }

    // A handle with no length still needs to be grabbable, so an unset tangent is drawn at a
    // default reach into its segment rather than sitting exactly on the key.
    readonly property real defaultHandleSeconds: 0.12
    // An unset handle reaches a third of its segment (After Effects' 33 % influence), or the fixed
    // default when the neighbour is unknown. A fixed reach let the two handles of a short segment sit on
    // each other, and a drag took the wrong one (bounce #21b: the fall slowed into the floor).
    function handleSeconds(point, outgoing, neighbour) {
        const raw = outgoing ? (point.outDx || 0) : (point.inDx || 0)
        if (Math.abs(raw) > 1e-6)
            return raw
        const reach = neighbour ? Math.abs(neighbour.seconds - point.seconds) / 3 : defaultHandleSeconds
        return outgoing ? reach : -reach
    }
    function handleValue(point, outgoing) {
        return point.value + (outgoing ? (point.outDy || 0) : (point.inDy || 0))
    }

    readonly property real clipStart: clip.start || 0
    readonly property real clipDuration: Math.max(0.1, clip.duration || 1)

    // Beat detection results for whatever range was last analyzed. Analysis is explicit
    // (the gutter buttons) because it renders the timeline mix — never on selection change.
    // The grid and the transients are separate layers over that one result.
    readonly property var beats: EditorState.beatAnalysis
    readonly property bool analyzed: !!beats && beats.rangeDuration > 0
    readonly property bool hasGrid: EditorState.beatGridVisible && !!beats && !!beats.beats
                                    && beats.beats.length > 0
    readonly property bool hasOnsets: EditorState.onsetsVisible && !!beats && !!beats.onsets
                                      && beats.onsets.length > 0
    readonly property real bpm: (beats && beats.bpm) ? beats.bpm : 0

    // Turning a layer on analyzes if this range has not been analyzed yet; analyzeBeats
    // no-ops when the result is already current.
    function showBeatLayer(gridLayer) {
        if (gridLayer)
            EditorState.beatGridVisible = true
        else
            EditorState.onsetsVisible = true
        EditorState.analyzeBeats(root.clipStart, root.clipDuration)
    }

    // An onset this close to a grid line is already represented by it — drawing both
    // would just thicken the same line.
    function nearAnyBeat(seconds) {
        if (!beats || !beats.beats)
            return false
        for (let i = 0; i < beats.beats.length; ++i) {
            if (Math.abs(beats.beats[i] - seconds) < 0.06)
                return true
        }
        return false
    }

    // Drag the bottom edge or wheel over the header to grow the lane.
    property real laneHeight: 88
    readonly property real minLaneHeight: 60
    readonly property real maxLaneHeight: 460
    readonly property real compactHeight: 88
    readonly property real expandedHeight: 180

    Behavior on laneHeight {
        enabled: !resizeDrag.active
        NumberAnimation { duration: 160; easing.type: Easing.OutCubic }
    }

    function toggleExpanded() {
        if (curveEditing)
            laneHeight = compactHeight
        else
            laneHeight = expandedHeight
    }

    // Open whenever the clip has an animation to show, even if every curve is currently folded
    // away — otherwise hiding the last one would take the chips with it. Its own property rather
    // than `visible`, which reads false while the item's parent is hidden: the panel decides
    // whether to show the strip from this.
    readonly property bool hasContent: keyframesTab && hasClip && !!clip && allSeries.length > 0
    height: hasContent ? laneHeight : 0
    visible: hasContent

    // Curve editing focuses one series: it gets tangent handles and owns the value axis,
    // while the others stay drawn as dimmed context. Handles from two series normalized to
    // different ranges are not comparable on screen, so only one can be live at a time.
    property string focusedProp: ""
    readonly property int focusedIndex: {
        for (let i = 0; i < series.length; ++i) {
            if (series[i].prop === focusedProp)
                return i
        }
        // X or Y focused while joined Position shows as one curve.
        for (let i = 0; i < series.length; ++i) {
            if (series[i].prop === "position" && (focusedProp === "x" || focusedProp === "y"))
                return i
        }
        return series.length > 0 ? 0 : -1
    }
    // Tangent handles need room; below this the lane is an overview and shows keys only.
    // Inside a track's lines it is as tall as they are (0.25): handles show at that size already,
    // with no need to grow the lane first.
    readonly property bool curveEditing: (inline ? height : laneHeight) >= 110
    function isFocused(index) { return index === focusedIndex }

    // Double-click on empty graph inserts a key on the focused curve. The value comes from the
    // curve itself rather than from the cursor's height, so dropping a node in never changes
    // the animation — same contract as the speed editor's addPointAt/speedAtPos.
    function addKeyAt(px) {
        if (focusedIndex < 0 || focusedIndex >= series.length)
            return
        const entry = series[focusedIndex]
        const seconds = Math.max(
            clipStart,
            Math.min(clipStart + clipDuration, EditorState.snapKeyTime(secondsForX(px))))
        const value = EditorState.propertyValueAt(
                        root.trackIndex, root.clipIndex, entry.prop,
                        seconds, entry.baseValue)
        EditorState.showKeyframeGraphProperty(entry.prop)
        EditorState.setClipKeyframe(root.trackIndex, root.clipIndex,
                                    entry.prop, seconds, value)
        focusedProp = entry.prop
    }

    // Absolute timeline X — same mapping as clips on the track.
    function xForSeconds(seconds) {
        return seconds * pxPerSecond
    }
    function secondsForX(x) {
        return x / pxPerSecond
    }
    function yForValue(v, entry) {
        const span = Math.max(1e-6, entry.valueMax - entry.valueMin)
        const t = ((v - entry.valueMin) / span - root.viewLo) / Math.max(1e-6, root.viewHi - root.viewLo)
        return graph.height - t * graph.height
    }
    function valueForY(y, entry) {
        const span = Math.max(1e-6, entry.valueMax - entry.valueMin)
        const t = (graph.height - y) / Math.max(1, graph.height)
        return entry.valueMin + (root.viewLo + t * (root.viewHi - root.viewLo)) * span
    }
    // Speed Graph (0.30, After Effects): the keys and their handles sit on the speed curve; a
    // handle's height is the speed on that side of its key, its reach the influence. The axis keeps
    // the top it had when a drag began, so it does not rescale under the pointer.
    property real frozenSpeedPeak: 0
    function speedTop() {
        return root.draggingKey && root.frozenSpeedPeak > 0 ? root.frozenSpeedPeak : root.speedPeak
    }
    function speedY(sp) {
        const top = root.speedTop()
        if (!(top > 0))
            return graph.height - 4
        return graph.height - 4 - (Math.min(sp, top) / top) * (graph.height - 8)
    }
    function speedForY(y) {
        return Math.max(0, (graph.height - 4 - y) / Math.max(1, graph.height - 8) * root.speedTop())
    }
    // How fast a property changes just after (or just before) a key, in its units per second.
    function keySideSpeed(entry, seconds, outgoing) {
        void EditorState.tracksRevision
        const h = 1 / 240
        const base = entry.baseValue !== undefined ? entry.baseValue : 0
        const a = outgoing ? seconds : seconds - h
        const v0 = EditorState.propertyValueAt(root.trackIndex, root.clipIndex, entry.prop, a, base)
        const v1 = EditorState.propertyValueAt(root.trackIndex, root.clipIndex, entry.prop, a + h, base)
        return Math.abs(v1 - v0) / h
    }

    Rectangle {
        anchors.fill: parent
        color: Theme.panelBackground
        border.width: 1
        border.color: Theme.panelBorder
    }

    Row {
        anchors.fill: parent

        // Left gutter — same width as track labels so the graph lines up.
        Item {
            id: leftGutter
            width: root.labelsWidth
            height: parent.height
            visible: !root.inline

            // DAW-style lane zoom: wheel over this header grows/shrinks the keyframe lane
            MouseArea {
                anchors.fill: parent
                acceptedButtons: Qt.NoButton
                z: 30
                onWheel: (wheel) => {
                    // Modified wheel belongs to the timeline's zoom/pan.
                    if (wheel.modifiers & (Qt.ControlModifier | Qt.ShiftModifier)) {
                        wheel.accepted = false
                        return
                    }
                    const dy = wheel.angleDelta.y !== 0 ? wheel.angleDelta.y
                                                        : wheel.pixelDelta.y
                    if (dy === 0)
                        return
                    const step = 20
                    const next = root.laneHeight + (dy > 0 ? step : -step)
                    root.laneHeight = Math.max(root.minLaneHeight,
                                               Math.min(root.maxLaneHeight, next))
                }
            }

            PinchHandler {
                target: null
                acceptedDevices: PointerDevice.TouchScreen
                property real startHeight: 0
                onActiveChanged: if (active) startHeight = root.laneHeight
                onActiveScaleChanged: {
                    if (active)
                        root.laneHeight = Math.max(root.minLaneHeight,
                                                   Math.min(root.maxLaneHeight, startHeight * activeScale))
                }
            }

            TapHandler {
                onDoubleTapped: root.toggleExpanded()
            }

            Column {
                id: gutterColumn
                anchors.fill: parent
                anchors.margins: 6
                spacing: 4

                Row {
                    id: graphButtons
                    // Inline, the buttons float over the graph's top right.
                    parent: root.inline ? floatButtons : gutterColumn
                    width: root.inline ? implicitWidth : parent.width
                    x: root.inline ? 4 : 0
                    y: root.inline ? 3 : 0
                    spacing: 4

                    IconButton {
                        visible: !root.inline
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: Theme.icons.x
                        variant: "text"
                        buttonSize: 20
                        iconSize: 12
                        tooltip: qsTranslate("FindReplaceDialog", "Close")
                        onClicked: EditorState.preferences.curveEditorVisible = false
                    }

                    Text {
                        visible: !root.inline
                        anchors.verticalCenter: parent.verticalCenter
                        text: qsTr("Keyframes")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                        font.weight: Font.Medium
                    }

                    IconButton {
                        visible: !root.inline
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: root.curveEditing ? Theme.icons.minimize : Theme.icons.maximize
                        variant: "text"
                        buttonSize: 20
                        iconSize: 14
                        tooltip: root.curveEditing
                                 ? qsTr("Collapse curve editor to compact view (88px)")
                                 : qsTr("Expand curve editor to view and edit Bezier handles (180px)")
                        onClicked: root.toggleExpanded()
                    }

                    // The other selected layers' curves (0.26), on or off.
                    IconButton {
                        anchors.verticalCenter: parent.verticalCenter
                        visible: EditorState.selectionCount > 1
                        glyph: Theme.icons.layers
                        variant: "text"
                        buttonSize: 20
                        iconSize: 14
                        active: root.showOtherLayers
                        tooltip: root.showOtherLayers ? qsTr("Hide the other selected layers' curves")
                                                      : qsTr("Show the other selected layers' curves")
                        onClicked: root.showOtherLayers = !root.showOtherLayers
                    }
                    // After Effects' Speed graph (0.25): how fast the focused curve changes, drawn
                    // over its values, so an ease that is too abrupt shows as a spike.
                    IconButton {
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: Theme.icons.gauge
                        variant: "text"
                        buttonSize: 20
                        iconSize: 14
                        active: root.graphType !== "value"
                        tooltip: root.graphType === "value" ? qsTr("Graph type: value. Click: speed graph")
                               : root.graphType === "speed" ? qsTr("Graph type: speed. Click: automatic")
                               : qsTr("Graph type: automatic (speed for a joined Position, value for the rest). Click: value graph")
                        onClicked: root.graphType = root.graphType === "value" ? "speed"
                                                  : root.graphType === "speed" ? "auto" : "value"
                    }
                    // After Effects' Fit All and Zoom to Selection (0.30).
                    IconButton {
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: "square-dashed"
                        variant: "text"
                        buttonSize: 20
                        iconSize: 13
                        tooltip: qsTr("Fit the whole curve in view (Ctrl+wheel zooms the values, Alt+wheel the time)")
                        onClicked: root.fitView()
                    }
                    IconButton {
                        anchors.verticalCenter: parent.verticalCenter
                        visible: !!root.tools && root.tools.keys.length > 0
                        glyph: "zoom-in"
                        variant: "text"
                        buttonSize: 20
                        iconSize: 13
                        tooltip: qsTr("Zoom to the picked keyframes")
                        onClicked: root.zoomToPicked()
                    }
                    IconButton {
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: Theme.icons.layers
                        variant: "text"
                        buttonSize: 20
                        iconSize: 13
                        active: !root.othersShown
                        tooltip: root.othersShown ? qsTr("Show only the curve being edited")
                                                  : qsTr("Show the other properties' curves too")
                        onClicked: root.othersShown = !root.othersShown
                    }
                    IconButton {
                        anchors.verticalCenter: parent.verticalCenter
                        visible: root.inline
                        glyph: root.fullView ? Theme.icons.minimize : "panel-top"
                        variant: "text"
                        buttonSize: 20
                        iconSize: 13
                        active: root.fullView
                        tooltip: root.fullView ? qsTr("Graph under its layer again")
                                               : qsTr("Graph over the whole timeline, as After Effects' Graph Editor")
                        onClicked: root.fullViewToggleRequested()
                    }
                    // Separate dimensions: X and Y of Position keyed apart, or together.
                    IconButton {
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: EditorState.positionLinked ? Theme.icons.link : Theme.icons.unlink
                        variant: "text"
                        buttonSize: 20
                        iconSize: 14
                        active: !EditorState.positionLinked
                        tooltip: EditorState.positionLinked
                                 ? qsTr("Separate dimensions: key X and Y of Position apart")
                                 : qsTr("Join dimensions: key X and Y of Position together")
                        onClicked: EditorState.positionLinked = !EditorState.positionLinked
                    }

                    // Beat grid / tempo.
                    IconButton {
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: Theme.icons.music
                        variant: "text"
                        buttonSize: 20
                        iconSize: 14
                        active: EditorState.beatGridVisible
                        enabled: !EditorState.beatAnalysisRunning
                        tooltip: EditorState.beatAnalysisRunning
                                 ? qsTr("Analyzing…")
                                 : (EditorState.beatGridVisible ? qsTr("Hide the beat markers")
                                                                : qsTr("Find the beat and show markers"))
                        onClicked: {
                            if (EditorState.beatGridVisible)
                                EditorState.beatGridVisible = false
                            else
                                root.showBeatLayer(true)
                        }
                    }

                    // Individual transients.
                    IconButton {
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: Theme.icons.audioLines
                        variant: "text"
                        buttonSize: 20
                        iconSize: 14
                        active: EditorState.onsetsVisible
                        enabled: !EditorState.beatAnalysisRunning
                        tooltip: EditorState.beatAnalysisRunning
                                 ? qsTr("Analyzing…")
                                 : (EditorState.onsetsVisible ? qsTr("Hide hits")
                                                              : qsTr("Find beats and hits in the audio under this clip"))
                        onClicked: {
                            if (EditorState.onsetsVisible)
                                EditorState.onsetsVisible = false
                            else
                                root.showBeatLayer(false)
                        }
                    }
                }

                // One chip per animated property of the clip, tinted to its curve. Clicking folds
                // that curve away or brings it back; the chip itself always stays put.
                Flow {
                    width: parent.width
                    spacing: 3
                    Repeater {
                        model: root.allSeries
                        delegate: ThemedChip {
                            required property var modelData
                            text: modelData.label
                            chipHeight: 18
                            horizontalPadding: 3
                            accentColor: modelData.color
                            // A property whose keyframes are switched off in the inspector still
                            // has a curve to look at; it just is not driving anything.
                            opacity: modelData.enabled ? 1.0 : 0.5
                            tooltip: {
                                const name = root.propertyLabel(modelData.prop)
                                const state = modelData.enabled ? name
                                                                : qsTr("%1 (keyframes off)").arg(name)
                                return modelData.shown ? qsTr("%1 — click to hide this curve").arg(state)
                                                       : qsTr("%1 — click to show this curve").arg(state)
                            }
                            selected: modelData.shown
                            onClicked: {
                                EditorState.toggleKeyframeGraphPropertyVisible(modelData.prop)
                                // Showing a curve also makes it the one the tangent handles belong
                                // to, so the chip you just clicked is the curve you can shape.
                                if (!modelData.shown)
                                    root.focusedProp = modelData.prop
                                else if (root.focusedProp === modelData.prop)
                                    root.focusedProp = ""
                            }
                        }
                    }
                }

                Text {
                    width: parent.width
                    wrapMode: Text.WordWrap
                    text: {
                        const keys = root.keyCount === 0 ? qsTr("No keyframes")
                                                         : qsTr("%n keyframes", "", root.keyCount)
                        let hint = ""
                        if (!root.curveEditing && root.keyCount > 0)
                            hint = " · " + qsTr("Expand for handles")
                        if (!EditorState.beatGridVisible || !root.analyzed)
                            return keys + hint
                        // The detector publishes no bpm when the tempo estimate was not
                        // confident — say so, rather than leaving the grid button lit over
                        // an empty lane. Onsets may still be perfectly usable.
                        return (root.bpm > 0 ? keys + " · " + Math.round(root.bpm) + qsTr(" BPM")
                                             : keys + qsTr(" · no beat found")) + hint
                    }
                    color: (!root.curveEditing && root.keyCount > 0) ? Theme.primary : Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs

                    MouseArea {
                        anchors.fill: parent
                        enabled: !root.curveEditing && root.keyCount > 0
                        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
                        onClicked: root.toggleExpanded()
                    }
                }
            }

            Rectangle {
                anchors.right: parent.right
                width: 1
                height: parent.height
                color: Theme.panelBorder
            }
        }

        // Timeline-aligned viewport (scrolls with the tracks below).
        Item {
            id: viewport
            width: parent.width - root.labelsWidth
            height: parent.height
            clip: true

            // The axis numbers, fixed at the left edge while the graph scrolls under them.
            Repeater {
                model: root.axisTicks
                delegate: Item {
                    required property var modelData
                    z: 30
                    x: 0
                    y: 6 + modelData.y
                    width: viewport.width
                    Rectangle {
                        width: parent.width
                        height: 1
                        color: Theme.panelBorder
                        opacity: 0.35
                    }
                    Text {
                        x: 4
                        // The top number goes under its line so it is not cut off.
                        y: parent.modelData.y < height + 2 ? 1 : -height - 1
                        text: parent.modelData.label
                        color: Theme.mutedForeground
                        font.family: Theme.monoFontFamily
                        font.pixelSize: Theme.fontSizeTiny
                    }
                }
            }

            Item {
                id: content
                x: -root.contentX
                width: Math.max(viewport.width + root.contentX, root.contentWidth)
                height: parent.height

                Item {
                    id: graph
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.topMargin: 6
                    anchors.bottomMargin: 6

                    // The wheel in the graph (0.30, After Effects' Graph Editor): Ctrl zooms the values
                    // around the pointer, Alt zooms time around it, Shift scrolls time; the plain wheel
                    // moves the values when the graph has the whole timeline, and scrolls it otherwise.
                    WheelHandler {
                        id: graphWheel
                        target: null
                        // Any modifier (the handler sorts them out below): a set of flags here means all
                        // of them pressed at once, so plain, Ctrl and Alt wheels never reached it (#16).
                        acceptedModifiers: Qt.KeyboardModifierMask
                        onWheel: (event) => {
                            const d = event.angleDelta.y !== 0 ? event.angleDelta.y : event.angleDelta.x
                            if (d === 0)
                                return
                            const steps = d / 120
                            const mods = event.modifiers
                            if (mods & Qt.ControlModifier) {
                                const f = 1 - (graph.height - graphWheel.point.position.y) / Math.max(1, graph.height)
                                const at = root.viewLo + (1 - f) * (root.viewHi - root.viewLo)
                                const k = Math.pow(0.85, steps)
                                root.setView(at - (at - root.viewLo) * k, at + (root.viewHi - at) * k)
                            } else if (mods & Qt.AltModifier) {
                                root.timeZoomRequested(Math.pow(1.2, steps), root.secondsForX(graphWheel.point.position.x))
                            } else if (mods & Qt.ShiftModifier) {
                                root.timeScrollRequested(-steps * 80)
                            } else if (root.fullView) {
                                const move = (root.viewHi - root.viewLo) * 0.1 * steps
                                root.setView(root.viewLo + move, root.viewHi + move)
                            } else {
                                event.accepted = false
                                return
                            }
                            event.accepted = true
                        }
                    }

                    // Selected clip's time span — sits under the same region as the clip.
                    Rectangle {
                        x: root.xForSeconds(root.clipStart)
                        width: Math.max(2, root.clipDuration * root.pxPerSecond)
                        height: parent.height
                        color: Theme.panelAccent
                        opacity: 0.55
                        radius: 2
                    }

                    Rectangle {
                        anchors.verticalCenter: parent.verticalCenter
                        x: root.xForSeconds(root.clipStart)
                        width: Math.max(2, root.clipDuration * root.pxPerSecond)
                        height: 1
                        color: Theme.panelBorder
                    }

                    // Playhead — same absolute X as the timeline playhead.
                    Rectangle {
                        x: root.xForSeconds(EditorState.playheadSeconds) - Theme.playheadLineWidth / 2
                        width: Theme.playheadLineWidth
                        height: parent.height
                        color: Theme.primary
                        z: 3
                    }

                    // Detected beat grid + onset ticks, under the curves and key dots.
                    Canvas {
                        id: beatCanvas
                        // Viewport-sized, not content-sized — see curveCanvas.
                        x: root.paintOriginX
                        width: viewport.width + 2 * root.paintChunk
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        z: 0
                        visible: root.hasGrid || root.hasOnsets

                        onPaint: {
                            const ctx = getContext("2d")
                            ctx.clearRect(0, 0, width, height)
                            const a = root.beats
                            if (!a)
                                return
                            // Canvas-local x for an absolute timeline position. Rounding happens
                            // after the shift, so a fractional scroll offset cannot push a 1px
                            // tick onto a half-pixel and smear it across two columns.
                            const localX = t => Math.round(root.xForSeconds(t) - root.paintOriginX)

                            if (root.hasGrid) {
                                const perBar = a.beatsPerBar || 4
                                const first = a.firstDownbeat || 0
                                for (let i = 0; i < a.beats.length; ++i) {
                                    const isBar = ((i - first) % perBar + perBar) % perBar === 0
                                    const px = localX(a.beats[i])
                                    if (px < -2 || px > width + 2)
                                        continue
                                    ctx.fillStyle = String(isBar ? Theme.beatBarColor
                                                                 : Theme.beatGridColor)
                                    ctx.fillRect(px, 0, isBar ? 2 : 1, height)
                                }
                            }

                            if (!root.hasOnsets)
                                return

                            // With the grid up, only transients that miss it — the rest would
                            // just double-draw lines already there. Height tracks strength.
                            ctx.fillStyle = String(Theme.beatOnsetColor)
                            const onsets = a.onsets || []
                            for (let j = 0; j < onsets.length; ++j) {
                                if (root.hasGrid && root.nearAnyBeat(onsets[j].seconds))
                                    continue
                                const ox = localX(onsets[j].seconds)
                                if (ox < -2 || ox > width + 2)
                                    continue
                                // Centered rather than sitting on the floor: a 1px tick down
                                // at the bottom edge read as chart furniture next to the
                                // full-height beat lines.
                                const h = Math.max(6, onsets[j].strength * height * 0.5)
                                ctx.fillRect(ox - 1, (height - h) / 2, 2, h)
                            }
                        }

                        // The canvas is hidden until the first analysis lands, and a
                        // requestPaint issued while hidden is dropped.
                        onVisibleChanged: if (visible) requestPaint()

                        Connections {
                            target: root
                            function onBeatsChanged() { beatCanvas.requestPaint() }
                            // Toggling a layer leaves beatAnalysis itself untouched, so
                            // onBeatsChanged does not fire for it.
                            function onHasGridChanged() { beatCanvas.requestPaint() }
                            function onHasOnsetsChanged() { beatCanvas.requestPaint() }
                            function onPxPerSecondChanged() { beatCanvas.requestPaint() }
                            function onPaintOriginXChanged() { beatCanvas.requestPaint() }
                        }
                    }

                    // The other selected layers' curves (0.26), under the edited ones.
                    Canvas {
                        id: otherCanvas
                        x: root.paintOriginX
                        width: viewport.width + 2 * root.paintChunk
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        visible: root.otherLayers.length > 0
                        onPaint: {
                            const ctx = getContext("2d")
                            ctx.clearRect(0, 0, width, height)
                            ctx.save()
                            ctx.translate(-root.paintOriginX, 0)
                            ctx.lineWidth = 1
                            ctx.setLineDash([5, 3])
                            ctx.globalAlpha = 0.6
                            for (let l = 0; l < root.otherLayers.length; ++l) {
                                const layer = root.otherLayers[l]
                                for (let s = 0; s < layer.curves.length; ++s) {
                                    const entry = layer.curves[s]
                                    const pts = entry.points.slice().sort((a, b) => a.seconds - b.seconds)
                                    ctx.strokeStyle = String(entry.color)
                                    ctx.beginPath()
                                    ctx.moveTo(root.xForSeconds(layer.start), root.yForValue(pts[0].value, entry))
                                    ctx.lineTo(root.xForSeconds(pts[0].seconds), root.yForValue(pts[0].value, entry))
                                    for (let i = 1; i < pts.length; ++i) {
                                        const a = pts[i - 1]
                                        const b = pts[i]
                                        const ax = root.xForSeconds(a.seconds)
                                        const bx = root.xForSeconds(b.seconds)
                                        const ay = root.yForValue(a.value, entry)
                                        const by = root.yForValue(b.value, entry)
                                        if (a.hold) {
                                            ctx.lineTo(bx, ay)
                                            ctx.lineTo(bx, by)
                                            continue
                                        }
                                        const c1x = Math.min(bx, Math.max(ax, ax + root.xForSeconds(a.outDx || 0)))
                                        const c2x = Math.min(bx, Math.max(ax, bx + root.xForSeconds(b.inDx || 0)))
                                        ctx.bezierCurveTo(c1x, root.yForValue(a.value + (a.outDy || 0), entry),
                                                          c2x, root.yForValue(b.value + (b.inDy || 0), entry), bx, by)
                                    }
                                    const tail = pts[pts.length - 1]
                                    ctx.lineTo(root.xForSeconds(layer.start + layer.duration), root.yForValue(tail.value, entry))
                                    ctx.stroke()
                                    // Its keys as small hollow diamonds.
                                    for (let i = 0; i < pts.length; ++i) {
                                        const kx = root.xForSeconds(pts[i].seconds)
                                        const ky = root.yForValue(pts[i].value, entry)
                                        ctx.beginPath()
                                        ctx.moveTo(kx, ky - 3)
                                        ctx.lineTo(kx + 3, ky)
                                        ctx.lineTo(kx, ky + 3)
                                        ctx.lineTo(kx - 3, ky)
                                        ctx.closePath()
                                        ctx.stroke()
                                    }
                                }
                            }
                            ctx.restore()
                        }
                        Connections {
                            target: root
                            function onOtherLayersChanged() { otherCanvas.requestPaint() }
                            function onPxPerSecondChanged() { otherCanvas.requestPaint() }
                            function onPaintOriginXChanged() { otherCanvas.requestPaint() }
                        }
                        onHeightChanged: requestPaint()
                    }

                    Canvas {
                        id: curveCanvas
                        // Only as wide as the visible strip, parked at the viewport's left edge
                        // (content is offset by -contentX, so x: contentX cancels the scroll).
                        // Filling the scrollable content instead would size the backing texture
                        // to the whole timeline, and QSGPlainTexture silently rescales anything
                        // past GL_MAX_TEXTURE_SIZE to fit — 16384px, which at 40x zoom is barely
                        // 8 seconds of timeline. Past that the curves are drawn correctly and
                        // then downsampled onto the GPU, which is what smeared them.
                        x: root.paintOriginX
                        width: viewport.width + 2 * root.paintChunk
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        onPaint: {
                            const ctx = getContext("2d")
                            ctx.clearRect(0, 0, width, height)
                            // Everything below is in absolute timeline coordinates.
                            ctx.save()
                            ctx.translate(-root.paintOriginX, 0)
                            const spanX0 = root.xForSeconds(root.clipStart)
                            const spanX1 = root.xForSeconds(root.clipStart + root.clipDuration)

                            for (let s = 0; s < root.series.length; ++s) {
                                // «Only the curve being edited» (0.30) leaves the others out.
                                if (!root.othersShown && !root.isFocused(s))
                                    continue
                                const entry = root.series[s]
                                const isLinkedPartner = EditorState.positionLinked
                                    && ((root.dragProp === "x" && entry.prop === "y") || (root.dragProp === "y" && entry.prop === "x"))

                                const live = entry.points.map(function (p, i) {
                                    if (root.shifted(entry.prop, p.seconds)) {
                                        return {
                                            seconds: p.seconds + root.shiftOf(p.seconds),
                                            value: root.groupValue(p.value, entry),
                                            inDx: p.inDx, inDy: p.inDy,
                                            outDx: p.outDx, outDy: p.outDy, hold: p.hold
                                        }
                                    }
                                    if (entry.prop === root.dragProp) {
                                        if (i === root.dragTangentIndex) {
                                            // Handle being dragged: same key, reshaped.
                                            return {
                                                seconds: p.seconds, value: p.value, hold: p.hold,
                                                inDx: root.dragTangentInDx, inDy: root.dragTangentInDy,
                                                outDx: root.dragTangentOutDx, outDy: root.dragTangentOutDy
                                            }
                                        }
                                        if (i === root.dragIndex) {
                                            // Key being moved: carry its tangents through, so the
                                            // curve shape does not snap back to linear mid-drag.
                                            return {
                                                seconds: root.dragSeconds, value: root.dragValue,
                                                inDx: p.inDx, inDy: p.inDy,
                                                outDx: p.outDx, outDy: p.outDy, hold: p.hold
                                            }
                                        }
                                    } else if (isLinkedPartner) {
                                        if (root.dragTangentIndex >= 0 && root.focusedIndex >= 0 && root.focusedIndex < root.series.length) {
                                            const masterPts = root.series[root.focusedIndex].points
                                            const masterP = masterPts ? masterPts[root.dragTangentIndex] : null
                                            if (masterP && Math.abs(masterP.seconds - p.seconds) < (1 / 30)) {
                                                let partnerInDy = 0.0
                                                let partnerOutDy = 0.0
                                                if (i + 1 < entry.points.length && root.dragTangentIndex + 1 < masterPts.length) {
                                                    const mSpan = masterPts[root.dragTangentIndex + 1].value - masterP.value
                                                    const sSpan = entry.points[i + 1].value - p.value
                                                    if (Math.abs(mSpan) > 1e-6)
                                                        partnerOutDy = root.dragTangentOutDy * (sSpan / mSpan)
                                                }
                                                if (i > 0 && root.dragTangentIndex > 0) {
                                                    const mSpan = masterP.value - masterPts[root.dragTangentIndex - 1].value
                                                    const sSpan = p.value - entry.points[i - 1].value
                                                    if (Math.abs(mSpan) > 1e-6)
                                                        partnerInDy = root.dragTangentInDy * (sSpan / mSpan)
                                                }
                                                return {
                                                    seconds: p.seconds, value: p.value, hold: p.hold,
                                                    inDx: root.dragTangentInDx, inDy: partnerInDy,
                                                    outDx: root.dragTangentOutDx, outDy: partnerOutDy
                                                }
                                            }
                                        } else if (root.dragIndex >= 0 && root.focusedIndex >= 0 && root.focusedIndex < root.series.length) {
                                            const masterPts = root.series[root.focusedIndex].points
                                            const masterP = masterPts ? masterPts[root.dragIndex] : null
                                            if (masterP && Math.abs(masterP.seconds - p.seconds) < (1 / 30)) {
                                                return {
                                                    seconds: root.dragSeconds, value: p.value,
                                                    inDx: p.inDx, inDy: p.inDy,
                                                    outDx: p.outDx, outDy: p.outDy, hold: p.hold
                                                }
                                            }
                                        }
                                    }
                                    return p
                                })
                                const sorted = live.sort((a, b) => a.seconds - b.seconds)

                                // The focused series is the one being edited; the rest are
                                // context and are drawn thinner and faded. A series whose
                                // keyframes are switched off is faded further still — its curve
                                // is a record of an animation that is not currently playing.
                                const focused = root.isFocused(s)
                                // Whole pixels. A 1.8px stroke lands ~40/100/40% across three
                                // rows, which reads as a glow wherever the curve runs shallow —
                                // exactly the flat tops and troughs between keys.
                                ctx.lineWidth = focused ? 2 : 1
                                ctx.globalAlpha = root.speedGraph ? 0.18
                                                  : (root.curveEditing && !focused) ? 0.35 : 1.0
                                if (entry.enabled === false)
                                    ctx.globalAlpha *= 0.45
                                ctx.strokeStyle = String(entry.color)
                                ctx.beginPath()

                                // An unkeyed property is a flat line at the value it actually
                                // holds, so every selected property reads as an editable curve
                                // spanning the clip rather than as nothing at all.
                                if (sorted.length === 0) {
                                    const by = root.yForValue(entry.baseValue, entry)
                                    ctx.moveTo(spanX0, by)
                                    ctx.lineTo(spanX1, by)
                                    ctx.stroke()
                                    continue
                                }

                                // Outside the keyed range the value is held flat, which is what
                                // evaluateAt does — so the drawn line matches playback.
                                const leadY = root.yForValue(sorted[0].value, entry)
                                ctx.moveTo(spanX0, leadY)
                                ctx.lineTo(root.xForSeconds(sorted[0].seconds), leadY)
                                for (let i = 1; i < sorted.length; ++i) {
                                    const a = sorted[i - 1]
                                    const b = sorted[i]
                                    const ax = root.xForSeconds(a.seconds)
                                    const ay = root.yForValue(a.value, entry)
                                    const bx = root.xForSeconds(b.seconds)
                                    const by = root.yForValue(b.value, entry)

                                    if (a.hold) {
                                        // Step: hold the outgoing value, then jump.
                                        ctx.lineTo(bx, ay)
                                        ctx.lineTo(bx, by)
                                        continue
                                    }
                                    // Handles are clamped into the segment exactly as the
                                    // evaluator does, so the drawn curve matches playback.
                                    const c1x = Math.min(bx, Math.max(ax, ax + root.xForSeconds(a.outDx || 0)))
                                    const c2x = Math.min(bx, Math.max(ax, bx + root.xForSeconds(b.inDx || 0)))
                                    const c1y = root.yForValue(a.value + (a.outDy || 0), entry)
                                    const c2y = root.yForValue(b.value + (b.inDy || 0), entry)
                                    ctx.bezierCurveTo(c1x, c1y, c2x, c2y, bx, by)
                                }
                                const tail = sorted[sorted.length - 1]
                                ctx.lineTo(spanX1, root.yForValue(tail.value, entry))
                                ctx.stroke()
                                // What plays with its behaviour on top (dashed), over the keys' curve.
                                if (!root.speedGraph && entry.result && entry.result.length > 1) {
                                    ctx.save()
                                    ctx.setLineDash([5, 3])
                                    ctx.lineWidth = focused ? 2 : 1
                                    ctx.beginPath()
                                    for (let k = 0; k < entry.result.length; ++k) {
                                        const rx = root.xForSeconds(entry.result[k].seconds)
                                        const ry = root.yForValue(entry.result[k].value, entry)
                                        if (k === 0)
                                            ctx.moveTo(rx, ry)
                                        else
                                            ctx.lineTo(rx, ry)
                                    }
                                    ctx.stroke()
                                    ctx.restore()
                                }
                            }
                            ctx.globalAlpha = 1.0
                            // The focused curve's speed, sampled from what plays: |Δvalue/Δt|,
                            // scaled to the lane (its fastest moment at the top).
                            if (root.speedGraph && root.focusedIndex >= 0 && root.focusedIndex < root.series.length
                                    && root.series[root.focusedIndex].points.length > 1) {
                                const entry = root.series[root.focusedIndex]
                                const t0 = root.clipStart
                                const t1 = root.clipStart + root.clipDuration
                                const steps = Math.min(400, Math.max(40, Math.round((spanX1 - spanX0) / 3)))
                                const dt = (t1 - t0) / steps
                                const base = entry.baseValue !== undefined ? entry.baseValue : 0
                                const speeds = []
                                let peak = 0
                                let prev = EditorState.propertyValueAt(root.trackIndex, root.clipIndex, entry.prop, t0, base)
                                for (let i = 1; i <= steps; ++i) {
                                    const v = EditorState.propertyValueAt(root.trackIndex, root.clipIndex, entry.prop,
                                                                          t0 + dt * i, base)
                                    const sp = Math.abs(v - prev) / Math.max(1e-6, dt)
                                    speeds.push(sp)
                                    peak = Math.max(peak, sp)
                                    prev = v
                                }
                                root.speedPeak = peak
                                if (peak > 1e-9) {
                                    // After Effects' Speed Graph: the speed is the curve now.
                                    ctx.strokeStyle = String(entry.color)
                                    ctx.globalAlpha = 1.0
                                    ctx.lineWidth = 2
                                    ctx.beginPath()
                                    for (let i = 0; i < speeds.length; ++i) {
                                        const x = root.xForSeconds(t0 + dt * (i + 0.5))
                                        const y = graph.height - 4 - (speeds[i] / peak) * (graph.height - 8)
                                        if (i === 0)
                                            ctx.moveTo(x, y)
                                        else
                                            ctx.lineTo(x, y)
                                    }
                                    ctx.stroke()
                                    ctx.setLineDash([])
                                    ctx.globalAlpha = 1.0
                                }
                            }
                            ctx.restore()
                        }
                        Connections {
                            target: root
                            function onSeriesChanged() { curveCanvas.requestPaint() }
                            function onPxPerSecondChanged() { curveCanvas.requestPaint() }
                            function onPaintOriginXChanged() { curveCanvas.requestPaint() }
                            function onDragSecondsChanged() { curveCanvas.requestPaint() }
                            function onDragValueChanged() { curveCanvas.requestPaint() }
                            function onShiftDeltaChanged() { curveCanvas.requestPaint() }
                            function onSpeedGraphChanged() { curveCanvas.requestPaint() }
                            function onGroupDyChanged() { curveCanvas.requestPaint() }
                            function onDragTangentOutDyChanged() { curveCanvas.requestPaint() }
                            function onDragTangentOutDxChanged() { curveCanvas.requestPaint() }
                            function onDragTangentInDyChanged() { curveCanvas.requestPaint() }
                            function onDragTangentInDxChanged() { curveCanvas.requestPaint() }
                            function onFocusedPropChanged() { curveCanvas.requestPaint() }
                            function onViewLoChanged() { curveCanvas.requestPaint() }
                            function onViewHiChanged() { curveCanvas.requestPaint() }
                            function onOthersShownChanged() { curveCanvas.requestPaint() }
                            function onLaneHeightChanged() { curveCanvas.requestPaint() }
                        }
                    }

                    // Below the key dots (z 2) and tangent grips (z 4), so double-clicking an
                    // existing node grabs it instead of inserting another one on top of it.
                    // A drag here draws the box that picks keys (Shift or Ctrl add to the picked).
                    MouseArea {
                        anchors.fill: parent
                        z: 1
                        acceptedButtons: Qt.LeftButton
                        preventStealing: true
                        property bool boxed: false
                        onDoubleClicked: function (mouse) { root.addKeyAt(mouse.x) }
                        onPressed: (mouse) => {
                            root.marqueeX0 = root.marqueeX1 = mouse.x
                            root.marqueeY0 = root.marqueeY1 = mouse.y
                            boxed = false
                            root.marqueeBase = root.tools
                                && (mouse.modifiers & (Qt.ShiftModifier | Qt.ControlModifier))
                                ? root.tools.keys.slice() : []
                        }
                        onPositionChanged: (mouse) => {
                            root.marqueeX1 = mouse.x
                            root.marqueeY1 = mouse.y
                            if (!root.marqueeActive && Math.abs(mouse.x - root.marqueeX0) < 4
                                    && Math.abs(mouse.y - root.marqueeY0) < 4)
                                return
                            root.marqueeActive = true
                            boxed = true
                            root.marqueeApply()
                        }
                        onReleased: {
                            if (root.marqueeActive)
                                root.marqueeApply()
                            else if (!boxed && root.tools && root.marqueeBase.length === 0)
                                root.tools.clear()
                            root.marqueeActive = false
                        }
                        onCanceled: root.marqueeActive = false
                    }
                    Rectangle {
                        visible: root.marqueeActive
                        z: 6
                        x: Math.min(root.marqueeX0, root.marqueeX1)
                        y: Math.min(root.marqueeY0, root.marqueeY1)
                        width: Math.abs(root.marqueeX1 - root.marqueeX0)
                        height: Math.abs(root.marqueeY1 - root.marqueeY0)
                        color: Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.14)
                        border.width: 1
                        border.color: Theme.primary
                    }

                    // The other selected layers' keys: a click picks one (Ctrl or Shift adds it to
                    // the keys picked on every layer) and makes its layer the edited one; a drag
                    // moves every picked key, on all the layers, in time.
                    Repeater {
                        model: root.otherKeyHandles
                        delegate: Item {
                            id: otherKey
                            required property var modelData
                            readonly property var ref: ({ clip: modelData.clip, prop: modelData.prop,
                                                          seconds: modelData.seconds })
                            readonly property bool isPicked: {
                                if (!root.tools)
                                    return false
                                void root.tools.keys
                                return root.tools.isPicked(modelData.track, ref)
                            }
                            readonly property real shiftDx: {
                                if (!root.tools)
                                    return 0
                                void root.tools.dragDelta
                                return root.tools.shifting && root.tools.isShifted(modelData.track, ref)
                                       ? root.tools.dragDelta * root.pxPerSecond : 0
                            }
                            width: 16
                            height: 16
                            x: root.xForSeconds(modelData.seconds) - width / 2 + shiftDx
                            y: root.yForValue(modelData.value, modelData.entry) - height / 2
                            z: 1
                            KeyframeGlyph {
                                anchors.centerIn: parent
                                size: otherKey.isPicked ? 13 : (otherHover.hovered ? 11 : 9)
                                color: otherKey.modelData.entry.color
                                picked: otherKey.isPicked
                                lit: otherHover.hovered
                            }
                            HoverHandler {
                                id: otherHover
                                cursorShape: Qt.PointingHandCursor
                            }
                            MouseArea {
                                anchors.fill: parent
                                preventStealing: true
                                property real pressX: 0
                                property bool moved: false
                                property bool armed: false
                                onPressed: (mouse) => {
                                    pressX = mapToItem(root, mouse.x, mouse.y).x
                                    moved = false
                                    armed = !(mouse.modifiers & (Qt.ControlModifier | Qt.ShiftModifier))
                                    root.tools.press(otherKey.modelData.track, otherKey.ref, mouse.modifiers,
                                                     otherKey.modelData.points)
                                }
                                onPositionChanged: (mouse) => {
                                    if (!pressed || !armed)
                                        return
                                    const dx = mapToItem(root, mouse.x, mouse.y).x - pressX
                                    if (!moved) {
                                        if (Math.abs(dx) < 3)
                                            return
                                        moved = true
                                        root.frozenOtherKeys = root.otherKeyHandles.slice()
                                        root.tools.beginShift()
                                    }
                                    const want = EditorState.snapKeyTime(otherKey.modelData.seconds + dx / root.pxPerSecond)
                                    root.tools.shiftTo(want - otherKey.modelData.seconds)
                                }
                                onReleased: {
                                    if (moved) {
                                        // Unfreezing rebuilds this delegate: everything else first.
                                        moved = false
                                        root.tools.endShift()
                                        root.frozenOtherKeys = []
                                        return
                                    }
                                    if (armed) {
                                        root.editLayer(otherKey.modelData.id)
                                        EditorState.playheadSeconds = otherKey.modelData.seconds
                                    }
                                    moved = false
                                }
                                onCanceled: {
                                    const was = moved
                                    moved = false
                                    if (was) {
                                        root.tools.endShift()
                                        root.frozenOtherKeys = []
                                    }
                                }
                            }
                        }
                    }

                    Repeater {
                        model: root.keyHandles
                        delegate: Item {
                            id: keyDot
                            required property var modelData
                            readonly property var entry: root.series[modelData.seriesIndex]
                            readonly property var ref: ({ clip: root.clipIndex,
                                                          prop: root.refProp(modelData.prop),
                                                          seconds: modelData.seconds })
                            readonly property bool isPicked: {
                                if (!root.tools)
                                    return false
                                void root.tools.keys
                                void root.tools.dragDelta
                                void root.tools.stretchFactor
                                // While the tracks' rows drag several keys the series is live
                                // here, so a moved key is matched by where it started.
                                return root.tools.isPicked(root.trackIndex, ref)
                                       || root.tools.isShifted(root.trackIndex,
                                              { clip: ref.clip, prop: ref.prop,
                                                seconds: root.tools.startOf(ref.seconds) })
                            }
                            // Moved with the others in a drag of several picked keys.
                            readonly property real shiftDx: root.draggingKey
                                && root.shifted(modelData.prop, modelData.seconds)
                                ? root.shiftOf(modelData.seconds) * root.pxPerSecond : 0
                            property bool groupDrag: false
                            width: 20
                            height: 20
                            opacity: (root.curveEditing && !root.isFocused(modelData.seriesIndex)
                                      && !isPicked) ? 0.4 : 1.0
                            readonly property bool isLinkedPartnerKey: EditorState.positionLinked
                                && ((root.dragProp === "x" && modelData.prop === "y") || (root.dragProp === "y" && modelData.prop === "x"))
                                && root.dragIndex >= 0 && root.focusedIndex >= 0 && root.focusedIndex < root.series.length
                                && Math.abs((root.series[root.focusedIndex].points[root.dragIndex] ? root.series[root.focusedIndex].points[root.dragIndex].seconds : -999) - modelData.seconds) < (1 / 30)
                            x: root.xForSeconds(modelData.seconds) - width / 2 + shiftDx + (isLinkedPartnerKey ? (root.xForSeconds(root.dragSeconds) - root.xForSeconds(modelData.seconds)) : dragDx)
                            y: (root.speedGraph
                                ? root.speedY(root.keySideSpeed(entry, modelData.seconds,
                                                                modelData.pointIndex < entry.points.length - 1))
                                : root.yForValue(root.draggingKey && root.shifted(modelData.prop, modelData.seconds)
                                                     ? root.groupValue(modelData.value, entry) : modelData.value, entry))
                               - height / 2 + dragDy
                            z: isPicked ? 3 : 2

                            // The same shapes as the tracks' rows: how the value arrives and
                            // leaves, red and larger when picked.
                            KeyframeGlyph {
                                anchors.centerIn: parent
                                size: keyDot.isPicked ? 17 : (keyHover.hovered ? 15 : 13)
                                inHalf: keyDot.modelData.halves["in"]
                                outHalf: keyDot.modelData.halves["out"]
                                color: keyDot.modelData.color
                                picked: keyDot.isPicked
                                lit: keyHover.hovered
                            }
                            HoverHandler {
                                id: keyHover
                                cursorShape: Qt.PointingHandCursor
                            }

                            // Offsets rather than direct x/y writes, which would
                            // clobber the bindings above for good.
                            property real dragDx: 0
                            property real dragDy: 0
                            property real editSeconds: modelData.seconds

                            // Touching a key moves focus to its series, which is what arms
                            // that curve's tangent handles.
                            function remove() {
                                EditorState.removeClipKeyframe(
                                    root.trackIndex,
                                    root.clipIndex,
                                    keyDot.modelData.prop,
                                    keyDot.modelData.seconds
                                )
                            }

                            // A click picks the key as the tracks' rows do (Ctrl adds or takes
                            // away, Shift picks a run) and brings the playhead to it.
                            function pickHere() {
                                if (!root.tools)
                                    return
                                root.tools.press(root.trackIndex, keyDot.ref,
                                                 EditorState.keyboardModifiers(), keyDot.entry.points)
                            }

                            TapHandler {
                                // Finger taps land on touchMove below, which takes the press.
                                acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
                                                 | PointerDevice.Stylus
                                onTapped: {
                                    root.focusedProp = keyDot.modelData.prop
                                    keyDot.pickHere()
                                    if (!(EditorState.keyboardModifiers()
                                          & (Qt.ControlModifier | Qt.ShiftModifier)))
                                        EditorState.playheadSeconds = keyDot.modelData.seconds
                                }
                                onDoubleTapped: keyDot.remove()
                            }
                            TapHandler {
                                acceptedButtons: Qt.RightButton
                                acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
                                                 | PointerDevice.Stylus
                                onTapped: {
                                    if (!root.tools)
                                        return
                                    root.focusedProp = keyDot.modelData.prop
                                    root.tools.openMenu(root.trackIndex, keyDot.ref,
                                                        keyDot.modelData.halves, keyDot.modelData.hold,
                                                        true, keyDot,
                                                        Qt.point(keyDot.width / 2, keyDot.height))
                                }
                            }

                            function beginMove() {
                                root.focusedProp = keyDot.modelData.prop
                                if (root.tools && !keyDot.isPicked)
                                    root.tools.pick(root.trackIndex, [keyDot.ref])
                                // Several picked: they all move in time together, values kept.
                                keyDot.groupDrag = !!root.tools && root.tools.keys.length > 1
                                if (keyDot.groupDrag) {
                                    // Each picked key's value where the drag starts.
                                    const base = []
                                    for (const k of root.tools.keys) {
                                        const entry = root.series.find((e) => e.prop === k.prop)
                                        const pt = entry ? entry.points.find((p) => Math.abs(p.seconds - k.seconds) < 1e-4)
                                                         : null
                                        if (entry && pt && k.clip === root.clipIndex
                                                && root.tools.keyTrack(k) === root.trackIndex)
                                            base.push({ key: k, value: pt.value, entry: entry })
                                    }
                                    root.groupValueBase = base
                                    root.groupDy = 0
                                    root.frozenSeries = root.series
                                    root.draggingKey = true
                                    root.tools.beginShift()
                                    return
                                }
                                keyDot.editSeconds = keyDot.modelData.seconds
                                root.frozenSeries = root.series
                                root.dragProp = keyDot.modelData.prop
                                root.dragIndex = keyDot.modelData.pointIndex
                                root.dragSeconds = keyDot.modelData.seconds
                                root.dragValue = keyDot.modelData.value
                                root.draggingKey = true
                                EditorState.beginPreviewDrag(qsTr("Move keyframe"))
                            }
                            function endMove() {
                                if (keyDot.groupDrag) {
                                    // Same order as below: unfreezing destroys this delegate.
                                    keyDot.groupDrag = false
                                    root.groupDy = 0
                                    root.groupValueBase = []
                                    root.tools.endShift()
                                    root.draggingKey = false
                                    return
                                }
                                // Unfreezing rebuilds the Repeater and destroys this
                                // delegate mid-handler, so every reset has to land first.
                                // The moved key stays picked at its new time.
                                if (root.tools)
                                    root.tools.pick(root.trackIndex,
                                                    [{ clip: root.clipIndex,
                                                       prop: root.refProp(keyDot.modelData.prop),
                                                       seconds: keyDot.editSeconds }])
                                root.dragProp = ""
                                root.dragIndex = -1
                                keyDot.dragDx = 0
                                keyDot.dragDy = 0
                                EditorState.commitPreviewDrag()
                                root.draggingKey = false
                            }
                            function moveBy(dx, dy) {
                                if (keyDot.groupDrag) {
                                    const from = keyDot.modelData.seconds
                                    const moved = root.tools.shiftTo(
                                        EditorState.snapKeyTime(from + dx / root.pxPerSecond) - from)
                                    EditorState.playheadSeconds = from + moved
                                    // Their values ride the pointer's height too, unless Shift.
                                    const keepValues = (EditorState.keyboardModifiers() & Qt.ShiftModifier) !== 0
                                    root.groupDy = keepValues ? 0 : dy
                                    for (const b of root.groupValueBase) {
                                        const at = b.key.seconds + moved
                                        EditorState.previewMoveClipKeyframe(
                                            root.trackIndex, b.key.clip, b.key.prop, at, at,
                                            root.groupValue(b.value, b.entry))
                                    }
                                    return
                                }
                                const entry = keyDot.entry
                                const baseSec = keyDot.modelData.seconds
                                const baseVal = keyDot.modelData.value
                                // snapTime pulls in beats, clip edges and the playhead,
                                // and is a no-op when the toolbar's snap toggle is off.
                                const rawSec = baseSec + dx / root.pxPerSecond
                                const newSec = Math.max(
                                    root.clipStart,
                                    Math.min(root.clipStart + root.clipDuration,
                                             EditorState.snapKeyTime(rawSec)))
                                // In Speed Graph a key moves in time only: its height there is a speed.
                                const isShift = root.speedGraph || (EditorState.keyboardModifiers() & Qt.ShiftModifier) !== 0
                                const newVal = isShift ? baseVal : Math.max(
                                    entry.valueMin,
                                    Math.min(entry.valueMax,
                                             root.valueForY(
                                                 root.yForValue(baseVal, entry) + dy,
                                                 entry)))
                                EditorState.previewMoveClipKeyframe(
                                    root.trackIndex, root.clipIndex,
                                    keyDot.modelData.prop, keyDot.editSeconds, newSec, newVal)
                                keyDot.editSeconds = newSec
                                keyDot.dragDx = root.xForSeconds(newSec) - root.xForSeconds(baseSec)
                                keyDot.dragDy = root.yForValue(newVal, entry)
                                              - root.yForValue(baseVal, entry)
                                root.dragSeconds = newSec
                                root.dragValue = newVal
                            }

                            DragHandler {
                                target: null
                                acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
                                                 | PointerDevice.Stylus
                                onActiveChanged: {
                                    if (active)
                                        keyDot.beginMove()
                                    else
                                        keyDot.endMove()
                                }
                                onTranslationChanged: {
                                    if (active)
                                        keyDot.moveBy(translation.x, translation.y)
                                }
                            }

                            // Touchscreen: a finger on the lane pans it, so a key only
                            // moves after a hold. Mouse presses are rejected for the DragHandler.
                            MouseArea {
                                id: touchMove
                                anchors.fill: parent
                                anchors.margins: -10
                                pressAndHoldInterval: Theme.touchLiftInterval
                                preventStealing: armed
                                property bool armed: false
                                property point origin
                                onPressed: (mouse) => {
                                    if (mouse.source === Qt.MouseEventNotSynthesized) {
                                        mouse.accepted = false
                                        return
                                    }
                                    armed = false
                                }
                                onPressAndHold: (mouse) => {
                                    origin = mapToItem(null, mouse.x, mouse.y)
                                    armed = true
                                    Haptics.pickUp()
                                    keyDot.beginMove()
                                }
                                onPositionChanged: (mouse) => {
                                    if (!armed)
                                        return
                                    const p = mapToItem(null, mouse.x, mouse.y)
                                    keyDot.moveBy(p.x - origin.x, p.y - origin.y)
                                }
                                onClicked: root.focusedProp = keyDot.modelData.prop
                                onDoubleClicked: keyDot.remove()
                                onReleased: finish()
                                onCanceled: finish()
                                function finish() {
                                    if (!armed)
                                        return
                                    armed = false
                                    keyDot.endMove()
                                }
                            }
                        }
                    }

                    // After Effects' transform box (0.30): two or more keys picked on the curve being shaped get
                    // a box; its left and right sides stretch them in time and its top and bottom scale their
                    // values, each from the side across. One undo step per drag.
                    Item {
                        id: transformBox
                        readonly property var picked: {
                            void root.series
                            if (!root.tools || !root.curveEditing || root.speedGraph
                                    || root.focusedIndex < 0 || root.focusedIndex >= root.series.length)
                                return []
                            void root.tools.keys
                            const entry = root.series[root.focusedIndex]
                            return entry.points.filter((p) => root.tools.isPicked(
                                root.trackIndex, { clip: root.clipIndex, prop: root.refProp(entry.prop), seconds: p.seconds }))
                        }
                        readonly property var entry: root.focusedIndex >= 0 && root.focusedIndex < root.series.length
                                                     ? root.series[root.focusedIndex] : null
                        visible: picked.length >= 2 && !!entry
                        z: 5
                        readonly property real t0: picked.length ? Math.min(...picked.map((p) => p.seconds)) : 0
                        readonly property real t1: picked.length ? Math.max(...picked.map((p) => p.seconds)) : 0
                        readonly property real v0: picked.length ? Math.min(...picked.map((p) => p.value)) : 0
                        readonly property real v1: picked.length ? Math.max(...picked.map((p) => p.value)) : 0
                        x: root.xForSeconds(t0) - 8
                        width: root.xForSeconds(t1) - root.xForSeconds(t0) + 16
                        y: entry ? root.yForValue(v1, entry) - 8 : 0
                        height: entry ? root.yForValue(v0, entry) - root.yForValue(v1, entry) + 16 : 0

                        Rectangle {
                            anchors.fill: parent
                            color: "transparent"
                            border.width: 1
                            border.color: Theme.primary
                            opacity: 0.8
                        }

                        // Where each picked key started, and where it is now in the drag.
                        property var base: []
                        property var now: []
                        function begin() {
                            const e = transformBox.entry
                            transformBox.base = transformBox.picked.map((p) => ({ "seconds": p.seconds, "value": p.value }))
                            transformBox.now = transformBox.base.map((b) => b.seconds)
                            EditorState.beginPreviewDrag(qsTr("Transform keyframes"))
                        }
                        // side: "left", "right", "top", "bottom"; k the stretch (1 = as it was).
                        function apply(side, k) {
                            const e = transformBox.entry
                            if (!e)
                                return
                            const b = transformBox.base
                            const tLo = Math.min(...b.map((x) => x.seconds)), tHi = Math.max(...b.map((x) => x.seconds))
                            const vLo = Math.min(...b.map((x) => x.value)), vHi = Math.max(...b.map((x) => x.value))
                            const order = b.map((x, i) => i)
                            const timed = side === "left" || side === "right"
                            const pivotT = side === "left" ? tHi : tLo
                            const pivotV = side === "top" ? vLo : vHi
                            // Keys move away from (or toward) the pivot: the far ones first when growing, so
                            // none lands on one that has not moved yet.
                            order.sort((i, j) => {
                                const di = Math.abs(timed ? b[i].seconds - pivotT : 0)
                                const dj = Math.abs(timed ? b[j].seconds - pivotT : 0)
                                return k >= 1 ? dj - di : di - dj
                            })
                            const refs = []
                            for (const i of order) {
                                const to = timed ? EditorState.snapKeyTime(pivotT + (b[i].seconds - pivotT) * k) : b[i].seconds
                                const value = timed ? b[i].value : pivotV + (b[i].value - pivotV) * k
                                EditorState.previewMoveClipKeyframe(root.trackIndex, root.clipIndex, e.prop,
                                                                    transformBox.now[i], to, value)
                                transformBox.now[i] = to
                            }
                            for (let i = 0; i < b.length; ++i)
                                refs.push({ clip: root.clipIndex, prop: root.refProp(e.prop), seconds: transformBox.now[i] })
                            root.tools.pick(root.trackIndex, refs)
                        }

                        BoxSide { box: transformBox; side: "left"; x: -3; width: 8; height: parent.height }
                        BoxSide { box: transformBox; side: "right"; x: parent.width - 5; width: 8; height: parent.height }
                        BoxSide { box: transformBox; side: "top"; y: -3; height: 8; width: parent.width; x: 0 }
                        BoxSide { box: transformBox; side: "bottom"; y: parent.height - 5; height: 8; width: parent.width; x: 0 }
                    }

                    // Tangent grips for the focused curve, above the keys so they stay
                    // grabbable where a handle folds back over its own key.
                    Repeater {
                        model: root.tangentHandles

                        delegate: Item {
                            id: tangent
                            required property var modelData

                            readonly property var entry: root.series[root.focusedIndex]
                            readonly property real keyX: root.xForSeconds(modelData.point.seconds)
                            readonly property real keyY: root.speedGraph
                                ? root.speedY(root.keySideSpeed(entry, modelData.point.seconds, modelData.outgoing))
                                : root.yForValue(modelData.point.value, entry)
                            readonly property real tipX:
                                root.xForSeconds(modelData.point.seconds
                                                 + root.handleSeconds(modelData.point, modelData.outgoing,
                                                                      modelData.neighbour))
                            // In Speed Graph the handle is level with its key: its height is that side's speed.
                            readonly property real tipY: root.speedGraph
                                ? tangent.keyY
                                : root.yForValue(root.handleValue(modelData.point, modelData.outgoing), entry)

                            anchors.fill: parent
                            z: 4

                            // Leader line from the key out to the grip.
                            Rectangle {
                                x: tangent.keyX
                                y: tangent.keyY
                                width: Math.hypot(tangent.tipX - tangent.keyX + tangent.dragDx,
                                                  tangent.tipY - tangent.keyY + tangent.dragDy)
                                height: 1
                                color: tangent.modelData.color
                                opacity: 0.55
                                transformOrigin: Item.TopLeft
                                rotation: Math.atan2(tangent.tipY - tangent.keyY + tangent.dragDy,
                                                     tangent.tipX - tangent.keyX + tangent.dragDx)
                                          * 180 / Math.PI
                            }

                            property real dragDx: 0
                            property real dragDy: 0

                            Rectangle {
                                id: grip
                                width: 8
                                height: 8
                                radius: 4
                                color: Theme.panelBackground
                                border.width: 1.5
                                border.color: tangent.modelData.color
                                x: tangent.tipX - width / 2 + tangent.dragDx
                                y: tangent.tipY - height / 2 + tangent.dragDy

                                // A MouseArea that takes the press (0.30): with a DragHandler the
                                // box-picking MouseArea under it took a quick drag and the handle
                                // did not move (bounce exercise #12). Larger than the dot.
                                MouseArea {
                                    id: gripDrag
                                    anchors.fill: parent
                                    anchors.margins: -5
                                    cursorShape: Qt.PointingHandCursor
                                    preventStealing: true
                                    property bool active: false
                                    property point origin
                                    property point translation: Qt.point(0, 0)
                                    property real startKeyY: 0
                                    onPressed: (mouse) => {
                                        startKeyY = tangent.keyY
                                        origin = mapToItem(null, mouse.x, mouse.y)
                                        translation = Qt.point(0, 0)
                                        active = true
                                    }
                                    onPositionChanged: (mouse) => {
                                        if (!active)
                                            return
                                        const p = mapToItem(null, mouse.x, mouse.y)
                                        translation = Qt.point(p.x - origin.x, p.y - origin.y)
                                    }
                                    onReleased: active = false
                                    onCanceled: active = false
                                    // Speed Graph (0.30): across is the influence (how far the handle
                                    // reaches into its segment), up the speed on that side of the key.
                                    // The handle keeps the way the value goes there; unless the key
                                    // is a corner, the other side takes the same speed.
                                    function speedDrag(p, outgoing) {
                                        const pts = root.series[root.focusedIndex].points
                                        const i = tangent.modelData.pointIndex
                                        const neighbour = outgoing ? pts[i + 1] : pts[i - 1]
                                        if (!neighbour)
                                            return
                                        const newX = tangent.tipX + translation.x
                                        let dx = root.secondsForX(newX - tangent.keyX)
                                        const segment = Math.abs(neighbour.seconds - p.seconds)
                                        dx = outgoing ? Math.max(segment * 0.01, Math.min(segment, dx))
                                                      : Math.min(-segment * 0.01, Math.max(-segment, dx))
                                        const speed = root.speedForY(gripDrag.startKeyY + translation.y)
                                        const rising = outgoing ? neighbour.value >= p.value : p.value >= neighbour.value
                                        const slope = (rising ? 1 : -1) * speed
                                        let inDx = p.inDx || 0
                                        let inDy = p.inDy || 0
                                        let outDx = p.outDx || 0
                                        let outDy = p.outDy || 0
                                        if (outgoing) {
                                            outDx = dx
                                            outDy = slope * dx
                                            if (!p.corner && Math.abs(inDx) > 1e-6)
                                                inDy = slope * inDx
                                        } else {
                                            inDx = dx
                                            inDy = slope * dx
                                            if (!p.corner && Math.abs(outDx) > 1e-6)
                                                outDy = slope * outDx
                                        }
                                        EditorState.previewSetKeyframeTangents(
                                            root.trackIndex, root.clipIndex, root.series[root.focusedIndex].prop,
                                            p.seconds, inDx, inDy, outDx, outDy, p.corner)
                                        root.dragTangentInDx = inDx
                                        root.dragTangentInDy = inDy
                                        root.dragTangentOutDx = outDx
                                        root.dragTangentOutDy = outDy
                                        tangent.dragDx = root.xForSeconds(p.seconds + dx) - tangent.tipX
                                        tangent.dragDy = root.speedY(speed) - tangent.keyY
                                    }
                                    onActiveChanged: {
                                        if (active) {
                                            // Freeze the model exactly as a key drag does, so the
                                            // Repeater cannot destroy this delegate mid-grab and
                                            // so the value axis stops auto-fitting under the cursor.
                                            const p = tangent.modelData.point
                                            root.frozenSeries = root.series
                                            root.dragProp = root.series[root.focusedIndex].prop
                                            root.dragTangentIndex = tangent.modelData.pointIndex
                                            root.dragTangentInDx = p.inDx || 0
                                            root.dragTangentInDy = p.inDy || 0
                                            root.dragTangentOutDx = p.outDx || 0
                                            root.dragTangentOutDy = p.outDy || 0
                                            root.frozenSpeedPeak = root.speedPeak
                                            root.draggingKey = true
                                            EditorState.beginPreviewDrag(qsTr("Edit keyframe curve"))
                                        } else {
                                            // Same ordering as the key drag: unfreezing destroys
                                            // this delegate, so reset before it.
                                            root.dragProp = ""
                                            root.dragTangentIndex = -1
                                            tangent.dragDx = 0
                                            tangent.dragDy = 0
                                            EditorState.commitPreviewDrag()
                                            root.draggingKey = false
                                        }
                                    }
                                    onTranslationChanged: {
                                        if (!active)
                                            return
                                        const p = tangent.modelData.point
                                        const outgoing = tangent.modelData.outgoing
                                        if (root.speedGraph) {
                                            gripDrag.speedDrag(p, outgoing)
                                            return
                                        }

                                        const isShift = (EditorState.keyboardModifiers() & Qt.ShiftModifier) !== 0
                                        const newX = tangent.tipX + translation.x
                                        const newY = isShift ? tangent.keyY : (tangent.tipY + translation.y)
                                        // dx keeps its sign: an out-handle may not reach back
                                        // past its key, nor an in-handle forward past its own.
                                        let dx = root.secondsForX(newX - tangent.keyX)
                                        dx = outgoing ? Math.max(0, dx) : Math.min(0, dx)
                                        const dy = isShift ? 0.0 : (root.valueForY(newY, tangent.entry) - p.value)

                                        const inDx = outgoing ? (p.inDx || 0) : dx
                                        const outDx = outgoing ? dx : (p.outDx || 0)
                                        let inDy = outgoing ? (p.inDy || 0) : dy
                                        let outDy = outgoing ? dy : (p.outDy || 0)

                                        // Unless the key is a corner, the far tangent takes the
                                        // same slope so the curve stays smooth through the key.
                                        // Its dx has the opposite sign, so its dy flips with it.
                                        if (!p.corner && Math.abs(dx) > 1e-6) {
                                            const slope = dy / dx
                                            if (outgoing)
                                                inDy = slope * inDx
                                            else
                                                outDy = slope * outDx
                                        }

                                        EditorState.previewSetKeyframeTangents(
                                            root.trackIndex, root.clipIndex,
                                            root.series[root.focusedIndex].prop,
                                            p.seconds, inDx, inDy, outDx, outDy, p.corner)

                                        root.dragTangentInDx = inDx
                                        root.dragTangentInDy = inDy
                                        root.dragTangentOutDx = outDx
                                        root.dragTangentOutDy = outDy
                                        tangent.dragDx = newX - tangent.tipX
                                        tangent.dragDy = isShift ? (tangent.keyY - tangent.tipY) : (newY - tangent.tipY)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    }

    // Bottom edge resize grip. A sibling of the Row rather than a child, so it anchors to the
    // lane instead of being laid out horizontally beside the graph, and sits above the lane's
    // content so a drag near the boundary resizes rather than grabbing what is underneath.
    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 5
        z: 100
        color: resizeHover.hovered || resizeDrag.active ? Theme.primary : "transparent"
        opacity: 0.6

        HoverHandler {
            id: resizeHover
            cursorShape: Qt.SizeVerCursor
        }
        TapHandler {
            onDoubleTapped: root.toggleExpanded()
        }
        DragHandler {
            id: resizeDrag
            target: null
            yAxis.enabled: true
            xAxis.enabled: false
            property real startHeight: 0
            onActiveChanged: {
                if (active)
                    startHeight = root.laneHeight
            }
            onTranslationChanged: {
                if (!active)
                    return
                root.laneHeight = Math.max(root.minLaneHeight,
                                           Math.min(root.maxLaneHeight,
                                                    startHeight + translation.y))
            }
        }
    }

    // The buttons over the graph when it sits inside the track's lines.
    Rectangle {
        id: floatButtons
        visible: root.inline && root.hasContent
        z: 40
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.topMargin: 4
        anchors.rightMargin: 6
        width: graphButtons.implicitWidth + 8
        height: 26
        radius: 4
        color: Qt.rgba(0, 0, 0, 0.45)
    }

    // The other selected layers whose curves are drawn (0.26): their names, a click edits one.
    Flow {
        visible: root.hasContent && root.otherLayers.length > 0
        z: 40
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.leftMargin: root.labelsWidth + 6
        anchors.bottomMargin: 4
        width: Math.min(parent.width - root.labelsWidth - 12, 600)
        spacing: 3
        ThemedChip {
            text: root.clip.name || qsTr("Layer")
            chipHeight: 18
            horizontalPadding: 4
            selected: true
            tooltip: qsTr("The layer whose curves you are editing")
        }
        Repeater {
            model: root.otherLayers
            delegate: ThemedChip {
                required property var modelData
                text: modelData.name
                chipHeight: 18
                horizontalPadding: 4
                selected: false
                tooltip: qsTr("Edit this layer's curves (dashed)")
                // As in After Effects, that layer becomes the selected one (the last of the
                // selection), so its track's lines and this graph follow it; the rest stay picked.
                onClicked: root.editLayer(modelData.id)
            }
        }
    }

    // A click on a line's name in the track (0.25) makes its curve the one being shaped.
    Connections {
        target: root.tools
        ignoreUnknownSignals: true
        function onFocusPropChanged() {
            if (root.tools.focusProp.length > 0)
                root.focusedProp = root.tools.focusProp
        }
    }
}
