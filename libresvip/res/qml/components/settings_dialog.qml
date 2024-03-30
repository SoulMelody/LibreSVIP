import QtCore
import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import QtQuick.Templates as T
import Qt.labs.qmlmodels

Dialog {
    id: settingsDialog
    x: window.width / 2 - width / 2
    y: window.height / 2 - height / 2
    width: 700
    height: 500
    padding: 5
    topPadding: 5
    signal autoOpenSaveFolderChanged(bool value)
    signal resetTasksOnInputChangeChanged(bool value)
    signal autoDetectInputFormatChanged(bool value)
    signal conflictPolicyChanged(string value)

    function save_folder_type(save_folder) {
        let preset_folder = null
        if (dialogs.folderPresetsList.count > 0 && dialogs.folderPresetsList.currentIndex >= 0) {
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
                text: qsTr("Options")
                font.bold: true
                font.pixelSize: 20
                Layout.fillWidth: true
            }
            IconButton {
                Layout.alignment: Qt.AlignRight
                icon_name: "mdi7.close"
                diameter: 30
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
        id: basicSettingsPage
        ColumnLayout {
            Layout.margins: 15
            GroupBox {
                Layout.fillWidth: true
                background: Rectangle {
                    color: "transparent"
                }
                ColumnLayout {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    Label {
                        text: qsTr("Conversion Settings")
                        font.bold: true
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: qsTr("Auto-Detect Input File Type")
                        }
                        Row {
                            Layout.fillWidth: true
                        }
                        Switch {
                            checked: ConfigItems.get_bool("auto_detect_input_format")
                            onClicked: {
                                ConfigItems.set_bool("auto_detect_input_format", checked)
                                autoDetectInputFormatChanged(checked)
                            }
                            Component.onCompleted: {
                                autoDetectInputFormatChanged.connect( (value) => {
                                    value === checked ? null : checked = value
                                })
                            }
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: qsTr("Reset Task List When Changing Input File Type")
                        }
                        Row {
                            Layout.fillWidth: true
                        }
                        Switch {
                            checked: ConfigItems.get_bool("reset_tasks_on_input_change")
                            onClicked: {
                                ConfigItems.set_bool("reset_tasks_on_input_change", checked)
                                resetTasksOnInputChangeChanged(checked)
                            }
                            Component.onCompleted: {
                                resetTasksOnInputChangeChanged.connect( (value) => {
                                    value === checked ? null : checked = value
                                })
                            }
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: qsTr("Set Output File Extension Automatically")
                        }
                        Row {
                            Layout.fillWidth: true
                        }
                        Switch {
                            checked: ConfigItems.get_bool("auto_set_output_extension")
                            onClicked: {
                                ConfigItems.set_bool("auto_set_output_extension", checked)
                            }
                            Component.onCompleted: {
                                ConfigItems.auto_set_output_extension_changed.connect( (value) => {
                                    value === checked ? null : checked = value
                                })
                            }
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: qsTr("Multi-Threaded Conversion")
                        }
                        Row {
                            Layout.fillWidth: true
                        }
                        Switch {
                            checked: ConfigItems.get_bool("multi_threaded_conversion")
                            onClicked: {
                                ConfigItems.set_bool("multi_threaded_conversion", checked)
                            }
                        }
                    }
                }
            }
            Rectangle {
                Layout.fillWidth: true
                border.color: "lightgrey"
                height: 1
            }
            GroupBox {
                Layout.fillWidth: true
                background: Rectangle {
                    color: "transparent"
                }
                ColumnLayout {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    Label {
                        text: qsTr("Output Settings")
                        font.bold: true
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: qsTr("Deal with Conflicts")
                        }
                        Row {
                            Layout.fillWidth: true
                        }
                        ComboBox {
                            padding: 0
                            Layout.alignment: Qt.AlignRight
                            textRole: "text"
                            valueRole: "value"
                            model: [
                                {value: "Overwrite", text: qsTr("Overwrite")},
                                {value: "Skip", text: qsTr("Skip")},
                                {value: "Prompt", text: qsTr("Prompt")}
                            ]
                            onActivated: (index) => {
                                ConfigItems.set_conflict_policy(currentValue)
                                conflictPolicyChanged(currentValue)
                            }
                            Component.onCompleted: {
                                currentIndex = indexOfValue(ConfigItems.get_conflict_policy())
                                conflictPolicyChanged.connect( (value) => {
                                    switch (value) {
                                        case "Overwrite":
                                        case "Skip":
                                        case "Prompt":
                                            currentIndex = indexOfValue(value)
                                            break
                                    }
                                })
                            }
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: qsTr("Open Output Folder When Done")
                        }
                        Row {
                            Layout.fillWidth: true
                        }
                        Switch {
                            checked: ConfigItems.get_bool("open_save_folder_on_completion")
                            onClicked: {
                                ConfigItems.set_bool("open_save_folder_on_completion", checked)
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
        }
    }

    Component {
        id: savePathSettingsPage
        ColumnLayout {
            spacing: 0
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
                            cur_value = ConfigItems.get_save_folder()
                            break
                    }
                    ConfigItems.set_save_folder(cur_value)
                    dialogs.save_folder_changed(cur_value)
                }
            }
            ColumnLayout {
                Layout.margins: 15
                GridLayout {
                    Layout.fillWidth: true
                    rows: 2
                    columns: 2
                    RadioButton {
                        Layout.fillWidth: true
                        Layout.row: 0
                        Layout.column: 0
                        ButtonGroup.group: saveFolderGroup
                        id: sameAsSourceRadio
                        text: qsTr("Same as Source")
                    }
                    RadioButton {
                        Layout.fillWidth: true
                        Layout.row: 0
                        Layout.column: 1
                        ButtonGroup.group: saveFolderGroup
                        id: desktopRadio
                        text: qsTr("Desktop")
                    }
                    RadioButton {
                        Layout.fillWidth: true
                        Layout.row: 1
                        Layout.column: 0
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
                                            let save_folder = ConfigItems.get_save_folder()
                                            if (save_folder !== presetRadioToolTip.text) {
                                                ConfigItems.set_save_folder(presetRadioToolTip.text)
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
                                            let save_folder = ConfigItems.get_save_folder()
                                            if (save_folder !== presetRadioToolTip.text) {
                                                ConfigItems.set_save_folder(presetRadioToolTip.text)
                                                dialogs.save_folder_changed(presetRadioToolTip.text)
                                            }
                                        }
                                    }
                                }
                                function onRowsRemoved(idx, first, last) {
                                    if (first == 0 && last == dialogs.folderPresetsList.count - 1) {
                                        presetRadioToolTip.text = ""
                                        if (presetRadio.checked) {
                                            dialogs.save_folder_changed(ConfigItems.get_save_folder())
                                        }
                                    }
                                }
                            }
                        }
                    }
                    RadioButton {
                        Layout.fillWidth: true
                        Layout.row: 1
                        Layout.column: 1
                        ButtonGroup.group: saveFolderGroup
                        id: customRadio
                        text: qsTr("Custom (Browse ...)")
                    }
                }
                Rectangle {
                    Layout.fillWidth: true
                    border.color: "lightgrey"
                    height: 1
                }
                Button {
                    Layout.alignment: Qt.AlignHCenter
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
    }

    Component {
        id: pluginsSettingsPage
        ColumnLayout {
            HorizontalHeaderView {
                id: horizontalHeader
                syncView: pluginsTableView
                Layout.fillWidth: true
                clip: true
                delegate: Rectangle {
                    implicitHeight: 50
                    border.width: 1
                    border.color: window.Material.backgroundDimColor
                    color: window.Material.dialogColor

                    RowLayout {
                        anchors.centerIn: parent
                        Layout.alignment: Qt.AlignHCenter
                        Label {
                            text: qsTr(display)
                            visible: index !== 3
                        }
                        IconButton {
                            icon_name: "mdi7.help-circle-outline"
                            diameter: 20
                            cursor_shape: Qt.WhatsThisCursor
                            ToolTip.visible: hovered
                            ToolTip.text: qsTr("Plugin is enabled or not (Click to enter editing mode)")
                            visible: index === 3
                        }
                    }
                }
            }
            TableView {
                id: pluginsTableView
                Layout.fillWidth: true
                Layout.fillHeight: true
                columnSpacing: 0
                rowSpacing: 0
                clip: true
                editTriggers: TableView.SingleTapped

                model: ConfigItems.qget("plugin_candidates")
                ScrollBar.vertical: ScrollBar {}
                ScrollBar.horizontal: ScrollBar {}

                delegate: DelegateChooser {
                    DelegateChoice{
                        column: 0
                        delegate: Rectangle {
                            implicitWidth: 220
                            implicitHeight: 32
                            border.width: 1
                            border.color: window.Material.backgroundDimColor
                            color: window.Material.dialogColor

                            Label {
                                text: qsTr(display)
                                anchors.centerIn: parent
                            }
                        }
                    }
                    DelegateChoice {
                        column: 1
                        delegate: Rectangle {
                            implicitWidth: 120
                            implicitHeight: 32
                            border.width: 1
                            border.color: window.Material.backgroundDimColor
                            color: window.Material.dialogColor

                            Label {
                                text: display
                                anchors.centerIn: parent
                            }
                        }
                    }
                    DelegateChoice {
                        column: 2
                        delegate: Rectangle {
                            implicitWidth: 60
                            implicitHeight: 32
                            border.width: 1
                            clip: true
                            border.color: window.Material.backgroundDimColor
                            color: window.Material.dialogColor

                            Label {
                                text: display
                                anchors.centerIn: parent
                            }
                        }
                    }
                    DelegateChoice {
                        column: 3
                        delegate: Rectangle {
                            implicitWidth: 70
                            implicitHeight: 32
                            border.width: 1
                            border.color: window.Material.backgroundDimColor
                            color: window.Material.dialogColor

                            Label {
                                text: IconicFontLoader.icon("mdi7." + display)
                                font.family: "Material Design Icons"
                                font.pixelSize: 22
                                color: window.Material.accent
                                anchors.centerIn: parent
                            }

                            TableView.editDelegate: CheckBox {
                                checked: value === "checkbox-marked"
                                anchors.centerIn: parent
                                onToggled: {
                                    if (ConfigItems.toggle_plugin(row)) {
                                        TaskManager.reload_formats()
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    Component {
        id: updatesSettingsPage
        ColumnLayout {
            Layout.margins: 15
            RowLayout {
                Layout.fillWidth: true
                Row {
                    width: 10
                }
                Label {
                    text: qsTr("Auto Check for Updates")
                }
                Row {
                    Layout.fillWidth: true
                }
                Switch {
                    checked: ConfigItems.get_bool("auto_check_for_updates")
                    onClicked: {
                        ConfigItems.set_bool("auto_check_for_updates", checked)
                    }
                }
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        TabBar {
            id: settingsTabBar
            Layout.fillHeight: true
            Layout.preferredWidth: 200

            contentItem: ListView {
                model: settingsTabBar.contentModel
                currentIndex: settingsTabBar.currentIndex

                spacing: settingsTabBar.spacing
                orientation: ListView.Vertical
                boundsBehavior: Flickable.StopAtBounds
                flickableDirection: Flickable.AutoFlickIfNeeded
                snapMode: ListView.SnapToItem

                highlightMoveDuration: 250
                highlightResizeDuration: 0
                highlightFollowsCurrentItem: true
                highlightRangeMode: ListView.ApplyRange
                preferredHighlightBegin: 48
                preferredHighlightEnd: width - 48

                highlight: Item {
                    Rectangle {
                        height: 46
                        width: settingsTabBar.width
                        y: settingsTabBar.position === T.TabBar.Footer ? 0 : parent.height - height
                        border.width: 1
                        border.color: settingsTabBar.Material.accentColor
                        color: "transparent"
                    }
                }
            }
            spacing: 5

            TabButton {
                id: basicSettingsBtn
                width: 200
                text: qsTr("Basic Settings")
                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: {
                    settingsStack.currentIndex = 0
                }
            }

            TabButton {
                id: savePathSettingsBtn
                width: 200
                text: qsTr("Save Path Settings")
                anchors.top: basicSettingsBtn.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.topMargin: parent.spacing
                onClicked: {
                    settingsStack.currentIndex = 1
                }
            }

            TabButton {
                id: pluginsSettingsBtn
                width: 200
                text: qsTr("Format Provider Plugins")
                enabled: !TaskManager.busy
                anchors.top: savePathSettingsBtn.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.topMargin: parent.spacing
                onClicked: {
                    settingsStack.currentIndex = 2
                }
            }

            TabButton {
                id: updatesSettingsBtn
                width: 200
                text: qsTr("Updates Settings")
                anchors.top: pluginsSettingsBtn.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.topMargin: parent.spacing
                onClicked: {
                    settingsStack.currentIndex = 3
                }
            }
        }
        Rectangle {
            Layout.fillHeight: true
            width: 1
            color: "lightgrey"
        }
        StackLayout {
            Layout.fillHeight: true
            Layout.fillWidth: true
            id: settingsStack
            clip: true
            currentIndex: 0
            Component.onCompleted: {
                basicSettingsPage.createObject(settingsStack)
                savePathSettingsPage.createObject(settingsStack)
                pluginsSettingsPage.createObject(settingsStack)
                updatesSettingsPage.createObject(settingsStack)
                dialogs.save_folder_changed(ConfigItems.get_save_folder())
            }
        }
    }
}