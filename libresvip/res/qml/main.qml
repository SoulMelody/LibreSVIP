import QtQuick
import QtQuick.Window
import QtQuick.Controls.Material
import FramelessWindow
import LibreSVIP
import "qrc:/qml/components/" as Components

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
        switch (configItems.theme) {
        case "Dark":
            return Material.Dark;
        case "Light":
            return Material.Light;
        default:
            return Material.System;
        }
    }

    Clipboard {
        id: clipboard
    }

    IconicFontLoader {
        id: iconicFontLoader
    }

    ConfigItems {
        id: configItems
    }

    Notifier {
        id: notifier
    }

    TaskManager {
        id: taskManager
    }

    FontLoader {
        source: iconicFontLoader.font_path("mdi7")
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
        Components.MessageBox {}
    }

    function handleThemeChange(theme) {
        switch (theme) {
        case "Light":
            window.Material.theme = Material.Light;
            configItems.theme = "Light";
            break;
        case "Dark":
            window.Material.theme = Material.Dark;
            configItems.theme = "Dark";
            break;
        case "System":
            window.Material.theme = Material.System;
            configItems.theme = "System";
            break;
        }
    }

    Connections {
        target: Application.styleHints
        function onColorSchemeChanged(value) {
            let currentTheme = configItems.theme;
            if (currentTheme === "System") {
                handleThemeChange(currentTheme);
            }
        }
    }

    Connections {
        target: configItems
        function onAuto_set_output_extension_changed(value) {
            taskManager.reset_output_ext("");
        }
    }

    Component.onCompleted: {
        if (configItems.auto_check_for_updates) {
            notifier.check_for_updates();
        }
    }
}
