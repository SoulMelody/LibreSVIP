import QtQuick
import QtQuick.Window
import QtQuick.Controls.Material as QQC2
import QtQuick.Dialogs
import QtQuick.Layouts

Item {
    signal save_folder_changed(string folder)
    property alias folderPresetsList: folderPresetsListView
    property alias folderPresetBtnGroup: folderPresetButtonGroup

    Component {
        id: folderPresetDelegate
        Rectangle {
            Layout.fillWidth: true
            width: 600
            height: 45
            color: folderPresetsListView.currentIndex === index ? QQC2.Material.listHighlightColor : "transparent"
            RowLayout {
                id: folderPresetRow
                anchors.fill: parent
                QQC2.RadioButton {
                    QQC2.ButtonGroup.group: folderPresetButtonGroup
                    checked: folderPresetsListView.currentIndex === index
                    onClicked: {
                        folderPresetsListView.currentIndex = index
                    }
                }
                IconButton {
                    icon_name: "mdi6.folder"
                    diameter: 38
                    icon_size_multiplier: 1.5
                    onClicked: {
                        chooseFolderDialog.choose_folder(model.path, (folder) => {
                            folderPresetsListView.model.update(index, {path: folder})
                        })
                    }
                }
                QQC2.TextField {
                    id: pathTextField
                    Layout.preferredWidth: 400
                    text: model.path
                    Rectangle {
                        anchors.left: parent.left
                        anchors.leftMargin: 50
                        anchors.verticalCenter: parent.verticalCenter
                        visible: pathTextField.length == 0
                        width: 18
                        height: 18
                        color: "transparent"
                        QQC2.Label {
                            anchors.centerIn: parent
                            text: qsTr("Custom folder")
                            color: QQC2.Material.color(QQC2.Material.Grey, QQC2.Material.Shade500)
                        }
                    }
                    Rectangle {
                        anchors.right: parent.right
                        anchors.rightMargin: 10
                        anchors.verticalCenter: parent.verticalCenter
                        visible: pathTextField.length > 0
                        width: 18
                        height: 18
                        radius: width / 2
                        color: QQC2.Material.color(QQC2.Material.Grey, QQC2.Material.Shade500)
                        QQC2.Label {
                            z: 1
                            anchors.centerIn: parent
                            text: py.qta.icon("mdi6.close")
                            font.family: materialFontLoader.name
                            HoverHandler {
                                acceptedDevices: PointerDevice.AllPointerTypes
                                cursorShape: Qt.PointingHandCursor
                            }
                            TapHandler {
                                onTapped: {
                                    folderPresetsListView.model.update(index, {path: ""})
                                }
                            }
                        }
                    }
                }
                IconButton {
                    icon_name: "mdi6.trash-can-outline"
                    diameter: 38
                    icon_size_multiplier: 1.5
                    onClicked: {
                        folderPresetsListView.model.delete(index)
                    }
                }
            }
        }
    }

    function url2path(url) {
        let url_string = url.toString();
        switch (Qt.platform.os) {
            case "windows":
                return url_string.replace(/^(file:\/{3})/, "");
            default:
                return url_string.replace(/^(file:\/{2})/, "");
        }
    }

    function path2url(path) {
        if (path.length == 0 || path.startsWith(".")) {
            return ""
        }
        switch (Qt.platform.os) {
            case "windows":
                return "file:///" + path;
            default:
                return "file://" + path;
        }
    }

    property QtObject openDialog: FileDialog {
        nameFilters: ["*.*", qsTr("All Files (*.*)")]
        fileMode: FileDialog.OpenFiles
        currentFolder: ""
        onAccepted: {
            py.task_manager.add_task_paths(
                selectedFiles.map(url2path)
            )
        }
    }

    property QtObject confirmInstallDialog: QQC2.Dialog {
        title: qsTr("Install New Plugins")
        x: window.width / 2 - width / 2
        y: window.height / 2 - height / 2
        property var plugin_infos: []
        standardButtons: QQC2.Dialog.Ok | QQC2.Dialog.Cancel

        ColumnLayout {
            width: 400
            QQC2.Label {
                text: qsTr("Are you sure to install following plugins?")
            }
            Repeater {
                model: confirmInstallDialog.plugin_infos
                QQC2.Label {
                    Layout.alignment: Qt.AlignHCenter
                    text: qsTr("Developed by ") + modelData.author + qsTr(", which supports ") + qsTr(modelData.format_desc)
                }
            }
        }
        onAccepted: {
            py.task_manager.install_plugins(plugin_infos)
        }
        function show_dialog(plugin_infos) {
            this.plugin_infos = plugin_infos
            open()
        }
    }

    property QtObject installPluginDialog: FileDialog {
        nameFilters: [qsTr("Compressed Plugin Package (*.zip)")]
        fileMode: FileDialog.OpenFiles
        currentFolder: ""
        onAccepted: {
            let plugin_infos = py.task_manager.extract_plugin_infos(selectedFiles.map(
                url2path
            ))
            if (plugin_infos.length > 0) {
                confirmInstallDialog.show_dialog(plugin_infos)
            }
        }
    }

    property QtObject saveDialog: FolderDialog {
        currentFolder: ""
        onAccepted: {
            let path = url2path(selectedFolder)
            py.config_items.set_save_folder(path)
            save_folder_changed(path)
        }
        onRejected: {
            save_folder_changed(py.config_items.get_save_folder())
        }
    }

    property QtObject chooseFolderDialog: FolderDialog {
        property var accept_callback: (value) => {}
        currentFolder: ""
        onAccepted: {
            accept_callback(url2path(selectedFolder))
        }
        function choose_folder(start_folder, callback) {
            currentFolder = path2url(start_folder)
            accept_callback = callback
            open()
        }
    }

    property QtObject folderPresetsDialog: QQC2.Dialog {
        x: window.width / 2 - width / 2
        y: window.height / 2 - height / 2
        width: 700
        height: 500
        header: ColumnLayout {
            Layout.fillWidth: true
            RowLayout {
                Layout.fillWidth: true
                QQC2.Label {
                    text: qsTr("Folder Presets")
                    font.bold: true
                    Layout.fillWidth: true
                }
                IconButton {
                    Layout.alignment: Qt.AlignRight
                    icon_name: "mdi6.close"
                    diameter: 30
                    icon_size_multiplier: 1.5
                    onClicked: folderPresetsDialog.close()
                }
            }
            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: "#ccc"
            }
        }
        Rectangle {
            width: 500
            height: 400
            x: parent.width / 2 - width / 2
            ColumnLayout {
                x: -50
                Layout.fillWidth: true
                Layout.fillHeight: true
                visible: folderPresetsListView.count > 0
                QQC2.Label {
                    text: qsTr(
                        "You can insert " + '"."' + " at the beginning to represent the source path, for example " + '"./subfolder"'
                    )
                    wrapMode: Text.Wrap
                }
                QQC2.ButtonGroup {
                    id: folderPresetButtonGroup
                    exclusive: true
                }
                QQC2.ScrollView {
                    clip: true
                    id: folderPresetsScrollView
                    Layout.minimumHeight: 300
                    Layout.maximumHeight: 300
                    width: 600
                    contentWidth: availableWidth
                    ListView {
                        id: folderPresetsListView
                        model: py.config_items.qget("folder_presets")
                        delegate: folderPresetDelegate
                        Component.onCompleted: {
                            let save_folder = py.config_items.get_save_folder()
                            if (count > 0) {
                                for (let i = 0; i < count; i++) {
                                    if (model.get(i).path == save_folder) {
                                        currentIndex = i
                                        break
                                    }
                                }
                            }
                            save_folder_changed(save_folder)
                        }
                    }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: "transparent"
                    }
                    QQC2.Button {
                        Layout.alignment: Qt.AlignHCenter
                        text: py.qta.icon("mdi6.plus")
                        font.family: materialFontLoader.name
                        font.pixelSize: Qt.application.font.pixelSize * 1.5
                        onClicked: {
                            folderPresetsListView.model.append({
                                "path": ""
                            })
                        }
                    }
                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: "transparent"
                    }
                }
            }
            Rectangle {
                anchors.fill: parent
                visible: folderPresetsListView.count == 0
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: {
                        if (folderPresetsListView.count == 0) {
                            parent.opacity = 0.5
                        }
                    }
                    onExited: {
                        if (parent.opacity < 1) {
                            parent.opacity = 1
                        }
                    }
                    onClicked: {
                        if (folderPresetsListView.count == 0) {
                            folderPresetsListView.model.append({
                                "path": ""
                            })
                        }
                    }
                    Column {
                        anchors.centerIn: parent
                        QQC2.Label {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: py.qta.icon("mdi6.folder-plus-outline")
                            font.family: materialFontLoader.name
                            font.pixelSize: 100
                        }
                        QQC2.Label {
                            text: qsTr("Click to add a folder preset")
                            font.pixelSize: 30
                        }
                    }
                }
            }
        }
    }

    property QtObject colorDialog: ColorDialog {
        property var accept_callback: (value) => {}
        onAccepted: {
            accept_callback(selectedColor)
        }
        function bind_color(color_value, callback) {
            selectedColor = color_value
            accept_callback = callback
            open()
        }
    }

    property QtObject aboutDialog: QQC2.Dialog {
        title: qsTr("About")
        x: window.width / 2 - width / 2
        y: window.height / 2 - height / 2
        standardButtons: QQC2.Dialog.Ok

        ColumnLayout {
            QQC2.Label {
                Layout.alignment: Qt.AlignHCenter
                text: qsTr("LibreSVIP")
                font.pixelSize: 48
                font.bold: true
            }
            QQC2.Label {
                Layout.alignment: Qt.AlignHCenter
                text: qsTr("Version: " + py.config_items.get_version())
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
                            text: py.qta.icon("ri.bilibili-line")
                            font.family: remixFontLoader.name
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
                text: qsTr("LibreSVIP is an open-sourced, liberal and extensionable framework that can convert your singing synthesis projects between different file formats.")
                wrapMode: Text.WordWrap
            }
            QQC2.Label {
                Layout.preferredWidth: parent.width
                text: qsTr("All people should have the right and freedom to choose. That's why we're committed to giving you a second chance to keep your creations free from the constraints of platforms and coterie.")
                wrapMode: Text.WordWrap
            }
        }
    }
}