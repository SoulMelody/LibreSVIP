import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material as QQC2
import QtQuick.Dialogs
import QtQuick.Layouts
import LibreSVIP

Item {
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
                        folderPresetsListView.currentIndex = index;
                    }
                }
                IconButton {
                    icon_name: "mdi7.folder"
                    diameter: 38
                    onClicked: {
                        chooseFolderDialog.choose_folder(model.path, folder => {
                            folderPresetsListView.model.update(index, {
                                path: folder
                            });
                        });
                    }
                }
                QQC2.TextField {
                    id: pathTextField
                    property string previousText: ""
                    Layout.preferredWidth: 400
                    text: model.path
                    onEditingFinished: {
                        if (configItems.dir_valid(text) === false) {
                            undo();
                        } else {
                            folderPresetsListView.model.update(index, {
                                path: text
                            });
                        }
                    }
                    Rectangle {
                        anchors.left: parent.left
                        anchors.leftMargin: 10
                        anchors.verticalCenter: parent.verticalCenter
                        visible: pathTextField.length == 0
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: "transparent"
                        QQC2.Label {
                            anchors.verticalCenter: parent.verticalCenter
                            text: qsTr("Custom folder")
                            color: QQC2.Material.color(QQC2.Material.Grey, QQC2.Material.Shade500)
                        }
                    }
                    Rectangle {
                        anchors.right: parent.right
                        anchors.rightMargin: 10
                        anchors.verticalCenter: parent.verticalCenter
                        visible: pathTextField.length > 0 && (pathTextField.activeFocus || pathTextField.hovered)
                        width: 18
                        height: 18
                        radius: width / 2
                        color: QQC2.Material.color(QQC2.Material.Grey, QQC2.Material.Shade500)
                        QQC2.Label {
                            z: 1
                            anchors.centerIn: parent
                            text: iconicFontLoader.icon("mdi7.close")
                            font.family: "Material Design Icons"
                            HoverHandler {
                                acceptedDevices: PointerDevice.AllPointerTypes
                                cursorShape: Qt.PointingHandCursor
                            }
                            TapHandler {
                                onTapped: {
                                    folderPresetsListView.model.update(index, {
                                        path: ""
                                    });
                                }
                            }
                        }
                    }
                }
                IconButton {
                    icon_name: "mdi7.trash-can-outline"
                    diameter: 38
                    onClicked: {
                        folderPresetsListView.model.delete(index);
                    }
                }
            }
        }
    }

    function url2path(url) {
        let url_string = unescape(url.toString());
        switch (Qt.platform.os) {
        case "windows":
            return url_string.replace(/^(file:\/{3})/, "");
        default:
            return url_string.replace(/^(file:\/{2})/, "");
        }
    }

    function path2url(path) {
        if (path.length == 0 || path.startsWith(".")) {
            return "";
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
            taskManager.add_task_paths(selectedFiles.map(url2path));
        }
    }

    property QtObject saveDialog: FolderDialog {
        currentFolder: ""
        onAccepted: {
            let path = url2path(selectedFolder);
            configItems.save_folder = path;
        }
        onRejected: {}
    }

    property QtObject chooseFolderDialog: FolderDialog {
        property var accept_callback: value => {}
        currentFolder: ""
        onAccepted: {
            accept_callback(url2path(selectedFolder));
        }
        function choose_folder(start_folder, callback) {
            currentFolder = path2url(start_folder);
            accept_callback = callback;
            open();
        }
    }

    property QtObject folderPresetsDialog: QQC2.Dialog {
        x: window.width / 2 - width / 2
        y: window.height / 2 - height / 2
        width: 700
        height: 500
        Overlay.modal: Rectangle {
            anchors.fill: parent
            anchors.topMargin: toolbar.height
            color: Material.backgroundDimColor
        }
        header: ColumnLayout {
            Layout.fillWidth: true
            RowLayout {
                Layout.fillWidth: true
                Rectangle {
                    Layout.fillHeight: true
                    width: 15
                    color: "transparent"
                }
                QQC2.Label {
                    text: qsTr("Folder Presets")
                    font.bold: true
                    font.pixelSize: 20
                    Layout.fillWidth: true
                }
                IconButton {
                    Layout.alignment: Qt.AlignRight
                    icon_name: "mdi7.close"
                    diameter: 30
                    new_padding: 6
                    onClicked: folderPresetsDialog.close()
                }
                Rectangle {
                    Layout.fillHeight: true
                    width: 10
                    color: "transparent"
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
            color: "transparent"
            ColumnLayout {
                x: -50
                Layout.fillWidth: true
                Layout.fillHeight: true
                visible: folderPresetsListView.count > 0
                QQC2.Label {
                    text: qsTr("You can insert " + '"."' + " at the beginning to represent the source path, for example " + '"./subfolder"')
                    wrapMode: Text.Wrap
                }
                QQC2.ButtonGroup {
                    id: folderPresetButtonGroup
                    exclusive: true
                }
                QQC2.ScrollView {
                    id: folderPresetsScrollView
                    clip: true
                    Layout.minimumHeight: 300
                    Layout.maximumHeight: 300
                    width: 600
                    contentWidth: availableWidth
                    ListView {
                        id: folderPresetsListView
                        model: configItems.qget("folder_presets")
                        delegate: folderPresetDelegate
                        Component.onCompleted: {
                            let save_folder = configItems.save_folder;
                            if (count > 0) {
                                for (let i = 0; i < count; i++) {
                                    if (model.get(i).path == save_folder) {
                                        currentIndex = i;
                                        break;
                                    }
                                }
                            }
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
                        text: iconicFontLoader.icon("mdi7.plus")
                        font.family: "Material Design Icons"
                        font.pixelSize: Qt.application.font.pixelSize * 1.5
                        onClicked: {
                            folderPresetsListView.model.append({
                                "path": ""
                            });
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
                            parent.opacity = 0.5;
                        }
                    }
                    onExited: {
                        if (parent.opacity < 1) {
                            parent.opacity = 1;
                        }
                    }
                    onClicked: {
                        if (folderPresetsListView.count == 0) {
                            folderPresetsListView.model.append({
                                "path": ""
                            });
                        }
                    }
                    Column {
                        anchors.centerIn: parent
                        QQC2.Label {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: iconicFontLoader.icon("mdi7.folder-plus-outline")
                            font.family: "Material Design Icons"
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
        property var accept_callback: value => {}
        onAccepted: {
            accept_callback(selectedColor);
        }
        function bind_color(color_value, callback) {
            selectedColor = color_value;
            accept_callback = callback;
            open();
        }
    }

    property QtObject aboutDialog: QQC2.Dialog {
        title: qsTr("About")
        x: window.width / 2 - width / 2
        y: window.height / 2 - height / 2
        standardButtons: QQC2.Dialog.Ok
        Overlay.modal: Rectangle {
            anchors.fill: parent
            anchors.topMargin: toolbar.height
            color: Material.backgroundDimColor
        }

        ColumnLayout {
            QQC2.Label {
                Layout.alignment: Qt.AlignHCenter
                text: qsTr("LibreSVIP")
                font.pixelSize: 48
                font.bold: true
            }
            QQC2.Label {
                Layout.alignment: Qt.AlignHCenter
                text: qsTr("Version: ") + configItems.version
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
                            text: iconicFontLoader.icon("mdi7.television-classic")
                            font.family: "Material Design Icons"
                        }
                        QQC2.Label {
                            text: qsTr("Author's Profile")
                        }
                    }
                    onClicked: {
                        Qt.openUrlExternally("https://space.bilibili.com/175862486");
                    }
                }
                QQC2.Button {
                    contentItem: RowLayout {
                        QQC2.Label {
                            text: iconicFontLoader.icon("mdi7.github")
                            font.family: "Material Design Icons"
                        }
                        QQC2.Label {
                            text: qsTr("Repo URL")
                        }
                    }
                    onClicked: {
                        Qt.openUrlExternally("https://github.com/SoulMelody/LibreSVIP");
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

    property QtObject settingsDialog: SettingsDialog {
        Overlay.modal: Rectangle {
            anchors.fill: parent
            anchors.topMargin: toolbar.height
            color: Material.backgroundDimColor
        }
    }
}
