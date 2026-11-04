import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift
import ".."

Item {
    id: root

    property int clipDataRevision: 0
    readonly property var clipData: {
        void clipDataRevision
        return EditorState.selectedClipData
    }
    readonly property bool hasSelection: !!clipData && Object.keys(clipData).length > 0
    readonly property string clipKind: hasSelection ? (clipData.kind || "") : ""
    // Read straight from a media file: stream choice, denoise and transcription need one.
    readonly property bool fileAudio: (clipKind === "audio" || clipKind === "video") && !clipData.sequenceId
    readonly property var propVolume: { "key": "volume", "label": qsTr("Volume"), "def": 1.0, "decimals": 2 }
    // CapCut's two pages: the basics, and the voice changer's grid.
    property string page: "basic"
    // Only a clip with sound has the voice changer's page.
    readonly property var pages: hasSound ? [
        { "id": "basic", "label": qsTr("Basic") },
        { "id": "voice", "label": qsTr("Voice changer") }
    ] : []
    readonly property bool hasSound: clipKind === "audio" || clipKind === "video"
    readonly property real clipLength: hasSelection && clipData.duration !== undefined ? clipData.duration : 0

    height: audioTabColumn.height
    implicitHeight: audioTabColumn.height

    function refreshFields() {}

    Connections {
        target: EditorState
        function onSelectionChanged() { root.clipDataRevision++ }
        function onSelectedClipDataChanged() { root.clipDataRevision++ }
        function onTracksChanged() { root.clipDataRevision++ }
    }

    Column {
        id: audioTabColumn
        width: root.width
        spacing: Theme.spacingXl

        Row {
            id: audioPageRow
            width: parent.width
            spacing: Theme.spacingSm
            visible: root.hasSound

            Repeater {
                model: root.pages
                delegate: ThemedToggleButton {
                    required property var modelData
                    width: (audioPageRow.width - audioPageRow.spacing) / 2
                    text: modelData.label
                    checked: root.page === modelData.id
                    onClicked: root.page = modelData.id
                }
            }
        }

        VoiceChanger {
            width: parent.width
            visible: root.hasSound && root.page === "voice"
        }

        Column {
        id: basicColumn
        width: parent.width
        spacing: Theme.spacingXl
        visible: !root.hasSound || root.page === "basic"

        PropertyKeyframeRow {
            width: root.width
            propDef: root.propVolume
            keyframeList: (root.clipData.keyframes && root.clipData.keyframes.volume && root.clipData.keyframes.volume.points) || []
            useSlider: true
            sliderFrom: 0
            sliderTo: 2
            percent: true
            decibels: true
        }

        // ----- Fades on the sound ------------------------------------------
        Repeater {
            model: [
                { "key": "audioFadeIn", "label": qsTr("Fade in") },
                { "key": "audioFadeOut", "label": qsTr("Fade out") }
            ]
            delegate: Column {
                id: fadeRow
                required property var modelData
                width: basicColumn.width
                spacing: Theme.spacingXs
                visible: root.hasSound
                readonly property real seconds: {
                    void root.clipDataRevision
                    return root.hasSelection && root.clipData[modelData.key] !== undefined ? root.clipData[modelData.key] : 0
                }

                Row {
                    width: parent.width
                    Text {
                        width: parent.width / 2
                        text: fadeRow.modelData.label
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                    Text {
                        width: parent.width / 2
                        horizontalAlignment: Text.AlignRight
                        text: (fadeSlider.pressed ? fadeSlider.value : fadeRow.seconds).toFixed(1) + " s"
                        color: Theme.panelForeground
                        font.family: Theme.monoFontFamily
                        font.pixelSize: Theme.fontSizeSm
                    }
                }

                ThemedSlider {
                    id: fadeSlider
                    width: parent.width
                    label: fadeRow.modelData.label
                    from: 0
                    to: Math.max(0.1, Math.min(10, root.clipLength / 2))
                    stepSize: 0.1
                    Binding on value {
                        when: !fadeSlider.pressed
                        restoreMode: Binding.RestoreNone
                        value: fadeRow.seconds
                    }
                    onPressedChanged: {
                        if (pressed)
                            return
                        const fadeIn = fadeRow.modelData.key === "audioFadeIn" ? value : (root.clipData.audioFadeIn || 0)
                        const fadeOut = fadeRow.modelData.key === "audioFadeOut" ? value : (root.clipData.audioFadeOut || 0)
                        EditorState.setClipAudioFade(EditorState.selectedTrack, EditorState.selectedClip, fadeIn, fadeOut)
                    }
                }
            }
        }

        // ----- A voice the app spoke: its script, to change and speak again (0.30) -----
        Column {
            readonly property string script: {
                void EditorState.tracksRevision
                return root.hasSelection ? EditorState.tts.clipScript(EditorState.selectedTrack, EditorState.selectedClip) : ""
            }
            width: parent.width
            spacing: Theme.spacingXs
            visible: script.length > 0

            Text {
                width: parent.width
                text: qsTr("Voice from text")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
            Text {
                width: parent.width
                wrapMode: Text.WordWrap
                maximumLineCount: 2
                elide: Text.ElideRight
                text: "“" + parent.script + "”"
                color: Theme.panelForeground
                opacity: 0.8
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
            ThemedButton {
                width: parent.width
                text: qsTr("Edit script…")
                glyph: Theme.icons.pencil
                enabled: !EditorState.tts.running
                tooltip: qsTr("Change the text or the voice and speak it again, in place of this audio")
                onClicked: {
                    const track = EditorState.selectedTrack
                    const clip = EditorState.selectedClip
                    discardTakeDialog.ask(() => EditorState.tts.editClipScript(track, clip))
                }
            }

            // A take not added yet would be thrown away by starting another (0.30 tests E56): asked first.
            ThemedDialog {
                id: discardTakeDialog
                property var proceed: null
                title: qsTr("Discard the voice you made?")
                preferredWidth: 380
                acceptText: qsTr("Discard and go on")
                acceptVariant: "destructive"
                onAccepted: { if (proceed) proceed(); proceed = null }
                onRejected: proceed = null
                contentItem: ThemedLabel {
                    width: discardTakeDialog.availableWidth
                    wrapMode: Text.WordWrap
                    text: qsTr("The Voice panel has a take that is not on the timeline yet. Add it first with «Add to timeline», or discard it to start this one.")
                }
                function ask(action) {
                    if (!EditorState.tts.hasTake) {
                        action()
                        return
                    }
                    proceed = action
                    open()
                }
            }
            ThemedButton {
                width: parent.width
                text: qsTr("Lower the music under this voice")
                glyph: Theme.icons.music
                variant: "secondary"
                onClicked: EditorState.tts.duckMusicUnder(EditorState.selectedTrack, EditorState.selectedClip)
            }
            ThemedButton {
                width: parent.width
                text: qsTr("Save the voice as a file…")
                glyph: Theme.icons.download
                variant: "ghost"
                onClicked: {
                    // MP3 first, as people share a voice; WAV and FLAC too (0.30 tests E59).
                    const url = FileDialogs.saveFile(qsTr("Save the voice"),
                                                     [qsTr("MP3 audio (*.mp3)"), qsTr("WAV audio (*.wav)"),
                                                      qsTr("FLAC audio (*.flac)")],
                                                     qsTr("voice"), "mp3")
                    if (url == "")
                        return
                    if (EditorState.tts.saveClipVoice(EditorState.selectedTrack, EditorState.selectedClip, url))
                        AppController.setLastMessage(qsTr("Voice saved"), "success")
                    else
                        AppController.setLastMessage(qsTr("Could not save the voice"), "error")
                }
            }
        }

        // ----- Normalize loudness -----------------------------------------
        Column {
            width: parent.width
            spacing: Theme.spacingXs
            visible: root.fileAudio

            Text {
                width: parent.width
                text: qsTr("Normalize loudness")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
            Text {
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("Sets the clip's volume so it sounds as loud as social media expects (−14 LUFS).")
                color: Theme.mutedForeground
                opacity: 0.8
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
            ThemedButton {
                width: parent.width
                text: EditorState.normalizing ? qsTr("Measuring…") : qsTr("Normalize to −14 LUFS")
                enabled: !EditorState.normalizing
                onClicked: EditorState.normalizeClipLoudness(EditorState.selectedTrack, EditorState.selectedClip, -14)
            }
        }

        // ----- Enhance voice ----------------------------------------------
        Column {
            width: parent.width
            spacing: Theme.spacingXs
            visible: root.fileAudio

            Text {
                width: parent.width
                text: qsTr("Enhance voice")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
            ThemedButton {
                width: parent.width
                text: qsTr("Enhance voice")
                tooltip: qsTr("Clearer, fuller speech: less room echo and background noise")
                onClicked: EditorState.enhanceVoice(EditorState.selectedTrack, EditorState.selectedClip)
            }
        }

        // ----- Fill channel -------------------------------------------------
        Column {
            id: fillSection
            width: parent.width
            spacing: Theme.spacingXs
            visible: root.hasSound
            readonly property int mode: {
                void root.clipDataRevision
                if (EditorState.selectedTrack < 0 || EditorState.selectedClip < 0)
                    return -1
                return EditorState.channelFillOf(EditorState.selectedTrack, EditorState.selectedClip)
            }

            ThemedCheckBox {
                width: parent.width
                text: qsTr("Fill channel")
                checked: fillSection.mode >= 0
                onToggled: EditorState.setChannelFill(EditorState.selectedTrack, EditorState.selectedClip,
                                                      checked ? fillSource.currentIndex : -1)
            }
            Text {
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("For recordings heard on one side only: copies that side to both.")
                color: Theme.mutedForeground
                opacity: 0.8
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
            ThemedComboBox {
                id: fillSource
                width: parent.width
                enabled: fillSection.mode >= 0
                // Indexes are the processor's modes: 0 left, 1 right, 2 automatic.
                model: [qsTr("Left to both"), qsTr("Right to both"), qsTr("Automatic")]
                currentIndex: fillSection.mode >= 0 ? fillSection.mode : 2
                onActivated: index => EditorState.setChannelFill(EditorState.selectedTrack, EditorState.selectedClip, index)
            }
        }

        Rectangle {
            visible: root.hasSound
            width: parent.width
            height: 1
            color: Theme.panelBorder
            opacity: 0.5
        }

        // ----- Pan (stereo balance) ----------------------------------------
        Column {
            id: panSection
            width: parent.width
            spacing: Theme.spacingSm

            readonly property real panValue: {
                void root.clipDataRevision
                void EditorState.playheadSeconds
                if (!root.clipData || root.clipData.pan === undefined)
                    return 0.0
                return EditorState.propertyValueAt(EditorState.selectedTrack, EditorState.selectedClip, "pan",
                                                   EditorState.playheadSeconds, root.clipData.pan)
            }

            // Keyframed like the volume (0.25): the diamond keys the balance at the playhead, so
            // the sound can travel from one side to the other.
            PropertyKeyframeRow {
                width: parent.width
                propDef: ({ "key": "pan", "label": qsTr("Pan"), "def": 0.0, "decimals": 2 })
                keyframeList: (root.clipData.keyframes && root.clipData.keyframes.pan
                               && root.clipData.keyframes.pan.points) || []
                useSlider: true
                sliderFrom: -1
                sliderTo: 1
                percent: true
            }

            ThemedButton {
                text: qsTr("Centre")
                enabled: Math.abs(panSection.panValue) >= 0.005
                onClicked: {
                    const keys = root.clipData.keyframes && root.clipData.keyframes.pan
                                 && root.clipData.keyframes.pan.points
                    if (keys && keys.length > 0)
                        EditorState.setClipKeyframe(EditorState.selectedTrack, EditorState.selectedClip,
                                                    "pan", EditorState.playheadSeconds, 0)
                    else
                        EditorState.setClipPan(EditorState.selectedTrack, EditorState.selectedClip, 0)
                }
            }
        }

        // ----- Audio Track Selection (Multi-Track) -------------------------
        Column {
            id: audioTrackSection
            width: parent.width
            spacing: Theme.spacingSm
            visible: root.fileAudio && audioTrackModel.length > 1

            property var audioTrackModel: {
                void root.clipDataRevision
                if (EditorState.selectedTrack < 0 || EditorState.selectedClip < 0)
                    return []
                return EditorState.clipAudioStreams(EditorState.selectedTrack, EditorState.selectedClip)
            }

            Text {
                width: parent.width
                text: qsTr("Audio track")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            ThemedComboBox {
                id: audioStreamSelector
                width: parent.width
                textRole: "label"
                valueRole: "index"
                model: audioTrackSection.audioTrackModel
                currentIndex: {
                    const currentIdx = (root.clipData && root.clipData.audioStreamIndex !== undefined)
                                       ? root.clipData.audioStreamIndex : 0
                    for (let i = 0; i < audioTrackSection.audioTrackModel.length; ++i) {
                        if (audioTrackSection.audioTrackModel[i].index === currentIdx)
                            return i
                    }
                    return 0
                }
                onActivated: {
                    EditorState.setClipAudioStreamIndex(
                        EditorState.selectedTrack, EditorState.selectedClip, currentValue)
                }
            }

            ThemedButton {
                visible: (root.clipKind === "video" || root.clipKind === "composite")
                         && EditorState.separateAudioAvailable
                width: parent.width
                text: qsTr("Extract all audio tracks")
                onClicked: {
                    EditorState.separateAllAudioTracks(EditorState.selectedTrack, EditorState.selectedClip)
                }
            }
        }

        Rectangle {
            visible: root.fileAudio
            width: parent.width
            height: 1
            color: Theme.panelBorder
            opacity: 0.5
        }

        // ----- Noise removal ---------------------------------------------
        Column {
            id: denoiseSection
            width: parent.width
            spacing: Theme.spacingSm
            visible: root.fileAudio

            // Whether the model is on disk is a one-shot filesystem answer, not a
            // binding, hence the reset below when an addon of this kind appears.
            // The runtime that runs it is a second, separate addon.
            property bool denoiseReady: EditorState.denoise.available()
            property bool runtimeReady: Addons.runtimeAvailable()

            Connections {
                target: Addons
                function onKindChanged(kind) {
                    if (kind === "denoise-model")
                        denoiseSection.denoiseReady = EditorState.denoise.available()
                    else if (kind === "onnxruntime")
                        denoiseSection.runtimeReady = Addons.runtimeAvailable()
                }
            }

            Text {
                width: parent.width
                text: qsTr("Noise")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            ThemedButton {
                visible: denoiseSection.denoiseReady && denoiseSection.runtimeReady
                width: parent.width
                text: qsTr("Remove noise…")
                enabled: !EditorState.denoise.running
                onClicked: {
                    const data = EditorState.selectedClipData
                    root.Window.window.openDenoise(
                        EditorState.selectedTrack, EditorState.selectedClip,
                        data.duration !== undefined ? data.duration : 0)
                }
            }

            ThemedButton {
                visible: !denoiseSection.denoiseReady || !denoiseSection.runtimeReady
                width: parent.width
                text: denoiseSection.runtimeReady
                      ? qsTr("Download noise removal (about 9 MB)")
                      : qsTr("Install AI engine first")
                variant: "primary"
                onClicked: root.Window.window.openAddonManager(
                    denoiseSection.runtimeReady ? "denoise-model" : "onnxruntime")
            }
        }

        Rectangle {
            visible: root.fileAudio
            width: parent.width
            height: 1
            color: Theme.panelBorder
            opacity: 0.5
        }

        // One place to create captions (Assets › Subtitles: language, length, style, cleanup): this
        // used to repeat part of it with fewer choices.
        ThemedButton {
            visible: root.fileAudio
            width: parent.width
            text: qsTr("Create captions…")
            variant: "secondary"
            glyph: Theme.icons.captions
            tooltip: qsTr("Open Subtitles to create captions from this clip's speech")
            onClicked: root.Window.window.showAssetsTab("subtitles")
        }

        // Descript's editing: strike words out of the transcript and the video loses them.
        ThemedButton {
            visible: root.fileAudio
            width: parent.width
            text: qsTr("Edit by text…")
            variant: "secondary"
            glyph: Theme.icons.scissors
            tooltip: qsTr("See what is said and strike out words: the video loses those moments")
            onClicked: EditorState.editClipByText(EditorState.selectedTrack, EditorState.selectedClip)
        }
        }
    }
}
