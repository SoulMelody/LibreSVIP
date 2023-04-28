import QtQuick
import QtQuick.Window
import QtQuick.Controls as QQC2
import QtQuick.Dialogs
import QtQuick.Layouts

Item {
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
            py.task_manager.add_task(
                py.task_manager.fill_task(url2path(selectedFiles[0]))
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
            converterPage.saveFolder.text = url2path(selectedFolder)
        }
    }

    property QtObject errorDialog: QQC2.Dialog {
        title: qsTr("Error")
        standardButtons: QQC2.Dialog.Ok
        x: window.width / 2 - width / 2
        y: window.height / 2 - height / 2
        RowLayout {
            QQC2.Label {
                text: py.qta.icon("mdi6.alert-circle")
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
    }
}