import QtQuick
import QtQml
import QtQuick.Layouts
import Drift
import ".."

// The strip under the preview that is always there: timecode, transport and fullscreen. Everything
// else lives in the preview's OSD. A RowLayout keeps Play centred while the side groups compress
// instead of colliding at narrow widths.
Item {
    id: bar

    property int projectFps: 30
    property real currentSeconds: 0
    property real durationSeconds: 0
    property bool fullscreen: false
    // Formats seconds as the panel's timecode.
    property var formatTimecode: function (seconds) { return "" }
    // The PreviewViewport the zoom menu drives; null hides the menu.
    property var viewport: null
    signal fullscreenRequested()

    // Zoom levels relative to the fitted view, CapCut's "Completa" being the fit itself.
    readonly property var zoomLevels: [1.0, 1.5, 2.0, 3.0, 4.0]
    readonly property string zoomLabel: {
        if (!viewport || Math.abs(viewport.userZoom - 1.0) < 0.01)
            return qsTr("Fit")
        return Math.round(viewport.userZoom * 100) + "%"
    }

    function zoomTo(level) {
        if (!viewport)
            return
        if (level === 1.0) {
            viewport.resetView()
            return
        }
        viewport.zoomAt(viewport.width / 2, viewport.height / 2, level / viewport.userZoom)
    }

    // The canvas shapes people publish in, sized on a 1080 short side like the Video dialog's.
    readonly property var ratios: [
        { label: "16:9", hint: qsTr("YouTube, horizontal"), w: 1920, h: 1080 },
        { label: "9:16", hint: qsTr("TikTok, Reels, Shorts"), w: 1080, h: 1920 },
        { label: "1:1", hint: qsTr("Square"), w: 1080, h: 1080 },
        { label: "4:5", hint: qsTr("Instagram post"), w: 1080, h: 1350 },
        { label: "4:3", hint: qsTr("Classic"), w: 1440, h: 1080 },
        { label: "21:9", hint: qsTr("Cinema"), w: 2520, h: 1080 }
    ]
    readonly property string ratioLabel: {
        void EditorState.tracksRevision
        const w = EditorState.projectFile.projectWidth()
        const h = EditorState.projectFile.projectHeight()
        for (let i = 0; i < ratios.length; ++i) {
            if (Math.abs(ratios[i].w / ratios[i].h - w / h) < 0.01)
                return ratios[i].label
        }
        return qsTr("Ratio")
    }

    function withShortcut(label, actionId) {
        const key = EditorState.shortcutFor(actionId)
        return key.length > 0 ? qsTr("%1 (%2)").arg(label).arg(key) : label
    }

    implicitHeight: Theme.iconButtonSize + Theme.previewTransportPadding * 2

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: Theme.spacing2xl + Theme.spacingSm
        anchors.rightMargin: Theme.spacing2xl + Theme.spacingSm
        spacing: Theme.spacingLg

        Row {
            Layout.alignment: Qt.AlignVCenter
            spacing: 0

            HoverHandler { id: timecodeHover }

            ThemedToolTip {
                text: qsTr("Current time / total · %1 frames per second").arg(bar.projectFps)
                visible: timecodeHover.hovered
            }

            Text {
                text: bar.formatTimecode(bar.currentSeconds)
                color: Theme.primary
                font.family: Theme.monoFontFamily
                font.pixelSize: Theme.fontSizeXs
                anchors.verticalCenter: parent.verticalCenter
            }
            Text {
                text: " / "
                color: Theme.mutedForeground
                font.family: Theme.monoFontFamily
                font.pixelSize: Theme.fontSizeXs
                anchors.verticalCenter: parent.verticalCenter
            }
            Text {
                text: bar.formatTimecode(bar.durationSeconds)
                color: Theme.mutedForeground
                font.family: Theme.monoFontFamily
                font.pixelSize: Theme.fontSizeXs
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        // Spacers on both sides keep Play optically centred while still letting the whole row
        // shrink instead of overlap.
        Item { Layout.fillWidth: true; Layout.minimumWidth: 0 }

        Row {
            Layout.alignment: Qt.AlignVCenter
            spacing: Theme.spacingXs

            // Jump amount comes from the modifiers held at click time rather than from a separate
            // control: three amounts in each direction would be six more buttons in a row that has
            // to stay centred. AbstractButton.clicked carries no modifiers, hence the query into Qt.
            function jumpStep() {
                const modifiers = EditorState.keyboardModifiers()
                if (Theme.primaryModifierPressed(modifiers))
                    return 10
                if (modifiers & Qt.ShiftModifier)
                    return 5
                return 1
            }

            IconButton {
                anchors.verticalCenter: parent.verticalCenter
                glyph: Theme.icons.rewind
                variant: "text"
                tooltip: Theme.platformShortcutText(qsTr("Jump back 1s · Shift for 5s · Ctrl for 10s"))
                onClicked: EditorState.jumpSeconds(-parent.jumpStep())
            }

            IconButton {
                anchors.verticalCenter: parent.verticalCenter
                glyph: Theme.icons.stepBack
                variant: "text"
                tooltip: bar.withShortcut(qsTr("Previous frame"), "stepBack")
                onClicked: EditorState.stepFrames(-1)
            }

            IconButton {
                anchors.verticalCenter: parent.verticalCenter
                glyph: EditorState.playing ? Theme.icons.pause : Theme.icons.play
                variant: "text"
                tooltip: EditorState.playing ? qsTr("Pause") : qsTr("Play")
                onClicked: EditorState.togglePlayback()
            }

            IconButton {
                anchors.verticalCenter: parent.verticalCenter
                glyph: Theme.icons.stepForward
                variant: "text"
                tooltip: bar.withShortcut(qsTr("Next frame"), "stepForward")
                onClicked: EditorState.stepFrames(1)
            }

            IconButton {
                anchors.verticalCenter: parent.verticalCenter
                glyph: Theme.icons.repeat
                variant: "text"
                tooltip: EditorState.loopWorkAreaEnabled
                         ? qsTr("Loop work area on — click to turn off")
                         : qsTr("Loop work area off — click to turn on")
                active: EditorState.loopWorkAreaEnabled
                enabled: EditorState.workAreaActive
                onClicked: EditorState.toggleLoopWorkArea()
            }

            IconButton {
                anchors.verticalCenter: parent.verticalCenter
                glyph: Theme.icons.fastForward
                variant: "text"
                tooltip: Theme.platformShortcutText(qsTr("Jump forward 1s · Shift for 5s · Ctrl for 10s"))
                onClicked: EditorState.jumpSeconds(parent.jumpStep())
            }
        }

        Item { Layout.fillWidth: true; Layout.minimumWidth: 0 }

        // Zoom: fit, or closer to check detail. The wheel over the preview does the same.
        ThemedChip {
            Layout.alignment: Qt.AlignVCenter
            visible: bar.viewport !== null && !bar.fullscreen
            variant: "outline"
            text: bar.zoomLabel
            tooltip: qsTr("Preview zoom")
            onClicked: zoomMenu.popup()

            ThemedContextMenu {
                id: zoomMenu
                Instantiator {
                    model: bar.zoomLevels
                    delegate: ThemedMenuItem {
                        required property real modelData
                        text: modelData === 1.0 ? qsTr("Fit") : Math.round(modelData * 100) + "%"
                        icon.name: bar.viewport && Math.abs(bar.viewport.userZoom - modelData) < 0.01
                                   ? Theme.icons.check : ""
                        onTriggered: bar.zoomTo(modelData)
                    }
                    onObjectAdded: (index, object) => zoomMenu.insertItem(index, object)
                    onObjectRemoved: (index, object) => zoomMenu.removeItem(object)
                }
            }
        }

        // Aspect ratio of the video, the one-click version of the Video dialog.
        ThemedChip {
            Layout.alignment: Qt.AlignVCenter
            visible: !bar.fullscreen
            variant: "outline"
            text: bar.ratioLabel
            tooltip: qsTr("Aspect ratio of the video")
            enabled: !EditorState.preview.canvasCropMode
            onClicked: ratioMenu.popup()

            ThemedContextMenu {
                id: ratioMenu
                Instantiator {
                    model: bar.ratios
                    delegate: ThemedMenuItem {
                        required property var modelData
                        text: modelData.label + "  ·  " + modelData.hint
                        icon.name: bar.ratioLabel === modelData.label ? Theme.icons.check : ""
                        onTriggered: EditorState.projectFile.setProjectResolution(modelData.w, modelData.h)
                    }
                    onObjectAdded: (index, object) => ratioMenu.insertItem(index, object)
                    onObjectRemoved: (index, object) => ratioMenu.removeItem(object)
                }
            }
        }

        IconButton {
            Layout.alignment: Qt.AlignVCenter
            glyph: bar.fullscreen ? Theme.icons.minimize : Theme.icons.maximize
            variant: "text"
            tooltip: bar.fullscreen ? qsTr("Exit fullscreen preview (Esc)") : qsTr("Fullscreen preview")
            active: bar.fullscreen
            // The window and the surrounding panels belong to Main, so the toggle is requested
            // rather than performed here.
            onClicked: bar.fullscreenRequested()
        }
    }
}
