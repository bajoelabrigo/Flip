import QtQuick
import QtQuick.Controls.Basic
import Drift

// "My account": the Flip Studio account at a glance (picture, name, email, since when), the
// user's favourites gathered from every panel, and the stock photos and videos downloaded on this
// computer. Opened from the picture in the editor header and on the start screen. Purchases and
// the user's store join it once the store exists.
ThemedDialog {
    id: root

    // Main jumps the assets panel to a tab ("music", "media", …) and closes this.
    signal assetsTabRequested(string tabId)
    signal settingsRequested()

    title: qsTr("My account")
    preferredWidth: 760
    showReject: false
    acceptText: qsTr("Done")

    property string section: "favorites"
    property int revision: 0

    // Favourite groups as the panels store them, with a name and the assets tab they live in.
    readonly property var favoriteGroups: [
        { id: "music", label: qsTr("Music"), tab: "music" },
        { id: "sounds", label: qsTr("Sounds"), tab: "sfx" },
        { id: "effects", label: qsTr("Effects"), tab: "effects" },
        { id: "transitions", label: qsTr("Transitions"), tab: "transitions" },
        { id: "templates", label: qsTr("Templates"), tab: "effectTemplates" },
        { id: "stickers", label: qsTr("Stickers"), tab: "stickers" },
        { id: "shapes", label: qsTr("Shapes"), tab: "shapes" },
        { id: "textStyles", label: qsTr("Text styles"), tab: "text" },
        { id: "textEffects", label: qsTr("Text effects"), tab: "text" },
        { id: "textBubbles", label: qsTr("Text bubbles"), tab: "text" },
        { id: "textAnimations", label: qsTr("Text animations"), tab: "text" },
        { id: "fonts", label: qsTr("Fonts"), tab: "text" },
        { id: "captionStyles", label: qsTr("Caption styles"), tab: "subtitles" },
        { id: "voices", label: qsTr("Voices"), tab: "speech" },
        { id: "retouch", label: qsTr("Retouch"), tab: "" }
    ]

    readonly property var favorites: {
        void root.revision
        const counts = EditorState.assetFavoriteCounts()
        const out = []
        for (const g of root.favoriteGroups) {
            if (counts[g.id])
                out.push(Object.assign({ count: counts[g.id] }, g))
        }
        // Groups this list does not know yet still show, under their stored name.
        for (const id in counts) {
            if (!root.favoriteGroups.some(g => g.id === id))
                out.push({ id: id, label: id, tab: "", count: counts[id] })
        }
        return out
    }

    property string favoriteGroup: ""
    readonly property string shownGroup: favorites.some(g => g.id === favoriteGroup)
                                         ? favoriteGroup
                                         : (favorites.length > 0 ? favorites[0].id : "")

    // The favourites of one group as tiles: { label, source (image), glyph (when there is no
    // image), font (a family to write "Aa" in), strip/frames (a transition's preview strip) }.
    // Each group reads the same catalog its own panel shows, so a tile looks like it does there.
    function favoriteTiles(groupId) {
        void root.revision
        const isFav = id => EditorState.isAssetFavorite(groupId, id)
        const enc = encodeURIComponent
        const sample = "?text=" + enc("Aa")
        const out = []
        const add = (label, extra) => out.push(Object.assign({ label: label, source: "", glyph: "", font: "" }, extra))
        switch (groupId) {
        case "music":
            for (const m of EditorState.soundEffects().filter(e => (e.id || "").startsWith("musica/") && isFav(e.id)))
                add(m.label, { glyph: Theme.icons.music })
            break
        case "sounds":
            for (const e of EditorState.soundEffects().filter(e => !(e.id || "").startsWith("musica/") && isFav(e.id)))
                add(e.label, { glyph: "audio-lines" })
            for (const e of EditorState.audioEffectCatalog().filter(e => !e.id.startsWith("voz.") && isFav(e.id)))
                add(e.label, { source: e.thumbnailPath ? EditorState.imageUrl(e.thumbnailPath) : "",
                               glyph: e.icon || "audio-lines" })
            break
        case "effects":
            for (const e of EditorState.effectCatalog().filter(e => isFav(e.id)))
                add(e.label, { source: e.thumbnailPath ? EditorState.imageUrl(e.thumbnailPath) : "",
                               glyph: Theme.icons.sparkles })
            break
        case "transitions":
            for (const t of EditorState.transitionKinds().filter(t => isFav(t.kind)))
                add(t.label, { strip: t.previewStripPath ? EditorState.imageUrl(t.previewStripPath) : "",
                               frames: Math.max(1, t.previewFrames || 1), glyph: Theme.icons.chevronsRight })
            break
        case "templates":
            for (const t of EditorState.effectTemplateCatalog().filter(t => isFav(t.id))) {
                const thumbs = t.effectThumbnails || []
                const path = t.thumbnailPath || (thumbs.length > 0 ? thumbs[0] : "")
                add(t.label, { source: path ? EditorState.imageUrl(path) : "", glyph: Theme.icons.sparkles })
            }
            break
        case "stickers":
            for (const st of EditorState.builtinStickers().filter(st => isFav(st.id)))
                add(st.label, { source: EditorState.imageUrl(st.thumbnail || st.path), fit: true })
            break
        case "shapes":
            for (const sh of EditorState.builtinShapes().concat(EditorState.userShapes()).filter(sh => isFav(sh.id)))
                add(sh.label, { source: "image://shape/" + sh.id, fit: true })
            break
        case "textStyles":
            for (const t of EditorState.textPresets().concat(EditorState.addonTextPresets()).filter(t => isFav(t.id)))
                add(t.label, { source: "image://textstyle/" + t.id, text: true })
            break
        case "captionStyles":
            for (const t of EditorState.subtitleStyleChoices().filter(t => isFav(t.id)))
                add(t.label, { source: "image://textstyle/" + t.id, text: true })
            break
        case "textEffects": {
            const quick = EditorState.textQuickStyles()
            const looks = EditorState.textLooks()
            const presets = EditorState.textPresets().concat(EditorState.userTextPresets())
            for (const q of quick.filter(q => isFav("quick:" + q.id)))
                add(q.label, { source: "image://textlook/quick:" + q.id + sample, text: true })
            for (const l of looks.filter(l => l.id !== "plain" && isFav("look:" + l.id)))
                add(l.label, { source: "image://textlook/" + l.id + sample, text: true })
            for (const t of presets.filter(t => isFav("template:" + t.id)))
                add(t.label, { source: "image://textstyle/" + t.id, text: true })
            break
        }
        case "textBubbles":
            for (const b of EditorState.textBubbles().filter(b => b.id !== "none" && isFav(b.id)))
                add(b.label, { source: "image://textlook/bubble:" + b.id + "?text=" + enc(qsTr("Hello")), text: true })
            break
        case "textAnimations":
            for (const a of EditorState.textAnimationPresets("").filter(a => isFav(a.id))) {
                const slot = (a.slots && a.slots.length > 0) ? a.slots[0] : "in"
                add(a.label, { source: "image://textanim/" + slot + "/" + a.id + "?w=104&h=58&still=1", text: true })
            }
            break
        case "fonts":
            for (const name of EditorState.assetFavoriteIds("fonts"))
                add(name, { font: name })
            break
        case "voices":
            for (const v of EditorState.audioEffectCatalog().filter(v => v.id.startsWith("voz.") && isFav(v.id)))
                add(v.label, { glyph: Theme.icons.mic })
            break
        case "retouch":
            for (const id of EditorState.assetFavoriteIds("retouch"))
                add(qsTranslate("VideoInspector", root.retouchLabels[id] || id),
                    { source: "qrc:/retouch/" + id + ".jpg" })
            break
        }
        return out
    }

    // Retouch lives in a local list in VideoInspector; its labels are reused (and translated)
    // from there.
    readonly property var retouchLabels: ({
        "auto-natural": QT_TRANSLATE_NOOP("VideoInspector", "Natural"),
        "auto-soft": QT_TRANSLATE_NOOP("VideoInspector", "Soft"),
        "auto-radiant": QT_TRANSLATE_NOOP("VideoInspector", "Radiant"),
        "auto-defined": QT_TRANSLATE_NOOP("VideoInspector", "Defined"),
        "skin-smooth": QT_TRANSLATE_NOOP("VideoInspector", "Smooth"),
        "skin-whiten": QT_TRANSLATE_NOOP("VideoInspector", "Whiten"),
        "skin-tone": QT_TRANSLATE_NOOP("VideoInspector", "Skin tone"),
        "skin-sharpen": QT_TRANSLATE_NOOP("VideoInspector", "Sharpen"),
        "slim-face": QT_TRANSLATE_NOOP("VideoInspector", "Slim face"),
        "big-eyes": QT_TRANSLATE_NOOP("VideoInspector", "Bigger eyes"),
        "face-width": QT_TRANSLATE_NOOP("VideoInspector", "Face width"),
        "wide-mouth": QT_TRANSLATE_NOOP("VideoInspector", "Wide mouth"),
        "whiten-teeth": QT_TRANSLATE_NOOP("VideoInspector", "Whiten teeth"),
        "lipstick": QT_TRANSLATE_NOOP("VideoInspector", "Lipstick"),
        "blush": QT_TRANSLATE_NOOP("VideoInspector", "Blush"),
        "eyeliner": QT_TRANSLATE_NOOP("VideoInspector", "Eyeliner"),
        "eyeshadow": QT_TRANSLATE_NOOP("VideoInspector", "Eyeshadow"),
        "brow-tint": QT_TRANSLATE_NOOP("VideoInspector", "Brow tint"),
        "eye-colour": QT_TRANSLATE_NOOP("VideoInspector", "Eye colour")
    })

    // This computer's downloads: tells whether a file from the account's list is here.
    readonly property var localDownloads: {
        void root.revision
        return Market.configured ? Market.downloadHistory() : []
    }
    // Signed in: the account's own list, kept on the server (it follows to another computer).
    // Signed out: this computer's history, in the same shape.
    readonly property var downloads: {
        if (Account.signedIn && Market.configured)
            return Market.library
        return localDownloads.map(d => ({ id: d.itemId, title: d.title, thumb_url: d.thumb, type: d.mediaKind,
                                          provider: d.provider, last_at: d.at }))
    }
    function localEntry(itemId) {
        for (let i = 0; i < localDownloads.length; ++i) {
            if (localDownloads[i].itemId === itemId)
                return localDownloads[i]
        }
        return null
    }
    function isTemplate(item) { return Market.sceneTemplateIdForItem(item.id || "") !== "" }
    function sourceName(item) {
        if (isTemplate(item))
            return qsTr("Template")
        if (item.provider === "pixabay")
            return "Pixabay"
        return item.provider === "pexels" ? "Pexels" : "Stock"
    }

    // What a row offers, as the web editor's: keep it where it belongs, or put it in the edit now.
    // Null when it is gone from Stock.
    function libraryActions(item) {
        if (!item || !item.id || item.downloadable === false)
            return null
        const applyHint = qsTr("On the selected clip, or on an adjustment layer at the playhead")
        const textHint = qsTr("On the selected text, or on a new text at the playhead")
        const placeHint = qsTr("Puts it on the timeline, at the playhead")
        switch (EditorState.stockLibraryDelivery(item)) {
        case "effect":
            return { save: qsTr("Save in Effects"), saveHint: qsTr("Puts it in Effects › Trending"),
                     place: qsTr("Apply"), placeHint: applyHint }
        case "effect-preset":
            return { save: qsTr("Save in My presets"), saveHint: qsTr("Puts it in My presets (the inspector's Effects)"),
                     place: qsTr("Apply"), placeHint: applyHint }
        case "lut":
            return { save: qsTr("Save in Filters"), saveHint: qsTr("Puts it in Filters and in Adjust › LUT"),
                     place: qsTr("Apply"), placeHint: applyHint }
        case "transition":
            return { save: qsTr("Save in Transitions"), saveHint: qsTr("Puts it in Transitions"),
                     place: qsTr("Apply"), placeHint: qsTr("On the selected clip's cut, or the one nearest the playhead") }
        case "shape":
            return { save: qsTr("Save in Shapes"), saveHint: qsTr("Puts it in Shapes"),
                     place: qsTr("Add to track"), placeHint: placeHint }
        case "text-style":
            return { save: qsTr("Save in Titles"), saveHint: qsTr("Puts it in Titles › Trending"),
                     place: qsTr("Apply"), placeHint: textHint }
        case "text-animation":
            return { save: qsTr("Save in Animation"), saveHint: qsTr("Puts it in Text › Animation"),
                     place: qsTr("Apply"), placeHint: textHint }
        case "scene-template":
            return { save: qsTr("Save in Templates"), saveHint: qsTr("Puts it in Templates, ready to use"),
                     place: qsTr("Add to track"), placeHint: placeHint }
        default:
            // Video, photo, music, sound, sticker, animation, overlay, background: a file for Media.
            return { save: qsTr("Add to Media"), saveHint: qsTr("Keeps it in Media to use whenever you like"),
                     place: qsTr("Add to track"), placeHint: placeHint }
        }
    }

    // "place" puts it in the edit, so the dialog goes and the result shows; "save" leaves the
    // dialog open and says here what happened (the status line is behind it).
    property string note: ""
    function useItem(item, mode) {
        root.note = ""
        root.watchingMessages = mode === "save"
        EditorState.useStockLibraryItem(item, mode)
        if (mode === "place")
            root.close()
    }
    property bool watchingMessages: false

    readonly property int projectCount: EditorState.projectFile.recentProjects.length

    onOpened: {
        root.revision++
        if (Account.signedIn)
            Market.refreshLibrary()
    }

    Connections {
        target: Market
        function onDownloadHistoryChanged() { root.revision++ }
        function onDownloadImported(itemId, name) {
            if (root.watchingMessages)
                root.note = name.length > 0 ? qsTr("“%1” was added to Media.").arg(name) : qsTr("Added to Media.")
        }
        function onDownloadInstalled(itemId, name, where) {
            if (root.watchingMessages)
                root.note = where.length > 0 ? qsTr("“%1” is ready. %2.").arg(name).arg(where) : qsTr("“%1” is installed.").arg(name)
        }
        function onDownloadFailed(itemId, code, message) {
            if (root.watchingMessages)
                root.note = message
        }
    }
    Connections {
        target: EditorState
        function onLastMessageChanged() {
            if (root.watchingMessages && root.visible)
                root.note = EditorState.lastMessage
        }
    }
    Connections {
        target: EditorState
        function onAssetFavoritesChanged() { root.revision++ }
    }

    contentItem: Column {
        spacing: Theme.spacingXl
        width: parent ? parent.width : 700

        // --- Who ---------------------------------------------------------------------------
        Row {
            width: parent.width
            spacing: Theme.spacingXl

            Rectangle {
                id: profileCard
                width: parent.width - planCard.width - parent.spacing
                height: 112
                radius: Theme.radiusMd
                color: Theme.panelSecondaryBg

                Row {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingXl
                    spacing: Theme.spacingXl

                    AccountAvatar {
                        size: 72
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Column {
                        width: parent.width - 72 - parent.spacing
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: Theme.spacingXs

                        ThemedLabel {
                            width: parent.width
                            size: "base"
                            tone: "default"
                            font.weight: Font.DemiBold
                            elide: Text.ElideRight
                            wrapMode: Text.NoWrap
                            text: Account.signedIn
                                  ? (Account.name.length > 0 ? Account.name : Account.email)
                                  : qsTr("Not signed in")
                        }
                        ThemedLabel {
                            width: parent.width
                            elide: Text.ElideRight
                            wrapMode: Text.NoWrap
                            visible: Account.signedIn && Account.name.length > 0
                            text: Account.email
                        }
                        ThemedLabel {
                            width: parent.width
                            text: {
                                const parts = []
                                if (Account.signedIn && !isNaN(Account.memberSince.getTime()))
                                    parts.push(qsTr("In Flip Studio since %1")
                                               .arg(Account.memberSince.toLocaleDateString(Qt.locale(), "MMMM yyyy")))
                                parts.push(qsTr("%n project(s)", "", root.projectCount))
                                return parts.join("  ·  ")
                            }
                        }
                        ThemedButton {
                            visible: !Account.signedIn && Account.available
                            variant: "primary"
                            glyph: Account.busy ? Theme.icons.spinner : Theme.icons.brandGoogle
                            text: Account.busy ? qsTr("Waiting for the browser…") : qsTr("Sign in with Google")
                            enabled: !Account.busy
                            onClicked: Account.signIn()
                        }
                    }
                }
            }

            Rectangle {
                id: planCard
                width: 220
                height: profileCard.height
                radius: Theme.radiusMd
                color: Theme.panelSecondaryBg

                Column {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingXl
                    spacing: Theme.spacingSm

                    ThemedLabel {
                        size: "sm"
                        tone: "default"
                        font.weight: Font.DemiBold
                        text: qsTr("Free plan")
                    }
                    ThemedLabel {
                        width: parent.width
                        text: qsTr("The whole editor, with no watermark.")
                    }
                }
            }
        }

        // --- Sections ----------------------------------------------------------------------
        Row {
            spacing: Theme.spacing2xl

            Repeater {
                model: [
                    { id: "favorites", label: qsTr("Favorites") },
                    { id: "downloads", label: qsTr("Stock downloads") }
                ]
                delegate: Item {
                    required property var modelData
                    readonly property bool active: root.section === modelData.id
                    width: sectionLabel.implicitWidth
                    height: sectionLabel.implicitHeight + Theme.spacingLg + 2
                    Accessible.role: Accessible.PageTab
                    Accessible.name: sectionLabel.text

                    Text {
                        id: sectionLabel
                        text: parent.modelData.label
                        color: parent.active || sectionHover.hovered ? Theme.panelForeground : Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSm
                        font.weight: parent.active ? Font.DemiBold : Font.Medium
                    }
                    Rectangle {
                        anchors.bottom: parent.bottom
                        width: parent.width
                        height: 2
                        radius: 1
                        color: Theme.primary
                        visible: parent.active
                    }
                    HoverHandler { id: sectionHover; cursorShape: Qt.PointingHandCursor }
                    TapHandler { onTapped: root.section = parent.modelData.id }
                }
            }
        }

        // Favourites, as in CapCut: a chip per group, then every favourite with its picture.
        // A tile opens the panel it comes from.
        Column {
            width: parent.width
            spacing: Theme.spacingLg
            visible: root.section === "favorites"

            ThemedLabel {
                width: parent.width
                visible: root.favorites.length === 0
                text: qsTr("No favorites yet. Mark music, effects, text styles and more with the star in each panel and they gather here.")
            }

            Flow {
                width: parent.width
                spacing: Theme.spacingSm
                visible: root.favorites.length > 0

                Repeater {
                    model: root.favorites
                    delegate: Rectangle {
                        required property var modelData
                        readonly property bool active: root.shownGroup === modelData.id
                        width: chipText.implicitWidth + Theme.spacingXl * 2
                        height: 28
                        radius: height / 2
                        color: active ? Qt.rgba(Theme.primary.r, Theme.primary.g, Theme.primary.b, 0.16)
                                      : Theme.panelSecondaryBg
                        border.width: Theme.borderWidth
                        border.color: active ? Theme.primary : "transparent"

                        Text {
                            id: chipText
                            anchors.centerIn: parent
                            text: parent.modelData.label + "  " + parent.modelData.count
                            color: parent.active ? Theme.panelForeground : Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                            font.weight: parent.active ? Font.DemiBold : Font.Normal
                        }
                        HoverHandler { cursorShape: Qt.PointingHandCursor }
                        TapHandler { onTapped: root.favoriteGroup = parent.modelData.id }
                    }
                }
            }

            Flickable {
                id: favFlick
                readonly property var group: root.favorites.find(g => g.id === root.shownGroup) || ({ tab: "" })
                readonly property var tiles: root.favoriteTiles(root.shownGroup)
                width: parent.width
                height: Math.min(favGrid.implicitHeight, 300)
                contentHeight: favGrid.implicitHeight
                clip: true
                visible: root.favorites.length > 0
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: AppScrollBar { }

                Flow {
                    id: favGrid
                    width: parent.width
                    spacing: Theme.spacingLg

                    Repeater {
                        model: favFlick.tiles
                        delegate: Column {
                            id: favTile
                            required property var modelData
                            width: 104
                            spacing: Theme.spacingXs

                            Rectangle {
                                id: tileBox
                                width: 104
                                height: 80
                                radius: Theme.radiusSm
                                color: favTile.modelData.text ? Theme.textStylePreviewBg : Theme.panelSecondaryBg
                                border.width: tileHover.hovered ? 2 : 0
                                border.color: Theme.primary
                                clip: true

                                // Plain picture: thumbnail, sticker, shape, text preview, retouch.
                                Image {
                                    id: tileImage
                                    anchors.fill: parent
                                    anchors.margins: favTile.modelData.fit || favTile.modelData.text ? Theme.spacingSm : 0
                                    visible: favTile.modelData.source.length > 0 && status === Image.Ready
                                    source: favTile.modelData.source
                                    sourceSize: Qt.size(208, 160)
                                    fillMode: favTile.modelData.fit || favTile.modelData.text
                                              ? Image.PreserveAspectFit : Image.PreserveAspectCrop
                                    asynchronous: true
                                }

                                // A transition's preview strip: one square frame of it.
                                Item {
                                    anchors.fill: parent
                                    visible: !!favTile.modelData.strip
                                    clip: true
                                    Image {
                                        readonly property int frame: Math.round(0.45 * ((favTile.modelData.frames || 1) - 1))
                                        height: parent.height
                                        width: parent.height * (favTile.modelData.frames || 1)
                                        x: (parent.width - parent.height) / 2 - frame * parent.height
                                        source: favTile.modelData.strip || ""
                                        asynchronous: true
                                    }
                                }

                                // A font: written in itself.
                                Text {
                                    anchors.centerIn: parent
                                    visible: favTile.modelData.font.length > 0
                                    text: "Aa"
                                    color: Theme.panelForeground
                                    font.family: favTile.modelData.font
                                    font.pixelSize: 30
                                }

                                // No picture (music, sounds, voices) or one that failed to load.
                                IconGlyph {
                                    anchors.centerIn: parent
                                    visible: favTile.modelData.font.length === 0 && !favTile.modelData.strip
                                             && !tileImage.visible
                                    glyph: favTile.modelData.glyph || Theme.icons.star
                                    iconSize: 28
                                    iconColor: Theme.mutedForeground
                                }

                                scale: tileHover.hovered ? 1.02 : 1.0
                                Behavior on scale {
                                    NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                                }
                                HoverHandler { id: tileHover; cursorShape: Qt.PointingHandCursor }
                                TapHandler {
                                    onTapped: if (favFlick.group.tab) root.assetsTabRequested(favFlick.group.tab)
                                }
                            }
                            ThemedLabel {
                                width: parent.width
                                elide: Text.ElideRight
                                wrapMode: Text.NoWrap
                                tone: "default"
                                text: favTile.modelData.label
                            }
                        }
                    }
                }
            }

            ThemedLabel {
                width: parent.width
                visible: root.favorites.length > 0 && favFlick.group.tab.length > 0
                text: qsTr("Click one to open its panel.")
            }
        }

        // Stock downloads: templates, photos and videos this account got from Stock.
        Column {
            width: parent.width
            spacing: Theme.spacingMd
            visible: root.section === "downloads"

            ThemedLabel {
                width: parent.width
                visible: root.downloads.length === 0
                text: qsTr("Nothing downloaded from Stock yet. Free templates, photos and videos you download there stay here, in your account.")
            }

            ThemedLabel {
                width: parent.width
                visible: root.downloads.length > 0
                text: qsTr("Click one to put it at the playhead, or keep it for later.")
            }

            Flickable {
                width: parent.width
                height: Math.min(downloadList.implicitHeight, 300)
                contentHeight: downloadList.implicitHeight
                clip: true
                visible: root.downloads.length > 0
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: AppScrollBar { }

                Column {
                    id: downloadList
                    width: parent.width
                    spacing: Theme.spacingSm

                    Repeater {
                        model: root.downloads
                        delegate: Rectangle {
                            id: downloadRow
                            required property var modelData
                            readonly property var item: modelData
                            readonly property var actions: root.libraryActions(item)
                            readonly property var local: root.localEntry(item.id)
                            readonly property bool here: root.isTemplate(item) ? Market.sceneTemplateInstalled(item.id)
                                                                              : !!(local && local.exists)
                            width: downloadList.width - Theme.spacingMd
                            height: 60
                            radius: Theme.radiusSm
                            color: rowHover.hovered && actions ? Theme.panelSecondaryBg : "transparent"

                            HoverHandler { id: rowHover }
                            ThemedToolTip {
                                visible: rowHover.hovered && !!downloadRow.actions && !saveButton.hovered
                                         && !placeButton.hovered && !removeArea.containsMouse
                                text: downloadRow.actions ? downloadRow.actions.placeHint : ""
                            }
                            // The row's own click: what the person most likely meant, put it in the edit.
                            // Under the buttons, which take their own clicks.
                            MouseArea {
                                anchors.fill: parent
                                enabled: !!downloadRow.actions
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.useItem(downloadRow.item, "place")
                            }

                            Rectangle {
                                id: rowThumb
                                x: Theme.spacingXs
                                anchors.verticalCenter: parent.verticalCenter
                                width: 80
                                height: 50
                                radius: Theme.radiusSm
                                color: Theme.panelSecondaryBg
                                clip: true
                                Image {
                                    anchors.fill: parent
                                    source: downloadRow.item.thumb_url || ""
                                    fillMode: Image.PreserveAspectCrop
                                    asynchronous: true
                                    opacity: downloadRow.here || root.isTemplate(downloadRow.item) ? 1 : 0.6
                                }
                            }

                            Column {
                                anchors.left: rowThumb.right
                                anchors.leftMargin: Theme.spacingMd
                                anchors.right: rowButtons.left
                                anchors.rightMargin: Theme.spacingMd
                                anchors.verticalCenter: parent.verticalCenter
                                spacing: 2
                                ThemedLabel {
                                    width: parent.width
                                    elide: Text.ElideRight
                                    wrapMode: Text.NoWrap
                                    tone: "default"
                                    text: downloadRow.item.title || ""
                                }
                                ThemedLabel {
                                    width: parent.width
                                    elide: Text.ElideRight
                                    wrapMode: Text.NoWrap
                                    text: [root.sourceName(downloadRow.item),
                                           Qt.formatDate(new Date(downloadRow.item.last_at), Qt.locale().dateFormat(Locale.ShortFormat))].join(" · ")
                                }
                            }

                            Row {
                                id: rowButtons
                                anchors.right: removeButton.visible ? removeButton.left : parent.right
                                anchors.rightMargin: Theme.spacingSm
                                anchors.verticalCenter: parent.verticalCenter
                                spacing: Theme.spacingSm

                                ThemedLabel {
                                    visible: !downloadRow.actions
                                    anchors.verticalCenter: parent.verticalCenter
                                    text: qsTr("No longer in Stock")
                                    HoverHandler { id: goneHover }
                                    ThemedToolTip {
                                        visible: goneHover.hovered
                                        text: qsTr("It is no longer in the Stock catalog")
                                    }
                                }
                                ThemedButton {
                                    id: saveButton
                                    visible: !!downloadRow.actions
                                    variant: "ghost"
                                    text: downloadRow.actions ? downloadRow.actions.save : ""
                                    tooltip: downloadRow.actions ? downloadRow.actions.saveHint : ""
                                    onClicked: root.useItem(downloadRow.item, "save")
                                }
                                ThemedButton {
                                    id: placeButton
                                    visible: !!downloadRow.actions
                                    variant: "primary"
                                    text: downloadRow.actions ? downloadRow.actions.place : ""
                                    tooltip: downloadRow.actions ? downloadRow.actions.placeHint : ""
                                    onClicked: root.useItem(downloadRow.item, "place")
                                }
                            }

                            // Off the account's list; the files on this computer stay.
                            Rectangle {
                                id: removeButton
                                anchors.right: parent.right
                                anchors.rightMargin: Theme.spacingXs
                                anchors.verticalCenter: parent.verticalCenter
                                visible: Account.signedIn
                                width: 22
                                height: 22
                                radius: 11
                                color: removeArea.containsMouse ? Theme.panelSecondaryBg : "transparent"
                                IconGlyph {
                                    anchors.centerIn: parent
                                    glyph: Theme.icons.x
                                    iconSize: 12
                                    iconColor: Theme.panelForeground
                                }
                                MouseArea {
                                    id: removeArea
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: Market.removeFromLibrary(downloadRow.item.id)
                                }
                                ThemedToolTip {
                                    visible: removeArea.containsMouse
                                    text: qsTr("Take it off the list (the files on this computer stay)")
                                }
                            }
                        }
                    }
                }
            }

            ThemedLabel {
                width: parent.width
                visible: root.note.length > 0 && root.downloads.length > 0
                text: root.note
            }

            ThemedButton {
                // The account's list is cleared one item at a time; this one is the local history.
                visible: root.downloads.length > 0 && !Account.signedIn
                variant: "ghost"
                text: qsTr("Clear the list")
                tooltip: qsTr("Forgets this list; the downloaded files stay where they are")
                onClicked: Market.clearDownloadHistory()
            }
        }

        // --- Account actions ---------------------------------------------------------------
        Row {
            spacing: Theme.spacingMd

            ThemedButton {
                variant: "secondary"
                glyph: Theme.icons.settings
                text: qsTr("Account settings")
                onClicked: root.settingsRequested()
            }
            ThemedButton {
                visible: Account.signedIn
                variant: "ghost"
                glyph: Theme.icons.signOut
                text: qsTr("Sign out")
                onClicked: Account.signOut()
            }
        }
    }
}
