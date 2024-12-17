import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import QtQuick.Shapes
import LibreSVIP

Page {
    title: qsTr("Converter")

    property alias taskList: taskListView
    property alias startConversionButton: startConversionBtn
    property alias inputFormatComboBox: inputFormat
    property alias outputFormatComboBox: outputFormat
    property alias swapInputOutputButton: swapInputOutput

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
                    list_view.model.update(index, {
                        value: text
                    });
                }
            }
            IconButton {
                icon_name: "mdi7.eyedropper-variant"
                diameter: 30
                new_padding: 6
                onClicked: {
                    dialogs.colorDialog.bind_color(colorField.text, color => {
                        colorField.text = color;
                        list_view.model.update(index, {
                            value: colorField.text
                        });
                    });
                }
            }
            IconButton {
                icon_name: "mdi7.help-circle-outline"
                diameter: 30
                new_padding: 6
                cursor_shape: Qt.WhatsThisCursor
                visible: field.description != ""
                ToolTip {
                    y: parent.y - parent.height
                    visible: parent.hovered
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
                    this.checked = field.value;
                }
                onCheckedChanged: {
                    list_view.model.update(index, {
                        value: this.checked
                    });
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
                new_padding: 6
                cursor_shape: Qt.WhatsThisCursor
                visible: field.description != ""
                ToolTip {
                    y: parent.y - parent.height
                    visible: parent.hovered
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
                        text: comboBox.textRole ? qsTr((comboBox.textRole in modelData) ? modelData[comboBox.textRole] : model[comboBox.textRole]) : qsTr(modelData)
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
                    implicitHeight: Math.min(field.choices.length * 35, 400)
                    padding: 1

                    contentItem: ListView {
                        clip: true
                        implicitHeight: contentHeight
                        model: comboBox.popup.visible ? comboBox.delegateModel : null
                        currentIndex: comboBox.highlightedIndex

                        ScrollIndicator.vertical: ScrollIndicator {}
                    }
                }

                Component.onCompleted: {
                    this.currentIndex = indexOfValue(field.value);
                }
                onActivated: index => {
                    list_view.model.update(comboBoxRow.index, {
                        value: this.currentValue
                    });
                }
                model: field.choices
            }
            IconButton {
                icon_name: "mdi7.help-circle-outline"
                diameter: 30
                new_padding: 6
                cursor_shape: Qt.WhatsThisCursor
                visible: field.description != ""
                ToolTip {
                    y: parent.y - parent.height
                    visible: parent.hovered
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
                        validator = Qt.createQmlObject('import QtQuick; IntValidator {}', this);
                        break;
                    case "float":
                        validator = Qt.createQmlObject('import QtQuick; DoubleValidator {}', this);
                        break;
                    default:
                        break;
                    }
                }
                onEditingFinished: {
                    list_view.model.update(index, {
                        value: text
                    });
                }
            }
            IconButton {
                icon_name: "mdi7.help-circle-outline"
                diameter: 30
                new_padding: 6
                cursor_shape: Qt.WhatsThisCursor
                visible: field.description != ""
                ToolTip {
                    y: parent.y - parent.height
                    visible: parent.hovered
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
                text: iconicFontLoader.icon("mdi7.tune-variant")
                font.family: "Material Design Icons"
                font.pixelSize: 12
            }
            Rectangle {
                Layout.fillWidth: true
                color: Material.color(Material.Grey, Material.Shade300)
                height: 1
            }
        }
    }

    ColumnLayout {
        id: selectFormatCard
        RowLayout {
            id: formatsTitleRow
            Layout.fillWidth: true
            Label {
                text: qsTr("Select File Formats")
                font.pixelSize: 20
                Layout.alignment: Qt.AlignVCenter
            }
            Item {
                Layout.fillWidth: true
            }
            Switch {
                id: resetTasksOnInputChange
                height: 40
                text: qsTr("Reset Tasks When Changing Input")
                checked: configItems.reset_tasks_on_input_change
                onClicked: {
                    configItems.reset_tasks_on_input_change = checked;
                }
            }
        }
        ColumnLayout {
            Layout.fillWidth: true
            RowLayout {
                Layout.fillWidth: true
                LabeledComboBox {
                    id: inputFormat
                    Layout.fillWidth: true
                    enabled: !taskManager.busy
                    hint: qsTr("Input Format: ")
                    onActivated: index => {
                        if (resetTasksOnInputChange.checked && taskManager.get_str("input_format") != currentValue) {
                            actions.clearTasks.trigger();
                        }
                        taskManager.set_str("input_format", currentValue);
                    }
                    Component.onCompleted: {
                        let last_input_format = taskManager.get_str("input_format");
                        if (last_input_format !== "") {
                            this.currentIndex = indexOfValue(last_input_format);
                        } else {
                            this.currentIndex = 0;
                        }
                        dialogs.openDialog.nameFilters[0] = qsTr(currentText) + " (*." + currentValue + ")";
                        taskManager.input_format_changed.connect(input_format => {
                            let new_index = indexOfValue(input_format);
                            if (new_index < 0) {
                                currentIndex = 0;
                                taskManager.set_str("input_format", currentValue);
                            } else {
                                if (new_index != currentIndex) {
                                    currentIndex = new_index;
                                }
                                let name_filter = qsTr(currentText) + " (*." + currentValue + ")";
                                if (name_filter != dialogs.openDialog.nameFilters[0]) {
                                    dialogs.openDialog.nameFilters[0] = name_filter;
                                }
                            }
                        });
                        taskManager.set_str("input_format", currentValue);
                    }
                    width: parent.width
                    choices: taskManager.qget("input_formats")
                }
                IconButton {
                    icon_name: "mdi7.information-outline"
                    diameter: 38
                    ToolTip.visible: hovered
                    ToolTip.text: qsTr("View Detail Information")
                    onClicked: {
                        inputInfoPowerAnimation.running = true;
                        inputFormatInfo.opened ? inputFormatInfo.close() : inputFormatInfo.open();
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
                        x: smallView.visible ? -width + parent.width : (parent.width - width) * 0.5
                        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent
                        contentItem: PluginInfo {
                            info: taskManager.plugin_info("input_format")
                            Component.onCompleted: {
                                taskManager.input_format_changed.connect(input_format => {
                                    info = taskManager.plugin_info("input_format");
                                });
                            }
                        }
                    }
                }
            }
            RowLayout {
                Layout.fillWidth: true
                Switch {
                    height: 40
                    text: qsTr("Auto-Detect Input File Type")
                    checked: configItems.auto_detect_input_format
                    onClicked: {
                        configItems.auto_detect_input_format = checked;
                    }
                }
                Item {
                    Layout.fillWidth: true
                }
                IconButton {
                    id: swapInputOutput
                    icon_name: "mdi7.swap-vertical"
                    diameter: 38
                    enabled: inputFormat.enabled && outputFormat.enabled
                    ToolTip.visible: hovered
                    ToolTip.text: qsTr("Swap Input and Output")
                    onClicked: {
                        if (inputFormat.enabled && outputFormat.enabled) {
                            [inputFormat.currentIndex, outputFormat.currentIndex] = [outputFormat.currentIndex, inputFormat.currentIndex];
                            taskManager.set_str("input_format", inputFormat.currentValue);
                            taskManager.set_str("output_format", outputFormat.currentValue);
                        }
                    }
                }
            }
            RowLayout {
                LabeledComboBox {
                    id: outputFormat
                    Layout.fillWidth: true
                    enabled: !taskManager.busy
                    hint: qsTr("Output Format: ")
                    onActivated: index => {
                        taskManager.set_str("output_format", currentValue);
                    }
                    Component.onCompleted: {
                        let last_output_format = taskManager.get_str("output_format");
                        if (last_output_format !== "") {
                            this.currentIndex = indexOfValue(last_output_format);
                        } else {
                            this.currentIndex = 0;
                        }
                        taskManager.output_format_changed.connect(output_format => {
                            let new_index = indexOfValue(output_format);
                            if (new_index < 0) {
                                currentIndex = 0;
                                taskManager.set_str("output_format", currentValue);
                            } else if (new_index != currentIndex) {
                                currentIndex = new_index;
                            }
                        });
                        taskManager.set_str("output_format", currentValue);
                    }
                    width: parent.width
                    model: taskManager.qget("output_formats")
                }
                IconButton {
                    icon_name: "mdi7.information-outline"
                    diameter: 38
                    ToolTip.visible: hovered
                    ToolTip.text: qsTr("View Detail Information")
                    onClicked: {
                        outputInfoPowerAnimation.running = true;
                        outputFormatInfo.opened ? outputFormatInfo.close() : outputFormatInfo.open();
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
                        x: smallView.visible ? -width + parent.width : (parent.width - width) * 0.5
                        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent
                        contentItem: PluginInfo {
                            info: taskManager.plugin_info("output_format")
                            Component.onCompleted: {
                                taskManager.output_format_changed.connect(output_format => {
                                    info = taskManager.plugin_info("output_format");
                                });
                            }
                        }
                    }
                }
            }
            RowLayout {
                Switch {
                    height: 40
                    text: qsTr("Set Output File Extension Automatically")
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
        }
    }

    DropArea {
        id: taskListArea
        clip: true
        onDropped: event => {
            if (inputFormat.enabled) {
                taskManager.add_task_paths(event.urls.map(dialogs.url2path));
            }
        }
        DashedRectangle {
            anchors.fill: parent
            anchors.margins: 12
            radius: 8
            visible: taskManager.count == 0
            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onEntered: {
                    if (taskManager.count == 0) {
                        parent.opacity = 0.5;
                    }
                }
                onExited: {
                    if (parent.opacity < 1) {
                        parent.opacity = 1;
                    }
                }
                onClicked: {
                    if (taskManager.count == 0) {
                        actions.openFile.trigger();
                    }
                }
                Column {
                    anchors.centerIn: parent
                    Label {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: iconicFontLoader.icon("mdi7.tray-arrow-up")
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
            anchors.margins: 15
            visible: taskManager.count > 0
            RowLayout {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                Label {
                    text: qsTr("Conversion Mode:")
                    font.pixelSize: 20
                    height: 30
                }
                TabBar {
                    height: 30

                    TabButton {
                        width: 50
                        text: iconicFontLoader.icon("mdi7.file-arrow-left-right-outline")
                        font.family: "Material Design Icons"
                        font.pixelSize: 25
                        enabled: !taskManager.busy
                        ToolTip.text: qsTr("Direct Mode")
                        ToolTip.visible: hovered
                        onClicked: {
                            taskManager.conversion_mode = "Direct";
                        }
                    }

                    TabButton {
                        width: 50
                        text: iconicFontLoader.icon("mdi7.set-merge")
                        font.family: "Material Design Icons"
                        font.pixelSize: 25
                        enabled: !taskManager.busy
                        ToolTip.text: qsTr("Singing Track Merging Mode")
                        ToolTip.visible: hovered
                        onClicked: {
                            taskManager.conversion_mode = "Merge";
                        }
                    }

                    TabButton {
                        width: 50
                        text: iconicFontLoader.icon("mdi7.set-split")
                        font.family: "Material Design Icons"
                        font.pixelSize: 25
                        enabled: !taskManager.busy
                        ToolTip.text: qsTr("Singing Track Grouping Mode")
                        ToolTip.visible: hovered
                        onClicked: {
                            taskManager.conversion_mode = "Split";
                        }
                    }
                }

                ToolSeparator {
                    height: 30
                }

                Label {
                    text: qsTr("Task List")
                    font.pixelSize: 20
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                    height: 30
                }
            }
            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: "lightgrey"
            }
            ScrollView {
                Layout.fillHeight: true
                Layout.fillWidth: true
                contentWidth: availableWidth
                ListView {
                    id: taskListView
                    Layout.fillWidth: true
                    model: taskManager.qget("tasks")
                    delegate: Qt.createComponent("task_row.qml")
                }
            }
            RowLayout {
                Layout.alignment: Qt.AlignBottom
                Layout.minimumHeight: 50
                Rectangle {
                    color: "transparent"
                    Timer {
                        id: hideTaskToolbarTimer
                        interval: 1000
                        repeat: true
                        triggeredOnStart: false
                        onTriggered: {
                            if (toggleTaskToolbarButton.hovered || addTaskButton.hovered || clearTaskButton.hovered || resetExtensionButton.hovered || removeOtherExtensionButton.hovered) {
                                return;
                            }
                            toggleTaskToolbarButton.state = "collapsed";
                            this.stop();
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
                            color: Material.color(Material.Indigo, Material.Shade300)
                        }
                        text: iconicFontLoader.icon("mdi7.hammer-wrench")
                        y: parent.height - this.height / 2
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
                                hideTaskToolbarTimer.stop();
                                state = "expanded";
                            } else if (!hideTaskToolbarTimer.running) {
                                hideTaskToolbarTimer.start();
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
                                text: iconicFontLoader.icon("mdi7.plus")
                                background: Rectangle {
                                    radius: this.height / 2
                                    color: Material.color(Material.LightBlue, Material.Shade200)
                                }
                                font.family: "Material Design Icons"
                                font.pixelSize: Qt.application.font.pixelSize * 1.5
                                radius: this.height / 2
                                ToolTip.visible: hovered
                                ToolTip.text: qsTr("Continue Adding files")
                                onHoveredChanged: {
                                    if (!hovered && !hideTaskToolbarTimer.running) {
                                        hideTaskToolbarTimer.start();
                                    }
                                }
                                onClicked: {
                                    actions.openFile.trigger();
                                }
                            }
                            RoundButton {
                                id: clearTaskButton
                                text: iconicFontLoader.icon("mdi7.refresh")
                                background: Rectangle {
                                    radius: this.height / 2
                                    color: Material.color(Material.LightBlue, Material.Shade200)
                                }
                                font.family: "Material Design Icons"
                                font.pixelSize: Qt.application.font.pixelSize * 1.5
                                radius: this.height / 2
                                enabled: taskManager.count > 0
                                ToolTip.visible: hovered
                                ToolTip.text: qsTr("Clear Task List")
                                onHoveredChanged: {
                                    if (!hovered && !hideTaskToolbarTimer.running) {
                                        hideTaskToolbarTimer.start();
                                    }
                                }
                                onClicked: {
                                    if (startConversionBtn.enabled) {
                                        actions.clearTasks.trigger();
                                    }
                                }
                            }
                            RoundButton {
                                id: resetExtensionButton
                                text: iconicFontLoader.icon("mdi7.form-textbox")
                                background: Rectangle {
                                    radius: this.height / 2
                                    color: Material.color(Material.LightBlue, Material.Shade200)
                                }
                                font.family: "Material Design Icons"
                                font.pixelSize: Qt.application.font.pixelSize * 1.5
                                radius: this.height / 2
                                ToolTip.visible: hovered
                                ToolTip.text: qsTr("Reset Default Extension")
                                onHoveredChanged: {
                                    if (!hovered && !hideTaskToolbarTimer.running) {
                                        hideTaskToolbarTimer.start();
                                    }
                                }
                                onClicked: {
                                    if (startConversionBtn.enabled) {
                                        taskManager.reset_stems();
                                    }
                                }
                            }
                            RoundButton {
                                id: removeOtherExtensionButton
                                text: iconicFontLoader.icon("mdi7.filter-minus-outline")
                                background: Rectangle {
                                    radius: this.height / 2
                                    color: Material.color(Material.LightBlue, Material.Shade200)
                                }
                                font.family: "Material Design Icons"
                                font.pixelSize: Qt.application.font.pixelSize * 1.5
                                radius: this.height / 2
                                ToolTip.visible: hovered
                                ToolTip.text: qsTr("Remove Tasks With Other Extensions")
                                onHoveredChanged: {
                                    if (!hovered && !hideTaskToolbarTimer.running) {
                                        hideTaskToolbarTimer.start();
                                    }
                                }
                                onClicked: {
                                    if (startConversionBtn.enabled) {
                                        // TODO
                                        for (var i = 0; i < taskListView.count; i++) {
                                            var task = taskListView.model.get(i);
                                            let extension = task.path.lastIndexOf(".") > -1 ? task.path.slice(task.path.lastIndexOf(".") + 1) : "";
                                            if (extension != inputFormat.currentValue) {
                                                taskListView.model.delete(i);
                                                i--;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                Row {
                    Layout.fillWidth: true
                }
                Label {
                    Layout.alignment: Qt.AlignVCenter
                    text: qsTr("Max Track count:")
                    visible: taskManager.conversion_mode === "Split"
                }
                SpinBox {
                    from: 1
                    value: configItems.max_track_count
                    visible: taskManager.conversion_mode === "Split"
                    onValueModified: {
                        configItems.max_track_count = value;
                    }
                }
            }
        }
        Rectangle {
            anchors.fill: parent
            color: "transparent"
            border.width: 1
            border.color: Material.color(Material.Grey, Material.Shade300)
        }
    }

    ScrollView {
        id: advancedSettingsArea
        contentHeight: advancedSettingsColumn.implicitHeight + 20
        ColumnLayout {
            id: advancedSettingsColumn
            Label {
                text: qsTr("Advanced Settings")
                font.pixelSize: 20
                Layout.alignment: Qt.AlignVCenter
            }
            ColumnLayout {
                Layout.fillWidth: true
                Layout.minimumWidth: advancedSettingsArea.availableWidth
                Row {
                    height: 30
                    visible: inputContainer.children.length > 0
                    Layout.fillWidth: true
                    RoundButton {
                        Layout.fillHeight: true
                        radius: this.height / 2
                        anchors.verticalCenter: parent.verticalCenter
                        contentItem: Label {
                            text: iconicFontLoader.icon("mdi7.chevron-right")
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
                            inputContainer.expanded = !inputContainer.expanded;
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
                        color: Material.color(Material.Grey)
                        font.pixelSize: 20
                        anchors.verticalCenter: parent.verticalCenter
                        Component.onCompleted: {
                            taskManager.input_format_changed.connect(input_format => {
                                let plugin_info = taskManager.plugin_info("input_format");
                                input_format_name = plugin_info.file_format;
                            });
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
                                SequentialAnimation {
                                    PropertyAnimation {
                                        target: inputContainer
                                        properties: "y,opacity,Layout.maximumHeight"
                                        duration: 300
                                        easing.type: Easing.InOutQuad
                                    }
                                    PropertyAction {
                                        target: inputContainer
                                        property: "visible"
                                    }
                                }
                            },
                            Transition {
                                from: "collapsed"
                                to: "expanded"
                                SequentialAnimation {
                                    PropertyAction {
                                        target: inputContainer
                                        property: "visible"
                                    }
                                    PropertyAnimation {
                                        target: inputContainer
                                        properties: "y,opacity,Layout.maximumHeight"
                                        duration: 300
                                        easing.type: Easing.InOutQuad
                                    }
                                }
                            }
                        ]
                    }
                    Rectangle {
                        width: 20
                    }
                }
                Repeater {
                    model: taskManager.qget("middleware_states")
                    delegate: ColumnLayout {
                        required property var modelData
                        Row {
                            height: 25
                            Layout.fillWidth: true
                            Switch {
                                Layout.fillHeight: true
                                anchors.verticalCenter: parent.verticalCenter
                                background: Rectangle {
                                    color: "transparent"
                                }
                                onToggled: {
                                    middlewareContainer.expanded = !middlewareContainer.expanded;
                                    taskManager.qget("middleware_states").update(modelData.index, {
                                        "value": middlewareContainer.expanded
                                    });
                                }
                            }
                            Label {
                                text: qsTr(modelData.name)
                                font.pixelSize: 22
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            Rectangle {
                                width: 10
                                height: 1
                                color: "transparent"
                            }
                            IconButton {
                                icon_name: "mdi7.help-circle-outline"
                                anchors.verticalCenter: parent.verticalCenter
                                diameter: 30
                                new_padding: 6
                                cursor_shape: Qt.WhatsThisCursor
                                visible: modelData.description != ""
                                ToolTip.visible: hovered
                                ToolTip.text: qsTr(modelData.description)
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            Rectangle {
                                width: 40
                            }
                            ColumnLayout {
                                id: middlewareContainer
                                property bool expanded: false
                                Layout.fillWidth: true
                                states: [
                                    State {
                                        name: "expanded"
                                        PropertyChanges {
                                            target: middlewareContainer
                                            Layout.maximumHeight: middlewareContainer.implicitHeight
                                            opacity: 1
                                            y: 0
                                            visible: true
                                        }
                                    },
                                    State {
                                        name: "collapsed"
                                        PropertyChanges {
                                            target: middlewareContainer
                                            Layout.maximumHeight: 0
                                            opacity: 0
                                            y: -middlewareContainer.implicitHeight
                                            visible: false
                                        }
                                    }
                                ]
                                state: expanded ? "expanded" : "collapsed"

                                transitions: [
                                    Transition {
                                        from: "expanded"
                                        to: "collapsed"
                                        SequentialAnimation {
                                            PropertyAnimation {
                                                target: middlewareContainer
                                                properties: "y,opacity,Layout.maximumHeight"
                                                duration: 300
                                                easing.type: Easing.InOutQuad
                                            }
                                            PropertyAction {
                                                target: middlewareContainer
                                                property: "visible"
                                            }
                                        }
                                    },
                                    Transition {
                                        from: "collapsed"
                                        to: "expanded"
                                        SequentialAnimation {
                                            PropertyAction {
                                                target: middlewareContainer
                                                property: "visible"
                                            }
                                            PropertyAnimation {
                                                target: middlewareContainer
                                                properties: "y,opacity,Layout.maximumHeight"
                                                duration: 300
                                                easing.type: Easing.InOutQuad
                                            }
                                        }
                                    }
                                ]
                            }
                            Rectangle {
                                width: 20
                            }
                        }
                        ListView {
                            id: middlewareFields
                            model: taskManager.get_middleware_fields(modelData.identifier)
                            function rebuildFields() {
                                for (var i = 0; i < model.rowCount(); i++) {
                                    let middleware_state = model.get(i);
                                    let separator_item = separatorItem.createObject(middlewareContainer);
                                    let item = null;
                                    switch (middleware_state.type) {
                                    case "bool":
                                        {
                                            item = switchItem.createObject(middlewareContainer, {
                                                "field": middleware_state,
                                                "index": i,
                                                "list_view": middlewareFields
                                            });
                                            break;
                                        }
                                    case "enum":
                                        {
                                            item = comboBoxItem.createObject(middlewareContainer, {
                                                "field": middleware_state,
                                                "index": i,
                                                "list_view": middlewareFields
                                            });
                                            break;
                                        }
                                    case "color":
                                        {
                                            item = colorPickerItem.createObject(middlewareContainer, {
                                                "field": middleware_state,
                                                "index": i,
                                                "list_view": middlewareFields
                                            });
                                            break;
                                        }
                                    default:
                                        {
                                            item = textFieldItem.createObject(middlewareContainer, {
                                                "field": middleware_state,
                                                "index": i,
                                                "list_view": middlewareFields
                                            });
                                            break;
                                        }
                                    }
                                }
                            }
                            delegate: Column {
                                Component.onCompleted: {
                                    if (index == 0) {
                                        middlewareContainer.children.length = 0;
                                        middlewareFields.rebuildFields();
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
                            text: iconicFontLoader.icon("mdi7.chevron-right")
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
                            outputContainer.expanded = !outputContainer.expanded;
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
                        color: Material.color(Material.Grey)
                        anchors.verticalCenter: parent.verticalCenter
                        Component.onCompleted: {
                            taskManager.output_format_changed.connect(output_format => {
                                let plugin_info = taskManager.plugin_info("output_format");
                                output_format_name = plugin_info.file_format;
                            });
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
                                SequentialAnimation {
                                    PropertyAnimation {
                                        target: outputContainer
                                        properties: "y,opacity,Layout.maximumHeight"
                                        duration: 300
                                        easing.type: Easing.InOutQuad
                                    }
                                    PropertyAction {
                                        target: outputContainer
                                        property: "visible"
                                    }
                                }
                            },
                            Transition {
                                from: "collapsed"
                                to: "expanded"
                                SequentialAnimation {
                                    PropertyAction {
                                        target: outputContainer
                                        property: "visible"
                                    }
                                    PropertyAnimation {
                                        target: outputContainer
                                        properties: "y,opacity,Layout.maximumHeight"
                                        duration: 300
                                        easing.type: Easing.InOutQuad
                                    }
                                }
                            }
                        ]
                    }
                    Rectangle {
                        width: 20
                    }
                }
                Repeater {
                    id: inputFields
                    model: taskManager.qget("input_fields")
                    delegate: Rectangle {
                        width: 0
                        height: 0
                        required property var modelData
                        Component.onCompleted: {
                            let separator_item = separatorItem.createObject(inputContainer);
                            this.Component.onDestruction.connect(separator_item.destroy);
                            let item = null;
                            switch (modelData.type) {
                            case "bool":
                                {
                                    item = switchItem.createObject(inputContainer, {
                                        "field": modelData,
                                        "index": modelData.index,
                                        "list_view": inputFields
                                    });
                                    break;
                                }
                            case "enum":
                                {
                                    item = comboBoxItem.createObject(inputContainer, {
                                        "field": modelData,
                                        "index": modelData.index,
                                        "list_view": inputFields
                                    });
                                    break;
                                }
                            case "color":
                                {
                                    item = colorPickerItem.createObject(inputContainer, {
                                        "field": modelData,
                                        "index": modelData.index,
                                        "list_view": inputFields
                                    });
                                    break;
                                }
                            default:
                                {
                                    item = textFieldItem.createObject(inputContainer, {
                                        "field": modelData,
                                        "index": modelData.index,
                                        "list_view": inputFields
                                    });
                                    break;
                                }
                            }
                            if (item) {
                                this.Component.onDestruction.connect(item.destroy);
                            }
                        }
                    }
                }
                Repeater {
                    id: outputFields
                    model: taskManager.qget("output_fields")
                    delegate: Rectangle {
                        width: 0
                        height: 0
                        required property var modelData
                        Component.onCompleted: {
                            let separator_item = separatorItem.createObject(outputContainer);
                            this.Component.onDestruction.connect(separator_item.destroy);
                            let item = null;
                            switch (modelData.type) {
                            case "bool":
                                {
                                    item = switchItem.createObject(outputContainer, {
                                        "field": modelData,
                                        "index": modelData.index,
                                        "list_view": outputFields
                                    });
                                    break;
                                }
                            case "enum":
                                {
                                    item = comboBoxItem.createObject(outputContainer, {
                                        "field": modelData,
                                        "index": modelData.index,
                                        "list_view": outputFields
                                    });
                                    break;
                                }
                            case "color":
                                {
                                    item = colorPickerItem.createObject(outputContainer, {
                                        "field": modelData,
                                        "index": modelData.index,
                                        "list_view": outputFields
                                    });
                                    break;
                                }
                            default:
                                {
                                    item = textFieldItem.createObject(outputContainer, {
                                        "field": modelData,
                                        "index": modelData.index,
                                        "list_view": outputFields
                                    });
                                    break;
                                }
                            }
                            if (item) {
                                this.Component.onDestruction.connect(item.destroy);
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
                checked: configItems.open_save_folder_on_completion
                onClicked: {
                    configItems.open_save_folder_on_completion = checked;
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
                    property color base_color: Material.color(Material.Indigo)
                    property int anim_index: 10
                    property bool anim_running: taskManager.busy
                    anchors.fill: parent
                    radius: 10
                    enabled: taskManager.count > 0 && !taskManager.busy
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
                        text: taskManager.busy ? qsTr("Converting") : qsTr("Start Conversion")
                        wrapMode: Text.WordWrap
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        color: "white"
                    }
                    onClicked: {
                        actions.startConversion.trigger();
                    }
                }
            }
            ColumnLayout {
                RowLayout {
                    IconButton {
                        icon_name: "mdi7.folder"
                        ToolTip.visible: hovered
                        ToolTip.text: qsTr("Choose Output Folder")
                        onClicked: {
                            actions.chooseSavePath.trigger();
                        }
                    }
                    TextField {
                        Layout.fillWidth: true
                        height: 50
                        placeholderText: qsTr("Output Folder")
                        text: configItems.save_folder
                        onEditingFinished: {
                            if (configItems.dir_valid(text) === true) {
                                configItems.save_folder = text;
                            } else {
                                undo();
                            }
                        }
                    }
                }
                RowLayout {
                    Label {
                        Layout.alignment: Qt.AlignVCenter
                        text: qsTr("Deal with Conflicts")
                        elide: Text.ElideRight
                    }
                    ComboBox {
                        id: conflictPolicyCombo
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
            SplitView.minimumWidth: formatsTitleRow.implicitWidth + 50
            orientation: Qt.Vertical

            Pane {
                SplitView.fillWidth: true
                SplitView.preferredHeight: 250
                SplitView.minimumHeight: 250
                SplitView.maximumHeight: 300
                background: Rectangle {
                    color: "transparent"
                    border.width: 1
                    border.color: Material.color(Material.Grey, Material.Shade300)
                }

                LayoutItemProxy {
                    anchors.fill: parent
                    anchors.margins: 20
                    width: 550
                    target: selectFormatCard
                }
            }

            Item {
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
            SplitView.minimumWidth: 450
            orientation: Qt.Vertical

            Pane {
                SplitView.fillWidth: true
                SplitView.minimumWidth: parent.width
                SplitView.preferredHeight: parent.height - 200
                SplitView.minimumHeight: parent.height - 250
                SplitView.maximumHeight: parent.height - 200
                background: Rectangle {
                    color: "transparent"
                    border.width: 1
                    border.color: Material.color(Material.Grey, Material.Shade300)
                }

                LayoutItemProxy {
                    anchors.fill: parent
                    anchors.topMargin: 20
                    anchors.leftMargin: 20
                    anchors.rightMargin: 10
                    Layout.fillWidth: true
                    target: advancedSettingsArea
                }
            }

            Pane {
                SplitView.fillWidth: true
                SplitView.minimumHeight: 200
                anchors.bottom: parent.bottom
                background: Rectangle {
                    color: "transparent"
                    border.width: 1
                    border.color: Material.color(Material.Grey, Material.Shade300)
                }
                LayoutItemProxy {
                    anchors.fill: parent
                    anchors.margins: 20
                    target: outputSettingsCard
                }
            }
        }
    }

    ColumnLayout {
        id: smallView
        visible: false
        anchors.fill: parent
        anchors.margins: 10
        Layout.fillWidth: true
        TabBar {
            Layout.fillWidth: true
            Layout.preferredHeight: 50

            TabButton {
                text: qsTr("Select File Formats")
                onClicked: {
                    smallViewStack.currentIndex = 0;
                }
            }

            TabButton {
                text: qsTr("Advanced Settings")
                onClicked: {
                    smallViewStack.currentIndex = 1;
                }
            }

            TabButton {
                text: qsTr("Output Settings")
                onClicked: {
                    smallViewStack.currentIndex = 2;
                }
            }
        }
        Rectangle {
            Layout.fillWidth: true
            width: 1
            color: "lightgrey"
        }
        StackLayout {
            id: smallViewStack
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: 0

            SplitView {
                SplitView.fillHeight: true
                SplitView.fillWidth: true
                orientation: Qt.Vertical

                Pane {
                    SplitView.fillWidth: true
                    SplitView.preferredHeight: 250
                    SplitView.minimumHeight: 250
                    SplitView.maximumHeight: 300
                    background: Rectangle {
                        color: "transparent"
                        border.width: 1
                        border.color: Material.color(Material.Grey, Material.Shade300)
                    }

                    LayoutItemProxy {
                        anchors.fill: parent
                        anchors.margins: 20
                        width: 550
                        target: selectFormatCard
                    }
                }

                Pane {
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
                SplitView.fillWidth: true
                SplitView.fillHeight: true
                orientation: Qt.Vertical

                Pane {
                    SplitView.fillWidth: true
                    SplitView.preferredHeight: parent.height - 350
                    SplitView.minimumHeight: parent.height - 400
                    SplitView.maximumHeight: parent.height - 300
                    background: Rectangle {
                        color: "transparent"
                        border.width: 1
                        border.color: Material.color(Material.Grey, Material.Shade300)
                    }

                    LayoutItemProxy {
                        anchors.fill: parent
                        anchors.topMargin: 20
                        anchors.leftMargin: 20
                        anchors.rightMargin: 10
                        Layout.fillWidth: true
                        target: advancedSettingsArea
                    }
                }

                Pane {
                    SplitView.fillWidth: true
                    SplitView.maximumHeight: 400
                    anchors.bottom: parent.bottom

                    LayoutItemProxy {
                        anchors.fill: parent
                        target: taskListArea
                    }
                }
            }
            SplitView {
                SplitView.fillWidth: true
                SplitView.fillHeight: true
                orientation: Qt.Vertical

                Pane {
                    SplitView.fillWidth: true
                    SplitView.minimumHeight: 200
                    SplitView.maximumHeight: 250
                    background: Rectangle {
                        color: "transparent"
                        border.width: 1
                        border.color: Material.color(Material.Grey, Material.Shade300)
                    }
                    LayoutItemProxy {
                        anchors.fill: parent
                        anchors.margins: 20
                        target: outputSettingsCard
                    }
                }

                Pane {
                    SplitView.fillWidth: true
                    SplitView.maximumHeight: parent.height - 200
                    anchors.bottom: parent.bottom

                    LayoutItemProxy {
                        anchors.fill: parent
                        target: taskListArea
                    }
                }
            }
        }
    }

    Connections {
        target: window
        function onWidthChanged() {
            if (window.width < 1000) {
                smallView.visible = true;
                largeView.visible = false;
            } else {
                smallView.visible = false;
                largeView.visible = true;
            }
        }
    }
}
