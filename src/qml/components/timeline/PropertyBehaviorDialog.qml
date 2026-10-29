import QtCore
import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift
import ".."

// After Effects' most used expressions as a behaviour of one property (0.26): loopOut (cycle,
// ping-pong, offset, continue), time × speed and wiggle, which add up in that order. Opened from a
// keyframe row's menu; "Apply to" picks any other property of the layer, as After Effects' stopwatch
// of each property does, and the expressions written can be saved and used again (Jorge, 0.26).
ThemedDialog {
    id: root

    property int trackIndex: -1
    property int clipIndex: -1
    // The props of the row (X and Y for Position); all of them take the same behaviour.
    property var props: []
    property string label: ""
    // [{label, props}]: what "Apply to" offers; the row it was opened from comes first.
    property var targets: []
    property int targetIndex: 0

    // My expressions, kept with the app's settings so every project has them: [{name, code}].
    Settings {
        id: savedStore
        category: "expressions"
        property string saved: "[]"
    }
    property var savedExpressions: []
    function loadSaved() {
        try {
            const list = JSON.parse(savedStore.saved)
            root.savedExpressions = Array.isArray(list) ? list : []
        } catch (e) {
            root.savedExpressions = []
        }
    }
    function storeSaved(list) {
        savedStore.saved = JSON.stringify(list)
        root.savedExpressions = list
    }

    readonly property var loops: [
        { id: "none", label: qsTr("No loop") },
        { id: "cycle", label: qsTr("Cycle (repeat the keys)") },
        { id: "pingpong", label: qsTr("Ping-pong (back and forth)") },
        { id: "offset", label: qsTr("Offset (repeat, adding up)") },
        { id: "continue", label: qsTr("Continue (keep the last speed)") }
    ]

    title: qsTr("Behavior · %1").arg(label)
    acceptText: qsTr("Apply")
    preferredWidth: Theme.dialogWidthSm

    function openFor(track, clip, props, label, targets) {
        root.trackIndex = track
        root.clipIndex = clip
        // The row it was opened from first, then the layer's other properties.
        const list = [{ label: label, props: props }]
        for (const t of (targets || [])) {
            if (JSON.stringify(t.props) !== JSON.stringify(props))
                list.push(t)
        }
        root.targets = list
        root.targetIndex = 0
        targetBox.currentIndex = 0
        root.loadSaved()
        savedBox.currentIndex = -1
        nameField.text = ""
        root.loadTarget(0)
        open()
    }

    // Shows what the property picked in "Apply to" already does.
    function loadTarget(index) {
        const t = root.targets[index]
        if (!t)
            return
        root.targetIndex = index
        root.props = t.props
        root.label = t.label
        const b = EditorState.propertyBehavior(root.trackIndex, root.clipIndex, t.props[0]) || {}
        let li = 0
        for (let i = 0; i < loops.length; ++i) {
            if (loops[i].id === (b.loop || "none"))
                li = i
        }
        loopBox.currentIndex = li
        wiggleSwitch.checked = (b.wiggleFrequency || 0) > 0 && (b.wiggleAmount || 0) !== 0
        frequencyField.value = b.wiggleFrequency > 0 ? b.wiggleFrequency : 2
        amountField.value = b.wiggleAmount ? b.wiggleAmount : 20
        seedField.value = b.wiggleSeed || 0
        speedField.value = b.speed || 0
        expressionField.text = b.expression || ""
    }

    function behavior() {
        return {
            loop: loops[loopBox.currentIndex].id,
            speed: speedField.value,
            wiggleFrequency: wiggleSwitch.checked ? frequencyField.value : 0,
            wiggleAmount: wiggleSwitch.checked ? amountField.value : 0,
            wiggleSeed: Math.round(seedField.value),
            expression: expressionField.text
        }
    }

    onAccepted: {
        for (const field of [frequencyField, amountField, seedField, speedField])
            field.parseAndCommit()
        const b = behavior()
        for (const prop of root.props)
            EditorState.setPropertyBehavior(root.trackIndex, root.clipIndex, prop, b)
    }

    contentItem: Column {
        width: root.preferredWidth
        spacing: Theme.spacingMd

        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            size: "sm"
            opacity: 0.85
            text: qsTr("What After Effects does with expressions, without writing code. They add up: the loop, then the constant speed, then the wiggle.")
        }

        ThemedLabel { text: qsTr("Apply to") }
        ThemedComboBox {
            id: targetBox
            width: parent.width
            model: root.targets.map(t => t.label)
            onActivated: index => root.loadTarget(index)
        }

        ThemedLabel { text: qsTr("Loop after the last keyframe") }
        ThemedComboBox {
            id: loopBox
            width: parent.width
            model: root.loops.map(l => l.label)
        }

        ThemedSwitch {
            id: wiggleSwitch
            width: parent.width
            text: qsTr("Wiggle")
            tooltip: qsTr("A smooth random shake around the value, like wiggle(frequency, amount)")
        }
        Row {
            width: parent.width
            spacing: Theme.spacingMd
            visible: wiggleSwitch.checked
            Column {
                width: (parent.width - 2 * parent.spacing) / 3
                spacing: 2
                ThemedLabel { text: qsTr("Per second"); size: "sm" }
                ThemedNumberField { id: frequencyField; width: parent.width; from: 0.01; to: 60; step: 0.5; decimals: 2 }
            }
            Column {
                width: (parent.width - 2 * parent.spacing) / 3
                spacing: 2
                ThemedLabel { text: qsTr("Amount"); size: "sm" }
                ThemedNumberField { id: amountField; width: parent.width; from: -100000; to: 100000; step: 1; decimals: 2 }
            }
            Column {
                width: (parent.width - 2 * parent.spacing) / 3
                spacing: 2
                ThemedLabel { text: qsTr("Seed"); size: "sm" }
                ThemedNumberField { id: seedField; width: parent.width; from: 0; to: 9999; step: 1 }
            }
        }

        ThemedLabel { text: qsTr("Constant speed (per second)") }
        ThemedNumberField {
            id: speedField
            width: parent.width
            from: -100000
            to: 100000
            step: 1
            decimals: 2
        }
        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            size: "sm"
            opacity: 0.7
            text: qsTr("For example 90 on Rotation turns the layer a quarter turn every second, for as long as the clip lasts.")
        }

        // After Effects' expression, in JavaScript (0.26): run last, on the value with all the above.
        // The spiral is After Effects' pick whip: dragged onto another layer's property line in the
        // timeline, it writes that property where the cursor is.
        Row {
            spacing: Theme.spacingSm
            ThemedLabel {
                anchors.verticalCenter: parent.verticalCenter
                text: qsTr("Expression (JavaScript)")
            }
            Item {
                id: whip
                width: 20
                height: 20
                anchors.verticalCenter: parent.verticalCenter
                property point from: Qt.point(0, 0)
                property point to: Qt.point(0, 0)

                // The property line under a point of the window, if any.
                function lineAt(item, sx, sy) {
                    if (!item || !item.visible)
                        return null
                    const kids = item.children
                    for (let i = kids.length - 1; i >= 0; --i) {
                        const k = kids[i]
                        if (!k || !k.visible || k.width <= 0 || k.height <= 0)
                            continue
                        const p = k.mapFromItem(null, sx, sy)
                        if (p.x < 0 || p.y < 0 || p.x > k.width || p.y > k.height)
                            continue
                        if (k.exprWhipTarget === true)
                            return k
                        const inner = lineAt(k, sx, sy)
                        if (inner)
                            return inner
                    }
                    return null
                }

                IconGlyph {
                    anchors.centerIn: parent
                    glyph: "pick-whip"
                    iconSize: 15
                    iconColor: whipArea.containsMouse || whipArea.pressed ? Theme.primary : Theme.mutedForeground
                }
                MouseArea {
                    id: whipArea
                    anchors.fill: parent
                    hoverEnabled: true
                    preventStealing: true
                    cursorShape: Qt.CrossCursor
                    onPressed: mouse => {
                        whip.from = mapToItem(null, width / 2, height / 2)
                        whip.to = whip.from
                        // See through the dialog to the timeline while aiming.
                        root.opacity = 0.3
                        whipLine.requestPaint()
                    }
                    onPositionChanged: mouse => {
                        if (!pressed)
                            return
                        whip.to = mapToItem(null, mouse.x, mouse.y)
                        whipLine.requestPaint()
                    }
                    onReleased: mouse => {
                        root.opacity = 1
                        const p = mapToItem(null, mouse.x, mouse.y)
                        const line = whip.lineAt(whip.Window.window ? whip.Window.window.contentItem : null, p.x, p.y)
                        if (!line)
                            return
                        const ref = line.exprWhipReference(root.props.length > 0 ? root.props[0] : "")
                        if (ref.length === 0) {
                            EditorState.setLastMessage(qsTr("The pick whip links another layer's position, rotation, scale, opacity or anchor point"), "warning")
                            return
                        }
                        expressionField.insert(expressionField.cursorPosition, ref)
                        expressionField.forceActiveFocus()
                    }
                    onCanceled: root.opacity = 1
                }
                ThemedToolTip {
                    visible: whipArea.containsMouse && !whipArea.pressed
                    text: qsTr("Pick whip: drag onto another layer's property line in the timeline")
                }
                // The rubber line while aiming, over everything.
                Canvas {
                    id: whipLine
                    parent: Overlay.overlay
                    anchors.fill: parent
                    z: 100000
                    visible: whipArea.pressed
                    onPaint: {
                        const ctx = getContext("2d")
                        ctx.clearRect(0, 0, width, height)
                        if (!whipArea.pressed)
                            return
                        ctx.strokeStyle = Theme.primary
                        ctx.lineWidth = 2
                        ctx.beginPath()
                        ctx.moveTo(whip.from.x, whip.from.y)
                        ctx.lineTo(whip.to.x, whip.to.y)
                        ctx.stroke()
                    }
                }
            }
        }
        ThemedTextArea {
            id: expressionField
            width: parent.width
            height: 72
            placeholderText: "value + wiggle(2, 10) - value  /  time * 90  /  thisComp.layer(\"Nulo 1\").transform.rotation"
            font.family: "Consolas"
        }
        // My expressions: pick one to write it in, or save the one written under a name.
        Row {
            width: parent.width
            spacing: Theme.spacingSm
            ThemedComboBox {
                id: savedBox
                width: parent.width - deleteSaved.width - parent.spacing
                model: root.savedExpressions.map(e => e.name)
                displayText: currentIndex < 0 ? qsTr("My expressions (%1)").arg(root.savedExpressions.length)
                                              : currentText
                onActivated: index => {
                    const e = root.savedExpressions[index]
                    if (e)
                        expressionField.text = e.code
                }
            }
            ThemedButton {
                id: deleteSaved
                variant: "ghost"
                glyph: Theme.icons.trash
                tooltip: qsTr("Delete this saved expression")
                enabled: savedBox.currentIndex >= 0
                onClicked: {
                    const list = root.savedExpressions.slice()
                    list.splice(savedBox.currentIndex, 1)
                    root.storeSaved(list)
                    savedBox.currentIndex = -1
                }
            }
        }
        Row {
            width: parent.width
            spacing: Theme.spacingSm
            ThemedTextField {
                id: nameField
                width: parent.width - saveButton.width - parent.spacing
                placeholderText: qsTr("Name to save this expression")
            }
            ThemedButton {
                id: saveButton
                text: qsTr("Save")
                enabled: expressionField.text.trim().length > 0
                         && EditorState.checkExpression(expressionField.text).length === 0
                onClicked: {
                    const name = nameField.text.trim().length > 0 ? nameField.text.trim()
                                                                   : expressionField.text.trim().split("
")[0].slice(0, 40)
                    // The same name replaces the one saved before.
                    const list = root.savedExpressions.filter(e => e.name !== name)
                    list.push({ name: name, code: expressionField.text })
                    list.sort((a, b) => a.name.localeCompare(b.name))
                    root.storeSaved(list)
                    savedBox.currentIndex = list.findIndex(e => e.name === name)
                    nameField.text = ""
                    EditorState.setLastMessage(qsTr("Expression saved as \"%1\"").arg(name), "info")
                }
            }
        }
        ThemedLabel {
            readonly property string error: EditorState.checkExpression(expressionField.text)
            width: parent.width
            wrapMode: Text.WordWrap
            size: "sm"
            color: error.length > 0 ? "#e5484d" : Theme.mutedForeground
            text: error.length > 0 ? error
                                   : qsTr("value, time, wiggle(freq, amount), Math, and thisComp.layer(\"Name\").transform.position[0], .rotation, .scale[0], .opacity, .anchorPoint[0]. The last line is the result.")
        }
    }
}
