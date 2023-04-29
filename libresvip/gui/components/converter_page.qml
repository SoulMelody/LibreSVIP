import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

Page {
    title: qsTr("Converter")

    property alias taskList: taskListView;
    property alias saveFolder: saveFolderTextField;
    signal swapInputOutput();

    Component {
        id: taskRow
        Column {
            required property string name
            required property string path
            required property string stem
            required property string ext
            required property string index
            width: taskList.width
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
                        taskList.model.update(index, {stem: this.text})
                    }
                    Component.onCompleted: {
                        taskList.model.dataChanged.connect( (idx1, idx2, stem) => {
                            if (index == idx1.row) {
                                this.text = taskList.model.get(index).stem
                            }
                        })
                    }
                }

                Label {
                    text: ext
                    Component.onCompleted: {
                        taskList.model.dataChanged.connect( (idx1, idx2, ext) => {
                            if (index == idx1.row) {
                                this.text = taskList.model.get(index).ext
                            }
                        })
                    }
                }

                RoundButton {
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
                        py.task_manager.all_tasks_finished.connect( () => {
                            let success = taskList.model.get(index).success
                            if (success) {
                                let conflict = py.task_manager.output_path_exists(index)
                                let conflict_policy = py.config_items.get_conflict_policy()
                                if (!conflict || conflict_policy == "Overwrite") {
                                    let move_result = py.task_manager.move_to_output(index)
                                    if (move_result) {
                                        visible = true
                                    } else {
                                        taskList.model.update(index, {success: false, error: "Failed to move file"})
                                    }
                                } else if (conflict_policy == "Skip") {
                                    skipButton.visible = true
                                } else {
                                    // TODO: show prompt
                                }
                            } else if (visible) {
                                visible = false
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
                                Layout.alignment: Qt.AlignHCenter
                                background: Rectangle {
                                    color: Material.color(Material.Indigo, Material.Shade500)
                                }
                                text: qsTr("Copy error message")
                                onClicked: {
                                    let copy_result = py.clipboard.set_clipboard(errorLabel.text)
                                    if (copy_result) {
                                        text = qsTr("Copied")
                                        let timer = Qt.createQmlObject(`
                                            import QtQuick;
                                            Timer {
                                                interval: 1000;
                                                repeat: false;
                                                triggeredOnStart: false;
                                            }`, errorToolTip
                                        )
                                        timer.triggered.connect( () => {
                                            text = qsTr("Copy error message")
                                        })
                                        timer.start()
                                        this.Component.onDestruction.connect(timer.destroy)
                                    }
                                }
                            }
                        }
                    }
                    onClicked: {
                        errorToolTip.visible = !errorToolTip.visible
                    }
                    Component.onCompleted: {
                        py.task_manager.all_tasks_finished.connect( () => {
                            let error = taskList.model.get(index).error
                            if (error) {
                                errorLabel.text = error
                                visible = true
                            } else if (visible) {
                                visible = false
                            }
                        })
                    }
                }

                RoundButton {
                    text: py.qta.icon("mdi6.trash-can-outline")
                    font.family: materialFontLoader.name
                    font.pixelSize: Qt.application.font.pixelSize * 1.2
                    radius: this.height / 2
                    onClicked: {
                        taskList.model.delete(index)
                        py.task_manager.trigger_event("tasks_size_changed", [])
                    }
                }
            }
        }
    }

    Component {
        id: colorPickerItem
        Column {
            property var field: {}
            height: 30
            RowLayout {
                Label {
                    text: field.title
                    Layout.alignment: Qt.AlignVCenter
                    font.pixelSize: 12
                    fontSizeMode: Text.Fit
                    wrapMode: Text.Wrap
                    Layout.preferredWidth: 150
                }
                TextField {
                    id: colorField
                    implicitWidth: 100
                    text: field.value
                    onEditingFinished: {
                        field.value = this.text
                    }
                }
                RoundButton {
                    text: py.qta.icon("mdi6.eyedropper-variant")
                    width: 30
                    radius: this.height / 2
                    font.family: materialFontLoader.name
                    font.pixelSize: Qt.application.font.pixelSize * 1.5
                    onClicked: {
                        var colorDialog = Qt.createQmlObject(
                            `import QtQuick.Dialogs;
                            ColorDialog {
                                selectedColor: colorField.text
                                onAccepted: {
                                    colorField.text = selectedColor
                                    field.value = selectedColor
                                }
                            }
                            `,
                            colorPickerItem, 'colorDialog'
                        )
                        this.Component.onDestruction.connect(colorDialog.destroy)
                        colorDialog.open()
                    }
                }
                RoundButton {
                    text: py.qta.icon("mdi6.help-circle-outline")
                    width: 30
                    radius: this.height / 2
                    font.family: materialFontLoader.name
                    font.pixelSize: Qt.application.font.pixelSize * 1.5
                    visible: field.description != ""
                    onClicked: {
                        info.visible = !info.visible
                    }
                    ToolTip {
                        id: info
                        y: parent.y - parent.height
                        visible: false
                        text: field.description
                    }
                    HoverHandler {
                        acceptedDevices: PointerDevice.Mouse
                        cursorShape: Qt.WhatsThisCursor
                    }
                }

            }
        }
    }

    Component {
        id: switchItem
        Column {
            property var field: {}
            height: 30
            RowLayout {
                Label {
                    text: field.title
                    Layout.alignment: Qt.AlignVCenter
                    font.pixelSize: 12
                    fontSizeMode: Text.Fit
                    wrapMode: Text.Wrap
                    Layout.preferredWidth: 150
                }
                Switch {
                    onCheckedChanged: {
                        field.value = this.checked
                    }
                }
                RoundButton {
                    text: py.qta.icon("mdi6.help-circle-outline")
                    width: 30
                    radius: this.height / 2
                    font.family: materialFontLoader.name
                    font.pixelSize: Qt.application.font.pixelSize * 1.5
                    visible: field.description != ""
                    onClicked: {
                        info.visible = !info.visible
                    }
                    ToolTip {
                        id: info
                        y: parent.y - parent.height
                        visible: false
                        text: field.description
                    }
                    HoverHandler {
                        acceptedDevices: PointerDevice.Mouse
                        cursorShape: Qt.WhatsThisCursor
                    }
                }
            }
        }
    }

    Component {
        id: comboBoxItem
        Column {
            property var field: {}
            height: 30
            RowLayout {
                Label {
                    text: field.title
                    Layout.alignment: Qt.AlignVCenter
                    font.pixelSize: 12
                    fontSizeMode: Text.Fit
                    wrapMode: Text.Wrap
                    Layout.preferredWidth: 150
                }
                ComboBox {
                    implicitWidth: 200
                    textRole: "text"
                    valueRole: "value"
                    onActivated: {
                        field.value = this.currentValue
                    }
                    model: field.choices
                }
                RoundButton {
                    text: py.qta.icon("mdi6.help-circle-outline")
                    width: 30
                    radius: this.height / 2
                    font.family: materialFontLoader.name
                    font.pixelSize: Qt.application.font.pixelSize * 1.5
                    visible: field.description != ""
                    onClicked: {
                        info.visible = !info.visible
                    }
                    ToolTip {
                        id: info
                        y: parent.y - parent.height
                        visible: false
                        text: field.description
                    }
                    HoverHandler {
                        acceptedDevices: PointerDevice.Mouse
                        cursorShape: Qt.WhatsThisCursor
                    }
                }
            }
        }
    }

    Component {
        id: textFieldItem
        Column {
            property var field: {}
            height: 30
            RowLayout {
                Label {
                    Layout.alignment: Qt.AlignVCenter
                    text: field.title
                    font.pixelSize: 12
                    fontSizeMode: Text.Fit
                    wrapMode: Text.Wrap
                    Layout.preferredWidth: 150
                }
                TextField {
                    implicitWidth: 200
                    text: field.value
                    onEditingFinished: {
                        field.value = this.text
                    }
                }
                RoundButton {
                    text: py.qta.icon("mdi6.help-circle-outline")
                    width: 30
                    radius: this.height / 2
                    font.family: materialFontLoader.name
                    font.pixelSize: Qt.application.font.pixelSize * 1.5
                    visible: field.description != ""
                    onClicked: {
                        info.visible = !info.visible
                    }
                    ToolTip {
                        id: info
                        y: parent.y - parent.height
                        visible: false
                        text: field.description
                    }
                    HoverHandler {
                        acceptedDevices: PointerDevice.Mouse
                        cursorShape: Qt.WhatsThisCursor
                    }
                }
            }
        }
    }


    GridLayout {
        anchors.fill: parent
        anchors.margins: 20
        columns: 10
        rows: 10

        Control {
            Layout.row: 0
            Layout.rowSpan: 4
            Layout.column: 0
            Layout.columnSpan: 5
            Layout.preferredWidth: parent.width * 0.5
            Layout.preferredHeight: parent.height * 0.4
            background: Rectangle {
                color: "transparent"
                border.width: 1
                border.color: Material.color(
                    Material.Grey,
                    Material.Shade300
                )
            }

            GridLayout {
                anchors.fill: parent
                anchors.margins: 20
                width: 550
                columns: 10
                rows: 5
                Label {
                    Layout.columnSpan: 10
                    Layout.row: 0
                    Layout.column: 0
                    text: qsTr("Select File Formats")
                    font.pixelSize: 20
                    Layout.alignment: Qt.AlignVCenter
                }
                Grid {
                    Layout.columnSpan: 8
                    Layout.row: 1
                    Layout.column: 0
                    Layout.preferredWidth: parent.width * 0.8
                    height: 50
                    ComboBox {
                        id: inputFormat
                        textRole: "text"
                        valueRole: "value"
                        displayText: "Input Format: " + currentText
                        onActivated: (index) => {
                            if (
                                resetTasksOnInputChange.checked &&
                                py.task_manager.get_str("input_format") != currentValue
                            ) {
                                actions.clearTasks.trigger()
                            }
                            py.task_manager.set_str("input_format", currentValue)
                        }
                        Component.onCompleted: {
                            dialogs.openDialog.nameFilters[0] = currentText
                            py.task_manager.set_str("input_format", currentValue)
                            py.task_manager.input_format_changed.connect(function(input_format) {
                                let new_index = indexOfValue(input_format)
                                if (new_index != currentIndex) {
                                    currentIndex = new_index
                                    dialogs.openDialog.nameFilters[0] = currentText
                                }
                            })
                        }
                        width: parent.width
                        model: py.task_manager.qget("input_formats")
                    }
                }
                RoundButton {
                    Layout.columnSpan: 2
                    Layout.row: 1
                    Layout.column: 8
                    text: py.qta.icon("mdi6.information-outline")
                    width: 40
                    radius: this.height / 2
                    font.family: materialFontLoader.name
                    font.pixelSize: Qt.application.font.pixelSize * 1.5
                    onClicked: {
                        inputFormatInfo.visible = !inputFormatInfo.visible
                    }
                    ToolTip {
                        id: inputFormatInfo
                        y: parent.y + parent.height * 0.5
                        visible: false
                        contentItem: PluginInfo {
                            info: py.task_manager.plugin_info("input_format")
                            Component.onCompleted: {
                                py.task_manager.input_format_changed.connect(function(input_format) {
                                    info = py.task_manager.plugin_info("input_format")
                                })
                            }
                        }
                    }
                }
                Switch {
                    Layout.columnSpan: 4
                    Layout.row: 2
                    Layout.column: 0
                    Layout.preferredWidth: parent.width * 0.4
                    height: 40
                    text: qsTr("Auto-Detect Input File Type")
                    checked: py.config_items.get_bool("auto_detect_input_format")
                    onClicked: {
                        py.config_items.set_bool("auto_detect_input_format", checked)
                        settingsDrawer.autoDetectInputFormatChanged(checked)
                    }
                    Component.onCompleted: {
                        settingsDrawer.autoDetectInputFormatChanged.connect( (value) => {
                            value === checked ? null : checked = value
                        })
                    }
                }
                Switch {
                    id: resetTasksOnInputChange
                    Layout.columnSpan: 4
                    Layout.row: 2
                    Layout.column: 4
                    Layout.preferredWidth: parent.width * 0.4
                    height: 40
                    text: qsTr("Reset Tasks When Changing Input")
                    checked: py.config_items.get_bool("reset_tasks_on_input_change")
                    onClicked: {
                        py.config_items.set_bool("reset_tasks_on_input_change", checked)
                        settingsDrawer.resetTasksOnInputChangeChanged(checked)
                    }
                    Component.onCompleted: {
                        settingsDrawer.resetTasksOnInputChangeChanged.connect( (value) => {
                            value === checked ? null : checked = value
                        })
                    }
                }
                RoundButton {
                    Layout.columnSpan: 2
                    Layout.row: 2
                    Layout.column: 8
                    text: py.qta.icon("mdi6.swap-vertical")
                    width: 40
                    radius: this.height / 2
                    font.family: materialFontLoader.name
                    font.pixelSize: Qt.application.font.pixelSize * 1.5
                    onClicked: {
                        [
                            inputFormat.currentIndex,
                            outputFormat.currentIndex
                        ] = [
                            outputFormat.currentIndex,
                            inputFormat.currentIndex
                        ]
                        py.task_manager.set_str("input_format", inputFormat.currentValue)
                        py.task_manager.set_str("output_format", outputFormat.currentValue)
                    }
                    Component.onCompleted: {
                        swapInputOutput.connect(onClicked)
                    }
                }
                Grid {
                    Layout.columnSpan: 8
                    Layout.row: 3
                    Layout.column: 0
                    Layout.preferredWidth: parent.width * 0.8
                    height: 50
                    ComboBox {
                        id: outputFormat
                        textRole: "text"
                        valueRole: "value"
                        displayText: "Output Format: " + currentText
                        onActivated: (index) => {
                            py.task_manager.set_str("output_format", currentValue)
                        }
                        Component.onCompleted: {
                            py.task_manager.set_str("output_format", currentValue)
                        }
                        width: parent.width
                        model: py.task_manager.qget("output_formats")
                    }
                }
                RoundButton {
                    Layout.columnSpan: 2
                    Layout.row: 3
                    Layout.column: 8
                    text: py.qta.icon("mdi6.information-outline")
                    width: 40
                    radius: this.height / 2
                    font.family: materialFontLoader.name
                    font.pixelSize: Qt.application.font.pixelSize * 1.5
                    onClicked: {
                        outputFormatInfo.visible = !outputFormatInfo.visible
                    }
                    ToolTip {
                        id: outputFormatInfo
                        y: parent.y - parent.height * 2
                        visible: false
                        contentItem: PluginInfo {
                            info: py.task_manager.plugin_info("output_format")
                            Component.onCompleted: {
                                py.task_manager.output_format_changed.connect(function() {
                                    info = py.task_manager.plugin_info("output_format")
                                })
                            }
                        }
                    }
                }
                Switch {
                    Layout.columnSpan: 5
                    Layout.row: 4
                    Layout.column: 0
                    height: 40
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
            }
        }

        ScrollView {
            id: advancedSettings
            Layout.row: 0
            Layout.rowSpan: 7
            Layout.column: 5
            Layout.columnSpan: 5
            Layout.preferredWidth: parent.width * 0.5
            Layout.preferredHeight: parent.height * 0.7
            background: Rectangle {
                color: "transparent"
                border.width: 1
                border.color: Material.color(
                    Material.Grey,
                    Material.Shade300
                )
            }
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                Label {
                    text: qsTr("Advanced Settings")
                    font.pixelSize: 20
                    Layout.alignment: Qt.AlignVCenter
                }
                ColumnLayout {
                    width: parent.width
                    Row {
                        RoundButton {
                            width: 40
                            height: 40
                            radius: this.height / 2
                            contentItem: Label {
                                id: inputCollapseIcon
                                text: py.qta.icon("mdi6.chevron-right")
                                font.family: materialFontLoader.name
                                font.pixelSize: 20
                                rotation: 45
                                Behavior on rotation {
                                    PropertyAnimation{
                                        duration: 200
                                        easing.type: Easing.InOutQuad
                                    }
                                }
                            }
                            background: Rectangle {
                                color: "transparent"
                            }
                            onClicked: {
                                inputContainer.visible = !inputContainer.visible
                                inputCollapseIcon.rotation = inputContainer.visible ? 0 : 45
                            }
                        }
                        Label {
                            text: qsTr("Input Options")
                            font.pixelSize: 30
                            Layout.alignment: Qt.AlignVCenter
                        }
                    }
                    RowLayout{
                        Rectangle {
                            width: inputCollapseIcon.width + 15
                        }
                        ColumnLayout {
                            id: inputContainer
                            Behavior on visible {
                                PropertyAnimation{
                                    duration: 200
                                    easing.type: Easing.InOutQuad
                                }
                            }
                        }
                    }
                    ListView {
                        id: inputOptions
                        model: py.task_manager.qget("input_fields")
                        delegate: Column {
                            Component.onCompleted: {
                                let separator_item = Qt.createQmlObject(
                                    `import QtQuick;
                                    import QtQuick.Controls;
                                    import QtQuick.Layouts;
                                    RowLayout {
                                        Layout.fillWidth: true
                                        Label {
                                            text: py.qta.icon("mdi6.tune-variant")
                                            font.family: materialFontLoader.name
                                            font.pixelSize: 12
                                        }
                                        Rectangle {
                                            color: Material.color(
                                                Material.Grey,
                                                Material.Shade300
                                            );
                                            height: 1;
                                            width: advancedSettings.width - 50
                                        }
                                    }`,
                                    inputContainer,
                                    "separator"
                                )
                                this.Component.onDestruction.connect(separator_item.destroy)
                                let item = null;
                                switch (model.type) {
                                    case "bool": {
                                        item = switchItem.createObject(inputContainer, {
                                            "field": model
                                        })
                                        break
                                    }
                                    case "enum": {
                                        item = comboBoxItem.createObject(inputContainer, {
                                            "field": model
                                        })
                                        break
                                    }
                                    case "color" : {
                                        item = colorPickerItem.createObject(outputContainer, {
                                            "field": model
                                        })
                                        break
                                    }
                                    case "other": {
                                        item = textFieldItem.createObject(inputContainer, {
                                            "field": model
                                        })
                                        break
                                    }
                                }
                                if (item) {
                                    this.Component.onDestruction.connect(item.destroy)
                                }
                            }
                        }
                    }
                }
                ColumnLayout {
                    width: parent.width
                    Row {
                        RoundButton {
                            width: 40
                            height: 40
                            radius: this.height / 2
                            contentItem: Label {
                                id: outputCollapseIcon
                                text: py.qta.icon("mdi6.chevron-right")
                                font.family: materialFontLoader.name
                                font.pixelSize: 20
                                rotation: 45
                                Behavior on rotation {
                                    PropertyAnimation{
                                        duration: 200
                                        easing.type: Easing.InOutQuad
                                    }
                                }
                            }
                            background: Rectangle {
                                color: "transparent"
                            }
                            onClicked: {
                                outputContainer.visible = !outputContainer.visible
                                outputCollapseIcon.rotation = outputContainer.visible ? 0 : 45
                            }
                        }
                        Label {
                            text: qsTr("Output Options")
                            font.pixelSize: 30
                            Layout.alignment: Qt.AlignVCenter
                        }
                    }
                    RowLayout{
                        Rectangle {
                            width: outputCollapseIcon.width + 15
                        }
                        ColumnLayout {
                            id: outputContainer
                            Behavior on visible {
                                PropertyAnimation{
                                    duration: 200
                                    easing.type: Easing.InOutQuad
                                }
                            }
                        }
                    }
                    ListView {
                        id: outputOptions
                        model: py.task_manager.qget("output_fields")
                        delegate: Column {
                            Component.onCompleted: {
                                let separator_item = Qt.createQmlObject(
                                    `import QtQuick;
                                    import QtQuick.Controls;
                                    import QtQuick.Layouts;
                                    RowLayout {
                                        Layout.fillWidth: true
                                        Label {
                                            text: py.qta.icon("mdi6.tune-variant")
                                            font.family: materialFontLoader.name
                                            font.pixelSize: 12
                                        }
                                        Rectangle {
                                            color: Material.color(
                                                Material.Grey,
                                                Material.Shade300
                                            );
                                            height: 1;
                                            width: advancedSettings.width - 50
                                        }
                                    }
                                    `,
                                    outputContainer,
                                    "separator"
                                )
                                this.Component.onDestruction.connect(separator_item.destroy)
                                let item = null;
                                switch (model.type) {
                                    case "bool": {
                                        item = switchItem.createObject(outputContainer, {
                                            "field": model
                                        })
                                        break
                                    }
                                    case "enum": {
                                        item = comboBoxItem.createObject(outputContainer, {
                                            "field": model
                                        })
                                        break
                                    }
                                    case "color" : {
                                        item = colorPickerItem.createObject(outputContainer, {
                                            "field": model
                                        })
                                        break
                                    }
                                    case "other": {
                                        item = textFieldItem.createObject(outputContainer, {
                                            "field": model
                                        })
                                        break
                                    }
                                }
                                if (item) {
                                    this.Component.onDestruction.connect(item.destroy)
                                }
                            }
                        }
                    }
                }
            }
        }

        DropArea {
            id: taskListArea
            Layout.row: 4
            Layout.rowSpan: 6
            Layout.column: 0
            Layout.columnSpan: 5
            Layout.preferredWidth: parent.width * 0.5
            Layout.preferredHeight: parent.height * 0.6
            onDropped: (event) => {
                py.task_manager.add_task_paths(event.urls.map(dialogs.url2path))
            }
            MouseArea {
                anchors.fill: parent
                anchors.margins: 20
                hoverEnabled: true
                onEntered: {
                    if (taskListView.count == 0) {
                        taskListArea.opacity = 0.5
                    }
                }
                onExited: {
                    if (taskListView.count == 0) {
                        taskListArea.opacity = 1
                    }
                }
                onClicked: {
                    if (taskListView.count == 0) {
                        actions.openFile.trigger()
                    }
                }
                Label {
                    id: taskToolbarLabel
                    anchors.top: parent.top
                    text: qsTr("Task List")
                    font.pixelSize: 20
                }
                ScrollView {
                    anchors.top: taskToolbarLabel.bottom
                    anchors.topMargin: 20
                    height: 250
                    width: taskListArea.width - 40
                    ListView {
                        id: taskListView
                        model: py.task_manager.qget("tasks")
                        delegate: taskRow
                    }
                    visible: taskListView.count > 0 
                }
                Column {
                    anchors.centerIn: parent
                    Label {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: py.qta.icon("mdi6.tray-arrow-up")
                        font.family: materialFontLoader.name
                        font.pixelSize: 100
                    }
                    Label {
                        text: qsTr("Drag and drop files here")
                        font.pixelSize: 30
                    }
                    visible: taskListView.count == 0
                }
                Rectangle {
                    anchors.bottom: parent.bottom
                    color: "transparent"
                    Timer {
                        id: hideTaskToolbarTimer;
                        interval: 1000;
                        repeat: true;
                        triggeredOnStart: false;
                        onTriggered: {
                            if (taskToolbarTestArea.containsMouse || toggleTaskToolbarTestArea.containsMouse) {
                                return
                            }
                            taskToolbar.shown = false
                            toggleTaskToolbarButton.rotation = 0
                            this.stop()
                        }
                    }
                    RoundButton {
                        id: toggleTaskToolbarButton
                        background: Rectangle {
                            radius: this.height / 2
                            color: Material.color(
                                Material.Indigo,
                                Material.Shade300
                            );
                        }
                        text: py.qta.icon("mdi6.hammer-wrench")
                        y: parent.height - this.height / 2 - 10
                        font.family: materialFontLoader.name
                        font.pixelSize: Qt.application.font.pixelSize * 1.5
                        radius: this.height / 2
                        Behavior on rotation {
                            NumberAnimation {
                                easing.type: Easing.InOutQuad
                            }
                        }
                        MouseArea {
                            id: toggleTaskToolbarTestArea
                            anchors.fill: parent
                            hoverEnabled: true
                            onEntered: {
                                parent.rotation = 45
                                taskToolbar.shown = true
                            }
                            onExited: {
                                if (!hideTaskToolbarTimer.running) {
                                    hideTaskToolbarTimer.start()
                                }
                            }
                        }
                    }
                    Pane {
                        id: taskToolbar
                        property bool shown: false
                        x: toggleTaskToolbarButton.width
                        y: toggleTaskToolbarButton.y - 12
                        width: shown ? implicitWidth : 0
                        background: Rectangle {
                            color: "transparent"
                        }
                        Behavior on width {
                            NumberAnimation {
                                easing.type: Easing.InOutQuad
                            }
                        }
                        clip: true
                        Row {
                            RoundButton {
                                text: py.qta.icon("mdi6.plus")
                                background: Rectangle {
                                    radius: this.height / 2
                                    color: Material.color(
                                        Material.LightBlue,
                                        Material.Shade200
                                    );
                                }
                                font.family: materialFontLoader.name
                                font.pixelSize: Qt.application.font.pixelSize * 1.5
                                radius: this.height / 2
                                onClicked: {
                                    actions.openFile.trigger()
                                }
                            }
                            RoundButton {
                                text: py.qta.icon("mdi6.refresh")
                                background: Rectangle {
                                    radius: this.height / 2
                                    color: Material.color(
                                        Material.LightBlue,
                                        Material.Shade200
                                    );
                                }
                                font.family: materialFontLoader.name
                                font.pixelSize: Qt.application.font.pixelSize * 1.5
                                radius: this.height / 2
                                onClicked: {
                                    actions.clearTasks.trigger()
                                }
                            }
                            RoundButton {
                                text: py.qta.icon("mdi6.form-textbox")
                                background: Rectangle {
                                    radius: this.height / 2
                                    color: Material.color(
                                        Material.LightBlue,
                                        Material.Shade200
                                    );
                                }
                                font.family: materialFontLoader.name
                                font.pixelSize: Qt.application.font.pixelSize * 1.5
                                radius: this.height / 2
                                onClicked: {
                                    py.task_manager.reset_stems()
                                }
                            }
                        }
                    }
                    MouseArea {
                        id: taskToolbarTestArea
                        anchors.fill: taskToolbar
                        hoverEnabled: true
                        propagateComposedEvents: true
                        onClicked: (mouse) => {
                            mouse.accepted = false
                        }
                        onPressed: (mouse) => {
                            mouse.accepted = false
                        }
                        onReleased: (mouse) => {
                            mouse.accepted = false
                        }
                        onExited: {
                            if (!hideTaskToolbarTimer.running) {
                                hideTaskToolbarTimer.start()
                            }
                        }
                    }
                }
            }
            Rectangle {
                anchors.fill: parent
                color: "transparent"
                border.width: 1
                border.color: Material.color(
                    Material.Grey,
                    Material.Shade300
                )
            }
        }

        Control {
            Layout.row: 7
            Layout.rowSpan: 3
            Layout.column: 5
            Layout.columnSpan: 5
            Layout.preferredWidth: parent.width * 0.5
            Layout.preferredHeight: parent.height * 0.3
            background: Rectangle {
                color: "transparent"
                border.width: 1
                border.color: Material.color(
                    Material.Grey,
                    Material.Shade300
                )
            }
            GridLayout {
                anchors.fill: parent
                anchors.margins: 20
                width: 400
                columns: 10
                rows: 3
                Label {
                    Layout.columnSpan: 10
                    Layout.row: 0
                    Layout.column: 0
                    text: qsTr("Output Settings")
                    font.pixelSize: 20
                    Layout.alignment: Qt.AlignVCenter
                }
                RoundButton {
                    Layout.columnSpan: 1
                    Layout.row: 1
                    Layout.column: 0
                    text: py.qta.icon("mdi6.folder")
                    radius: this.height / 2
                    font.family: materialFontLoader.name
                    font.pixelSize: Qt.application.font.pixelSize * 1.5
                    onClicked: {
                        actions.chooseSavePath.trigger()
                    }
                }
                TextField {
                    id: saveFolderTextField
                    Layout.columnSpan: 7
                    Layout.row: 1
                    Layout.column: 1
                    Layout.preferredWidth: parent.width * 0.7
                    height: 50
                    placeholderText: qsTr("Output Folder")
                    text: py.config_items.get_save_folder()
                    onEditingFinished: {
                        if (py.config_items.set_save_folder(text) === true) {
                            saveFolderTextField.text = text
                        } else {
                            saveFolderTextField.text = py.config_items.get_save_folder()
                        }
                    }
                    Component.onCompleted: {
                        dialogs.save_folder_changed.connect( (value) => {
                            saveFolderTextField.text = value
                        })
                    }
                }
                Container {
                    id: startConversionContainer
                    Layout.rowSpan: 2
                    Layout.row: 1
                    Layout.columnSpan: 2
                    Layout.column: 8
                    Layout.preferredHeight: parent.height * 0.6
                    Layout.preferredWidth: parent.width * 0.2
                    contentItem: Item {
                        RoundButton {
                            anchors.fill: parent
                            radius: 10
                            enabled: taskListView.count > 0
                            opacity: (py.task_manager.is_busy() || !enabled) ? 0.5 : 1
                            background: Rectangle {
                                color: Material.color(
                                    Material.Indigo,
                                    Material.Shade500
                                )
                                radius: 10
                            }
                            contentItem: Label {
                                text: qsTr("Start Conversion")
                                wrapMode: Text.WordWrap
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignHCenter
                                color: "white"
                                Component.onCompleted: {
                                    py.task_manager.tasks_size_changed.connect(function() {
                                        text = py.task_manager.is_busy() ? qsTr("Converting") : qsTr("Start Conversion")
                                    })
                                    py.task_manager.busy_changed.connect(function(busy) {
                                        text = busy ? qsTr("Converting") : qsTr("Start Conversion")
                                    })
                                }
                            }
                            Component.onCompleted: {
                                py.task_manager.tasks_size_changed.connect(function() {
                                    enabled = taskListView.count > 0
                                    opacity = (py.task_manager.is_busy() || !enabled) ? 0.5 : 1
                                })
                                py.task_manager.busy_changed.connect(function(busy) {
                                    enabled = taskListView.count > 0
                                    opacity = (busy || !enabled) ? 0.5 : 1
                                })
                            }
                            onClicked: {
                                actions.startConversion.trigger()
                            }
                        }
                        BusyIndicator {
                            anchors.centerIn: parent
                            running: py.task_manager.is_busy()
                            visible: running
                            Component.onCompleted: {
                                py.task_manager.busy_changed.connect(function(busy) {
                                    running = visible = busy
                                })
                            }
                        }
                    }
                }
                Switch {
                    Layout.columnSpan: 3
                    Layout.row: 2
                    Layout.column: 0
                    Layout.preferredWidth: parent.width * 0.3
                    text: qsTr("Open Output Folder When Done")
                    checked: py.config_items.get_bool("open_save_folder_on_completion")
                    onClicked: {
                        py.config_items.set_bool("open_save_folder_on_completion", checked)
                        settingsDrawer.autoOpenSaveFolderChanged(checked)
                    }
                    Component.onCompleted: {
                        settingsDrawer.autoOpenSaveFolderChanged.connect( (value) => {
                            value === checked ? null : checked = value
                        })
                    }
                }
                Label {
                    Layout.columnSpan: 3
                    Layout.row: 2
                    Layout.column: 3
                    Layout.preferredWidth: parent.width * 0.3
                    text: qsTr("Deal with Same Name Files:")
                    Layout.alignment: Qt.AlignVCenter
                }
                ComboBox {
                    Layout.columnSpan: 2
                    Layout.row: 2
                    Layout.column: 6
                    Layout.preferredWidth: parent.width * 0.2
                    model: ["Overwrite", "Skip", "Prompt"]
                    onActivated: (index) => {
                        py.config_items.set_conflict_policy(currentValue)
                        settingsDrawer.conflictPolicyChanged(currentValue)
                    }
                    Component.onCompleted: {
                        currentIndex = indexOfValue(py.config_items.get_conflict_policy())
                        settingsDrawer.conflictPolicyChanged.connect( (value) => {
                            switch (value) {
                                case "Overwrite":
                                    currentIndex = 0
                                    break
                                case "Skip":
                                    currentIndex = 1
                                    break
                                case "Prompt":
                                    currentIndex = 2
                                    break
                            }
                        })
                    }
                }
            }
        }
    }
}