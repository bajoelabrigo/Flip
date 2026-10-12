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

                Repeater {
                    model: root.pages
                    delegate: Rectangle {
                        required property var modelData
                        required property int index
                        width: (strip.width - 6) / root.pages.length
                        height: stripLabel.implicitHeight + 14
                        radius: Theme.radiusSm
                        color: index === root.pageIndex ? Theme.popoverHover : "transparent"

                        Text {
                            id: stripLabel
                            anchors.centerIn: parent
                            width: parent.width - 8
                            horizontalAlignment: Text.AlignHCenter
                            elide: Text.ElideRight
                            text: modelData.label
                            color: index === root.pageIndex ? Theme.foreground : Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
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
        Column {
            id: retoquePage
            visible: root.page === "retoque"
            width: parent.width
            spacing: Theme.spacingLg

            readonly property var faceEffects: [
                { id: "face_retouch", label: qsTr("Skin retouch"), hint: qsTr("Smooth, whiten, tone, slim the face, bigger eyes, lipstick and blush") },
                { id: "face_fat_slim", label: qsTr("Body reshape"), hint: qsTr("Slim or widen what the mesh follows") },
                { id: "face_big_eyes", label: qsTr("Bigger eyes"), hint: qsTr("Enlarges the eyes the mesh found") },
                { id: "face_teeth_whiten", label: qsTr("Whiten teeth"), hint: qsTr("Needs the lip contour from a face scan") },
                { id: "face_eyeliner", label: qsTr("Eyeliner"), hint: qsTr("Draws along the eyelid contour") },
                { id: "face_eyeshadow", label: qsTr("Eyeshadow"), hint: qsTr("Colours the eyelid") },
                { id: "face_brow_tint", label: qsTr("Brow tint"), hint: qsTr("Colours the eyebrows") },
                { id: "face_eye_color", label: qsTr("Eye colour"), hint: qsTr("Recolours the iris") }
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

            Text {
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("Face, body and hair retouching: skin, makeup and the fun face effects. Add what you want, then scan the clip's faces so the effect has something to follow.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            Text {
                visible: !retoquePage.canTrack
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("Select a video clip to retouch a face.")
                color: Theme.warning
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            Text {
                visible: retoquePage.canTrack && !retoquePage.faceReady
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("Install Face retouch from Extras (it needs the AI engine) to use these.")
                color: Theme.warning
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            Repeater {
                model: retoquePage.faceEffects
                delegate: ThemedButton {
                    required property var modelData
                    width: parent.width
                    text: modelData.label
                    enabled: retoquePage.canTrack && retoquePage.faceReady
                    tooltip: modelData.hint
                    onClicked: EditorState.addEffect(EditorState.selectedTrack,
                                                     EditorState.selectedClip, modelData.id)
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
