import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Controls.Material.impl

RoundButton {
    id: iconButton
    property string icon_name: ""
    property double icon_size_multiplier: 1.2
    property double diameter: 36
    property int cursor_shape: Qt.PointingHandCursor

    width: diameter
    height: diameter

    contentItem: Label {
        anchors.centerIn: parent
        anchors.margins: 0
        text: py.qta.icon(icon_name)
        font.family: "Material Design Icons"
        font.pixelSize: diameter * 0.6
    }

    background: Rectangle {
        anchors.centerIn: parent
        width: diameter
        height: diameter
        radius: diameter / 2
        color: iconButton.Material.buttonColor(iconButton.Material.theme, iconButton.Material.background,
            iconButton.Material.accent, iconButton.enabled, iconButton.flat, iconButton.highlighted, iconButton.checked)
        HoverHandler {
            acceptedDevices: PointerDevice.AllPointerTypes
            cursorShape: cursor_shape
        }
        layer.enabled: iconButton.enabled && color.a > 0 && !iconButton.flat
        layer.effect: RoundedElevationEffect {
            elevation: iconButton.Material.elevation
            roundedScale: iconButton.background.radius
        }
    }
}