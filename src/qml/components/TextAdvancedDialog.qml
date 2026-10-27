import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import Drift

// Texto avanzado (0.23, como Filmora): una ventana que se mueve y se maximiza, con la barra de un
// procesador de textos arriba (fuente, tamaño, negrita, cursiva, subrayado, color, mayúsculas,
// alineación e interlineado), la vista previa grande del texto (sus asas para moverlo, girarlo y
// escribir sobre él con doble clic), su línea de tiempo y, a la derecha, Estilo, Personalizar,
// Animación y Burbuja. Personalizar empieza por «Texto de entrada»: ahí se escribe, y las letras que
// se eligen ahí (o sobre la vista previa) son las que la barra cambia; sin nada elegido, la barra
// cambia el texto entero. Cada letra con algo propio es un tramo del estilo (`TextRun`).
//
// Todo cambia en vivo y la ventana es una sesión de edición: Aplicar deja lo hecho dentro como un
// solo paso de deshacer; Cancelar lo devuelve todo como estaba.
ThemedDialog {
    id: root

    // El clip que se está editando, congelado al abrir: si cambia la selección, se cierra.
    property int trackIndex: -1
    property int clipIndex: -1
    property string clipId: ""
    // Las letras elegidas, de donde se eligieron por última vez (el cuadro o la vista previa).
    property int selectionStart: -1
    property int selectionEnd: -1
    readonly property bool hasSelection: selectionStart >= 0 && selectionEnd > selectionStart
    // "style" | "customize" | "animation" | "bubble", como las pestañas de Filmora.
    property string page: "customize"
    property bool keepEdits: false

    readonly property var clipData: EditorState.selectedClipData || ({})
    readonly property var textStyle: root.clipData.textStyle || ({})
    readonly property string text: root.clipData.textContent || ""
    readonly property var runs: {
        void EditorState.tracksRevision
        void root.clipData
        return root.trackIndex >= 0 ? EditorState.textRuns(root.trackIndex, root.clipIndex) : []
    }
    readonly property real clipStart: Number(root.clipData.start) || 0
    readonly property real clipDuration: Math.max(0.04, Number(root.clipData.duration) || 0)
    readonly property real basePx: Math.max(1, Number(root.textStyle.pixelSize) || 64)

    // Lo que tienen las letras elegidas (el tramo de la primera), o el texto entero.
    readonly property var selRun: {
        if (!root.hasSelection)
            return null
        for (const run of root.runs) {
            if (root.selectionStart >= run.start && root.selectionStart < run.end)
                return run
        }
        return null
    }
    readonly property bool shownBold: root.selRun && root.selRun.boldEnabled ? root.selRun.bold
                                                                             : Number(root.textStyle.fontWeight) >= 600
    readonly property bool shownItalic: root.selRun && root.selRun.italicEnabled ? root.selRun.italic
                                                                                 : root.textStyle.italic === true
    readonly property bool shownUnderline: !!(root.selRun && root.selRun.underlineEnabled && root.selRun.underline)
    readonly property string shownFont: root.selRun && root.selRun.fontEnabled && root.selRun.fontFamily
                                        ? root.selRun.fontFamily : (root.textStyle.fontFamily || "")
    readonly property real shownSize: root.selRun && root.selRun.sizeEnabled
                                      ? Math.round(root.basePx * root.selRun.sizeScale) : Math.round(root.basePx)
    readonly property color shownColor: root.selRun && root.selRun.colorEnabled ? root.selRun.color
                                                                                : (root.textStyle.color || "#ffffff")

    title: qsTr("Advanced text")
    preferredWidth: 1280
    movable: true
    acceptText: qsTr("Apply")
    rejectText: qsTr("Cancel")
    acceptOnReturn: false

    function openFor(track, clip, id) {
        root.trackIndex = track
        root.clipIndex = clip
        root.clipId = id
        root.selectionStart = -1
        root.selectionEnd = -1
        root.keepEdits = false
        root.maximized = false
        input.text = root.text
        // El texto a la vista: con el cabezal fuera del clip, al principio de él.
        const now = EditorState.playheadSeconds
        if (now < root.clipStart || now >= root.clipStart + root.clipDuration)
            EditorState.playheadSeconds = root.clipStart + Math.min(0.5, root.clipDuration / 2)
        EditorState.playing = false
        EditorState.beginEditSession(qsTr("Advanced text"))
        root.open()
    }

    onAccepted: root.keepEdits = true
    onClosed: {
        typing.stop()
        root.commitTyping()
        if (previewEditor.active)
            previewEditor.commit()
        EditorState.playing = false
        EditorState.endEditSession(root.keepEdits)
        root.trackIndex = -1
    }

    // Si el clip deja de ser el que se abrió (otro clip elegido en la vista previa, otro proyecto),
    // se aplica y se cierra: los tramos son de ese texto.
    Connections {
        target: EditorState
        function onSelectedClipDataChanged() {
            if (!root.visible)
                return
            const data = EditorState.selectedClipData || ({})
            if ((data.id || "") !== root.clipId) {
                root.keepEdits = true
                root.close()
                return
            }
            // Escrito en otra parte (sobre la vista previa): el cuadro lo sigue, salvo mientras
            // se escribe en él.
            if (!input.activeFocus && input.text !== root.text)
                input.text = root.text
        }
        // Reproducir dentro de la ventana es reproducir el texto: al llegar a su final, se para.
        function onPlayheadSecondsChanged() {
            if (root.visible && EditorState.playing
                    && EditorState.playheadSeconds >= root.clipStart + root.clipDuration) {
                EditorState.playing = false
                EditorState.playheadSeconds = root.clipStart + root.clipDuration - 0.001
            }
        }
    }

    // Lo escrito en «Texto de entrada» llega al clip solo, sin botón, un momento después de la
    // última tecla (los tramos se corren con lo escrito).
    Timer {
        id: typing
        interval: 250
        onTriggered: root.commitTyping()
    }

    function commitTyping() {
        if (root.trackIndex < 0)
            return
        const typed = input.text
        if (typed.trim().length > 0 && typed.trim() !== root.text)
            EditorState.setClipTextContent(root.trackIndex, root.clipIndex, typed)
    }

    function setStyle(key, value) {
        const patch = {}
        patch[key] = value
        EditorState.setTextStyle(root.trackIndex, root.clipIndex, patch)
    }

    // La barra: con letras elegidas cambia esas (un tramo, sin quitarles lo que ya tenían); sin
    // nada elegido, el texto entero.
    function format(runKey, runValue, styleKey, styleValue) {
        if (root.trackIndex < 0)
            return
        root.commitTyping()
        if (root.hasSelection) {
            const patch = {}
            patch[runKey] = runValue
            EditorState.patchTextRuns(root.trackIndex, root.clipIndex, root.selectionStart, root.selectionEnd, patch)
        } else if (styleKey.length > 0) {
            root.setStyle(styleKey, styleValue)
        } else {
            // Sin equivalente para todo el bloque (el subrayado fino): un tramo de todo el texto.
            const patch = {}
            patch[runKey] = runValue
            EditorState.patchTextRuns(root.trackIndex, root.clipIndex, 0, root.text.length, patch)
        }
    }

    function timeText(seconds) {
        const s = Math.max(0, seconds)
        const m = Math.floor(s / 60)
        const rest = s - m * 60
        return String(m).padStart(2, "0") + ":" + rest.toFixed(2).padStart(5, "0")
    }

    function takeFieldSelection() {
        if (input.selectionEnd > input.selectionStart) {
            root.selectionStart = input.selectionStart
            root.selectionEnd = input.selectionEnd
        } else if (input.activeFocus) {
            // Un clic sin arrastrar en el cuadro: ya no hay letras elegidas.
            root.selectionStart = -1
            root.selectionEnd = -1
        }
    }

    function takePreviewSelection() {
        if (previewEditor.active && previewEditor.selectionEnd !== previewEditor.selectionStart) {
            root.selectionStart = Math.min(previewEditor.selectionStart, previewEditor.selectionEnd)
            root.selectionEnd = Math.max(previewEditor.selectionStart, previewEditor.selectionEnd)
        }
    }

    contentItem: Item {
        implicitWidth: 1200
        implicitHeight: root.maximized ? root.availableContentHeight : Math.min(720, root.availableContentHeight)

        RowLayout {
            anchors.fill: parent
            spacing: Theme.spacingLg

            // ===== Izquierda: la barra, la vista previa, la reproducción y la línea de tiempo =====
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: Theme.spacingSm

                // --- La barra, como un procesador de textos -------------------------------------
                Flow {
                    Layout.fillWidth: true
                    spacing: Theme.spacingSm

                    FontPicker {
                        width: 190
                        family: root.shownFont
                        onFamilyPicked: family => root.format("fontFamily", family, "fontFamily", family)
                    }

                    ThemedNumberField {
                        width: 84
                        from: 4
                        to: 1000
                        value: root.shownSize
                        unit: "px"
                        onEdited: v => root.format("sizeScale", Math.max(4, v) / root.basePx, "pixelSize", Math.max(4, v))
                    }

                    ThemedToggleButton {
                        width: 34
                        text: "B"
                        checked: root.shownBold
                        tooltip: qsTr("Bold")
                        onClicked: root.format("bold", !root.shownBold, "fontWeight", root.shownBold ? 400 : 700)
                    }

                    ThemedToggleButton {
                        width: 34
                        text: "I"
                        checked: root.shownItalic
                        tooltip: qsTr("Italic")
                        onClicked: root.format("italic", !root.shownItalic, "italic", !root.shownItalic)
                    }

                    ThemedToggleButton {
                        width: 34
                        text: "U"
                        checked: root.shownUnderline
                        tooltip: qsTr("Underline")
                        onClicked: root.format("underline", !root.shownUnderline, "", null)
                    }

                    // El color: el cuadrito muestra el de las letras elegidas (o el del texto).
                    Item {
                        width: Theme.controlHeight
                        height: Theme.controlHeight

                        Rectangle {
                            anchors.centerIn: parent
                            width: 24
                            height: 24
                            radius: Theme.radiusSm
                            color: root.shownColor
                            border.width: 1
                            border.color: Theme.panelBorder
                        }
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                colorPicker.selectedColor = root.shownColor
                                colorPicker.open()
                            }
                        }
                        ToolTip.visible: colorHover.hovered
                        ToolTip.text: qsTr("Text color")
                        HoverHandler { id: colorHover }
                    }

                    ThemedColorDialog {
                        id: colorPicker
                        onAccepted: root.format("color", String(selectedColor), "color", String(selectedColor))
                    }

                    Repeater {
                        model: [
                            { "id": "none", "label": "Aa", "tip": qsTranslate("TextInspector", "As typed") },
                            { "id": "upper", "label": "TT", "tip": qsTranslate("TextInspector", "UPPERCASE") },
                            { "id": "lower", "label": "tt", "tip": qsTranslate("TextInspector", "lowercase") },
                            { "id": "title", "label": "Tt", "tip": qsTranslate("TextInspector", "Title Case") }
                        ]
                        delegate: ThemedToggleButton {
                            required property var modelData
                            width: 36
                            text: modelData.label
                            tooltip: modelData.tip
                            checked: (root.textStyle.textCase || "none") === modelData.id
                            onClicked: root.setStyle("textCase", modelData.id)
                        }
                    }

                    Repeater {
                        model: [
                            { "value": "left", "glyph": Theme.icons.alignLeft, "label": qsTranslate("TextInspector", "Align left") },
                            { "value": "center", "glyph": Theme.icons.alignCenter, "label": qsTranslate("TextInspector", "Align centre") },
                            { "value": "right", "glyph": Theme.icons.alignRight, "label": qsTranslate("TextInspector", "Align right") },
                            { "value": "justify", "glyph": Theme.icons.alignJustify, "label": qsTranslate("TextInspector", "Justify") }
                        ]
                        delegate: ThemedToggleButton {
                            required property var modelData
                            width: 34
                            glyph: modelData.glyph
                            checked: root.textStyle.align === modelData.value
                            tooltip: modelData.label
                            onClicked: root.setStyle("align", modelData.value)
                        }
                    }

                    // Interlineado y espacio entre letras, como los dos números de Filmora.
                    ThemedNumberField {
                        width: 78
                        from: 0.5
                        to: 4
                        step: 0.05
                        decimals: 2
                        value: Number(root.textStyle.lineHeight) || 1.2
                        ToolTip.visible: lineHover.hovered
                        ToolTip.text: qsTr("Line spacing")
                        HoverHandler { id: lineHover }
                        onEdited: v => root.setStyle("lineHeight", v)
                    }

                    ThemedNumberField {
                        width: 78
                        from: -50
                        to: 200
                        value: Number(root.textStyle.letterSpacing) || 0
                        unit: "px"
                        ToolTip.visible: spacingHover.hovered
                        ToolTip.text: qsTr("Letter spacing")
                        HoverHandler { id: spacingHover }
                        onEdited: v => root.setStyle("letterSpacing", v)
                    }
                }

                // --- La vista previa, con las asas del texto ---------------------------------------
                Rectangle {
                    id: stage
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#000000"
                    radius: Theme.radiusSm
                    clip: true

                    readonly property real aspect: {
                        void EditorState.tracksRevision
                        const w = EditorState.projectFile.projectWidth()
                        const h = EditorState.projectFile.projectHeight()
                        return (w > 0 && h > 0) ? (w / h) : (16 / 9)
                    }
                    // Margen para que las asas de un texto pegado al borde no se corten.
                    readonly property real inset: Theme.spacingXl

                    Rectangle {
                        id: canvasRect
                        readonly property real fitWidth: Math.min(stage.width - stage.inset * 2,
                                                                  (stage.height - stage.inset * 2) * stage.aspect)
                        width: Math.max(1, fitWidth)
                        height: Math.max(1, fitWidth / stage.aspect)
                        x: (stage.width - width) / 2
                        y: (stage.height - height) / 2
                        color: Theme.overlayColor
                        clip: true

                        // La misma imagen que la vista previa principal: el compositor dibuja un solo
                        // cuadro para toda la app, aquí se muestra más grande.
                        PreviewItem {
                            id: mirror
                            anchors.fill: parent
                            Component.onCompleted: {
                                mirror.textureSize = EditorState.playback.previewTextureSize
                                mirror.textureId = EditorState.playback.previewTextureId
                            }
                        }

                        Connections {
                            target: EditorState.playback
                            function onCurrentFrameChanged() {
                                mirror.textureSize = EditorState.playback.previewTextureSize
                                mirror.textureId = EditorState.playback.previewTextureId
                            }
                        }
                    }

                    // Mover, cambiar de tamaño y girar, como en la vista previa principal; doble clic
                    // sobre el texto para escribir en él y elegir letras.
                    PreviewToolHost {
                        anchors.fill: parent
                        z: 100
                        canvas: canvasRect
                        visible: !previewEditor.active
                        tools: ({ transform: transformTool })
                    }

                    Component {
                        id: transformTool
                        TransformOverlay {
                            onTextEditRequested: (track, clip) => previewEditor.start(track, clip, false)
                        }
                    }

                    InlineTextEditor {
                        id: previewEditor
                        z: 150
                        canvas: canvasRect
                        onSelectionStartChanged: root.takePreviewSelection()
                        onSelectionEndChanged: root.takePreviewSelection()
                    }
                }

                // --- Reproducir, dentro del clip --------------------------------------------------
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacingSm

                    IconButton {
                        glyph: EditorState.playing ? Theme.icons.pause : Theme.icons.play
                        tooltip: EditorState.playing ? qsTranslate("PreviewTransportBar", "Pause")
                                                     : qsTranslate("PreviewTransportBar", "Play")
                        onClicked: {
                            if (!EditorState.playing
                                    && EditorState.playheadSeconds >= root.clipStart + root.clipDuration - 0.05)
                                EditorState.playheadSeconds = root.clipStart
                            EditorState.playing = !EditorState.playing
                        }
                    }

                    IconButton {
                        glyph: Theme.icons.square
                        tooltip: qsTr("Back to the start")
                        onClicked: {
                            EditorState.playing = false
                            EditorState.playheadSeconds = root.clipStart
                        }
                    }

                    ThemedSlider {
                        Layout.fillWidth: true
                        from: 0
                        to: root.clipDuration
                        value: Math.max(0, Math.min(root.clipDuration, EditorState.playheadSeconds - root.clipStart))
                        onMoved: EditorState.playheadSeconds = root.clipStart + Math.min(value, root.clipDuration - 0.001)
                    }

                    Text {
                        text: root.timeText(EditorState.playheadSeconds - root.clipStart) + " / "
                              + root.timeText(root.clipDuration)
                        color: Theme.foreground
                        font.family: Theme.monoFontFamily || Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSm
                    }
                }

                // --- Su línea de tiempo: el texto como una barra y el cabezal ---------------------
                Rectangle {
                    id: miniTimeline
                    Layout.fillWidth: true
                    Layout.preferredHeight: 64
                    color: Theme.panelBackground
                    radius: Theme.radiusSm
                    border.width: Theme.borderWidth
                    border.color: Theme.panelBorder

                    readonly property real pad: Theme.spacingMd
                    readonly property real usable: width - pad * 2

                    // Las marcas de cada segundo.
                    Repeater {
                        model: Math.min(200, Math.floor(root.clipDuration) + 1)
                        delegate: Rectangle {
                            required property int index
                            x: miniTimeline.pad + miniTimeline.usable * index / root.clipDuration
                            y: 4
                            width: 1
                            height: 8
                            color: Theme.mutedForeground
                            opacity: 0.6
                        }
                    }

                    Rectangle {
                        x: miniTimeline.pad
                        y: 18
                        width: miniTimeline.usable
                        height: miniTimeline.height - 26
                        radius: Theme.radiusSm
                        color: Theme.primary
                        opacity: 0.85

                        Text {
                            anchors.fill: parent
                            anchors.leftMargin: Theme.spacingSm
                            verticalAlignment: Text.AlignVCenter
                            text: root.text.replace(/\n/g, " ")
                            elide: Text.ElideRight
                            color: Theme.primaryForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeSm
                        }
                    }

                    Rectangle {
                        x: miniTimeline.pad + miniTimeline.usable
                           * Math.max(0, Math.min(1, (EditorState.playheadSeconds - root.clipStart) / root.clipDuration)) - 1
                        width: 2
                        height: parent.height
                        color: "#ff4d4d"
                    }

                    MouseArea {
                        anchors.fill: parent
                        function seek(mx) {
                            const f = Math.max(0, Math.min(1, (mx - miniTimeline.pad) / miniTimeline.usable))
                            EditorState.playing = false
                            EditorState.playheadSeconds = root.clipStart + Math.min(f * root.clipDuration,
                                                                                     root.clipDuration - 0.001)
                        }
                        onPressed: (mouse) => seek(mouse.x)
                        onPositionChanged: (mouse) => { if (pressed) seek(mouse.x) }
                    }
                }

                // --- Abajo a la izquierda, como Filmora ------------------------------------------
                Row {
                    spacing: Theme.spacingSm

                    ThemedButton {
                        text: qsTr("Save as custom")
                        tooltip: qsTranslate("TextInspector", "Keep this text's font, colours, background and effects to reuse them")
                        variant: "secondary"
                        glyph: Theme.icons.save
                        onClicked: inspector.saveAsMyStyle()
                    }

                    // El estilo de este texto (fuente, colores, fondo, efectos) a los demás títulos
                    // del proyecto; las letras con color propio de cada uno se quedan.
                    ThemedButton {
                        text: qsTr("Apply changes to all texts")
                        tooltip: qsTr("Give every other text in the project this text's style")
                        variant: "primary"
                        onClicked: {
                            root.commitTyping()
                            EditorState.applyTextStyleToCaptions(root.trackIndex, root.clipIndex, "texts")
                        }
                    }
                }
            }

            // ===== Derecha: Estilo, Personalizar, Animación, Burbuja =====
            Rectangle {
                Layout.preferredWidth: 380
                Layout.fillHeight: true
                color: Theme.panelBackground
                radius: Theme.radiusSm
                border.width: Theme.borderWidth
                border.color: Theme.panelBorder

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingSm
                    spacing: Theme.spacingSm

                    // Las pestañas, subrayadas como en Filmora.
                    Row {
                        Layout.fillWidth: true
                        spacing: Theme.spacingXl
                        leftPadding: Theme.spacingSm

                        Repeater {
                            model: [
                                { id: "style", label: qsTr("Style") },
                                { id: "customize", label: qsTr("Customize") },
                                { id: "animation", label: qsTranslate("TextInspector", "Animation") },
                                { id: "bubble", label: qsTranslate("TextInspector", "Bubble") }
                            ]
                            delegate: Item {
                                required property var modelData
                                readonly property bool current: root.page === modelData.id
                                width: tabText.implicitWidth
                                height: tabText.implicitHeight + Theme.spacingMd

                                Text {
                                    id: tabText
                                    text: parent.modelData.label
                                    color: parent.current ? Theme.primary : Theme.foreground
                                    font.family: Theme.fontFamily
                                    font.pixelSize: Theme.fontSizeSm
                                    font.weight: parent.current ? Font.DemiBold : Font.Normal
                                }
                                Rectangle {
                                    anchors.bottom: parent.bottom
                                    width: parent.width
                                    height: 2
                                    color: Theme.primary
                                    visible: parent.current
                                }
                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.page = parent.modelData.id
                                }
                            }
                        }
                    }

                    Flickable {
                        id: sideScroll
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        contentWidth: width
                        contentHeight: sideColumn.height
                        boundsBehavior: Flickable.StopAtBounds
                        ScrollBar.vertical: AppScrollBar {}

                        Column {
                            id: sideColumn
                            // The always-on scroll bar (12 px) sits over the right edge: leave the
                            // same room the right panel's tabColumn does, or a switch anchored to
                            // parent.right ends up under the bar.
                            x: Theme.pagePadding
                            width: sideScroll.width - Theme.pagePadding * 2 - (Theme.spacingLg + 4)
                            spacing: Theme.spacingMd

                            // --- Personalizar › Texto de entrada: se escribe y se eligen letras ----
                            Column {
                                width: parent.width
                                spacing: Theme.spacingSm
                                visible: root.page === "customize"

                                Text {
                                    text: qsTr("Text input")
                                    color: Theme.foreground
                                    font.family: Theme.fontFamily
                                    font.pixelSize: Theme.fontSizeSm
                                    font.weight: Font.Medium
                                }

                                Rectangle {
                                    width: parent.width
                                    height: 120
                                    color: Theme.panelSecondaryBg
                                    radius: Theme.radiusSm
                                    border.width: input.activeFocus ? Theme.borderWidthFocus : Theme.borderWidth
                                    border.color: input.activeFocus ? Theme.focusRing : Theme.panelBorder

                                    Flickable {
                                        anchors.fill: parent
                                        anchors.margins: Theme.spacingSm
                                        anchors.bottomMargin: Theme.spacingXl
                                        clip: true
                                        contentWidth: width
                                        contentHeight: input.contentHeight

                                        TextArea.flickable: TextArea {
                                            id: input
                                            selectByMouse: true
                                            // Elegir letras y pulsar la barra no pierde lo elegido.
                                            persistentSelection: true
                                            color: Theme.foreground
                                            font.family: Theme.fontFamily
                                            font.pixelSize: Theme.fontSizeBase
                                            wrapMode: TextArea.Wrap
                                            background: null
                                            onTextChanged: {
                                                if (activeFocus)
                                                    typing.restart()
                                            }
                                            onSelectionStartChanged: root.takeFieldSelection()
                                            onSelectionEndChanged: root.takeFieldSelection()
                                        }
                                    }

                                    Text {
                                        anchors.right: parent.right
                                        anchors.bottom: parent.bottom
                                        anchors.margins: Theme.spacingSm
                                        text: input.length + "/1500"
                                        color: Theme.mutedForeground
                                        font.family: Theme.fontFamily
                                        font.pixelSize: Theme.fontSizeXs
                                    }
                                }

                                RowLayout {
                                    width: parent.width
                                    spacing: Theme.spacingSm
                                    visible: root.runs.length > 0

                                    Text {
                                        Layout.fillWidth: true
                                        text: root.runs.length === 1 ? qsTr("1 stretch with its own style")
                                                                     : qsTr("%1 stretches with their own style").arg(root.runs.length)
                                        color: Theme.mutedForeground
                                        font.family: Theme.fontFamily
                                        font.pixelSize: Theme.fontSizeXs
                                        elide: Text.ElideRight
                                    }

                                    ThemedButton {
                                        text: qsTr("Clear all")
                                        variant: "ghost"
                                        onClicked: EditorState.setTextRuns(root.trackIndex, root.clipIndex, [])
                                    }
                                }

                                Rectangle {
                                    width: parent.width
                                    height: Theme.borderWidth
                                    color: Theme.panelBorder
                                }
                            }

                            // --- Las páginas del inspector de Texto, las mismas del panel -------------
                            TextInspector {
                                id: inspector
                                width: parent.width
                                inAdvanced: true
                                // Las letras sombreadas en «Texto de entrada» (de esta ventana) son
                                // las que reciben los estilos de la derecha (0.24).
                                runSelectionStart: root.selectionStart
                                runSelectionEnd: root.selectionEnd
                                textTab: root.page === "style" ? "effects"
                                         : root.page === "animation" ? "animate"
                                         : root.page === "bubble" ? "bubble" : "basic"
                                // «Más estilos», «Burbujas» y compañía cambian la pestaña del inspector
                                // desde dentro, y eso rompe el binding de arriba: la ventana sigue al
                                // inspector para que la pestaña y el panel no se separen.
                                onTextTabChanged: {
                                    if (textTab === "effects" && root.page !== "style")
                                        root.page = "style"
                                    else if (textTab === "animate" && root.page !== "animation")
                                        root.page = "animation"
                                    else if (textTab === "bubble" && root.page !== "bubble")
                                        root.page = "bubble"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
