import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

Dialog {
    id: detailDialog
    property string heading: ""
    property string detailText: ""
    property string copyText: qsTr("Copy message")
    property alias textEdit: detailEdit

    parent: Overlay.overlay
    modal: true
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
    width: Math.max(1, Math.min(640, parent ? parent.width - 64 : 1))
    height: Math.max(1, Math.min(420, parent ? parent.height - 64 : 1))
    x: Math.max(0, (parent.width - width) / 2)
    y: Math.max(0, (parent.height - height) / 2)
    padding: 16

    onOpened: textEdit.forceActiveFocus()

    Overlay.modal: Rectangle {
        color: Material.backgroundDimColor
    }

    contentItem: ColumnLayout {
        spacing: 12

        Label {
            Layout.fillWidth: true
            text: detailDialog.heading
            wrapMode: Text.Wrap
            font.bold: true
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 6
            color: "transparent"
            border.width: 1
            border.color: Theme.colorBorder

            Flickable {
                id: detailFlickable
                anchors.fill: parent
                anchors.margins: 8
                clip: true
                contentWidth: width
                contentHeight: detailEdit.contentHeight
                boundsBehavior: Flickable.StopAtBounds

                TextEdit {
                    id: detailEdit
                    property real contentHeight: paintedHeight
                    width: detailFlickable.width
                    text: detailDialog.detailText
                    readOnly: true
                    selectByMouse: true
                    selectByKeyboard: true
                    activeFocusOnPress: true
                    wrapMode: TextEdit.Wrap
                    textFormat: TextEdit.PlainText
                    color: Material.foreground
                }

                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Item {
                Layout.fillWidth: true
            }

            Button {
                id: copyButton
                Accessible.name: detailDialog.copyText
                text: detailDialog.copyText
                onClicked: {
                    if (clipboard.set_clipboard(detailDialog.detailText)) {
                        text = qsTr("Copied");
                        resetCopyButtonTimer.start();
                    }
                }

                Timer {
                    id: resetCopyButtonTimer
                    interval: 1000
                    repeat: false
                    triggeredOnStart: false
                    onTriggered: {
                        copyButton.text = detailDialog.copyText;
                    }
                }
            }

            Button {
                id: closeButton
                Accessible.name: qsTr("Close")
                flat: true
                text: qsTr("Close")
                onClicked: detailDialog.close()
            }
        }
    }
}
