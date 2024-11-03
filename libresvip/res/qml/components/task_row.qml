import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import LibreSVIP

ColumnLayout {
    id: taskRow
    required property string name
    required property string path
    required property string stem
    required property string ext
    required property int index
    width: converterPage.taskList.width
    height: 45

    RowLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true
        RowLayout {
            Layout.fillWidth: true
            Column {
                Layout.fillWidth: true
                Label {
                    width: parent.width
                    text: name
                    elide: Text.ElideRight
                    font.bold: true
                    font.pixelSize: Qt.application.font.pixelSize * 1.2
                }
                Label {
                    width: parent.width
                    text: path
                    elide: Text.ElideRight
                }
            }
            Label {
                text: taskManager.conversion_mode === "Merge" && index !== 0 ? iconicFontLoader.icon("mdi7.transfer-up") : iconicFontLoader.icon("mdi7.transfer-right")
                font.family: "Material Design Icons"
                font.pixelSize: Qt.application.font.pixelSize * 1.5
            }
        }
        RowLayout {
            Layout.preferredWidth: 260
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignVCenter

            TextField {
                id: stemField
                visible: taskManager.conversion_mode === "Merge" ? index === 0 : true
                text: stem
                onEditingFinished: {
                    converterPage.taskList.model.update(index, {
                        stem: this.text
                    });
                }
            }

            Label {
                id: extLabel
                visible: taskManager.conversion_mode === "Merge" ? index === 0 : true
                text: ext
            }

            IconButton {
                id: deleteButton
                icon_name: "mdi7.trash-can-outline"
                enabled: !taskManager.busy
                onClicked: {
                    converterPage.taskList.model.delete(index);
                }
                ToolTip.visible: hovered
                ToolTip.text: qsTr("Remove")
            }

            Rectangle {
                id: statusIndicator
                height: 44
                width: height
                color: "transparent"

                RoundButton {
                    id: successButton
                    anchors.centerIn: parent
                    visible: false
                    text: iconicFontLoader.icon("mdi7.check")
                    background: Rectangle {
                        color: Material.color(Material.Green, Material.Shade300)
                        radius: parent.height / 2
                        HoverHandler {
                            acceptedDevices: PointerDevice.AllPointerTypes
                            cursorShape: Qt.PointingHandCursor
                        }
                    }
                    font.family: "Material Design Icons"
                    font.pixelSize: Qt.application.font.pixelSize * 1.2
                    height: parent.height
                    width: height
                    radius: height / 2
                    ToolTip {
                        id: successToolTip
                        contentItem: ColumnLayout {
                            Label {
                                text: qsTr("File successfully converted")
                            }
                            Button {
                                Layout.alignment: Qt.AlignHCenter
                                visible: taskManager.conversion_mode === "Split" ? false : true
                                background: Rectangle {
                                    color: Material.color(Material.Indigo, Material.Shade500)
                                }
                                contentItem: Label {
                                    text: qsTr("Open")
                                }
                                onClicked: {
                                    taskManager.open_output_path(index);
                                }
                            }
                            Button {
                                Layout.alignment: Qt.AlignHCenter
                                background: Rectangle {
                                    color: Material.color(Material.Indigo, Material.Shade500)
                                }
                                contentItem: Label {
                                    text: qsTr("Open folder")
                                }
                                onClicked: {
                                    taskManager.open_output_dir(index);
                                }
                            }
                        }
                    }
                    onClicked: {
                        successToolTip.visible = !successToolTip.visible;
                    }
                }

                RoundButton {
                    id: skipButton
                    anchors.centerIn: parent
                    visible: false
                    background: Rectangle {
                        color: Material.color(Material.Blue, Material.Shade300)
                        radius: parent.height / 2
                        HoverHandler {
                            acceptedDevices: PointerDevice.AllPointerTypes
                            cursorShape: Qt.PointingHandCursor
                        }
                    }
                    text: iconicFontLoader.icon("mdi7.minus-thick")
                    font.family: "Material Design Icons"
                    font.pixelSize: Qt.application.font.pixelSize * 1.2
                    height: parent.height
                    width: height
                    radius: height / 2
                    ToolTip {
                        id: skipToolTip
                        contentItem: ColumnLayout {
                            Label {
                                text: qsTr("File skipped due to conflict")
                            }
                            Button {
                                Layout.alignment: Qt.AlignHCenter
                                background: Rectangle {
                                    color: Material.color(Material.Indigo, Material.Shade500)
                                }
                                contentItem: Label {
                                    text: qsTr("Open folder")
                                }
                                onClicked: {
                                    taskManager.open_output_dir(index);
                                }
                            }
                        }
                    }
                    onClicked: {
                        skipToolTip.visible = !skipToolTip.visible;
                    }
                }

                RoundButton {
                    id: warningButton
                    anchors.centerIn: parent
                    visible: false
                    background: Rectangle {
                        color: Material.color(Material.Orange, Material.Shade300)
                        radius: parent.height / 2
                        HoverHandler {
                            acceptedDevices: PointerDevice.AllPointerTypes
                            cursorShape: Qt.PointingHandCursor
                        }
                    }
                    text: iconicFontLoader.icon("mdi7.alert-circle")
                    font.family: "Material Design Icons"
                    font.pixelSize: Qt.application.font.pixelSize * 1.2
                    height: parent.height
                    width: height
                    radius: height / 2
                    ToolTip {
                        id: warningToolTip
                        contentItem: ColumnLayout {
                            Label {
                                text: qsTr("This project file may contain abnormal or illegal data")
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                height: 1
                                color: Material.color(Material.Gray, Material.Shade0)
                            }
                            Label {
                                id: warningLabel
                                text: ""
                                property string warningFullText
                            }
                        }
                    }
                    onClicked: {
                        warningToolTip.visible = !warningToolTip.visible;
                    }
                }

                RoundButton {
                    id: errorButton
                    anchors.centerIn: parent
                    visible: false
                    background: Rectangle {
                        color: Material.color(Material.Red, Material.Shade300)
                        radius: parent.height / 2
                        HoverHandler {
                            acceptedDevices: PointerDevice.AllPointerTypes
                            cursorShape: Qt.PointingHandCursor
                        }
                    }
                    text: iconicFontLoader.icon("mdi7.alert-circle")
                    font.family: "Material Design Icons"
                    font.pixelSize: Qt.application.font.pixelSize * 1.2
                    height: parent.height
                    width: height
                    radius: height / 2
                    ToolTip {
                        id: errorToolTip
                        contentItem: ColumnLayout {
                            Label {
                                Layout.alignment: Qt.AlignHCenter
                                text: qsTr("File failed to convert, below is the error message:")
                            }
                            Label {
                                id: errorLabel
                                text: ""
                                property string errorFullText
                            }
                            Button {
                                id: copyErrorButton
                                Layout.alignment: Qt.AlignHCenter
                                background: Rectangle {
                                    color: Material.color(Material.Indigo, Material.Shade500)
                                }
                                text: qsTr("Copy error message")
                                onClicked: {
                                    let copy_result = clipboard.set_clipboard(errorLabel.errorFullText);
                                    if (copy_result) {
                                        text = qsTr("Copied");
                                        resetCopyErrorButtonTimer.start();
                                    }
                                }
                            }
                            Timer {
                                id: resetCopyErrorButtonTimer
                                interval: 1000
                                repeat: false
                                triggeredOnStart: false
                                onTriggered: {
                                    copyErrorButton.text = qsTr("Copy error message");
                                }
                            }
                        }
                    }
                    onClicked: {
                        errorToolTip.visible = !errorToolTip.visible;
                    }
                }
                RunningIndicator {
                    id: runningIndicator
                    anchors.centerIn: parent
                    width: 44
                    height: width
                    visible: false
                    enabled: false
                }
            }
        }
    }
    Rectangle {
        Layout.fillWidth: true
        height: 1
        color: Material.color(Material.Grey, Material.Shade700)
    }
    Connections {
        target: converterPage.taskList.model
        function onDataChanged(idx1, idx2, value) {
            if (idx1.row <= taskRow.index && taskRow.index <= idx2.row) {
                let task_result = converterPage.taskList.model.get(taskRow.index);
                if (value.includes(2)) {
                    // 2 is the index of the stem field
                    stemField.text = task_result.stem;
                }
                if (value.includes(3)) {
                    // 3 is the index of the ext field
                    extLabel.text = task_result.ext;
                }
                if (value.includes(5)) {
                    // 5 is the index of the running field
                    if (task_result.running) {
                        successButton.visible = errorButton.visible = warningButton.visible = skipButton.visible = false;
                        runningIndicator.visible = true;
                    } else {
                        runningIndicator.visible = false;
                        let error = task_result.error;
                        if (error) {
                            errorLabel.text = clipboard.shorten_error_message(error);
                            errorLabel.errorFullText = error;
                            errorButton.visible = true;
                            runningIndicator.visible = false;
                        } else if (task_result.success) {
                            let conflict = taskManager.output_path_exists(index);
                            let conflict_policy = configItems.conflict_policy;
                            if (!conflict || conflict_policy == "Overwrite" || (conflict_policy == "Prompt" && window.yesToAll)) {
                                let move_result = taskManager.move_to_output(index);
                                if (move_result) {
                                    if (task_result.warning) {
                                        warningLabel.text = clipboard.shorten_error_message(task_result.warning);
                                        warningLabel.warningFullText = task_result.warning;
                                        warningButton.visible = true;
                                    } else {
                                        successButton.visible = true;
                                    }
                                } else {
                                    error = converterPage.taskList.model.get(taskRow.index).error;
                                    errorLabel.text = clipboard.shorten_error_message(error);
                                    errorLabel.errorFullText = error;
                                    errorButton.visible = true;
                                }
                            } else if (conflict_policy == "Skip" || (conflict_policy == "Prompt" && window.noToAll)) {
                                skipButton.visible = true;
                            } else {
                                let message_box = messageBox.createObject(taskList, {
                                    body: "<b>" + qsTr("Do you want to overwrite the file?") + "</b>",
                                    message: qsTr("File %1 already exists. Overwrite?").arg(taskManager.get_output_path(index)),
                                    onOk: () => {
                                        let move_result = taskManager.move_to_output(index);
                                        if (move_result) {
                                            if (task_result.warning) {
                                                warningLabel.text = task_result.warning;
                                                warningButton.visible = true;
                                            } else {
                                                successButton.visible = true;
                                            }
                                        } else {
                                            error = converterPage.taskList.model.get(taskRow.index).error;
                                            errorLabel.text = clipboard.shorten_error_message(error);
                                            errorLabel.errorFullText = error;
                                            errorButton.visible = true;
                                        }
                                    },
                                    onCancel: () => {
                                        skipButton.visible = true;
                                    }
                                });
                                message_box.open();
                            }
                        } else {
                            successButton.visible = errorButton.visible = warningButton.visible = skipButton.visible = false;
                        }
                    }
                }
            }
        }
    }
}
