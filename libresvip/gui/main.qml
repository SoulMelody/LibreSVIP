import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import "./components/" as Components


ApplicationWindow {
    id: window
    title: qsTr("LibreSVIP")
    visible: true
    minimumWidth: 800
    minimumHeight: 720
    width: 1200
    height: 800
    Material.primary: "#FF5722"
    Material.accent: "#3F51B5"
    Material.theme: {
        switch (py.config_items.get_theme()) {
            case "Dark":
                return Material.Dark
            case "Light":
                return Material.Light
            default:
                return Material.System
        }
    }

    FontLoader {
        id: materialFontLoader
        source: py.qta.font_dir("mdi6")
    }

    FontLoader {
        id: remixFontLoader
        source: py.qta.font_dir("ri")
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