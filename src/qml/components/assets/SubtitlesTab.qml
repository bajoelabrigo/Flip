import QtCore
import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift
import ".."

// Subtitles tab: timed caption clips, .srt import, and auto-caption from speech.
Item {
    id: root
    // The panel's sidebar drives the category (0.23): its chips are not shown.
    property bool panelDriven: false

    // A clip landed on the timeline. The phone shell closes the sheet on this —
    // the thing you came for is behind it. Auto-caption deliberately does not
    // emit it: its progress and cancel button live in this sheet.
    signal added()

    // The last language and caption length, kept for next time (they went back to the first entry).
    Settings {
        id: captionPrefs
        category: "subtitles"
        property string language: ""
        property int words: 0
        property bool optionsOpen: false
    }

    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: subtitleColumn.height + Theme.spacing3xl
        clip: true
        ScrollBar.vertical: AppScrollBar { }

        // One clear way to do each thing (Jorge, 2026-11-01): the language and «Create captions» first,
        // the rest folded under Options, the styles below, writing by hand or importing at the end.
        Column {
            id: subtitleColumn
            x: Theme.pagePadding
            width: parent.width - Theme.pagePadding * 2
            spacing: Theme.spacingMd
            topPadding: Theme.pagePadding

            readonly property real contentWidth: width

            // ---- Create with AI ---------------------------------------------------------------
            Text {
                width: subtitleColumn.contentWidth
                text: qsTr("Captions from the voice")
                color: Theme.panelForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                font.weight: Font.Medium
            }

            Text {
                visible: root.captionEngineReady && !root.captionTargetReady && !EditorState.subtitleGenerating
                width: subtitleColumn.contentWidth
                wrapMode: Text.WordWrap
                text: qsTr("Select a video or audio clip on the timeline first.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            // The transcriber ships as an addon, and so does the runtime it needs; without
            // both there are no languages to list and nothing to run, so offer the download
            // in place of the controls.
            ThemedComboBox {
                id: captionLanguageBox
                visible: root.captionEngineReady
                width: subtitleColumn.contentWidth
                enabled: root.captionTargetReady && !EditorState.subtitleGenerating
                textRole: "label"
                valueRole: "code"
                model: EditorState.whisperLanguages()
                Component.onCompleted: currentIndex = Math.max(0, indexOfValue(captionPrefs.language))
                onActivated: captionPrefs.language = currentValue !== undefined ? currentValue : ""
            }

            ThemedButton {
                visible: root.captionEngineReady && !EditorState.subtitleGenerating
                width: subtitleColumn.contentWidth
                text: qsTr("Create captions")
                variant: "primary"
                glyph: Theme.icons.captions
                tooltip: root.captionTargetReady
                         ? qsTr("Create captions from the selected clips' speech — several clips become one caption clip")
                         : qsTr("Select a video or audio clip first")
                enabled: root.captionTargetReady
                onClicked: EditorState.generateSubtitlesForSelection(root.captionLanguage(), captionWordsBox.currentValue)
            }

            Column {
                visible: root.captionEngineReady && EditorState.subtitleGenerating
                width: subtitleColumn.contentWidth
                spacing: Theme.spacingMd

                Text {
                    width: parent.width
                    text: EditorState.subtitleGenStatus.length > 0
                          ? EditorState.subtitleGenStatus
                          : qsTr("Creating captions… %1%").arg(Math.round(EditorState.subtitleGenProgress * 100))
                    color: Theme.panelForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                    elide: Text.ElideRight
                }

                Rectangle {
                    width: parent.width
                    height: Theme.spacingMd
                    radius: height / 2
                    color: Theme.panelMuted

                    Rectangle {
                        width: parent.width * Math.max(0, Math.min(1, EditorState.subtitleGenProgress))
                        height: parent.height
                        radius: parent.radius
                        color: Theme.primary

                        Behavior on width {
                            NumberAnimation { duration: Theme.durationBase; easing.type: Theme.easing }
                        }
                    }
                }

                ThemedButton {
                    text: qsTr("Cancel")
                    variant: "destructive"
                    glyph: Theme.icons.x
                    tooltip: qsTr("Stop creating captions")
                    onClicked: EditorState.cancelSubtitleGeneration()
                }
            }

            ThemedButton {
                visible: !root.captionEngineReady
                width: subtitleColumn.contentWidth
                text: root.runtimeReady
                      ? qsTr("Download speech recognition (about 670 MB)")
                      : qsTr("Install AI engine first")
                variant: "primary"
                glyph: Theme.icons.download
                tooltip: qsTr("Needed for auto captions from speech")
                onClicked: root.Window.window.openAddonManager(
                    root.runtimeReady ? "whisper-model" : "onnxruntime")
            }

            // Word timing is its own download; without it captions are split by length and the
            // karaoke word is estimated, so say what the extra buys.
            Text {
                visible: root.whisperReady && !root.alignReady
                width: subtitleColumn.contentWidth
                wrapMode: Text.WordWrap
                text: qsTr("Tip: install “Word sync” in Extras so captions start and end exactly on the voice.")
                color: Theme.primary
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.Window.window.openAddonManager("align-model")
                }
            }

            // Everything else about how captions are made, folded (remembered open or closed).
            ThemedButton {
                visible: root.captionEngineReady
                width: subtitleColumn.contentWidth
                text: qsTr("Options")
                variant: "ghost"
                glyph: captionPrefs.optionsOpen ? Theme.icons.chevronUp : Theme.icons.chevronDown
                onClicked: captionPrefs.optionsOpen = !captionPrefs.optionsOpen
            }

            Column {
                visible: root.captionEngineReady && captionPrefs.optionsOpen
                width: subtitleColumn.contentWidth
                spacing: Theme.spacingSm

                ThemedComboBox {
                    id: captionWordsBox
                    width: parent.width
                    enabled: !EditorState.subtitleGenerating
                    textRole: "label"
                    valueRole: "words"
                    model: root.captionLengthOptions
                    Component.onCompleted: currentIndex = Math.max(0, indexOfValue(captionPrefs.words))
                    onActivated: captionPrefs.words = currentValue
                }

                Text {
                    // With Word sync the times are measured, not split: nothing to warn about.
                    visible: root.whisperReady && !root.alignReady && captionWordsBox.currentValue > 0
                    width: parent.width
                    wrapMode: Text.WordWrap
                    text: qsTr("Shorter captions are timed by splitting each phrase evenly, so they can drift slightly out of sync with the speech.")
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                }

                // Each voice in its colour, with a name (needs the speaker-labels extra on this computer).
                ThemedCheckBox {
                    visible: EditorState.subtitleSpeakersAvailable()
                    width: parent.width
                    text: qsTr("Tell the speakers apart (a colour for each)")
                    checked: EditorState.subtitleSpeakersEnabled()
                    onToggled: EditorState.setSubtitleSpeakersEnabled(checked)
                }

                ThemedCheckBox {
                    width: parent.width
                    text: qsTr("Two lines per caption")
                    checked: EditorState.subtitleTwoLines()
                    onToggled: EditorState.setSubtitleTwoLines(checked)
                }

                ThemedCheckBox {
                    width: parent.width
                    text: qsTr("Remove hesitations (eh, mmm) and capitalize")
                    checked: EditorState.subtitleCleanupEnabled()
                    onToggled: EditorState.setSubtitleCleanupEnabled(checked)
                }

                ThemedCheckBox {
                    width: parent.width
                    text: qsTr("Highlight key words in colour")
                    checked: EditorState.subtitleKeywordsEnabled()
                    onToggled: EditorState.setSubtitleKeywordsEnabled(checked)
                }

                ThemedCheckBox {
                    width: parent.width
                    text: qsTr("Add emojis for keywords (fuego 🔥, Dios 🙏)")
                    checked: EditorState.subtitleEmojisEnabled()
                    onToggled: EditorState.setSubtitleEmojisEnabled(checked)
                }

                ThemedCheckBox {
                    width: parent.width
                    text: qsTr("Hide swear words (m*****)")
                    checked: EditorState.subtitleProfanityFilter()
                    onToggled: EditorState.setSubtitleProfanityFilter(checked)
                }

                // Where the speech is recognized: on this computer, or with ElevenLabs (offered once it
                // is set up in Settings › Cloud). The cloud takes a list of hard words.
                Row {
                    id: engineRow
                    visible: root.cloudReady
                    width: parent.width
                    spacing: 6
                    readonly property real half: (width - spacing) / 2

                    ThemedButton {
                        width: engineRow.half
                        text: qsTr("On this computer")
                        variant: root.useCloud ? "ghost" : "secondary"
                        enabled: root.whisperReady
                        onClicked: {
                            root.useCloud = false
                            EditorState.setSubtitleCloudEngine(false)
                        }
                    }
                    ThemedButton {
                        width: engineRow.half
                        text: qsTr("In the cloud")
                        variant: root.useCloud ? "secondary" : "ghost"
                        tooltip: qsTr("ElevenLabs Scribe: the audio is sent to ElevenLabs with your key")
                        onClicked: {
                            root.useCloud = true
                            EditorState.setSubtitleCloudEngine(true)
                        }
                    }
                }

                // Names, brands and terms to spell as given (the cloud's keyterms, Whisper's prompt here).
                ThemedTextField {
                    width: parent.width
                    placeholderText: qsTr("Hard words: names, brands… (separated by commas)")
                    text: EditorState.subtitleKeytermsText()
                    onEditingFinished: EditorState.setSubtitleKeytermsText(text)
                }

                // Whisper's translate task: the same speech written in English, placed above the
                // original captions — bilingual videos in two clicks.
                ThemedButton {
                    visible: root.whisperReady && !EditorState.subtitleGenerating
                    width: parent.width
                    text: qsTr("Add English translation")
                    variant: "secondary"
                    glyph: Theme.icons.languages
                    tooltip: qsTr("Captions translated to English, above the original ones. English is the only language the model translates to.")
                    enabled: root.captionTargetReady
                    onClicked: EditorState.generateEnglishSubtitlesForSelection(root.captionLanguage(),
                                                                                captionWordsBox.currentValue)
                }
            }

            Rectangle {
                width: subtitleColumn.contentWidth
                height: Theme.borderWidth
                color: Theme.panelBorder
            }

            // ---- Style ------------------------------------------------------------------------
            // The look captions are created with, remembered for next time. With captions picked,
            // the same gallery restyles them.
            Text {
                width: subtitleColumn.contentWidth
                text: root.captionClipKind === "subtitle" ? qsTr("Style of the selected captions")
                                                          : qsTr("Caption style")
                color: Theme.panelForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                font.weight: Font.Medium
            }

            Grid {
                id: captionStyleGrid
                width: subtitleColumn.contentWidth
                columns: 2
                columnSpacing: Theme.spacingSm
                rowSpacing: Theme.spacingSm
                readonly property real cardWidth: (width - columnSpacing) / 2

                Repeater {
                    // Starred styles first, then the one in use, so the six shown folded are the ones
                    // that matter; «See all» opens the rest.
                    model: {
                        void root.favoritesTick
                        const fav = s => EditorState.isAssetFavorite("captionStyles", s.id)
                        const current = s => s.id === root.captionStyle
                        const ordered = root.captionStyles.filter(fav)
                            .concat(root.captionStyles.filter(s => !fav(s) && current(s)))
                            .concat(root.captionStyles.filter(s => !fav(s) && !current(s)))
                        return root.stylesOpen ? ordered : ordered.slice(0, root.foldedStyles)
                    }
                    delegate: Column {
                        id: styleCard
                        required property var modelData
                        width: captionStyleGrid.cardWidth
                        spacing: Theme.spacingXs
                        scale: styleMouse.pressed ? 0.97 : (styleMouse.containsMouse ? 1.02 : 1.0)
                        Behavior on scale {
                            NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                        }

                        TextStylePackThumb {
                            width: parent.width
                            height: Math.round(width * 0.5)
                            presetId: styleCard.modelData.id
                            selected: root.captionStyle === styleCard.modelData.id
                            hovered: styleMouse.containsMouse

                            MouseArea {
                                id: styleMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    root.captionStyle = styleCard.modelData.id
                                    EditorState.setSubtitleStylePreset(styleCard.modelData.id)
                                    if (root.captionClipKind === "subtitle")
                                        EditorState.applyTextPreset(EditorState.selectedTrack,
                                                                    EditorState.selectedClip,
                                                                    styleCard.modelData.id)
                                }
                            }

                            AssetFavoriteButton {
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.margins: 3
                                tabId: "captionStyles"
                                itemId: styleCard.modelData.id
                            }
                        }

                        Text {
                            width: parent.width
                            text: styleCard.modelData.label
                            elide: Text.ElideRight
                            horizontalAlignment: Text.AlignHCenter
                            color: root.captionStyle === styleCard.modelData.id ? Theme.panelForeground
                                                                                : Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                    }
                }
            }

            ThemedButton {
                visible: root.captionStyles.length > root.foldedStyles
                width: subtitleColumn.contentWidth
                text: root.stylesOpen ? qsTr("Show fewer")
                                      : qsTr("See all styles (%1)").arg(root.captionStyles.length)
                variant: "ghost"
                glyph: root.stylesOpen ? Theme.icons.chevronUp : Theme.icons.chevronDown
                onClicked: root.stylesOpen = !root.stylesOpen
            }

            Rectangle {
                width: subtitleColumn.contentWidth
                height: Theme.borderWidth
                color: Theme.panelBorder
            }

            // ---- By hand ----------------------------------------------------------------------
            Row {
                id: manualRow
                width: subtitleColumn.contentWidth
                spacing: 6
                readonly property real half: (width - spacing) / 2

                ThemedButton {
                    width: manualRow.half
                    text: qsTr("Write by hand")
                    variant: "secondary"
                    glyph: Theme.icons.plus
                    tooltip: qsTr("An empty caption clip at the playhead: write each line in the clip panel")
                    onClicked: {
                        EditorState.addSubtitleClip(-1)
                        root.added()
                    }
                }

                ThemedButton {
                    width: manualRow.half
                    text: qsTr("Import file")
                    variant: "secondary"
                    glyph: Theme.icons.upload
                    tooltip: qsTr("Import an SRT, WebVTT or ASS file as a subtitle clip")
                    onClicked: {
                        const url = FileDialogs.openFile(
                            qsTr("Import Subtitles"),
                            [qsTr("Subtitle files (*.srt *.vtt *.ass *.ssa)"),
                             qsTr("SubRip subtitles (*.srt)"),
                             qsTr("WebVTT subtitles (*.vtt)"),
                             qsTr("SubStation Alpha subtitles (*.ass *.ssa)"),
                             qsTr("All files (*)")])
                        if (url != "") {
                            EditorState.importSubtitleFile(url, -1)
                            root.added()
                        }
                    }
                }
            }
        }
    }

    function captionLanguage() {
        return captionLanguageBox.currentValue !== undefined ? captionLanguageBox.currentValue : ""
    }
    // Styles shown with the gallery folded (three rows of two).
    readonly property int foldedStyles: 6
    property bool stylesOpen: false

    // "Recommended" packs by display width like openai-whisper does; the numbered entries cap
    // words per caption on top of that.
    readonly property var captionLengthOptions: {
        const options = [{ label: qsTr("Recommended caption length"), words: 0 }]
        options.push({ label: qsTr("1 word per caption"), words: 1 })
        for (let n = 2; n <= 8; ++n)
            options.push({ label: qsTr("%1 words per caption").arg(n), words: n })
        return options
    }

    property bool alignReady: Addons.hasKind("align-model")
    property var captionStyles: EditorState.subtitleStyleChoices()
    property int favoritesTick: 0
    Connections {
        target: EditorState
        function onAssetFavoritesChanged() { root.favoritesTick++ }
    }
    property string captionStyle: EditorState.subtitleStylePreset()

    // ElevenLabs set up in Settings › Cloud: captions can also be made there.
    property bool cloudReady: {
        void EditorState.cloudProviders.revision // a key or consent given in Settings shows it at once
        return EditorState.subtitleCloudReady()
    }
    property bool useCloud: EditorState.subtitleCloudEngine()
    readonly property bool captionEngineReady: whisperReady || (cloudReady && useCloud)
    property bool whisperReady: Addons.hasKind("whisper-model")
                                && Addons.runtimeAvailable()
    property bool runtimeReady: Addons.runtimeAvailable()

    readonly property string captionClipKind: {
        const data = EditorState.selectedClipData
        return (data && data.kind) ? data.kind : ""
    }
    readonly property bool captionTargetReady: captionClipKind === "video"
                                               || captionClipKind === "audio"

    Connections {
        target: Addons
        function onKindChanged(kind) {
            if (kind === "text-styles") {
                root.captionStyles = EditorState.subtitleStyleChoices()
                root.captionStyle = EditorState.subtitleStylePreset()
                return
            }
            if (kind === "align-model") {
                root.alignReady = Addons.hasKind("align-model")
                return
            }
            if (kind !== "whisper-model" && kind !== "onnxruntime")
                return
            root.runtimeReady = Addons.runtimeAvailable()
            root.whisperReady = Addons.hasKind("whisper-model")
                                && root.runtimeReady
        }
    }
}
