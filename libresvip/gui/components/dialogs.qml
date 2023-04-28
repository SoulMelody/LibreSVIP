import QtQuick
import QtQuick.Window
import QtQuick.Controls as QQC2
import QtQuick.Dialogs

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

    property QtObject aboutDialog: QQC2.Dialog {
        title: qsTr("About")
        x: window.width / 2 - width / 2
        y: window.height / 2 - height / 2
        standardButtons: QQC2.Dialog.Ok
    }
}