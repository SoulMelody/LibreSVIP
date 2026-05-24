import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import QtQuick.Effects

GridLayout {
    property var info
    rows: 10
    columns: 10

    Rectangle {
        Layout.row: 0
        Layout.column: 0
        Layout.rowSpan: 3
        Layout.columnSpan: 3
        width: 100
        height: 100
        radius: 50
        Image {
            id: logo
            anchors.fill: parent
            source: info.icon_base64
            visible: false
        }
        MultiEffect {
            anchors.fill: logo
            source: logo
            maskEnabled: true
            maskSource: maskRect
        }
        Rectangle {
            id: maskRect
            anchors.fill: parent
            width: 100
            height: 100
            radius: 50
            layer.enabled: true
            visible: false
        }
    }

    Label {
        Layout.row: 0
        Layout.column: 3
        Layout.columnSpan: 7
        text: qsTr(info.name)
        font.pixelSize: 30
        font.bold: true
    }

    Button {
        Layout.row: 1
        Layout.column: 3
        Layout.columnSpan: 3
        background: Rectangle {
            color: "transparent"
        }
        contentItem: RowLayout {
            Label {
                text: iconicFontLoader.icon("mdi7.tag")
                font.family: "Material Design Icons"
            }
            Label {
                text: info.version
            }
        }
        ToolTip {
            z: 1
            visible: parent.hovered
            text: qsTr("Version")
        }
    }

    Button {
        Layout.row: 1
        Layout.column: 6
        Layout.columnSpan: 4
        background: Rectangle {
            color: "transparent"
        }
        contentItem: RowLayout {
            Label {
                text: iconicFontLoader.icon("mdi7.account")
                font.family: "Material Design Icons"
            }

            Label {
                text: qsTr(info.author)
                font.underline: true
                HoverHandler {
                    acceptedDevices: PointerDevice.AllPointerTypes
                    cursorShape: Qt.PointingHandCursor
                }
            }

            Label {
                text: iconicFontLoader.icon("mdi7.open-in-new")
                font.family: "Material Design Icons"
            }
        }
        ToolTip {
            z: 1
            visible: parent.hovered
            text: info.website
        }
        onClicked: Qt.openUrlExternally(info.website)
    }

    RowLayout {
        Layout.row: 2
        Layout.column: 3
        Layout.columnSpan: 7
        Label {
            text: iconicFontLoader.icon("mdi7.file-outline")
            font.family: "Material Design Icons"
        }
        Label {
            text: qsTr(info.file_format) + " " + info.suffix
        }
    }

    Rectangle {
        Layout.row: 3
        Layout.column: 0
        Layout.columnSpan: 10
        Layout.fillWidth: true
        height: 1
        color: Material.color(Material.Gray, Material.Shade0)
        border.color: Material.color(Material.Black, Material.Shade0)
        border.width: 1
    }

    ColumnLayout {
        Layout.row: 4
        Layout.column: 0
        Layout.columnSpan: 10
        spacing: 10
        Label {
            text: qsTr("Introduction")
            font.bold: true
        }
        Label {
            Layout.maximumWidth: 500
            text: qsTr(info.description)
            wrapMode: Text.Wrap
        }
    }
}
