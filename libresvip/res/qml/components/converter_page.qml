import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import QtQuick.Shapes

Page {
    title: qsTr("Converter")

    property alias taskList: taskListView
    property alias startConversionButton: startConversionBtn
    property alias inputFormatComboBox: inputFormat
    property alias outputFormatComboBox: outputFormat
    property alias swapInputOutputButton: swapInputOutput

    // Breakpoint selector: switch to stack-based small layout when the window
    // is too narrow to host the split-based layout, or when the user has
    // scaled the font large enough that the split panes would overflow.
    readonly property bool compactLayout: window.width < 1000 || (selectFormatCard.implicitWidth + advancedSettingsArea.implicitWidth + 48) > window.width || Qt.application.font.pixelSize > 16

    function optionFieldComponent(fieldType) {
        switch (fieldType) {
        case "bool":
            return switchItem;
        case "enum":
            return comboBoxItem;
        case "color":
            return colorPickerItem;
        default:
            return textFieldItem;
        }
    }

    function updateOptionField(listModel, itemIndex, patch) {
        if (listModel && itemIndex >= 0 && typeof listModel.update === "function") {
            listModel.update(itemIndex, patch);
        }
    }

    function getOptionField(listModel, itemIndex) {
        if (listModel && itemIndex >= 0 && typeof listModel.get === "function") {
            return listModel.get(itemIndex);
        }
        return null;
    }

    function fieldText(field) {
        if (!field || field.value === undefined || field.value === null) {
            return "";
        }
        return String(field.value);
    }

    property bool inputSectionExpanded: true
    property bool outputSectionExpanded: true

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
                        let format_name = currentText.replace(/\s*\(.*\)$/, "");
                        dialogs.setFormatFilter(qsTr(format_name) + " (" + currentSuffixes.replace(/; /g, " ") + ")");
                        taskManager.input_format_changed.connect(input_format => {
                            let new_index = indexOfValue(input_format);
                            if (new_index < 0) {
                                currentIndex = 0;
                                taskManager.set_str("input_format", currentValue);
                            } else {
                                if (new_index != currentIndex) {
                                    currentIndex = new_index;
                                }
                                let format_name = currentText.replace(/\s*\(.*\)$/, "");
                                let name_filter = qsTr(format_name) + " (" + currentSuffixes.replace(/; /g, " ") + ")";
                                if (name_filter != dialogs.openDialog.nameFilters[0]) {
                                    dialogs.setFormatFilter(name_filter);
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
                    accessibleName: qsTr("View Detail Information")
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
                        color: Theme.colorMutedText
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
                    FormatInfoPopup {
                        id: inputFormatInfo
                        format_type: "input_format"
                        x: smallView.visible ? -width + parent.width : (parent.width - width) * 0.5
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
                    accessibleName: qsTr("Swap Input and Output")
                    diameter: 38
                    enabled: inputFormat.enabled && outputFormat.enabled
                    ToolTip.visible: hovered
                    ToolTip.text: qsTr("Swap Input and Output")
                    onClicked: {
                        if (inputFormat.enabled && outputFormat.enabled) {
                            let inputFormatChangedIndex = inputFormat.indexOfValue(outputFormat.currentValue);
                            let outputFormatChangedIndex = outputFormat.indexOfValue(inputFormat.currentValue);
                            if (inputFormatChangedIndex >= 0 && outputFormatChangedIndex >= 0) {
                                [inputFormat.currentIndex, outputFormat.currentIndex] = [inputFormatChangedIndex, outputFormatChangedIndex];
                                taskManager.set_str("input_format", inputFormat.currentValue);
                                taskManager.set_str("output_format", outputFormat.currentValue);
                            }
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
                    accessibleName: qsTr("View Detail Information")
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
                        color: Theme.colorMutedText
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
                    FormatInfoPopup {
                        id: outputFormatInfo
                        format_type: "output_format"
                        x: smallView.visible ? -width + parent.width : (parent.width - width) * 0.5
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
            id: emptyState
            anchors.fill: parent
            anchors.margins: Theme.spacingS
            radius: 8
            visible: taskManager.count == 0
            strokeColor: taskListArea.containsDrag ? Material.accentColor : Theme.colorBorder
            strokeWidth: taskListArea.containsDrag ? 3 : 1
            fillColor: taskListArea.containsDrag ? Qt.rgba(Material.accentColor.r, Material.accentColor.g, Material.accentColor.b, 0.08) : "transparent"
            Behavior on strokeColor {
                ColorAnimation {
                    duration: 150
                }
            }
            Behavior on fillColor {
                ColorAnimation {
                    duration: 150
                }
            }
            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    if (taskManager.count == 0 && !taskListArea.containsDrag) {
                        actions.openFile.trigger();
                    }
                }
                Column {
                    anchors.centerIn: parent
                    spacing: Theme.spacingXS
                    Label {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: iconicFontLoader.icon("mdi7.tray-arrow-up")
                        font.family: "Material Design Icons"
                        font.pixelSize: 100
                    }
                    Label {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: taskListArea.containsDrag ? qsTr("Release to add files") : qsTr("Drag and drop files here")
                        font.pixelSize: 30
                    }
                    Label {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: qsTr("or")
                        font.pixelSize: 14
                        color: Theme.colorMutedText
                    }
                    Button {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: qsTr("Browse Files")
                        icon.name: "mdi7.folder-open-outline"
                        onClicked: actions.openFile.trigger()
                    }
                }
            }
        }
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Theme.spacingM
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
                        Accessible.name: qsTr("Direct Mode")
                        Accessible.role: Accessible.Button
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
                        Accessible.name: qsTr("Singing Track Merging Mode")
                        Accessible.role: Accessible.Button
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
                        Accessible.name: qsTr("Singing Track Grouping Mode")
                        Accessible.role: Accessible.Button
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
                color: Theme.colorBorder
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
                        Accessible.name: qsTr("Expand or Collapse Task Toolbar")
                        Accessible.role: Accessible.Button
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
                        font.pixelSize: Qt.application.font.pixelSize
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
                                Accessible.name: qsTr("Continue Adding files")
                                Accessible.role: Accessible.Button
                                text: iconicFontLoader.icon("mdi7.plus")
                                background: Rectangle {
                                    radius: this.height / 2
                                    color: Material.color(Material.LightBlue, Material.Shade200)
                                }
                                font.family: "Material Design Icons"
                                font.pixelSize: Qt.application.font.pixelSize
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
                                Accessible.name: qsTr("Clear Task List")
                                Accessible.role: Accessible.Button
                                text: iconicFontLoader.icon("mdi7.refresh")
                                background: Rectangle {
                                    radius: this.height / 2
                                    color: Material.color(Material.LightBlue, Material.Shade200)
                                }
                                font.family: "Material Design Icons"
                                font.pixelSize: Qt.application.font.pixelSize
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
                                Accessible.name: qsTr("Reset Extensions")
                                Accessible.role: Accessible.Button
                                text: iconicFontLoader.icon("mdi7.form-textbox")
                                background: Rectangle {
                                    radius: this.height / 2
                                    color: Material.color(Material.LightBlue, Material.Shade200)
                                }
                                font.family: "Material Design Icons"
                                font.pixelSize: Qt.application.font.pixelSize
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
                                Accessible.name: qsTr("Remove Other Extensions")
                                Accessible.role: Accessible.Button
                                text: iconicFontLoader.icon("mdi7.filter-minus-outline")
                                background: Rectangle {
                                    radius: this.height / 2
                                    color: Material.color(Material.LightBlue, Material.Shade200)
                                }
                                font.family: "Material Design Icons"
                                font.pixelSize: Qt.application.font.pixelSize
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
                                        for (var i = 0; i < taskListView.count; i++) {
                                            var task = taskListView.model.get(i);
                                            let extension = task.path.lastIndexOf(".") > -1 ? task.path.slice(task.path.lastIndexOf(".") + 1).toLowerCase() : "";
                                            let suffixes = inputFormat.currentSuffixValues.length > 0 ? inputFormat.currentSuffixValues : [inputFormat.currentValue];
                                            let matched = false;
                                            for (var suffixIndex = 0; suffixIndex < suffixes.length; suffixIndex++) {
                                                if (extension === String(suffixes[suffixIndex]).toLowerCase()) {
                                                    matched = true;
                                                    break;
                                                }
                                            }
                                            if (!matched) {
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
            border.color: Theme.colorBorder
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
                ExpandableSection {
                    id: inputSection
                    Layout.fillWidth: true
                    visible: inputFieldsRepeater.count > 0
                    title: qsTr("Input Options")
                    subtitle: qsTr("[Import as ") + qsTr(input_format_name) + "]"
                    expanded: inputSectionExpanded
                    onExpandedChanged: inputSectionExpanded = expanded
                    property string input_format_name: ""
                    Component.onCompleted: {
                        let plugin_info = taskManager.plugin_info("input_format");
                        input_format_name = plugin_info.file_format;
                        taskManager.input_format_changed.connect(input_format => {
                            let info = taskManager.plugin_info("input_format");
                            input_format_name = info.file_format;
                        });
                    }
                    Repeater {
                        id: inputFieldsRepeater
                        model: taskManager.input_fields
                        delegate: FieldDelegate {
                            Layout.fillWidth: true
                            required property int index
                            required property var modelData
                            field: modelData
                            showSeparator: index < inputFieldsRepeater.count - 1
                            onValueChanged: value => {
                                updateOptionField(inputFieldsRepeater.model, index, {
                                    value: value
                                });
                            }
                        }
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
                                id: middlewareSwitch
                                checked: false
                                Layout.fillHeight: true
                                anchors.verticalCenter: parent.verticalCenter
                                background: Rectangle {
                                    color: "transparent"
                                }
                                Component.onCompleted: {
                                    middlewareContainer.expanded = modelData.value;
                                    checked = modelData.value;
                                }
                                onToggled: {
                                    middlewareContainer.expanded = checked;
                                    taskManager.qget("middleware_states").update(modelData.index, {
                                        "value": checked
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
                                accessibleName: qsTr("Help")
                                anchors.verticalCenter: parent.verticalCenter
                                diameter: 30
                                new_padding: 7
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
                                            visible: true
                                        }
                                    },
                                    State {
                                        name: "collapsed"
                                        PropertyChanges {
                                            target: middlewareContainer
                                            Layout.maximumHeight: 0
                                            opacity: 0
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
                                                properties: "opacity,Layout.maximumHeight"
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
                                                properties: "opacity,Layout.maximumHeight"
                                                duration: 300
                                                easing.type: Easing.InOutQuad
                                            }
                                        }
                                    }
                                ]
                                Repeater {
                                    id: middlewareFieldsRepeater
                                    model: taskManager.get_middleware_fields(modelData.identifier)
                                    delegate: FieldDelegate {
                                        Layout.fillWidth: true
                                        required property int index
                                        required property var modelData
                                        field: modelData
                                        showSeparator: index < middlewareFieldsRepeater.count - 1
                                        onValueChanged: value => {
                                            updateOptionField(middlewareFieldsRepeater.model, index, {
                                                value: value
                                            });
                                        }
                                    }
                                }
                            }
                            Rectangle {
                                width: 20
                            }
                        }
                    }
                }
                ExpandableSection {
                    id: outputSection
                    Layout.fillWidth: true
                    visible: outputFieldsRepeater.count > 0
                    title: qsTr("Output Options")
                    subtitle: qsTr("[Export to ") + qsTr(output_format_name) + "]"
                    expanded: outputSectionExpanded
                    onExpandedChanged: outputSectionExpanded = expanded
                    property string output_format_name: ""
                    Component.onCompleted: {
                        let plugin_info = taskManager.plugin_info("output_format");
                        output_format_name = plugin_info.file_format;
                        taskManager.output_format_changed.connect(output_format => {
                            let info = taskManager.plugin_info("output_format");
                            output_format_name = info.file_format;
                        });
                    }
                    Repeater {
                        id: outputFieldsRepeater
                        model: taskManager.output_fields
                        delegate: FieldDelegate {
                            Layout.fillWidth: true
                            required property int index
                            required property var modelData
                            field: modelData
                            showSeparator: index < outputFieldsRepeater.count - 1
                            onValueChanged: value => {
                                updateOptionField(outputFieldsRepeater.model, index, {
                                    value: value
                                });
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
                Layout.margins: Theme.spacingM
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
                        accessibleName: qsTr("Choose Output Folder")
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
                    ConflictPolicyComboBox {
                        id: conflictPolicyCombo
                        Layout.fillWidth: true
                    }
                }
            }
        }
    }

    SplitView {
        id: largeView
        visible: !compactLayout
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
                    border.color: Theme.colorBorder
                }

                LayoutItemProxy {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingL
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
                    border.color: Theme.colorBorder
                }

                LayoutItemProxy {
                    anchors.fill: parent
                    anchors.topMargin: Theme.spacingL
                    anchors.leftMargin: Theme.spacingL
                    anchors.rightMargin: Theme.spacingS
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
                    border.color: Theme.colorBorder
                }
                LayoutItemProxy {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingL
                    target: outputSettingsCard
                }
            }
        }
    }

    ColumnLayout {
        id: smallView
        visible: compactLayout
        anchors.fill: parent
        anchors.margins: Theme.spacingS
        Layout.fillWidth: true
        TabBar {
            Layout.fillWidth: true
            Layout.preferredHeight: 50

            TabButton {
                text: qsTr("In/Out")
                onClicked: {
                    smallViewStack.currentIndex = 0;
                }
            }

            TabButton {
                text: qsTr("Settings")
                onClicked: {
                    smallViewStack.currentIndex = 1;
                }
            }

            TabButton {
                text: qsTr("Tasks")
                onClicked: {
                    smallViewStack.currentIndex = 2;
                }
            }
        }
        Rectangle {
            Layout.fillWidth: true
            width: 1
            color: Theme.colorBorder
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
                        border.color: Theme.colorBorder
                    }

                    LayoutItemProxy {
                        anchors.fill: parent
                        anchors.margins: Theme.spacingL
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
                        border.color: Theme.colorBorder
                    }

                    LayoutItemProxy {
                        anchors.fill: parent
                        anchors.topMargin: Theme.spacingL
                        anchors.leftMargin: Theme.spacingL
                        anchors.rightMargin: Theme.spacingS
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
                        border.color: Theme.colorBorder
                    }
                    LayoutItemProxy {
                        anchors.fill: parent
                        anchors.margins: Theme.spacingL
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
}
