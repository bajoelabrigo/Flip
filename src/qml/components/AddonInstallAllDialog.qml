import QtQuick
import QtQuick.Controls.Basic
import Drift

// «Install all» (0.32): says how many extras and how much will be downloaded before it starts,
// since a few AI models are large. The queue itself lives in Addons (C++), so this closes as soon
// as it starts: the progress shows at the bottom of the window and the user keeps editing.
ThemedDialog {
    id: root

    // Limits the queue to these ids (resuming one a closed app left half done); empty = all.
    property var onlyIds: []
    property var plan: ({ count: 0, bytes: 0, names: [] })

    title: qsTr("Install all the extras?")
    acceptText: qsTr("Install all")
    preferredWidth: Theme.dialogWidthSm

    function formatSize(bytes) {
        if (bytes >= 1e9)
            return (bytes / 1e9).toFixed(1) + " GB"
        if (bytes >= 1e6)
            return Math.round(bytes / 1e6) + " MB"
        return Math.max(1, Math.round(bytes / 1e3)) + " KB"
    }

    function ask(only) {
        root.onlyIds = only || []
        root.plan = Addons.installAllPlan(root.onlyIds)
        if (Addons.bulk.active) {
            Toasts.info(qsTr("The extras are already being installed."))
            return
        }
        if (root.plan.count === 0) {
            Toasts.success(qsTr("You already have every extra."))
            return
        }
        root.open()
    }

    contentItem: Column {
        width: parent ? parent.width : Theme.dialogWidthSm
        spacing: Theme.spacingLg

        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            size: "sm"
            tone: "default"
            text: qsTr("%n extra(s) will be downloaded and installed: %1 in total.", "", root.plan.count)
                      .arg(root.formatSize(root.plan.bytes))
        }

        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            size: "sm"
            text: qsTr("You can keep editing while they install: the progress shows at the bottom of the window. "
                       + "If you close Flip Studio, it finishes first and then closes by itself.")
        }

        ThemedLabel {
            width: parent.width
            wrapMode: Text.WordWrap
            size: "sm"
            text: (root.plan.names || []).join(" · ")
        }
    }

    onAccepted: {
        if (!Addons.installAll(root.onlyIds))
            Toasts.warning(Addons.installAllRunningElsewhere()
                           ? qsTr("Another Flip Studio window is already installing the extras.")
                           : qsTr("Nothing to install right now."))
    }
}
