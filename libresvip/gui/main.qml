import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import "./components/" as Components


ApplicationWindow {
    id: window
    title: qsTr("LibreSVIP")
    visible: true
    minimumWidth: 1200
    minimumHeight: 800
    Material.primary: "#FF5722"
    Material.accent: "#3F51B5"

    FontLoader {
        id: materialFontLoader
        source: py.qta.font_dir("mdi6")
    }

    Components.Dialogs {
        id: dialogs
    }

    Components.Actions {
        id: actions
    }

    header: Components.TopToolbar {
        id: toolbar
    }

    Components.SettingsDrawer {
        id: settingsDrawer
    }

    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: converterPage
    }

    Components.ConverterPage {
        id: converterPage
    }
}