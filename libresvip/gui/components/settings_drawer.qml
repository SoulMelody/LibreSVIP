import QtCore
import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

Drawer {
    width: window.width * 0.3
    height: window.height
    signal openSettings()
    signal autoOpenSaveFolderChanged(bool value)
    signal autoSetOutputFileExtensionChanged(bool value)
    signal resetTasksOnInputChangeChanged(bool value)
    signal autoDetectInputFormatChanged(bool value)
    signal conflictPolicyChanged(string value)

    function save_folder_type() {
        let save_folder = py.config_items.get_save_folder()
        switch (save_folder) {
            case ".":
            case "./":
                return 1
            case dialogs.url2path(StandardPaths.standardLocations(StandardPaths.DesktopLocation)[0]):
                return 2
            default:
                return 3
        }
    }

    Column {
        anchors.fill: parent
        anchors.margins: 10
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
                autoSetOutputFileExtensionChanged(checked)
            }
            Component.onCompleted: {
                autoSetOutputFileExtensionChanged.connect( (value) => {
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
        Switch {
            text: qsTr("Auto Check for Updates")
            enabled: false
        }
        ColumnLayout {
            anchors.margins: 20
            Label {
                text: qsTr("Set Save Path")
                font.bold: true
            }
            RadioButton {
                id: sameAsSourceRadio
                text: qsTr("Same as Source")
                onClicked: {
                    let path = "."
                    converterPage.saveFolder.text = path
                    py.config_items.set_save_folder(path)
                }
                checked: save_folder_type() === 1
            }
            RadioButton {
                id: desktopRadio
                text: qsTr("Desktop")
                onClicked: {
                    let path = dialogs.url2path(StandardPaths.standardLocations(StandardPaths.DesktopLocation)[0])
                    converterPage.saveFolder.text = path
                    py.config_items.set_save_folder(path)
                }
                checked: save_folder_type === 2
            }
            RadioButton {
                text: qsTr("Custom (Browse ...)")
                onClicked: {
                    actions.chooseSavePath.trigger()
                }
                checked: save_folder_type() === 3
            }
        }
        ColumnLayout {
            anchors.margins: 20
            Label {
                text: qsTr("Deal With Existing Files")
                font.bold: true
            }
            RadioButton {
                text: qsTr("Overwrite")
                checked: py.config_items.get_conflict_policy() === "Overwrite"
                onClicked: {
                    py.config_items.set_conflict_policy("Overwrite")
                    conflictPolicyChanged("Overwrite")
                }
                Component.onCompleted: {
                    conflictPolicyChanged.connect( (value) => {
                        checked = (value === "Overwrite")
                    })
                }
            }
            RadioButton {
                text: qsTr("Skip")
                checked: py.config_items.get_conflict_policy() === "Skip"
                onClicked: {
                    py.config_items.set_conflict_policy("Skip")
                    conflictPolicyChanged("Skip")
                }
                Component.onCompleted: {
                    conflictPolicyChanged.connect( (value) => {
                        checked = (value === "Skip")
                    })
                }
            }
            RadioButton {
                text: qsTr("Prompt")
                checked: py.config_items.get_conflict_policy() === "Prompt"
                onClicked: {
                    py.config_items.set_conflict_policy("Prompt")
                    conflictPolicyChanged("Prompt")
                }
                Component.onCompleted: {
                    conflictPolicyChanged.connect( (value) => {
                        checked = (value === "Prompt")
                    })
                }
            }
        }
    }
    Component.onCompleted: {
        openSettings.connect(this.open)
    }
}