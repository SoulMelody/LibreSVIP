import QtQuick
import QtQuick.Window
import QtQuick.Controls as QQC2
import QtQuick.Dialogs
import QtQuick.Layouts

Item {
    signal save_folder_changed(string folder)

    function url2path(url) {
        let url_string = url.toString();
        switch (Qt.platform.os) {
            case "windows":
                return url_string.replace(/^(file:\/{3})/, "");
            default:
                return url_string.replace(/^(file:\/{2})/, "");
        }
    }

    property QtObject openDialog: FileDialog {
        nameFilters: ["*.*", qsTr("所有文件 (*.*)")]
        fileMode: FileDialog.OpenFiles
        currentFolder: ""
        onAccepted: {
            py.task_manager.add_task_paths(
                [url2path(selectedFiles[0])]
            )
        }
    }

    property QtObject installPluginDialog: FileDialog {
        nameFilters: [qsTr("Compressed Plugin Package (*.zip)")]
        fileMode: FileDialog.OpenFile
        currentFolder: ""
        onAccepted: {
            py.task_manager.install_plugin(url2path(selectedFile))
        }
    }

    property QtObject saveDialog: FolderDialog {
        currentFolder: ""
        onAccepted: {
            let path = url2path(selectedFolder)
            py.config_items.set_save_folder(path)
            save_folder_changed(path)
        }
    }

    property QtObject errorDialog: QQC2.Dialog {
        title: qsTr("Error")
        standardButtons: QQC2.Dialog.Ok
        x: window.width / 2 - width / 2
        y: window.height / 2 - height / 2
        RowLayout {
            QQC2.Label {
                text: py.qta.icon("mdi6.tooltip-remove-outline")
                font.family: materialFontLoader.name
                font.pixelSize: 24
            }
            QQC2.Label {
                id: errorText
                text: ""
            }
            QQC2.RoundButton {
                text: py.qta.icon("mdi6.content-copy")
                font.family: materialFontLoader.name
                radius: height / 2
                onClicked: py.clipboard.set_clipboard(errorText.text)
            }
        }
        function show_error(text) {
            errorText.text = text
            open()
        }
    }

    property QtObject aboutDialog: QQC2.Dialog {
        title: qsTr("About")
        x: window.width / 2 - width / 2
        y: window.height / 2 - height / 2
        standardButtons: QQC2.Dialog.Ok

        ColumnLayout {
            width: 400
            QQC2.Label {
                Layout.alignment: Qt.AlignHCenter
                text: qsTr("LibreSVIP")
                font.pixelSize: 48
                font.bold: true
            }
            QQC2.Label {
                Layout.alignment: Qt.AlignHCenter
                text: qsTr("Version: 0.1.0")
            }
            QQC2.Label {
                Layout.alignment: Qt.AlignHCenter
                text: qsTr("Author: SoulMelody")
            }
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                QQC2.Button {
                    contentItem: RowLayout {
                        QQC2.Label {
                            text: py.qta.icon("mdi6.account-circle")
                            font.family: materialFontLoader.name
                        }
                        QQC2.Label {
                            text: qsTr("Author's Profile")
                        }
                    }
                    onClicked: {
                        Qt.openUrlExternally("https://space.bilibili.com/175862486")
                    }
                }
                QQC2.Button {
                    contentItem: RowLayout {
                        QQC2.Label {
                            text: py.qta.icon("mdi6.github")
                            font.family: materialFontLoader.name
                        }
                        QQC2.Label {
                            text: qsTr("Repo URL")
                        }
                    }
                    onClicked: {
                        Qt.openUrlExternally("https://github.com/SoulMelody/LibreSVIP")
                    }
                }
            }
            QQC2.Label {
                Layout.preferredWidth: parent.width
                text: qsTr("LibreSVIP 是一个开源、开放、插件化的歌声合成工程文件中介与转换平台。")
                wrapMode: Text.WordWrap
            }
            QQC2.Label {
                Layout.preferredWidth: parent.width
                text: qsTr("所有人都应享有选择的权利和自由。因此，我们致力于为您带来第二次机会，使您的创作免受平台的制约与圈子的束缚。")
                wrapMode: Text.WordWrap
            }
        }
    }
}