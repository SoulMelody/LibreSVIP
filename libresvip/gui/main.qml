import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import Qt5Compat.GraphicalEffects
import "./components/" as Components


ApplicationWindow {
    id: window
    title: qsTr("LibreSVIP")
    flags: Qt.FramelessWindowHint | Qt.Window
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

    MouseArea {
        id: corner
        anchors.fill: parent
        hoverEnabled: true
        onPositionChanged: (mouse) => {
            if (mouse.x < 15) {
                if (mouse.y < 15) {
                    cursorShape = Qt.SizeFDiagCursor
                } else if (mouse.y > window.height - 15) {
                    cursorShape = Qt.SizeBDiagCursor
                } else {
                    cursorShape = Qt.SizeHorCursor
                }
            } else if (mouse.x > window.width - 15) {
                if (mouse.y < 15) {
                    cursorShape = Qt.SizeBDiagCursor
                } else if (mouse.y > window.height - 15) {
                    cursorShape = Qt.SizeFDiagCursor
                } else {
                    cursorShape = Qt.SizeHorCursor
                }
            } else if (mouse.y < 15 || mouse.y > window.height - 15) {
                cursorShape = Qt.SizeVerCursor
            }
        }
        DragHandler {
            id: resizeHandler
            onActiveChanged: if (active) {
                const p = resizeHandler.centroid.position;
                let e = 0;
                if (p.x / width < 0.10) { e |= Qt.LeftEdge }
                if (p.x / width > 0.90) { e |= Qt.RightEdge }
                if (p.y / height < 0.10) { e |= Qt.TopEdge }
                if (p.y / height > 0.90) { e |= Qt.BottomEdge }
                window.startSystemResize(e);
            }
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

    Rectangle {
        id: rect
        anchors.fill: parent
        radius: window.visibility === Window.Maximized ? 0 : 8
        anchors.margins: window.visibility === Window.Maximized ? 0 : 10
    }

    Components.ConverterPage {
        id: converterPage
        header: Components.TopToolbar {
            id: toolbar
        }
        anchors.fill: rect
        layer.enabled: true
        layer.effect: OpacityMask {
            maskSource: rect
        }
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