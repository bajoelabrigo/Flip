import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import Drift

// Texto avanzado (0.23, como Filmora): una ventana grande con la vista previa del texto (sus asas
// para moverlo, girarlo y escribir sobre él con doble clic), su propia línea de tiempo y, a la
// derecha, las pestañas Estilo, Personalizar, Animación y Burbuja. Arriba, la barra da color,
// tamaño, negrita o cursiva a las letras elegidas (en «Texto de entrada» o sobre la vista previa):
// cada una es un tramo del estilo (`EditorState.textRuns` / `setTextRuns`).
//
// Todo se edita en vivo y la ventana es una sesión de edición: al Aplicar, lo hecho dentro queda
// como un solo paso de deshacer; Cancelar lo devuelve todo como estaba.
ThemedDialog {
    id: root

    // El clip que se está editando, congelado al abrir: si cambia la selección, se cierra.
    property int trackIndex: -1
    property int clipIndex: -1
    property string clipId: ""
    // Lo que la barra aplica a las letras elegidas.
    property color brushColor: "#ff4d4d"
    property real brushSize: 1.0
    property bool brushBold: true
    property bool brushItalic: false
    // Las letras elegidas, de donde se eligieron por última vez (el cuadro o la vista previa).
    property int selectionStart: -1
    property int selectionEnd: -1
    readonly property bool canApply: selectionStart >= 0 && selectionEnd > selectionStart
    // "style" | "customize" | "animation" | "bubble", como las pestañas de Filmora.
    property string page: "customize"
    property bool keepEdits: false

    readonly property var clipData: EditorState.selectedClipData || ({})
    readonly property string text: root.clipData.textContent || ""
    readonly property var runs: {
        void EditorState.tracksRevision
        void root.clipData
        return root.trackIndex >= 0 ? EditorState.textRuns(root.trackIndex, root.clipIndex) : []
    }
    readonly property real clipStart: Number(root.clipData.start) || 0
    readonly property real clipDuration: Math.max(0.04, Number(root.clipData.duration) || 0)

    title: qsTr("Advanced text")
    preferredWidth: 1280
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
            }
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

    function runFor(start, end) {
        return { "start": start, "end": end, "colorEnabled": false, "color": "#ffffffff",
                 "sizeEnabled": false, "sizeScale": 1.0, "boldEnabled": false, "bold": true,
                 "italicEnabled": false, "italic": true }
    }

    function writeRuns(next) {
        if (root.trackIndex >= 0)
            EditorState.setTextRuns(root.trackIndex, root.clipIndex, next)
    }

    // La barra sobre las letras elegidas: un tramo nuevo, encima de lo que hubiera.
    function applyBrushToSelection() {
        if (!root.canApply)
            return
        const run = root.runFor(root.selectionStart, root.selectionEnd)
        run.colorEnabled = true
        run.color = String(root.brushColor)
        if (!Math.abs(root.brushSize - 1.0) < 1e-6) {
            run.sizeEnabled = true
            run.sizeScale = root.brushSize
        }
        if (root.brushBold) {
            run.boldEnabled = true
            run.bold = true
        }
        if (root.brushItalic) {
            run.italicEnabled = true
            run.italic = true
        }
        // Detrás en la lista: donde se pise con otro, gana este (lo último elegido).
        const next = root.runs.slice()
        next.push(run)
        root.writeRuns(next)
    }

    // Lo que la barra dice, en la forma que espera EditorState.applyTextBrushToAllTexts.
    function brushPatch() {
        return {
            "colorEnabled": true,
            "color": String(root.brushColor),
            "sizeEnabled": !Math.abs(root.brushSize - 1.0) < 1e-6,
            "sizeScale": root.brushSize,
            "boldEnabled": root.brushBold,
            "bold": true,
            "italicEnabled": root.brushItalic,
            "italic": true
        }
    }

    function removeRunAt(index) {
        const next = root.runs.slice()
        next.splice(index, 1)
        root.writeRuns(next)
    }

    // El texto con cada tramo pintado como quedará (color, tamaño, negrita, cursiva). Un carácter
    // del texto es un carácter del documento (el salto de línea va como <br>), así que la
    // selección del cuadro sigue dando desplazamientos del texto.
    function previewHtml() {
        const text = root.text
        const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
                          .replace(/\n/g, "<br>")
        // Por letra, el último tramo de la lista que la cubre (como en el proyecto).
        const owner = new Array(text.length).fill(-1)
        root.runs.forEach((run, i) => {
            for (let at = Math.max(0, run.start); at < Math.min(text.length, run.end); ++at)
                owner[at] = i
        })
        let html = ""
        let at = 0
        while (at < text.length) {
            const who = owner[at]
            let end = at + 1
            while (end < text.length && owner[end] === who)
                ++end
            const piece = esc(text.substring(at, end))
            if (who < 0) {
                html += piece
            } else {
                const run = root.runs[who]
                let css = ""
                if (run.colorEnabled)
                    css += "color:" + String(run.color).replace(/^#ff([0-9a-f]{6})$/i, "#$1") + ";"
                if (run.sizeEnabled)
                    css += "font-size:" + Math.round(22 * run.sizeScale) + "px;"
                if (run.boldEnabled)
                    css += "font-weight:" + (run.bold ? "bold" : "normal") + ";"
                if (run.italicEnabled)
                    css += "font-style:" + (run.italic ? "italic" : "normal") + ";"
                html += "<span style=\"" + css + "\">" + piece + "</span>"
            }
            at = end
        }
        return html
    }

    function timeText(seconds) {
        const s = Math.max(0, seconds)
        const m = Math.floor(s / 60)
        const rest = s - m * 60
        return String(m).padStart(2, "0") + ":" + rest.toFixed(2).padStart(5, "0")
    }

    contentItem: Item {
        implicitWidth: 1200
        implicitHeight: Math.min(720, root.availableContentHeight)

        RowLayout {
            anchors.fill: parent
            spacing: Theme.spacingLg

            // ===== Izquierda: la barra, la vista previa, la reproducción y la línea de tiempo =====
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: Theme.spacingSm

                // --- La barra: lo que se aplica a las letras elegidas --------------------------------
                Flow {
                    Layout.fillWidth: true
                    spacing: Theme.spacingSm

                    ThemedButton {
                        text: qsTr("Bold")
                        variant: root.brushBold ? "primary" : "secondary"
                        onClicked: root.brushBold = !root.brushBold
                    }

                    ThemedButton {
                        text: qsTr("Italic")
                        variant: root.brushItalic ? "primary" : "secondary"
                        onClicked: root.brushItalic = !root.brushItalic
                    }

                    Repeater {
                        model: ["#ff4d4d", "#ffd23f", "#4dd2ff", "#7bff6b", "#c47bff", "#ffffff"]

                        // As tall as the buttons, so the bar's rows line up when it wraps.
                        delegate: Item {
                            id: swatch
                            required property string modelData
                            width: 24
                            height: Theme.controlHeight

                            Rectangle {
                                anchors.centerIn: parent
                                width: 24
                                height: 24
                                radius: width / 2
                                color: swatch.modelData
                                border.width: String(root.brushColor).toLowerCase() === swatch.modelData ? 3 : 1
                                border.color: border.width > 1 ? Theme.foreground : Theme.panelBorder
                            }
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.brushColor = swatch.modelData
                            }
                        }
                    }

                    ThemedColorDialog {
                        id: customColor
                        onAccepted: root.brushColor = selectedColor
                    }

                    ThemedButton {
                        text: qsTr("More colors…")
                        variant: "ghost"
                        onClicked: customColor.open()
                    }

                    Text {
                        height: Theme.controlHeight
                        verticalAlignment: Text.AlignVCenter
                        text: qsTr("Size")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSm
                    }

                    ThemedComboBox {
                        model: ["50 %", "75 %", "100 %", "125 %", "150 %", "200 %", "300 %"]
                        currentIndex: 2
                        onActivated: (index) => root.brushSize = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0][index]
                    }

                    ThemedButton {
                        text: qsTr("Apply to selection")
                        variant: "primary"
                        enabled: root.canApply
                        onClicked: root.applyBrushToSelection()
                    }

                    // La barra entera (color, tamaño, negrita, cursiva) al texto entero de todos los
                    // textos del proyecto.
                    ThemedButton {
                        text: qsTr("Apply to all texts")
                        variant: "secondary"
                        tooltip: qsTr("Puts the bar's color, size and bold or italic on the whole text of every text clip in the project")
                        onClicked: EditorState.applyTextBrushToAllTexts(root.brushPatch())
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

                ThemedButton {
                    text: qsTr("Save as custom")
                    tooltip: qsTranslate("TextInspector", "Keep this text's font, colours, background and effects to reuse them")
                    variant: "secondary"
                    glyph: Theme.icons.save
                    onClicked: inspector.saveAsMyStyle()
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
                            width: sideScroll.width - Theme.spacingMd
                            spacing: Theme.spacingMd

                            // --- Personalizar › Texto de entrada: elegir letras y ver sus estilos ---
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
                                    height: Math.min(160, Math.max(72, letters.contentHeight + Theme.spacingMd * 2))
                                    color: Theme.panelSecondaryBg
                                    radius: Theme.radiusSm
                                    border.width: Theme.borderWidth
                                    border.color: Theme.panelBorder

                                    Flickable {
                                        anchors.fill: parent
                                        anchors.margins: Theme.spacingSm
                                        clip: true
                                        contentWidth: width
                                        contentHeight: letters.contentHeight

                                        TextArea.flickable: TextArea {
                                            id: letters
                                            // Aquí se eligen letras; el texto se escribe sobre la vista
                                            // previa (doble clic) o en Básico.
                                            readOnly: true
                                            selectByMouse: true
                                            textFormat: TextEdit.RichText
                                            text: root.previewHtml()
                                            color: Theme.foreground
                                            font.family: Theme.fontFamily
                                            font.pixelSize: 22
                                            wrapMode: TextArea.Wrap
                                            background: null
                                            onSelectionStartChanged: root.takeFieldSelection()
                                            onSelectionEndChanged: root.takeFieldSelection()
                                        }
                                    }
                                }

                                Text {
                                    width: parent.width
                                    wrapMode: Text.WordWrap
                                    text: qsTr("Select letters here or on the preview (double-click the text), then use the bar above.")
                                    color: Theme.mutedForeground
                                    font.family: Theme.fontFamily
                                    font.pixelSize: Theme.fontSizeXs
                                }

                                RowLayout {
                                    width: parent.width
                                    spacing: Theme.spacingSm

                                    Text {
                                        Layout.fillWidth: true
                                        text: root.runs.length === 0 ? qsTr("No letters with their own style yet.")
                                              : (root.runs.length === 1 ? qsTr("1 stretch with its own style")
                                                 : qsTr("%1 stretches with their own style").arg(root.runs.length))
                                        color: Theme.mutedForeground
                                        font.family: Theme.fontFamily
                                        font.pixelSize: Theme.fontSizeSm
                                        elide: Text.ElideRight
                                    }

                                    ThemedButton {
                                        text: qsTr("Clear all")
                                        variant: "ghost"
                                        enabled: root.runs.length > 0
                                        onClicked: root.writeRuns([])
                                    }
                                }

                                Flow {
                                    width: parent.width
                                    spacing: Theme.spacingSm
                                    visible: root.runs.length > 0

                                    Repeater {
                                        model: root.runs

                                        delegate: Rectangle {
                                            required property var modelData
                                            required property int index
                                            readonly property string snippet: {
                                                const from = Math.max(0, modelData.start)
                                                const to = Math.min(root.text.length, modelData.end)
                                                return root.text.substring(from, to)
                                            }
                                            width: chipRow.width + Theme.spacingMd * 2
                                            height: 30
                                            radius: Theme.radiusSm
                                            color: Theme.panelSecondaryBg
                                            border.width: Theme.borderWidth
                                            border.color: Theme.panelBorder

                                            Row {
                                                id: chipRow
                                                anchors.centerIn: parent
                                                spacing: Theme.spacingSm

                                                Rectangle {
                                                    anchors.verticalCenter: parent.verticalCenter
                                                    width: 14
                                                    height: 14
                                                    radius: 7
                                                    color: modelData.colorEnabled ? modelData.color : "transparent"
                                                    border.width: 1
                                                    border.color: Theme.panelBorder
                                                }

                                                Text {
                                                    anchors.verticalCenter: parent.verticalCenter
                                                    text: "«" + snippet + "»"
                                                    color: Theme.foreground
                                                    font.family: Theme.fontFamily
                                                    font.pixelSize: Theme.fontSizeSm
                                                }

                                                Text {
                                                    anchors.verticalCenter: parent.verticalCenter
                                                    text: modelData.sizeEnabled ? Math.round(modelData.sizeScale * 100) + " %"
                                                          : (modelData.boldEnabled ? qsTr("Bold")
                                                             : (modelData.italicEnabled ? qsTr("Italic") : ""))
                                                    color: Theme.mutedForeground
                                                    font.family: Theme.fontFamily
                                                    font.pixelSize: Theme.fontSizeXs
                                                }

                                                IconGlyph {
                                                    anchors.verticalCenter: parent.verticalCenter
                                                    glyph: Theme.icons.trash
                                                    iconSize: Theme.iconSizeSm
                                                    iconColor: Theme.mutedForeground

                                                    TapHandler { onTapped: root.removeRunAt(index) }
                                                }
                                            }
                                        }
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
                                textTab: root.page === "style" ? "effects"
                                         : root.page === "animation" ? "animate"
                                         : root.page === "bubble" ? "bubble" : "basic"
                            }
                        }
                    }
                }
            }
        }
    }

    function takeFieldSelection() {
        if (letters.selectionEnd > letters.selectionStart) {
            root.selectionStart = letters.selectionStart
            root.selectionEnd = letters.selectionEnd
        }
    }

    function takePreviewSelection() {
        if (previewEditor.active && previewEditor.selectionEnd !== previewEditor.selectionStart) {
            root.selectionStart = Math.min(previewEditor.selectionStart, previewEditor.selectionEnd)
            root.selectionEnd = Math.max(previewEditor.selectionStart, previewEditor.selectionEnd)
        }
    }
}
