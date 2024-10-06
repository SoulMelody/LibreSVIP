import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import LibreSVIP

MenuItem {
    property string icon_name: ""
    property string label: ""
    contentItem: Row {
        Label {
            text: iconicFontLoader.icon(icon_name)
            font.family: "Material Design Icons"
            font.pixelSize: Qt.application.font.pixelSize * 1.2
            width: 35
            anchors.verticalCenter: parent.verticalCenter
        }
        Label {
            text: label
            width: parent.width - 35
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
