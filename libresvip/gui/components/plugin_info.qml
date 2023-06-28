import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

GridLayout {
    property var info
    rows: 10
    columns: 10

    Image {
        Layout.row: 0
        Layout.column: 0
        Layout.rowSpan: 3
        Layout.columnSpan: 3
        sourceSize.width: 100
        sourceSize.height: 100
        source: info.icon_base64
        fillMode: Image.PreserveAspectFit
        BorderImage {
            source: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAACYElEQVR4nO2dW3KDMBAEJd//zspHCspgAXqstAN0H8COujPYuCpOTCml8ABijPEJZ7nFIWKM0eqx1M8rF8RSfilKDiSCeEQ4wtuHaxClEHu8vLgEUQ6xZ7afqUHuFGLPLE9Tgtw5xJ7RvoYGeVKIPaO8fUY8aAjPjhHCuPOZL+TpIXJYOjRdyBtjhGB7brMgb42xYHV+kyBvj7Fg4aE7CDG29ProCkKMPD1emoMQ45xWP01BiFFGi6fqIMSoo9ZXVRBitFHjrTgIMfoo9TfssyxooygI67ChxONlEGLYcuWTS5YYp0FYxxjOvLIQMQ6DsI6xHPllIWJkg7COOeQ8sxAxfoKwjrnsfbMQMTZBWIcP395ZiBgEEWMNwuXKl8U/CxGDIGIQRAyCqOH9V6ewhYWIQRAxCCIGQcQgiBgEEYMgYhAE4BTu1LXgkiUGQcQgiBgEEYMgYhBEDIKIQRAxPiFwc6hCSimxEDEIIgZBxCCIGGsQXth9WfyzEDEIIsYmCJctH769sxAxfoKwkrnsfbMQMbJBWMkccp5ZiBiHQVjJWI78shAxToOwkjGceWUhYlwGYSW2XPksWghRbCjxyCVLjOIgrKSPUn9VCyFKGzXeqi9ZRKmj1lfTawhRymjx1PyiTpRzWv10vcsiSp4eL91ve4mypdeHyX0IUf6x8GB2Y/j2KFbnN71Tf2sUy3Ob/4P79YFf8LWzI9wN+yzr6WsZ9os8Q9yT1jLa15Qg65PdOMwsT1ODrE96ozCz/bgEWZ9cOIyXF9cg6w8hFMbbh0SQbzziKDmQC5LDMpL6ef8AbMk4aED3PSgAAAAASUVORK5CYII="
        }
    }

    Label {
        Layout.row: 0
        Layout.column: 3
        Layout.columnSpan: 7
        text: info.name
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
                text: py.qta.icon("mdi6.tag")
                font.family: materialFontLoader.name
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
                text: py.qta.icon("mdi6.account")
                font.family: materialFontLoader.name
            }

            Label {
                text: info.author
                font.underline: true
                HoverHandler {
                    acceptedDevices: PointerDevice.AllPointerTypes
                    cursorShape: Qt.PointingHandCursor
                }
            }

            Label {
                text: py.qta.icon("mdi6.open-in-new")
                font.family: materialFontLoader.name
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
            text: py.qta.icon("mdi6.file-outline")
            font.family: materialFontLoader.name
        }
        Label {
            text: qsTr(info.format_desc)
        }
    }

    Rectangle {
        Layout.row: 3
        Layout.column: 0
        Layout.columnSpan: 10
        Layout.fillWidth: true
        height: 1
        color: Material.color(Material.Gray, Material.Shade0)
        border.color: Material.color(
            Material.Black,
            Material.Shade0
        )
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