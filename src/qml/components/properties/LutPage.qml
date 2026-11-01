import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// Adjust > LUT: a gallery of looks (the factory ones and those the person imported, each tile the
// real table applied to a reference photo), the one in use with its strength, on/off, reset and
// remove, and Import LUT… for a .cube file. The look is the clip's color.lut effect, so it lives in
// the same stack as the rest of the colour: on a clip, or on an adjustment layer for everything
// under it.
Column {
    id: lutPage

    // The AdjustInspector: effect lookups and the one-undo-step edit helpers.
    required property var host

    spacing: Theme.spacingLg

    readonly property int fxIndex: host.effectIndex("color.lut")
    readonly property var fx: fxIndex >= 0 ? host.effects[fxIndex] : null
    readonly property string lutPath: {
        if (!fx)
            return ""
        const params = fx.params || []
        for (let i = 0; i < params.length; i++) {
            if (params[i].key === "lut")
                return params[i].value || ""
        }
        return ""
    }
    readonly property bool lutOn: !!fx && fx.enabled !== false
    readonly property var info: lutPath ? EditorState.lutInfo(lutPath) : ({})
    property int libraryRevision: 0
    readonly property var library: {
        void libraryRevision
        return EditorState.lutLibrary()
    }
    property string importError: ""

    Connections {
        target: EditorState
        function onLutLibraryChanged() { lutPage.libraryRevision++ }
    }

    // Puts a LUT on the clip: adds the effect the first time, then points it at the file.
    function use(path) {
        if (!host.canEdit)
            return
        if (host.effectIndex("color.lut") < 0)
            EditorState.addEffect(EditorState.selectedTrack, EditorState.selectedClip, "color.lut")
        const i = host.effectIndex("color.lut")
        if (i >= 0)
            EditorState.setEffectStringParam(EditorState.selectedTrack, EditorState.selectedClip, i, "lut",
                                             "file:///" + String(path).replace(/^\/+/, ""))
    }

    function importFile() {
        const url = FileDialogs.openFile(qsTr("Import LUT"), [qsTr("LUT (*.cube)"), qsTr("All files (*)")])
        if (!url || url.toString() === "")
            return
        const result = EditorState.importLut(url)
        if (!result.ok) {
            lutPage.importError = result.error || qsTr("This file is not a LUT that can be used.")
            return
        }
        lutPage.importError = ""
        lutPage.use(result.path)
    }

    Text {
        width: parent.width
        wrapMode: Text.WordWrap
        text: qsTr("A LUT is a ready-made colour look. Pick one, or import a .cube file; Intensity mixes it with the original colour.")
        color: Theme.mutedForeground
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }

    ThemedButton {
        width: parent.width
        text: qsTr("Import LUT…")
        glyph: "image-up"
        enabled: lutPage.host.canEdit
        onClicked: lutPage.importFile()
    }

    Text {
        visible: lutPage.importError.length > 0
        width: parent.width
        wrapMode: Text.WordWrap
        text: lutPage.importError
        color: Theme.destructive
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeXs
    }

    // --- The LUT in use ------------------------------------------------------------------------
    Column {
        visible: !!lutPage.fx
        width: parent.width
        spacing: Theme.spacingMd

        Row {
            width: parent.width
            spacing: Theme.spacingSm
            Text {
                width: parent.width - lutSwitch.width - Theme.spacingSm
                anchors.verticalCenter: parent.verticalCenter
                elide: Text.ElideRight
                text: lutPage.lutPath ? (lutPage.info.name || "") : qsTr("No LUT chosen yet")
                color: Theme.foreground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                font.weight: Font.Medium
            }
            ThemedSwitch {
                id: lutSwitch
                checked: lutPage.lutOn
                tooltip: qsTr("Turn the LUT off to compare with and without it")
                onToggled: EditorState.setEffectEnabled(EditorState.selectedTrack, EditorState.selectedClip,
                                                        lutPage.fxIndex, checked)
            }
        }

        // Saved in the project but not found here, or found and unreadable.
        Column {
            visible: !!lutPage.lutPath && !lutPage.info.ok
            width: parent.width
            spacing: Theme.spacingSm
            Text {
                width: parent.width
                wrapMode: Text.WordWrap
                text: lutPage.info.error || ""
                color: Theme.destructive
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeXs
            }
            ThemedButton {
                text: qsTr("Find the LUT…")
                glyph: Theme.icons.folder
                variant: "ghost"
                onClicked: lutPage.importFile()
            }
        }

        // Intensity, 0..100 %: one undo step a drag, double-click for 100 %.
        Column {
            id: intensityRow
            width: parent.width
            spacing: 2
            readonly property real current: lutPage.host.value("color.lut", "intensity", 1)
            Row {
                width: parent.width
                Text {
                    width: parent.width - 48
                    text: qsTr("Intensity")
                    color: Theme.mutedForeground
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeXs
                }
                Text {
                    width: 48
                    horizontalAlignment: Text.AlignRight
                    text: Math.round(intensitySlider.value * 100) + " %"
                    color: Theme.panelForeground
                    font.family: Theme.monoFontFamily
                    font.pixelSize: Theme.fontSizeXs
                }
            }
            ThemedSlider {
                id: intensitySlider
                width: parent.width
                label: qsTr("Intensity")
                from: 0
                to: 1
                Binding on value {
                    when: !intensitySlider.pressed
                    restoreMode: Binding.RestoreNone
                    value: intensityRow.current
                }
                onMoved: lutPage.host.preview("intensity", value)
                onPressedChanged: {
                    if (pressed)
                        lutPage.host.beginEdit("color.lut", qsTr("LUT intensity"))
                    else
                        lutPage.host.endEdit()
                }
                TapHandler {
                    acceptedButtons: Qt.LeftButton
                    onDoubleTapped: lutPage.host.setMany("color.lut", qsTr("Reset LUT intensity"), ({ intensity: 1 }))
                }
            }
        }

        Row {
            spacing: Theme.spacingSm
            ThemedButton {
                text: qsTr("Reset intensity")
                variant: "ghost"
                glyph: Theme.icons.reset
                onClicked: lutPage.host.setMany("color.lut", qsTr("Reset LUT intensity"), ({ intensity: 1 }))
            }
            ThemedButton {
                text: qsTr("Remove LUT")
                variant: "ghost"
                glyph: Theme.icons.x
                onClicked: EditorState.removeEffect(EditorState.selectedTrack, EditorState.selectedClip,
                                                    lutPage.fxIndex)
            }
        }
    }

    // --- Gallery -------------------------------------------------------------------------------
    Repeater {
        model: [
            { factory: true, title: qsTr("Looks") },
            { factory: false, title: qsTr("Imported") }
        ]
        delegate: Column {
            id: group
            required property var modelData
            readonly property var items: lutPage.library.filter(l => l.factory === group.modelData.factory)
            visible: items.length > 0
            width: lutPage.width
            spacing: Theme.spacingSm

            Text {
                text: group.modelData.title
                color: Theme.foreground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
                font.weight: Font.Medium
            }

            Flow {
                width: parent.width
                spacing: Theme.spacingSm
                Repeater {
                    model: group.items
                    delegate: Rectangle {
                        id: tile
                        required property var modelData
                        readonly property bool current: !!lutPage.lutPath
                            && String(lutPage.lutPath).split(/[/\\]/).pop() === String(modelData.path).split(/[/\\]/).pop()
                        width: (group.width - Theme.spacingSm * 2) / 3
                        height: width + tileName.implicitHeight + 6
                        radius: Theme.radiusSm
                        color: "transparent"
                        border.width: current ? 2 : Theme.borderWidth
                        border.color: current ? Theme.primary : Theme.panelBorder
                        opacity: lutPage.host.canEdit ? 1 : 0.5
                        scale: tileTap.pressed ? 0.97 : (tileHover.hovered ? 1.02 : 1.0)
                        Behavior on scale {
                            NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easing }
                        }

                        // Under the pointer: the reference photo without the look, wiping to it.
                        BeforeAfterImage {
                            id: thumb
                            x: 3
                            y: 3
                            width: parent.width - 6
                            height: width
                            beforeSource: EditorState.lutReference(tile.modelData.path)
                            afterSource: EditorState.lutThumbnail(tile.modelData.path)
                            playing: tileHover.hovered
                        }
                        Text {
                            id: tileName
                            anchors.top: thumb.bottom
                            anchors.topMargin: 2
                            width: parent.width
                            horizontalAlignment: Text.AlignHCenter
                            elide: Text.ElideRight
                            text: tile.modelData.name
                            color: tile.current ? Theme.foreground : Theme.mutedForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                        }
                        // Pointer handlers, as the asset cards: the MouseArea never got the click.
                        HoverHandler {
                            id: tileHover
                            enabled: lutPage.host.canEdit
                            cursorShape: Qt.PointingHandCursor
                        }
                        TapHandler {
                            id: tileTap
                            enabled: lutPage.host.canEdit
                            acceptedButtons: Qt.LeftButton
                            onTapped: lutPage.use(tile.modelData.path)
                        }
                        TapHandler {
                            enabled: lutPage.host.canEdit && !tile.modelData.factory
                            acceptedButtons: Qt.RightButton
                            onTapped: deleteMenu.popup()
                        }
                        ThemedContextMenu {
                            id: deleteMenu
                            ThemedMenuItem {
                                text: qsTr("Delete from my LUTs")
                                onTriggered: EditorState.removeImportedLut(tile.modelData.path)
                            }
                        }
                    }
                }
            }
        }
    }
}
