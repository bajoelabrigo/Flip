import QtCore
import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import QtMultimedia
import Drift
import ".."

// Speech tab: local text-to-speech with optional voice cloning. The script is spoken into a take,
// heard (and fixed sentence by sentence) before it goes on the timeline.
Item {
    id: root
    // The panel's sidebar drives the category (0.23): its chips are not shown.
    property bool panelDriven: false

    readonly property bool ready: EditorState.tts.available
    property bool runtimeReady: Addons.runtimeAvailable()
    // Kept by the controller, so switching tabs (which unloads this one) loses neither (0.30).
    property string resultText: EditorState.tts.lastResultText
    property bool resultOk: EditorState.tts.lastResultOk
    onResultTextChanged: EditorState.tts.lastResultText = resultText
    onResultOkChanged: EditorState.tts.lastResultOk = resultOk

    readonly property string clipKind: {
        const data = EditorState.selectedClipData
        return (data && data.kind) ? data.kind : ""
    }
    readonly property bool clipUsable: clipKind === "video" || clipKind === "audio"
    readonly property bool busy: EditorState.tts.running || EditorState.voices.encoding
    readonly property bool canGenerate: ready && !busy && scriptField.text.trim().length > 0

    function selectVoice(id) {
        const row = EditorState.voices.indexOfId(id)
        voiceBox.currentIndex = row >= 0 ? row : 0
    }

    Component.onCompleted: {
        if (root.ready)
            EditorState.tts.warmUp()
    }

    Connections {
        target: EditorState.tts
        function onAvailableChanged() {
            if (EditorState.tts.available)
                EditorState.tts.warmUp()
        }
        function onFinished(ok, message) {
            root.resultOk = ok
            root.resultText = message
        }
    }

    Connections {
        target: EditorState.voices
        function onVoiceAdded(id) {
            root.selectVoice(id)
            root.resultOk = true
            root.resultText = qsTr("Voice saved")
        }
        function onError(message) {
            root.resultOk = false
            root.resultText = message
        }
    }

    Connections {
        target: Addons
        function onKindChanged(kind) {
            if (kind === "onnxruntime")
                root.runtimeReady = Addons.runtimeAvailable()
        }
    }

    MediaPlayer {
        id: voicePlayer
        audioOutput: AudioOutput {}
    }

    Settings {
        id: speechPrefs
        category: "tts"
        property bool optionsOpen: false
        property bool captions: false
    }

    function play(url) {
        voicePlayer.stop()
        voicePlayer.source = url
        voicePlayer.play()
    }
    readonly property bool playing: voicePlayer.playbackState === MediaPlayer.PlayingState
    // A dialogue («Ana: …», «Luis: …»): a voice for each person (0.30).
    property var speakerVoices: ({})
    readonly property var speakers: EditorState.tts.scriptSpeakers(scriptField.text)

    // «Edit script…» on a voice of the timeline: its script and settings, ready to speak again.
    Connections {
        target: EditorState.tts
        function onEditRequested(settings) {
            scriptField.text = settings.text
            root.selectVoice(settings.voice)
            langBox.currentIndex = Math.max(0, langBox.indexOfValue(settings.lang))
            exaggerationSlider.value = settings.exaggeration
            speedSlider.value = settings.speed
            pitchSlider.value = settings.pitch
        }
    }

    // A new speed or pitch reshapes the take once the slider rests (without speaking it again).
    Timer {
        id: retuneTimer
        interval: 450
        onTriggered: if (EditorState.tts.hasTake)
                         EditorState.tts.retune(speedSlider.value, pitchSlider.value)
    }

    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: speechColumn.height + Theme.spacing3xl
        clip: true
        ScrollBar.vertical: AppScrollBar { }

        // As Subtitles (Jorge, 0.30): the script, the voice and «Generate» first, the take to hear
        // below, the rest folded under Options.
        Column {
            id: speechColumn
            x: Theme.pagePadding
            width: parent.width - Theme.pagePadding * 2
            spacing: Theme.spacingMd
            topPadding: Theme.pagePadding

            readonly property real contentWidth: width

            Text {
                width: speechColumn.contentWidth
                text: qsTr("Voice from your text")
                color: Theme.panelForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                font.weight: Font.Medium
            }

            Text {
                visible: !root.ready
                width: speechColumn.contentWidth
                wrapMode: Text.WordWrap
                text: qsTr("Speech generation runs on this device and needs the voice model.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            ThemedButton {
                visible: !root.ready
                width: speechColumn.contentWidth
                text: root.runtimeReady
                      ? qsTr("Download voice model")
                      : qsTr("Install AI engine first")
                variant: "primary"
                glyph: Theme.icons.download
                tooltip: qsTr("Needed to generate speech")
                onClicked: root.Window.window.openAddonManager(
                    root.runtimeReady ? "tts-model" : "onnxruntime")
            }

            Column {
                visible: root.ready
                width: speechColumn.contentWidth
                spacing: Theme.spacingMd

                Text {
                    visible: EditorState.tts.replacing
                    width: parent.width
                    wrapMode: Text.WordWrap
                    text: qsTr("Editing the script of a voice on the timeline: the new take replaces its audio.")
                    color: Theme.primary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                }

                ThemedTextArea {
                    id: scriptField
                    width: parent.width
                    height: 140
                    enabled: !EditorState.tts.running
                    placeholderText: qsTr("Type or paste the script. [pause 1s] adds a silence.")
                    placeholderTextColor: Theme.mutedForeground
                    Component.onCompleted: text = EditorState.tts.draftScript
                    onTextChanged: EditorState.tts.draftScript = text
                }

                Item {
                    width: parent.width
                    height: importButton.height

                    Text {
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.width - importButton.width - Theme.spacingSm
                        elide: Text.ElideRight
                        text: qsTr("%1 characters, about %2 s").arg(scriptField.text.length)
                              .arg(Math.ceil(scriptField.text.length / 14 / Math.max(0.5, speedSlider.value)))
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                    ThemedButton {
                        id: importButton
                        anchors.right: parent.right
                        text: qsTr("Import script…")
                        variant: "ghost"
                        glyph: Theme.icons.upload
                        enabled: !EditorState.tts.running
                        tooltip: qsTr("A .txt, .md or Word (.docx) file")
                        onClicked: {
                            const url = FileDialogs.openFile(qsTr("Import a script"),
                                                             [qsTr("Scripts (*.txt *.md *.docx)"), qsTr("All files (*)")])
                            if (url == "")
                                return
                            const text = EditorState.tts.readScriptFile(url)
                            if (text.length > 0)
                                scriptField.text = text
                            else {
                                root.resultOk = false
                                root.resultText = qsTr("That file has no text that can be read")
                            }
                        }
                    }
                }

                Row {
                    width: parent.width
                    spacing: Theme.spacingSm

                    ThemedComboBox {
                        id: voiceBox
                        width: parent.width - previewButton.width - moreButton.width - parent.spacing * 2
                        anchors.verticalCenter: parent.verticalCenter
                        enabled: !root.busy
                        model: EditorState.voices
                        textRole: "name"
                        valueRole: "id"
                        Component.onCompleted: root.selectVoice(EditorState.tts.lastVoice)
                    }

                    IconButton {
                        id: previewButton
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: root.playing ? Theme.icons.pause : Theme.icons.play
                        tooltip: root.playing ? qsTr("Stop") : qsTr("Play the voice sample")
                        onClicked: {
                            if (root.playing) {
                                voicePlayer.stop()
                                return
                            }
                            root.play(EditorState.voices.referenceUrl(voiceBox.currentValue))
                        }
                    }

                    IconButton {
                        id: moreButton
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: Theme.icons.ellipsis
                        tooltip: qsTr("Rename or delete this voice")
                        enabled: voiceBox.currentIndex > 0 && !root.busy
                        onClicked: voiceMenu.popup()

                        ThemedContextMenu {
                            id: voiceMenu
                            ThemedMenuItem {
                                text: qsTr("Rename…")
                                icon.name: Theme.icons.pencil
                                onTriggered: renameDialog.openWith(qsTr("Rename voice"), voiceBox.currentText)
                            }
                            ThemedMenuItem {
                                text: qsTr("Delete")
                                icon.name: Theme.icons.trash
                                onTriggered: {
                                    voicePlayer.stop()
                                    EditorState.voices.remove(voiceBox.currentValue)
                                    voiceBox.currentIndex = 0
                                }
                            }
                        }
                    }
                }

                Column {
                    visible: root.speakers.length > 0
                    width: parent.width
                    spacing: Theme.spacingXs

                    Text {
                        width: parent.width
                        wrapMode: Text.WordWrap
                        text: qsTr("A dialogue: a voice for each person")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                    Repeater {
                        model: root.speakers
                        delegate: Row {
                            id: speakerRow
                            required property string modelData
                            width: parent.width
                            spacing: Theme.spacingSm
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                width: parent.width * 0.32
                                elide: Text.ElideRight
                                text: speakerRow.modelData
                                color: Theme.panelForeground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeSm
                            }
                            ThemedComboBox {
                                width: parent.width * 0.68 - parent.spacing
                                enabled: !root.busy
                                model: EditorState.voices
                                textRole: "name"
                                valueRole: "id"
                                Component.onCompleted: {
                                    const chosen = root.speakerVoices[speakerRow.modelData]
                                    // A second person starts on another voice, so the two are told apart.
                                    const fallback = Math.min(count - 1, root.speakers.indexOf(speakerRow.modelData))
                                    currentIndex = chosen ? Math.max(0, EditorState.voices.indexOfId(chosen)) : Math.max(0, fallback)
                                    const map = Object.assign({}, root.speakerVoices)
                                    map[speakerRow.modelData] = currentValue
                                    root.speakerVoices = map
                                }
                                onActivated: {
                                    const map = Object.assign({}, root.speakerVoices)
                                    map[speakerRow.modelData] = currentValue
                                    root.speakerVoices = map
                                }
                            }
                        }
                    }
                }

                ThemedComboBox {
                    id: langBox
                    width: parent.width
                    enabled: !EditorState.tts.running
                    textRole: "label"
                    valueRole: "code"
                    model: EditorState.tts.languageOptions()
                    Component.onCompleted: currentIndex = Math.max(0, indexOfValue(EditorState.tts.lastLanguage))
                }

                ThemedButton {
                    visible: !EditorState.tts.running
                    width: parent.width
                    text: EditorState.tts.hasTake ? qsTr("Generate again") : qsTr("Generate speech")
                    variant: EditorState.tts.hasTake ? "secondary" : "primary"
                    glyph: Theme.icons.audioLines
                    enabled: root.canGenerate
                    tooltip: qsTr("Speak the script; you hear it before it goes on the timeline")
                    onClicked: {
                        root.resultText = ""
                        voicePlayer.stop()
                        EditorState.tts.generate(scriptField.text, voiceBox.currentValue, langBox.currentValue,
                                                 exaggerationSlider.value, speedSlider.value, pitchSlider.value,
                                                 root.speakerVoices)
                    }
                }

                Row {
                    visible: EditorState.tts.loading && !EditorState.tts.running
                    width: parent.width
                    spacing: Theme.spacingMd

                    IconGlyph {
                        anchors.verticalCenter: parent.verticalCenter
                        glyph: Theme.icons.spinner
                        spinning: true
                    }

                    Text {
                        width: parent.width - Theme.iconSizeBase - parent.spacing
                        anchors.verticalCenter: parent.verticalCenter
                        wrapMode: Text.WordWrap
                        text: qsTr("Loading voice model (first use takes a while)…")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                }

                Column {
                    visible: EditorState.tts.running
                    width: parent.width
                    spacing: Theme.spacingMd

                    Text {
                        width: parent.width
                        text: EditorState.tts.loading
                              ? qsTr("Loading voice model (first use takes a while)…")
                              : EditorState.tts.status
                        color: Theme.panelForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                        elide: Text.ElideRight
                    }

                    ThemedProgressBar {
                        width: parent.width
                        value: EditorState.tts.progress
                        opacity: EditorState.tts.loading ? 0.4 : 1
                    }

                    ThemedButton {
                        text: qsTr("Cancel")
                        variant: "destructive"
                        glyph: Theme.icons.x
                        tooltip: qsTr("Stop generating")
                        onClicked: EditorState.tts.cancel()
                    }
                }

                // ---- The take: heard before it goes on the timeline -----------------------------
                Rectangle {
                    visible: EditorState.tts.hasTake && !EditorState.tts.running
                    width: parent.width
                    height: takeColumn.height + Theme.spacingMd * 2
                    radius: Theme.radiusMd
                    color: Theme.panelMuted

                    Column {
                        id: takeColumn
                        x: Theme.spacingMd
                        y: Theme.spacingMd
                        width: parent.width - Theme.spacingMd * 2
                        spacing: Theme.spacingSm

                        Row {
                            spacing: Theme.spacingSm
                            IconButton {
                                anchors.verticalCenter: parent.verticalCenter
                                glyph: root.playing && voicePlayer.source == EditorState.tts.takeUrl
                                       ? Theme.icons.pause : Theme.icons.play
                                tooltip: qsTr("Listen to the whole take")
                                onClicked: {
                                    if (root.playing && voicePlayer.source == EditorState.tts.takeUrl)
                                        voicePlayer.stop()
                                    else
                                        root.play(EditorState.tts.takeUrl)
                                }
                            }
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: qsTr("Take: %1 s").arg(EditorState.tts.takeSeconds.toFixed(1))
                                color: Theme.panelForeground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeSm
                            }
                        }

                        // Each sentence: hear it, or speak it again if it came out wrong.
                        Repeater {
                            model: EditorState.tts.sentences
                            delegate: Row {
                                id: sentenceRow
                                required property var modelData
                                required property int index
                                width: takeColumn.width
                                spacing: Theme.spacingXs
                                IconButton {
                                    id: sentencePlay
                                    anchors.verticalCenter: parent.verticalCenter
                                    glyph: Theme.icons.play
                                    tooltip: qsTr("Listen to this sentence")
                                    onClicked: root.play(sentenceRow.modelData.url)
                                }
                                Text {
                                    anchors.verticalCenter: parent.verticalCenter
                                    width: parent.width - sentencePlay.width - sentenceAgain.width - parent.spacing * 2
                                    elide: Text.ElideRight
                                    text: sentenceRow.modelData.text
                                    color: Theme.panelForeground
                                    font.family: Theme.fontFamily
                                    font.pixelSize: Theme.fontSizeXs
                                }
                                IconButton {
                                    id: sentenceAgain
                                    anchors.verticalCenter: parent.verticalCenter
                                    glyph: Theme.icons.refresh
                                    tooltip: qsTr("Speak this sentence again")
                                    onClicked: {
                                        voicePlayer.stop()
                                        EditorState.tts.regenerateSentence(sentenceRow.index, voiceBox.currentValue,
                                                                           langBox.currentValue, exaggerationSlider.value)
                                    }
                                }
                            }
                        }

                        ThemedCheckBox {
                            width: parent.width
                            text: qsTr("Also create its captions")
                            checked: speechPrefs.captions
                            onToggled: speechPrefs.captions = checked
                        }

                        ThemedButton {
                            width: parent.width
                            text: EditorState.tts.replacing ? qsTr("Replace the voice on the timeline")
                                                            : qsTr("Add to the timeline")
                            variant: "primary"
                            glyph: Theme.icons.plus
                            onClicked: {
                                voicePlayer.stop()
                                EditorState.tts.insertTake(speechPrefs.captions)
                            }
                        }
                        ThemedButton {
                            width: parent.width
                            text: qsTr("Discard")
                            variant: "ghost"
                            glyph: Theme.icons.trash
                            onClicked: {
                                voicePlayer.stop()
                                EditorState.tts.discardTake()
                            }
                        }
                    }
                }

                Text {
                    visible: root.resultText.length > 0 && !EditorState.tts.running
                    width: parent.width
                    wrapMode: Text.WordWrap
                    text: root.resultText
                    color: root.resultOk ? Theme.mutedForeground : Theme.destructive
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                }

                // Everything else, folded (remembered open or closed).
                ThemedButton {
                    width: parent.width
                    text: qsTr("Options")
                    variant: "ghost"
                    glyph: speechPrefs.optionsOpen ? Theme.icons.chevronUp : Theme.icons.chevronDown
                    onClicked: speechPrefs.optionsOpen = !speechPrefs.optionsOpen
                }

                Column {
                    visible: speechPrefs.optionsOpen
                    width: parent.width
                    spacing: Theme.spacingSm

                    ThemedSlider {
                        id: speedSlider
                        width: parent.width
                        label: qsTr("Speed")
                        from: 0.5
                        to: 2.0
                        stepSize: 0.05
                        value: EditorState.tts.lastSpeed
                        valueFormatter: v => qsTr("%1×").arg(Number(v).toFixed(2))
                        enabled: !EditorState.tts.running
                        onMoved: retuneTimer.restart()
                    }

                    ThemedSlider {
                        id: pitchSlider
                        width: parent.width
                        label: qsTr("Pitch")
                        from: 0.5
                        to: 2.0
                        stepSize: 0.05
                        value: EditorState.tts.lastPitch
                        valueFormatter: v => qsTr("%1×").arg(Number(v).toFixed(2))
                        enabled: !EditorState.tts.running
                        onMoved: retuneTimer.restart()
                    }

                    ThemedSlider {
                        id: exaggerationSlider
                        width: parent.width
                        label: qsTr("Expressiveness")
                        from: 0.25
                        to: 2.0
                        stepSize: 0.05
                        value: EditorState.tts.lastExaggeration
                        enabled: !EditorState.tts.running
                    }

                    Text {
                        width: parent.width
                        wrapMode: Text.WordWrap
                        text: qsTr("Higher values sound more dramatic and speak faster")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }

                    ThemedButton {
                        id: newVoiceButton
                        width: parent.width
                        text: qsTr("New voice")
                        variant: "secondary"
                        glyph: Theme.icons.plus
                        enabled: !root.busy
                        tooltip: qsTr("Clone a voice from a recording")
                        onClicked: newVoiceMenu.popup()

                        ThemedContextMenu {
                            id: newVoiceMenu
                            ThemedMenuItem {
                                text: qsTr("From selected clip")
                                enabled: root.clipUsable
                                onTriggered: voiceDialog.openForClip()
                            }
                            ThemedMenuItem {
                                text: qsTr("Record…")
                                icon.name: Theme.icons.mic
                                onTriggered: voiceDialog.openForMic()
                            }
                            ThemedMenuItem {
                                text: qsTr("Import file…")
                                icon.name: Theme.icons.upload
                                onTriggered: voiceDialog.openForFile()
                            }
                        }
                    }

                    // Cloning a voice: what it is doing, how far, and a way out (0.30).
                    Column {
                        visible: EditorState.voices.encoding
                        width: parent.width
                        spacing: Theme.spacingSm
                        Text {
                            width: parent.width
                            wrapMode: Text.WordWrap
                            text: EditorState.tts.loading
                                  ? qsTr("Loading voice model (first use takes a while)…")
                                  : (EditorState.voices.encodeStatus || qsTr("Learning the voice…"))
                            color: Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                        ThemedProgressBar {
                            width: parent.width
                            value: EditorState.voices.encodeProgress
                        }
                        ThemedButton {
                            text: qsTr("Cancel")
                            variant: "destructive"
                            glyph: Theme.icons.x
                            tooltip: qsTr("Stop preparing the voice")
                            onClicked: EditorState.voices.cancelEncoding()
                        }
                    }
                }
            }
        }
    }

    NameDialog {
        id: renameDialog
        onSubmitted: name => EditorState.voices.rename(voiceBox.currentValue, name)
    }

    ThemedDialog {
        id: voiceDialog

        property string mode: "clip"
        property string sourcePath: ""
        property real sourceIn: 0
        property real sourceOut: 0
        property real offset: 0
        readonly property real range: Math.max(0, sourceOut - sourceIn)
        readonly property bool recording: EditorState.voices.recording
        readonly property bool saveReady: nameField.text.trim().length > 0 && rightsBox.checked
                                         && (mode !== "mic"
                                             || (recording && EditorState.voices.recordingSeconds >= 3))

        title: mode === "mic" ? qsTr("Record a voice")
                              : (mode === "file" ? qsTr("Import a voice") : qsTr("Voice from clip"))
        preferredWidth: Theme.dialogWidthMd
        acceptText: qsTr("Save")
        showAccept: saveReady

        function openWithName(defaultName) {
            nameField.text = defaultName
            rightsBox.checked = false
            offset = 0
            open()
            nameField.forceActiveFocus()
            nameField.selectAll()
        }

        function openForClip() {
            const data = EditorState.selectedClipData
            mode = "clip"
            sourcePath = data.path
            sourceIn = data.inPoint
            sourceOut = data.outPoint
            openWithName(data.name || qsTr("My voice"))
        }

        function openForMic() {
            mode = "mic"
            openWithName(qsTr("My voice"))
        }

        function openForFile() {
            const url = FileDialogs.openFile(qsTr("Import a voice sample"),
                                             [qsTr("Audio files (*.wav *.mp3 *.flac *.ogg *.m4a *.aac *.opus)"),
                                              qsTr("All files (*)")])
            if (url == "")
                return
            mode = "file"
            sourcePath = url.toString()
            openWithName(decodeURIComponent(sourcePath.split("/").pop().replace(/\.[^.]*$/, "")))
        }

        onAccepted: {
            const name = nameField.text.trim()
            if (mode === "mic")
                EditorState.voices.stopRecordingAndAdd(name)
            else if (mode === "file")
                EditorState.voices.addFromFile(sourcePath, name)
            else
                EditorState.voices.addFromMedia(sourcePath, sourceIn + offset,
                                                Math.min(sourceOut, sourceIn + offset + 20), name)
        }
        onClosed: EditorState.voices.cancelRecording()

        contentItem: Column {
            spacing: Theme.spacingLg
            width: parent ? parent.width : 360

            ThemedLabel {
                text: qsTr("Name")
            }

            ThemedTextField {
                id: nameField
                width: parent.width
                placeholderText: qsTr("My voice")
            }

            ThemedLabel {
                visible: voiceDialog.mode === "clip"
                width: parent.width
                text: voiceDialog.range > 20
                      ? qsTr("The clip is longer than 20 seconds, so 20 seconds are used. Starting at %1 s.")
                            .arg(voiceDialog.offset.toFixed(1))
                      : qsTr("Using %1 seconds of the selected clip.").arg(voiceDialog.range.toFixed(1))
            }

            ThemedSlider {
                visible: voiceDialog.mode === "clip" && voiceDialog.range > 20
                width: parent.width
                label: qsTr("Start offset")
                from: 0
                to: Math.max(0.1, voiceDialog.range - 20)
                value: voiceDialog.offset
                valueFormatter: v => qsTr("%1 s").arg(Number(v).toFixed(1))
                onMoved: voiceDialog.offset = value
            }

            Column {
                visible: voiceDialog.mode === "mic"
                width: parent.width
                spacing: Theme.spacingMd

                ThemedLabel {
                    width: parent.width
                    text: qsTr("Record 3 to 20 seconds in a quiet room (it stops by itself at 20). Read this aloud in your natural voice:")
                }

                Text {
                    width: parent.width
                    wrapMode: Text.WordWrap
                    text: qsTr("The quick brown fox jumps over the lazy dog, while a gentle breeze moves through the quiet garden and the evening light fades slowly.")
                    color: Theme.panelForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSm
                }

                Rectangle {
                    width: parent.width
                    height: Theme.spacingMd
                    radius: height / 2
                    color: Theme.panelMuted

                    Rectangle {
                        width: parent.width * Math.max(0, Math.min(1, EditorState.voices.level))
                        height: parent.height
                        radius: parent.radius
                        color: Theme.primary
                    }
                }

                Row {
                    spacing: Theme.spacingLg

                    ThemedButton {
                        text: voiceDialog.recording ? qsTr("Recording…") : qsTr("Start recording")
                        variant: "secondary"
                        glyph: Theme.icons.mic
                        enabled: !voiceDialog.recording
                        onClicked: EditorState.voices.startRecording()
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: EditorState.voices.recordingSeconds >= 20
                              ? qsTr("20 s: done, save the voice")
                              : qsTr("%1 s").arg(EditorState.voices.recordingSeconds.toFixed(1))
                        color: Theme.panelForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSm
                    }
                }
            }

            ThemedCheckBox {
                id: rightsBox
                width: parent.width
                text: qsTr("I have the right to use this person's voice")
            }
        }
    }
}
