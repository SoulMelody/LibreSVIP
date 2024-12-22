import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Controls.Material.impl
import QtQuick.Layouts
import LibreSVIP

ToolBar {
    id: toolBar
    implicitHeight: 32
    height: 32
    signal openConvertMenu
    signal openFormatsMenu
    signal openImportFormatMenu
    signal openExportFormatMenu
    signal openSettingsMenu
    signal openThemesMenu
    signal openLanguageMenu
    signal openHelpMenu

    function toggleMaximized() {
        window.click_maximize_btn();
    }

    LocaleSwitcher {
        id: localeSwitcher
    }

    background: Rectangle {
        implicitHeight: 32
        color: window.Material.background
        border.width: 1
        border.color: Material.color(Material.Grey, Material.Shade300)

        layer.enabled: toolBar.Material.elevation > 0
        layer.effect: ElevationEffect {
            elevation: toolBar.Material.elevation
            fullWidth: true
        }
    }

    Item {
        anchors.fill: parent
        TapHandler {
            onTapped: if (tapCount === 2)
                toggleMaximized()
            gesturePolicy: TapHandler.DragThreshold
        }
        DragHandler {
            grabPermissions: TapHandler.CanTakeOverFromAnything
            onActiveChanged: if (active) {
                window.startSystemMove();
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            width: 32
            height: 32
            color: "transparent"
            Image {
                anchors.centerIn: parent
                source: configItems.icon_data
                sourceSize.width: 16
                sourceSize.height: 16
            }
        }

        RowLayout {
            Layout.alignment: Qt.AlignRight
            layoutDirection: Qt.RightToLeft

            RowLayout {
                implicitHeight: 24
                spacing: 0
                Button {
                    id: minimizeButton
                    Material.roundedScale: Material.NotRounded
                    Layout.fillHeight: true
                    leftPadding: 0
                    rightPadding: 0
                    topInset: 0
                    bottomInset: 0
                    flat: true
                    implicitWidth: 46
                    implicitHeight: 24
                    background.implicitWidth: implicitWidth
                    background.implicitHeight: implicitHeight
                    text: iconicFontLoader.icon("mdi7.window-minimize")
                    font.family: "Material Design Icons"
                    font.pixelSize: Qt.application.font.pixelSize * 1.3
                    onClicked: window.showMinimized()
                }

                Button {
                    id: maximizeButton
                    objectName: "maximizeButton"
                    Material.roundedScale: Material.NotRounded
                    Layout.fillHeight: true
                    hoverEnabled: true
                    leftPadding: 0
                    rightPadding: 0
                    topInset: 0
                    bottomInset: 0
                    flat: true
                    implicitWidth: 46
                    implicitHeight: 24
                    background.implicitWidth: implicitWidth
                    background.implicitHeight: implicitHeight
                    text: window.visibility == Window.Maximized ? iconicFontLoader.icon("mdi7.window-restore") : iconicFontLoader.icon("mdi7.window-maximize")
                    font.family: "Material Design Icons"
                    font.pixelSize: Qt.application.font.pixelSize * 1.3
                    onClicked: toggleMaximized()
                }

                Button {
                    id: exitButton
                    Material.roundedScale: Material.NotRounded
                    Layout.fillHeight: true
                    leftPadding: 0
                    rightPadding: 0
                    topInset: 0
                    bottomInset: 0
                    flat: true
                    implicitWidth: 46
                    implicitHeight: 24
                    background.implicitWidth: implicitWidth
                    background.implicitHeight: implicitHeight
                    text: hovered ? "<font color='white'>" + iconicFontLoader.icon("mdi7.close") + "</font>" : iconicFontLoader.icon("mdi7.close")
                    font.family: "Material Design Icons"
                    font.pixelSize: Qt.application.font.pixelSize * 1.3
                    onClicked: actions.quit.trigger()
                    onHoveredChanged: {
                        if (hovered) {
                            exitButton.background.color = Material.color(Material.Red);
                        } else {
                            exitButton.background.color = "transparent";
                        }
                    }
                }
            }

            Label {
                objectName: "captionLabel"
                Layout.fillWidth: true
                Layout.fillHeight: true
                verticalAlignment: Text.AlignVCenter
                text: window.title + " - " + qsTr("SVS Projects Converter")
                font.pixelSize: Qt.application.font.pixelSize * 1.2
                elide: Text.ElideRight
            }

            ToolSeparator {
                contentItem.implicitHeight: 16
            }

            RowLayout {
                Button {
                    Material.roundedScale: Material.NotRounded
                    Layout.fillHeight: true
                    flat: true
                    text: qsTr("Convert (&C)")
                    onClicked: convertMenu.open()
                    Menu {
                        id: convertMenu
                        width: 300
                        y: parent.height
                        IconMenuItem {
                            action: actions.openFile
                            icon_name: "mdi7.file-import-outline"
                            label: qsTr("Import Projects (Ctrl+O)")
                        }
                        IconMenuItem {
                            id: startConversionMenuItem
                            action: actions.startConversion
                            icon_name: "mdi7.share-all-outline"
                            label: qsTr("Perform All Tasks (Ctrl+Enter)")
                            enabled: converterPage.startConversionButton.enabled
                        }
                        IconMenuItem {
                            id: clearTasksMenuItem
                            action: actions.clearTasks
                            icon_name: "mdi7.refresh"
                            label: qsTr("Clear Tasks (Ctrl+R)")
                            enabled: taskManager.count > 0
                        }
                        MenuSeparator {}
                        IconMenuItem {
                            action: actions.swapInputOutput
                            icon_name: "mdi7.swap-vertical"
                            label: qsTr("Swap Input and Output (Ctrl+Tab)")
                        }
                    }
                }
                Button {
                    Material.roundedScale: Material.NotRounded
                    Layout.fillHeight: true
                    flat: true
                    text: qsTr("Formats (&F)")
                    onClicked: formatsMenu.open()
                    Menu {
                        id: formatsMenu
                        width: 200
                        y: parent.height
                        Menu {
                            id: importFormatMenu
                            width: 300
                            title: qsTr("Input Format (&I)")
                            enabled: !taskManager.busy
                            ButtonGroup {
                                id: inputFormatButtonGroup
                            }
                            contentItem: ListView {
                                id: importMenuList
                                model: taskManager.qget("input_formats")
                                delegate: MenuItem {
                                    checkable: true
                                    checked: ListView.isCurrentItem
                                    ButtonGroup.group: inputFormatButtonGroup
                                    onTriggered: {
                                        taskManager.set_str("input_format", model.value);
                                    }
                                    text: String(index % 10) + " " + qsTr(model.text ? model.text : "")
                                }
                                Connections {
                                    target: taskManager
                                    function onInput_format_changed(input_format) {
                                        let new_index = converterPage.inputFormatComboBox.indexOfValue(input_format);
                                        if (new_index != importMenuList.currentIndex) {
                                            importMenuList.currentIndex = new_index;
                                        }
                                    }
                                }
                                focus: true
                                function navigate(event, key) {
                                    if (count >= 10 + key) {
                                        let next_focus = 10 * (Math.floor(currentIndex / 10) + 1);
                                        next_focus = next_focus + key >= count ? key : next_focus + key;
                                        itemAtIndex(next_focus).ListView.focus = true;
                                        currentIndex = next_focus;
                                    } else {
                                        itemAtIndex(key).triggered();
                                    }
                                }
                                Keys.onDigit0Pressed: event => navigate(event, 0)
                                Keys.onDigit1Pressed: event => navigate(event, 1)
                                Keys.onDigit2Pressed: event => navigate(event, 2)
                                Keys.onDigit3Pressed: event => navigate(event, 3)
                                Keys.onDigit4Pressed: event => navigate(event, 4)
                                Keys.onDigit5Pressed: event => navigate(event, 5)
                                Keys.onDigit6Pressed: event => navigate(event, 6)
                                Keys.onDigit7Pressed: event => navigate(event, 7)
                                Keys.onDigit8Pressed: event => navigate(event, 8)
                                Keys.onDigit9Pressed: event => navigate(event, 9)
                            }
                            implicitHeight: importMenuList.contentHeight
                            onClosed: {
                                if (importMenuList.currentIndex != converterPage.inputFormatComboBox.currentIndex) {
                                    importMenuList.currentIndex = converterPage.inputFormatComboBox.currentIndex;
                                }
                            }
                        }
                        Menu {
                            id: exportFormatMenu
                            width: 300
                            title: qsTr("Output Format (&E)")
                            enabled: !taskManager.busy
                            ButtonGroup {
                                id: exportFormatButtonGroup
                            }
                            contentItem: ListView {
                                id: exportMenuList
                                model: taskManager.qget("output_formats")
                                delegate: MenuItem {
                                    checkable: true
                                    checked: ListView.isCurrentItem
                                    ButtonGroup.group: exportFormatButtonGroup
                                    onTriggered: {
                                        taskManager.set_str("output_format", model.value);
                                    }
                                    text: String(index % 10) + " " + qsTr(model.text ? model.text : "")
                                }
                                Connections {
                                    target: taskManager
                                    function onOutput_format_changed(output_format) {
                                        let new_index = converterPage.outputFormatComboBox.indexOfValue(output_format);
                                        if (new_index != exportMenuList.currentIndex) {
                                            exportMenuList.currentIndex = new_index;
                                        }
                                    }
                                }
                                focus: true
                                function navigate(event, key) {
                                    if (count >= 10 + key) {
                                        let next_focus = 10 * (Math.floor(currentIndex / 10) + 1);
                                        next_focus = next_focus + key >= count ? key : next_focus + key;
                                        itemAtIndex(next_focus).ListView.focus = true;
                                        currentIndex = next_focus;
                                    } else {
                                        itemAtIndex(key).triggered();
                                    }
                                }
                                Keys.onDigit0Pressed: event => navigate(event, 0)
                                Keys.onDigit1Pressed: event => navigate(event, 1)
                                Keys.onDigit2Pressed: event => navigate(event, 2)
                                Keys.onDigit3Pressed: event => navigate(event, 3)
                                Keys.onDigit4Pressed: event => navigate(event, 4)
                                Keys.onDigit5Pressed: event => navigate(event, 5)
                                Keys.onDigit6Pressed: event => navigate(event, 6)
                                Keys.onDigit7Pressed: event => navigate(event, 7)
                                Keys.onDigit8Pressed: event => navigate(event, 8)
                                Keys.onDigit9Pressed: event => navigate(event, 9)
                            }
                            implicitHeight: exportMenuList.contentHeight
                            onClosed: {
                                if (exportMenuList.currentIndex != converterPage.outputFormatComboBox.currentIndex) {
                                    exportMenuList.currentIndex = converterPage.outputFormatComboBox.currentIndex;
                                }
                            }
                        }
                    }
                }
                Button {
                    Material.roundedScale: Material.NotRounded
                    Layout.fillHeight: true
                    flat: true
                    text: qsTr("Settings (&S)")
                    onClicked: settingsMenu.open()
                    Menu {
                        id: settingsMenu
                        y: parent.height
                        MenuItem {
                            text: qsTr("Options (&O)")
                            onTriggered: {
                                actions.openOptions.trigger();
                            }
                        }
                        Menu {
                            id: themesMenu
                            title: qsTr("Themes (&T)")
                            ButtonGroup {
                                id: themeButtonGroup
                            }
                            MenuItem {
                                id: lightThemeMenuItem
                                checkable: true
                                ButtonGroup.group: themeButtonGroup
                                text: qsTr("Light")
                                onTriggered: {
                                    handleThemeChange("Light");
                                }
                            }
                            MenuItem {
                                id: darkThemeMenuItem
                                checkable: true
                                ButtonGroup.group: themeButtonGroup
                                text: qsTr("Dark")
                                onTriggered: {
                                    handleThemeChange("Dark");
                                }
                            }
                            MenuItem {
                                id: systemThemeMenuItem
                                checkable: true
                                ButtonGroup.group: themeButtonGroup
                                text: qsTr("System")
                                onTriggered: {
                                    handleThemeChange("System");
                                }
                            }
                            Component.onCompleted: {
                                let currentTheme = configItems.theme;
                                if (currentTheme === "Light") {
                                    lightThemeMenuItem.checked = true;
                                } else if (currentTheme === "Dark") {
                                    darkThemeMenuItem.checked = true;
                                } else {
                                    systemThemeMenuItem.checked = true;
                                }
                            }
                        }
                        Menu {
                            id: languageMenu
                            title: qsTr("Language (&L)")
                            ButtonGroup {
                                id: languageButtonGroup
                                onClicked: {
                                    dialogs.openDialog.nameFilters[0] = qsTr(converterPage.inputFormatComboBox.currentText) + " (*." + converterPage.inputFormatComboBox.currentValue + ")";
                                }
                            }
                            MenuItem {
                                id: zhCNMenuItem
                                checkable: true
                                ButtonGroup.group: languageButtonGroup
                                text: "简体中文"
                                onTriggered: localeSwitcher.switch_language("zh_CN")
                            }
                            MenuItem {
                                id: enUSMenuItem
                                checkable: true
                                ButtonGroup.group: languageButtonGroup
                                text: "English"
                                onTriggered: localeSwitcher.switch_language("en_US")
                            }
                            MenuItem {
                                id: jaJPMenuItem
                                checkable: true
                                ButtonGroup.group: languageButtonGroup
                                text: "日本語"
                                onTriggered: localeSwitcher.switch_language("ja_JP")
                                enabled: false
                            }
                            MenuItem {
                                id: deDEMenuItem
                                checkable: true
                                ButtonGroup.group: languageButtonGroup
                                text: "Deutsch"
                                onTriggered: localeSwitcher.switch_language("de_DE")
                            }
                            Component.onCompleted: {
                                let currentLanguage = localeSwitcher.get_language();
                                if (currentLanguage === "zh_CN") {
                                    zhCNMenuItem.checked = true;
                                } else if (currentLanguage === "ja_JP") {
                                    jaJPMenuItem.checked = true;
                                } else if (currentLanguage === "en_US") {
                                    deDEMenuItem.checked = true;
                                } else {
                                    enUSMenuItem.checked = true;
                                }
                            }
                        }
                    }
                }
                Button {
                    Material.roundedScale: Material.NotRounded
                    Layout.fillHeight: true
                    flat: true
                    text: qsTr("Help (&H)")
                    onClicked: helpMenu.open()
                    Menu {
                        id: helpMenu
                        width: 250
                        y: parent.height
                        IconMenuItem {
                            action: actions.openAbout
                            icon_name: "mdi7.information-outline"
                            label: qsTr("About (Ctrl+A)")
                        }
                        IconMenuItem {
                            icon_name: "mdi7.progress-upload"
                            label: qsTr("Check for Updates")
                            enabled: true
                            onTriggered: notifier.check_for_updates()
                        }
                        IconMenuItem {
                            action: actions.openDocumentation
                            icon_name: "mdi7.text-box-search-outline"
                            label: qsTr("Documentation (F1)")
                        }
                    }
                }
            }
        }
    }
    Connections {
        target: toolBar
        function onOpenConvertMenu() {
            convertMenu.open();
        }
        function openFormatsMenu() {
            formatsMenu.open();
        }
        function onOpenImportFormatMenu() {
            if (!formatsMenu.opened) {
                formatsMenu.open();
            }
            importFormatMenu.open();
        }
        function onOpenExportFormatMenu() {
            if (!formatsMenu.opened) {
                formatsMenu.open();
            }
            exportFormatMenu.open();
        }
        function openSettingsMenu() {
            settingsMenu.open();
        }
        function onOpenThemesMenu() {
            if (!settingsMenu.opened) {
                settingsMenu.open();
            }
            themesMenu.open();
        }
        function onOpenLanguageMenu() {
            if (!settingsMenu.opened) {
                settingsMenu.open();
            }
            languageMenu.open();
        }
        function onOpenHelpMenu() {
            helpMenu.open();
        }
    }
}
