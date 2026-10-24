import QtQuick
import QtMultimedia
import Drift
import ".."

// One stock result as a tile: thumbnail, price and duration badges, and the download state
// drawn over it (progress with cancel, or failure with retry). A video tile plays its preview,
// muted, while hovered; a music or sound tile plays its audio.
Rectangle {
    id: root

    required property var item
    property bool compact: Theme.compact
    property bool current: false
    // Off where something else sits in that corner (Titles › Trending's download mark).
    property bool showDuration: true
    // The flame on what is trending (MarketClient::isTrendingItem), and the star that keeps one of
    // our own items in its panel's favorites ("stock:<type>:<id>" in the panel's group), as on the web.
    property bool showTrend: true
    property bool showFavorite: true
    readonly property bool trending: {
        void Market.weeklyTrendingIds
        return showTrend && Market.isTrendingItem(item)
    }
    readonly property bool favoritable: showFavorite && String(item.id || "").indexOf("flip:") === 0

    signal openRequested()

    readonly property var job: {
        void Market.downloadsRevision
        return Market.downloadInfo(item.id)
    }
    readonly property bool busy: job.status === "waiting" || job.status === "queued"
                                 || job.status === "processing" || job.status === "downloading"
                                 || job.status === "importing"
    readonly property int price: Number(item.price_coins || 0)
    readonly property string kind: item.media_kind || item.type || ""
    readonly property bool isVideo: kind === "video" || kind === "greenscreen"
    readonly property bool isAudio: kind === "audio" || kind === "music" || kind === "sound"
    // A card wider than it is tall (a 16:9 template, a landscape overlay): use the plain wide
    // frame and loop when the item has them, not the 9:16 storyboard card cropped to a band.
    readonly property bool wide: width > height + 1
    readonly property string thumbSource: wide ? (item.thumb_wide_url || item.thumb_url || "")
                                              : (item.thumb_url || "")
    readonly property string previewSource: wide ? (item.preview_wide_url || item.preview_url || "")
                                                : (item.preview_url || "")
    // Anything with a moving preview plays it under the pointer, not only stock footage: templates,
    // overlays, transitions, animated texts and stickers ship a preview.mp4 too (Jorge, 2026-10-18).
    readonly property bool hasMotion: !isAudio && /\.(mp4|webm|mov)(\?|$)/i.test(previewSource)

    radius: Theme.radiusSm
    color: Theme.panelAccent
    clip: true
    border.width: current ? Theme.borderWidthFocus : 0
    border.color: Theme.focusRing
    // Grows a little under the pointer and gives under a press, like the other asset cards.
    scale: tap.pressed ? 0.97 : (hover.hovered && !root.compact ? 1.02 : 1.0)
    Behavior on scale {
        NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
    }

    function formatDuration(ms) {
        const n = Number(ms)
        if (!n || n <= 0)
            return ""
        const s = Math.round(n / 1000)
        return Math.floor(s / 60) + ":" + (s % 60 < 10 ? "0" : "") + (s % 60)
    }

    // Music and sounds play once the pointer has rested a moment, so sweeping across a shelf
    // stays quiet.
    property bool audioArmed: false

    HoverHandler {
        id: hover
        cursorShape: Qt.PointingHandCursor
        onHoveredChanged: {
            root.audioArmed = false
            if (hovered && root.isAudio)
                audioDelay.restart()
            else
                audioDelay.stop()
        }
    }

    SkeletonBox {
        anchors.fill: parent
        visible: thumb.status === Image.Loading
    }

    Image {
        id: thumb
        anchors.fill: parent
        source: root.thumbSource
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        cache: true
        // Decoded at the drawn size; the served thumbnail is several times larger.
        sourceSize.width: Math.max(1, Math.round(parent.width))
        opacity: status === Image.Ready ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: Theme.durationBase; easing.type: Theme.easing } }
    }

    // One player at a time: only the hovered tile creates one.
    Loader {
        anchors.fill: parent
        active: (root.isVideo || root.hasMotion) && hover.hovered && !root.busy && !!root.previewSource
                && !root.compact
        sourceComponent: Item {
            VideoOutput {
                id: out
                anchors.fill: parent
                fillMode: VideoOutput.PreserveAspectCrop
            }
            MediaPlayer {
                source: root.previewSource
                videoOutput: out
                loops: MediaPlayer.Infinite
                Component.onCompleted: play()
            }
        }
    }

    Timer {
        id: audioDelay
        interval: 300
        onTriggered: root.audioArmed = true
    }
    Loader {
        active: root.isAudio && root.audioArmed && hover.hovered && !root.busy
                && !!root.item.preview_url && !root.compact
        sourceComponent: MediaPlayer {
            source: root.item.preview_url
            audioOutput: AudioOutput {}
            Component.onCompleted: play()
        }
    }
    Rectangle {
        visible: root.isAudio
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: Theme.spacingSm
        width: Theme.iconSizeBase + Theme.spacingMd
        height: width
        radius: width / 2
        color: Theme.scrimStrong
        IconGlyph {
            anchors.centerIn: parent
            glyph: hover.hovered && !root.compact ? Theme.icons.volumeHigh : Theme.icons.music
            iconSize: Theme.iconSizeSm
            iconColor: Theme.onMedia
        }
    }

    // A song or a sound: the flame beside its star, top right (Jorge, 2026-10-24), as the web.
    TrendBadge {
        anchors.left: root.isAudio ? undefined : parent.left
        anchors.right: root.isAudio ? (favButton.visible ? favButton.left : parent.right) : undefined
        anchors.top: parent.top
        anchors.margins: 3
        visible: root.trending && root.price <= 0
    }

    AssetFavoriteButton {
        id: favButton
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 3
        z: 2
        visible: root.favoritable && !root.busy
        tabId: root.favoritable ? Market.stockFavoriteGroup(root.item) : ""
        itemId: root.favoritable ? Market.stockFavoriteKey(root.item.id) : ""
        stockItem: root.item
    }

    Rectangle {
        visible: root.price > 0
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: Theme.spacingSm
        color: Theme.scrimStrong
        radius: Theme.radiusXs
        width: coinLabel.implicitWidth + Theme.spacingLg
        height: coinLabel.implicitHeight + Theme.spacingSm
        Text {
            id: coinLabel
            anchors.centerIn: parent
            text: String(root.price)
            color: Theme.onMedia
            font.pixelSize: Theme.fontSizeXs
            font.family: Theme.fontFamily
        }
    }

    Rectangle {
        visible: root.showDuration && durLabel.text.length > 0
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: Theme.spacingSm
        color: Theme.scrimStrong
        radius: Theme.radiusXs
        width: durLabel.implicitWidth + Theme.spacingLg
        height: durLabel.implicitHeight + Theme.spacingSm
        Text {
            id: durLabel
            anchors.centerIn: parent
            text: root.formatDuration(root.item.duration_ms)
            color: Theme.onMedia
            font.pixelSize: Theme.fontSizeXs
            font.family: Theme.fontFamily
        }
    }

    TapHandler {
        id: tap
        onTapped: root.openRequested()
    }

    // Progress with a way out: a job wedged on a slow source otherwise held its tile until the
    // file timeout. On touch the ring and a real cancel button are both shown.
    Rectangle {
        visible: root.busy
        anchors.fill: parent
        color: Theme.scrimStrong

        CircularProgress {
            anchors.centerIn: parent
            visible: root.compact || !busyHover.hovered
            value: Number(root.job.progress || 0)
            indeterminate: Number(root.job.progress || 0) <= 0
            size: Theme.spacing3xl
            progressColor: Theme.onMedia
        }
        IconGlyph {
            anchors.centerIn: parent
            visible: !root.compact && busyHover.hovered
            glyph: Theme.icons.x
            iconSize: Theme.iconSizeBase
            iconColor: Theme.onMedia
        }
        IconButton {
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: Theme.spacingXs
            visible: root.compact
            buttonSize: Theme.androidMinTouchTarget
            iconSize: Theme.iconSizeMd
            glyph: Theme.icons.x
            tooltip: qsTr("Cancel download")
            onClicked: Market.cancelDownload(root.item.id)
        }
        HoverHandler {
            id: busyHover
            enabled: !root.compact
            cursorShape: Qt.PointingHandCursor
        }
        ThemedToolTip {
            text: qsTr("Cancel download")
            visible: busyHover.hovered
            y: parent.height + 4
        }
        TapHandler {
            enabled: !root.compact
            onTapped: Market.cancelDownload(root.item.id)
        }
    }

    Rectangle {
        visible: root.job.status === "failed"
        anchors.fill: parent
        color: Theme.scrimStrong

        Column {
            anchors.centerIn: parent
            spacing: Theme.spacingSm
            IconGlyph {
                anchors.horizontalCenter: parent.horizontalCenter
                glyph: Theme.icons.error
                iconSize: Theme.iconSizeBase
                iconColor: Theme.onMedia
            }
            ThemedButton {
                anchors.horizontalCenter: parent.horizontalCenter
                visible: root.job.retryable === true
                text: qsTr("Retry")
                onClicked: Market.retryDownload(root.item.id)
            }
        }
        // Retry is the one thing to press on a failed tile.
        TapHandler { }
    }
}
