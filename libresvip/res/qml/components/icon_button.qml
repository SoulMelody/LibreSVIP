import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Controls.Material.impl

RoundButton {
    id: iconButton
    property string icon_name: ""
    property string accessibleName: ""
    property string accessibleDescription: ""
    property double diameter: 36
    property int cursor_shape: Qt.PointingHandCursor

    Accessible.role: Accessible.Button
    Accessible.name: iconButton.accessibleName
    Accessible.description: iconButton.accessibleDescription

    padding: 0
    topInset: 0
    bottomInset: 0
    leftInset: 0
    rightInset: 0
    background: null

    contentItem: Item {
        implicitWidth: Math.max(iconButton.diameter, Theme.minClickSize)
        implicitHeight: implicitWidth

        Rectangle {
            id: face
            anchors.centerIn: parent
            width: Math.min(iconButton.diameter, parent.width)
            height: width
            radius: width / 2
            color: iconButton.Material.buttonColor(iconButton.Material.theme, iconButton.Material.background, iconButton.Material.accent, iconButton.enabled, iconButton.flat, iconButton.highlighted, iconButton.checked)
            layer.enabled: iconButton.enabled && color.a > 0 && !iconButton.flat
            layer.effect: RoundedElevationEffect {
                elevation: iconButton.Material.elevation
                roundedScale: face.radius
            }
        }

        HoverHandler {
            acceptedDevices: PointerDevice.AllPointerTypes
            cursorShape: iconButton.cursor_shape
        }

        Label {
            anchors.centerIn: parent
            text: iconicFontLoader.icon(iconButton.icon_name)
            font.family: "Material Design Icons"
            font.pixelSize: Math.round(iconButton.diameter * 0.5)
            color: iconButton.Material.foreground
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }
}
