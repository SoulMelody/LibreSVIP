import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
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
    property int edgeSize: 8
    property bool yesToAll: false
    property bool noToAll: false
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

    // Left bottom edge
    MouseArea {
        // from https://github.com/cutefishos/fishui/blob/main/src/controls/Window.qml
        height: edgeSize * 2
        width: height
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        cursorShape: Qt.SizeBDiagCursor
        propagateComposedEvents: true
        preventStealing: false
        z: 999
        visible: window.visibility !== Window.Maximized

        onPressed: (mouse) => {
            mouse.accepted = false
        }

        DragHandler {
            grabPermissions: TapHandler.TakeOverForbidden
            target: null
            onActiveChanged: if (active) { window.startSystemResize(Qt.LeftEdge | Qt.BottomEdge) }
        }
    }

    // Right bottom edge
    MouseArea {
        height: edgeSize * 2
        width: height
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        cursorShape: Qt.SizeFDiagCursor
        propagateComposedEvents: true
        preventStealing: false
        z: 999
        visible: window.visibility !== Window.Maximized

        onPressed: (mouse) => {
            mouse.accepted = false
        }

        DragHandler {
            grabPermissions: TapHandler.TakeOverForbidden
            target: null
            onActiveChanged: if (active) { window.startSystemResize(Qt.RightEdge | Qt.BottomEdge) }
        }
    }

    // Top edge
    MouseArea {
        height: edgeSize / 2
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: header.top
        anchors.leftMargin: edgeSize * 2
        anchors.rightMargin: edgeSize * 2
        cursorShape: Qt.SizeVerCursor
        z: 999
        visible: window.visibility !== Window.Maximized

        onPressed: (mouse) => {
            mouse.accepted = false
        }

        DragHandler {
            grabPermissions: TapHandler.TakeOverForbidden
            target: null
            onActiveChanged: if (active) { window.startSystemResize(Qt.TopEdge) }
        }
    }

    // Bottom edge
    MouseArea {
        height: edgeSize / 2
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.leftMargin: edgeSize * 2
        anchors.rightMargin: edgeSize * 2
        cursorShape: Qt.SizeVerCursor
        z: 999
        visible: window.visibility !== Window.Maximized

        onPressed: (mouse) => {
            mouse.accepted = false
        }

        DragHandler {
            grabPermissions: TapHandler.TakeOverForbidden
            target: null
            onActiveChanged: if (active) { window.startSystemResize(Qt.BottomEdge) }
        }
    }

    // Left edge
    MouseArea {
        width: edgeSize / 2
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.topMargin: edgeSize
        anchors.bottomMargin: edgeSize * 2
        cursorShape: Qt.SizeHorCursor
        z: 999
        visible: window.visibility !== Window.Maximized

        onPressed: (mouse) => {
            mouse.accepted = false
        }

        DragHandler {
            grabPermissions: TapHandler.TakeOverForbidden
            target: null
            onActiveChanged: if (active) { window.startSystemResize(Qt.LeftEdge) }
        }
    }

    // Right edge
    MouseArea {
        width: edgeSize / 2
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: edgeSize
        anchors.bottomMargin: edgeSize * 2
        cursorShape: Qt.SizeHorCursor
        z: 999
        visible: window.visibility !== Window.Maximized

        onPressed: (mouse) => {
            mouse.accepted = false
        }

        DragHandler {
            grabPermissions: TapHandler.TakeOverForbidden
            target: null
            onActiveChanged: if (active) { window.startSystemResize(Qt.RightEdge) }
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

    Components.ConverterPage {
        id: converterPage
        anchors.fill: parent
        anchors.margins: edgeSize
    }

    Component {
        id: messageBox
        Components.MessageBox {
        }
    }
}