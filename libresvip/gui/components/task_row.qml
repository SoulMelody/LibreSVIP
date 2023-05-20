import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts


Column {
    required property string name
    required property string path
    required property string stem
    required property string ext
    required property string index
    signal py_busy_changed(bool busy)
    signal py_all_tasks_finished()
    signal py_tasks_data_changed()
    RowLayout {
        Column {
            Label {
                Layout.fillWidth: true
                text: name.length > 25 ? name.substring(0, 25) + "..." : name
                font.bold: true
                font.pixelSize: Qt.application.font.pixelSize * 1.2
            }
            Label {
                Layout.fillWidth: true
                text: path.length > 30 ? path.substring(0, 30) + "..." : path
            }
        }

        Label {
            text: py.qta.icon("mdi6.transfer-right")
            font.family: materialFontLoader.name
            font.pixelSize: Qt.application.font.pixelSize * 1.5
        }

        TextField {
            text: stem
            onEditingFinished: {
                converterPage.taskList.model.update(index, {stem: this.text})
            }
            Component.onCompleted: {
                py_tasks_data_changed.connect( () => {
                    this.text = converterPage.taskList.model.get(index).stem
                })
            }
        }

        Label {
            text: ext
            Component.onCompleted: {
                py_tasks_data_changed.connect( (idx1, idx2, ext) => {
                    this.text = converterPage.taskList.model.get(index).ext
                })
            }
        }

        IconButton {
            icon_name: "mdi6.trash-can-outline"
            icon_size_multiplier: 1.2
            onClicked: {
                converterPage.taskList.model.delete(index)
                py.task_manager.trigger_event("tasks_size_changed", [])
            }
        }

        RoundButton {
            id: successButton
            visible: false
            text: py.qta.icon("mdi6.check")
            background: Rectangle {
                color: Material.color(Material.Green, Material.Shade300)
                radius: parent.height / 2
            }
            font.family: materialFontLoader.name
            font.pixelSize: Qt.application.font.pixelSize * 1.2
            radius: this.height / 2
            Behavior on visible {
                PropertyAnimation {
                    duration: 300
                    easing.type: Easing.InOutQuad
                }
            }
            ToolTip {
                id: successToolTip
                contentItem: ColumnLayout {
                    Label {
                        text: qsTr("File successfully converted")
                    }
                    Button {
                        Layout.alignment: Qt.AlignHCenter
                        background: Rectangle {
                            color: Material.color(Material.Indigo, Material.Shade500)
                        }
                        contentItem: Label {
                            text: qsTr("Open")
                        }
                        onClicked: {
                            py.task_manager.open_output_path(index)
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
                            py.task_manager.open_output_dir(index)
                        }
                    }
                }
            }
            onClicked: {
                successToolTip.visible = !successToolTip.visible
            }
            Component.onCompleted: {
                py_all_tasks_finished.connect( () => {
                    let success = converterPage.taskList.model.get(index).success
                    if (success) {
                        let conflict = py.task_manager.output_path_exists(index)
                        let conflict_policy = py.config_items.get_conflict_policy()
                        if (!conflict || conflict_policy == "Overwrite") {
                            let move_result = py.task_manager.move_to_output(index)
                            if (move_result) {
                                visible = true
                            }
                        } else if (conflict_policy == "Skip") {
                            skipButton.visible = true
                        } else {
                            let message_box = messageBox.createObject(
                                taskList,
                                {
                                    message: qsTr("File %1 already exists. Overwrite?").arg(
                                        py.task_manager.get_output_path(index)
                                    ),
                                    onOk: () => {
                                        let move_result = py.task_manager.move_to_output(index)
                                        if (move_result) {
                                            successToolTip.visible = true
                                        } else {
                                            converterPage.taskList.model.update(index, {success: false, error: qsTr("Failed to move file")})
                                        }
                                    },
                                    onCancel: () => {
                                        converterPage.taskList.model.update(index, {success: false, error: qsTr("File already exists")})
                                    }
                                }
                            )
                            message_box.open()
                        }
                    } else if (successToolTip.visible) {
                        successToolTip.visible = false
                    }
                })
                py_busy_changed.connect( (busy) => {
                    if (busy) {
                        successButton.visible = false
                    }
                })
            }
        }

        RoundButton {
            id: skipButton
            visible: false
            background: Rectangle {
                color: Material.color(Material.Blue, Material.Shade300)
                radius: parent.height / 2
            }
            text: py.qta.icon("mdi6.minus-thick")
            font.family: materialFontLoader.name
            font.pixelSize: Qt.application.font.pixelSize * 1.2
            radius: this.height / 2
            Behavior on visible {
                PropertyAnimation {
                    duration: 300
                    easing.type: Easing.InOutQuad
                }
            }
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
                            py.task_manager.open_output_dir(index)
                        }
                    }
                }
            }
            onClicked: {
                skipToolTip.visible = !skipToolTip.visible
            }
            Component.onCompleted: {
                py_busy_changed.connect( (busy) => {
                    if (busy) {
                        skipButton.visible = false
                    }
                })
            }
        }

        RoundButton {
            id: errorButton
            visible: false
            background: Rectangle {
                color: Material.color(Material.Red, Material.Shade300)
                radius: parent.height / 2
            }
            text: py.qta.icon("mdi6.alert-circle")
            font.family: materialFontLoader.name
            font.pixelSize: Qt.application.font.pixelSize * 1.2
            radius: this.height / 2
            Behavior on visible {
                PropertyAnimation {
                    duration: 300
                    easing.type: Easing.InOutQuad
                }
            }
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
                    }
                    Button {
                        id: copyErrorButton
                        Layout.alignment: Qt.AlignHCenter
                        background: Rectangle {
                            color: Material.color(Material.Indigo, Material.Shade500)
                        }
                        text: qsTr("Copy error message")
                        onClicked: {
                            let copy_result = py.clipboard.set_clipboard(errorLabel.text)
                            if (copy_result) {
                                text = qsTr("Copied")
                                resetCopyErrorButtonTimer.start()
                            }
                        }
                    }
                    Timer {
                        id: resetCopyErrorButtonTimer
                        interval: 1000
                        repeat: false
                        triggeredOnStart: false
                        onTriggered: {
                            copyErrorButton.text = qsTr("Copy error message")
                        }
                    }
                }
            }
            onClicked: {
                errorToolTip.visible = !errorToolTip.visible
            }
            Component.onCompleted: {
                py_tasks_data_changed.connect( () => {
                    let error = converterPage.taskList.model.get(index).error
                    if (error) {
                        errorLabel.text = error
                        visible = true
                    } else if (visible) {
                        visible = false
                    }
                })
                py_busy_changed.connect( (busy) => {
                    if (busy) {
                        errorButton.visible = false
                    }
                })
            }
        }

        RoundButton {
            id: runningButton
            radius: this.width / 2
            visible: false
            enabled: false
            Behavior on visible {
                PropertyAnimation {
                    duration: 300
                    easing.type: Easing.InOutQuad
                }
            }
            contentItem: Label {
                property bool running: false
                text: py.qta.icon("mdi6.autorenew")
                font.family: materialFontLoader.name
                font.pixelSize: Qt.application.font.pixelSize * 1.2
                NumberAnimation on rotation {
                    running: running;
                    from: 0;
                    to: 360;
                    loops: Animation.Infinite;
                    duration: 1200
                }
                Component.onCompleted: {
                    py_busy_changed.connect(function(busy) {
                        if (busy) {
                            running = true
                        } else {
                            running = false
                        }
                    })
                }
            }
            Component.onCompleted: {
                py_busy_changed.connect(function(busy) {
                    if (busy) {
                        runningButton.visible = true
                    } else {
                        runningButton.visible = false
                    }
                })
            }
        }
        Component.onCompleted: {
            py.task_manager.busy_changed.connect(py_busy_changed)
            py.task_manager.all_tasks_finished.connect(py_all_tasks_finished)
            converterPage.taskList.model.dataChanged.connect(
                (idx1, idx2, value) => {
                    if (index !== undefined && index == idx1.row){
                        py_tasks_data_changed()
                    }
                }
            )
        }
    }
}