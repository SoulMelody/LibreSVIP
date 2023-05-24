import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import QtQuick.Shapes

Page {
    title: qsTr("Converter")

    property alias taskList: taskListView;
    property alias startConversionButton: startConversionBtn;
    property alias saveFolder: saveFolderTextField;
    property alias inputFormatComboBox: inputFormat;
    property alias outputFormatComboBox: outputFormat;
    property alias swapInputOutputButton: swapInputOutput;

    Component {
        id: colorPickerItem
        RowLayout {
            property var field: {}
            height: 30
            Layout.fillWidth: true
            Label {
                text: field.title + "："
                Layout.alignment: Qt.AlignVCenter
                font.pixelSize: 12
                fontSizeMode: Text.Fit
                wrapMode: Text.Wrap
                Layout.preferredWidth: 150
            }
            TextField {
                id: colorField
                Layout.fillWidth: true
                text: field.value
                onEditingFinished: {
                    field.value = this.text
                }
            }
            IconButton {
                icon_name: "mdi6.eyedropper-variant"
                diameter: 30
                icon_size_multiplier: 1.5
                onClicked: {
                    dialogs.colorDialog.bind_color(
                        colorField.text,
                        (color) => {
                            colorField.text = color
                            field.value = color
                        }
                    )
                }
            }
            IconButton {
                icon_name: "mdi6.help-circle-outline"
                diameter: 30
                icon_size_multiplier: 1.5
                cursor_shape: Qt.WhatsThisCursor
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
            }
        }
    }

    Component {
        id: switchItem
        RowLayout {
            property var field: {}
            height: 30
            Layout.fillWidth: true
            Label {
                text: field.title + "："
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
            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: "transparent"
            }
            IconButton {
                icon_name: "mdi6.help-circle-outline"
                diameter: 30
                icon_size_multiplier: 1.5
                cursor_shape: Qt.WhatsThisCursor
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
            }
        }
    }

    Component {
        id: comboBoxItem
        RowLayout {
            property var field: {}
            height: 30
            Layout.fillWidth: true
            Label {
                text: field.title + "："
                Layout.alignment: Qt.AlignVCenter
                font.pixelSize: 12
                fontSizeMode: Text.Fit
                wrapMode: Text.Wrap
                Layout.preferredWidth: 150
            }
            ComboBox {
                Layout.fillWidth: true
                textRole: "text"
                valueRole: "value"
                onActivated: {
                    field.value = this.currentValue
                }
                model: field.choices
            }
            IconButton {
                icon_name: "mdi6.help-circle-outline"
                diameter: 30
                icon_size_multiplier: 1.5
                cursor_shape: Qt.WhatsThisCursor
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
            }
        }
    }

    Component {
        id: textFieldItem
        RowLayout {
            property var field: {}
            height: 30
            Layout.fillWidth: true
            Label {
                Layout.alignment: Qt.AlignVCenter
                text: field.title + "："
                font.pixelSize: 12
                fontSizeMode: Text.Fit
                wrapMode: Text.Wrap
                Layout.preferredWidth: 150
            }
            TextField {
                Layout.fillWidth: true
                text: field.value
                onEditingFinished: {
                    field.value = this.text
                }
            }
            IconButton {
                icon_name: "mdi6.help-circle-outline"
                diameter: 30
                icon_size_multiplier: 1.5
                cursor_shape: Qt.WhatsThisCursor
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
            }
        }
    }

    Component {
        id: separatorItem
        RowLayout {
            Layout.fillWidth: true
            Label {
                text: py.qta.icon("mdi6.tune-variant")
                font.family: materialFontLoader.name
                font.pixelSize: 12
            }
            Rectangle {
                Layout.fillWidth: true
                color: Material.color(
                    Material.Grey,
                    Material.Shade300
                );
                height: 1
            }
        }
    }

    SplitView {
        anchors.fill: parent
        orientation: Qt.Horizontal

        SplitView {
            SplitView.fillHeight: true
            SplitView.preferredWidth: parent.width / 2
            SplitView.minimumWidth: parent.width * 0.45
            orientation: Qt.Vertical

            Control {
                SplitView.fillWidth: true
                SplitView.preferredHeight: 250
                SplitView.minimumHeight: 250
                SplitView.maximumHeight: parent.height * 0.4
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
                        Layout.fillWidth: true
                        height: 50
                        LabeledComboBox {
                            id: inputFormat
                            hint: qsTr("Input Format: ")
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
                                py.task_manager.input_format_changed.connect((input_format) => {
                                    let new_index = indexOfValue(input_format)
                                    if (new_index != currentIndex) {
                                        currentIndex = new_index
                                    }
                                    if (currentText != dialogs.openDialog.nameFilters[0]) {
                                        dialogs.openDialog.nameFilters[0] = currentText
                                    }
                                })
                                py.task_manager.set_str("input_format", currentValue)
                            }
                            width: parent.width
                            choices: py.task_manager.qget("input_formats")
                        }
                    }
                    IconButton {
                        Layout.columnSpan: 2
                        Layout.row: 1
                        Layout.column: 8
                        icon_name: "mdi6.information-outline"
                        diameter: 36
                        icon_size_multiplier: 1.5
                        onClicked: {
                            inputFormatInfo.opened ? inputFormatInfo.close() : inputFormatInfo.open()
                        }
                        Popup {
                            id: inputFormatInfo
                            y: 45
                            x: - width * 0.5
                            closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent
                            PluginInfo {
                                info: py.task_manager.plugin_info("input_format")
                                Component.onCompleted: {
                                    py.task_manager.input_format_changed.connect( (input_format) => {
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
                    IconButton {
                        id: swapInputOutput
                        Layout.columnSpan: 2
                        Layout.row: 2
                        Layout.column: 8
                        icon_name: "mdi6.swap-vertical"
                        diameter: 36
                        icon_size_multiplier: 1.5
                        ToolTip.visible: hovered
                        ToolTip.text: qsTr("Swap Input and Output")
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
                    }
                    Grid {
                        Layout.columnSpan: 8
                        Layout.row: 3
                        Layout.column: 0
                        Layout.fillWidth: true
                        height: 50
                        LabeledComboBox {
                            id: outputFormat
                            hint: qsTr("Output Format: ")
                            onActivated: (index) => {
                                py.task_manager.set_str("output_format", currentValue)
                            }
                            Component.onCompleted: {
                                py.task_manager.output_format_changed.connect((output_format) => {
                                    let new_index = indexOfValue(output_format)
                                    if (new_index != currentIndex) {
                                        currentIndex = new_index
                                    }
                                })
                                py.task_manager.set_str("output_format", currentValue)
                            }
                            width: parent.width
                            model: py.task_manager.qget("output_formats")
                        }
                    }
                    IconButton {
                        Layout.columnSpan: 2
                        Layout.row: 3
                        Layout.column: 8
                        icon_name: "mdi6.information-outline"
                        diameter: 36
                        icon_size_multiplier: 1.5
                        onClicked: {
                            outputFormatInfo.opened ? outputFormatInfo.close() : outputFormatInfo.open()
                        }
                        Popup {
                            id: outputFormatInfo
                            y: 45
                            x: - width * 0.5
                            closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent
                            PluginInfo {
                                info: py.task_manager.plugin_info("output_format")
                                Component.onCompleted: {
                                    py.task_manager.output_format_changed.connect( (output_format) => {
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

            DropArea {
                id: taskListArea
                SplitView.fillWidth: true
                SplitView.maximumHeight: parent.height - 250
                anchors.bottom: parent.bottom
                onDropped: (event) => {
                    py.task_manager.add_task_paths(event.urls.map(dialogs.url2path))
                }
                DashedRectangle {
                    anchors.fill: parent
                    anchors.margins: 12
                    radius: 8
                    visible: taskListView.count == 0
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        onEntered: {
                            if (taskListView.count == 0) {
                                parent.opacity = 0.5
                            }
                        }
                        onExited: {
                            if (parent.opacity < 1) {
                                parent.opacity = 1
                            }
                        }
                        onClicked: {
                            if (taskListView.count == 0) {
                                actions.openFile.trigger()
                            }
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
                        }
                    }
                }
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    visible: taskListView.count > 0
                    Label {
                        Layout.alignment: Qt.AlignTop
                        text: qsTr("Task List")
                        font.pixelSize: 20
                        height: 30
                    }
                    ScrollView {
                        Layout.alignment: Qt.AlignTop
                        Layout.fillHeight: true
                        Layout.fillWidth: true
                        contentWidth: availableWidth
                        ListView {
                            id: taskListView
                            Layout.fillWidth: true
                            model: py.task_manager.qget("tasks")
                            delegate: Qt.createComponent(
                                "task_row.qml"
                            )
                        }
                    }
                    Rectangle {
                        Layout.alignment: Qt.AlignBottom
                        color: "transparent"
                        Timer {
                            id: hideTaskToolbarTimer;
                            interval: 1000;
                            repeat: true;
                            triggeredOnStart: false;
                            onTriggered: {
                                if (
                                    toggleTaskToolbarButton.hovered ||
                                    addTaskButton.hovered ||
                                    clearTaskButton.hovered ||
                                    resetExtensionButton.hovered ||
                                    removeOtherExtensionButton.hovered
                                ) {
                                    return
                                }
                                toggleTaskToolbarButton.state = "collapsed"
                                this.stop()
                            }
                        }
                        RoundButton {
                            id: toggleTaskToolbarButton
                            states: [
                                State {
                                    name: "expanded"
                                    PropertyChanges {
                                        target: toggleTaskToolbarButton
                                        rotation: 45
                                    }
                                    PropertyChanges {
                                        target: taskToolbar
                                        shown: true
                                    }
                                },
                                State {
                                    name: "collapsed"
                                    PropertyChanges {
                                        target: toggleTaskToolbarButton
                                        rotation: 0
                                    }
                                    PropertyChanges {
                                        target: taskToolbar
                                        shown: false
                                    }
                                }
                            ]
                            state: "collapsed"
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
                                RotationAnimation {
                                    duration: 200
                                    easing.type: Easing.InOutQuad
                                }
                            }
                            onHoveredChanged: {
                                if (hovered) {
                                    hideTaskToolbarTimer.stop()
                                    state = "expanded"
                                }
                                else if (!hideTaskToolbarTimer.running) {
                                    hideTaskToolbarTimer.start()
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
                                    id: addTaskButton
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
                                    ToolTip.visible: hovered
                                    ToolTip.text: qsTr("Continue Adding files")
                                    onHoveredChanged: {
                                        if (!hovered && !hideTaskToolbarTimer.running) {
                                            hideTaskToolbarTimer.start()
                                        }
                                    }
                                    onClicked: {
                                        actions.openFile.trigger()
                                    }
                                }
                                RoundButton {
                                    id: clearTaskButton
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
                                    enabled: taskListView.count > 0
                                    ToolTip.visible: hovered
                                    ToolTip.text: qsTr("Clear Task List")
                                    onHoveredChanged: {
                                        if (!hovered && !hideTaskToolbarTimer.running) {
                                            hideTaskToolbarTimer.start()
                                        }
                                    }
                                    onClicked: {
                                        actions.clearTasks.trigger()
                                    }
                                }
                                RoundButton {
                                    id: resetExtensionButton
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
                                    ToolTip.visible: hovered
                                    ToolTip.text: qsTr("Reset Default Extension")
                                    onHoveredChanged: {
                                        if (!hovered && !hideTaskToolbarTimer.running) {
                                            hideTaskToolbarTimer.start()
                                        }
                                    }
                                    onClicked: {
                                        py.task_manager.reset_stems()
                                    }
                                }
                                RoundButton {
                                    id: removeOtherExtensionButton
                                    text: py.qta.icon("mdi6.filter-minus-outline")
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
                                    ToolTip.visible: hovered
                                    ToolTip.text: qsTr("Remove Tasks With Other Extensions")
                                    onHoveredChanged: {
                                        if (!hovered && !hideTaskToolbarTimer.running) {
                                            hideTaskToolbarTimer.start()
                                        }
                                    }
                                    onClicked: {
                                        for (var i = 0; i < taskListView.count; i++) {
                                            var task = taskListView.model.get(i)
                                            let extension = task.path.lastIndexOf(".") > -1 ? task.path.slice(task.path.lastIndexOf(".") + 1) : ""
                                            if (extension != inputFormat.currentValue) {
                                                taskListView.model.delete(i)
                                                i--
                                            }
                                        }
                                    }
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
        }

        SplitView {
            anchors.right: parent.right
            SplitView.fillHeight: true
            SplitView.preferredWidth: parent.width / 2
            SplitView.minimumWidth: parent.width * 0.45
            orientation: Qt.Vertical

            ScrollView {
                id: advancedSettings
                SplitView.fillWidth: true
                SplitView.preferredHeight: parent.height - 200
                SplitView.minimumHeight: parent.height - 250
                SplitView.maximumHeight: parent.height - 150
                contentWidth: availableWidth
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
                    anchors.topMargin: 20
                    anchors.leftMargin: 20
                    anchors.rightMargin: 10
                    Layout.fillWidth: true
                    Label {
                        text: qsTr("Advanced Settings")
                        font.pixelSize: 20
                        Layout.alignment: Qt.AlignVCenter
                    }
                    ColumnLayout {
                        Layout.fillWidth: true
                        Row {
                            height: 30
                            visible: inputFields.count > 0
                            Layout.fillWidth: true
                            RoundButton {
                                Layout.fillHeight: true
                                radius: this.height / 2
                                anchors.verticalCenter: parent.verticalCenter
                                contentItem: Label {
                                    text: py.qta.icon("mdi6.chevron-right")
                                    font.family: materialFontLoader.name
                                    font.pixelSize: 20
                                    rotation: inputContainer.expanded ? 45 : 0
                                    Behavior on rotation {
                                        RotationAnimation {
                                            duration: 500
                                            easing.type: Easing.InOutQuad
                                        }
                                    }
                                }
                                background: Rectangle {
                                    color: "transparent"
                                }
                                onClicked: {
                                    inputContainer.expanded = !inputContainer.expanded
                                }
                            }
                            Label {
                                text: qsTr("Input Options")
                                font.pixelSize: 22
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            Rectangle {
                                width: 20
                                height: 1
                                color: "transparent"
                            }
                            Label {
                                property string input_format_name: ""
                                text: qsTr("[Import as ") + input_format_name + qsTr(" Format]")
                                color: Material.color(
                                    Material.Grey
                                )
                                font.pixelSize: 20
                                anchors.verticalCenter: parent.verticalCenter
                                Component.onCompleted: {
                                    py.task_manager.input_format_changed.connect((input_format) => {
                                        let plugin_info = py.task_manager.plugin_info("input_format")
                                        input_format_name = plugin_info.name
                                    })
                                }
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            Rectangle {
                                width: 40
                            }
                            ColumnLayout {
                                id: inputContainer
                                property bool expanded: true
                                Layout.fillWidth: true
                                states: [
                                    State {
                                        name: "expanded"
                                        PropertyChanges {
                                            target: inputContainer
                                            Layout.maximumHeight: inputContainer.implicitHeight
                                            opacity: 1
                                            y: 0
                                            visible: true
                                        }
                                    },
                                    State {
                                        name: "collapsed"
                                        PropertyChanges {
                                            target: inputContainer
                                            Layout.maximumHeight: 0
                                            opacity: 0
                                            y: -inputContainer.implicitHeight
                                            visible: false
                                        }
                                    }
                                ]
                                state: expanded ? "expanded" : "collapsed"

                                transitions: [
                                    Transition {
                                        from: "expanded"
                                        to: "collapsed"
                                        PropertyAnimation {
                                            target: inputContainer
                                            properties: "y,opacity,Layout.maximumHeight,visible"
                                            duration: 500
                                            easing.type: Easing.InOutQuad
                                        }
                                    },

                                    Transition {
                                        from: "collapsed"
                                        to: "expanded"
                                        PropertyAnimation {
                                            target: inputContainer
                                            properties: "y,opacity,Layout.maximumHeight,visible"
                                            duration: 500
                                            easing.type: Easing.InOutQuad
                                        }
                                    }
                                ]
                            }
                        }
                        ListView {
                            id: inputFields
                            model: py.task_manager.qget("input_fields")
                            delegate: Column {
                                Component.onCompleted: {
                                    let separator_item = separatorItem.createObject(inputContainer)
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
                                            item = colorPickerItem.createObject(inputContainer, {
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
                        Row {
                            height: 30
                            visible: outputFields.count > 0
                            Layout.fillWidth: true
                            RoundButton {
                                Layout.fillHeight: true
                                radius: this.height / 2
                                anchors.verticalCenter: parent.verticalCenter
                                contentItem: Label {
                                    text: py.qta.icon("mdi6.chevron-right")
                                    font.family: materialFontLoader.name
                                    font.pixelSize: 20
                                    rotation: outputContainer.expanded ? 45 : 0
                                    Behavior on rotation {
                                        RotationAnimation {
                                            duration: 500
                                            easing.type: Easing.InOutQuad
                                        }
                                    }
                                }
                                background: Rectangle {
                                    color: "transparent"
                                }
                                onClicked: {
                                    outputContainer.expanded = !outputContainer.expanded
                                }
                            }
                            Label {
                                text: qsTr("Output Options")
                                font.pixelSize: 22
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            Rectangle {
                                width: 20
                                height: 1
                                color: "transparent"
                            }
                            Label {
                                property string output_format_name: ""
                                text: qsTr("[Export to ") + output_format_name + qsTr(" Format]")
                                font.pixelSize: 20
                                color: Material.color(
                                    Material.Grey
                                )
                                anchors.verticalCenter: parent.verticalCenter
                                Component.onCompleted: {
                                    py.task_manager.output_format_changed.connect((output_format) => {
                                        let plugin_info = py.task_manager.plugin_info("output_format")
                                        output_format_name = plugin_info.name
                                    })
                                }
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            Rectangle {
                                width: 40
                            }
                            ColumnLayout {
                                id: outputContainer
                                property bool expanded: true
                                Layout.fillWidth: true
                                states: [
                                    State {
                                        name: "expanded"
                                        PropertyChanges {
                                            target: outputContainer
                                            Layout.maximumHeight: outputContainer.implicitHeight
                                            opacity: 1
                                            y: 0
                                            visible: true
                                        }
                                    },
                                    State {
                                        name: "collapsed"
                                        PropertyChanges {
                                            target: outputContainer
                                            Layout.maximumHeight: 0
                                            opacity: 0
                                            y: -outputContainer.implicitHeight
                                            visible: false
                                        }
                                    }
                                ]
                                state: expanded ? "expanded" : "collapsed"

                                transitions: [
                                    Transition {
                                        from: "expanded"
                                        to: "collapsed"
                                        PropertyAnimation {
                                            target: outputContainer
                                            properties: "y,opacity,Layout.maximumHeight,visible"
                                            duration: 500
                                            easing.type: Easing.InOutQuad
                                        }
                                    },

                                    Transition {
                                        from: "collapsed"
                                        to: "expanded"
                                        PropertyAnimation {
                                            target: outputContainer
                                            properties: "y,opacity,Layout.maximumHeight,visible"
                                            duration: 500
                                            easing.type: Easing.InOutQuad
                                        }
                                    }
                                ]
                            }
                        }
                        ListView {
                            id: outputFields
                            model: py.task_manager.qget("output_fields")
                            delegate: Column {
                                Component.onCompleted: {
                                    let separator_item = separatorItem.createObject(outputContainer)
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
                    Rectangle {
                        Layout.fillWidth: true
                        height: 10
                        color: "transparent"
                    }
                }
            }

            Control {
                SplitView.fillWidth: true
                SplitView.minimumHeight: 150
                anchors.bottom: parent.bottom
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
                    IconButton {
                        Layout.columnSpan: 1
                        Layout.row: 1
                        Layout.column: 0
                        icon_name: "mdi6.folder"
                        icon_size_multiplier: 1.5
                        ToolTip.visible: hovered
                        ToolTip.text: qsTr("Choose Output Folder")
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
                    Item {
                        Layout.rowSpan: 2
                        Layout.row: 1
                        Layout.columnSpan: 2
                        Layout.column: 8
                        Layout.preferredHeight: parent.height * 0.6
                        Layout.preferredWidth: parent.width * 0.2
                        RoundButton {
                            id: startConversionBtn
                            property color base_color: Material.color(
                                Material.Indigo
                            )
                            property int anim_index: 10
                            property bool anim_running: false
                            anchors.fill: parent
                            radius: 10
                            enabled: taskListView.count > 0
                            opacity: enabled ? 1 : 0.7
                            background: Rectangle {
                                color: startConversionBtn.base_color
                                radius: 10
                                gradient: LinearGradient {
                                    orientation: Gradient.Horizontal
                                    GradientStop {
                                        position: 0
                                        color: startConversionBtn.anim_running && startConversionBtn.anim_index < 0 ? Qt.lighter(startConversionBtn.base_color, 1.25) : startConversionBtn.base_color
                                    }
                                    GradientStop {
                                        position: startConversionBtn.anim_index / 10 - 0.01
                                        color: startConversionBtn.anim_running && startConversionBtn.anim_index < 0 ? Qt.lighter(startConversionBtn.base_color, 1.25) : startConversionBtn.base_color
                                    }
                                    GradientStop {
                                        position: startConversionBtn.anim_index / 10
                                        color: startConversionBtn.anim_running ? Qt.lighter(startConversionBtn.base_color, 1.25) : startConversionBtn.base_color
                                    }
                                    GradientStop {
                                        position: (startConversionBtn.anim_index + 2) / 10
                                        color: startConversionBtn.anim_running ? Qt.lighter(startConversionBtn.base_color, 1.25) : startConversionBtn.base_color
                                    }
                                    GradientStop {
                                        position: (startConversionBtn.anim_index + 2) / 10 + 0.01
                                        color: startConversionBtn.anim_running && startConversionBtn.anim_index > 8 ? Qt.lighter(startConversionBtn.base_color, 1.25) : startConversionBtn.base_color
                                    }
                                    GradientStop {
                                        position: 1
                                        color: startConversionBtn.anim_running && startConversionBtn.anim_index > 8 ? Qt.lighter(startConversionBtn.base_color, 1.25) : startConversionBtn.base_color
                                    }
                                }
                                SequentialAnimation {
                                    running: startConversionBtn.anim_running
                                    loops: Animation.Infinite
                                    NumberAnimation {
                                        target: startConversionBtn
                                        property: "anim_index"
                                        from: -2
                                        to: 10
                                        duration: 2000
                                    }
                                }
                            }
                            contentItem: Label {
                                text: qsTr("Start Conversion")
                                wrapMode: Text.WordWrap
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignHCenter
                                color: "white"
                            }
                            onClicked: {
                                actions.startConversion.trigger()
                            }
                            Connections {
                                target: taskListView.model
                                function onRowsInserted(idx, first, last) {
                                    startConversionBtn.enabled = true
                                }
                                function onRowsRemoved(idx, first, last) {
                                    startConversionBtn.enabled = !(first == 0 && last == taskListView.count - 1)
                                }
                            }
                            Connections {
                                target: py.task_manager
                                function onBusy_changed(busy) {
                                    startConversionBtn.contentItem.text = busy ? qsTr("Converting") : qsTr("Start Conversion")
                                    startConversionBtn.enabled = taskListView.count > 0 && !busy
                                    startConversionBtn.anim_running = busy
                                }
                            }
                        }
                    }
                    Switch {
                        Layout.columnSpan: 4
                        Layout.row: 2
                        Layout.column: 0
                        Layout.preferredWidth: parent.width * 0.4
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
                        Layout.columnSpan: 2
                        Layout.row: 2
                        Layout.column: 4
                        Layout.preferredWidth: parent.width * 0.2
                        Layout.alignment: Qt.AlignVCenter
                        text: qsTr("Deal with Conflicts:")
                        elide: Text.ElideRight
                    }
                    ComboBox {
                        Layout.columnSpan: 2
                        Layout.row: 2
                        Layout.column: 6
                        Layout.preferredWidth: parent.width * 0.2
                        textRole: "text"
                        valueRole: "value"
                        model: [
                            {value: "Overwrite", text: qsTr("Overwrite")},
                            {value: "Skip", text: qsTr("Skip")},
                            {value: "Prompt", text: qsTr("Prompt")}
                        ]
                        onActivated: (index) => {
                            py.config_items.set_conflict_policy(currentValue)
                            settingsDrawer.conflictPolicyChanged(currentValue)
                        }
                        Component.onCompleted: {
                            currentIndex = indexOfValue(py.config_items.get_conflict_policy())
                            settingsDrawer.conflictPolicyChanged.connect( (value) => {
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
            }
        }
    }
}