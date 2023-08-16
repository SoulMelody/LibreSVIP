import QtQuick
import QtQuick.Window
import QtQuick.Controls.Material
import FramelessWindow
import "./components/" as Components


FramelessWindow {
    id: window
    title: qsTr("LibreSVIP")
    visible: true
    minimumWidth: 800
    minimumHeight: 600
    width: 1200
    height: 800
    property bool yesToAll: false
    property bool noToAll: false
    color: "transparent"
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
        source: py.qta.font_path("mdi6")
    }

    FontLoader {
        id: remixFontLoader
        source: py.qta.font_path("ri")
    }

    Components.Dialogs {
        id: dialogs
    }

    Components.Actions {
        id: actions
    }

    Components.ConverterPage {
        id: converterPage
        header: Components.TopToolbar {
            id: toolbar
        }
        anchors.fill: parent
    }

    Component {
        id: messageBox
        Components.MessageBox {
        }
    }

    function handleThemeChange(theme){
        switch (theme) {
            case "Light":
                window.Material.theme = Material.Light
                py.config_items.set_theme("Light")
                break
            case "Dark":
                window.Material.theme = Material.Dark
                py.config_items.set_theme("Dark")
                break
            case "System":
                window.Material.theme = Material.System
                py.config_items.set_theme("System")
                break
        }
    }

    Connections {
        target: Application.styleHints
        function onColorSchemeChanged(value) {
            let currentTheme = py.config_items.get_theme()
            if (currentTheme === "System") {
                handleThemeChange(currentTheme)
            }
        }
    }
}