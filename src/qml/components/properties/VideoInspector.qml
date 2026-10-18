import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."
import "../assets"

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
    // Face / Body / Hair on the Retouch page; kept by the panel across reloads like `page`.
    property string retouchArea: "rostro"

    readonly property var pages: [
        { id: "basico", label: qsTr("Basic") },
        { id: "fondo", label: qsTr("Remove background"),
          ai: qsTr("Cuts out the person or the subject from the background, frame by frame.") },
        { id: "mascara", label: qsTr("Mask") },
        { id: "retoque", label: qsTr("Retouch"),
          ai: qsTr("Finds the face, the body and the hair to retouch them.") }
    ]

    readonly property int pageIndex: Math.max(0, pages.findIndex(p => p.id === root.page))
    readonly property string clipKind: {
        void clipRevision
        const d = EditorState.selectedClipData
        return d && d.kind ? d.kind : ""
    }
    property int clipRevision: 0
    // Photos get every page too: masks, cutouts and retouch all work on a still.
    readonly property bool visual: clipKind === "video" || clipKind === "image"

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

                        AiBadge {
                            visible: !!modelData.ai
                            compact: true
                            info: modelData.ai || ""
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.rightMargin: 3
                            anchors.topMargin: 1
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

            // Stabilizing follows motion over time; a photo has none.
            StabilizeInspector {
                width: parent.width
                visible: root.clipKind === "video"
            }

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

            // A titled section with its icon, as CapCut heads each one.
            Row {
                width: parent.width
                spacing: Theme.spacingSm

                IconGlyph {
                    glyph: Theme.icons.cutoutPeople
                    iconSize: 16
                    iconColor: Theme.foreground
                    anchors.verticalCenter: parent.verticalCenter
                }
                Text {
                    text: qsTr("Automatic removal")
                    color: Theme.foreground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSm
                    font.weight: Font.Medium
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            ThemedButton {
                width: parent.width
                text: qsTr("Cut out people…")
                glyph: Theme.icons.cutoutPeople
                enabled: root.visual && EditorState.segmentation.available()
                         && Addons.runtimeAvailable() && !EditorState.segmentation.running
                tooltip: root.visual
                         ? qsTr("Finds the people in the clip and removes the background")
                         : qsTr("Select a video or image clip first")
                onClicked: {
                    const d = EditorState.selectedClipData
                    root.Window.window.openSegmentation(EditorState.selectedTrack,
                                                        EditorState.selectedClip,
                                                        d.start || 0, d.duration || 0)
                }
            }

            Text {
                visible: !root.visual
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("Select a video or image clip to remove its background.")
                color: Theme.warning
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            // A titled section with its icon, as CapCut heads each one.
            Row {
                width: parent.width
                spacing: Theme.spacingSm
                topPadding: Theme.spacingLg

                IconGlyph {
                    glyph: Theme.icons.cutoutSubject
                    iconSize: 16
                    iconColor: Theme.foreground
                    anchors.verticalCenter: parent.verticalCenter
                }
                Text {
                    text: qsTr("Custom removal")
                    color: Theme.foreground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSm
                    font.weight: Font.Medium
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            ThemedButton {
                width: parent.width
                text: qsTr("Cut out a subject…")
                glyph: Theme.icons.cutoutSubject
                enabled: root.visual && EditorState.segmentation.available()
                         && Addons.runtimeAvailable() && !EditorState.segmentation.running
                tooltip: qsTr("Mark with a click what you want to keep and it follows it")
                onClicked: {
                    const d = EditorState.selectedClipData
                    root.Window.window.openSegmentation(EditorState.selectedTrack,
                                                        EditorState.selectedClip,
                                                        d.start || 0, d.duration || 0)
                }
            }

            // A titled section with its icon, as CapCut heads each one.
            Row {
                width: parent.width
                spacing: Theme.spacingSm
                topPadding: Theme.spacingLg

                IconGlyph {
                    glyph: Theme.icons.chromaKey
                    iconSize: 16
                    iconColor: Theme.foreground
                    anchors.verticalCenter: parent.verticalCenter
                }
                Text {
                    text: qsTr("Chroma key")
                    color: Theme.foreground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSm
                    font.weight: Font.Medium
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            ThemedButton {
                width: parent.width
                text: qsTr("Remove a colour")
                glyph: Theme.icons.chromaKey
                enabled: root.visual
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
                glyph: Theme.icons.imageMask
                enabled: root.visual
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
        // CapCut's page: the clip's masks, the shape tiles and the settings, edited in place.
        VideoMaskPage {
            visible: root.page === "mascara"
            width: parent.width
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

            property alias area: root.retouchArea
            readonly property var areas: [
                { id: "rostro", label: qsTr("Face"), glyph: Theme.icons.face },
                { id: "cuerpo", label: qsTr("Body"), glyph: Theme.icons.body },
                { id: "cabello", label: qsTr("Hair"), glyph: Theme.icons.hair }
            ]

            // values: face_retouch parameters to set; effect: a separate catalog effect instead.
            readonly property var sections: [
                { title: qsTr("Auto styles"), glyph: Theme.icons.autoStyle, items: [
                    { id: "auto-natural", label: qsTr("Natural"), hint: qsTr("Light smoothing and a touch of brightness"),
                      values: { smoothing: 0.45, whitening: 0.2, sharpen: 0.2, slimFace: 0.1, bigEyes: 0.1 } },
                    { id: "auto-soft", label: qsTr("Soft"), hint: qsTr("Strong smoothing for an even, soft skin"),
                      values: { smoothing: 0.75, whitening: 0.3, sharpen: 0.1, slimFace: 0.1, bigEyes: 0.1 } },
                    { id: "auto-radiant", label: qsTr("Radiant"), hint: qsTr("Brighter, glowing skin"),
                      values: { smoothing: 0.55, whitening: 0.55, sharpen: 0.25, slimFace: 0.1, bigEyes: 0.1 } },
                    { id: "auto-defined", label: qsTr("Defined"), hint: qsTr("Crisper features and a slimmer face"),
                      values: { smoothing: 0.35, whitening: 0.15, sharpen: 0.5, slimFace: 0.25, bigEyes: 0.15 } }
                ] },
                { title: qsTr("Skin"), glyph: Theme.icons.skin, items: [
                    { id: "skin-smooth", label: qsTr("Smooth"), hint: qsTr("Evens out the skin"), values: { smoothing: 0.7 } },
                    { id: "skin-blemish", label: qsTr("Blemishes"), hint: qsTr("Evens out spots, pimples and fine wrinkles"), effect: "face_blemish" },
                    { id: "skin-whiten", label: qsTr("Whiten"), hint: qsTr("Brightens the skin"), values: { whitening: 0.5 } },
                    { id: "skin-tone", label: qsTr("Skin tone"), hint: qsTr("Warms the skin towards the tone colour"), values: { skinTone: 0.5 } },
                    { id: "skin-sharpen", label: qsTr("Sharpen"), hint: qsTr("Brings back detail after smoothing"), values: { sharpen: 0.5 } }
                ] },
                { title: qsTr("Features"), glyph: Theme.icons.features, items: [
                    { id: "slim-face", label: qsTr("Slim face"), hint: qsTr("Narrows the jaw and cheeks"), values: { slimFace: 0.45 } },
                    { id: "big-eyes", label: qsTr("Bigger eyes"), hint: qsTr("Enlarges the eyes the mesh found"), effect: "face_big_eyes" },
                    { id: "face-width", label: qsTr("Face width"), hint: qsTr("Slim or widen what the mesh follows"), effect: "face_fat_slim" },
                    { id: "wide-mouth", label: qsTr("Wide mouth"), hint: qsTr("Widens the mouth"), effect: "face_wide_mouth" },
                    { id: "whiten-teeth", label: qsTr("Whiten teeth"), hint: qsTr("Needs the lip contour from a face scan"), effect: "face_teeth_whiten" }
                ] },
                { title: qsTr("Makeup"), glyph: Theme.icons.makeup, items: [
                    { id: "lipstick", label: qsTr("Lipstick"), hint: qsTr("Colours the lips"), values: { lipstick: 0.6 } },
                    { id: "blush", label: qsTr("Blush"), hint: qsTr("Adds colour to the cheeks"), values: { blush: 0.5 } },
                    { id: "eyeliner", label: qsTr("Eyeliner"), hint: qsTr("Draws along the eyelid contour"), effect: "face_eyeliner" },
                    { id: "eyeshadow", label: qsTr("Eyeshadow"), hint: qsTr("Colours the eyelid"), effect: "face_eyeshadow" },
                    { id: "brow-tint", label: qsTr("Brow tint"), hint: qsTr("Colours the eyebrows"), effect: "face_brow_tint" },
                    { id: "eye-colour", label: qsTr("Eye colour"), hint: qsTr("Recolours the iris"), effect: "face_eye_color" }
                ] }
            ]

            // Body: presets of body.reshape. Adding it starts the body analysis when the clip has none.
            readonly property var bodySections: [
                { title: qsTr("Body"), glyph: Theme.icons.body, items: [
                    { id: "body-slim", label: qsTr("Slim"), hint: qsTr("Slims the whole body"), effect: "body.reshape", values: { slim: 0.8 } },
                    { id: "body-waist", label: qsTr("Waist"), hint: qsTr("Narrows the waist"), effect: "body.reshape", values: { waist: 0.8 } },
                    { id: "body-legs", label: qsTr("Longer legs"), hint: qsTr("Lengthens the legs below the hips"), effect: "body.reshape", values: { legs: 0.7 } },
                    { id: "body-shoulders", label: qsTr("Shoulders"), hint: qsTr("Widens the shoulders"), effect: "body.reshape", values: { shoulders: 0.7 } },
                    { id: "body-head", label: qsTr("Smaller head"), hint: qsTr("Makes the head a little smaller"), effect: "body.reshape", values: { head: -0.6 } }
                ] }
            ]

            // Starred tiles, shown first as their own section, like the favorites of the library.
            property int favoritesTick: 0
            readonly property var favoriteItems: {
                void favoritesTick
                const out = []
                for (const section of sections) {
                    for (const item of section.items) {
                        if (EditorState.isAssetFavorite("retouch", item.id))
                            out.push(item)
                    }
                }
                return out
            }
            readonly property var shownSections: favoriteItems.length > 0
                                                 ? [{ title: qsTr("Favorites"), glyph: Theme.icons.star, items: favoriteItems }].concat(sections)
                                                 : sections

            Connections {
                target: EditorState
                function onAssetFavoritesChanged() { retoquePage.favoritesTick++ }
            }

            property bool faceReady: EditorState.faces.available() && Addons.runtimeAvailable()
            property bool bodyReady: EditorState.body.available() && Addons.runtimeAvailable()
            readonly property bool canTrack: {
                void root.clipRevision
                const d = EditorState.selectedClipData
                return !!d && (d.kind === "video" || d.kind === "image")
            }

            Connections {
                target: Addons
                function onKindChanged(kind) {
                    if (kind === "face-model" || kind === "onnxruntime")
                        retoquePage.faceReady = EditorState.faces.available() && Addons.runtimeAvailable()
                    if (kind === "body-model" || kind === "onnxruntime")
                        retoquePage.bodyReady = EditorState.body.available() && Addons.runtimeAvailable()
                }
            }

            // Adds `effectId`, or reuses the one the clip already carries, then sets `values` on it.
            // Done in C++: adding moves the selection, which unloads this tab mid-call.
            function apply(effectId, values) {
                EditorState.applyRetouchLook(EditorState.selectedTrack, EditorState.selectedClip, effectId,
                                             values || {})
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

                            IconGlyph {
                                anchors.right: areaLabel.left
                                anchors.rightMargin: 6
                                anchors.verticalCenter: parent.verticalCenter
                                glyph: areaCell.modelData.glyph
                                iconSize: 14
                                iconColor: areaCell.current ? Theme.foreground : Theme.mutedForeground
                            }

                            Text {
                                id: areaLabel
                                anchors.centerIn: parent
                                anchors.horizontalCenterOffset: 10
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
                visible: retoquePage.area !== "rostro" && !retoquePage.canTrack
                width: parent.width
                wrapMode: Text.WordWrap
                text: retoquePage.area === "cuerpo"
                      ? qsTr("Select a video or image clip to retouch a body.")
                      : qsTr("Select a video or image clip to colour the hair.")
                color: Theme.warning
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            Text {
                visible: retoquePage.area !== "rostro" && retoquePage.canTrack && !retoquePage.bodyReady
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("Install Body and hair retouch from Extras (it needs the AI engine) to use these.")
                color: Theme.warning
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            // --- Cuerpo: the analysis the body warps follow. The tiles are in the grid below.
            Column {
                id: bodySection
                visible: retoquePage.area === "cuerpo"
                width: parent.width
                spacing: Theme.spacingSm

                readonly property bool analysed: {
                    void root.clipRevision
                    const d = EditorState.selectedClipData
                    return !!d && !!d.hasPoseTrack
                }

                Text {
                    width: parent.width
                    wrapMode: Text.WordWrap
                    visible: retoquePage.canTrack && retoquePage.bodyReady && !EditorState.body.running
                    text: bodySection.analysed
                          ? qsTr("The body in this clip is analysed: the sliders below follow it.")
                          : qsTr("Pick a look: the clip is analysed first, so the warps know where the body is.")
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                }

                ThemedButton {
                    visible: retoquePage.canTrack && retoquePage.bodyReady && !EditorState.body.running
                    width: parent.width
                    text: bodySection.analysed ? qsTr("Analyse the body again") : qsTr("Analyse body")
                    variant: bodySection.analysed ? "ghost" : "secondary"
                    onClicked: EditorState.body.analyzeBody(EditorState.selectedTrack, EditorState.selectedClip)
                }
            }

            // --- Cabello: colour swatches. The first one finds the hair; the rest only recolour.
            Column {
                id: hairSection
                visible: retoquePage.area === "cabello"
                width: parent.width
                spacing: Theme.spacingSm

                readonly property var current: {
                    void root.clipRevision
                    return retoquePage.canTrack
                           ? EditorState.body.hairColor(EditorState.selectedTrack, EditorState.selectedClip)
                           : ({})
                }
                readonly property bool coloured: !!current.shade
                readonly property bool usable: retoquePage.canTrack && retoquePage.bodyReady
                                               && !EditorState.body.running
                readonly property var shades: [
                    { id: "hair-black", label: qsTr("Black"), color: "#1f1a17" },
                    { id: "hair-brown", label: qsTr("Brown"), color: "#5a3825" },
                    { id: "hair-chocolate", label: qsTr("Chocolate"), color: "#3e2418" },
                    { id: "hair-caramel", label: qsTr("Caramel"), color: "#a3672f" },
                    { id: "hair-blonde", label: qsTr("Blonde"), color: "#d8b06a" },
                    { id: "hair-platinum", label: qsTr("Platinum"), color: "#e6dfcc" },
                    { id: "hair-copper", label: qsTr("Copper"), color: "#b4542a" },
                    { id: "hair-red", label: qsTr("Red"), color: "#a3192d" },
                    { id: "hair-pink", label: qsTr("Pink"), color: "#e27aa8" },
                    { id: "hair-lilac", label: qsTr("Lilac"), color: "#9c80d8" },
                    { id: "hair-blue", label: qsTr("Blue"), color: "#3c6fd2" },
                    { id: "hair-mint", label: qsTr("Mint"), color: "#5fc4a8" }
                ]

                Text {
                    width: parent.width
                    wrapMode: Text.WordWrap
                    visible: retoquePage.canTrack && retoquePage.bodyReady
                    text: hairSection.coloured
                          ? qsTr("Pick another colour to change it. Strength and lightening are on the Hair colour row of the timeline.")
                          : qsTr("Pick a colour: the hair is found in every frame first, which takes a moment.")
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                }

                Grid {
                    id: swatches
                    width: parent.width
                    columns: Math.max(4, Math.floor((width + columnSpacing) / (56 + columnSpacing)))
                    columnSpacing: Theme.spacingSm
                    rowSpacing: Theme.spacingMd

                    Repeater {
                        model: hairSection.shades
                        delegate: Column {
                            id: swatch
                            required property var modelData
                            readonly property bool picked: hairSection.coloured
                                                           && hairSection.current.shade.toLowerCase() === modelData.color
                            width: (swatches.width - swatches.columnSpacing * (swatches.columns - 1)) / swatches.columns
                            spacing: 4
                            opacity: hairSection.usable ? 1 : 0.55

                            Rectangle {
                                anchors.horizontalCenter: parent.horizontalCenter
                                width: Math.min(parent.width, 44)
                                height: width
                                radius: width / 2
                                color: swatch.modelData.color
                                border.width: swatch.picked || swatchHover.hovered ? 2 : 1
                                border.color: swatch.picked ? Theme.primary
                                              : swatchHover.hovered ? Theme.foreground : Theme.panelBorder

                                HoverHandler { id: swatchHover }

                                MouseArea {
                                    anchors.fill: parent
                                    enabled: hairSection.usable
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: EditorState.body.colorHair(EditorState.selectedTrack,
                                                                          EditorState.selectedClip,
                                                                          swatch.modelData.color)
                                }
                            }

                            Text {
                                width: parent.width
                                horizontalAlignment: Text.AlignHCenter
                                elide: Text.ElideRight
                                text: swatch.modelData.label
                                color: swatch.picked ? Theme.foreground : Theme.mutedForeground
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeXs
                            }
                        }
                    }
                }

                ThemedButton {
                    visible: hairSection.coloured && !EditorState.body.running
                    width: parent.width
                    text: qsTr("Remove hair colour")
                    variant: "ghost"
                    onClicked: EditorState.body.removeHairColor(EditorState.selectedTrack, EditorState.selectedClip)
                }
            }

            // Progress of either analysis, wherever it was started from.
            Column {
                visible: retoquePage.area !== "rostro" && EditorState.body.running
                width: parent.width
                spacing: Theme.spacingSm

                Text {
                    width: parent.width
                    wrapMode: Text.WordWrap
                    text: EditorState.body.status
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                }
                ThemedProgressBar {
                    width: parent.width
                    value: EditorState.body.progress
                }
                ThemedButton {
                    width: parent.width
                    text: qsTr("Cancel")
                    variant: "ghost"
                    onClicked: EditorState.body.cancel()
                }
            }

            Text {
                visible: retoquePage.area === "rostro" && !retoquePage.canTrack
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("Select a video or image clip to retouch a face.")
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
                model: retoquePage.area === "rostro" ? retoquePage.shownSections
                       : retoquePage.area === "cuerpo" ? retoquePage.bodySections : []
                delegate: Column {
                    id: section
                    required property var modelData
                    width: retoquePage.width
                    spacing: Theme.spacingSm

                    Row {
                        spacing: Theme.spacingSm

                        IconGlyph {
                            visible: !!section.modelData.glyph
                            glyph: section.modelData.glyph || ""
                            iconSize: 16
                            iconColor: Theme.foreground
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            text: section.modelData.title
                            color: Theme.foreground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeSm
                            font.weight: Font.Medium
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    // Photo tiles, as on CapCut: the same face with each look applied (rendered
                    // by Flip Studio itself, see resources/retouch), the name underneath.
                    Grid {
                        id: tiles
                        width: parent.width
                        columns: Math.max(3, Math.floor((width + columnSpacing) / (72 + columnSpacing)))
                        columnSpacing: Theme.spacingSm
                        rowSpacing: Theme.spacingMd

                        Repeater {
                            model: section.modelData.items
                            delegate: Column {
                                id: retouchTile
                                required property var modelData
                                readonly property bool usable: retoquePage.canTrack
                                                               && (retoquePage.area === "cuerpo" ? retoquePage.bodyReady
                                                                                                 : retoquePage.faceReady)
                                width: (tiles.width - tiles.columnSpacing * (tiles.columns - 1)) / tiles.columns
                                spacing: 4

                                Rectangle {
                                    id: photoFrame
                                    width: parent.width
                                    height: width
                                    radius: Theme.radiusMd
                                    color: Theme.panelAccent
                                    border.width: retouchHover.hovered && retouchTile.usable ? 2 : 1
                                    border.color: retouchHover.hovered && retouchTile.usable
                                                  ? Theme.primary : Theme.panelBorder
                                    clip: true
                                    opacity: retouchTile.usable ? 1 : 0.55

                                    Image {
                                        anchors.fill: parent
                                        anchors.margins: parent.border.width
                                        source: "qrc:/retouch/" + retouchTile.modelData.id + ".jpg"
                                        fillMode: Image.PreserveAspectCrop
                                        asynchronous: true
                                        smooth: true
                                        mipmap: true
                                    }

                                    HoverHandler {
                                        id: retouchHover
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        enabled: retouchTile.usable
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: retoquePage.apply(retouchTile.modelData.effect || "face_retouch",
                                                                     retouchTile.modelData.values)
                                    }

                                    ThemedToolTip {
                                        visible: retouchHover.hovered
                                        text: retouchTile.modelData.hint
                                    }

                                    // A star to keep it in Favorites, at the top of this page.
                                    AssetFavoriteButton {
                                        visible: favorited || retouchHover.hovered
                                        anchors.right: parent.right
                                        anchors.top: parent.top
                                        anchors.margins: 2
                                        tabId: "retouch"
                                        itemId: retouchTile.modelData.id
                                    }
                                }

                                Text {
                                    width: parent.width
                                    horizontalAlignment: Text.AlignHCenter
                                    elide: Text.ElideRight
                                    text: retouchTile.modelData.label
                                    color: retouchHover.hovered ? Theme.foreground : Theme.mutedForeground
                                    font.family: Theme.fontFamily
                                    font.pixelSize: Theme.fontSizeXs
                                }
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
