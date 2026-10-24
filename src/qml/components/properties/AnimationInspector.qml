import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift
import ".."

// Filmora / CapCut-style Animation: In, Out and Combo galleries of presets
// (presets/clip-animations), plus Fade, which owns the clip's edge fade. A combo is one motion
// that brings the clip in and takes it out; it replaces the In and Out motion.
Item {
    id: root

    property int clipDataRevision: 0
    readonly property var clipData: {
        void clipDataRevision
        return EditorState.selectedClipData
    }
    readonly property bool hasSelection: !!clipData && Object.keys(clipData).length > 0
    readonly property string clipKind: hasSelection ? (clipData.kind || "") : ""
    readonly property bool supportsBodyAnim: clipKind === "video" || clipKind === "image"
                                             || clipKind === "shape" || clipKind === "text"
    readonly property bool supportsFade: supportsBodyAnim || clipKind === "audio"

    readonly property var styleIds: ["linear", "smooth", "equalPower", "custom", "bezier"]
    readonly property var styleLabels: [qsTr("Linear"), qsTr("Smooth"), qsTr("Natural"), qsTr("Custom"), qsTr("Bezier")]

    readonly property var animIn: {
        void clipDataRevision
        return (clipData && clipData.animIn)
               ? clipData.animIn
               : { kind: "none", duration: 0.5, curve: "smooth" }
    }
    readonly property var animOut: {
        void clipDataRevision
        return (clipData && clipData.animOut)
               ? clipData.animOut
               : { kind: "none", duration: 0.5, curve: "smooth" }
    }
    readonly property var animCombo: {
        void clipDataRevision
        return (clipData && clipData.animCombo)
               ? clipData.animCombo
               : { kind: "none", duration: 0, curve: "smooth" }
    }

    // ----- Gallery -----------------------------------------------------------------------
    property string animTab: "in"
    property string animCategory: ""
    // Trending ones show for everyone but apply only signed in (Jorge, 2026-10-23): picking one
    // signed out asks for the account and applies it once signed in.
    readonly property bool trendsNeedAccount: Account.available && !Account.signedIn
    readonly property string slotKey: animTab === "in" ? "animIn" : animTab === "out" ? "animOut" : "animCombo"
    readonly property var currentAnim: animTab === "in" ? animIn : animTab === "out" ? animOut : animCombo
    readonly property bool currentSlotActive: !!currentAnim && (currentAnim.kind || "none") !== "none"
    readonly property var animPresets: EditorState.clipAnimationPresets(animTab)
    readonly property var animCategories: EditorState.clipAnimationCategories(animTab)
    // The kinds that came before the presets, matched to the preset that replaced each.
    readonly property var legacyPreset: ({
        "slideUp": "slide-up", "slideDown": "slide-down", "slideLeft": "slide-left", "slideRight": "slide-right",
        "zoomIn": "zoom-in", "zoomOut": "zoom-out", "pop": "pop", "spinCW": "spin-cw", "spinCCW": "spin-ccw",
        "bounce": "bounce"
    })
    // Starred ones behind the Favorites chip ("clipAnimations", the web's ClipAnimGallery group).
    property int favoritesTick: 0
    Connections {
        target: EditorState
        function onAssetFavoritesChanged() { root.favoritesTick++ }
    }
    readonly property var animTileModel: {
        void root.favoritesTick
        const filtered = animCategory.length === 0 ? animPresets
                       : animCategory === "__favorites__" ? animPresets.filter(p => EditorState.isAssetFavorite("clipAnimations", p.id))
                       : animCategory === "trending" ? animPresets.filter(p => p.trending)
                       : animPresets.filter(p => p.category === animCategory)
        const tiles = [{ "label": qsTr("None") }]
        if (animTab !== "combo" && (animCategory.length === 0 || animCategory === "basic") && animCategory !== "__favorites__")
            tiles.push({ "kind": "fade", "label": qsTr("Fade"), "duration": 0.5 })
        for (let i = 0; i < filtered.length; ++i)
            tiles.push({ "preset": filtered[i].id, "label": filtered[i].label, "duration": filtered[i].duration,
                         "trending": !!filtered[i].trending })
        return tiles
    }

    function isTileSelected(tile) {
        const a = root.currentAnim || {}
        const kind = a.kind || "none"
        if (tile.preset)
            return kind === "preset" ? a.preset === tile.preset
                                     : root.animTab + "-" + root.legacyPreset[kind] === tile.preset
        if (tile.kind)
            return kind === tile.kind
        return kind === "none"
    }

    function pickTile(tile) {
        if (tile.trending && root.trendsNeedAccount) {
            const slotKey = root.slotKey
            const track = EditorState.selectedTrack
            const clip = EditorState.selectedClip
            signInLoader.active = true
            signInLoader.item.openFor(() => EditorState.setClipAnimation(track, clip, slotKey, { preset: tile.preset }))
            return
        }
        if (tile.preset) {
            root.setAnim(root.slotKey, { preset: tile.preset })
        } else if (tile.kind) {
            root.setAnim(root.slotKey, { kind: tile.kind, preset: "", duration: root.currentAnim.duration || 0.5 })
        } else {
            root.setAnim(root.slotKey, { kind: "none", preset: "" })
        }
    }

    height: column.height
    implicitHeight: column.height

    function setAnim(which, patch) {
        EditorState.setClipAnimation(EditorState.selectedTrack, EditorState.selectedClip, which, patch)
    }

    function styleIndexFor(anim) {
        const id = (anim && anim.curve) ? anim.curve : (root.clipData.fadeCurve || "smooth")
        return Math.max(0, root.styleIds.indexOf(id))
    }

    function setStyle(which, index) {
        const id = root.styleIds[index]
        if (id === "custom" || id === "bezier") {
            root.setAnim(which, { curve: id })
            root.Window.window.openFadeCurve(EditorState.selectedTrack, EditorState.selectedClip)
            return
        }
        root.setAnim(which, { curve: id })
    }

    function refreshFields() {
        if (root.supportsBodyAnim && animDurationField && !animDurationField.activeFocus)
            animDurationField.value = root.currentAnim.duration || 0
        if (root.clipKind === "audio") {
            if (audioFadeInField && !audioFadeInField.activeFocus)
                audioFadeInField.value = root.clipData.fadeIn || 0
            if (audioFadeOutField && !audioFadeOutField.activeFocus)
                audioFadeOutField.value = root.clipData.fadeOut || 0
        }
    }

    Connections {
        target: EditorState
        function onSelectionChanged() { root.clipDataRevision++; root.refreshFields() }
        function onSelectedClipDataChanged() { root.clipDataRevision++; root.refreshFields() }
        function onTracksChanged() { root.clipDataRevision++; root.refreshFields() }
    }

    Component.onCompleted: refreshFields()
    onAnimTabChanged: refreshFields()

    Column {
        id: column
        width: root.width
        spacing: Theme.spacingXl

        EmptyState {
            visible: !root.supportsFade
            width: parent.width
            compact: true
            glyph: Theme.icons.sparkles
            title: qsTr("Not available")
            hint: qsTr("Animation applies to video, image, shape, text, and audio.")
        }

        // ----- Audio: volume fades only ----------------------------------------------------
        Text {
            visible: root.clipKind === "audio"
            text: qsTr("Fade in / out (volume)")
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }

        Row {
            visible: root.clipKind === "audio"
            width: parent.width
            spacing: 6

            ThemedNumberField {
                id: audioFadeInField
                to: Math.max(0.1, root.clipData.duration || 1)
                unit: "s"
                width: (parent.width - parent.spacing) / 2
                decimals: 2
                step: 0.05
                from: 0
                onEdited: v => EditorState.setClipFade(
                               EditorState.selectedTrack, EditorState.selectedClip,
                               v, root.clipData.fadeOut || 0)
            }
            ThemedNumberField {
                id: audioFadeOutField
                to: Math.max(0.1, root.clipData.duration || 1)
                unit: "s"
                width: (parent.width - parent.spacing) / 2
                decimals: 2
                step: 0.05
                from: 0
                onEdited: v => EditorState.setClipFade(
                               EditorState.selectedTrack, EditorState.selectedClip,
                               root.clipData.fadeIn || 0, v)
            }
        }

        Text {
            visible: root.clipKind === "audio"
            text: qsTr("Style")
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }

        ThemedComboBox {
            visible: root.clipKind === "audio"
            width: parent.width
            model: root.styleLabels
            currentIndex: Math.max(0, root.styleIds.indexOf(root.clipData.fadeCurve || "smooth"))
            onActivated: (index) => {
                const id = root.styleIds[index]
                if (id === "custom" || id === "bezier") {
                    EditorState.setClipFadeCurve(
                                EditorState.selectedTrack, EditorState.selectedClip, id)
                    root.Window.window.openFadeCurve(
                                EditorState.selectedTrack, EditorState.selectedClip)
                    return
                }
                EditorState.setClipFadeCurve(
                            EditorState.selectedTrack, EditorState.selectedClip, id)
            }
        }

        // ----- Visual: Filmora's In / Out / Combo gallery ---------------------------------
        AnimSlotTabs {
            visible: root.supportsBodyAnim
            width: parent.width
            model: [
                { "id": "in", "label": qsTr("In") },
                { "id": "out", "label": qsTr("Out") },
                { "id": "combo", "label": qsTr("Combo") }
            ]
            current: root.animTab
            onActivated: id => {
                root.animTab = id
                root.animCategory = ""
                clipAnimChips.reset()
            }
        }

        ChipScroller {
            id: clipAnimChips
            visible: root.supportsBodyAnim && root.animCategories.length > 0
            width: parent.width

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
            id: signInLoader
            active: false
            sourceComponent: Component { SignInRequiredDialog { reason: "trends" } }
        }

        Grid {
            id: animGrid
            visible: root.supportsBodyAnim
            width: parent.width
            readonly property real gap: Theme.spacingMd
            columns: Math.max(3, Math.floor((width + gap) / (76 + gap)))
            columnSpacing: gap
            rowSpacing: gap
            readonly property real tileWidth: Math.floor((width - gap * (columns - 1)) / columns)

            Repeater {
                model: root.animTileModel
                delegate: ClipAnimPresetTile {
                    required property var modelData
                    slot: root.animTab
                    presetId: modelData.preset || ""
                    kind: modelData.kind || ""
                    label: modelData.label
                    seconds: modelData.duration || 0.6
                    trending: !!modelData.trending
                    tileWidth: animGrid.tileWidth
                    selected: root.isTileSelected(modelData)
                    playing: root.visible && !EditorState.playing && (Theme.touchUi ? selected : hovered)
                    onClicked: root.pickTile(modelData)
                    favoriteTab: "clipAnimations"
                }
            }
        }

        // The picked animation's length and style.
        Row {
            visible: root.supportsBodyAnim && root.currentSlotActive
            width: parent.width
            spacing: 6

            Text {
                width: 72
                anchors.verticalCenter: parent.verticalCenter
                text: qsTr("Duration")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
            ThemedNumberField {
                id: animDurationField
                width: 76
                to: root.animTab === "combo" ? Math.max(0.1, root.clipData.duration || 1) : 10
                unit: "s"
                decimals: 2
                step: 0.05
                from: 0
                onEdited: v => root.setAnim(root.slotKey, { duration: v })
            }
            ThemedComboBox {
                visible: root.animTab !== "combo"
                width: Math.max(60, parent.width - 72 - 76 - parent.spacing * 3)
                model: root.styleLabels
                currentIndex: root.styleIndexFor(root.currentAnim)
                onActivated: (index) => root.setStyle(root.slotKey, index)
            }
        }

        Text {
            visible: root.supportsBodyAnim && root.animTab === "combo" && root.currentSlotActive
            width: parent.width
            wrapMode: Text.WordWrap
            text: qsTr("0 s plays the combo over the whole clip. A combo replaces the In and Out motion.")
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }

        ThemedButton {
            visible: root.supportsBodyAnim
                     && ((root.animIn.curve || "") === "custom"
                         || (root.animOut.curve || "") === "custom"
                         || (root.clipData.fadeCurve || "") === "custom")
            width: parent.width
            text: qsTr("Edit custom curve…")
            variant: "secondary"
            onClicked: root.Window.window.openFadeCurve(
                           EditorState.selectedTrack, EditorState.selectedClip)
        }

        Text {
            visible: root.supportsBodyAnim && root.clipKind === "text"
            width: parent.width
            wrapMode: Text.WordWrap
            text: qsTr("Letter and word animations live in the Text tab, under Animate. This moves the whole clip.")
            color: Theme.mutedForeground
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeXs
        }
    }
}
