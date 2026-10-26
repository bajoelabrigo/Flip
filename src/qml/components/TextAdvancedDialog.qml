import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import Drift

// Texto avanzado (0.23, como Filmora): una ventana grande con el texto del clip, donde se
// seleccionan letras con el ratón y se les da su propio color, tamaño, negrita o cursiva. Cada
// tramo es un `TextRun` del estilo (`EditorState.textRuns` / `setTextRuns`); al Aplicar se manda
// todo de una vez, así que deshacerlo es un solo paso. Cancelar no toca el proyecto.
ThemedDialog {
    id: root

    // El clip que se está editando, congelado al abrir: si cambia la selección, se cierra.
    property int trackIndex: -1
    property int clipIndex: -1
    property string clipId: ""
    property string text: ""
    property var runs: []
    property var openedRuns: []
    // Lo que la barra aplicaría a lo seleccionado.
    property color brushColor: "#ff4d4d"
    property real brushSize: 1.0
    property bool brushBold: true
    property bool brushItalic: false

    readonly property bool canApply: selectionStart >= 0 && selectionEnd > selectionStart

    title: qsTr("Advanced text")
    preferredWidth: 980
    acceptText: qsTr("Apply")
    rejectText: qsTr("Cancel")

    function openFor(track, clip, id) {
        root.trackIndex = track
        root.clipIndex = clip
        root.clipId = id
        const data = EditorState.selectedClipData || ({})
        root.text = data.textContent || ""
        root.runs = EditorState.textRuns(track, clip)
        root.openedRuns = JSON.parse(JSON.stringify(root.runs))
        root.open()
    }

    function runFor(start, end) {
        return { "start": start, "end": end, "colorEnabled": false, "color": "#ffffffff",
                 "sizeEnabled": false, "sizeScale": 1.0, "boldEnabled": false, "bold": true,
                 "italicEnabled": false, "italic": true }
    }

    // Lo elegido en el cuadro, en desplazamientos del texto.
    property int selectionStart: -1
    property int selectionEnd: -1

    // Aplica el pincel a lo seleccionado: un tramo nuevo con eso, encima de lo que hubiera.
    function applyBrushToSelection() {
        if (!canApply)
            return
        let run = runFor(selectionStart, selectionEnd)
        run.colorEnabled = true
        run.color = String(root.brushColor)
        if (!qFuzzyCompare(root.brushSize, 1.0)) {
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
        // El nuevo va detrás en la lista: donde se pise con otro, gana este (lo último elegido).
        const next = root.runs.slice()
        next.push(run)
        root.runs = next
    }

    // Lo que la barra dice, en la forma que espera EditorState.applyTextBrushToAllTexts.
    function brushPatch() {
        return {
            "colorEnabled": true,
            "color": String(root.brushColor),
            "sizeEnabled": !qFuzzyCompare(root.brushSize, 1.0),
            "sizeScale": root.brushSize,
            "boldEnabled": root.brushBold,
            "bold": true,
            "italicEnabled": root.brushItalic,
            "italic": true
        }
    }

    // El texto con cada tramo pintado como quedará (color, tamaño, negrita, cursiva), para ver lo
    // elegido mientras se trabaja. Un carácter del texto es un carácter del documento (el salto
    // de línea va como <br>), así que la selección sigue dando desplazamientos del texto.
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
                    css += "font-size:" + Math.round(28 * run.sizeScale) + "px;"
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

    function removeRunAt(index) {
        const next = root.runs.slice()
        next.splice(index, 1)
        root.runs = next
    }

    onAccepted: {
        if (root.trackIndex >= 0)
            EditorState.setTextRuns(root.trackIndex, root.clipIndex, root.runs)
    }
    onRejected: root.runs = root.openedRuns

    // Si el clip deja de ser el que se abrió (otra selección, otro proyecto), se cierra: editar
    // tramos de un texto que ya no es el de la ventana sería un lío.
    Connections {
        target: EditorState
        function onSelectedClipDataChanged() {
            if (!root.visible)
                return
            const data = EditorState.selectedClipData || ({})
            if ((data.id || "") !== root.clipId)
                root.close()
        }
    }

    contentItem: ColumnLayout {
        spacing: Theme.spacingMd

        // --- La barra: lo que se aplica a las letras seleccionadas -------------------------------
        RowLayout {
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

            Item { width: Theme.spacingSm; height: 1 }

            Repeater {
                model: ["#ff4d4d", "#ffd23f", "#4dd2ff", "#7bff6b", "#c47bff", "#ffffff"]

                delegate: Rectangle {
                    required property string modelData
                    width: 26
                    height: 26
                    radius: width / 2
                    color: modelData
                    border.width: String(root.brushColor).toLowerCase() === modelData ? 3 : 1
                    border.color: border.width > 1 ? Theme.foreground : Theme.panelBorder
                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.brushColor = modelData
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

            Item { Layout.fillWidth: true }

            Text {
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

            // El pincel entero (color, tamaño, negrita, cursiva) a todos los textos del proyecto.
            ThemedButton {
                text: qsTr("Apply to all texts")
                variant: "secondary"
                tooltip: qsTr("Puts the bar's color, size and bold or italic on the whole text of every text clip in the project")
                onClicked: {
                    EditorState.applyTextBrushToAllTexts(root.brushPatch())
                    // Ya está en el proyecto (y se deshace aparte): la ventana sigue desde ahí, y
                    // Aplicar no lo pisa con los tramos de cuando se abrió.
                    root.runs = EditorState.textRuns(root.trackIndex, root.clipIndex)
                    root.openedRuns = JSON.parse(JSON.stringify(root.runs))
                }
            }
        }

        // --- El texto: se seleccionan letras y se les da el pincel --------------------------------
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: Theme.panelBackground
            radius: Theme.radiusSm
            border.width: Theme.borderWidth
            border.color: Theme.panelBorder

            Flickable {
                anchors.fill: parent
                anchors.margins: Theme.spacingMd
                clip: true
                contentWidth: width
                contentHeight: editor.contentHeight

                TextArea.flickable: TextArea {
                    id: editor
                    // Solo se lee: el texto se escribe en el inspector; aquí se elige qué letras
                    // llevan su propio estilo.
                    readOnly: true
                    selectByMouse: true
                    textFormat: TextEdit.RichText
                    text: root.previewHtml()
                    color: Theme.foreground
                    font.family: Theme.fontFamily
                    font.pixelSize: 28
                    wrapMode: TextArea.Wrap
                    background: null
                    onSelectionStartChanged: root.selectionStart = selectionStart
                    onSelectionEndChanged: root.selectionEnd = selectionEnd
                }
            }
        }

        // --- Los tramos que hay ---------------------------------------------------------------
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingSm

            Text {
                text: root.runs.length === 0 ? qsTr("No letters with their own style yet.")
                                             : (root.runs.length === 1 ? qsTr("1 stretch with its own style")
                                                                        : qsTr("%1 stretches with their own style").arg(root.runs.length))
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
            }

            Item { Layout.fillWidth: true }

            ThemedButton {
                text: qsTr("Clear all")
                variant: "ghost"
                enabled: root.runs.length > 0
                onClicked: root.runs = []
            }
        }

        Flow {
            Layout.fillWidth: true
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
                            width: 14
                            height: 14
                            radius: 7
                            color: modelData.colorEnabled ? modelData.color : "transparent"
                            border.width: 1
                            border.color: Theme.panelBorder
                        }

                        Text {
                            text: "«" + snippet + "»"
                            color: Theme.foreground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeSm
                        }

                        Text {
                            text: modelData.sizeEnabled ? Math.round(modelData.sizeScale * 100) + " %"
                                  : (modelData.boldEnabled ? qsTr("Bold") : (modelData.italicEnabled ? qsTr("Italic") : ""))
                            color: Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }

                        IconGlyph {
                            glyph: Theme.icons.trash
                            iconSize: Theme.iconSizeSm
                            iconColor: Theme.mutedForeground

                            TapHandler { onTapped: root.removeRunAt(index) }
                        }
                    }
                }
            }
        }
    }
}
