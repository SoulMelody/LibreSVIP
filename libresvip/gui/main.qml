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

        Image {
            id: img_cache
            visible: false
            anchors.fill: parent
        }

        Canvas {
            id: canvas
            anchors.fill: parent
            property int centerX: width / 2
            property int centerY: height / 2
            property real radius: 0
            property int maxRadius: 0
            property url imageUrl
            Behavior on radius {
                id: anim_radius
                NumberAnimation {
                    target: canvas
                    property: "radius"
                    duration: 666
                    easing.type: Easing.OutCubic
                }
            }
            onRadiusChanged: {
                canvas.requestPaint()
            }
            onPaint: {
                var ctx = canvas.getContext("2d");
                ctx.setTransform(1, 0, 0, 1, 0, 0);
                ctx.clearRect(0, 0, canvasSize.width, canvasSize.height);
                ctx.save()
                if( img_cache.source.toString().length!==0){
                    try {
                        ctx.drawImage(img_cache, 0, 0,  canvasSize.width, canvasSize.height, 0, 0,  canvasSize.width, canvasSize.height)
                    } catch(e) {
                        img_cache.source = ""
                    }
                }
                clearArc(ctx, centerX, centerY, radius)
                ctx.restore()
            }
            function clearArc(ctx,x, y, radius, startAngle, endAngle) {
                ctx.beginPath()
                ctx.globalCompositeOperation = 'destination-out'
                ctx.fillStyle = 'black'
                ctx.arc(x, y, radius, 0, 2*Math.PI);
                ctx.fill();
                ctx.closePath();
            }
        }

    }

    Component {
        id: messageBox
        Components.MessageBox {
        }
    }

    function distance(x1, y1, x2, y2){
        return Math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
    }

    function handleThemeChange(theme){
        // Adapted from https://github.com/zhuzichu520/FluentUI/blob/main/example/qml/window/MainWindow.qml
        var target = converterPage
        var pos = toolbar.themesBtn.mapToItem(target, 0, 0)
        var mouseX = pos.x
        var mouseY = pos.y
        canvas.maxRadius = Math.max(
            distance(mouseX, mouseY, 0, 0),
            distance(mouseX, mouseY, target.width, 0),
            distance(mouseX, mouseY, 0, target.height),
            distance(mouseX, mouseY, target.width, target.height)
        )
        target.grabToImage(
            (result) => {
                img_cache.source = result.url
                canvas.requestPaint()
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
                canvas.centerX = mouseX
                canvas.centerY = mouseY
                anim_radius.enabled = false
                canvas.radius = 0
                anim_radius.enabled = true
                canvas.radius = canvas.maxRadius
            }, canvas.canvasSize
        )
    }
}