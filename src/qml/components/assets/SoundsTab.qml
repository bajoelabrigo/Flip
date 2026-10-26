import QtQuick
import Drift

// Audio FX tab: audio-effect preset library (browse left, edit in the Audio inspector).
Item {
    id: root
    // The panel's sidebar drives the category (0.23): its chips are not shown.
    property bool panelDriven: false

    property alias searchText: browser.searchText
    property alias activeCategory: browser.activeCategory
    property alias categories: browser.categories

    AudioEffectBrowser {
        id: browser
        anchors.fill: parent
        panelDriven: root.panelDriven
    }
}
