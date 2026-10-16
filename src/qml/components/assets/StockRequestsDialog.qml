import QtQuick
import QtQuick.Controls.Basic
import Drift
import ".."

// «Ask for a template»: say what Stock is missing, and vote for what other people asked for.
// The most voted ideas are what gets made next.
ThemedDialog {
    id: root

    title: qsTr("Ask for a template")
    showAccept: false
    rejectText: qsTr("Close")
    preferredWidth: Theme.dialogWidthMd

    property string sort: "top"
    property string message: ""
    property bool messageIsError: false
    property bool sending: false

    // What can be asked for: Stock's own kinds, then "something else".
    readonly property var kinds: {
        const out = []
        const types = Market.types
        for (let i = 0; i < types.length; ++i) {
            const t = types[i]
            if (t.id === "all" || t.id === "video" || t.id === "photo")
                continue
            out.push({ id: t.id, label: t.label || t.id })
        }
        if (out.length === 0)
            out.push({ id: "template", label: qsTr("Template") })
        out.push({ id: "other", label: qsTr("Something else") })
        return out
    }

    function openFor(typeId) {
        root.message = ""
        requestText.text = ""
        let index = 0
        for (let i = 0; i < kinds.length; ++i) {
            if (kinds[i].id === typeId)
                index = i
        }
        kindBox.currentIndex = index
        open()
        requestText.forceActiveFocus()
        Market.refreshRequests(root.sort)
    }

    Connections {
        target: Market
        function onRequestSubmitted(ok, text) {
            root.sending = false
            root.message = text
            root.messageIsError = !ok
            if (ok) {
                requestText.text = ""
                root.sort = "new"
            }
        }
    }

    contentItem: Column {
        spacing: Theme.spacingLg
        width: parent ? parent.width : 420

        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            text: qsTr("Tell us what you would like to find in Stock. The most voted ideas are made first.")
        }

        ThemedTextArea {
            id: requestText
            width: parent.width
            height: 72
            placeholderText: qsTr("For example: a birthday template for my mom with 5 photos")
            wrapMode: TextEdit.Wrap
        }

        Row {
            width: parent.width
            spacing: Theme.spacingMd

            ThemedComboBox {
                id: kindBox
                width: parent.width - sendButton.width - parent.spacing
                model: root.kinds
                textRole: "label"
                valueRole: "id"
            }
            ThemedButton {
                id: sendButton
                variant: "primary"
                text: root.sending ? qsTr("Sending…") : qsTr("Send")
                enabled: !root.sending && requestText.text.trim().length >= 3
                onClicked: {
                    root.sending = true
                    root.message = ""
                    Market.submitRequest(requestText.text, kindBox.currentValue || "template")
                }
            }
        }

        ThemedLabel {
            width: parent.width
            visible: root.message.length > 0
            wrapMode: Text.WordWrap
            color: root.messageIsError ? Theme.destructive : Theme.mutedForeground
            text: root.message
        }

        Rectangle {
            width: parent.width
            height: Theme.borderWidth
            color: Theme.panelBorder
        }

        Row {
            spacing: Theme.spacingSm
            ThemedChip {
                text: qsTr("Most voted")
                selected: root.sort === "top"
                variant: "outline"
                onClicked: { root.sort = "top"; Market.refreshRequests("top") }
            }
            ThemedChip {
                text: qsTr("Newest")
                selected: root.sort === "new"
                variant: "outline"
                onClicked: { root.sort = "new"; Market.refreshRequests("new") }
            }
        }

        ListView {
            id: list
            width: parent.width
            height: Math.min(320, Math.max(80, contentHeight))
            clip: true
            spacing: Theme.spacingSm
            model: Market.requests
            boundsBehavior: Flickable.StopAtBounds
            ScrollBar.vertical: AppScrollBar { }

            Text {
                anchors.centerIn: parent
                visible: list.count === 0
                text: Market.requestsLoading ? qsTr("Loading…") : qsTr("No ideas yet. Be the first!")
                color: Theme.mutedForeground
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSm
            }

            delegate: Rectangle {
                id: row
                required property var modelData
                width: list.width
                height: Math.max(voteButton.height, texts.implicitHeight) + Theme.spacingMd
                radius: Theme.radiusSm
                color: Theme.panelAccent

                // The vote: an arrow and the count, filled once you voted.
                Rectangle {
                    id: voteButton
                    anchors.left: parent.left
                    anchors.leftMargin: Theme.spacingSm
                    anchors.verticalCenter: parent.verticalCenter
                    width: 44
                    height: 44
                    radius: Theme.radiusSm
                    color: row.modelData.voted ? Theme.primary : (voteHover.hovered ? Theme.popoverHover : "transparent")
                    border.width: 1
                    border.color: row.modelData.voted ? Theme.primary : Theme.panelBorder
                    Column {
                        anchors.centerIn: parent
                        IconGlyph {
                            anchors.horizontalCenter: parent.horizontalCenter
                            glyph: Theme.icons.chevronUp
                            iconSize: Theme.iconSizeSm
                            iconColor: row.modelData.voted ? Theme.primaryForeground : Theme.panelForeground
                        }
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: String(row.modelData.votes || 0)
                            color: row.modelData.voted ? Theme.primaryForeground : Theme.panelForeground
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeXs
                            font.weight: Font.DemiBold
                        }
                    }
                    HoverHandler { id: voteHover; cursorShape: Qt.PointingHandCursor }
                    TapHandler { onTapped: Market.voteRequest(row.modelData.id) }
                    ThemedToolTip {
                        text: row.modelData.voted ? qsTr("Remove your vote") : qsTr("Vote for this idea")
                        visible: voteHover.hovered
                    }
                }

                Column {
                    id: texts
                    anchors.left: voteButton.right
                    anchors.right: parent.right
                    anchors.leftMargin: Theme.spacingMd
                    anchors.rightMargin: Theme.spacingMd
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 2
                    Text {
                        width: parent.width
                        text: row.modelData.text || ""
                        color: Theme.panelForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSm
                        wrapMode: Text.WordWrap
                    }
                    Text {
                        width: parent.width
                        text: {
                            const parts = []
                            if (row.modelData.type_label)
                                parts.push(row.modelData.type_label)
                            if (row.modelData.status === "done")
                                parts.push(qsTr("Done — it’s in Stock"))
                            if (row.modelData.mine)
                                parts.push(qsTr("Your idea"))
                            return parts.join(" · ")
                        }
                        color: row.modelData.status === "done" ? Theme.accentOnPanel : Theme.mutedForeground
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeXs
                        elide: Text.ElideRight
                    }
                }
            }
        }
    }
}
