import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."
import "../assets"

Item {
    id: root

    property int clipDataRevision: 0
    readonly property var clipData: {
        void clipDataRevision
        return EditorState.selectedClipData
    }
    readonly property bool hasSelection: !!clipData && Object.keys(clipData).length > 0
    readonly property string clipKind: hasSelection ? (clipData.kind || "") : ""
    readonly property bool hasTextStyle: hasSelection
                                         && (clipKind === "text" || clipKind === "subtitle")
                                         && !!clipData.textStyle
    readonly property var textStyle: hasTextStyle ? clipData.textStyle : ({
                                                                       "fontFamily": "Inter",
                                                                       "pixelSize": 64,
                                                                       "fontWeight": 700,
                                                                       "italic": false,
                                                                       "layers": [],
                                                                       "lookId": "",
                                                                       "lookParams": ({}),
                                                                       "pathBend": 0,
                                                                       "align": "center",
                                                                       "valign": "middle",
                                                                       "wordWrap": true,
                                                                       "lineHeight": 1.2,
                                                                       "letterSpacing": 0,
                                                                       "boxEnabled": false,
                                                                       "boxColor": "#80000000",
                                                                       "boxPadding": 8,
                                                                       "boxRadius": 0,
                                                                       "packId": "",
                                                                       "wordHighlight": { "enabled": false, "color": "#ffe62828", "padding": 6, "radius": 4 },
                                                                       "underlineEnabled": false,
                                                                       "underlineColor": "#ffe62828",
                                                                       "underlineWidth": 6,
                                                                       "underlineOffset": 4,
                                                                       "accent": { "rule": "none", "n": 2, "phase": 0,
                                                                                   "colorEnabled": false, "color": "#ffffd640",
                                                                                   "sizeScale": 1, "outlineEnabled": false,
                                                                                   "outlineWidth": 0, "outlineColor": "#ff000000",
                                                                                   "highlight": { "enabled": false, "color": "#ffe62828", "padding": 6, "radius": 4 } },
                                                                       "animation": { "in": { "preset": "", "enabled": true, "custom": false },
                                                                                      "out": { "preset": "", "enabled": true, "custom": false },
                                                                                      "loop": { "preset": "", "enabled": true, "custom": false },
                                                                                      "custom": false }
                                                                   })

    // The selected family's real weight ladder — never an invented one. Single-weight display faces
    // (Anton, Bebas Neue, Pacifico...) expose exactly one entry and no italic.
    readonly property var fontFamilyInfo: {
        void clipDataRevision
        const catalog = EditorState.fontCatalog()
        for (let i = 0; i < catalog.length; ++i) {
            if (catalog[i].family === root.textStyle.fontFamily)
                return catalog[i]
        }
        return null
    }
    readonly property var availableWeights: fontFamilyInfo ? fontFamilyInfo.weights
                                                           : [100, 200, 300, 400, 500, 600, 700, 800, 900]
    readonly property bool familyHasItalic: fontFamilyInfo ? fontFamilyInfo.hasItalic : true

    readonly property var weightLabels: ({
                                             100: "Thin", 200: "ExtraLight", 300: "Light",
                                             400: "Regular", 500: "Medium", 600: "SemiBold",
                                             700: "Bold", 800: "ExtraBold", 900: "Black"
                                         })
    readonly property var accentRules: ["none", "firstWord", "lastWord", "everyOther", "everyNth",
                                        "longestWord", "randomStable", "karaoke", "keywords"]
    readonly property var accentRuleLabels: [qsTr("No accent"), qsTr("First word"), qsTr("Last word"),
                                             qsTr("Every other word"), qsTr("Every Nth word"),
                                             qsTr("Longest word"), qsTr("Random words"),
                                             qsTr("Spoken word (karaoke)"),
                                             qsTr("Keywords (long words and numbers)")]

    // ----- Layers / looks --------------------------------------------------
    readonly property var layers: {
        const own = root.hasRunSelection ? root.runUnderCursor : null
        if (own && own.layersEnabled && own.layers && own.layers.length > 0)
            return own.layers
        return (textStyle && textStyle.layers) || []
    }
    // The fill the Type section's colour swatch edits: the front-most enabled fill, or the
    // front-most fill at all when every fill is hidden.
    readonly property var frontFill: {
        let fallback = null
        for (let i = root.layers.length - 1; i >= 0; --i) {
            const l = root.layers[i]
            if (l.kind !== "fill")
                continue
            if (l.enabled !== false)
                return l
            if (!fallback)
                fallback = l
        }
        return fallback
    }
    readonly property string frontFillPaintKind: frontFill && frontFill.paint ? (frontFill.paint.kind || "solid") : "solid"
    readonly property string frontFillColor: {
        if (root.hasRunSelection && root.runUnderCursor.colorEnabled === true && root.runUnderCursor.color)
            return root.runUnderCursor.color
        if (!root.frontFill || !root.frontFill.paint)
            return "#ffffffff"
        const p = root.frontFill.paint
        if (root.frontFillPaintKind === "gradient") {
            const stops = p.gradient && p.gradient.stops
            return stops && stops.length > 0 ? stops[0].color : "#ffffffff"
        }
        return p.color || "#ffffffff"
    }
    readonly property var looks: EditorState.textLooks()
    readonly property var selectedLook: {
        for (let i = 0; i < root.looks.length; ++i) {
            if (root.looks[i].id === root.textStyle.lookId)
                return root.looks[i]
        }
        return null
    }
    readonly property string lookSampleText: {
        const words = String((root.hasSelection && root.clipData.textContent) || "").trim().split(/\s+/)
        const sample = words.length > 0 ? words[0] : ""
        return sample.length > 0 ? sample : qsTr("Aa")
    }
    property var expandedLayerIds: ({})

    // ----- Animation ---------------------------------------------------------
    property string animSlot: "in"
    property string animCategory: ""
    // The visual animation editor (Personalizar) is open for the current slot.
    property bool animEditorOpen: false
    // Trending ones show for everyone but apply only signed in (Jorge, 2026-10-23): picking one
    // signed out asks for the account and applies it once signed in.
    readonly property bool trendsNeedAccount: Account.available && !Account.signedIn
    // Bumped when the user saves, renames or deletes one of their own animations.
    property int animPresetsTick: 0
    readonly property var animPresets: {
        void root.animSlot
        void root.animPresetsTick
        return EditorState.textAnimationPresets(root.animSlot)
    }
    readonly property var animCategories: {
        void root.animSlot
        void root.animPresetsTick
        return EditorState.textAnimationCategories(root.animSlot)
    }
    readonly property string animQuery: animSearch.text.trim().toLowerCase()
    readonly property var animTileModel: {
        void root.favoritesTick
        if (root.animQuery.length > 0) {
            const q = root.foldText(root.animQuery)
            return [{ "id": "", "label": qsTr("None") }].concat(
                root.animPresets.filter(p => root.foldText(p.label || "").indexOf(q) >= 0
                                             || root.foldText(p.id || "").indexOf(q) >= 0))
        }
        const filtered = root.animCategory.length === 0
                         ? root.animPresets
                         : root.animCategory === "__favorites__"
                           ? root.animPresets.filter(p => EditorState.isAssetFavorite("textAnimations", p.id))
                           : root.animCategory === "trending"
                             ? root.animPresets.filter(p => p.trending)
                             : root.animPresets.filter(p => p.category === root.animCategory)
        return [{ "id": "", "label": qsTr("None") }].concat(filtered)
    }
    // Trending › From Stock (0.22): Stock's text animations under the trending ones that come with
    // the app; in Favorites, the starred ones from Stock. A click downloads one (once) and sets it on
    // this slot when it is made for it.
    readonly property bool animStockShown: root.animCategory === "trending" || root.animCategory === "__favorites__"
    readonly property var animStockFavorites: {
        void root.favoritesTick
        void Market.favoriteItemsRevision
        return root.animCategory === "__favorites__"
               ? Market.stockFavoriteItems(EditorState.assetFavoriteIds("textAnimations"), ["text-animation"], "textAnimations")
               : []
    }
    function stockAnimPreset(item) {
        void root.animPresetsTick
        const id = Market.placedId(item.id)
        return id.length > 0 ? EditorState.textAnimationPresets("").find(p => p.id === id) : undefined
    }
    function applyStockAnim(item) {
        root.animPresetsTick++
        const preset = root.stockAnimPreset(item)
        if (!preset)
            return
        if ((preset.slots || [root.animSlot]).indexOf(root.animSlot) < 0) {
            EditorState.setLastMessage(qsTr("“%1” is for another tab (In, Out or Loop): it is there now.").arg(item.title || preset.label), "info")
            return
        }
        root.pickPreset(preset.id)
    }
    readonly property var animation: (textStyle && textStyle.animation) || ({})
    readonly property var slotData: animation[animSlot] || ({ "preset": "", "enabled": true, "custom": false })
    readonly property bool slotHasPreset: !!slotData.preset && slotData.preset.length > 0
    readonly property var selectedPreset: {
        for (let i = 0; i < root.animPresets.length; ++i) {
            if (root.animPresets[i].id === root.slotData.preset)
                return root.animPresets[i]
        }
        return null
    }
    readonly property var presetFlags: (selectedPreset && selectedPreset.flags) || ({})
    // A Loop shows only the controls its animation reads (auditoría D10): Loops declare none of
    // the reveal's common params, and only a progress-driven one repeats with the period.
    function slotControlShown(paramId) {
        if (root.animSlot !== "loop")
            return true
        if (!root.selectedPreset)
            return false
        if (paramId === "period")
            return !!root.selectedPreset.progressDriven
        return (root.selectedPreset.params || []).some(p => p.id === paramId)
    }
    readonly property var commonAnimParamIds: ["duration", "stagger", "unit", "order", "ease", "period"]
    readonly property var presetOwnParams: selectedPreset
                                           ? (selectedPreset.params || []).filter(p => root.commonAnimParamIds.indexOf(p.id) < 0)
                                           : []
    readonly property var animUnits: ["block", "character", "word", "line"]
    readonly property var animUnitLabels: [qsTr("Whole block"), qsTr("Character"), qsTr("Word"), qsTr("Line")]
    readonly property var animOrders: ["forward", "backward", "centerOut", "random"]
    readonly property var animOrderLabels: [qsTr("Forward"), qsTr("Backward"), qsTr("Center out"), qsTr("Random")]
    readonly property var easeChips: [
        { "id": "linear", "label": qsTr("Linear") },
        { "id": "easeInOut", "label": qsTr("Smooth") },
        { "id": "smooth", "label": qsTr("Gentle") },
        { "id": "easeIn", "label": qsTr("Speed up") },
        { "id": "easeOut", "label": qsTr("Snappy") },
        { "id": "back", "label": qsTr("Back") },
        { "id": "bounce", "label": qsTr("Bounce") }
    ]

    // Sub-page of the inspector: "text", "style" or "animate". Survives selection changes so a
    // pass over several clips stays on the page being worked in.
    property string textTab: "basic"
    // Inside the Texto avanzado window (0.23): the window has its own tabs for the pages, and
    // opening the window again from here makes no sense.
    property bool inAdvanced: false

    // The content field's user-dragged height and the id of the clip its text was loaded from,
    // so a commit can never land on a clip selected after the typing began.
    property real contentFieldHeight: 96
    property string contentClipId: ""
    readonly property bool contentDirty: root.clipKind === "text"
                                         && textContentField.text !== (root.clipData.textContent || "")

    function applyText() {
        if (!root.hasSelection || root.clipKind !== "text" || root.clipData.id !== root.contentClipId)
            return
        EditorState.commitTextEdit(EditorState.selectedTrack, EditorState.selectedClip, textContentField.text)
    }

    // Lands a freshly added text clip in its content field, where the inline editor used to open.
    function focusContent() {
        root.textTab = "basic"
        textContentField.forceActiveFocus()
        textContentField.selectAll()
    }

    // Lower case without accents, so «animacion» finds «Animación».
    function foldText(text) {
        return String(text).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
    }

    // --- Letras elegidas (0.24, como Filmora) -------------------------------------------------
    // El cuadro «Texto de entrada» dice qué letras están sombreadas; los controles de estilo se
    // aplican solo a ellas. Sin sombrear, a todo el texto como siempre.
    property int runSelectionStart: -1
    property int runSelectionEnd: -1
    readonly property bool hasRunSelection: runSelectionStart >= 0 && runSelectionEnd > runSelectionStart
    readonly property bool canStyleRuns: hasSelection && clipKind === "text"
    function syncStyleRange() {
        if (!root.hasSelection)
            return
        const on = root.canStyleRuns && root.hasRunSelection
        EditorState.setTextStyleRange(EditorState.selectedTrack, EditorState.selectedClip,
                                      on ? root.runSelectionStart : -1, on ? root.runSelectionEnd : -1)
    }
    onRunSelectionStartChanged: root.syncStyleRange()
    onRunSelectionEndChanged: root.syncStyleRange()
    // Hidden (the Texto avanzado window closed, another clip in the panel), its shaded letters stop
    // steering the layer calls: nothing would say so any more.
    onVisibleChanged: {
        if (!visible && root.hasRunSelection && root.hasSelection)
            EditorState.setTextStyleRange(EditorState.selectedTrack, EditorState.selectedClip, -1, -1)
        else if (visible)
            root.syncStyleRange()
    }

    // Lo que el patch del bloque se convierte en patch del tramo: la pila entera (trazo, sombra,
    // resplandor, estilos), el fondo, el color, la fuente y el tamaño.
    function runPatchFor(patch) {
        const run = {}
        if (patch.layers !== undefined)
            run.layers = patch.layers
        if (patch.color !== undefined)
            run.color = patch.color
        if (patch.fontFamily !== undefined)
            run.fontFamily = patch.fontFamily
        if (patch.bold !== undefined)
            run.bold = patch.bold
        if (patch.fontWeight !== undefined)
            run.bold = Number(patch.fontWeight) >= 600
        if (patch.italic !== undefined)
            run.italic = patch.italic
        if (patch.underline !== undefined)
            run.underline = patch.underline
        const base = root.textStyle.pixelSize
        if (patch.pixelSize !== undefined && base > 0)
            run.sizeScale = patch.pixelSize / base
        // The letters' box has one padding: either of the block's two sets it. The C++ side takes
        // the keys one by one, so a slider keeps the colour and boxEnabled:false takes it away.
        const boxKeys = ["boxEnabled", "boxColor", "boxPadding", "boxRadius", "boxBorderWidth", "boxBorderColor"]
        for (const key of boxKeys) {
            if (patch[key] !== undefined)
                run[key] = patch[key]
        }
        if (patch.boxPaddingX !== undefined)
            run.boxPadding = patch.boxPaddingX
        if (patch.boxPaddingY !== undefined)
            run.boxPadding = patch.boxPaddingY
        const transformKeys = ["transformEnabled", "offsetX", "offsetY", "transformScale", "rotation"]
        for (const key of transformKeys) {
            if (patch[key] !== undefined)
                run[key] = patch[key]
        }
        return run
    }

    // What the Background section shows: the letters' own box when some are shaded.
    readonly property var boxSource: {
        if (!root.hasRunSelection)
            return root.textStyle
        const r = root.runUnderCursor
        const pad = r.boxPadding !== undefined ? Number(r.boxPadding) : 6
        return {
            "boxEnabled": r.boxEnabled === true,
            "boxColor": r.boxColor || "#80000000",
            "boxRadius": r.boxRadius !== undefined ? Number(r.boxRadius) : 4,
            "boxPaddingX": pad,
            "boxPaddingY": pad,
            "boxOffsetX": root.textStyle.boxOffsetX,
            "boxOffsetY": root.textStyle.boxOffsetY,
            "boxStyle": root.textStyle.boxStyle,
            "boxShape": root.textStyle.boxShape,
            "boxBorderColor": r.boxBorderColor || "#ffffffff",
            "boxBorderWidth": r.boxBorderWidth !== undefined ? Number(r.boxBorderWidth) : 0
        }
    }

    // El tramo que cubre el cursor (o el comienzo de la selección): sus valores, para enseñarlos.
    readonly property var runUnderCursor: {
        void root.textStyle
        void root.runSelectionStart
        if (!root.canStyleRuns)
            return ({})
        const runs = EditorState.textRuns(EditorState.selectedTrack, EditorState.selectedClip)
        const at = root.hasRunSelection ? root.runSelectionStart : 0
        for (let i = 0; i < runs.length; ++i) {
            if (runs[i].start <= at && at < runs[i].end)
                return runs[i]
        }
        return ({})
    }

    // La transformación de esas letras (px al tamaño del bloque y grados).
    function runTransformValue(key, fallback) {
        const value = root.runUnderCursor[key]
        return value === undefined || value === null ? fallback : Number(value)
    }

    function setRunTransform(key, value) {
        const patch = {}
        patch[key] = value
        root.applyStyle(patch)
    }

    // La única puerta de los controles de estilo: con letras sombreadas al tramo, sin ellas al bloque.
    function applyStyle(patch) {
        if (!root.hasSelection)
            return
        if (root.canStyleRuns && root.hasRunSelection) {
            const run = root.runPatchFor(patch)
            if (Object.keys(run).length > 0) {
                EditorState.patchTextRuns(EditorState.selectedTrack, EditorState.selectedClip,
                                          root.runSelectionStart, root.runSelectionEnd, run)
                return
            }
        }
        EditorState.setTextStyle(EditorState.selectedTrack, EditorState.selectedClip, patch)
    }

    function setTextStyleKey(key, value) {
        const patch = {}
        patch[key] = value
        root.applyStyle(patch)
    }

    // Nested style groups: the C++ side takes the same partial-patch shape one level down.
    function setTextGroupKey(group, key, value) {
        const inner = {}
        inner[key] = value
        const patch = {}
        patch[group] = inner
        root.applyStyle(patch)
    }

    function setTextAccentHighlightKey(key, value) {
        const highlight = {}
        highlight[key] = value
        EditorState.setTextStyle(EditorState.selectedTrack, EditorState.selectedClip,
                                 { "accent": { "highlight": highlight } })
    }


    // ----- CapCut pages: Básico, Burbuja, Efectos, Animación ---------------------------------------
    readonly property var pages: [
        { "id": "basic", "label": qsTr("Basic") },
        { "id": "bubble", "label": qsTr("Bubble") },
        { "id": "effects", "label": qsTr("Effects") },
        { "id": "animate", "label": qsTr("Animation") }
    ]
    // textTab is remembered across selections; an older value ("text", "style") lands on Básico.
    readonly property string page: {
        for (let i = 0; i < root.pages.length; ++i) {
            if (root.pages[i].id === root.textTab)
                return root.textTab
        }
        return "basic"
    }
    property bool advancedOpen: false
    // The galleries cannot tell which recipe produced a style, so the one tapped last is outlined.
    property string lastQuickId: ""
    property string lastBubbleId: ""
    property string bubbleCategory: ""
    property string effectsCategory: "basic"
    // A layer slider (shadow distance, angle) mid-drag: its release commits the preview.
    property bool layerDragActive: false

    readonly property real em: Math.max(1, Number(root.textStyle.pixelSize) || 64)
    readonly property var quickStyles: EditorState.textQuickStyles()
    readonly property var bubbles: EditorState.textBubbles()
    readonly property var bubbleCategories: EditorState.textBubbleCategories()
    readonly property var templatePresets: EditorState.textPresets()
    readonly property var effectCategories: [{ "id": "favorites", "label": qsTr("Favorites") }]
        .concat(EditorState.textQuickStyleCategories())
        .concat([
            { "id": "looks", "label": qsTr("Effects") },
            { "id": "templates", "label": qsTr("Templates") },
            { "id": "mine", "label": qsTr("My styles") }
        ])
    // The styles the user saved (Guardar estilo), and a tick that refreshes them and the stars.
    property int savedTick: 0
    readonly property var savedPresets: {
        void root.savedTick
        return EditorState.userTextPresets()
    }
    property int favoritesTick: 0
    Connections {
        target: EditorState
        function onUserTextPresetsChanged() { root.savedTick++ }
        function onAssetFavoritesChanged() { root.favoritesTick++ }
        function onUserTextAnimationPresetsChanged() { root.animPresetsTick++ }
    }
    function isFavorite(tab, id) {
        void root.favoritesTick
        return EditorState.isAssetFavorite(tab, id)
    }

    readonly property var strokeLayer: root.layerOfKind("stroke")
    readonly property var glowLayer: root.layerOfKind("glow")
    readonly property var shadowLayer: root.layerOfKind("shadow")
    readonly property real shadowDistance: root.shadowLayer
                                           ? Math.hypot(Number(root.shadowLayer.offsetX) || 0,
                                                        Number(root.shadowLayer.offsetY) || 0)
                                           : 0
    readonly property real shadowAngle: root.shadowLayer
                                        ? Math.atan2(Number(root.shadowLayer.offsetY) || 0,
                                                     Number(root.shadowLayer.offsetX) || 0) * 180 / Math.PI
                                        : 45

    // The front-most layer of a kind: what a Básico section (Trazo, Brillo, Sombra) edits.
    function layerOfKind(kind) {
        for (let i = root.layers.length - 1; i >= 0; --i) {
            if (root.layers[i].kind === kind)
                return root.layers[i]
        }
        return null
    }
    function layerOn(kind) {
        const layer = root.layerOfKind(kind)
        return !!layer && layer.enabled !== false
    }
    function setLayerKey(layer, patch) {
        if (layer)
            EditorState.setStyleLayer(EditorState.selectedTrack, EditorState.selectedClip, layer.id, patch)
    }
    function previewLayer(layer, patch) {
        if (layer)
            EditorState.previewSetStyleLayer(EditorState.selectedTrack, EditorState.selectedClip, layer.id, patch)
    }
    function beginLayerDrag(undoText) {
        root.layerDragActive = true
        EditorState.beginPreviewDrag(undoText)
    }
    function commitLayer(layer, patch) {
        if (!layer)
            return
        if (root.layerDragActive) {
            root.previewLayer(layer, patch)
            EditorState.commitPreviewDrag()
            root.layerDragActive = false
        } else {
            root.setLayerKey(layer, patch)
        }
    }
    // A Básico section's switch: shows or hides its layer, creating it the first time where that
    // kind belongs in the stack (addStyleLayer's natural order: shadows and glows behind the fill).
    function enableLayer(kind, on, defaults) {
        const existing = root.layerOfKind(kind)
        if (!on) {
            if (existing)
                root.setLayerKey(existing, { "enabled": false })
            return
        }
        if (existing) {
            root.setLayerKey(existing, { "enabled": true })
            return
        }
        const id = EditorState.addTextLayer(EditorState.selectedTrack, EditorState.selectedClip, kind, -1,
                                            root.hasRunSelection ? root.runSelectionStart : -1,
                                            root.hasRunSelection ? root.runSelectionEnd : -1)
        if (id && id.length > 0)
            EditorState.setStyleLayer(EditorState.selectedTrack, EditorState.selectedClip, id, defaults)
    }
    function layerColor(layer, fallback) {
        return layer && layer.paint && layer.paint.color ? layer.paint.color : fallback
    }
    function layerProp(layer, field, label, decimals) {
        if (!layer || root.hasRunSelection)
            return { "key": "", "label": label, "def": 0, "decimals": decimals }
        return { "key": "text.layer." + layer.id + "." + field, "label": label,
                 "def": Number(layer[field]) || 0, "decimals": decimals }
    }
    function layerKeyframes(layer, field) {
        return layer && !root.hasRunSelection ? root.textKeyframes("layer." + layer.id + "." + field) : []
    }
    function shadowOffsets(distance, angle) {
        const a = angle * Math.PI / 180
        return { "offsetX": distance * Math.cos(a), "offsetY": distance * Math.sin(a) }
    }
    // B toggles between the family's weight nearest 700 and the one nearest 400.
    function boldToggleWeight() {
        const weights = root.availableWeights
        const target = Number(root.textStyle.fontWeight) >= 600 ? 400 : 700
        let best = weights[0]
        for (let i = 0; i < weights.length; ++i) {
            if (Math.abs(weights[i] - target) < Math.abs(best - target))
                best = weights[i]
        }
        return best
    }
    // U draws the underline in the text's own colour, sized to the font.
    function toggleUnderline() {
        const on = root.textStyle.underlineEnabled !== true
        const patch = { "underlineEnabled": on }
        if (on) {
            patch.underlineColor = root.frontFillColor
            patch.underlineWidth = Math.max(2, root.em * 0.06)
            patch.underlineOffset = Math.max(2, root.em * 0.1)
        }
        root.applyStyle(patch)
    }
    // Colours travel as #AARRGGBB; the background's opacity slider edits only the alpha byte.
    function hexAlpha(hex) {
        const s = String(hex || "")
        return s.length === 9 ? parseInt(s.substr(1, 2), 16) / 255 : 1
    }
    function withAlpha(hex, alpha) {
        const s = String(hex || "#000000")
        const rgb = s.length === 9 ? s.substr(3) : s.substr(1, 6)
        const level = Math.round(Math.max(0, Math.min(1, alpha)) * 255)
        return "#" + (level < 16 ? "0" : "") + level.toString(16) + rgb
    }
    // A colour picked without transparency keeps the background's current opacity.
    function keepAlpha(picked, current) {
        return root.hexAlpha(picked) < 0.999 ? picked : root.withAlpha(picked, root.hexAlpha(current))
    }
    function previewQuery(text) {
        return "?text=" + encodeURIComponent(text)
               + "&font=" + encodeURIComponent(root.textStyle.fontFamily || "")
               + "&weight=" + Math.round(Number(root.textStyle.fontWeight) || 400)
               + "&italic=" + (root.textStyle.italic ? 1 : 0)
    }
    function quickPreview(id) {
        return "image://textlook/quick:" + id + root.previewQuery(root.lookSampleText)
    }
    function bubblePreview(id) {
        return "image://textlook/bubble:" + id + root.previewQuery(qsTr("Hello"))
    }
    function applyQuick(id) {
        root.lastQuickId = id
        // Con letras sombreadas, el estilo preestablecido va solo a ellas (0.24).
        EditorState.applyTextQuickStyle(EditorState.selectedTrack, EditorState.selectedClip, id,
                                        root.hasRunSelection ? root.runSelectionStart : -1,
                                        root.hasRunSelection ? root.runSelectionEnd : -1)
    }
    function applyBubble(id) {
        root.lastBubbleId = id
        EditorState.applyTextBubble(EditorState.selectedTrack, EditorState.selectedClip, id)
    }
    // Efectos: the quick styles by category, the look gallery and the built-in templates in one grid.
    function effectTiles(search) {
        const query = String(search || "").trim().toLowerCase()
        const tiles = []
        for (let i = 0; i < root.quickStyles.length; ++i) {
            const q = root.quickStyles[i]
            tiles.push({ "kind": "quick", "id": q.id, "label": q.label, "category": q.category,
                         "source": root.quickPreview(q.id) })
        }
        for (let i = 0; i < root.looks.length; ++i) {
            const look = root.looks[i]
            if (look.id === "plain")
                continue
            tiles.push({ "kind": "look", "id": look.id, "label": look.label, "category": "looks",
                         "source": "image://textlook/" + look.id + root.previewQuery(root.lookSampleText) })
        }
        for (let i = 0; i < root.templatePresets.length; ++i) {
            const preset = root.templatePresets[i]
            tiles.push({ "kind": "template", "id": preset.id, "label": preset.label, "category": "templates",
                         "source": "image://textstyle/" + preset.id })
        }
        for (let i = 0; i < root.savedPresets.length; ++i) {
            const preset = root.savedPresets[i]
            tiles.push({ "kind": "template", "id": preset.id, "label": preset.label, "category": "mine",
                         "source": "image://textstyle/" + preset.id })
        }
        if (query.length > 0)
            return tiles.filter(t => String(t.label).toLowerCase().indexOf(query) >= 0)
        if (root.effectsCategory === "favorites")
            return tiles.filter(t => root.isFavorite("textEffects", t.kind + ":" + t.id))
        return tiles.filter(t => t.category === root.effectsCategory)
    }
    function applyEffectTile(tile) {
        if (tile.kind === "look")
            EditorState.applyTextLook(EditorState.selectedTrack, EditorState.selectedClip, tile.id)
        else if (tile.kind === "template")
            EditorState.applyTextPreset(EditorState.selectedTrack, EditorState.selectedClip, tile.id)
        else
            root.applyQuick(tile.id)
    }

    function setLayerExpanded(id, on) {
        const next = Object.assign({}, root.expandedLayerIds)
        if (on)
            next[id] = true
        else
            delete next[id]
        root.expandedLayerIds = next
    }

    function addLayer(kind) {
        // Con letras sombreadas, la capa es para ellas (0.24).
        const id = EditorState.addTextLayer(EditorState.selectedTrack, EditorState.selectedClip, kind, -1,
                                            root.hasRunSelection ? root.runSelectionStart : -1,
                                            root.hasRunSelection ? root.runSelectionEnd : -1)
        if (id && id.length > 0)
            root.setLayerExpanded(id, true)
    }

    function setSlot(patch) {
        EditorState.setTextAnimationSlot(EditorState.selectedTrack, EditorState.selectedClip, root.animSlot, patch)
    }
    function previewSlot(patch) {
        EditorState.previewSetTextAnimationSlot(EditorState.selectedTrack, EditorState.selectedClip, root.animSlot, patch)
    }
    function slotParamPatch(id, value) {
        const params = {}
        params[id] = value
        return { "params": params }
    }
    function seekToSlotStart() {
        EditorState.playheadSeconds = EditorState.textAnimationSlotStartSeconds(
                    EditorState.selectedTrack, EditorState.selectedClip, root.animSlot)
    }
    // Every animation that comes with the app wears the flame and asks for the account (Jorge,
    // 2026-10-24: In, Out and Loop alike); the user's own ones ("user:") do not.
    function wearsFlame(id) {
        return id.length > 0 && !id.startsWith("user:")
    }
    function pickPreset(id) {
        if (id.length === 0) {
            EditorState.clearTextAnimationSlot(EditorState.selectedTrack, EditorState.selectedClip, root.animSlot)
            return
        }
        if (root.trendsNeedAccount && root.wearsFlame(id)) {
            const slot = root.animSlot
            const track = EditorState.selectedTrack
            const clip = EditorState.selectedClip
            animSignInLoader.active = true
            animSignInLoader.item.openFor(() => {
                // Only onto the text that asked, still on the same slot.
                if (root.animSlot !== slot || EditorState.selectedTrack !== track || EditorState.selectedClip !== clip)
                    return
                root.setSlot({ "preset": id })
                root.seekToSlotStart()
            })
            return
        }
        root.setSlot({ "preset": id })
        root.seekToSlotStart()
    }
    // Plays the slot from its start and stops once the last unit has finished.
    function previewAnimation() {
        root.seekToSlotStart()
        const s = root.slotData
        const length = root.animSlot === "loop" ? (Number(s.period) || 1) : (Number(s.duration) || 0.4)
        previewStopTimer.interval = Math.round((length + 4 * (Number(s.stagger) || 0) + 0.5) * 1000)
        EditorState.playing = true
        previewStopTimer.restart()
    }
    function revertCustomAnimation() {
        const slots = ["in", "out", "loop"]
        for (let i = 0; i < slots.length; ++i) {
            const s = root.animation[slots[i]]
            if (s && s.custom)
                EditorState.clearTextAnimationSlot(EditorState.selectedTrack, EditorState.selectedClip, slots[i])
        }
    }

    height: contentCol.height
    implicitHeight: contentCol.height

    // Keyframed style scalars ride the generic keyframe API as "text.<key>"; the key list comes
    // back inside textStyle.keyframes with times already on the timeline, like a mask's. `def`
    // tracks the static scalar so an unkeyed row shows the value the clip actually renders with.
    function textKeyframes(key) {
        const keys = root.textStyle && root.textStyle.keyframes
        const entry = keys && keys[key]
        return (entry && entry.points) || []
    }
    function textProp(key, label, decimals) {
        return { "key": "text." + key, "label": label, "def": Number(root.textStyle[key]),
                 "decimals": decimals }
    }

    function refreshFields() {
        if (root.hasSelection) {
            // A different clip replaces the field outright, unapplied typing included — the same
            // rule as the subtitle cue editor. The same clip's edits leave focused typing alone.
            const id = root.clipData.id || ""
            if (id !== root.contentClipId) {
                root.contentClipId = id
                textContentField.text = root.clipData.textContent || ""
            } else if (!textContentField.activeFocus) {
                textContentField.text = root.clipData.textContent || ""
            }
        }
        if (!root.hasTextStyle)
            return
        const s = root.textStyle
        if (wordHighlightPaddingField && !wordHighlightPaddingField.activeFocus)
            wordHighlightPaddingField.value = s.wordHighlight.padding
        if (wordHighlightRadiusField && !wordHighlightRadiusField.activeFocus)
            wordHighlightRadiusField.value = s.wordHighlight.radius
        if (underlineWidthField && !underlineWidthField.activeFocus)
            underlineWidthField.value = s.underlineWidth
        if (underlineOffsetField && !underlineOffsetField.activeFocus)
            underlineOffsetField.value = s.underlineOffset
        if (accentEveryNField && !accentEveryNField.activeFocus)
            accentEveryNField.value = s.accent.n
        if (accentSizeScaleField && !accentSizeScaleField.activeFocus)
            accentSizeScaleField.value = s.accent.sizeScale
        if (accentOutlineWidthField && !accentOutlineWidthField.activeFocus)
            accentOutlineWidthField.value = s.accent.outlineWidth
    }

    Connections {
        target: EditorState
        function onSelectionChanged() { root.clipDataRevision++; root.refreshFields() }
        function onSelectedClipDataChanged() { root.clipDataRevision++; root.refreshFields() }
        function onTracksChanged() { root.clipDataRevision++; root.refreshFields() }
    }

    Component.onCompleted: refreshFields()
    // The Properties panel unloads this tab when another is picked; land typed text first.
    Component.onDestruction: {
        if (contentDirty)
            applyText()
    }

    Timer {
        id: previewStopTimer
        repeat: false
        onTriggered: EditorState.playing = false
    }

    // A card in the Estilo preestablecido / Burbuja / Efectos galleries: the recipe drawn by the
    // real text painter (image://textlook), its name under it, the applied one outlined.
    component GalleryTile: Item {
        id: tile
        property string source: ""
        property string label: ""
        property bool selected: false
        property bool none: false
        property real tileWidth: 80
        property bool showLabel: true
        // Set both to show a favorite star in the corner.
        property string favoriteTab: ""
        property string favoriteId: ""
        signal clicked()

        width: tileWidth
        height: tileCard.height + (showLabel ? tileLabel.implicitHeight + 4 : 0)

        Rectangle {
            id: tileCard
            width: parent.width
            height: Math.round(tile.tileWidth * 0.62)
            radius: Theme.radiusSm
            color: Theme.textStylePreviewBg
            border.width: tile.selected ? 2 : Theme.borderWidth
            border.color: tile.selected ? Theme.primary
                                        : (tileHover.hovered ? Theme.mutedForeground : Theme.textStylePreviewBorder)
            clip: true

            Image {
                anchors.fill: parent
                anchors.margins: 2
                visible: !tile.none
                source: tile.source
                sourceSize: Qt.size(Math.round(width * 2), Math.round(height * 2))
                fillMode: Image.PreserveAspectFit
                asynchronous: true
                cache: true
                smooth: true
            }

            IconGlyph {
                anchors.centerIn: parent
                visible: tile.none
                glyph: Theme.icons.x
                iconSize: Theme.iconSizeLg
                iconColor: Theme.mutedForeground
            }

            HoverHandler {
                id: tileHover
                cursorShape: Qt.PointingHandCursor
            }
            TapHandler {
                // A tap on the star stars the card; it does not apply it.
                onTapped: if (!tileStar.hovered) tile.clicked()
            }
            ThemedToolTip {
                text: tile.label
                visible: !tile.showLabel && tileHover.hovered && tile.label.length > 0
            }

            AssetFavoriteButton {
                id: tileStar
                visible: tile.favoriteTab.length > 0 && (tileHover.hovered || favorited)
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 2
                tabId: tile.favoriteTab
                itemId: tile.favoriteId
            }
        }

        Text {
            id: tileLabel
            visible: tile.showLabel
            anchors.top: tileCard.bottom
            anchors.topMargin: 3
            width: parent.width
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
            text: tile.label
            color: tile.selected ? Theme.foreground : Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }
    }

    // A labelled slider for the style values that are not keyframed (the background's size and
    // place, the shadow's distance and angle). `moved` fires while dragging, `committed` on release.
    component SliderRow: Column {
        id: sliderRow
        property string label: ""
        property real from: 0
        property real to: 1
        property real stepSize: 0
        property real value: 0
        property string suffix: ""
        property int decimals: 0
        property real displayScale: 1
        signal dragStarted()
        signal moved(real value)
        signal committed(real value)

        width: parent ? parent.width : 200
        spacing: 2

        Row {
            width: parent.width

            Text {
                width: parent.width - sliderReadout.width
                text: sliderRow.label
                elide: Text.ElideRight
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
            Text {
                id: sliderReadout
                text: (rowSlider.value * sliderRow.displayScale).toFixed(sliderRow.decimals) + sliderRow.suffix
                color: Theme.panelForeground
                font.family: Theme.monoFontFamily
                font.pixelSize: Theme.fontSizeXs
            }
        }

        ThemedSlider {
            id: rowSlider
            width: parent.width
            label: sliderRow.label
            from: sliderRow.from
            to: sliderRow.to
            stepSize: sliderRow.stepSize
            valueFormatter: function (v) {
                return (v * sliderRow.displayScale).toFixed(sliderRow.decimals) + sliderRow.suffix
            }
            Binding on value {
                when: !rowSlider.pressed
                value: sliderRow.value
            }
            onMoved: {
                if (pressed)
                    sliderRow.moved(value)
                else
                    sliderRow.committed(value)
            }
            onPressedChanged: {
                if (pressed)
                    sliderRow.dragStarted()
                else
                    sliderRow.committed(value)
            }
        }
    }
    Column {
        id: contentCol
        width: root.width
        spacing: Theme.spacingMd

        // Filmora's AVANZADO: the big window with the preview, the letters' own styles and every
        // page side by side.
        ThemedButton {
            width: parent.width
            visible: !root.inAdvanced && root.hasTextStyle
            text: qsTr("Open Advanced text…")
            glyph: Theme.icons.type
            variant: "primary"
            onClicked: {
                advancedTextLoader.active = true
                if (advancedTextLoader.item)
                    advancedTextLoader.item.openFor(EditorState.selectedTrack, EditorState.selectedClip,
                                                    (root.clipData && root.clipData.id) ? root.clipData.id : "")
            }
        }

        // CapCut's text pages as a segmented strip: Básico, Burbuja, Efectos and Animación.
        Rectangle {
            visible: !root.inAdvanced
            width: parent.width
            height: visible ? pageStrip.height + 6 : 0
            radius: Theme.radiusSm
            color: Theme.panelAccent

            Row {
                id: pageStrip
                anchors.centerIn: parent
                width: parent.width - 6
                spacing: 2

                // One font size for every label: the largest at which the longest single word
                // still fits its cell, since a word cannot wrap.
                property real cellHeight: 0
                property real labelPx: Theme.fontSizeXs
                onWidthChanged: Qt.callLater(measure)
                Component.onCompleted: Qt.callLater(measure)
                function measure() {
                    const room = (width - 6) / root.pages.length - 8
                    let px = Theme.fontSizeXs
                    for (const page of root.pages) {
                        for (const word of String(page.label).split(" ")) {
                            pageMetrics.text = word
                            if (room > 0 && pageMetrics.advanceWidth > room)
                                px = Math.min(px, Math.floor(Theme.fontSizeXs * room / pageMetrics.advanceWidth))
                        }
                    }
                    labelPx = Math.max(8, px)
                    let h = 0
                    for (let i = 0; i < pageCells.count; i++) {
                        const cell = pageCells.itemAt(i)
                        if (cell)
                            h = Math.max(h, cell.labelHeight)
                    }
                    cellHeight = h + 14
                }

                TextMetrics {
                    id: pageMetrics
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                    font.weight: Font.Medium
                }

                Repeater {
                    id: pageCells
                    model: root.pages
                    delegate: Rectangle {
                        id: pageCell
                        required property var modelData
                        required property int index
                        readonly property bool current: root.page === modelData.id
                        readonly property real labelHeight: pageLabel.implicitHeight
                        onLabelHeightChanged: Qt.callLater(pageStrip.measure)
                        width: (pageStrip.width - 6) / root.pages.length
                        height: pageStrip.cellHeight
                        radius: Theme.radiusSm
                        color: current ? Theme.popoverHover : "transparent"

                        Text {
                            id: pageLabel
                            anchors.centerIn: parent
                            width: parent.width - 8
                            horizontalAlignment: Text.AlignHCenter
                            wrapMode: Text.WordWrap
                            maximumLineCount: 2
                            elide: Text.ElideRight
                            text: pageCell.modelData.label
                            color: pageCell.current ? Theme.foreground : Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: pageStrip.labelPx
                            font.weight: pageCell.current ? Font.Medium : Font.Normal
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: root.textTab = pageCell.modelData.id
                        }
                    }
                }
            }
        }

        // --- Básico ---------------------------------------------------------------------------
        Column {
            width: parent.width
            spacing: Theme.spacingMd
            visible: root.page === "basic"

            CollapsibleSection {
                width: parent.width
                title: qsTr("Text")
                collapsible: false
                showSeparator: false
                // In Texto avanzado the words are typed in its own «Texto de entrada».
                visible: root.clipKind === "text" && !root.inAdvanced

                ThemedTextArea {
                    id: textContentField
                    width: parent.width
                    height: root.contentFieldHeight
                    clip: true
                    placeholderText: qsTr("Type your text…")
                    onEditingFinished: root.applyText()
                    // Sin esto, pulsar cualquier control de estilo quita el foco, se pierde el
                    // sombreado y el efecto se va a todo el texto (probado en ventana, 0.24).
                    persistentSelection: true
                    // Las letras sombreadas aquí son las que reciben los estilos (0.24).
                    onSelectionStartChanged: root.runSelectionStart = selectionStart
                    onSelectionEndChanged: root.runSelectionEnd = selectionEnd
                    // No se limpia en onCursorPositionChanged: al empezar el arrastre la selección
                    // está colapsada y borraba el comienzo, así que el sombreado nunca llegaba
                    // (con la selección vacía hasRunSelection ya es falso por sí solo).
                }

                // A qué se aplica lo que se toque debajo.
                Text {
                    width: parent.width
                    visible: root.hasRunSelection
                    text: qsTr("Applies to the selected letters")
                    color: Theme.primary
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                    wrapMode: Text.WordWrap
                }

                // Drag grip: the field grows and shrinks with it.
                Item {
                    width: parent.width
                    height: 10

                    Rectangle {
                        anchors.centerIn: parent
                        width: 32
                        height: 3
                        radius: 1.5
                        color: gripArea.pressed || gripArea.containsMouse ? Theme.mutedForeground : Theme.panelBorder
                    }

                    MouseArea {
                        id: gripArea
                        anchors.fill: parent
                        anchors.topMargin: -4
                        anchors.bottomMargin: -4
                        hoverEnabled: true
                        preventStealing: true
                        cursorShape: Qt.SizeVerCursor
                        property real pressY: 0
                        property real pressHeight: 0
                        // Measured against the inspector, not the grip: the grip moves as the field grows.
                        onPressed: mouse => {
                            pressY = mapToItem(root, mouse.x, mouse.y).y
                            pressHeight = root.contentFieldHeight
                        }
                        onPositionChanged: mouse => {
                            if (!pressed)
                                return
                            const dy = mapToItem(root, mouse.x, mouse.y).y - pressY
                            root.contentFieldHeight = Math.max(56, Math.min(400, pressHeight + dy))
                        }
                    }
                }

                ThemedButton {
                    width: parent.width
                    variant: "primary"
                    glyph: Theme.icons.check
                    text: qsTr("Apply")
                    enabled: root.contentDirty
                    tooltip: qsTr("Apply the text to this clip")
                    onClicked: root.applyText()
                }
            }

            // Subtitles carry two extra jobs CapCut also puts on the caption's text page.
            Row {
                width: parent.width
                spacing: Theme.spacingSm
                visible: root.clipKind === "subtitle" && root.hasTextStyle

                ThemedButton {
                    width: (parent.width - parent.spacing) * 0.6
                    variant: "secondary"
                    glyph: Theme.icons.captions
                    text: qsTr("Apply to all captions")
                    tooltip: qsTr("Copy this style to every other caption on this track")
                    onClicked: EditorState.applyTextStyleToCaptions(
                                   EditorState.selectedTrack, EditorState.selectedClip, "track")
                }
                ThemedButton {
                    width: (parent.width - parent.spacing) * 0.4
                    variant: "secondary"
                    text: qsTr("…every track")
                    tooltip: qsTr("Copy this style to every caption in the project")
                    onClicked: EditorState.applyTextStyleToCaptions(
                                   EditorState.selectedTrack, EditorState.selectedClip, "project")
                }
            }

            ThemedButton {
                visible: root.clipKind === "subtitle" && root.hasTextStyle
                width: parent.width
                variant: "secondary"
                glyph: Theme.icons.audioLines
                text: qsTr("Generate voiceover")
                enabled: EditorState.tts.available
                tooltip: EditorState.tts.available
                         ? qsTr("Speak every caption with a generated voice")
                         : qsTr("Install the voice model from the add-on manager first")
                onClicked: voiceoverDialog.openFor(EditorState.selectedTrack, EditorState.selectedClip)
            }

            // Font, size, weight, case, colour, spacing and alignment: CapCut's Básico head.
            Column {
                width: parent.width
                spacing: Theme.spacingMd
                visible: root.hasTextStyle

                Text {
                    text: qsTr("Font")
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                }

                FontPicker {
                    width: parent.width
                    family: root.textStyle.fontFamily
                    onFamilyPicked: family => root.setTextStyleKey("fontFamily", family)
                }

                PropertyKeyframeRow {
                    width: parent.width
                    propDef: root.textProp("pixelSize", qsTr("Font size"), 0)
                    keyframeList: root.textKeyframes("pixelSize")
                    useSlider: true
                    sliderFrom: 1
                    sliderTo: 500
                    unit: "px"
                }

                Row {
                    width: parent.width
                    spacing: Theme.spacingSm

                    Text {
                        width: 74
                        anchors.verticalCenter: parent.verticalCenter
                        text: qsTr("Style")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                    ThemedToggleButton {
                        width: 34
                        text: "B"
                        checked: Number(root.textStyle.fontWeight) >= 600
                        tooltip: qsTr("Bold")
                        onClicked: root.setTextStyleKey("fontWeight", root.boldToggleWeight())
                    }
                    ThemedToggleButton {
                        width: 34
                        text: "U"
                        checked: root.textStyle.underlineEnabled === true
                        tooltip: qsTr("Underline")
                        onClicked: root.toggleUnderline()
                    }
                    ThemedToggleButton {
                        width: 34
                        text: "S"
                        checked: root.textStyle.strikeEnabled === true
                        tooltip: qsTr("Strikethrough")
                        onClicked: root.setTextStyleKey("strikeEnabled", root.textStyle.strikeEnabled !== true)
                    }
                    ThemedToggleButton {
                        width: 34
                        text: "I"
                        checked: root.textStyle.italic === true
                        enabled: root.familyHasItalic
                        tooltip: root.familyHasItalic ? qsTr("Italic")
                                                      : qsTr("%1 has no italic face").arg(root.textStyle.fontFamily)
                        onClicked: root.setTextStyleKey("italic", !root.textStyle.italic)
                    }
                    ThemedComboBox {
                        id: fontWeightBox
                        width: Math.max(80, parent.width - 74 - 34 * 4 - parent.spacing * 5) // B, U, S, I
                        model: root.availableWeights.map(w => root.weightLabels[w] || String(w))
                        currentIndex: Math.max(0, root.availableWeights.indexOf(root.textStyle.fontWeight))
                        onActivated: root.setTextStyleKey("fontWeight", root.availableWeights[currentIndex])
                    }
                }

                Row {
                    width: parent.width
                    spacing: Theme.spacingSm

                    Text {
                        width: 74
                        anchors.verticalCenter: parent.verticalCenter
                        text: qsTr("Case")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                    Repeater {
                        model: [
                            { "id": "none", "label": "Aa", "tip": qsTr("As typed") },
                            { "id": "upper", "label": "TT", "tip": qsTr("UPPERCASE") },
                            { "id": "lower", "label": "tt", "tip": qsTr("lowercase") },
                            { "id": "title", "label": "Tt", "tip": qsTr("Title Case") }
                        ]
                        delegate: ThemedToggleButton {
                            required property var modelData
                            width: 40
                            text: modelData.label
                            tooltip: modelData.tip
                            checked: (root.textStyle.textCase || "none") === modelData.id
                            onClicked: root.setTextStyleKey("textCase", modelData.id)
                        }
                    }
                }

                // Animated counter: the number in the text counts up over the clip.
                Row {
                    width: parent.width
                    spacing: Theme.spacingSm

                    Text {
                        width: 74
                        anchors.verticalCenter: parent.verticalCenter
                        text: qsTr("Counter")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                    ThemedSwitch {
                        anchors.verticalCenter: parent.verticalCenter
                        checked: !!root.textStyle.counter
                        tooltip: qsTr("The number in the text counts up over the clip, as in a counter: $1.000.000, 10K, day 100…")
                        onToggled: root.setTextStyleKey("counter", checked)
                    }
                    Text {
                        visible: !!root.textStyle.counter
                        anchors.verticalCenter: parent.verticalCenter
                        text: qsTr("from")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                    ThemedTextField {
                        visible: !!root.textStyle.counter
                        width: 90
                        anchors.verticalCenter: parent.verticalCenter
                        text: String(root.textStyle.counterFrom || 0)
                        inputMethodHints: Qt.ImhFormattedNumbersOnly
                        onEditingFinished: {
                            const v = Number(text.replace(",", "."))
                            if (!isNaN(v))
                                root.setTextStyleKey("counterFrom", v)
                        }
                    }
                }

                Row {
                    width: parent.width
                    spacing: Theme.spacingSm

                    Text {
                        width: 74
                        anchors.verticalCenter: parent.verticalCenter
                        text: qsTr("Colour")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }
                    ColorSwatchField {
                        visible: root.frontFillPaintKind === "solid" || root.frontFillPaintKind === "gradient"
                        hex: root.frontFillColor
                        tooltip: root.frontFillPaintKind === "gradient"
                                 ? qsTr("Choose the gradient's first colour")
                                 : qsTr("Choose text colour")
                        onEdited: value => root.setTextStyleKey("color", value)
                    }
                    ThemedChip {
                        visible: root.frontFillPaintKind === "texture" || root.frontFillPaintKind === "effect"
                        text: qsTr("Edit in Advanced")
                        tooltip: root.frontFillPaintKind === "texture"
                                 ? qsTr("The text is painted with an image; change it under Advanced")
                                 : qsTr("The text is painted with an effect; change it under Advanced")
                        onClicked: {
                            root.advancedOpen = true
                            if (root.frontFill)
                                root.setLayerExpanded(root.frontFill.id, true)
                        }
                    }
                }

                Row {
                    width: parent.width
                    spacing: 8

                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.textProp("letterSpacing", qsTr("Character"), 1)
                        keyframeList: root.textKeyframes("letterSpacing")
                        useSlider: true
                        sliderFrom: -100
                        sliderTo: 200
                        unit: "px"
                    }
                    PropertyKeyframeRow {
                        width: (parent.width - parent.spacing) / 2
                        propDef: root.textProp("lineHeight", qsTr("Line"), 2)
                        keyframeList: root.textKeyframes("lineHeight")
                        useSlider: true
                        sliderFrom: 0.5
                        sliderTo: 4
                    }
                }

                // Space added between words (0.22.1), apart from the letters' spacing.
                SliderRow {
                    width: parent.width
                    label: qsTr("Word spacing")
                    from: -20
                    to: 200
                    suffix: " px"
                    value: Number(root.textStyle.wordSpacing) || 0
                    onCommitted: v => root.setTextStyleKey("wordSpacing", Math.round(v))
                }

                Text {
                    text: qsTr("Alignment")
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                }

                Flow {
                    width: parent.width
                    spacing: Theme.spacingSm

                    Repeater {
                        model: [
                            { value: "left",   glyph: Theme.icons.alignLeft,   label: qsTr("Align left") },
                            { value: "center", glyph: Theme.icons.alignCenter, label: qsTr("Align centre") },
                            { value: "right",  glyph: Theme.icons.alignRight,  label: qsTr("Align right") },
                            { value: "justify", glyph: Theme.icons.alignJustify, label: qsTr("Justify") }
                        ]
                        delegate: ThemedToggleButton {
                            required property var modelData
                            width: 34
                            glyph: modelData.glyph
                            checked: root.textStyle.align === modelData.value
                            tooltip: modelData.label
                            onClicked: root.setTextStyleKey("align", modelData.value)
                        }
                    }

                    Rectangle {
                        width: Theme.borderWidth
                        height: Theme.controlHeightSm
                        color: Theme.panelBorder
                    }

                    Repeater {
                        model: [
                            { value: "top",    glyph: Theme.icons.alignTop,    label: qsTr("Align top") },
                            { value: "middle", glyph: Theme.icons.alignMiddle, label: qsTr("Align middle") },
                            { value: "bottom", glyph: Theme.icons.alignBottom, label: qsTr("Align bottom") }
                        ]
                        delegate: ThemedToggleButton {
                            required property var modelData
                            width: 34
                            glyph: modelData.glyph
                            checked: root.textStyle.valign === modelData.value
                            tooltip: modelData.label
                            onClicked: root.setTextStyleKey("valign", modelData.value)
                        }
                    }

                    ThemedToggleButton {
                        width: 96
                        text: qsTr("Word wrap")
                        checked: root.textStyle.wordWrap
                        tooltip: qsTr("Wrap long lines inside the text box instead of overflowing")
                        onClicked: root.setTextStyleKey("wordWrap", !root.textStyle.wordWrap)
                    }
                }
            }

            // --- Estilo preestablecido: one tap over the clip's own font ---------------------------
            CollapsibleSection {
                width: parent.width
                title: qsTr("Preset style")
                tooltip: qsTr("Colour, outline and shadow in one tap, keeping your font")
                collapsible: false
                visible: root.hasTextStyle

                Grid {
                    id: quickGrid
                    width: parent.width
                    readonly property real gap: Theme.spacingSm
                    columns: Math.max(3, Math.floor((width + gap) / (64 + gap)))
                    columnSpacing: gap
                    rowSpacing: gap
                    readonly property real tileWidth: Math.floor((width - gap * (columns - 1)) / columns)

                    GalleryTile {
                        tileWidth: quickGrid.tileWidth
                        none: true
                        showLabel: false
                        label: qsTr("No style")
                        selected: root.lastQuickId === "q-plain"
                        onClicked: root.applyQuick("q-plain")
                    }

                    Repeater {
                        model: root.quickStyles.filter(q => q.category === "basic")
                        delegate: GalleryTile {
                            required property var modelData
                            tileWidth: quickGrid.tileWidth
                            showLabel: false
                            label: modelData.label
                            source: root.quickPreview(modelData.id)
                            selected: root.lastQuickId === modelData.id
                            onClicked: root.applyQuick(modelData.id)
                        }
                    }
                }

                ThemedButton {
                    width: parent.width
                    variant: "secondary"
                    glyph: Theme.icons.sparkles
                    text: qsTr("More styles: neon, gradient, 3D…")
                    onClicked: root.textTab = "effects"
                }
            }

            // --- Trazo ---------------------------------------------------------------------------
            CollapsibleSection {
                width: parent.width
                title: qsTr("Stroke")
                tooltip: qsTr("An outline around the letters")
                visible: root.hasTextStyle
                showSwitch: true
                switchChecked: root.layerOn("stroke")
                switchTooltip: qsTr("Outline the text")
                onSwitchToggled: on => root.enableLayer("stroke", on, {
                                     "width": root.em * 0.07, "paint": { "color": "#ff000000" } })

                Column {
                    width: parent.width
                    spacing: Theme.spacingMd
                    enabled: root.layerOn("stroke")
                    opacity: enabled ? 1 : 0.5

                    Row {
                        spacing: Theme.spacingSm
                        Text {
                            width: 74
                            anchors.verticalCenter: parent.verticalCenter
                            text: qsTr("Colour")
                            color: Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                        ColorSwatchField {
                            hex: root.layerColor(root.strokeLayer, "#ff000000")
                            tooltip: qsTr("Choose outline colour")
                            onEdited: value => root.setLayerKey(root.strokeLayer, { "paint": { "color": value } })
                        }
                    }

                    PropertyKeyframeRow {
                        width: parent.width
                        visible: !!root.strokeLayer
                        propDef: root.layerProp(root.strokeLayer, "width", qsTr("Thickness"), 1)
                        keyframeList: root.layerKeyframes(root.strokeLayer, "width")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: Math.max(10, root.em * 0.4)
                        unit: "px"
                    }
                }
            }

            // --- Fondo ---------------------------------------------------------------------------
            CollapsibleSection {
                width: parent.width
                title: qsTr("Background")
                tooltip: qsTr("A box behind the text: one for the block or one per line")
                visible: root.hasTextStyle
                showSwitch: true
                switchChecked: root.boxSource.boxEnabled === true
                switchTooltip: qsTr("Draw a box behind the text")
                onSwitchToggled: on => root.setTextStyleKey("boxEnabled", on)

                Column {
                    width: parent.width
                    spacing: Theme.spacingMd
                    enabled: root.boxSource.boxEnabled === true
                    opacity: enabled ? 1 : 0.5

                    Row {
                        width: parent.width
                        spacing: Theme.spacingSm

                        Repeater {
                            model: [
                                { "id": "block", "label": qsTr("Whole block") },
                                { "id": "line", "label": qsTr("Per line") }
                            ]
                            delegate: ThemedToggleButton {
                                required property var modelData
                                width: (parent.width - parent.spacing) / 2
                                text: modelData.label
                                checked: (root.boxSource.boxStyle || "block") === modelData.id
                                onClicked: root.setTextStyleKey("boxStyle", modelData.id)
                            }
                        }
                    }

                    // Only the outline of the box: the Bubble gallery replaces the whole look, this
                    // keeps the text's layers, colours and padding.
                    Row {
                        spacing: Theme.spacingSm
                        Text {
                            width: 74
                            anchors.verticalCenter: parent.verticalCenter
                            text: qsTr("Shape")
                            color: Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                        ThemedComboBox {
                            width: parent.parent.width - 74 - Theme.spacingSm
                            readonly property var shapes: [
                                { "id": "rect", "label": qsTr("Rectangle") },
                                { "id": "pill", "label": qsTr("Pill") },
                                { "id": "speech", "label": qsTr("Speech bubble") },
                                { "id": "oval", "label": qsTr("Oval") },
                                { "id": "thought", "label": qsTr("Thought bubble") },
                                { "id": "cloud", "label": qsTr("Cloud") },
                                { "id": "burst", "label": qsTr("Burst") },
                                { "id": "shout", "label": qsTr("Shout") },
                                { "id": "tag", "label": qsTr("Tag") },
                                { "id": "ribbon", "label": qsTr("Ribbon") },
                                { "id": "arrow", "label": qsTr("Arrow") },
                                { "id": "note", "label": qsTr("Note") },
                                { "id": "ticket", "label": qsTr("Ticket") },
                                { "id": "brush", "label": qsTr("Brush stroke") },
                                { "id": "torn", "label": qsTr("Torn paper") },
                                { "id": "heart", "label": qsTr("Heart") }
                            ]
                            model: shapes.map(s => s.label)
                            currentIndex: Math.max(0, shapes.findIndex(s => s.id === (root.boxSource.boxShape || "rect")))
                            onActivated: root.setTextStyleKey("boxShape", shapes[currentIndex].id)
                        }
                    }

                    Row {
                        spacing: Theme.spacingSm
                        Text {
                            width: 74
                            anchors.verticalCenter: parent.verticalCenter
                            text: qsTr("Colour")
                            color: Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                        ColorSwatchField {
                            hex: root.boxSource.boxColor
                            tooltip: qsTr("Choose background colour")
                            onEdited: value => root.setTextStyleKey("boxColor", root.keepAlpha(value, root.boxSource.boxColor))
                        }
                    }

                    SliderRow {
                        width: parent.width
                        label: qsTr("Opacity")
                        from: 0
                        to: 1
                        displayScale: 100
                        suffix: "%"
                        value: root.hexAlpha(root.boxSource.boxColor)
                        onCommitted: v => root.setTextStyleKey("boxColor", root.withAlpha(root.boxSource.boxColor, v))
                    }

                    SliderRow {
                        width: parent.width
                        label: qsTr("Rounded corners")
                        from: 0
                        to: 1
                        displayScale: 100
                        suffix: "%"
                        value: Number(root.boxSource.boxRadius) / root.em
                        onCommitted: v => root.setTextStyleKey("boxRadius", v * root.em)
                    }

                    SliderRow {
                        width: parent.width
                        label: qsTr("Height")
                        from: 0
                        to: 1.5
                        displayScale: 100
                        suffix: "%"
                        value: Number(root.boxSource.boxPaddingY) / root.em
                        onCommitted: v => root.setTextStyleKey("boxPaddingY", v * root.em)
                    }

                    SliderRow {
                        width: parent.width
                        label: qsTr("Width")
                        from: 0
                        to: 2
                        displayScale: 100
                        suffix: "%"
                        value: Number(root.boxSource.boxPaddingX) / root.em
                        onCommitted: v => root.setTextStyleKey("boxPaddingX", v * root.em)
                    }

                    SliderRow {
                        width: parent.width
                        label: qsTr("Offset Y")
                        from: -1
                        to: 1
                        displayScale: 100
                        suffix: "%"
                        value: Number(root.boxSource.boxOffsetY) / root.em
                        onCommitted: v => root.setTextStyleKey("boxOffsetY", v * root.em)
                    }

                    SliderRow {
                        width: parent.width
                        label: qsTr("Offset X")
                        from: -1
                        to: 1
                        displayScale: 100
                        suffix: "%"
                        value: Number(root.boxSource.boxOffsetX) / root.em
                        onCommitted: v => root.setTextStyleKey("boxOffsetX", v * root.em)
                    }

                    Row {
                        spacing: Theme.spacingSm
                        Text {
                            width: 74
                            anchors.verticalCenter: parent.verticalCenter
                            text: qsTr("Border")
                            color: Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                        ColorSwatchField {
                            hex: root.boxSource.boxBorderColor || "#ff000000"
                            tooltip: qsTr("Choose border colour")
                            onEdited: value => root.setTextStyleKey("boxBorderColor", value)
                        }
                    }

                    SliderRow {
                        width: parent.width
                        label: qsTr("Border thickness")
                        from: 0
                        to: 0.3
                        displayScale: 100
                        suffix: "%"
                        value: Number(root.boxSource.boxBorderWidth) / root.em
                        onCommitted: v => root.setTextStyleKey("boxBorderWidth", v * root.em)
                    }

                    ThemedButton {
                        width: parent.width
                        variant: "secondary"
                        glyph: Theme.icons.messageSquare
                        text: qsTr("Shapes: speech, cloud, tag, brush…")
                        tooltip: qsTr("Pick a bubble shape on the Bubble page")
                        onClicked: root.textTab = "bubble"
                    }
                }
            }

            // --- Brillo --------------------------------------------------------------------------
            CollapsibleSection {
                width: parent.width
                title: qsTr("Glow")
                tooltip: qsTr("A soft light around the letters")
                visible: root.hasTextStyle
                showSwitch: true
                switchChecked: root.layerOn("glow")
                switchTooltip: qsTr("Add a glow")
                onSwitchToggled: on => root.enableLayer("glow", on, {
                                     "blur": root.em * 0.35, "opacity": 0.9, "paint": { "color": "#ffffffff" } })

                Column {
                    width: parent.width
                    spacing: Theme.spacingMd
                    enabled: root.layerOn("glow")
                    opacity: enabled ? 1 : 0.5

                    Row {
                        width: parent.width
                        spacing: Theme.spacingSm
                        ThemedToggleButton {
                            width: (parent.width - parent.spacing) / 2
                            text: qsTr("Soft")
                            checked: !!root.glowLayer && Number(root.glowLayer.spread) <= 0.001
                            onClicked: root.setLayerKey(root.glowLayer, { "blur": root.em * 0.45, "spread": 0, "opacity": 0.75 })
                        }
                        ThemedToggleButton {
                            width: (parent.width - parent.spacing) / 2
                            text: qsTr("Strong")
                            checked: !!root.glowLayer && Number(root.glowLayer.spread) > 0.001
                            onClicked: root.setLayerKey(root.glowLayer, { "blur": root.em * 0.25, "spread": root.em * 0.04, "opacity": 1 })
                        }
                    }

                    Row {
                        spacing: Theme.spacingSm
                        Text {
                            width: 74
                            anchors.verticalCenter: parent.verticalCenter
                            text: qsTr("Colour")
                            color: Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                        ColorSwatchField {
                            hex: root.layerColor(root.glowLayer, "#ffffffff")
                            tooltip: qsTr("Choose glow colour")
                            onEdited: value => root.setLayerKey(root.glowLayer, { "paint": { "color": value } })
                        }
                    }

                    PropertyKeyframeRow {
                        width: parent.width
                        visible: !!root.glowLayer
                        propDef: root.layerProp(root.glowLayer, "opacity", qsTr("Intensity"), 2)
                        keyframeList: root.layerKeyframes(root.glowLayer, "opacity")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: 1
                        percent: true
                    }
                    PropertyKeyframeRow {
                        width: parent.width
                        visible: !!root.glowLayer
                        propDef: root.layerProp(root.glowLayer, "blur", qsTr("Range"), 1)
                        keyframeList: root.layerKeyframes(root.glowLayer, "blur")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: Math.max(20, root.em * 1.5)
                        unit: "px"
                    }
                    Row {
                        width: parent.width
                        spacing: 8
                        visible: !!root.glowLayer
                        PropertyKeyframeRow {
                            width: (parent.width - parent.spacing) / 2
                            propDef: root.layerProp(root.glowLayer, "offsetX", qsTr("Offset X"), 1)
                            keyframeList: root.layerKeyframes(root.glowLayer, "offsetX")
                            useSlider: true
                            sliderFrom: -root.em
                            sliderTo: root.em
                            unit: "px"
                        }
                        PropertyKeyframeRow {
                            width: (parent.width - parent.spacing) / 2
                            propDef: root.layerProp(root.glowLayer, "offsetY", qsTr("Offset Y"), 1)
                            keyframeList: root.layerKeyframes(root.glowLayer, "offsetY")
                            useSlider: true
                            sliderFrom: -root.em
                            sliderTo: root.em
                            unit: "px"
                        }
                    }
                }
            }

            // --- Sombra --------------------------------------------------------------------------
            CollapsibleSection {
                width: parent.width
                title: qsTr("Shadow")
                tooltip: qsTr("A shadow cast by the letters")
                visible: root.hasTextStyle
                showSwitch: true
                switchChecked: root.layerOn("shadow")
                switchTooltip: qsTr("Add a shadow")
                onSwitchToggled: on => root.enableLayer("shadow", on, {
                                     "offsetX": root.em * 0.05, "offsetY": root.em * 0.05,
                                     "blur": root.em * 0.12, "opacity": 0.8, "paint": { "color": "#ff000000" } })

                Column {
                    width: parent.width
                    spacing: Theme.spacingMd
                    enabled: root.layerOn("shadow")
                    opacity: enabled ? 1 : 0.5

                    Row {
                        spacing: Theme.spacingSm
                        Text {
                            width: 74
                            anchors.verticalCenter: parent.verticalCenter
                            text: qsTr("Colour")
                            color: Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                        ColorSwatchField {
                            hex: root.layerColor(root.shadowLayer, "#ff000000")
                            tooltip: qsTr("Choose shadow colour")
                            onEdited: value => root.setLayerKey(root.shadowLayer, { "paint": { "color": value } })
                        }
                    }

                    PropertyKeyframeRow {
                        width: parent.width
                        visible: !!root.shadowLayer
                        propDef: root.layerProp(root.shadowLayer, "opacity", qsTr("Opacity"), 2)
                        keyframeList: root.layerKeyframes(root.shadowLayer, "opacity")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: 1
                        percent: true
                    }
                    PropertyKeyframeRow {
                        width: parent.width
                        visible: !!root.shadowLayer
                        propDef: root.layerProp(root.shadowLayer, "blur", qsTr("Blur"), 1)
                        keyframeList: root.layerKeyframes(root.shadowLayer, "blur")
                        useSlider: true
                        sliderFrom: 0
                        sliderTo: Math.max(20, root.em)
                        unit: "px"
                    }
                    SliderRow {
                        width: parent.width
                        visible: !!root.shadowLayer
                        label: qsTr("Distance")
                        from: 0
                        to: Math.max(10, root.em * 0.5)
                        decimals: 0
                        suffix: " px"
                        value: root.shadowDistance
                        onDragStarted: root.beginLayerDrag(qsTr("Adjust shadow"))
                        onMoved: v => root.previewLayer(root.shadowLayer, root.shadowOffsets(v, root.shadowAngle))
                        onCommitted: v => root.commitLayer(root.shadowLayer, root.shadowOffsets(v, root.shadowAngle))
                    }
                    SliderRow {
                        width: parent.width
                        visible: !!root.shadowLayer
                        label: qsTr("Angle")
                        from: -180
                        to: 180
                        stepSize: 1
                        decimals: 0
                        suffix: "°"
                        value: root.shadowAngle
                        onDragStarted: root.beginLayerDrag(qsTr("Adjust shadow"))
                        onMoved: v => root.previewLayer(root.shadowLayer, root.shadowOffsets(root.shadowDistance, v))
                        onCommitted: v => root.commitLayer(root.shadowLayer, root.shadowOffsets(root.shadowDistance, v))
                    }
                }
            }

            // --- Curva ---------------------------------------------------------------------------
            CollapsibleSection {
                width: parent.width
                title: qsTr("Curve")
                tooltip: qsTr("Bend a single line of text along an arc")
                visible: root.hasTextStyle
                showSwitch: true
                switchChecked: Math.abs(Number(root.textStyle.pathBend) || 0) > 0.01
                               || Number(root.textStyle.pathCircle) > 0
                switchTooltip: qsTr("Bend the text")
                onSwitchToggled: on => {
                    if (on)
                        root.setTextStyleKey("pathBend", 40)
                    else
                        EditorState.setTextStyle(EditorState.selectedTrack, EditorState.selectedClip,
                                                 { "pathBend": 0, "pathCircle": 0 })
                }

                PropertyKeyframeRow {
                    width: parent.width
                    visible: !(Number(root.textStyle.pathCircle) > 0)
                    propDef: root.textProp("pathBend", qsTr("Strength"), 0)
                    keyframeList: root.textKeyframes("pathBend")
                    useSlider: true
                    sliderFrom: -100
                    sliderTo: 100
                }

                // All the way round (0.22.1): the line wraps a circle instead of an arc.
                ThemedCheckBox {
                    width: parent.width
                    text: qsTr("Around a circle")
                    checked: Number(root.textStyle.pathCircle) > 0
                    onToggled: root.setTextStyleKey("pathCircle", checked ? 100 : 0)
                }
                SliderRow {
                    width: parent.width
                    visible: Number(root.textStyle.pathCircle) > 0
                    label: qsTr("Circle covered")
                    from: 10
                    to: 100
                    suffix: " %"
                    value: Number(root.textStyle.pathCircle) || 100
                    onCommitted: v => root.setTextStyleKey("pathCircle", Math.round(v))
                }
                ThemedCheckBox {
                    width: parent.width
                    visible: Number(root.textStyle.pathCircle) > 0
                    text: qsTr("Letters inside the circle")
                    checked: Number(root.textStyle.pathBend) < 0
                    onToggled: root.setTextStyleKey("pathBend", checked ? -40 : 40)
                }
            }

            // Your own template: this text's whole look, kept under Efectos → My styles and the Text tab.
            ThemedButton {
                width: parent.width
                visible: root.hasTextStyle
                variant: "secondary"
                glyph: Theme.icons.save
                text: qsTr("Save as my style…")
                tooltip: qsTr("Keep this text's font, colours, background and effects to reuse them")
                onClicked: saveStyleDialog.openWith(qsTr("Save text style"),
                                                    qsTr("My style %1")
                                                        .arg(EditorState.userTextPresets().length + 1))
            }

            // --- Transformación y Mezcla, as on CapCut's text page ------------------------------------
            CollapsibleSection {
                width: parent.width
                title: qsTr("Transform")
                expanded: false
                visible: root.hasTextStyle

                Column {
                    width: parent.width
                    spacing: Theme.spacingSm
                    visible: root.hasRunSelection

                    Text {
                        width: parent.width
                        text: qsTr("These letters move, scale and turn on their own: the rest of the text stays put.")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                        wrapMode: Text.WordWrap
                    }

                    ThemedNumberField {
                        width: parent.width
                        unit: "X"
                        value: root.runTransformValue("offsetX", 0.0)
                        onEdited: v => root.setRunTransform("offsetX", v)
                    }
                    ThemedNumberField {
                        width: parent.width
                        unit: "Y"
                        value: root.runTransformValue("offsetY", 0.0)
                        onEdited: v => root.setRunTransform("offsetY", v)
                    }
                    ThemedNumberField {
                        width: parent.width
                        // Ya traducido en esos contextos: no hace falta otro texto en el catálogo.
                        unit: qsTranslate("TransformInspector", "Scale")
                        decimals: 2
                        step: 0.05
                        from: 0.05
                        to: 20
                        value: root.runTransformValue("transformScale", 1.0)
                        onEdited: v => root.applyStyle({ "transformScale": v })
                    }
                    ThemedNumberField {
                        width: parent.width
                        unit: qsTranslate("KeyframeGraph", "Rotation")
                        decimals: 1
                        from: -360
                        to: 360
                        value: root.runTransformValue("rotation", 0.0)
                        onEdited: v => root.applyStyle({ "rotation": v })
                    }
                }

                TransformInspector {
                    width: parent.width
                    // Con letras sombreadas, lo de arriba manda en ellas; esto queda para el clip.
                    visible: !root.hasRunSelection
                    sizeLinked: EditorState.sizeLinked
                    onSizeLinkedChanged: EditorState.sizeLinked = sizeLinked
                    positionLinked: EditorState.positionLinked
                    onPositionLinkedChanged: EditorState.positionLinked = positionLinked
                }
            }

            CollapsibleSection {
                width: parent.width
                title: qsTr("Blend")
                expanded: false
                visible: root.hasTextStyle

                BlendingInspector { width: parent.width }
            }

            // --- Avanzado: the full layer stack, packs, decorations and word accents ----------------
            CollapsibleSection {
                width: parent.width
                title: qsTr("Advanced")
                tooltip: qsTr("Every layer of the look, style packs, word highlight, underline and word accents")
                expanded: root.advancedOpen
                onExpandedChanged: root.advancedOpen = expanded
                visible: root.hasTextStyle

                CollapsibleSection {
                    width: parent.width
                    title: qsTr("Preset")
                    tooltip: qsTr("A whole text style — font, colour and effect — applied in one tap")
                    collapsible: false
                    showSeparator: false
                    visible: root.hasTextStyle

                    Text {
                        width: parent.width
                        wrapMode: Text.WordWrap
                        text: qsTr("Font, colour and effect in one tap. Save your own to reuse it.")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }

                    TextStylePackPicker {
                        width: parent.width
                        packId: root.textStyle.packId || ""
                        onPackPicked: id => EditorState.applyTextPreset(
                                           EditorState.selectedTrack,
                                           EditorState.selectedClip,
                                           id)
                    }

                    ThemedButton {
                        width: parent.width
                        variant: "secondary"
                        glyph: Theme.icons.save
                        text: qsTr("Save style…")
                        tooltip: qsTr("Save this text's style as a reusable preset")
                        onClicked: saveStyleDialog.openWith(qsTr("Save text style"),
                                                            qsTr("My style %1")
                                                                .arg(EditorState.userTextPresets().length + 1))
                    }

                }

                CollapsibleSection {
                    width: parent.width
                    title: qsTr("Effect")
                    tooltip: qsTr("Shadow, outline, neon and friends — a recipe that builds the layers below")
                    collapsible: false
                    visible: root.hasTextStyle

                    Text {
                        width: parent.width
                        wrapMode: Text.WordWrap
                        text: qsTr("Shadow, outline, neon… built as layers you can fine-tune below.")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }

                    TextLookPicker {
                        width: parent.width
                        lookId: root.textStyle.lookId || ""
                        sampleText: root.lookSampleText
                        fontFamily: root.textStyle.fontFamily || ""
                        fontWeight: Math.round(Number(root.textStyle.fontWeight) || 400)
                        italic: root.textStyle.italic === true
                        onLookPicked: id => EditorState.applyTextLook(EditorState.selectedTrack,
                                                                      EditorState.selectedClip, id)
                    }

                    TextParamSlots {
                        width: parent.width
                        visible: !!root.selectedLook && (root.selectedLook.params || []).length > 0
                        specs: root.selectedLook ? (root.selectedLook.params || []) : []
                        values: root.textStyle.lookParams || ({})
                        onChanged: (id, value) => EditorState.setTextLookParam(
                                       EditorState.selectedTrack, EditorState.selectedClip, id, value)
                        onPreviewChanged: (id, value) => EditorState.previewSetTextLookParam(
                                              EditorState.selectedTrack, EditorState.selectedClip, id, value)
                        onDragStarted: EditorState.beginPreviewDrag(qsTr("Adjust text look"))
                        onDragEnded: EditorState.commitPreviewDrag()
                    }

                    Row {
                        width: parent.width
                        spacing: Theme.spacingSm

                        Text {
                            width: parent.width - addLayerButton.width - parent.spacing
                            anchors.verticalCenter: parent.verticalCenter
                            text: qsTr("Layers")
                            color: Theme.panelForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeSm
                            font.weight: Font.DemiBold
                        }
                        ThemedButton {
                            id: addLayerButton
                            variant: "secondary"
                            glyph: Theme.icons.plus
                            text: qsTr("Add layer")
                            tooltip: qsTr("Add a fill, stroke, shadow, glow or extrude layer")
                            onClicked: addLayerMenu.popup()

                            ThemedContextMenu {
                                id: addLayerMenu
                                ThemedMenuItem { text: qsTr("Fill"); onTriggered: root.addLayer("fill") }
                                ThemedMenuItem { text: qsTr("Stroke"); onTriggered: root.addLayer("stroke") }
                                ThemedMenuItem { text: qsTr("Shadow"); onTriggered: root.addLayer("shadow") }
                                ThemedMenuItem { text: qsTr("Glow"); onTriggered: root.addLayer("glow") }
                                ThemedMenuItem { text: qsTr("Extrude"); onTriggered: root.addLayer("extrude") }
                            }
                        }
                    }

                    Text {
                        visible: root.layers.length === 0
                        width: parent.width
                        wrapMode: Text.WordWrap
                        text: qsTr("No layers. Pick an effect above or add a fill to start.")
                        color: Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                    }

                    // Integer model so rows survive the fresh QVariantList every edit produces; the list
                    // is walked from the back so the front-most layer sits on top.
                    Repeater {
                        model: root.layers.length
                        delegate: ShadingLayerRow {
                            required property int index
                            width: parent.width
                            layerData: root.layers[root.layers.length - 1 - index] || ({})
                            styleData: root.textStyle
                            position: index
                            count: root.layers.length
                            expanded: root.expandedLayerIds[layerId] === true
                            onToggleRequested: root.setLayerExpanded(layerId, !expanded)
                        }
                    }

                    CollapsibleSection {
                        width: parent.width
                        title: qsTr("Decorations")
                        tooltip: qsTr("Boxes and rules drawn around the text rather than on it")
                        expanded: false

                        CollapsibleSection {
                            width: parent.width
                            title: qsTr("Word highlight")
                            tooltip: qsTr("Filled pill behind every word, sized to the word itself")
                            collapsible: false
                            showSeparator: false
                            showSwitch: true
                            switchChecked: root.textStyle.wordHighlight.enabled
                            switchTooltip: qsTr("Filled pill behind every word, sized to the word itself")
                            onSwitchToggled: on => root.setTextGroupKey("wordHighlight", "enabled", on)

                            Row {
                                width: parent.width
                                spacing: 8

                                Column {
                                    width: (parent.width - parent.spacing) / 2
                                    spacing: 4
                                    Text {
                                        text: qsTr("Thickness")
                                        HoverHandler { id: tipHoverHlPad }
                                        TapHandler {
                                            id: tipTapHlPad
                                            acceptedDevices: PointerDevice.TouchScreen
                                            onLongPressed: tipHlPad.held = true
                                            onPressedChanged: if (!pressed) tipHlPad.held = false
                                        }
                                        ThemedToolTip { id: tipHlPad; property bool held: false; text: qsTr("How far the pill extends past the word"); visible: tipHoverHlPad.hovered || held }
                                        color: Theme.mutedForeground
                                        font.pixelSize: Theme.fontSizeXs
                                        font.family: Theme.fontFamily
                                    }
                                    ThemedNumberField {
                                        id: wordHighlightPaddingField
                                        to: 200
                                        unit: "px"
                                        width: parent.width
                                        decimals: 1
                                        step: 1
                                        from: 0
                                        onEdited: v => root.setTextGroupKey("wordHighlight", "padding", v)
                                    }
                                }

                                Column {
                                    width: (parent.width - parent.spacing) / 2
                                    spacing: 4
                                    Text {
                                        text: qsTr("Corner radius")
                                        color: Theme.mutedForeground
                                        font.pixelSize: Theme.fontSizeXs
                                        font.family: Theme.fontFamily
                                    }
                                    ThemedNumberField {
                                        id: wordHighlightRadiusField
                                        to: 200
                                        unit: "px"
                                        width: parent.width
                                        decimals: 1
                                        step: 1
                                        from: 0
                                        onEdited: v => root.setTextGroupKey("wordHighlight", "radius", v)
                                    }
                                }
                            }

                            Column {
                                width: parent.width
                                spacing: 4
                                Text {
                                    text: qsTr("Highlight colour")
                                    color: Theme.mutedForeground
                                    font.pixelSize: Theme.fontSizeXs
                                    font.family: Theme.fontFamily
                                }
                                ColorSwatchField {
                                    hex: root.textStyle.wordHighlight.color
                                    tooltip: qsTr("Choose highlight colour")
                                    onEdited: value => root.setTextGroupKey("wordHighlight", "color", value)
                                }
                            }
                        }

                        CollapsibleSection {
                            width: parent.width
                            title: qsTr("Underline")
                            tooltip: qsTr("Draw a rule under each line of text")
                            collapsible: false
                            showSeparator: false
                            showSwitch: true
                            switchChecked: root.textStyle.underlineEnabled
                            switchTooltip: qsTr("Draw a rule under each line of text")
                            onSwitchToggled: on => root.setTextStyleKey("underlineEnabled", on)

                            Row {
                                width: parent.width
                                spacing: 8

                                Column {
                                    width: (parent.width - parent.spacing) / 2
                                    spacing: 4
                                    Text {
                                        text: qsTr("Thickness")
                                        color: Theme.mutedForeground
                                        font.pixelSize: Theme.fontSizeXs
                                        font.family: Theme.fontFamily
                                    }
                                    ThemedNumberField {
                                        id: underlineWidthField
                                        to: 100
                                        unit: "px"
                                        width: parent.width
                                        decimals: 1
                                        step: 0.5
                                        from: 0
                                        onEdited: v => root.setTextStyleKey("underlineWidth", v)
                                    }
                                }

                                Column {
                                    width: (parent.width - parent.spacing) / 2
                                    spacing: 4
                                    Text {
                                        text: qsTr("Offset")
                                        HoverHandler { id: tipHoverUnderlineOffset }
                                        TapHandler {
                                            id: tipTapUnderlineOffset
                                            acceptedDevices: PointerDevice.TouchScreen
                                            onLongPressed: tipUnderlineOffset.held = true
                                            onPressedChanged: if (!pressed) tipUnderlineOffset.held = false
                                        }
                                        ThemedToolTip { id: tipUnderlineOffset; property bool held: false; text: qsTr("Gap between the baseline and the rule"); visible: tipHoverUnderlineOffset.hovered || held }
                                        color: Theme.mutedForeground
                                        font.pixelSize: Theme.fontSizeXs
                                        font.family: Theme.fontFamily
                                    }
                                    ThemedNumberField {
                                        id: underlineOffsetField
                                        to: 200
                                        unit: "px"
                                        width: parent.width
                                        decimals: 1
                                        step: 1
                                        from: -200
                                        onEdited: v => root.setTextStyleKey("underlineOffset", v)
                                    }
                                }
                            }

                            Column {
                                width: parent.width
                                spacing: 4
                                Text {
                                    text: qsTr("Underline colour")
                                    color: Theme.mutedForeground
                                    font.pixelSize: Theme.fontSizeXs
                                    font.family: Theme.fontFamily
                                }
                                ColorSwatchField {
                                    hex: root.textStyle.underlineColor
                                    tooltip: qsTr("Choose underline colour")
                                    onEdited: value => root.setTextStyleKey("underlineColor", value)
                                }
                            }
                        }
                    }
                }

                CollapsibleSection {
                    width: parent.width
                    title: qsTr("Word accent")
                    tooltip: qsTr("Style some words differently from the rest, chosen by rule")
                    expanded: false
                    visible: root.hasTextStyle

                    Row {
                        width: parent.width
                        spacing: 8

                        ThemedComboBox {
                            id: accentRuleBox
                            readonly property bool counted: root.textStyle.accent.rule === "everyNth"
                                                            || root.textStyle.accent.rule === "everyOther"
                            width: !counted ? parent.width
                                   : root.textStyle.accent.rule === "everyNth"
                                     ? (parent.width - 2 * parent.spacing) * 0.5 : (parent.width - parent.spacing) * 0.66
                            model: root.accentRuleLabels
                            currentIndex: Math.max(0, root.accentRules.indexOf(root.textStyle.accent.rule))
                            onActivated: root.setTextGroupKey("accent", "rule",
                                                              root.accentRules[currentIndex])
                        }

                        ThemedNumberField {
                            id: accentEveryNField
                            visible: root.textStyle.accent.rule === "everyNth"
                            width: (parent.width - 2 * parent.spacing) * 0.25
                            to: 16
                            from: 1
                            decimals: 0
                            step: 1
                            onEdited: v => root.setTextGroupKey("accent", "n", v)
                        }

                        // Which word the pattern starts on: 0 is the first word.
                        ThemedNumberField {
                            id: accentPhaseField
                            visible: accentRuleBox.counted
                            width: root.textStyle.accent.rule === "everyNth"
                                   ? (parent.width - 2 * parent.spacing) * 0.25 : (parent.width - parent.spacing) * 0.34
                            from: 0
                            to: 16
                            decimals: 0
                            step: 1
                            ThemedToolTip { text: qsTr("Start at word"); visible: accentPhaseHover.hovered }
                            HoverHandler { id: accentPhaseHover }
                            Binding on value {
                                when: !accentPhaseField.activeFocus
                                value: Number(root.textStyle.accent.phase) || 0
                            }
                            onEdited: v => root.setTextGroupKey("accent", "phase", Math.round(v))
                        }
                    }

                    Column {
                        width: parent.width
                        spacing: Theme.spacingMd
                        visible: root.textStyle.accent.rule !== "none"

                        CollapsibleSection {
                            width: parent.width
                            title: qsTr("Accent colour")
                            tooltip: qsTr("Recolour the words the rule picks out")
                            collapsible: false
                            showSeparator: false
                            showSwitch: true
                            switchChecked: root.textStyle.accent.colorEnabled
                            switchTooltip: qsTr("Recolour the words the rule picks out")
                            onSwitchToggled: on => root.setTextGroupKey("accent", "colorEnabled", on)

                            ColorSwatchField {
                                hex: root.textStyle.accent.color
                                tooltip: qsTr("Choose accent colour")
                                onEdited: value => root.setTextGroupKey("accent", "color", value)
                            }
                        }

                        Column {
                            width: (parent.width - 8) / 2
                            spacing: 4
                            Text {
                                text: qsTr("Accent size")
                                HoverHandler { id: tipHoverAccentSize }
                                TapHandler {
                                    id: tipTapAccentSize
                                    acceptedDevices: PointerDevice.TouchScreen
                                    onLongPressed: tipAccentSize.held = true
                                    onPressedChanged: if (!pressed) tipAccentSize.held = false
                                }
                                ThemedToolTip {
                                    id: tipAccentSize
                                    property bool held: false
                                    text: qsTr("Size of the accented words relative to the rest of the line")
                                    visible: tipHoverAccentSize.hovered || held
                                }
                                color: Theme.mutedForeground
                                font.pixelSize: Theme.fontSizeXs
                                font.family: Theme.fontFamily
                            }
                            ThemedNumberField {
                                id: accentSizeScaleField
                                to: 4
                                unit: "x"
                                width: parent.width
                                decimals: 2
                                step: 0.05
                                from: 0.2
                                onEdited: v => root.setTextGroupKey("accent", "sizeScale", v)
                            }
                        }

                        CollapsibleSection {
                            width: parent.width
                            title: qsTr("Accent outline")
                            tooltip: qsTr("Give the accented words their own outline")
                            collapsible: false
                            showSeparator: false
                            showSwitch: true
                            switchChecked: root.textStyle.accent.outlineEnabled
                            switchTooltip: qsTr("Give the accented words their own outline")
                            onSwitchToggled: on => root.setTextGroupKey("accent", "outlineEnabled", on)

                            ColorSwatchField {
                                hex: root.textStyle.accent.outlineColor
                                tooltip: qsTr("Choose accent outline colour")
                                onEdited: value => root.setTextGroupKey("accent", "outlineColor", value)
                            }

                            Column {
                                width: (parent.width - 8) / 2
                                spacing: 4
                                Text {
                                    text: qsTr("Width")
                                    color: Theme.mutedForeground
                                    font.pixelSize: Theme.fontSizeXs
                                    font.family: Theme.fontFamily
                                }
                                ThemedNumberField {
                                    id: accentOutlineWidthField
                                    to: 100
                                    unit: "px"
                                    width: parent.width
                                    decimals: 1
                                    step: 0.5
                                    from: 0
                                    onEdited: v => root.setTextGroupKey("accent", "outlineWidth", v)
                                }
                            }
                        }

                        CollapsibleSection {
                            width: parent.width
                            title: qsTr("Accent pill")
                            tooltip: qsTr("Highlight only the accented words, instead of every word")
                            collapsible: false
                            showSeparator: false
                            showSwitch: true
                            switchChecked: root.textStyle.accent.highlight.enabled
                            switchTooltip: qsTr("Highlight only the accented words, instead of every word")
                            onSwitchToggled: on => root.setTextAccentHighlightKey("enabled", on)

                            Column {
                                width: parent.width
                                spacing: Theme.spacingSm
                                ColorSwatchField {
                                    hex: root.textStyle.accent.highlight.color
                                    tooltip: qsTr("Choose accent highlight colour")
                                    onEdited: value => root.setTextAccentHighlightKey("color", value)
                                }
                                Row {
                                    width: parent.width
                                    spacing: 8
                                    Column {
                                        width: (parent.width - parent.spacing) / 2
                                        spacing: 4
                                        Text {
                                            text: qsTr("Padding")
                                            color: Theme.mutedForeground
                                            font.pixelSize: Theme.fontSizeXs
                                            font.family: Theme.fontFamily
                                        }
                                        ThemedNumberField {
                                            id: accentPillPaddingField
                                            width: parent.width
                                            from: 0
                                            to: 200
                                            unit: "px"
                                            decimals: 1
                                            step: 1
                                            Binding on value {
                                                when: !accentPillPaddingField.activeFocus
                                                value: Number(root.textStyle.accent.highlight.padding) || 0
                                            }
                                            onEdited: v => root.setTextAccentHighlightKey("padding", v)
                                        }
                                    }
                                    Column {
                                        width: (parent.width - parent.spacing) / 2
                                        spacing: 4
                                        Text {
                                            text: qsTr("Corner radius")
                                            color: Theme.mutedForeground
                                            font.pixelSize: Theme.fontSizeXs
                                            font.family: Theme.fontFamily
                                        }
                                        ThemedNumberField {
                                            id: accentPillRadiusField
                                            width: parent.width
                                            from: 0
                                            to: 200
                                            unit: "px"
                                            decimals: 1
                                            step: 1
                                            Binding on value {
                                                when: !accentPillRadiusField.activeFocus
                                                value: Number(root.textStyle.accent.highlight.radius) || 0
                                            }
                                            onEdited: v => root.setTextAccentHighlightKey("radius", v)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // --- Burbuja ---------------------------------------------------------------------------
        Column {
            width: parent.width
            spacing: Theme.spacingMd
            visible: root.page === "bubble" && root.hasTextStyle

            Text {
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("A shape behind the text: speech balloons, labels, brush strokes… Fine-tune its colour and size under Básico → Background.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            Flow {
                width: parent.width
                spacing: Theme.spacingSm

                ThemedChip {
                    text: qsTr("All")
                    variant: "secondary"
                    selected: root.bubbleCategory.length === 0
                    onClicked: root.bubbleCategory = ""
                }
                ThemedChip {
                    text: qsTr("Favorites")
                    variant: "secondary"
                    selected: root.bubbleCategory === "favorites"
                    onClicked: root.bubbleCategory = "favorites"
                }
                Repeater {
                    model: root.bubbleCategories
                    delegate: ThemedChip {
                        required property var modelData
                        required property int index
                        text: modelData.label
                        variant: "secondary"
                        accentColor: Theme.categoryColor(index)
                        selected: root.bubbleCategory === modelData.id
                        onClicked: root.bubbleCategory = modelData.id
                    }
                }
            }

            Grid {
                id: bubbleGrid
                width: parent.width
                readonly property real gap: Theme.spacingSm
                columns: Math.max(3, Math.floor((width + gap) / (76 + gap)))
                columnSpacing: gap
                rowSpacing: gap
                readonly property real tileWidth: Math.floor((width - gap * (columns - 1)) / columns)

                Repeater {
                    model: root.bubbles.filter(b => b.id === "none"
                                                    || root.bubbleCategory.length === 0
                                                    || (root.bubbleCategory === "favorites"
                                                        ? root.isFavorite("textBubbles", b.id)
                                                        : b.category === root.bubbleCategory))
                    delegate: GalleryTile {
                        required property var modelData
                        tileWidth: bubbleGrid.tileWidth
                        none: modelData.id === "none"
                        label: modelData.label
                        source: none ? "" : root.bubblePreview(modelData.id)
                        selected: none ? root.textStyle.boxEnabled !== true
                                       : (root.textStyle.boxEnabled === true && root.lastBubbleId === modelData.id)
                        favoriteTab: none ? "" : "textBubbles"
                        favoriteId: modelData.id
                        onClicked: root.applyBubble(modelData.id)
                    }
                }
            }
        }

        // --- Efectos ---------------------------------------------------------------------------
        Column {
            width: parent.width
            spacing: Theme.spacingMd
            visible: root.page === "effects" && root.hasTextStyle

            ThemedTextField {
                id: effectSearch
                width: parent.width
                placeholderText: qsTr("Search text effects and styles")
            }

            Flow {
                width: parent.width
                spacing: Theme.spacingSm
                visible: effectSearch.text.trim().length === 0

                Repeater {
                    model: root.effectCategories
                    delegate: ThemedChip {
                        required property var modelData
                        required property int index
                        text: modelData.label
                        variant: "secondary"
                        accentColor: Theme.categoryColor(index)
                        selected: root.effectsCategory === modelData.id
                        onClicked: root.effectsCategory = modelData.id
                    }
                }
            }

            Text {
                width: parent.width
                wrapMode: Text.WordWrap
                visible: root.effectsCategory === "templates" && effectSearch.text.trim().length === 0
                text: qsTr("Templates change the font too. The other styles keep yours.")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            Grid {
                id: effectGrid
                width: parent.width
                readonly property real gap: Theme.spacingSm
                columns: Math.max(3, Math.floor((width + gap) / (76 + gap)))
                columnSpacing: gap
                rowSpacing: gap
                readonly property real tileWidth: Math.floor((width - gap * (columns - 1)) / columns)

                Repeater {
                    model: root.effectTiles(effectSearch.text)
                    delegate: GalleryTile {
                        required property var modelData
                        tileWidth: effectGrid.tileWidth
                        none: modelData.kind === "none"
                        label: modelData.label
                        source: modelData.source || ""
                        selected: modelData.kind === "look" ? root.textStyle.lookId === modelData.id
                                : modelData.kind === "template" ? root.textStyle.packId === modelData.id
                                : root.lastQuickId === modelData.id
                        favoriteTab: "textEffects"
                        favoriteId: modelData.kind + ":" + modelData.id
                        onClicked: root.applyEffectTile(modelData)
                    }
                }
            }

            // Look parameters (Neon's colour, Glitch's offset…) for the look just applied.
            TextParamSlots {
                width: parent.width
                visible: !!root.selectedLook && (root.selectedLook.params || []).length > 0
                specs: root.selectedLook ? (root.selectedLook.params || []) : []
                values: root.textStyle.lookParams || ({})
                onChanged: (id, value) => EditorState.setTextLookParam(
                               EditorState.selectedTrack, EditorState.selectedClip, id, value)
                onPreviewChanged: (id, value) => EditorState.previewSetTextLookParam(
                                      EditorState.selectedTrack, EditorState.selectedClip, id, value)
                onDragStarted: EditorState.beginPreviewDrag(qsTr("Adjust text look"))
                onDragEnded: EditorState.commitPreviewDrag()
            }

            ThemedButton {
                width: parent.width
                variant: "secondary"
                glyph: Theme.icons.save
                text: qsTr("Save style…")
                tooltip: qsTr("Save this text's style as a reusable preset")
                onClicked: saveStyleDialog.openWith(qsTr("Save text style"),
                                                    qsTr("My style %1")
                                                        .arg(EditorState.userTextPresets().length + 1))
            }
        }

        Column {
            width: parent.width
            spacing: Theme.spacingMd
            visible: root.page === "animate" && root.hasTextStyle

            AnimSlotTabs {
                width: parent.width
                model: [
                    { "id": "in", "label": qsTr("In") },
                    { "id": "out", "label": qsTr("Out") },
                    { "id": "loop", "label": qsTr("Loop") }
                ]
                current: root.animSlot
                marked: id => {
                    const slot = root.animation[id]
                    return !!slot && !!slot.preset && slot.preset.length > 0
                }
                onActivated: id => {
                    root.animSlot = id
                    root.animCategory = ""
                    animChips.reset()
                }
            }

            Text {
                visible: root.clipKind === "subtitle"
                width: parent.width
                text: qsTr("Plays for every caption")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }

            // 349 animations: find one by name (0.22.1). A search spans every category of the tab.
            ThemedTextField {
                id: animSearch
                width: parent.width
                placeholderText: qsTr("Search animations")
            }

            ChipScroller {
                id: animChips
                width: parent.width
                visible: root.animCategories.length > 1 && root.animQuery.length === 0

                ThemedChip {
                    anchors.verticalCenter: parent.verticalCenter
                    text: qsTr("All")
                    variant: "secondary"
                    selected: root.animCategory.length === 0
                    onClicked: root.animCategory = ""
                }

                ThemedChip {
                    anchors.verticalCenter: parent.verticalCenter
                    text: qsTr("Favorites")
                    variant: "secondary"
                    selected: root.animCategory === "__favorites__"
                    onClicked: root.animCategory = "__favorites__"
                }

                // Trending always: Stock's text animations are there too.
                ThemedChip {
                    anchors.verticalCenter: parent.verticalCenter
                    visible: Market.configured && !root.animCategories.some(c => c.id === "trending")
                    text: qsTr("Trending")
                    variant: "secondary"
                    selected: root.animCategory === "trending"
                    onClicked: root.animCategory = "trending"
                }

                Repeater {
                    model: root.animCategories
                    delegate: ThemedChip {
                        required property var modelData
                        required property int index
                        anchors.verticalCenter: parent.verticalCenter
                        text: modelData.label
                        variant: "secondary"
                        accentColor: Theme.categoryColor(index)
                        selected: root.animCategory === modelData.id
                        onClicked: root.animCategory = modelData.id
                    }
                }
            }

            Loader {
                id: animSignInLoader
                active: false
                sourceComponent: Component { SignInRequiredDialog { reason: "trends" } }
            }

            Grid {
                id: presetGrid
                width: parent.width
                readonly property real gap: Theme.spacingLg
                columns: Theme.touchUi
                         ? Math.max(2, Math.min(3, Math.floor((width + gap) / (104 + gap))))
                         : Math.max(2, Math.floor((width + gap) / (104 + gap)))
                columnSpacing: gap
                rowSpacing: gap
                readonly property real tileWidth: Math.floor((width - gap * (columns - 1)) / columns)
                Repeater {
                    model: root.animTileModel
                    delegate: TextAnimPresetTile {
                        required property var modelData
                        required property int index
                        slot: root.animSlot
                        presetId: modelData.id
                        label: modelData.label
                        trending: root.wearsFlame(modelData.id)
                        tileWidth: presetGrid.tileWidth
                        selected: modelData.id.length === 0
                                  ? (!root.slotHasPreset && !root.slotData.custom)
                                  : root.slotData.preset === modelData.id
                        playing: root.page === "animate" && root.visible && !EditorState.playing
                                 && modelData.id.length > 0
                                 && (Theme.touchUi ? selected : hovered)
                        onClicked: root.pickPreset(modelData.id)

                        AssetFavoriteButton {
                            visible: modelData.id.length > 0
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.margins: 2
                            tabId: "textAnimations"
                            itemId: modelData.id
                        }

                        // The user's own animations (saved here, imported or from Stock) can be
                        // renamed, shared and removed.
                        IconButton {
                            visible: modelData.id.startsWith("user:")
                            anchors.left: parent.left
                            anchors.top: parent.top
                            anchors.margins: 2
                            glyph: Theme.icons.ellipsis
                            variant: "ghost"
                            buttonSize: 20
                            iconSize: 12
                            tooltip: qsTr("Animation options")
                            onClicked: animMenu.popup()
                        }
                        ThemedContextMenu {
                            id: animMenu
                            ThemedMenuItem {
                                text: qsTr("Rename…")
                                icon.name: Theme.icons.pencil
                                onTriggered: animRenameDialog.openFor(modelData)
                            }
                            ThemedMenuItem {
                                text: qsTr("Export…")
                                icon.name: Theme.icons.folderOutput
                                onTriggered: {
                                    const url = FileDialogs.saveFile(qsTr("Export text animation"),
                                                                     [qsTr("Text animations (*.json)")],
                                                                     modelData.label, "json")
                                    if (url.toString().length > 0)
                                        EditorState.exportUserTextAnimationPreset(modelData.id, url)
                                }
                            }
                            ThemedMenuSeparator { }
                            ThemedMenuItem {
                                text: qsTr("Delete")
                                icon.name: Theme.icons.trash
                                onTriggered: animDeleteDialog.openFor(modelData)
                            }
                        }
                    }
                }
            }

            Text {
                visible: root.animStockShown && Market.configured
                width: parent.width
                text: root.animCategory === "__favorites__" ? qsTr("Stock favorites") : qsTr("From Stock")
                color: Theme.panelForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                font.weight: Font.Medium
            }

            StockPanelCards {
                visible: root.animStockShown && Market.configured
                width: parent.width
                type: "text-animation"
                items: root.animCategory === "__favorites__" ? root.animStockFavorites : null
                bare: root.animCategory === "__favorites__"
                glyph: Theme.icons.type
                isInstalled: function(item) { return !!root.stockAnimPreset(item) }
                apply: function(item) { root.applyStockAnim(item) }
            }

            // Selected preset's controls.
            Column {
                width: parent.width
                spacing: Theme.spacingMd
                visible: root.slotHasPreset && !!root.selectedPreset
                enabled: !root.slotData.custom

                Row {
                    width: parent.width
                    spacing: Theme.spacingSm

                    Text {
                        width: parent.width - previewButton.width - saveAnimButton.width - 2 * parent.spacing
                        anchors.verticalCenter: parent.verticalCenter
                        text: root.selectedPreset ? root.selectedPreset.label : ""
                        elide: Text.ElideRight
                        color: Theme.panelForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSm
                        font.weight: Font.DemiBold
                    }
                    // Keeps this slot's settings as one of My animations, to reuse on other texts.
                    IconButton {
                        id: saveAnimButton
                        glyph: Theme.icons.save
                        variant: "ghost"
                        buttonSize: Theme.controlHeightSm
                        iconSize: 14
                        tooltip: qsTr("Save as my animation…")
                        onClicked: saveAnimDialog.openWith(qsTr("Save text animation"),
                                                           root.selectedPreset ? root.selectedPreset.label : "")
                    }
                    IconButton {
                        id: previewButton
                        glyph: EditorState.playing && previewStopTimer.running ? Theme.icons.pause : Theme.icons.play
                        variant: "ghost"
                        buttonSize: Theme.controlHeightSm
                        iconSize: 14
                        tooltip: qsTr("Preview this animation")
                        onClicked: {
                            if (EditorState.playing && previewStopTimer.running) {
                                previewStopTimer.stop()
                                EditorState.playing = false
                            } else {
                                root.previewAnimation()
                            }
                        }
                    }
                }

                Column {
                    width: parent.width
                    spacing: 4
                    visible: root.animSlot === "loop" ? root.slotControlShown("period") : !root.presetFlags.durationLocked

                    Row {
                        width: parent.width
                        spacing: 6
                        Text {
                            text: root.animSlot === "loop" ? qsTr("Period") : qsTr("Duration")
                            color: Theme.mutedForeground
                            font.pixelSize: Theme.fontSizeXs
                            font.family: Theme.fontFamily
                        }
                        Text {
                            text: Number(durationSlider.value).toFixed(2) + " s"
                            color: Theme.mutedForeground
                            font.pixelSize: Theme.fontSizeXs
                            font.family: Theme.monoFontFamily
                        }
                    }
                    ThemedSlider {
                        id: durationSlider
                        lockWhilePlaying: true
                        width: parent.width
                        label: root.animSlot === "loop" ? qsTr("Period") : qsTr("Duration")
                        from: root.animSlot === "loop" ? 0.1 : 0
                        to: root.animSlot === "loop" ? 10 : 5
                        stepSize: 0.01
                        valueFormatter: function (v) { return Number(v).toFixed(2) + " s" }
                        Binding on value {
                            when: !durationSlider.pressed
                            value: root.animSlot === "loop"
                                   ? (Number(root.slotData.period) || 1)
                                   : (Number(root.slotData.duration) || 0)
                        }
                        onMoved: {
                            const patch = {}
                            patch[root.animSlot === "loop" ? "period" : "duration"] = value
                            if (pressed)
                                root.previewSlot(patch)
                            else
                                root.setSlot(patch)
                        }
                        onPressedChanged: {
                            if (pressed)
                                EditorState.beginPreviewDrag(qsTr("Edit text animation"))
                            else
                                EditorState.commitPreviewDrag()
                        }
                    }
                }

                Row {
                    width: parent.width
                    spacing: 8
                    visible: (!root.presetFlags.unitLocked && root.slotControlShown("unit")) || root.slotControlShown("stagger")

                    Column {
                        width: (parent.width - parent.spacing) / 2
                        spacing: 4
                        visible: !root.presetFlags.unitLocked && root.slotControlShown("unit")
                        Text {
                            text: qsTr("By")
                            color: Theme.mutedForeground
                            font.pixelSize: Theme.fontSizeXs
                            font.family: Theme.fontFamily
                        }
                        ThemedComboBox {
                            width: parent.width
                            model: root.animUnitLabels
                            currentIndex: Math.max(0, root.animUnits.indexOf(root.slotData.unit || "block"))
                            onActivated: root.setSlot({ "unit": root.animUnits[currentIndex] })
                        }
                    }

                    Column {
                        width: (parent.width - parent.spacing) / 2
                        spacing: 4
                        visible: root.slotControlShown("stagger")
                        Text {
                            text: root.animSlot === "loop" ? qsTr("Phase") : qsTr("Stagger")
                            HoverHandler { id: staggerHover }
                            TapHandler {
                                id: staggerTap
                                acceptedDevices: PointerDevice.TouchScreen
                                onLongPressed: staggerTip.held = true
                                onPressedChanged: if (!pressed) staggerTip.held = false
                            }
                            ThemedToolTip {
                                id: staggerTip
                                property bool held: false
                                text: root.animSlot === "loop"
                                      ? qsTr("Delay between one unit and the next along the cycle")
                                      : qsTr("Delay between one unit starting and the next")
                                visible: staggerHover.hovered || held
                            }
                            color: Theme.mutedForeground
                            font.pixelSize: Theme.fontSizeXs
                            font.family: Theme.fontFamily
                        }
                        ThemedNumberField {
                            id: staggerField
                            width: parent.width
                            decimals: 0
                            step: 10
                            from: 0
                            to: 2000
                            unit: "ms"
                            enabled: (root.slotData.unit || "block") !== "block"
                            Binding on value {
                                when: !staggerField.activeFocus
                                value: Math.round((Number(root.slotData.stagger) || 0) * 1000)
                            }
                            onEdited: v => root.setSlot({ "stagger": v / 1000 })
                        }
                    }
                }

                Column {
                    width: (parent.width - 8) / 2
                    spacing: 4
                    visible: !root.presetFlags.orderLocked && root.slotControlShown("order")
                    Text {
                        text: qsTr("Order")
                        color: Theme.mutedForeground
                        font.pixelSize: Theme.fontSizeXs
                        font.family: Theme.fontFamily
                    }
                    ThemedComboBox {
                        width: parent.width
                        model: root.animOrderLabels
                        enabled: (root.slotData.unit || "block") !== "block"
                        currentIndex: Math.max(0, root.animOrders.indexOf(root.slotData.order || "forward"))
                        onActivated: root.setSlot({ "order": root.animOrders[currentIndex] })
                    }
                }

                Column {
                    width: parent.width
                    spacing: 4
                    visible: !root.presetFlags.easeLocked && root.slotControlShown("ease")
                    Text {
                        text: qsTr("Ease")
                        color: Theme.mutedForeground
                        font.pixelSize: Theme.fontSizeXs
                        font.family: Theme.fontFamily
                    }
                    Flow {
                        width: parent.width
                        spacing: Theme.spacingSm
                        Repeater {
                            model: root.easeChips
                            delegate: ThemedChip {
                                required property var modelData
                                text: modelData.label
                                selected: (root.slotData.ease || "") === modelData.id
                                onClicked: root.setSlot({ "ease": modelData.id })
                            }
                        }
                    }
                }

                TextParamSlots {
                    width: parent.width
                    visible: root.presetOwnParams.length > 0
                    specs: root.presetOwnParams
                    values: root.slotData.params || ({})
                    onChanged: (id, value) => root.setSlot(root.slotParamPatch(id, value))
                    onPreviewChanged: (id, value) => root.previewSlot(root.slotParamPatch(id, value))
                    onDragStarted: EditorState.beginPreviewDrag(qsTr("Edit text animation"))
                    onDragEnded: EditorState.commitPreviewDrag()
                }
            }

            // Customize: the slot's animation part by part (TextAnimatorEditor), starting from the
            // chosen preset, the slot's own animators, or a fade by letter.
            ThemedButton {
                width: parent.width
                visible: !root.animEditorOpen
                variant: "secondary"
                glyph: Theme.icons.sliders
                text: qsTr("Customize animation")
                tooltip: qsTr("Choose what moves, by letter, word or line, and how")
                onClicked: root.animEditorOpen = true
            }

            Loader {
                width: parent.width
                active: root.animEditorOpen && root.page === "animate" && root.hasTextStyle
                visible: active
                sourceComponent: Component {
                    TextAnimatorEditor {
                        width: parent ? parent.width : 0
                        slot: root.animSlot
                        trackIndex: EditorState.selectedTrack
                        clipIndex: EditorState.selectedClip
                        slotData: root.slotData
                        onCloseRequested: root.animEditorOpen = false
                        onPreviewRequested: root.previewAnimation()
                        onSaveRequested: saveAnimDialog.openWith(qsTr("Save text animation"),
                                                                 root.selectedPreset ? root.selectedPreset.label : "")
                    }
                }
            }

            CollapsibleSection {
                width: parent.width
                title: qsTr("Advanced")
                expanded: false
                visible: root.animation.custom === true

                Text {
                    width: parent.width
                    wrapMode: Text.WordWrap
                    text: qsTr("Custom animation: change it with Customize animation, or go back to picking presets.")
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                }
                ThemedButton {
                    variant: "secondary"
                    glyph: Theme.icons.reset
                    text: qsTr("Revert to preset")
                    tooltip: qsTr("Drop the custom animators and go back to picking presets")
                    onClicked: root.revertCustomAnimation()
                }
            }
        }
    }

    NameDialog {
        id: saveStyleDialog
        onSubmitted: name => EditorState.saveTextStyleAsPreset(EditorState.selectedTrack,
                                                               EditorState.selectedClip, name)
    }

    NameDialog {
        id: saveAnimDialog
        onSubmitted: name => {
            const id = EditorState.saveTextAnimationAsPreset(EditorState.selectedTrack, EditorState.selectedClip,
                                                             root.animSlot, name)
            if (id.length > 0) {
                root.animCategory = "mine"
                root.pickPreset(id)
            }
        }
    }

    NameDialog {
        id: animRenameDialog
        property string presetId: ""
        function openFor(preset) {
            presetId = preset.id
            openWith(qsTr("Rename text animation"), preset.label)
        }
        onSubmitted: name => EditorState.renameUserTextAnimationPreset(animRenameDialog.presetId, name)
    }

    ThemedDialog {
        id: animDeleteDialog
        property string presetId: ""
        property string presetLabel: ""
        title: qsTr("Delete text animation")
        acceptText: qsTr("Delete")
        acceptVariant: "destructive"
        preferredWidth: Theme.dialogWidthSm
        acceptOnReturn: false
        function openFor(preset) {
            presetId = preset.id
            presetLabel = preset.label
            open()
        }
        onAccepted: EditorState.deleteUserTextAnimationPreset(animDeleteDialog.presetId)

        contentItem: Text {
            width: parent ? parent.width : 320
            wrapMode: Text.WordWrap
            text: qsTr("Delete “%1”? Texts that use it keep their motion.").arg(animDeleteDialog.presetLabel)
            color: Theme.panelForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSm
        }
    }

    VoiceoverDialog {
        id: voiceoverDialog
    }

    // «Guardar como personalizado» in the Texto avanzado window.
    function saveAsMyStyle() {
        saveStyleDialog.openWith(qsTr("Save text style"),
                                 qsTr("My style %1").arg(EditorState.userTextPresets().length + 1))
    }

    // By URL, not by type: the window holds a TextInspector of its own (inAdvanced), and naming
    // the type here would make the two files depend on each other.
    Loader {
        id: advancedTextLoader
        active: false
        source: root.inAdvanced ? "" : Qt.resolvedUrl("../TextAdvancedDialog.qml")
    }
}
