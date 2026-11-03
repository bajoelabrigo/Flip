import QtCore
import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift
import "."

// Live-lyrics style subtitle editor. The list auto-scrolls and highlights the cue
// currently on screen as the playhead moves, keeping the neighbouring lines visible.
// Editing happens in the fixed panel below so the list always shows context.
// Owns the full panel content area (the list manages its own scrolling).
Item {
    id: root

    property var clip: null
    property var formatSeconds: (function (v) { return Number(v || 0).toFixed(2) })
    property int trackIndex: EditorState.selectedTrack
    property int clipIndex: EditorState.selectedClip

    // The phone's properties sheet: a cue is edited in the keyboard composer instead of the
    // panel below the list, so a tap on a row asks the editor page to open it.
    property bool compactEdit: false
    signal cueEditRequested(int index)

    readonly property double defaultCueDuration: 3.0

    // The cue being edited, shared with the timeline cue lane. Follows the active cue
    // during playback; while paused it only changes on an explicit click / add.
    readonly property int selectedCueIndex: EditorState.selectedSubtitleCue

    readonly property double localPlayhead: {
        void EditorState.inspectorPlayheadSeconds
        void root.clip
        return clip ? EditorState.subtitleLocalPlayheadSeconds(trackIndex, clipIndex) : -1
    }
    readonly property double clipDuration: (clip && clip.duration) ? clip.duration : 0
    readonly property var cues: (clip && clip.subtitleCues) ? clip.subtitleCues : []
    readonly property int activeCueIndex: {
        const t = localPlayhead
        if (t < 0)
            return -1
        for (let i = 0; i < cues.length; i++) {
            if (t >= cues[i].start && t < cues[i].end)
                return i
        }
        return -1
    }
    readonly property var selectedCue: (selectedCueIndex >= 0 && selectedCueIndex < cues.length)
                                       ? cues[selectedCueIndex] : null

    function formatCueTime(seconds) {
        const clamped = Math.max(0, seconds)
        const m = Math.floor(clamped / 60)
        const s = clamped - m * 60
        const whole = Math.floor(s)
        const frac = Math.floor((s - whole) * 1000)
        return String(m).padStart(2, "0") + ":" + String(whole).padStart(2, "0") + "."
               + String(frac).padStart(3, "0")
    }

    function parseCueTime(str) {
        const t = String(str).trim()
        if (t.indexOf(":") >= 0) {
            const parts = t.split(":")
            const m = parseFloat(parts[0])
            const s = parseFloat(parts[1])
            if (isNaN(m) || isNaN(s))
                return NaN
            return m * 60 + s
        }
        return parseFloat(t)
    }

    // «Clean up» and «Emojis» show what they would change first, applied only on «Apply».
    property string changesKind: ""
    property var changesList: []
    function showChanges(kind) {
        root.changesList = EditorState.subtitleChangesPreview(root.trackIndex, root.clipIndex, kind)
        root.changesKind = kind
    }
    function applyChanges() {
        if (root.changesKind === "emojis")
            EditorState.addEmojisToSubtitles(root.trackIndex, root.clipIndex)
        else if (root.changesKind === "keywords")
            EditorState.highlightSubtitleKeywords(root.trackIndex, root.clipIndex)
        else if (root.changesKind === "cleanup")
            EditorState.cleanUpSubtitles(root.trackIndex, root.clipIndex)
        root.changesKind = ""
    }

    // Spelling, one flagged word at a time (the system's spell checker): a suggestion fixes it in its
    // caption, «Ignore» skips that word for the rest of the check.
    readonly property bool spellAvailable: EditorState.subtitleSpellCheckAvailable()
    property bool spellOpen: false
    property var spellIssues: []
    property var spellIgnored: ({})
    readonly property var spellIssue: spellIssues.length > 0 ? spellIssues[0] : null
    function checkSpelling() {
        root.spellIssues = EditorState.subtitleSpellingIssues(root.trackIndex, root.clipIndex)
            .filter(i => !root.spellIgnored[i.word.toLowerCase()])
        root.spellOpen = true
        if (root.spellIssue)
            EditorState.selectedSubtitleCue = root.spellIssue.cue
    }
    function fixSpelling(suggestion) {
        const issue = root.spellIssue
        const cue = issue ? root.cues[issue.cue] : null
        if (!cue || String(cue.text).substr(issue.start, issue.length) !== issue.word) {
            root.checkSpelling()
            return
        }
        let before = cue.text.slice(0, issue.start)
        const after = cue.text.slice(issue.start + issue.length)
        const patch = {}
        if (suggestion === "") {
            // A repeated word: it goes with its space, and the first of the pair takes its timing.
            before = before.replace(/\s+$/, "")
            const ends = (cue.wordEnds || []).slice()
            const k = root.wordCount(before)
            if (ends.length === root.wordCount(cue.text) && k > 0) {
                ends.splice(k - 1, 1)
                patch.wordEnds = ends
            }
        }
        patch.text = before + suggestion + after
        root.updateCue(issue.cue, patch)
        Qt.callLater(root.checkSpelling)
    }
    function ignoreSpelling() {
        const issue = root.spellIssue
        if (!issue)
            return
        const ignored = Object.assign({}, root.spellIgnored)
        ignored[issue.word.toLowerCase()] = true
        root.spellIgnored = ignored
        root.spellIssues = root.spellIssues.filter(i => !ignored[i.word.toLowerCase()])
        if (root.spellIssue)
            EditorState.selectedSubtitleCue = root.spellIssue.cue
    }
    function escapeHtml(t) {
        return String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    }

    // Reading rules (as Premiere's caption checks): a caption shown too briefly, too long, or with
    // more letters than a viewer reads in its time (about 20 per second). Empty when it reads well.
    function readingIssue(cue) {
        if (!cue)
            return ""
        const length = cue.end - cue.start
        const letters = String(cue.text || "").replace(/\*/g, "").trim().length
        if (letters === 0)
            return ""
        if (length < 0.7)
            return qsTr("Too short to read")
        if (length > 7)
            return qsTr("On screen too long")
        if (letters / length > 20)
            return qsTr("Too fast to read")
        return ""
    }

    function replaceCues(newCues) {
        EditorState.setSubtitleCues(trackIndex, clipIndex, newCues)
    }

    function cloneCues() {
        const next = []
        for (let i = 0; i < cues.length; i++)
            next.push({ start: cues[i].start, end: cues[i].end, text: cues[i].text,
                        wordEnds: (cues[i].wordEnds || []).slice(),
                        style: cues[i].style || "", place: cues[i].place || "",
                        speaker: cues[i].speaker !== undefined ? cues[i].speaker : -1 })
        return next
    }

    function wordCount(text) {
        const t = String(text).trim()
        return t.length ? t.split(/\s+/).length : 0
    }

    // Each cue keeps its word timings (the karaoke follows the voice); a text whose words no
    // longer match them loses its own, and only its own.
    function updateCue(index, patch) {
        const next = cloneCues()
        if (index >= 0 && index < next.length) {
            const before = next[index]
            if (patch.text !== undefined && patch.wordEnds === undefined
                    && wordCount(patch.text) !== wordCount(before.text))
                patch.wordEnds = []
            Object.assign(before, patch)
        }
        replaceCues(next)
    }

    function removeCue(index) {
        const next = []
        for (let i = 0; i < cues.length; i++) {
            if (i !== index)
                next.push(cues[i])
        }
        replaceCues(next)
    }

    // Insert an empty cue directly after `index`. It prefers the gap that follows the cue,
    // and when the cues are back to back it takes over the second half of `index` instead —
    // that way only the cue you clicked (+) on is ever re-timed, and everything later stays
    // in sync with the audio.
    function insertCueAfter(index) {
        if (index < 0 || index >= root.cues.length)
            return

        const list = cloneCues()
        const cur = list[index]
        const next = (index + 1 < list.length) ? list[index + 1] : null

        let newStart = cur.end
        let newEnd = next ? Math.min(next.start, cur.end + root.defaultCueDuration)
                          : cur.end + root.defaultCueDuration
        if (!next && root.clipDuration > 0)
            newEnd = Math.min(newEnd, root.clipDuration)

        if (newEnd - newStart < 0.2) {
            const mid = (cur.start + cur.end) / 2
            newStart = mid
            newEnd = cur.end
            cur.end = mid
        }

        list.splice(index + 1, 0, { start: newStart, end: newEnd, text: "", wordEnds: [] })
        replaceCues(list)
        EditorState.selectedSubtitleCue = index + 1
    }

    function selectCue(index) {
        EditorState.selectedSubtitleCue = index
        EditorState.seekToSubtitleCue(root.trackIndex, root.clipIndex, index)
    }

    function setCueEdgeToPlayhead(index, edge) {
        const t = root.localPlayhead
        if (t < 0 || index < 0 || index >= root.cues.length)
            return
        const cue = root.cues[index]
        if (edge === "start" && t >= cue.end)
            return
        if (edge === "end" && t <= cue.start)
            return
        const patch = {}
        patch[edge] = t
        root.updateCue(index, patch)
    }

    // One frame of the project: what the arrows move a cue's start or end by.
    readonly property double frameSeconds: {
        const fps = EditorState.projectFile.projectFps()
        return fps > 0 ? 1 / fps : 1 / 30
    }

    function nudgeCueEdge(index, edge, direction) {
        if (index < 0 || index >= root.cues.length)
            return
        const cue = root.cues[index]
        const minLength = root.frameSeconds
        let v = cue[edge] + direction * root.frameSeconds
        if (edge === "start")
            v = Math.max(0, Math.min(v, cue.end - minLength))
        else
            v = Math.max(cue.start + minLength, root.clipDuration > 0 ? Math.min(v, root.clipDuration) : v)
        const patch = {}
        patch[edge] = v
        root.updateCue(index, patch)
    }

    // Every caption earlier or later at once (an .srt out of sync, a video trimmed at the start),
    // with its word timings. What would go before the clip's start or past its end is trimmed there
    // (a caption reaching the end used to stop the whole move, so the button did nothing).
    function shiftAllCues(delta) {
        const list = cloneCues()
        if (!list.length || Math.abs(delta) < 1e-6)
            return
        const end = root.clipDuration > 0 ? root.clipDuration : Infinity
        const clampTime = t => Math.max(0, Math.min(end, t))
        const next = []
        for (let i = 0; i < list.length; i++) {
            const cue = list[i]
            const start = clampTime(cue.start + delta)
            const stop = clampTime(cue.end + delta)
            if (stop - start < 0.05)
                continue // pushed off the clip entirely
            next.push({ start: start, end: stop, text: cue.text, style: cue.style, place: cue.place,
                        speaker: cue.speaker,
                        wordEnds: cue.wordEnds.map(e => Math.max(start, Math.min(stop, e + delta))) })
        }
        if (next.length)
            replaceCues(next)
    }

    // The caption under the playhead in two (CapCut's Split): the words said before it stay, the
    // rest start a caption there. With word timings the cut falls between the right words.
    readonly property bool canSplitCue: {
        const i = root.selectedCueIndex
        if (i < 0 || i >= root.cues.length)
            return false
        const t = root.localPlayhead
        return t > root.cues[i].start + 0.05 && t < root.cues[i].end - 0.05
    }
    function splitCueAtPlayhead() {
        const index = root.selectedCueIndex
        if (!root.canSplitCue)
            return
        const t = root.localPlayhead
        const list = cloneCues()
        const cue = list[index]
        const words = String(cue.text).trim().split(/\s+/).filter(w => w.length)
        const timed = cue.wordEnds.length === words.length && words.length > 0
        let k = 0
        if (timed) {
            while (k < words.length && cue.wordEnds[k] <= t)
                ++k
        } else {
            k = Math.round(words.length * (t - cue.start) / (cue.end - cue.start))
        }
        if (words.length > 1)
            k = Math.max(1, Math.min(words.length - 1, k))
        // Each word with the space or line break after it, so a two-line caption keeps its break.
        const pieces = String(cue.text).trim().match(/\S+\s*/g) || []
        const first = { start: cue.start, end: t, text: pieces.slice(0, k).join("").trim(),
                        wordEnds: timed ? cue.wordEnds.slice(0, k) : [], style: cue.style, place: cue.place,
                        speaker: cue.speaker }
        const second = { start: t, end: cue.end, text: pieces.slice(k).join("").trim(),
                         wordEnds: timed ? cue.wordEnds.slice(k) : [], style: cue.style, place: cue.place,
                         speaker: cue.speaker }
        list.splice(index, 1, first, second)
        replaceCues(list)
        EditorState.selectedSubtitleCue = index + 1
    }

    // The caption and the next one become one (their words and timings kept).
    function joinWithNext(index) {
        if (index < 0 || index + 1 >= root.cues.length)
            return
        const list = cloneCues()
        const a = list[index]
        const b = list[index + 1]
        const joined = { start: a.start, end: b.end, text: (a.text + " " + b.text).trim(),
                         wordEnds: a.wordEnds.concat(b.wordEnds), style: a.style, place: a.place,
                         speaker: a.speaker }
        list.splice(index, 2, joined)
        replaceCues(list)
        EditorState.selectedSubtitleCue = index
    }

    // Add a new cue at the playhead, chaining it to its neighbours: the preceding cue's
    // end is trimmed back to the new start if it would otherwise overlap (never extended),
    // and the new cue runs until the next cue's start (or a default length when there is
    // none). This lets you add subtitles back to back.
    function addCueAtPlayhead() {
        const t = root.localPlayhead
        if (t < 0)
            return

        const list = cloneCues()

        // If a cue already begins here, just select it instead of stacking a duplicate.
        for (let i = 0; i < list.length; i++) {
            if (Math.abs(list[i].start - t) < 0.05) {
                EditorState.selectedSubtitleCue = i
                return
            }
        }

        let prevIdx = -1
        let nextStart = -1
        for (let i = 0; i < list.length; i++) {
            if (list[i].start < t && (prevIdx < 0 || list[i].start > list[prevIdx].start))
                prevIdx = i
            if (list[i].start > t && (nextStart < 0 || list[i].start < nextStart))
                nextStart = list[i].start
        }
        if (prevIdx >= 0 && list[prevIdx].end > t)
            list[prevIdx].end = t

        let newEnd
        if (nextStart >= 0)
            newEnd = nextStart
        else if (root.clipDuration > 0)
            newEnd = Math.min(t + root.defaultCueDuration, root.clipDuration)
        else
            newEnd = t + root.defaultCueDuration
        if (newEnd <= t)
            newEnd = t + 0.5

        list.push({ start: t, end: newEnd, text: "", wordEnds: [] })
        list.sort(function (a, b) { return a.start - b.start })
        replaceCues(list)

        Qt.callLater(function () {
            for (let i = 0; i < root.cues.length; i++) {
                if (Math.abs(root.cues[i].start - t) < 0.001) {
                    EditorState.selectedSubtitleCue = i
                    break
                }
            }
        })
    }

    // Both editor refreshes run from change handlers on what `selectedCue` is derived from, and a
    // derived binding is not guaranteed to have been re-evaluated by then — reading it there hands
    // back the previously selected cue. Resolve the cue from the source of truth instead.
    function currentCue() {
        const i = EditorState.selectedSubtitleCue
        return (i >= 0 && i < cues.length) ? cues[i] : null
    }

    // Refresh the fields from the model after the cue list was rebuilt elsewhere (a start/end
    // commit, a timeline-lane drag) without fighting an edit in progress.
    function syncEditor() {
        const cue = currentCue()
        if (!cueText.activeFocus)
            cueText.text = cue ? cue.text : ""
    }

    // A different cue was picked: its values replace the fields outright. Clicking a row does
    // not move focus out of the text box, so the guards in syncEditor would otherwise leave
    // the previous cue's text sitting there. Anything typed and not applied is dropped.
    function loadEditor() {
        const cue = currentCue()
        cueText.text = cue ? cue.text : ""
    }

    // While playing, the edited cue tracks the playhead — but not while the text box is being
    // typed into, since following would replace what is in it. When paused it only changes on
    // an explicit click (side list or timeline lane) or when adding a cue.
    onActiveCueIndexChanged: {
        if (EditorState.playing && !cueText.activeFocus)
            EditorState.selectedSubtitleCue = root.activeCueIndex
    }
    onCuesChanged: {
        if (root.selectedCueIndex >= root.cues.length)
            EditorState.selectedSubtitleCue = root.cues.length - 1
        syncEditor()
    }
    onSelectedCueIndexChanged: loadEditor()

    // Reset the editing selection only when a different clip is selected — not on every
    // cue edit (selectedClipData hands back a fresh object each time).
    function resetSelectionForClip() {
        root.changesKind = "" // a preview belongs to the clip it was made for
        root.spellOpen = false
        root.spellIssues = []
        root.spellIgnored = ({})
        Qt.callLater(function () {
            // loadEditor explicitly: a new clip whose active cue lands on the same index
            // leaves selectedCueIndex unchanged, so nothing else would refresh the fields.
            EditorState.selectedSubtitleCue = root.activeCueIndex
            loadEditor()
        })
    }
    onTrackIndexChanged: resetSelectionForClip()
    onClipIndexChanged: resetSelectionForClip()
    Component.onCompleted: {
        EditorState.selectedSubtitleCue = root.activeCueIndex
        loadEditor()
        // I and O (mark in / out) set the picked caption's start and end while this is open.
        const w = root.Window.window
        if (w && w.subtitleCueEditor !== undefined)
            w.subtitleCueEditor = root
    }
    Component.onDestruction: {
        const w = root.Window.window
        if (w && w.subtitleCueEditor === root)
            w.subtitleCueEditor = null
    }
    // The I / O keys: true when they went to a caption (else they mark the work area as before).
    function markCueEdge(edge) {
        if (!root.visible || root.selectedCue === null)
            return false
        root.setCueEdgeToPlayhead(root.selectedCueIndex, edge)
        return true
    }

    Connections {
        target: EditorState
        function onPlayingChanged() {
            if (EditorState.playing)
                EditorState.selectedSubtitleCue = root.activeCueIndex
        }
    }

    // ---- Header ----------------------------------------------------------------
    Column {
        id: header
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 12
        spacing: 4

        Item {
            width: parent.width
            height: titleText.implicitHeight

            Text {
                id: titleText
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                text: qsTr("Subtitles")
                color: Theme.panelForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                font.weight: Font.Medium
            }

            Text {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                text: qsTr("%1 captions").arg(root.cues.length)
                color: Theme.mutedForeground
                font.family: Theme.monoFontFamily
                font.pixelSize: Theme.fontSizeXs
            }
        }

        Grid {
            id: toolGrid
            width: parent.width
            columns: 2
            spacing: 6
            readonly property real cell: (width - spacing) / 2

            ThemedButton {
                width: toolGrid.cell
                text: qsTr("Emojis")
                variant: "secondary"
                glyph: Theme.icons.smile
                tooltip: qsTr("Add an emoji at the end of captions that mention a keyword (fuego 🔥, fiesta 🎉)")
                enabled: root.cues.length > 0
                onClicked: root.showChanges("emojis")
            }

            // Into another language (DeepL on our server): a second caption clip above, bilingual.
            ThemedButton {
                width: toolGrid.cell
                text: qsTr("Translate")
                variant: root.translateOpen ? "primary" : "secondary"
                glyph: Theme.icons.languages
                tooltip: qsTr("The captions in another language, as a second line above (bilingual)")
                enabled: root.cues.length > 0
                onClicked: root.translateOpen = !root.translateOpen
            }

            // CapCut's animated emojis over the captions that mention one (an extra of Stickers).
            ThemedButton {
                visible: root.animatedEmojis
                width: toolGrid.cell
                text: qsTr("Animated")
                variant: "secondary"
                glyph: Theme.icons.smile
                tooltip: qsTr("An animated emoji above each caption that mentions one (fuego, Dios, fiesta…)")
                enabled: root.cues.length > 0
                onClicked: EditorState.addAnimatedEmojisToSubtitles(root.trackIndex, root.clipIndex)
            }

            // The TV bleep over the hidden swear words (m*****), once captions have some.
            ThemedButton {
                visible: { void root.cues; return EditorState.subtitleHasHiddenWords(root.trackIndex, root.clipIndex) }
                width: toolGrid.cell
                text: qsTr("Bleep")
                variant: "secondary"
                glyph: Theme.icons.volumeOff
                tooltip: qsTr("A beep over each hidden swear word, with the voice muted under it")
                onClicked: EditorState.bleepSubtitleSwearWords(root.trackIndex, root.clipIndex)
            }

            ThemedButton {
                width: toolGrid.cell
                text: qsTr("Key words")
                variant: "secondary"
                glyph: Theme.icons.sparkles
                tooltip: qsTr("Highlight the key word of each caption in colour (a number, a name, what matters)")
                enabled: root.cues.length > 0
                onClicked: root.showChanges("keywords")
            }

            ThemedButton {
                width: toolGrid.cell
                text: qsTr("Clean up")
                variant: "secondary"
                glyph: Theme.icons.wand
                tooltip: qsTr("Remove hesitations (eh, mmm), capitalize each caption and apply your dictionary")
                enabled: root.cues.length > 0
                onClicked: root.showChanges("cleanup")
            }

            ThemedButton {
                width: toolGrid.cell
                text: qsTr("Find & replace")
                variant: root.replaceOpen ? "primary" : "secondary"
                glyph: Theme.icons.search
                tooltip: qsTr("Fix a word in every caption at once")
                enabled: root.cues.length > 0
                onClicked: root.replaceOpen = !root.replaceOpen
            }

            ThemedButton {
                visible: root.spellAvailable
                width: toolGrid.cell
                text: qsTr("Spelling")
                variant: root.spellOpen ? "primary" : "secondary"
                glyph: Theme.icons.check
                tooltip: qsTr("Check the spelling of every caption, one word at a time")
                enabled: root.cues.length > 0
                onClicked: {
                    if (root.spellOpen) {
                        root.spellOpen = false
                    } else {
                        root.spellIgnored = ({})
                        root.checkSpelling()
                    }
                }
            }
        }

        // The voices told apart: a colour (click for the next one) and a name for each.
        Column {
            visible: root.speakers.length > 0
            width: parent.width
            spacing: 4

            Text {
                text: qsTr("Speakers")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            Repeater {
                model: root.speakers
                Row {
                    id: speakerRow
                    required property var modelData
                    required property int index
                    width: parent.width
                    spacing: 6

                    Rectangle {
                        width: 22
                        height: 22
                        radius: 11
                        anchors.verticalCenter: parent.verticalCenter
                        color: speakerRow.modelData.color
                        border.width: 1
                        border.color: Theme.panelBorder
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: EditorState.setSubtitleSpeaker(root.trackIndex, root.clipIndex, speakerRow.index,
                                                                      "", root.nextVoiceColour(speakerRow.modelData.color))
                        }
                    }
                    ThemedTextField {
                        width: speakerRow.width - 22 - speakerRow.spacing
                        text: speakerRow.modelData.name
                        onEditingFinished: EditorState.setSubtitleSpeaker(root.trackIndex, root.clipIndex,
                                                                          speakerRow.index, text, "")
                    }
                }
            }
        }

        // Less used: the file and moving every caption, folded (minimal panel, Jorge 2026-11-01).
        ThemedButton {
            width: parent.width
            text: qsTr("File and timing")
            variant: "ghost"
            glyph: root.moreOpen ? Theme.icons.chevronUp : Theme.icons.chevronDown
            onClicked: root.moreOpen = !root.moreOpen
        }

        Column {
            visible: root.moreOpen
            width: parent.width
            spacing: 4

            // Every caption earlier or later at once: for a file out of sync with the voice.
            Row {
                id: shiftRow
                width: parent.width
                spacing: 4
                visible: root.cues.length > 0

                Text {
                    width: shiftRow.width - shiftBack.width * 2 - shiftRow.spacing * 2
                    height: shiftBack.height
                    verticalAlignment: Text.AlignVCenter
                    text: qsTr("Move all captions")
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                    elide: Text.ElideRight
                }
                IconButton {
                    id: shiftBack
                    glyph: Theme.icons.chevronLeft
                    variant: "ghost"
                    tooltip: qsTr("All captions 0.1 s earlier")
                    onClicked: root.shiftAllCues(-0.1)
                }
                IconButton {
                    glyph: Theme.icons.chevronRight
                    variant: "ghost"
                    tooltip: qsTr("All captions 0.1 s later")
                    onClicked: root.shiftAllCues(0.1)
                }
            }

            Row {
                width: parent.width
                spacing: 6

                ThemedButton {
                    width: (parent.width - parent.spacing) / 2
                    text: qsTr("Import")
                    variant: "secondary"
                    glyph: Theme.icons.upload
                    tooltip: qsTr("Replace these captions from an SRT, WebVTT or ASS file")
                    onClicked: {
                        const url = FileDialogs.openFile(
                            qsTr("Import Subtitles"),
                            [qsTr("Subtitle files (*.srt *.vtt *.ass *.ssa)"),
                             qsTr("SubRip subtitles (*.srt)"),
                             qsTr("WebVTT subtitles (*.vtt)"),
                             qsTr("SubStation Alpha subtitles (*.ass *.ssa)"),
                             qsTr("All files (*)")])
                        if (url != "")
                            EditorState.importSubtitleFileIntoClip(
                                root.trackIndex, root.clipIndex, url)
                    }
                }

                ThemedButton {
                    width: (parent.width - parent.spacing) / 2
                    text: qsTr("Export")
                    variant: "secondary"
                    glyph: Theme.icons.save
                    tooltip: qsTr("Save captions as SRT, WebVTT (.vtt) or ASS (.ass): the extension picks the format")
                    enabled: root.cues.length > 0
                    onClicked: {
                        const url = FileDialogs.saveFile(
                            qsTr("Export Subtitles"),
                            [qsTr("SubRip subtitles (*.srt)"),
                             qsTr("WebVTT subtitles (*.vtt)"),
                             qsTr("Advanced SubStation Alpha subtitles (*.ass)")],
                            (root.clip && root.clip.name) ? root.clip.name : EditorState.projectFile.projectName,
                            "srt")
                        if (url != "")
                            EditorState.exportSubtitleFile(
                                root.trackIndex, root.clipIndex, url, timelineTimesBox.checked)
                    }
                }
            }

            ThemedCheckBox {
                id: timelineTimesBox
                width: parent.width
                // On by default: the file then matches the exported video even when this clip does not
                // start at 0:00 (off, it came out of sync).
                checked: true
                text: qsTr("Timestamps from the start of the video")
                tooltip: qsTr("Offset the exported captions by this clip's start so they match the exported video")
            }
        }

        // Translate: the language, then the translated captions land above the originals.
        Rectangle {
            visible: root.translateOpen
            width: parent.width
            height: visible ? translateColumn.implicitHeight + 16 : 0
            radius: Theme.radiusMd
            color: Theme.panelAccent
            border.width: 1
            border.color: Theme.panelBorder

            Column {
                id: translateColumn
                x: 8
                y: 8
                width: parent.width - 16
                spacing: 6

                ThemedComboBox {
                    id: translateLanguageBox
                    width: parent.width
                    textRole: "label"
                    valueRole: "code"
                    model: EditorState.subtitleTranslationLanguages()
                    Component.onCompleted: currentIndex = Math.max(0, indexOfValue(translatePrefs.translateTo))
                    onActivated: translatePrefs.translateTo = currentValue
                }

                Text {
                    visible: !Account.signedIn
                    width: parent.width
                    wrapMode: Text.WordWrap
                    text: qsTr("Sign in with Google to translate captions.")
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                }

                Row {
                    width: parent.width
                    spacing: 6
                    ThemedButton {
                        width: (parent.width - parent.spacing) / 2
                        text: qsTr("Close")
                        variant: "ghost"
                        onClicked: root.translateOpen = false
                    }
                    ThemedButton {
                        width: (parent.width - parent.spacing) / 2
                        text: EditorState.subtitleTranslating ? qsTr("Translating…") : qsTr("Translate")
                        variant: "primary"
                        enabled: Account.signedIn && !EditorState.subtitleTranslating
                        onClicked: EditorState.translateSubtitles(root.trackIndex, root.clipIndex,
                                                                  translateLanguageBox.currentValue)
                    }
                }
            }
        }

        // Spelling: the flagged word in its caption, the suggestions to fix it, or Ignore.
        Rectangle {
            visible: root.spellOpen
            width: parent.width
            height: visible ? spellColumn.implicitHeight + 16 : 0
            radius: Theme.radiusMd
            color: Theme.panelAccent
            border.width: 1
            border.color: Theme.panelBorder

            Column {
                id: spellColumn
                x: 8
                y: 8
                width: parent.width - 16
                spacing: 6

                Text {
                    width: parent.width
                    wrapMode: Text.WordWrap
                    text: root.spellIssue ? qsTr("Words to check: %1").arg(root.spellIssues.length)
                                          : qsTr("No spelling mistakes found.")
                    color: Theme.panelForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                    font.weight: Font.Medium
                }

                Text {
                    visible: root.spellIssue !== null
                    width: parent.width
                    wrapMode: Text.WordWrap
                    textFormat: Text.StyledText
                    text: {
                        const issue = root.spellIssue
                        const cue = issue ? root.cues[issue.cue] : null
                        if (!cue)
                            return ""
                        const t = String(cue.text)
                        return root.escapeHtml(t.slice(0, issue.start))
                            + "<u><b>" + root.escapeHtml(issue.word) + "</b></u>"
                            + root.escapeHtml(t.slice(issue.start + issue.length))
                    }
                    color: Theme.panelForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSm
                }

                Flow {
                    visible: root.spellIssue !== null
                    width: parent.width
                    spacing: 6
                    Repeater {
                        model: root.spellIssue ? root.spellIssue.suggestions : []
                        ThemedButton {
                            required property var modelData
                            text: modelData === "" ? qsTr("Remove repeated word") : modelData
                            variant: "secondary"
                            onClicked: root.fixSpelling(modelData)
                        }
                    }
                    Text {
                        visible: root.spellIssue !== null && root.spellIssue.suggestions.length === 0
                        height: 28
                        verticalAlignment: Text.AlignVCenter
                        text: qsTr("No suggestions: fix it in the text box.")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                }

                Row {
                    width: parent.width
                    spacing: 6
                    ThemedButton {
                        width: (parent.width - parent.spacing) / 2
                        text: qsTr("Close")
                        variant: "ghost"
                        onClicked: root.spellOpen = false
                    }
                    ThemedButton {
                        width: (parent.width - parent.spacing) / 2
                        visible: root.spellIssue !== null
                        text: qsTr("Ignore")
                        variant: "secondary"
                        onClicked: root.ignoreSpelling()
                    }
                }
            }
        }

        // The preview: a few «before → after» lines, then Apply or Cancel.
        Rectangle {
            id: changesCard
            visible: root.changesKind !== ""
            width: parent.width
            height: visible ? changesColumn.implicitHeight + 16 : 0
            radius: Theme.radiusMd
            color: Theme.panelAccent
            border.width: 1
            border.color: Theme.panelBorder

            Column {
                id: changesColumn
                x: 8
                y: 8
                width: parent.width - 16
                spacing: 6

                Text {
                    width: parent.width
                    wrapMode: Text.WordWrap
                    text: root.changesList.length === 0
                          ? qsTr("Nothing to change in these captions.")
                          : qsTr("Captions that will change: %1").arg(root.changesList.length)
                    color: Theme.panelForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                    font.weight: Font.Medium
                }

                Repeater {
                    model: root.changesList.slice(0, 5)
                    delegate: Column {
                        required property var modelData
                        width: changesColumn.width
                        spacing: 1
                        Text {
                            width: parent.width
                            text: modelData.before
                            elide: Text.ElideRight
                            font.strikeout: true
                            color: Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                        Text {
                            width: parent.width
                            text: modelData.after.length ? modelData.after : qsTr("(removed)")
                            elide: Text.ElideRight
                            color: Theme.panelForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                    }
                }

                Text {
                    visible: root.changesList.length > 5
                    text: qsTr("+ %1 more").arg(root.changesList.length - 5)
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                }

                Row {
                    width: parent.width
                    spacing: 6
                    ThemedButton {
                        width: (parent.width - parent.spacing) / 2
                        text: qsTr("Cancel")
                        variant: "ghost"
                        onClicked: root.changesKind = ""
                    }
                    ThemedButton {
                        width: (parent.width - parent.spacing) / 2
                        text: qsTr("Apply")
                        variant: "primary"
                        enabled: root.changesList.length > 0
                        onClicked: root.applyChanges()
                    }
                }
            }
        }

        Column {
            width: parent.width
            spacing: 4
            visible: root.replaceOpen

            ThemedTextField {
                id: findField
                width: parent.width
                placeholderText: qsTr("Find (e.g. jesus)")
                font.family: Theme.fontFamily
            }

            ThemedTextField {
                id: replaceField
                width: parent.width
                placeholderText: qsTr("Replace with (e.g. Jesús)")
                font.family: Theme.fontFamily
                onAccepted: replaceAllButton.clicked()
            }

            ThemedCheckBox {
                id: rememberBox
                width: parent.width
                checked: true
                text: qsTr("Always fix it in new subtitles")
                tooltip: qsTr("Adds it to your subtitle dictionary")
            }

            Row {
                width: parent.width
                spacing: 6

                ThemedButton {
                    id: replaceAllButton
                    width: (parent.width - parent.spacing) / 2
                    text: qsTr("Replace all")
                    variant: "primary"
                    enabled: findField.text.trim().length > 0
                    onClicked: {
                        EditorState.replaceInSubtitles(root.trackIndex, root.clipIndex,
                                                       findField.text, replaceField.text, rememberBox.checked)
                        findField.text = ""
                        replaceField.text = ""
                    }
                }

                ThemedButton {
                    width: (parent.width - parent.spacing) / 2
                    text: qsTr("Dictionary…")
                    variant: "ghost"
                    tooltip: qsTr("Words fixed automatically in every new subtitle")
                    onClicked: dictionaryDialog.openDictionary()
                }
            }
        }
    }

    property bool replaceOpen: false
    property bool moreOpen: false
    property bool translateOpen: false
    Settings {
        id: translatePrefs
        category: "subtitles"
        property string translateTo: "en"
    }
    readonly property bool animatedEmojis: EditorState.animatedEmojisAvailable()
    readonly property var cueStyleChoices: EditorState.subtitleStyleChoices()
    readonly property var speakers: (clip && clip.subtitleSpeakers) ? clip.subtitleSpeakers : []
    function speakerOf(cue) {
        const i = cue && cue.speaker !== undefined ? cue.speaker : -1
        return i >= 0 && i < root.speakers.length ? root.speakers[i] : null
    }
    readonly property var voiceColours: ["#ffffff", "#ffd640", "#60cdff", "#ff80ab", "#8ce678", "#ffa050"]
    function nextVoiceColour(current) {
        const now = String(current).toLowerCase()
        let i = root.voiceColours.findIndex(c => now.indexOf(c.substring(1)) >= 0)
        return root.voiceColours[(i + 1) % root.voiceColours.length]
    }

    ThemedDialog {
        id: dictionaryDialog
        title: qsTr("Subtitle dictionary")
        acceptText: qsTr("Save")
        preferredWidth: Theme.dialogWidthMd

        property var entries: []

        function openDictionary() {
            entries = EditorState.subtitleDictionary()
            open()
        }

        onAccepted: EditorState.setSubtitleDictionary(entries)

        contentItem: Column {
            spacing: Theme.spacingMd

            Text {
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("New subtitles fix these words on their own: names, places, words the speech recognition gets wrong.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            Text {
                visible: dictionaryDialog.entries.length === 0
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("Empty for now. Use Find & replace with “Always fix it” to add words.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
            }

            ListView {
                width: parent.width
                height: Math.min(260, contentHeight)
                clip: true
                model: dictionaryDialog.entries
                ScrollBar.vertical: AppScrollBar {}
                delegate: Item {
                    required property var modelData
                    required property int index
                    width: ListView.view.width
                    height: 30

                    Text {
                        anchors.left: parent.left
                        anchors.right: removeButton.left
                        anchors.verticalCenter: parent.verticalCenter
                        elide: Text.ElideRight
                        text: modelData.find + "  →  " + modelData.replace
                        color: Theme.panelForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSm
                    }

                    IconButton {
                        id: removeButton
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: Theme.icons.trash
                        variant: "ghost"
                        tooltip: qsTr("Remove")
                        onClicked: {
                            const next = dictionaryDialog.entries.slice()
                            next.splice(index, 1)
                            dictionaryDialog.entries = next
                        }
                    }
                }
            }

            Row {
                width: parent.width
                spacing: 6

                ThemedTextField {
                    id: newFind
                    width: (parent.width - addButton.width - parent.spacing * 2) / 2
                    placeholderText: qsTr("Wrong")
                    font.family: Theme.fontFamily
                }

                ThemedTextField {
                    id: newReplace
                    width: (parent.width - addButton.width - parent.spacing * 2) / 2
                    placeholderText: qsTr("Right")
                    font.family: Theme.fontFamily
                    onAccepted: addButton.clicked()
                }

                IconButton {
                    id: addButton
                    anchors.verticalCenter: parent.verticalCenter
                    glyph: Theme.icons.plus
                    variant: "ghost"
                    tooltip: qsTr("Add")
                    enabled: newFind.text.trim().length > 0
                    onClicked: {
                        dictionaryDialog.entries = dictionaryDialog.entries.concat(
                            [{ "find": newFind.text.trim(), "replace": newReplace.text }])
                        newFind.text = ""
                        newReplace.text = ""
                    }
                }
            }
        }
    }

    // ---- Lyrics list (compact, keeps neighbours in view) -----------------------
    ListView {
        id: listView
        reuseItems: true
        anchors.top: header.bottom
        anchors.topMargin: 8
        anchors.bottom: editorPanel.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: 6
        anchors.rightMargin: 6
        clip: true
        spacing: 2
        model: root.cues

        currentIndex: root.activeCueIndex
        highlightFollowsCurrentItem: true
        highlightRangeMode: ListView.ApplyRange
        preferredHighlightBegin: height * 0.4
        preferredHighlightEnd: height * 0.6
        highlightMoveDuration: 320
        highlightMoveVelocity: -1
        highlight: Item { }

        ScrollBar.vertical: AppScrollBar { }

        delegate: Item {
            id: cueDelegate
            required property int index
            required property var modelData
            readonly property bool isActive: index === root.activeCueIndex
            readonly property bool isSelected: index === root.selectedCueIndex

            width: ListView.view ? ListView.view.width : 0
            height: card.height + (isSelected ? addRow.height : 0)

            Rectangle {
                id: card
                width: parent.width
                height: lineCol.implicitHeight + 14
                radius: Theme.radiusMd
                color: cueDelegate.isSelected ? Theme.panelAccent : (rowHover.containsMouse ? Theme.panelAccent : "transparent")
                border.width: (cueDelegate.isSelected || cueDelegate.isActive || rowHover.containsMouse) ? 1 : 0
                border.color: cueDelegate.isActive ? Theme.clipSubtitle : (cueDelegate.isSelected ? Theme.panelBorder : (rowHover.containsMouse ? Theme.panelBorder : "transparent"))

                Behavior on color { ColorAnimation { duration: Theme.durationFast } }
                Behavior on border.color { ColorAnimation { duration: Theme.durationFast } }

                MouseArea {
                    id: rowHover
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        root.selectCue(cueDelegate.index)
                        if (root.compactEdit)
                            root.cueEditRequested(cueDelegate.index)
                    }
                }

                Column {
                    id: lineCol
                    x: 12
                    y: 7
                    // The bin's slot is reserved even while it is hidden, so the wrapped
                    // caption text doesn't reflow as the pointer moves down the list.
                    width: parent.width - 24 - deleteButton.width
                    spacing: 2

                    Row {
                        spacing: 8
                        // Who says it, in that voice's colour.
                        Text {
                            readonly property var who: root.speakerOf(cueDelegate.modelData)
                            visible: who !== null
                            text: who ? who.name : ""
                            color: who ? who.color : Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                            font.weight: Font.Medium
                        }
                        Text {
                            text: root.formatCueTime(cueDelegate.modelData.start) + "  →  "
                                  + root.formatCueTime(cueDelegate.modelData.end)
                            color: Theme.mutedForeground
                            font.family: Theme.monoFontFamily
                            font.pixelSize: Theme.fontSizeXs
                            opacity: (cueDelegate.isActive || cueDelegate.isSelected) ? 0.95 : (rowHover.containsMouse ? 0.85 : 0.65)
                            Behavior on opacity { NumberAnimation { duration: 150 } }
                        }
                        // A quiet word when the caption does not read well (see readingIssue).
                        Text {
                            readonly property string issue: root.readingIssue(cueDelegate.modelData)
                            visible: issue.length > 0
                            text: "• " + issue
                            color: Theme.warning
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                    }

                    Text {
                        width: parent.width
                        wrapMode: Text.WordWrap
                        text: (cueDelegate.modelData.text && cueDelegate.modelData.text.length)
                              ? cueDelegate.modelData.text : qsTr("(empty)")
                        font.family: Theme.fontFamily
                        font.pixelSize: cueDelegate.isActive ? Theme.fontSizeBase : Theme.fontSizeSm
                        font.weight: cueDelegate.isActive ? Font.DemiBold : Font.Normal
                        font.italic: !(cueDelegate.modelData.text && cueDelegate.modelData.text.length)
                        color: cueDelegate.isActive ? Theme.clipSubtitle
                               : (cueDelegate.isSelected || rowHover.containsMouse ? Theme.panelForeground : Theme.foreground)
                        opacity: (cueDelegate.isActive || cueDelegate.isSelected) ? 1.0 : (rowHover.containsMouse ? 0.95 : 0.82)
                        Behavior on opacity { NumberAnimation { duration: 200 } }
                        Behavior on color { ColorAnimation { duration: 200 } }
                    }
                }

                IconButton {
                    id: deleteButton
                    anchors.right: parent.right
                    anchors.rightMargin: 6
                    anchors.verticalCenter: parent.verticalCenter
                    glyph: Theme.icons.trash
                    variant: "ghost"
                    iconSize: Theme.iconSizeSm
                    tooltip: qsTr("Delete this subtitle")
                    opacity: (rowHover.containsMouse || cueDelegate.isSelected || visualFocus
                              || Theme.touchInput) ? 1 : 0
                    enabled: opacity > 0
                    onClicked: root.removeCue(cueDelegate.index)

                    Behavior on opacity { NumberAnimation { duration: Theme.durationFast } }
                }
            }

            // Insertion point for the cue that follows the one being edited.
            Item {
                id: addRow
                anchors.top: card.bottom
                width: parent.width
                height: 30
                visible: cueDelegate.isSelected

                IconButton {
                    anchors.centerIn: parent
                    glyph: Theme.icons.plus
                    variant: "ghost"
                    iconSize: Theme.iconSizeSm
                    tooltip: qsTr("Add a subtitle after this one")
                    onClicked: root.insertCueAfter(cueDelegate.index)
                }
            }
        }

        // Empty state
        Column {
            anchors.centerIn: parent
            width: Math.min(220, parent.width - 24)
            spacing: 10
            visible: root.cues.length === 0

            IconGlyph {
                anchors.horizontalCenter: parent.horizontalCenter
                glyph: Theme.icons.captions
                iconSize: 24
                iconColor: Theme.mutedForeground
            }
            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                text: qsTr("No subtitles yet. Move to a time inside this clip and add one below.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
        }
    }

    // ---- Editor + add panel (capped so the cue list keeps space; scrolls when short)
    Rectangle {
        id: editorPanel
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        readonly property real naturalHeight: panelCol.implicitHeight + 24
        readonly property real minListHeight: 80
        readonly property real minEditorHeight: 72
        readonly property real headerBlock: header.height + header.anchors.topMargin
                                           + listView.anchors.topMargin
        height: Math.min(naturalHeight,
                         Math.max(minEditorHeight,
                                  parent.height - headerBlock - minListHeight))
        color: Theme.panelBackground

        Rectangle {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 1
            color: Theme.panelBorder
        }

        Flickable {
            id: editorFlick
            anchors.fill: parent
            anchors.margins: 12
            contentWidth: width
            contentHeight: panelCol.implicitHeight
            clip: true
            boundsBehavior: Flickable.StopAtBounds
            interactive: contentHeight > height
            ScrollBar.vertical: AppScrollBar {
                policy: editorFlick.contentHeight > editorFlick.height
                        ? ScrollBar.AlwaysOn : ScrollBar.AsNeeded
            }

            Column {
                id: panelCol
                width: parent.width
                spacing: 8

                // Editor for the selected cue.
                Column {
                    width: parent.width
                    spacing: 8
                    visible: root.selectedCue !== null && !root.compactEdit

                    Text {
                        width: parent.width
                        wrapMode: Text.WordWrap
                        text: qsTr("Tip: write a word between asterisks, like *faith*, to highlight it in colour.")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }

                    Row {
                        width: parent.width
                        spacing: 6

                        ThemedTextArea {
                            id: cueText
                            width: parent.width - applyButton.width - parent.spacing
                            height: 56
                            placeholderText: qsTr("Type subtitle…")
                            onEditingFinished: {
                                if (root.selectedCueIndex >= 0)
                                    root.updateCue(root.selectedCueIndex, { text: text })
                            }
                        }

                        // Explicit "apply text" affordance (separate from adding a cue).
                        Rectangle {
                            id: applyButton
                            width: 40
                            height: 56
                            radius: Theme.radiusSm
                            readonly property bool dirty: root.selectedCue !== null
                                                          && cueText.text !== (root.selectedCue ? root.selectedCue.text : "")
                            color: applyMouse.containsMouse ? Qt.lighter(Theme.primary, 1.08) : Theme.primary
                            opacity: (dirty || applyMouse.containsMouse) ? 1 : 0.5

                            // Was a raw "✓" glyph while every other button in the app
                            // uses IconGlyph + Theme.icons.
                            IconGlyph {
                                anchors.centerIn: parent
                                glyph: Theme.icons.check
                                iconSize: Theme.iconSizeBase
                                iconColor: Theme.primaryForeground
                            }

                            MouseArea {
                                id: applyMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (root.selectedCueIndex >= 0)
                                        root.updateCue(root.selectedCueIndex, { text: cueText.text })
                                }
                            }

                            ThemedToolTip {
                                visible: applyMouse.containsMouse
                                text: qsTr("Apply text to this subtitle")
                            }
                        }
                    }

                    // Start and end, each on its own line: the arrows move it a frame, the last button
                    // puts it at the playhead. Typing the time still works.
                    Repeater {
                        model: [{ edge: "start", label: qsTr("Start"), glyph: Theme.icons.setStart,
                                  tip: qsTr("Set start to current time") + " (I)" },
                                { edge: "end", label: qsTr("End"), glyph: Theme.icons.setEnd,
                                  tip: qsTr("Set end to current time") + " (O)" }]
                        delegate: Row {
                            id: edgeRow
                            required property var modelData
                            width: parent.width
                            spacing: 4

                            Text {
                                width: 44
                                height: edgeField.height
                                verticalAlignment: Text.AlignVCenter
                                text: edgeRow.modelData.label
                                color: Theme.mutedForeground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeXs
                                elide: Text.ElideRight
                            }
                            IconButton {
                                id: edgeBack
                                glyph: Theme.icons.chevronLeft
                                variant: "ghost"
                                enabled: root.selectedCueIndex >= 0
                                tooltip: qsTr("One frame earlier")
                                onClicked: root.nudgeCueEdge(root.selectedCueIndex, edgeRow.modelData.edge, -1)
                            }
                            ThemedTextField {
                                id: edgeField
                                width: edgeRow.width - 44 - edgeBack.width * 3 - edgeRow.spacing * 4
                                horizontalAlignment: Text.AlignHCenter
                                text: {
                                    void root.cues
                                    const cue = root.selectedCue
                                    return cue ? root.formatCueTime(cue[edgeRow.modelData.edge]) : ""
                                }
                                onEditingFinished: {
                                    const v = root.parseCueTime(text)
                                    if (!isNaN(v) && root.selectedCueIndex >= 0) {
                                        const patch = {}
                                        patch[edgeRow.modelData.edge] = v
                                        root.updateCue(root.selectedCueIndex, patch)
                                    }
                                }
                            }
                            IconButton {
                                glyph: Theme.icons.chevronRight
                                variant: "ghost"
                                enabled: root.selectedCueIndex >= 0
                                tooltip: qsTr("One frame later")
                                onClicked: root.nudgeCueEdge(root.selectedCueIndex, edgeRow.modelData.edge, 1)
                            }
                            IconButton {
                                glyph: edgeRow.modelData.glyph
                                variant: "ghost"
                                enabled: root.localPlayhead >= 0 && root.selectedCueIndex >= 0
                                tooltip: edgeRow.modelData.tip
                                onClicked: root.setCueEdgeToPlayhead(root.selectedCueIndex, edgeRow.modelData.edge)
                            }
                        }
                    }

                    // What can be done to this caption, in one quiet row.
                    Row {
                        id: cueActions
                        width: parent.width
                        spacing: 6
                        readonly property real third: (width - spacing * 2) / 3

                        ThemedButton {
                            width: cueActions.third
                            text: qsTr("Split")
                            variant: "ghost"
                            glyph: Theme.icons.scissors
                            enabled: root.canSplitCue
                            tooltip: qsTr("Split this caption at the playhead")
                            onClicked: root.splitCueAtPlayhead()
                        }
                        ThemedButton {
                            width: cueActions.third
                            text: qsTr("Join")
                            variant: "ghost"
                            glyph: Theme.icons.link
                            enabled: root.selectedCueIndex >= 0 && root.selectedCueIndex + 1 < root.cues.length
                            tooltip: qsTr("Join this caption with the next one")
                            onClicked: root.joinWithNext(root.selectedCueIndex)
                        }
                        ThemedButton {
                            width: cueActions.third
                            text: qsTr("Delete")
                            variant: "ghost"
                            glyph: Theme.icons.trash
                            enabled: root.selectedCueIndex >= 0
                            tooltip: qsTr("Delete this caption")
                            onClicked: root.removeCue(root.selectedCueIndex)
                        }
                    }

                    // Just this caption's look and place (CapCut lets one line stand out).
                    ThemedComboBox {
                        id: cueStyleBox
                        width: parent.width
                        enabled: root.selectedCue !== null
                        textRole: "label"
                        valueRole: "id"
                        model: [{ id: "", label: qsTr("Style: same as the clip") }].concat(root.cueStyleChoices)
                        currentIndex: {
                            const id = root.selectedCue ? (root.selectedCue.style || "") : ""
                            return Math.max(0, indexOfValue(id))
                        }
                        onActivated: root.updateCue(root.selectedCueIndex, { style: currentValue })
                    }

                    Row {
                        id: cuePlaceRow
                        width: parent.width
                        spacing: 6
                        readonly property real third: (width - spacing * 2) / 3
                        Repeater {
                            model: [{ id: "", label: qsTr("Like the clip") }, { id: "top", label: qsTr("Top") },
                                    { id: "middle", label: qsTr("Middle") }]
                            ThemedButton {
                                required property var modelData
                                width: cuePlaceRow.third
                                text: modelData.label
                                enabled: root.selectedCue !== null
                                variant: root.selectedCue && (root.selectedCue.place || "") === modelData.id
                                         ? "primary" : "ghost"
                                tooltip: qsTr("Where this caption sits on screen")
                                onClicked: root.updateCue(root.selectedCueIndex, { place: modelData.id })
                            }
                        }
                    }

                    Rectangle {
                        width: parent.width
                        height: 1
                        color: Theme.panelBorder
                        opacity: 0.6
                    }
                }

                Text {
                    width: parent.width
                    text: root.localPlayhead >= 0
                          ? qsTr("At %1").arg(root.formatCueTime(root.localPlayhead))
                          : qsTr("Move to a time inside this clip to add a subtitle")
                    color: Theme.mutedForeground
                    font.family: Theme.monoFontFamily
                    font.pixelSize: Theme.fontSizeXs
                }

                ThemedButton {
                    width: parent.width
                    variant: "primary"
                    glyph: Theme.icons.plus
                    enabled: root.localPlayhead >= 0
                    text: qsTr("Add subtitle at current time")
                    onClicked: root.addCueAtPlayhead()
                }
            }
        }
    }
}
