import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// The video clip's tools, laid out the way CapCut lays them out: four named pages, each one
// holding what the corresponding CapCut page holds. The inspectors underneath are the same ones
// the rest of the panel uses -- this only decides what appears under which name, so an effect
// added here is the same effect the Effects tab edits.
//
// The page definitions mirror the reference screenshots:
//   Basico          Transformacion, Mezcla, Estabilizacion, Mejorar la calidad, Reducir el ruido,
//                   Flujo optico, Eliminacion/Ampliacion/Remix de IA, Contacto visual,
//                   Sincronizacion labial, Adicion de iluminacion
//   Eliminar fondo  Eliminacion automatica, Eliminacion personalizada, Chroma key
//   Mascara         Mascara (formas) y Agregar mascara
//   Retoque         Rostro / Cuerpo / Cabello, Estilos automaticos, Piel, Funciones, Maquillaje
Item {
    id: root

    // Which of the four pages is open. Owned by PropertiesPanel's inspectorUi so it survives a
    // tab switch, like every other view state in this panel.
    property string page: "basico"

    readonly property var pages: [
        { id: "basico", label: qsTr("Basic") },
        { id: "fondo", label: qsTr("Remove background") },
        { id: "mascara", label: qsTr("Mask") },
        { id: "retoque", label: qsTr("Retouch") }
    ]

    readonly property int pageIndex: Math.max(0, pages.findIndex(p => p.id === root.page))
    readonly property string clipKind: {
        void clipRevision
        const d = EditorState.selectedClipData
        return d && d.kind ? d.kind : ""
    }
    property int clipRevision: 0

    Connections {
        target: EditorState
        function onSelectionChanged() { root.clipRevision++ }
        function onSelectedClipDataChanged() { root.clipRevision++ }
    }

    height: contentCol.height
    implicitHeight: contentCol.height

    function refreshFields() {}

    Column {
        id: contentCol
        width: root.width
        spacing: Theme.spacingXl

        // A segmented strip, like CapCut's: four equal cells with the open one filled.
        Rectangle {
            width: parent.width
            height: strip.height + 6
            radius: Theme.radiusSm
            color: Theme.panelAccent

            Row {
                id: strip
                anchors.centerIn: parent
                width: parent.width - 6
                spacing: 2

                // Every cell as tall as the tallest label: a name that needs two lines in a
                // narrow panel wraps instead of turning into "Quit…".
                // One font size for every label: the largest at which the longest single word
                // ("Máscara") still fits its cell, since a word cannot wrap.
                property real cellHeight: 0
                property real labelPx: Theme.fontSizeXs
                onWidthChanged: Qt.callLater(measure)
                Component.onCompleted: Qt.callLater(measure)
                function measure() {
                    const room = (width - 6) / root.pages.length - 8
                    let px = Theme.fontSizeXs
                    for (const page of root.pages) {
                        for (const word of String(page.label).split(" ")) {
                            wordMetrics.text = word
                            if (room > 0 && wordMetrics.advanceWidth > room)
                                px = Math.min(px, Math.floor(Theme.fontSizeXs * room / wordMetrics.advanceWidth))
                        }
                    }
                    labelPx = Math.max(8, px)
                    let h = 0
                    for (let i = 0; i < stripCells.count; i++) {
                        const cell = stripCells.itemAt(i)
                        if (cell)
                            h = Math.max(h, cell.labelHeight)
                    }
                    cellHeight = h + 14
                }

                TextMetrics {
                    id: wordMetrics
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                    font.weight: Font.Medium
                }

                Repeater {
                    id: stripCells
                    model: root.pages
                    delegate: Rectangle {
                        required property var modelData
                        required property int index
                        readonly property real labelHeight: stripLabel.implicitHeight
                        onLabelHeightChanged: Qt.callLater(strip.measure)
                        width: (strip.width - 6) / root.pages.length
                        height: strip.cellHeight
                        radius: Theme.radiusSm
                        color: index === root.pageIndex ? Theme.popoverHover : "transparent"

                        Text {
                            id: stripLabel
                            anchors.centerIn: parent
                            width: parent.width - 8
                            horizontalAlignment: Text.AlignHCenter
                            wrapMode: Text.WordWrap
                            maximumLineCount: 2
                            elide: Text.ElideRight
                            text: modelData.label
                            color: index === root.pageIndex ? Theme.foreground : Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: strip.labelPx
                            font.weight: index === root.pageIndex ? Font.Medium : Font.Normal
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: root.page = modelData.id
                        }
                    }
                }
            }
        }

        // --- Basico -------------------------------------------------------------------------
        Column {
            visible: root.page === "basico"
            width: parent.width
            spacing: Theme.spacingXl

            TransformInspector {
                width: parent.width
                sizeLinked: EditorState.sizeLinked
                onSizeLinkedChanged: EditorState.sizeLinked = sizeLinked
                positionLinked: EditorState.positionLinked
                onPositionLinkedChanged: EditorState.positionLinked = positionLinked
            }

            BlendingInspector { width: parent.width }

            StabilizeInspector { width: parent.width }

            // Mejorar la calidad, reducir el ruido, la iluminacion 3D y el resto de efectos de IA
            // viven en el catalogo, asi que la pestana de efectos es la que los ofrece. Se deja
            // entera para no tener dos listas de efectos que puedan discrepar.
            EffectsInspector { width: parent.width }
        }

        // --- Eliminar fondo ----------------------------------------------------------------
        Column {
            id: fondoPage
            visible: root.page === "fondo"
            width: parent.width
            spacing: Theme.spacingLg

            readonly property bool runtimeReady: Addons.runtimeAvailable()
            readonly property bool segmentReady: EditorState.segmentation.available()

            Connections {
                target: Addons
                function onKindChanged(kind) {
                    if (kind === "sam2-model" || kind === "rvm-model" || kind === "onnxruntime")
                        fondoPage.segmentReady = EditorState.segmentation.available()
                }
            }

            Text {
                width: parent.width
                text: qsTr("Automatic removal")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            ThemedButton {
                width: parent.width
                text: qsTr("Cut out people…")
                enabled: root.clipKind === "video" && EditorState.segmentation.available()
                         && Addons.runtimeAvailable() && !EditorState.segmentation.running
                tooltip: root.clipKind === "video"
                         ? qsTr("Finds the people in the clip and removes the background")
                         : qsTr("Select a video clip first")
                onClicked: {
                    const d = EditorState.selectedClipData
                    root.Window.window.openSegmentation(EditorState.selectedTrack,
                                                        EditorState.selectedClip,
                                                        d.start || 0, d.duration || 0)
                }
            }

            Text {
                visible: !root.clipKind || root.clipKind !== "video"
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("Select a video clip to remove its background.")
                color: Theme.warning
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            Text {
                width: parent.width
                text: qsTr("Custom removal")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
                topPadding: Theme.spacingLg
            }

            ThemedButton {
                width: parent.width
                text: qsTr("Cut out a subject…")
                enabled: root.clipKind === "video" && EditorState.segmentation.available()
                         && Addons.runtimeAvailable() && !EditorState.segmentation.running
                tooltip: qsTr("Mark with a click what you want to keep and it follows it")
                onClicked: {
                    const d = EditorState.selectedClipData
                    root.Window.window.openSegmentation(EditorState.selectedTrack,
                                                        EditorState.selectedClip,
                                                        d.start || 0, d.duration || 0)
                }
            }

            Text {
                width: parent.width
                text: qsTr("Chroma key")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
                topPadding: Theme.spacingLg
            }

            ThemedButton {
                width: parent.width
                text: qsTr("Remove a colour")
                enabled: root.clipKind === "video"
                tooltip: qsTr("Adds Chroma Key, with the colour and tolerance to tune in Effects")
                onClicked: EditorState.addEffect(EditorState.selectedTrack,
                                                 EditorState.selectedClip,
                                                 "chroma_key")
            }

            // An image or a video as the coverage map is the third way to remove a background, and
            // it needs a file rather than a model. Same dialog and call the assets panel uses.
            ThemedButton {
                width: parent.width
                text: qsTr("Image or video as mask…")
                enabled: root.clipKind === "video"
                tooltip: qsTr("Use a file's own pixels as the coverage map")
                onClicked: {
                    const url = FileDialogs.openFile(
                        qsTr("Choose a mask image or video"),
                        [qsTr("Media files (*.png *.jpg *.jpeg *.webp *.heic *.heif *.avif *.tif *.tiff *.bmp *.gif *.mp4 *.mov *.mkv *.webm)"),
                         qsTr("All files (*)")])
                    if (!url || url.toString() === "")
                        return
                    EditorState.addMediaMaskToClip(EditorState.selectedTrack,
                                                   EditorState.selectedClip, url)
                }
            }
        }

        // --- Mascara -----------------------------------------------------------------------
        Column {
            visible: root.page === "mascara"
            width: parent.width
            spacing: Theme.spacingLg

            Text {
                width: parent.width
                text: qsTr("Add mask")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            Grid {
                width: parent.width
                columns: 3
                spacing: Theme.spacingSm
                readonly property real cell: (width - spacing * 2) / 3

                Repeater {
                    model: EditorState.maskCatalog()
                    delegate: ThemedButton {
                        required property var modelData
                        width: parent.cell
                        text: modelData.label
                        enabled: root.clipKind === "video"
                        onClicked: EditorState.addMaskToClip(EditorState.selectedTrack,
                                                             EditorState.selectedClip,
                                                             modelData.id)
                    }
                }
            }

            // The mask's own scalars, plus the list of masks already on the clip.
            MasksInspector { width: parent.width }
        }

        // --- Retoque -----------------------------------------------------------------------
        // Laid out like CapCut's Retouch page: Face / Body / Hair across the top, and under Face
        // the auto styles, skin, features and makeup. Most entries are presets of face_retouch
        // (one shader with every skin and makeup control), so they reuse the retouch already on
        // the clip rather than stacking a second one.
        Column {
            id: retoquePage
            visible: root.page === "retoque"
            width: parent.width
            spacing: Theme.spacingLg

            property string area: "rostro"
            readonly property var areas: [
                { id: "rostro", label: qsTr("Face") },
                { id: "cuerpo", label: qsTr("Body") },
                { id: "cabello", label: qsTr("Hair") }
            ]

            // values: face_retouch parameters to set; effect: a separate catalog effect instead.
            readonly property var sections: [
                { title: qsTr("Auto styles"), items: [
                    { label: qsTr("Natural"), hint: qsTr("Light smoothing and a touch of brightness"),
                      values: { smoothing: 0.45, whitening: 0.2, sharpen: 0.2, slimFace: 0.1, bigEyes: 0.1 } },
                    { label: qsTr("Soft"), hint: qsTr("Strong smoothing for an even, soft skin"),
                      values: { smoothing: 0.75, whitening: 0.3, sharpen: 0.1, slimFace: 0.1, bigEyes: 0.1 } },
                    { label: qsTr("Radiant"), hint: qsTr("Brighter, glowing skin"),
                      values: { smoothing: 0.55, whitening: 0.55, sharpen: 0.25, slimFace: 0.1, bigEyes: 0.1 } },
                    { label: qsTr("Defined"), hint: qsTr("Crisper features and a slimmer face"),
                      values: { smoothing: 0.35, whitening: 0.15, sharpen: 0.5, slimFace: 0.25, bigEyes: 0.15 } }
                ] },
                { title: qsTr("Skin"), items: [
                    { label: qsTr("Smooth"), hint: qsTr("Evens out the skin"), values: { smoothing: 0.7 } },
                    { label: qsTr("Whiten"), hint: qsTr("Brightens the skin"), values: { whitening: 0.5 } },
                    { label: qsTr("Skin tone"), hint: qsTr("Warms the skin towards the tone colour"), values: { skinTone: 0.5 } },
                    { label: qsTr("Sharpen"), hint: qsTr("Brings back detail after smoothing"), values: { sharpen: 0.5 } }
                ] },
                { title: qsTr("Features"), items: [
                    { label: qsTr("Slim face"), hint: qsTr("Narrows the jaw and cheeks"), values: { slimFace: 0.45 } },
                    { label: qsTr("Bigger eyes"), hint: qsTr("Enlarges the eyes the mesh found"), effect: "face_big_eyes" },
                    { label: qsTr("Face width"), hint: qsTr("Slim or widen what the mesh follows"), effect: "face_fat_slim" },
                    { label: qsTr("Wide mouth"), hint: qsTr("Widens the mouth"), effect: "face_wide_mouth" },
                    { label: qsTr("Whiten teeth"), hint: qsTr("Needs the lip contour from a face scan"), effect: "face_teeth_whiten" }
                ] },
                { title: qsTr("Makeup"), items: [
                    { label: qsTr("Lipstick"), hint: qsTr("Colours the lips"), values: { lipstick: 0.6 } },
                    { label: qsTr("Blush"), hint: qsTr("Adds colour to the cheeks"), values: { blush: 0.5 } },
                    { label: qsTr("Eyeliner"), hint: qsTr("Draws along the eyelid contour"), effect: "face_eyeliner" },
                    { label: qsTr("Eyeshadow"), hint: qsTr("Colours the eyelid"), effect: "face_eyeshadow" },
                    { label: qsTr("Brow tint"), hint: qsTr("Colours the eyebrows"), effect: "face_brow_tint" },
                    { label: qsTr("Eye colour"), hint: qsTr("Recolours the iris"), effect: "face_eye_color" }
                ] }
            ]

            readonly property bool faceReady: EditorState.faces.available() && Addons.runtimeAvailable()
            readonly property bool canTrack: {
                void root.clipRevision
                const d = EditorState.selectedClipData
                return !!d && d.kind === "video"
            }

            Connections {
                target: Addons
                function onKindChanged(kind) {
                    if (kind === "face-model" || kind === "onnxruntime")
                        retoquePage.faceReady = EditorState.faces.available() && Addons.runtimeAvailable()
                }
            }

            // Adds `effectId`, or reuses the one the selection already carries, then sets
            // `values` on it. addEffect moves the selection to whatever hosts the stack, so the
            // indices are read back after it.
            function findLast(effectId) {
                const effects = EditorState.selectedClipEffects || []
                for (let i = effects.length - 1; i >= 0; i--) {
                    if (effects[i].catalogId === effectId)
                        return i
                }
                return -1
            }

            function apply(effectId, values) {
                let index = findLast(effectId)
                if (index < 0) {
                    EditorState.addEffect(EditorState.selectedTrack, EditorState.selectedClip, effectId)
                    index = findLast(effectId)
                }
                if (index < 0 || !values)
                    return
                for (const key in values)
                    EditorState.setEffectParam(EditorState.selectedTrack, EditorState.selectedClip,
                                               index, key, values[key])
            }

            // Face / Body / Hair, drawn like the page strip above.
            Rectangle {
                width: parent.width
                height: areaStrip.height + 6
                radius: Theme.radiusSm
                color: Theme.panelAccent

                Row {
                    id: areaStrip
                    anchors.centerIn: parent
                    width: parent.width - 6
                    spacing: 2

                    Repeater {
                        model: retoquePage.areas
                        delegate: Rectangle {
                            id: areaCell
                            required property var modelData
                            readonly property bool current: retoquePage.area === modelData.id
                            width: (areaStrip.width - 4) / retoquePage.areas.length
                            height: areaLabel.implicitHeight + 12
                            radius: Theme.radiusSm
                            color: current ? Theme.popoverHover : "transparent"

                            Text {
                                id: areaLabel
                                anchors.centerIn: parent
                                text: areaCell.modelData.label
                                color: areaCell.current ? Theme.foreground : Theme.mutedForeground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeXs
                                font.weight: areaCell.current ? Font.Medium : Font.Normal
                            }

                            MouseArea {
                                anchors.fill: parent
                                onClicked: retoquePage.area = areaCell.modelData.id
                            }
                        }
                    }
                }
            }

            Text {
                visible: retoquePage.area !== "rostro"
                width: parent.width
                wrapMode: Text.WordWrap
                text: retoquePage.area === "cuerpo"
                      ? qsTr("Body retouching (slimmer waist, longer legs and so on) needs a body-tracking model, which Flip Studio does not have yet.")
                      : qsTr("Hair colour and volume need a hair segmentation model, which Flip Studio does not have yet.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            Text {
                visible: retoquePage.area === "rostro" && !retoquePage.canTrack
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("Select a video clip to retouch a face.")
                color: Theme.warning
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            Text {
                visible: retoquePage.area === "rostro" && retoquePage.canTrack && !retoquePage.faceReady
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("Install Face retouch from Extras (it needs the AI engine) to use these.")
                color: Theme.warning
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            Repeater {
                model: retoquePage.area === "rostro" ? retoquePage.sections : []
                delegate: Column {
                    id: section
                    required property var modelData
                    width: retoquePage.width
                    spacing: Theme.spacingSm

                    Text {
                        text: section.modelData.title
                        color: Theme.foreground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSm
                        font.weight: Font.Medium
                    }

                    Grid {
                        id: tiles
                        width: parent.width
                        // One column when the panel is too narrow for "Adelgazar rostro" twice.
                        columns: width >= 280 ? 2 : 1
                        columnSpacing: Theme.spacingSm
                        rowSpacing: Theme.spacingSm

                        Repeater {
                            model: section.modelData.items
                            delegate: ThemedButton {
                                required property var modelData
                                width: (tiles.width - tiles.columnSpacing * (tiles.columns - 1)) / tiles.columns
                                text: modelData.label
                                tooltip: modelData.hint
                                enabled: retoquePage.canTrack && retoquePage.faceReady
                                onClicked: retoquePage.apply(modelData.effect || "face_retouch",
                                                             modelData.values)
                            }
                        }
                    }
                }
            }

            Text {
                width: parent.width
                topPadding: Theme.spacingLg
                text: qsTr("What the clip already carries")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            // The parameters of whatever is in the stack, plus the face scan button. Same UI the
            // Effects tab shows: a second copy of it is how the two would drift apart.
            EffectsInspector { width: parent.width }
        }
    }
}
