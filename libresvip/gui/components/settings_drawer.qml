import QtCore
import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

Drawer {
    id: drawer
    height: window.height
    signal autoOpenSaveFolderChanged(bool value)
    signal resetTasksOnInputChangeChanged(bool value)
    signal autoDetectInputFormatChanged(bool value)
    signal conflictPolicyChanged(string value)

    function save_folder_type(save_folder) {
        let preset_folder = null
        if (dialogs.folderPresetsList.model.rowCount() > 0 && dialogs.folderPresetsList.currentIndex >= 0) {
            preset_folder = dialogs.folderPresetsList.model.get(dialogs.folderPresetsList.currentIndex).path
        }
        switch (save_folder) {
            case ".":
            case "./":
                return 1
            case dialogs.url2path(StandardPaths.standardLocations(StandardPaths.DesktopLocation)[0]):
                return 2
            case preset_folder:
                return 3
            default:
                return 4
        }
    }

    ScrollView {
        anchors.fill: parent
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 10
            GroupBox {
                anchors.margins: 15
                label: Label {
                    text: qsTr("Conversion Settings")
                    font.bold: true
                }
                background: Rectangle {
                    color: "transparent"
                }
                ColumnLayout {
                    Switch {
                        text: qsTr("Auto-Detect Input File Type")
                        checked: py.config_items.get_bool("auto_detect_input_format")
                        onClicked: {
                            py.config_items.set_bool("auto_detect_input_format", checked)
                            autoDetectInputFormatChanged(checked)
                        }
                        Component.onCompleted: {
                            autoDetectInputFormatChanged.connect( (value) => {
                                value === checked ? null : checked = value
                            })
                        }
                    }
                    Switch {
                        text: qsTr("Reset Task List When Changing Input File Type")
                        checked: py.config_items.get_bool("reset_tasks_on_input_change")
                        onClicked: {
                            py.config_items.set_bool("reset_tasks_on_input_change", checked)
                            resetTasksOnInputChangeChanged(checked)
                        }
                        Component.onCompleted: {
                            resetTasksOnInputChangeChanged.connect( (value) => {
                                value === checked ? null : checked = value
                            })
                        }
                    }
                    Switch {
                        text: qsTr("Set Output File Extension Automatically")
                        checked: py.config_items.get_bool("auto_set_output_extension")
                        onClicked: {
                            py.config_items.set_bool("auto_set_output_extension", checked)
                        }
                        Component.onCompleted: {
                            py.config_items.auto_set_output_extension_changed.connect( (value) => {
                                value === checked ? null : checked = value
                            })
                        }
                    }
                    Switch {
                        text: qsTr("Multi-Threaded Conversion")
                        checked: py.config_items.get_bool("multi_threaded_conversion")
                        onClicked: {
                            py.config_items.set_bool("multi_threaded_conversion", checked)
                        }
                    }
                    Switch {
                        text: qsTr("Open Output Folder When Done")
                        checked: py.config_items.get_bool("open_save_folder_on_completion")
                        onClicked: {
                            py.config_items.set_bool("open_save_folder_on_completion", checked)
                            autoOpenSaveFolderChanged(checked)
                        }
                        Component.onCompleted: {
                            autoOpenSaveFolderChanged.connect( (value) => {
                                value === checked ? null : checked = value
                            })
                        }
                    }
                }
            }
            ButtonGroup {
                id: saveFolderGroup
                onClicked: (button) => {
                    let cur_value = null
                    switch (button.text) {
                        case qsTr("Same as Source"): {
                            cur_value = "."
                            break
                        }
                        case qsTr("Desktop"): {
                            cur_value = dialogs.url2path(StandardPaths.standardLocations(StandardPaths.DesktopLocation)[0])
                            break
                        }
                        case qsTr("Preset Folder"): {
                            cur_value = dialogs.folderPresetsList.model.get(dialogs.folderPresetsList.currentIndex).path
                            break
                        }
                        case qsTr("Custom (Browse ...)"): {
                            actions.chooseSavePath.trigger()
                            return
                        }
                        default:
                            cur_value = py.config_items.get_save_folder()
                            break
                    }
                    py.config_items.set_save_folder(cur_value)
                    dialogs.save_folder_changed(cur_value)
                }
            }
            GroupBox {
                anchors.margins: 15
                label: Label {
                    text: qsTr("Set Save Path")
                    font.bold: true
                }
                background: Rectangle {
                    color: "transparent"
                }
                ColumnLayout {
                    spacing: 0
                    RadioButton {
                        ButtonGroup.group: saveFolderGroup
                        id: sameAsSourceRadio
                        text: qsTr("Same as Source")
                    }
                    RadioButton {
                        ButtonGroup.group: saveFolderGroup
                        id: desktopRadio
                        text: qsTr("Desktop")
                    }
                    RadioButton {
                        ButtonGroup.group: saveFolderGroup
                        id: presetRadio
                        enabled: dialogs.folderPresetsList.count > 0
                        text: qsTr("Preset Folder")
                        ToolTip {
                            id: presetRadioToolTip
                            visible: presetRadio.hovered
                            Component.onCompleted: {
                                if (dialogs.folderPresetsList.count > 0 && dialogs.folderPresetsList.currentIndex >= 0) {
                                    text = dialogs.folderPresetsList.model.get(dialogs.folderPresetsList.currentIndex).path
                                }
                            }
                            Connections {
                                target: dialogs.folderPresetBtnGroup
                                function onClicked() {
                                    if (dialogs.folderPresetsList.count > 0 && dialogs.folderPresetsList.currentIndex >= 0) {
                                        presetRadioToolTip.text = dialogs.folderPresetsList.model.get(dialogs.folderPresetsList.currentIndex).path
                                        if (presetRadio.checked) {
                                            let save_folder = py.config_items.get_save_folder()
                                            if (save_folder !== presetRadioToolTip.text) {
                                                py.config_items.set_save_folder(presetRadioToolTip.text)
                                                dialogs.save_folder_changed(presetRadioToolTip.text)
                                            }
                                        }
                                    }
                                }
                            }
                            Connections {
                                target: dialogs.folderPresetsList.model
                                function onDataChanged(idx1, idx2, value) {
                                    if (dialogs.folderPresetsList.count > 0 && dialogs.folderPresetsList.currentIndex >= 0) {
                                        presetRadioToolTip.text = dialogs.folderPresetsList.model.get(dialogs.folderPresetsList.currentIndex).path
                                        if (presetRadio.checked && dialogs.folderPresetsList.currentIndex >= idx1.row && dialogs.folderPresetsList.currentIndex <= idx2.row ) {
                                            let save_folder = py.config_items.get_save_folder()
                                            if (save_folder !== presetRadioToolTip.text) {
                                                py.config_items.set_save_folder(presetRadioToolTip.text)
                                                dialogs.save_folder_changed(presetRadioToolTip.text)
                                            }
                                        }
                                    }
                                }
                                function onRowsRemoved(idx, first, last) {
                                    if (first == 0 && last == dialogs.folderPresetsList.count - 1) {
                                        presetRadioToolTip.text = ""
                                        if (presetRadio.checked) {
                                            dialogs.save_folder_changed(py.config_items.get_save_folder())
                                        }
                                    }
                                }
                            }
                        }
                    }
                    RadioButton {
                        ButtonGroup.group: saveFolderGroup
                        id: customRadio
                        text: qsTr("Custom (Browse ...)")
                    }
                    Rectangle {
                        width: drawer.width - 30
                        border.color: "lightgrey"
                        height: 1
                    }
                    Button {
                        text: qsTr("Manage Folders Presets")
                        onClicked: {
                            dialogs.folderPresetsDialog.open()
                        }
                    }
                }
                Connections {
                    target: dialogs
                    function onSave_folder_changed(value) {
                        let selected_index = save_folder_type(value)
                        if (selected_index === 1) {
                            sameAsSourceRadio.checked = true
                        } else if (selected_index === 2) {
                            desktopRadio.checked = true
                        } else if (selected_index === 3) {
                            presetRadio.checked = true                        
                        } else {
                            customRadio.checked = true
                        }
                    }
                }
            }
            ButtonGroup {
                id: conflictPolicyGroup
                onClicked: (button) => {
                    let cur_value = null
                    switch (button.text) {
                        case qsTr("Overwrite"):
                            cur_value = "Overwrite"
                            break
                        case qsTr("Skip"):
                            cur_value = "Skip"
                            break
                        case qsTr("Prompt"):
                            cur_value = "Prompt"
                            break
                        default:
                            cur_value = py.config_items.get_conflict_policy()
                            break
                    }
                    py.config_items.set_conflict_policy(cur_value)
                    conflictPolicyChanged(cur_value)
                }
            }
            GroupBox {
                anchors.margins: 15
                label: Label {
                    text: qsTr("Deal With Existing Files")
                    font.bold: true
                }
                background: Rectangle {
                    color: "transparent"
                }
                ColumnLayout {
                    spacing: 0
                    RadioButton {
                        id: overwriteRadio
                        text: qsTr("Overwrite")
                        checked: py.config_items.get_conflict_policy() === "Overwrite"
                        ButtonGroup.group: conflictPolicyGroup
                    }
                    RadioButton {
                        id: skipRadio
                        text: qsTr("Skip")
                        checked: py.config_items.get_conflict_policy() === "Skip"
                        ButtonGroup.group: conflictPolicyGroup
                    }
                    RadioButton {
                        id: promptRadio
                        text: qsTr("Prompt")
                        checked: py.config_items.get_conflict_policy() === "Prompt"
                        ButtonGroup.group: conflictPolicyGroup
                    }
                }
                Connections {
                    target: drawer
                    function onConflictPolicyChanged(value) {
                        switch (value) {
                            case "Overwrite":
                                overwriteRadio.checked = true
                                break
                            case "Skip":
                                skipRadio.checked = true
                                break
                            case "Prompt":
                                promptRadio.checked = true
                                break
                        }
                    }
                }
            }
            Switch {
                text: qsTr("Auto Check for Updates")
                enabled: false
            }
        }
    }
}