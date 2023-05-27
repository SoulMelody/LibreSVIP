import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material

RoundButton {
    id: iconButton
    property string icon_name: ""
    property double icon_size_multiplier: 1.2
    property double diameter: 35
    property int cursor_shape: Qt.PointingHandCursor

    width: diameter
    height: diameter

    contentItem: Label {
        anchors.centerIn: parent
        text: py.qta.icon(icon_name)
        font.family: materialFontLoader.name
        font.pixelSize: Qt.application.font.pixelSize * icon_size_multiplier
    }

    background: Rectangle {
        anchors.centerIn: parent
        width: diameter
        height: diameter
        radius: diameter / 2
        color: iconButton.hovered ? Material.color(
            Material.Grey, iconButton.pressed ? Material.Shade400 : Material.Shade300
        ) : "transparent"
        HoverHandler {
            acceptedDevices: PointerDevice.AllPointerTypes
            cursorShape: cursor_shape
        }
    }
}