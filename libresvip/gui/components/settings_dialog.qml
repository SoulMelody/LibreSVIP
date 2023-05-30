import QtCore
import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

Dialog {
    id: settingsDialog
    x: window.width / 2 - width / 2
    y: window.height / 2 - height / 2
    width: 700
    height: 500
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
    header: ColumnLayout {
        Layout.fillWidth: true
        RowLayout {
            Layout.fillWidth: true
            Rectangle {
                Layout.fillHeight: true
                width: 15
                color: "transparent"
            }
            Label {
                text: qsTr("Settings")
                font.bold: true
                font.pixelSize: 20
                Layout.fillWidth: true
            }
            IconButton {
                Layout.alignment: Qt.AlignRight
                icon_name: "mdi6.close"
                diameter: 30
                icon_size_multiplier: 1.5
                onClicked: settingsDialog.close()
            }
        }
        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: "#ccc"
        }
    }

    Component {
        id: convertSettingsPage
        GroupBox {
            anchors.margins: 15
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
    }

    Component {
        id: savePathSettingsPage
        ColumnLayout {
            spacing: 0
            anchors.margins: 15
            Layout.fillWidth: true
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
                    visible: presetRadio.hovered && text !== ""
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
                Layout.fillWidth: true
                border.color: "lightgrey"
                height: 1
            }
            Button {
                text: qsTr("Manage Folders Presets")
                onClicked: {
                    dialogs.folderPresetsDialog.open()
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
    }

    Component {
        id: conflictPolicySettingsPage        
        GroupBox {
            anchors.margins: 15
            background: Rectangle {
                color: "transparent"
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
                target: settingsDialog
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
    }
    
    Component {
        id: updatesSettingsPage
        ColumnLayout {
            anchors.margins: 15
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
            Column {
                Switch {
                    text: qsTr("Auto Check for Updates")
                    enabled: false
                }
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        ColumnLayout {
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
            Layout.fillHeight: true
            Layout.preferredWidth: 200
            Repeater {
                model: ListModel {
                    ListElement {
                        label: qsTr("Conversion Settings")
                        value: "conversion"
                    }
                    ListElement {
                        label: qsTr("Save Path Settings")
                        value: "save_path"
                    }
                    ListElement {
                        label: qsTr("Conflict Policy Settings")
                        value: "file_conflict_policy"
                    }
                    ListElement {
                        label: qsTr("Updates Settings")
                        value: "updates"
                    }
                }
                Column {
                    required property string label
                    required property string value
                    Layout.preferredWidth: 200
                    height: 40
                    Button {
                        width: parent.width
                        text: qsTr(label)
                        onClicked: {
                            if (value === "conversion") {
                                settingsStack.push(convertSettingsPage)
                            } else if (value === "save_path") {
                                settingsStack.push(savePathSettingsPage)
                            } else if (value === "file_conflict_policy") {
                                settingsStack.push(conflictPolicySettingsPage)
                            } else if (value === "updates") {
                                settingsStack.push(updatesSettingsPage)
                            }
                        }
                    }
                }
            }
        }
        Rectangle {
            Layout.fillHeight: true
            width: 1
            color: "lightgrey"
        }
        ColumnLayout {
            Layout.fillHeight: true
            Layout.fillWidth: true
            StackView {
                Layout.fillHeight: true
                Layout.fillWidth: true
                id: settingsStack
                initialItem: convertSettingsPage
                pushEnter: Transition {
                    PropertyAnimation {
                        property: "opacity"
                        from: 0
                        to:1
                        duration: 200
                    }
                }
                pushExit: Transition {
                    PropertyAnimation {
                        property: "opacity"
                        from: 1
                        to:0
                        duration: 200
                    }
                }
                popEnter: Transition {
                    PropertyAnimation {
                        property: "opacity"
                        from: 0
                        to:1
                        duration: 200
                    }
                }
                popExit: Transition {
                    PropertyAnimation {
                        property: "opacity"
                        from: 1
                        to:0
                        duration: 200
                    }
                }
            }
        }
    }
}