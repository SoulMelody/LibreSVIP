import QtQuick
import QtQuick.Window
import QtQuick.Controls.Material
import FramelessWindow
import LibreSVIP
import "./components/" as Components


FramelessWindow {
    id: window
    title: qsTr("LibreSVIP")
    visible: true
    minimumWidth: 700
    minimumHeight: 600
    width: 1200
    height: 800
    property bool yesToAll: false
    property bool noToAll: false
    color: "transparent"
    Material.primary: "#FF5722"
    Material.accent: "#3F51B5"
    Material.theme: {
        switch (ConfigItems.get_theme()) {
            case "Dark":
                return Material.Dark
            case "Light":
                return Material.Light
            default:
                return Material.System
        }
    }

    FontLoader {
        source: IconicFontLoader.font_path("mdi7")
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
        anchors.margins: (window.visibility === Window.Maximized && Qt.platform.os === "windows") ? 5 : 0
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
                ConfigItems.set_theme("Light")
                break
            case "Dark":
                window.Material.theme = Material.Dark
                ConfigItems.set_theme("Dark")
                break
            case "System":
                window.Material.theme = Material.System
                ConfigItems.set_theme("System")
                break
        }
    }

    Connections {
        target: Application.styleHints
        function onColorSchemeChanged(value) {
            let currentTheme = ConfigItems.get_theme()
            if (currentTheme === "System") {
                handleThemeChange(currentTheme)
            }
        }
    }

    Connections {
        target: ConfigItems
        function onAuto_set_output_extension_changed(value) {
            TaskManager.reset_output_ext("")
        }
    }
}