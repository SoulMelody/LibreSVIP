import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import QtQuick.Shapes
import LibreSVIP

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
            property int index
            property QtObject list_view
            height: 40
            Layout.fillWidth: true
            Label {
                text: qsTr(field.title) + "："
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
                    list_view.model.update(index, {value: text})
                }
            }
            IconButton {
                icon_name: "mdi7.eyedropper-variant"
                diameter: 30
                icon_size_multiplier: 1.5
                onClicked: {
                    dialogs.colorDialog.bind_color(
                        colorField.text,
                        (color) => {
                            colorField.text = color
                            list_view.model.update(index, {value: colorField.text})
                        }
                    )
                }
            }
            IconButton {
                icon_name: "mdi7.help-circle-outline"
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
                    text: qsTr(field.description)
                }
            }
        }
    }

    Component {
        id: switchItem
        RowLayout {
            property var field: {}
            property int index
            property QtObject list_view
            height: 40
            Layout.fillWidth: true
            Label {
                text: qsTr(field.title) + "："
                Layout.alignment: Qt.AlignVCenter
                font.pixelSize: 12
                fontSizeMode: Text.Fit
                wrapMode: Text.Wrap
                Layout.preferredWidth: 150
            }
            Switch {
                Component.onCompleted: {
                    this.checked = field.value
                }
                onCheckedChanged: {
                    list_view.model.update(index, {value: this.checked})
                }
            }
            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: "transparent"
            }
            IconButton {
                icon_name: "mdi7.help-circle-outline"
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
                    text: qsTr(field.description)
                }
            }
        }
    }

    Component {
        id: comboBoxItem
        RowLayout {
            id: comboBoxRow
            property var field: {}
            property int index
            property QtObject list_view
            height: 40
            Layout.fillWidth: true
            Label {
                text: qsTr(field.title) + "："
                Layout.alignment: Qt.AlignVCenter
                font.pixelSize: 12
                fontSizeMode: Text.Fit
                wrapMode: Text.Wrap
                Layout.preferredWidth: 150
            }
            ComboBox {
                id: comboBox
                Layout.fillWidth: true
                textRole: "text"
                valueRole: "value"
                displayText: qsTr(currentText)
                delegate: MenuItem {
                    width: ListView.view.width
                    contentItem: Label {
                        text: comboBox.textRole
                            ? qsTr(Array.isArray(comboBox.model) ? modelData[comboBox.textRole] : model[comboBox.textRole])
                            : qsTr(modelData)
                        color: comboBox.highlightedIndex === index ? Material.accentColor : window.Material.foreground
                        ToolTip.visible: hovered && modelData["desc"]
                        ToolTip.text: qsTr(modelData["desc"] || "")
                        ToolTip.delay: 500
                    }
                    highlighted: comboBox.highlightedIndex === index
                    hoverEnabled: comboBox.hoverEnabled
                }

                popup: Popup {
                    y: comboBox.height
                    width: comboBox.width
                    padding: 1

                    contentItem: ListView {
                        clip: true
                        implicitHeight: contentHeight
                        model: comboBox.popup.visible ? comboBox.delegateModel : null
                        currentIndex: comboBox.highlightedIndex

                        ScrollIndicator.vertical: ScrollIndicator { }
                    }
                }

                Component.onCompleted: {
                    this.currentIndex = indexOfValue(field.value)
                }
                onActivated: (index) => {
                    list_view.model.update(comboBoxRow.index, {value: this.currentValue})
                }
                model: field.choices
            }
            IconButton {
                icon_name: "mdi7.help-circle-outline"
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
                    text: qsTr(field.description)
                }
            }
        }
    }

    Component {
        id: textFieldItem
        RowLayout {
            property var field: {}
            property int index
            property QtObject list_view
            height: 40
            Layout.fillWidth: true
            Label {
                Layout.alignment: Qt.AlignVCenter
                text: qsTr(field.title) + "："
                font.pixelSize: 12
                fontSizeMode: Text.Fit
                wrapMode: Text.Wrap
                Layout.preferredWidth: 150
            }
            TextField {
                Layout.fillWidth: true
                text: field.value
                Component.onCompleted: {
                    switch (field.type) {
                        case "int":
                            validator = Qt.createQmlObject('import QtQuick; IntValidator {}', this)
                            break
                        case "float":
                            validator = Qt.createQmlObject('import QtQuick; DoubleValidator {}', this)
                            break
                        default:
                            break
                    }
                }
                onEditingFinished: {
                    list_view.model.update(index, {value: text})
                }
            }
            IconButton {
                icon_name: "mdi7.help-circle-outline"
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
                    text: qsTr(field.description)
                }
            }
        }
    }

    Component {
        id: separatorItem
        RowLayout {
            Layout.fillWidth: true
            Label {
                text: IconicFontLoader.icon("mdi7.tune-variant")
                font.family: "Material Design Icons"
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

    ColumnLayout {
        id: selectFormatCard
        Layout.fillWidth: true
        Label {
            text: qsTr("Select File Formats")
            font.pixelSize: 20
            Layout.alignment: Qt.AlignVCenter
        }
        ColumnLayout {
            Layout.fillWidth: true
            RowLayout {
                Layout.fillWidth: true
                Grid {
                    Layout.fillWidth: true
                    height: 50
                    LabeledComboBox {
                        id: inputFormat
                        hint: qsTr("Input Format: ")
                        onActivated: (index) => {
                            if (
                                resetTasksOnInputChange.checked &&
                                TaskManager.get_str("input_format") != currentValue
                            ) {
                                actions.clearTasks.trigger()
                            }
                            TaskManager.set_str("input_format", currentValue)
                        }
                        Component.onCompleted: {
                            let last_input_format = TaskManager.get_str("input_format")
                            if (last_input_format != null) {
                                this.currentIndex = indexOfValue(last_input_format)
                            }
                            dialogs.openDialog.nameFilters[0] = qsTr(currentText) + " (*." + currentValue + ")"
                            TaskManager.input_format_changed.connect((input_format) => {
                                let new_index = indexOfValue(input_format)
                                if (new_index != currentIndex) {
                                    currentIndex = new_index
                                }
                                let name_filter = qsTr(currentText) + " (*." + currentValue + ")"
                                if (name_filter != dialogs.openDialog.nameFilters[0]) {
                                    dialogs.openDialog.nameFilters[0] = name_filter
                                }
                            })
                            TaskManager.set_str("input_format", currentValue)
                        }
                        width: parent.width
                        choices: TaskManager.qget("input_formats")
                    }
                }
                IconButton {
                    icon_name: "mdi7.information-outline"
                    diameter: 38
                    icon_size_multiplier: 1.5
                    ToolTip.visible: hovered
                    ToolTip.text: qsTr("View Detail Information")
                    onClicked: {
                        inputInfoPowerAnimation.running = true
                        inputFormatInfo.opened ? inputFormatInfo.close() : inputFormatInfo.open()
                    }
                    Rectangle {
                        id: inputInfoPower
                        height: width
                        radius: width / 2
                        anchors.centerIn: parent
                        color: Material.color(Material.Grey, Material.Shade400)
                        SequentialAnimation {
                            id: inputInfoPowerAnimation
                            running: false
                            loops: 1
                            PropertyAnimation {
                                target: inputInfoPower
                                property: "visible"
                                from: false
                                to: true
                                duration: 0
                            }
                            NumberAnimation {
                                target: inputInfoPower
                                property: "opacity"
                                from: 0
                                to: 1
                                duration: 0
                            }
                            NumberAnimation {
                                target: inputInfoPower
                                property: "width"
                                from: 0
                                to: 100
                                duration: 250
                                easing.type: Easing.InQuad
                            }
                            NumberAnimation {
                                target: inputInfoPower
                                property: "opacity"
                                from: 1
                                to: 0
                                duration: 50
                                easing.type: Easing.OutQuad
                            }
                            PropertyAnimation {
                                target: inputInfoPower
                                property: "visible"
                                from: true
                                to: false
                                duration: 0
                            }
                        }
                    }
                    Popup {
                        id: inputFormatInfo
                        y: 45
                        x: - width * 0.5
                        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent
                        contentItem: PluginInfo {
                            info: TaskManager.plugin_info("input_format")
                            Component.onCompleted: {
                                TaskManager.input_format_changed.connect( (input_format) => {
                                    info = TaskManager.plugin_info("input_format")
                                })
                            }
                        }
                    }
                }
            }
            RowLayout {
                Layout.fillWidth: true
                Switch {
                    id: resetTasksOnInputChange
                    height: 40
                    text: qsTr("Reset Tasks When Changing Input")
                    checked: ConfigItems.get_bool("reset_tasks_on_input_change")
                    onClicked: {
                        ConfigItems.set_bool("reset_tasks_on_input_change", checked)
                        dialogs.settingsDialog.resetTasksOnInputChangeChanged(checked)
                    }
                    Connections {
                        target: dialogs.settingsDialog
                        function onResetTasksOnInputChangeChanged(value) {
                            value === resetTasksOnInputChange.checked ? null : resetTasksOnInputChange.checked = value
                        }
                    }
                }
                Item {
                    Layout.fillWidth: true
                }
                Switch {
                    height: 40
                    text: qsTr("Auto-Detect Input File Type")
                    checked: ConfigItems.get_bool("auto_detect_input_format")
                    onClicked: {
                        ConfigItems.set_bool("auto_detect_input_format", checked)
                        dialogs.settingsDialog.autoDetectInputFormatChanged(checked)
                    }
                    Component.onCompleted: {
                        dialogs.settingsDialog.autoDetectInputFormatChanged.connect( (value) => {
                            value === checked ? null : checked = value
                        })
                    }
                }
                Item {
                    Layout.fillWidth: true
                }
                IconButton {
                    id: swapInputOutput
                    icon_name: "mdi7.swap-vertical"
                    diameter: 38
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
                        TaskManager.set_str("input_format", inputFormat.currentValue)
                        TaskManager.set_str("output_format", outputFormat.currentValue)
                    }
                }
            }
            RowLayout {
                Grid {
                    Layout.fillWidth: true
                    height: 50
                    LabeledComboBox {
                        id: outputFormat
                        hint: qsTr("Output Format: ")
                        onActivated: (index) => {
                            TaskManager.set_str("output_format", currentValue)
                        }
                        Component.onCompleted: {
                            let last_output_format = TaskManager.get_str("output_format")
                            if (last_output_format != null) {
                                this.currentIndex = indexOfValue(last_output_format)
                            }
                            TaskManager.output_format_changed.connect((output_format) => {
                                let new_index = indexOfValue(output_format)
                                if (new_index != currentIndex) {
                                    currentIndex = new_index
                                }
                            })
                            TaskManager.set_str("output_format", currentValue)
                        }
                        width: parent.width
                        model: TaskManager.qget("output_formats")
                    }
                }
                IconButton {
                    icon_name: "mdi7.information-outline"
                    diameter: 38
                    icon_size_multiplier: 1.5
                    ToolTip.visible: hovered
                    ToolTip.text: qsTr("View Detail Information")
                    onClicked: {
                        outputInfoPowerAnimation.running = true
                        outputFormatInfo.opened ? outputFormatInfo.close() : outputFormatInfo.open()
                    }
                    Rectangle {
                        id: outputInfoPower
                        height: width
                        radius: width / 2
                        anchors.centerIn: parent
                        color: Material.color(Material.Grey, Material.Shade400)
                        SequentialAnimation {
                            id: outputInfoPowerAnimation
                            running: false
                            loops: 1
                            PropertyAnimation {
                                target: outputInfoPower
                                property: "visible"
                                from: false
                                to: true
                                duration: 0
                            }
                            NumberAnimation {
                                target: outputInfoPower
                                property: "opacity"
                                from: 0
                                to: 1
                                duration: 0
                            }
                            NumberAnimation {
                                target: outputInfoPower
                                property: "width"
                                from: 0
                                to: 100
                                duration: 250
                                easing.type: Easing.InQuad
                            }
                            NumberAnimation {
                                target: outputInfoPower
                                property: "opacity"
                                from: 1
                                to: 0
                                duration: 50
                                easing.type: Easing.OutQuad
                            }
                            PropertyAnimation {
                                target: outputInfoPower
                                property: "visible"
                                from: true
                                to: false
                                duration: 0
                            }
                        }
                    }
                    Popup {
                        id: outputFormatInfo
                        y: 45
                        x: - width * 0.5
                        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent
                        contentItem: PluginInfo {
                            info: TaskManager.plugin_info("output_format")
                            Component.onCompleted: {
                                TaskManager.output_format_changed.connect( (output_format) => {
                                    info = TaskManager.plugin_info("output_format")
                                })
                            }
                        }
                    }
                }
            }
            RowLayout {
                Switch {
                    height: 40
                    text: qsTr("Set Output File Extension Automatically")
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
        }
    }

    DropArea {
        id: taskListArea
        onDropped: (event) => {
            TaskManager.add_task_paths(event.urls.map(dialogs.url2path))
        }
        DashedRectangle {
            anchors.fill: parent
            anchors.margins: 12
            radius: 8
            visible: taskListView.count == 0
            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
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
                        text: IconicFontLoader.icon("mdi7.tray-arrow-up")
                        font.family: "Material Design Icons"
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
                    model: TaskManager.qget("tasks")
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
                    text: IconicFontLoader.icon("mdi7.hammer-wrench")
                    y: parent.height - this.height / 2 - 10
                    font.family: "Material Design Icons"
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
                            text: IconicFontLoader.icon("mdi7.plus")
                            background: Rectangle {
                                radius: this.height / 2
                                color: Material.color(
                                    Material.LightBlue,
                                    Material.Shade200
                                );
                            }
                            font.family: "Material Design Icons"
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
                            text: IconicFontLoader.icon("mdi7.refresh")
                            background: Rectangle {
                                radius: this.height / 2
                                color: Material.color(
                                    Material.LightBlue,
                                    Material.Shade200
                                );
                            }
                            font.family: "Material Design Icons"
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
                            text: IconicFontLoader.icon("mdi7.form-textbox")
                            background: Rectangle {
                                radius: this.height / 2
                                color: Material.color(
                                    Material.LightBlue,
                                    Material.Shade200
                                );
                            }
                            font.family: "Material Design Icons"
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
                                TaskManager.reset_stems()
                            }
                        }
                        RoundButton {
                            id: removeOtherExtensionButton
                            text: IconicFontLoader.icon("mdi7.filter-minus-outline")
                            background: Rectangle {
                                radius: this.height / 2
                                color: Material.color(
                                    Material.LightBlue,
                                    Material.Shade200
                                );
                            }
                            font.family: "Material Design Icons"
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
    ColumnLayout {
        id: advancedSettingsColumn
        Label {
            text: qsTr("Advanced Settings")
            font.pixelSize: 20
            Layout.alignment: Qt.AlignVCenter
        }
        ColumnLayout {
            Layout.fillWidth: true
            Row {
                height: 30
                visible: inputContainer.children.length > 0
                Layout.fillWidth: true
                RoundButton {
                    Layout.fillHeight: true
                    radius: this.height / 2
                    anchors.verticalCenter: parent.verticalCenter
                    contentItem: Label {
                        text: IconicFontLoader.icon("mdi7.chevron-right")
                        font.family: "Material Design Icons"
                        font.pixelSize: 20
                        rotation: inputContainer.expanded ? 45 : 0
                        Behavior on rotation {
                            RotationAnimation {
                                duration: 300
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
                    text: qsTr("[Import as ") + qsTr(input_format_name) + "]"
                    color: Material.color(
                        Material.Grey
                    )
                    font.pixelSize: 20
                    anchors.verticalCenter: parent.verticalCenter
                    Component.onCompleted: {
                        TaskManager.input_format_changed.connect((input_format) => {
                            let plugin_info = TaskManager.plugin_info("input_format")
                            input_format_name = plugin_info.file_format
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
                                duration: 300
                                easing.type: Easing.InOutQuad
                            }
                        },

                        Transition {
                            from: "collapsed"
                            to: "expanded"
                            PropertyAnimation {
                                target: inputContainer
                                properties: "y,opacity,Layout.maximumHeight,visible"
                                duration: 300
                                easing.type: Easing.InOutQuad
                            }
                        }
                    ]
                }
                Rectangle {
                    width: 20
                }
            }
            ListView {
                id: inputFields
                model: TaskManager.qget("input_fields")
                delegate: Column {
                    Component.onCompleted: {
                        if (index == 0) {
                            for (var i = 0; i < inputFields.count; i++) {
                                let model = inputFields.model.get(i)
                                let separator_item = separatorItem.createObject(inputContainer)
                                this.Component.onDestruction.connect(separator_item.destroy)
                                let item = null;
                                switch (model.type) {
                                    case "bool": {
                                        item = switchItem.createObject(inputContainer, {
                                            "field": model,
                                            "index": i,
                                            "list_view": inputFields
                                        })
                                        break
                                    }
                                    case "enum": {
                                        item = comboBoxItem.createObject(inputContainer, {
                                            "field": model,
                                            "index": i,
                                            "list_view": inputFields
                                        })
                                        break
                                    }
                                    case "color" : {
                                        item = colorPickerItem.createObject(inputContainer, {
                                            "field": model,
                                            "index": i,
                                            "list_view": inputFields
                                        })
                                        break
                                    }
                                    default: {
                                        item = textFieldItem.createObject(inputContainer, {
                                            "field": model,
                                            "index": i,
                                            "list_view": inputFields,
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
            Row {
                height: 30
                visible: outputContainer.children.length > 0
                Layout.fillWidth: true
                RoundButton {
                    Layout.fillHeight: true
                    radius: this.height / 2
                    anchors.verticalCenter: parent.verticalCenter
                    contentItem: Label {
                        text: IconicFontLoader.icon("mdi7.chevron-right")
                        font.family: "Material Design Icons"
                        font.pixelSize: 20
                        rotation: outputContainer.expanded ? 45 : 0
                        Behavior on rotation {
                            RotationAnimation {
                                duration: 300
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
                    text: qsTr("[Export to ") + qsTr(output_format_name) + "]"
                    font.pixelSize: 20
                    color: Material.color(
                        Material.Grey
                    )
                    anchors.verticalCenter: parent.verticalCenter
                    Component.onCompleted: {
                        TaskManager.output_format_changed.connect((output_format) => {
                            let plugin_info = TaskManager.plugin_info("output_format")
                            output_format_name = plugin_info.file_format
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
                                duration: 300
                                easing.type: Easing.InOutQuad
                            }
                        },

                        Transition {
                            from: "collapsed"
                            to: "expanded"
                            PropertyAnimation {
                                target: outputContainer
                                properties: "y,opacity,Layout.maximumHeight,visible"
                                duration: 300
                                easing.type: Easing.InOutQuad
                            }
                        }
                    ]
                }
                Rectangle {
                    width: 20
                }
            }
            ListView {
                id: outputFields
                model: TaskManager.qget("output_fields")
                delegate: Column {
                    Component.onCompleted: {
                        if (index == 0) {
                            for (var i = 0; i < outputFields.count; i++) {
                                let model = outputFields.model.get(i)
                                let separator_item = separatorItem.createObject(outputContainer)
                                this.Component.onDestruction.connect(separator_item.destroy)
                                let item = null;
                                switch (model.type) {
                                    case "bool": {
                                        item = switchItem.createObject(outputContainer, {
                                            "field": model,
                                            "index": i,
                                            "list_view": outputFields
                                        })
                                        break
                                    }
                                    case "enum": {
                                        item = comboBoxItem.createObject(outputContainer, {
                                            "field": model,
                                            "index": i,
                                            "list_view": outputFields
                                        })
                                        break
                                    }
                                    case "color" : {
                                        item = colorPickerItem.createObject(outputContainer, {
                                            "field": model,
                                            "index": i,
                                            "list_view": outputFields
                                        })
                                        break
                                    }
                                    default: {
                                        item = textFieldItem.createObject(outputContainer, {
                                            "field": model,
                                            "index": i,
                                            "list_view": outputFields
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
    }
    
    ColumnLayout {
        id: outputSettingsCard
        RowLayout {
            Label {
                Layout.fillWidth: true
                text: qsTr("Output Settings")
                font.pixelSize: 20
                Layout.alignment: Qt.AlignVCenter
            }
            Switch {
                text: qsTr("Open Output Folder When Done")
                checked: ConfigItems.get_bool("open_save_folder_on_completion")
                onClicked: {
                    ConfigItems.set_bool("open_save_folder_on_completion", checked)
                    dialogs.settingsDialog.autoOpenSaveFolderChanged(checked)
                }
                Component.onCompleted: {
                    dialogs.settingsDialog.autoOpenSaveFolderChanged.connect( (value) => {
                        value === checked ? null : checked = value
                    })
                }
            }
        }
        RowLayout {
            Layout.fillWidth: true
            layoutDirection: Qt.RightToLeft
            Item {
                Layout.fillHeight: true
                Layout.minimumWidth: 150
                Layout.margins: 15
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
                        target: TaskManager
                        function onBusy_changed(busy) {
                            startConversionBtn.contentItem.text = busy ? qsTr("Converting") : qsTr("Start Conversion")
                            startConversionBtn.enabled = taskListView.count > 0 && !busy
                            startConversionBtn.anim_running = busy
                        }
                    }
                }
            }
            ColumnLayout {
                RowLayout {
                    IconButton {
                        icon_name: "mdi7.folder"
                        icon_size_multiplier: 1.5
                        ToolTip.visible: hovered
                        ToolTip.text: qsTr("Choose Output Folder")
                        onClicked: {
                            actions.chooseSavePath.trigger()
                        }
                    }
                    TextField {
                        id: saveFolderTextField
                        Layout.fillWidth: true
                        height: 50
                        placeholderText: qsTr("Output Folder")
                        text: ConfigItems.get_save_folder()
                        onEditingFinished: {
                            if (ConfigItems.dir_valid(text) === true) {
                                ConfigItems.set_save_folder(text)
                                saveFolderTextField.text = text
                            } else {
                                undo()
                            }
                        }
                        Connections {
                            target: dialogs
                            function onSave_folder_changed(value) {
                                saveFolderTextField.text = value
                            }
                        }
                    }
                }
                RowLayout {
                    Label {
                        Layout.alignment: Qt.AlignVCenter
                        text: qsTr("Deal with Conflicts:")
                        elide: Text.ElideRight
                    }
                    ComboBox {
                        textRole: "text"
                        valueRole: "value"
                        model: [
                            {value: "Overwrite", text: qsTr("Overwrite")},
                            {value: "Skip", text: qsTr("Skip")},
                            {value: "Prompt", text: qsTr("Prompt")}
                        ]
                        onActivated: (index) => {
                            ConfigItems.set_conflict_policy(currentValue)
                            dialogs.settingsDialog.conflictPolicyChanged(currentValue)
                        }
                        Component.onCompleted: {
                            currentIndex = indexOfValue(ConfigItems.get_conflict_policy())
                            dialogs.settingsDialog.conflictPolicyChanged.connect( (value) => {
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

    SplitView {
        id: largeView
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

                LayoutItemProxy {
                    anchors.fill: parent
                    anchors.margins: 20
                    width: 550
                    target: selectFormatCard
                }
            }

            Control {
                SplitView.fillWidth: true
                SplitView.maximumHeight: parent.height - 250
                anchors.bottom: parent.bottom

                LayoutItemProxy {
                    anchors.fill: parent
                    target: taskListArea
                }
            }
        }

        SplitView {
            Layout.alignment: Qt.AlignRight
            SplitView.fillWidth: true
            SplitView.fillHeight: true
            SplitView.preferredWidth: parent.width / 2
            SplitView.minimumWidth: parent.width * 0.45
            orientation: Qt.Vertical

            ScrollView {   
                SplitView.fillWidth: true
                SplitView.preferredHeight: parent.height - 200
                SplitView.minimumHeight: parent.height - 250
                SplitView.maximumHeight: parent.height - 200
                contentWidth: availableWidth
                contentHeight: advancedSettingsColumn.implicitHeight + 20
                background: Rectangle {
                    color: "transparent"
                    border.width: 1
                    border.color: Material.color(
                        Material.Grey,
                        Material.Shade300
                    )
                }

                LayoutItemProxy {
                    anchors.fill: parent
                    anchors.topMargin: 20
                    anchors.leftMargin: 20
                    anchors.rightMargin: 10
                    Layout.fillWidth: true
                    target: advancedSettingsColumn
                }
            }

            Control {
                SplitView.fillWidth: true
                SplitView.minimumHeight: 200
                anchors.bottom: parent.bottom
                background: Rectangle {
                    color: "transparent"
                    border.width: 1
                    border.color: Material.color(
                        Material.Grey,
                        Material.Shade300
                    )
                }
                LayoutItemProxy {
                    anchors.fill: parent
                    anchors.margins: 20
                    target: outputSettingsCard
                }
            }
        }
    }

    ScrollView {
        id: smallView
        visible: false
        anchors.fill: parent
        ColumnLayout {
            id: smallViewColumn
            LayoutItemProxy {
                target: selectFormatCard
            }
            LayoutItemProxy {
                width: smallView.width
                height: 500
                target: taskListArea
            }
            LayoutItemProxy {
                target: advancedSettingsColumn
            }
            LayoutItemProxy {
                width: smallView.width
                target: outputSettingsCard
            }
        }
    }

    Connections {
        target: window
        function onWidthChanged() {
            if (window.width < 900) {
                smallView.visible = true
                largeView.visible = false
            } else {
                smallView.visible = false
                largeView.visible = true
            }
        }
    }
}