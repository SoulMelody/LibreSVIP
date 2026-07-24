import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

Column {
    id: root

    property string title: ""
    property string subtitle: ""
    property bool expanded: true
    property alias headerExtras: headerExtrasRow.data
    default property alias content: bodyColumn.data

    width: parent ? parent.width : implicitWidth
    spacing: Theme.spacingXS

    RowLayout {
        width: root.width
        height: Theme.minClickSize
        spacing: Theme.spacingXS

        RoundButton {
            Accessible.name: qsTr(root.expanded ? "Collapse" : "Expand")
            Accessible.role: Accessible.Button
            width: Theme.minClickSize
            height: Theme.minClickSize
            radius: height / 2
            background: Rectangle {
                color: "transparent"
            }
            contentItem: Label {
                text: iconicFontLoader.icon("mdi7.chevron-right")
                font.family: "Material Design Icons"
                font.pixelSize: 16
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                rotation: root.expanded ? 45 : 0
                Behavior on rotation {
                    RotationAnimation {
                        duration: 220
                        easing.type: Easing.InOutQuad
                    }
                }
            }
            onClicked: root.expanded = !root.expanded
        }

        Label {
            text: root.title
            font.pixelSize: 22
            Layout.alignment: Qt.AlignVCenter
        }

        Label {
            text: root.subtitle
            visible: root.subtitle !== ""
            color: Theme.colorMutedText
            font.pixelSize: 16
            Layout.alignment: Qt.AlignVCenter
        }

        Item {
            Layout.fillWidth: true
        }

        Row {
            id: headerExtrasRow
            spacing: Theme.spacingXS
            Layout.alignment: Qt.AlignVCenter
        }
    }

    Item {
        id: clipper
        width: root.width
        height: root.expanded ? bodyColumn.implicitHeight : 0
        clip: true
        Behavior on height {
            NumberAnimation {
                duration: 260
                easing.type: Easing.InOutQuad
            }
        }

        ColumnLayout {
            id: bodyColumn
            x: Theme.spacingL
            width: Math.max(0, clipper.width - Theme.spacingL - Theme.spacingM)
        }
    }
}
