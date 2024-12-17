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

    function save_folder_type(save_folder) {
        let preset_folder = null;
        if (dialogs.folderPresetsList.count > 0 && dialogs.folderPresetsList.currentIndex >= 0) {
            preset_folder = dialogs.folderPresetsList.model.get(dialogs.folderPresetsList.currentIndex).path;
        }
        switch (save_folder) {
        case ".":
        case "./":
            return 1;
        case dialogs.url2path(StandardPaths.standardLocations(StandardPaths.DesktopLocation)[0]):
            return 2;
        case preset_folder:
            return 3;
        default:
            return 4;
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
                new_padding: 6
                onClicked: settingsDialog.close()
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
                            checked: configItems.auto_detect_input_format
                            onClicked: {
                                configItems.auto_detect_input_format = checked;
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
                            checked: configItems.reset_tasks_on_input_change
                            onClicked: {
                                configItems.reset_tasks_on_input_change = checked;
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
                            checked: configItems.auto_set_output_extension
                            onClicked: {
                                configItems.auto_set_output_extension = checked;
                            }
                            Component.onCompleted: {
                                configItems.auto_set_output_extension_changed.connect(value => {
                                    value === checked ? null : checked = value;
                                });
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
                            checked: configItems.multi_threaded_conversion
                            onClicked: {
                                configItems.multi_threaded_conversion = checked;
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
                            id: conflictPolicyCombo
                            padding: 0
                            Layout.alignment: Qt.AlignRight
                            textRole: "text"
                            valueRole: "value"
                            model: [
                                {
                                    value: "Overwrite",
                                    text: qsTr("Overwrite")
                                },
                                {
                                    value: "Skip",
                                    text: qsTr("Skip")
                                },
                                {
                                    value: "Prompt",
                                    text: qsTr("Prompt")
                                }
                            ]
                            onActivated: index => {
                                configItems.conflict_policy = currentValue;
                            }
                            Connections {
                                target: configItems
                                function onConflict_policy_changed(value) {
                                    switch (value) {
                                    case "Overwrite":
                                    case "Skip":
                                    case "Prompt":
                                        conflictPolicyCombo.currentIndex = conflictPolicyCombo.indexOfValue(value);
                                        break;
                                    }
                                }
                            }
                            Component.onCompleted: {
                                currentIndex = indexOfValue(configItems.conflict_policy);
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
                            checked: configItems.open_save_folder_on_completion
                            onClicked: {
                                configItems.open_save_folder_on_completion = checked;
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
                onClicked: button => {
                    let cur_value = null;
                    switch (button.text) {
                    case qsTr("Same as Source"):
                        {
                            cur_value = ".";
                            break;
                        }
                    case qsTr("Desktop"):
                        {
                            cur_value = dialogs.url2path(StandardPaths.standardLocations(StandardPaths.DesktopLocation)[0]);
                            break;
                        }
                    case qsTr("Preset Folder"):
                        {
                            cur_value = dialogs.folderPresetsList.model.get(dialogs.folderPresetsList.currentIndex).path;
                            break;
                        }
                    case qsTr("Custom (Browse ...)"):
                        {
                            actions.chooseSavePath.trigger();
                            return;
                        }
                    default:
                        {
                            cur_value = configItems.save_folder;
                            break;
                        }
                    }
                    configItems.save_folder = cur_value;
                }
            }
            ColumnLayout {
                Layout.margins: 15
                GridLayout {
                    Layout.fillWidth: true
                    rows: 2
                    columns: 2
                    RadioButton {
                        id: sameAsSourceRadio
                        Layout.fillWidth: true
                        Layout.row: 0
                        Layout.column: 0
                        ButtonGroup.group: saveFolderGroup
                        text: qsTr("Same as Source")
                    }
                    RadioButton {
                        id: desktopRadio
                        Layout.fillWidth: true
                        Layout.row: 0
                        Layout.column: 1
                        ButtonGroup.group: saveFolderGroup
                        text: qsTr("Desktop")
                    }
                    RadioButton {
                        id: presetRadio
                        Layout.fillWidth: true
                        Layout.row: 1
                        Layout.column: 0
                        ButtonGroup.group: saveFolderGroup
                        enabled: dialogs.folderPresetsList.count > 0
                        text: qsTr("Preset Folder")
                        ToolTip {
                            id: presetRadioToolTip
                            visible: presetRadio.hovered && text !== ""
                            Component.onCompleted: {
                                if (dialogs.folderPresetsList.count > 0 && dialogs.folderPresetsList.currentIndex >= 0) {
                                    text = dialogs.folderPresetsList.model.get(dialogs.folderPresetsList.currentIndex).path;
                                }
                            }
                            Connections {
                                target: dialogs.folderPresetBtnGroup
                                function onClicked() {
                                    if (dialogs.folderPresetsList.count > 0 && dialogs.folderPresetsList.currentIndex >= 0) {
                                        presetRadioToolTip.text = dialogs.folderPresetsList.model.get(dialogs.folderPresetsList.currentIndex).path;
                                        if (presetRadio.checked) {
                                            let save_folder = configItems.save_folder;
                                            if (save_folder !== presetRadioToolTip.text) {
                                                configItems.save_folder = presetRadioToolTip.text;
                                            }
                                        }
                                    }
                                }
                            }
                            Connections {
                                target: dialogs.folderPresetsList.model
                                function onDataChanged(idx1, idx2, value) {
                                    if (dialogs.folderPresetsList.count > 0 && dialogs.folderPresetsList.currentIndex >= 0) {
                                        presetRadioToolTip.text = dialogs.folderPresetsList.model.get(dialogs.folderPresetsList.currentIndex).path;
                                        if (presetRadio.checked && dialogs.folderPresetsList.currentIndex >= idx1.row && dialogs.folderPresetsList.currentIndex <= idx2.row) {
                                            let save_folder = configItems.save_folder;
                                            if (save_folder !== presetRadioToolTip.text) {
                                                configItems.save_folder = presetRadioToolTip.text;
                                            }
                                        }
                                    }
                                }
                                function onRowsRemoved(idx, first, last) {
                                    if (first == 0 && last == dialogs.folderPresetsList.count - 1) {
                                        presetRadioToolTip.text = "";
                                        if (presetRadio.checked) {
                                            configItems.save_folder = configItems.save_folder;
                                        }
                                    }
                                }
                            }
                        }
                    }
                    RadioButton {
                        id: customRadio
                        Layout.fillWidth: true
                        Layout.row: 1
                        Layout.column: 1
                        ButtonGroup.group: saveFolderGroup
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
                        dialogs.folderPresetsDialog.open();
                    }
                }
            }
            Connections {
                target: configItems
                function onSave_folder_changed(value) {
                    let selected_index = save_folder_type(value);
                    if (selected_index === 1) {
                        sameAsSourceRadio.checked = true;
                    } else if (selected_index === 2) {
                        desktopRadio.checked = true;
                    } else if (selected_index === 3) {
                        presetRadio.checked = true;
                    } else {
                        customRadio.checked = true;
                    }
                }
            }
        }
    }

    Component {
        id: pluginsSettingsPage
        ColumnLayout {
            anchors.fill: parent
            HorizontalHeaderView {
                resizableColumns: false
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

                model: taskManager.qget("plugin_candidates")
                ScrollBar.vertical: ScrollBar {}
                ScrollBar.horizontal: ScrollBar {}

                delegate: DelegateChooser {
                    DelegateChoice {
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
                                text: qsTr(display)
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
                            required property bool editing

                            Label {
                                text: iconicFontLoader.icon("mdi7." + display)
                                font.family: "Material Design Icons"
                                font.pixelSize: 22
                                color: window.Material.accent
                                anchors.centerIn: parent
                                visible: !editing
                            }

                            TableView.editDelegate: CheckBox {
                                checked: value === "checkbox-marked"
                                anchors.fill: parent
                                onToggled: {
                                    taskManager.toggle_plugin(row);
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Component {
        id: lyricReplacementSettingsPage
        ColumnLayout {
            anchors.fill: parent
            RowLayout {
                Layout.fillWidth: true
                ComboBox {
                    id: lyricReplacementPresetsComboBox
                    editable: true
                    textRole: "display"
                    model: configItems.qget("lyric_replacement_presets")
                    ToolTip.visible: hovered
                    ToolTip.text: qsTr("Preset")
                    onAccepted: {
                        if (find(editText) === -1) {
                            lyricReplacementPresetsComboBox.model.append(editText);
                            taskManager.middleware_options_updated();
                        }
                    }
                    onActivated: index => {
                        lyricReplacementRulesTableView.model.modelReset();
                    }
                }
                IconButton {
                    icon_name: "mdi7.minus"
                    diameter: 35
                    ToolTip.visible: hovered
                    ToolTip.text: qsTr("Remove current preset")
                    onClicked: {
                        if (lyricReplacementPresetsComboBox.currentText !== "default") {
                            lyricReplacementPresetsComboBox.model.remove(lyricReplacementPresetsComboBox.currentText);
                            lyricReplacementPresetsComboBox.currentIndex = 0;
                            taskManager.middleware_options_updated();
                        }
                    }
                }
                Row {
                    Layout.fillWidth: true
                }
                Label {
                    text: qsTr("Add new rule")
                }
                ComboBox {
                    id: addPresetComboBox
                    Layout.preferredWidth: 150
                    textRole: "text"
                    valueRole: "value"
                    model: ListModel {
                        ListElement {
                            text: qsTr("Full match")
                            value: "full"
                        }
                        ListElement {
                            text: qsTr("Alphabetic")
                            value: "alphabetic"
                        }
                        ListElement {
                            text: qsTr("Non-alphabetic")
                            value: "non_alphabetic"
                        }
                        ListElement {
                            text: qsTr("Regex")
                            value: "regex"
                        }
                    }
                    onActivated: {
                        lyricReplacementRulesTableView.model.append(currentValue);
                    }
                }
                IconButton {
                    icon_name: "mdi7.help-circle-outline"
                    diameter: 35
                    cursor_shape: Qt.WhatsThisCursor
                    ToolTip.visible: hovered
                    ToolTip.text: qsTr("Alphabetic: Applies to alphabetic characters.\nNon-Alphabetic: For non-alphabetic characters and punctuation marks.\nRegex: for advanced users with knowledge of regular expressions.")
                }
            }
            HorizontalHeaderView {
                resizableColumns: false
                syncView: lyricReplacementRulesTableView
                Layout.fillWidth: true
                clip: true
                delegate: Rectangle {
                    implicitHeight: 50
                    implicitWidth: 70
                    border.width: 1
                    border.color: window.Material.backgroundDimColor
                    color: window.Material.dialogColor

                    RowLayout {
                        anchors.centerIn: parent
                        Layout.alignment: Qt.AlignHCenter
                        Label {
                            text: qsTr(display)
                            font.pixelSize: 10
                        }
                    }
                }
            }
            TableView {
                id: lyricReplacementRulesTableView
                Layout.fillWidth: true
                Layout.fillHeight: true
                columnSpacing: 0
                rowSpacing: 0
                clip: true
                editTriggers: TableView.SingleTapped

                model: configItems.rules_for_preset(lyricReplacementPresetsComboBox.currentText)
                ScrollBar.vertical: ScrollBar {}
                ScrollBar.horizontal: ScrollBar {}

                delegate: DelegateChooser {
                    DelegateChoice {
                        column: 0
                        delegate: Rectangle {
                            implicitWidth: 100
                            implicitHeight: 32
                            border.width: 1
                            border.color: window.Material.backgroundDimColor
                            color: window.Material.dialogColor

                            Label {
                                text: addPresetComboBox.textAt(addPresetComboBox.indexOfValue(display))
                                anchors.centerIn: parent
                            }
                        }
                    }
                    DelegateChoice {
                        column: 1
                        delegate: Rectangle {
                            clip: true
                            implicitWidth: 60
                            implicitHeight: 32
                            border.width: 1
                            border.color: window.Material.backgroundDimColor
                            color: window.Material.dialogColor
                            required property bool editing

                            Label {
                                text: display
                                anchors.centerIn: parent
                                visible: !editing
                            }

                            TableView.editDelegate: TextField {
                                anchors.fill: parent
                                text: value
                                horizontalAlignment: TextInput.AlignHCenter
                                verticalAlignment: TextInput.AlignVCenter
                                onEditingFinished: {
                                    display = text;
                                    parent.children[0].text = text;
                                }
                                TableView.onCommit: {
                                    editingFinished();
                                }
                            }
                        }
                    }
                    DelegateChoice {
                        column: 2
                        delegate: Rectangle {
                            clip: true
                            implicitWidth: 60
                            implicitHeight: 32
                            border.width: 1
                            border.color: window.Material.backgroundDimColor
                            color: window.Material.dialogColor
                            required property bool editing

                            Label {
                                text: display
                                anchors.centerIn: parent
                                visible: !editing
                            }

                            TableView.editDelegate: TextField {
                                anchors.fill: parent
                                text: value
                                horizontalAlignment: TextInput.AlignHCenter
                                verticalAlignment: TextInput.AlignVCenter
                                onEditingFinished: {
                                    display = text;
                                    parent.children[0].text = text;
                                }
                                TableView.onCommit: {
                                    editingFinished();
                                }
                            }
                        }
                    }
                    DelegateChoice {
                        column: 3
                        delegate: Rectangle {
                            clip: true
                            implicitWidth: 50
                            implicitHeight: 32
                            border.width: 1
                            border.color: window.Material.backgroundDimColor
                            color: window.Material.dialogColor
                            required property bool editing

                            Label {
                                text: display
                                anchors.centerIn: parent
                                visible: !editing
                            }

                            TableView.editDelegate: TextField {
                                anchors.fill: parent
                                text: value
                                horizontalAlignment: TextInput.AlignHCenter
                                verticalAlignment: TextInput.AlignVCenter
                                onEditingFinished: {
                                    display = text;
                                    parent.children[0].text = text;
                                }
                                TableView.onCommit: {
                                    editingFinished();
                                }
                            }
                        }
                    }
                    DelegateChoice {
                        column: 4
                        delegate: Rectangle {
                            clip: true
                            implicitWidth: 60
                            implicitHeight: 32
                            border.width: 1
                            border.color: window.Material.backgroundDimColor
                            color: window.Material.dialogColor
                            required property bool editing

                            Label {
                                text: display
                                anchors.centerIn: parent
                                visible: !editing
                            }

                            TableView.editDelegate: TextField {
                                anchors.fill: parent
                                text: value
                                horizontalAlignment: TextInput.AlignHCenter
                                verticalAlignment: TextInput.AlignVCenter
                                onEditingFinished: {
                                    display = text;
                                    parent.children[0].text = text;
                                }
                                TableView.onCommit: {
                                    editingFinished();
                                }
                            }
                        }
                    }
                    DelegateChoice {
                        column: 5
                        delegate: Rectangle {
                            implicitWidth: 70
                            implicitHeight: 32
                            border.width: 1
                            border.color: window.Material.backgroundDimColor
                            color: window.Material.dialogColor
                            required property bool editing

                            Label {
                                text: iconicFontLoader.icon("mdi7." + (display === "UNICODE" ? "checkbox-marked" : "checkbox-blank-outline"))
                                font.family: "Material Design Icons"
                                font.pixelSize: 22
                                color: window.Material.accent
                                anchors.centerIn: parent
                                visible: !editing
                            }

                            TableView.editDelegate: CheckBox {
                                checked: value === "UNICODE"
                                anchors.fill: parent
                                onToggled: {
                                    let index = TableView.view.index(row, column);
                                    lyricReplacementRulesTableView.model.setData(index, checked ? "UNICODE" : "IGNORECASE", Qt.DisplayRole);
                                    parent.children[0].text = iconicFontLoader.icon("mdi7." + (checked ? "checkbox-marked" : "checkbox-blank-outline"));
                                }
                            }
                        }
                    }
                    DelegateChoice {
                        column: 6
                        delegate: Rectangle {
                            implicitWidth: 80
                            implicitHeight: 32
                            border.width: 1
                            border.color: window.Material.backgroundDimColor
                            color: window.Material.dialogColor

                            RowLayout {
                                anchors.centerIn: parent
                                IconButton {
                                    icon_name: "mdi7.arrow-up-circle-outline"
                                    diameter: 20
                                    new_padding: 4
                                    visible: row > 0
                                    onClicked: {
                                        lyricReplacementRulesTableView.model.swap(row - 1, row);
                                    }
                                }
                                IconButton {
                                    icon_name: "mdi7.arrow-down-circle-outline"
                                    diameter: 20
                                    new_padding: 4
                                    visible: row < lyricReplacementRulesTableView.model.rowCount() - 1
                                    onClicked: {
                                        lyricReplacementRulesTableView.model.swap(row, row + 1);
                                    }
                                }
                                IconButton {
                                    icon_name: "mdi7.minus"
                                    diameter: 20
                                    new_padding: 4
                                    onClicked: {
                                        lyricReplacementRulesTableView.model.delete(row);
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
                    checked: configItems.auto_check_for_updates
                    onClicked: {
                        configItems.auto_check_for_updates = checked;
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
            Layout.preferredWidth: 180

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
                width: 180
                contentItem: RowLayout {
                    Label {
                        text: iconicFontLoader.icon("mdi7.application-cog-outline")
                        font.family: "Material Design Icons"
                        font.pixelSize: 22
                    }
                    Label {
                        text: qsTr("Basic Settings")
                    }
                }
                onClicked: {
                    settingsStack.currentIndex = 0;
                }
            }

            TabButton {
                id: savePathSettingsBtn
                width: 180
                contentItem: RowLayout {
                    Label {
                        text: iconicFontLoader.icon("mdi7.folder-download-outline")
                        font.family: "Material Design Icons"
                        font.pixelSize: 22
                    }
                    Label {
                        text: qsTr("Save Path Settings")
                    }
                }
                anchors.top: basicSettingsBtn.bottom
                anchors.topMargin: parent.spacing
                onClicked: {
                    settingsStack.currentIndex = 1;
                }
            }

            TabButton {
                id: pluginsSettingsBtn
                width: 180
                contentItem: RowLayout {
                    Label {
                        text: iconicFontLoader.icon("mdi7.puzzle-check-outline")
                        font.family: "Material Design Icons"
                        font.pixelSize: 22
                    }
                    Label {
                        text: qsTr("Format Provider Plugins")
                    }
                }
                enabled: !taskManager.busy
                anchors.top: savePathSettingsBtn.bottom
                anchors.topMargin: parent.spacing
                onClicked: {
                    settingsStack.currentIndex = 2;
                }
            }

            TabButton {
                id: lyricReplacementSettingsBtn
                width: 180
                contentItem: RowLayout {
                    Label {
                        text: iconicFontLoader.icon("mdi7.find-replace")
                        font.family: "Material Design Icons"
                        font.pixelSize: 22
                    }
                    Label {
                        text: qsTr("Lyric Replacement Rules")
                    }
                }
                anchors.top: pluginsSettingsBtn.bottom
                anchors.topMargin: parent.spacing
                onClicked: {
                    settingsStack.currentIndex = 3;
                }
            }

            TabButton {
                id: updatesSettingsBtn
                width: 180
                contentItem: RowLayout {
                    Label {
                        text: iconicFontLoader.icon("mdi7.update")
                        font.family: "Material Design Icons"
                        font.pixelSize: 22
                    }
                    Label {
                        text: qsTr("Updates Settings")
                    }
                }
                anchors.top: lyricReplacementSettingsBtn.bottom
                anchors.topMargin: parent.spacing
                onClicked: {
                    settingsStack.currentIndex = 4;
                }
            }
        }
        Rectangle {
            Layout.fillHeight: true
            width: 1
            color: "lightgrey"
        }
        StackLayout {
            id: settingsStack
            Layout.fillHeight: true
            Layout.fillWidth: true
            clip: true
            currentIndex: 0
            Component.onCompleted: {
                basicSettingsPage.createObject(settingsStack);
                savePathSettingsPage.createObject(settingsStack);
                pluginsSettingsPage.createObject(settingsStack);
                lyricReplacementSettingsPage.createObject(settingsStack);
                updatesSettingsPage.createObject(settingsStack);
                configItems.save_folder = configItems.save_folder;
            }
        }
    }
}
