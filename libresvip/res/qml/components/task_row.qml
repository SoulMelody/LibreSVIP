import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ColumnLayout {
    id: taskRow
    spacing: 0
    required property string name
    required property string path
    required property string stem
    required property string ext
    required property int index
    required property bool running
    property string errorFullText: ""
    property string warningFullText: ""
    width: converterPage.taskList.width
    implicitHeight: Math.max(40, contentRow.implicitHeight + divider.implicitHeight)
    // Height adapts to content while keeping a 40px minimum hit target (Phase 4.4).

    function resetStatusButtons() {
        successButton.visible = false;
        skipButton.visible = false;
        warningButton.visible = false;
        errorButton.visible = false;
    }

    function clearTaskDetails() {
        errorFullText = "";
        warningFullText = "";
        errorDetailDialog.close();
        warningDetailDialog.close();
    }

    function showRunningStatus() {
        clearTaskDetails();
        resetStatusButtons();
    }

    function showErrorDetails(message) {
        errorFullText = message || "";
        warningFullText = "";
        warningDetailDialog.close();
        resetStatusButtons();
        errorButton.visible = true;
    }

    function showWarningDetails(message) {
        warningFullText = message || "";
        errorFullText = "";
        errorDetailDialog.close();
        resetStatusButtons();
        warningButton.visible = true;
    }

    function showSuccessStatus() {
        clearTaskDetails();
        resetStatusButtons();
        successButton.visible = true;
    }

    function showSkipStatus() {
        clearTaskDetails();
        resetStatusButtons();
        skipButton.visible = true;
    }

    RowLayout {
        id: contentRow
        spacing: Theme.spacingXS
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.alignment: Qt.AlignVCenter
        Column {
            Layout.fillWidth: true
            Label {
                id: nameLabel
                width: parent.width
                text: name
                elide: Text.ElideRight
                font.bold: true
                font.pixelSize: Qt.application.font.pixelSize * 1.2
            }
            Label {
                id: pathLabel
                width: parent.width
                text: path
                elide: Text.ElideRight
                Accessible.description: qsTr("Path: %1").arg(path)
                HoverHandler {
                    id: pathHoverHandler
                }
                ToolTip.visible: pathHoverHandler.hovered && contentWidth > width
                ToolTip.text: qsTr("Path: %1").arg(path)
            }
        }
        Label {
            id: directionIndicator
            text: taskManager.conversion_mode === "Merge" && index !== 0 ? iconicFontLoader.icon("mdi7.transfer-up") : iconicFontLoader.icon("mdi7.transfer-right")
            font.family: "Material Design Icons"
            font.pixelSize: Qt.application.font.pixelSize * 1.5
        }
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
            accessibleName: qsTr("Remove")
            enabled: !taskManager.busy
            onClicked: {
                converterPage.taskList.model.delete(index);
            }
            ToolTip.visible: hovered
            ToolTip.text: qsTr("Remove")
        }

        RowLayout {
            id: statusArea
            spacing: Theme.spacingXS
            Layout.minimumWidth: 40

            Rectangle {
                id: statusIndicator
                implicitWidth: Math.max(44, Theme.minClickSize)
                implicitHeight: Math.max(44, Theme.minClickSize)
                color: "transparent"

                RoundButton {
                    id: successButton
                    anchors.centerIn: parent
                    visible: false
                    text: iconicFontLoader.icon("mdi7.check")
                    background: Rectangle {
                        color: Theme.colorSuccess
                        radius: parent.height / 2
                        HoverHandler {
                            acceptedDevices: PointerDevice.AllPointerTypes
                            cursorShape: Qt.PointingHandCursor
                        }
                    }
                    font.family: "Material Design Icons"
                    font.pixelSize: Qt.application.font.pixelSize
                    height: parent.height
                    width: height
                    radius: height / 2
                    Accessible.name: qsTr("File successfully converted")
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
                        color: Theme.colorInfo
                        radius: parent.height / 2
                        HoverHandler {
                            acceptedDevices: PointerDevice.AllPointerTypes
                            cursorShape: Qt.PointingHandCursor
                        }
                    }
                    text: iconicFontLoader.icon("mdi7.minus-thick")
                    font.family: "Material Design Icons"
                    font.pixelSize: Qt.application.font.pixelSize
                    height: parent.height
                    width: height
                    radius: height / 2
                    Accessible.name: qsTr("File skipped due to conflict")
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
                        color: Theme.colorWarning
                        radius: parent.height / 2
                        HoverHandler {
                            acceptedDevices: PointerDevice.AllPointerTypes
                            cursorShape: Qt.PointingHandCursor
                        }
                    }
                    text: iconicFontLoader.icon("mdi7.alert-circle")
                    font.family: "Material Design Icons"
                    font.pixelSize: Qt.application.font.pixelSize
                    height: parent.height
                    width: height
                    radius: height / 2
                    Accessible.name: qsTr("Show warning details")
                    ToolTip.visible: hovered
                    ToolTip.text: qsTr("This project file may contain abnormal or illegal data")
                    onClicked: {
                        warningDetailDialog.open();
                    }
                }

                RoundButton {
                    id: errorButton
                    anchors.centerIn: parent
                    visible: false
                    background: Rectangle {
                        color: Theme.colorError
                        radius: parent.height / 2
                        HoverHandler {
                            acceptedDevices: PointerDevice.AllPointerTypes
                            cursorShape: Qt.PointingHandCursor
                        }
                    }
                    text: iconicFontLoader.icon("mdi7.alert-circle")
                    font.family: "Material Design Icons"
                    font.pixelSize: Qt.application.font.pixelSize
                    height: parent.height
                    width: height
                    radius: height / 2
                    Accessible.name: qsTr("Show error details")
                    ToolTip.visible: hovered
                    ToolTip.text: qsTr("File failed to convert, click to view the error message")
                    onClicked: {
                        errorDetailDialog.open();
                    }
                }

                RunningIndicator {
                    id: runningIndicator
                    anchors.centerIn: parent
                    width: 44
                    height: width
                    visible: taskRow.running
                    running: taskRow.running
                    Accessible.ignored: true
                }

                TaskDetailDialog {
                    id: errorDetailDialog
                    heading: qsTr("File failed to convert, below is the error message:")
                    detailText: taskRow.errorFullText
                    copyText: qsTr("Copy error message")
                }

                TaskDetailDialog {
                    id: warningDetailDialog
                    heading: qsTr("This project file may contain abnormal or illegal data")
                    detailText: taskRow.warningFullText
                    copyText: qsTr("Copy warning message")
                }
            }
        }
    }
    Rectangle {
        id: divider
        Layout.fillWidth: true
        implicitHeight: 1
        color: Theme.colorBorder
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
                        taskRow.showRunningStatus();
                    } else {
                        let error = task_result.error;
                        if (error) {
                            taskRow.showErrorDetails(error);
                        } else if (task_result.success) {
                            let conflict = taskManager.output_path_exists(index);
                            let conflict_policy = configItems.conflict_policy;
                            if (!conflict || conflict_policy == "Overwrite" || (conflict_policy == "Prompt" && window.yesToAll)) {
                                let move_result = taskManager.move_to_output(index);
                                if (move_result) {
                                    if (task_result.warning) {
                                        taskRow.showWarningDetails(task_result.warning);
                                    } else {
                                        taskRow.showSuccessStatus();
                                    }
                                } else {
                                    error = converterPage.taskList.model.get(taskRow.index).error;
                                    taskRow.showErrorDetails(error);
                                }
                            } else if (conflict_policy == "Skip" || (conflict_policy == "Prompt" && window.noToAll)) {
                                taskRow.showSkipStatus();
                            } else {
                                let message_box = messageBox.createObject(taskList, {
                                    body: "<b>" + qsTr("Do you want to overwrite the file?") + "</b>",
                                    message: qsTr("File %1 already exists. Overwrite?").arg(taskManager.get_output_path(index)),
                                    onOk: () => {
                                        let move_result = taskManager.move_to_output(index);
                                        if (move_result) {
                                            if (task_result.warning) {
                                                taskRow.showWarningDetails(task_result.warning);
                                            } else {
                                                taskRow.showSuccessStatus();
                                            }
                                        } else {
                                            error = converterPage.taskList.model.get(taskRow.index).error;
                                            taskRow.showErrorDetails(error);
                                        }
                                    },
                                    onCancel: () => {
                                        taskRow.showSkipStatus();
                                    }
                                });
                                message_box.open();
                            }
                        } else {
                            taskRow.clearTaskDetails();
                            taskRow.resetStatusButtons();
                        }
                    }
                }
            }
        }
    }
}
