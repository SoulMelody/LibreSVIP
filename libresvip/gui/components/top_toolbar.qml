import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Controls.Material.impl
import QtQuick.Layouts
import LibreSVIP

ToolBar {
    id: toolBar
    signal openConvertMenu()
    signal openFormatsMenu()
    signal openImportFormatMenu()
    signal openExportFormatMenu()
    signal openPluginsMenu()
    signal openSettingsMenu()
    signal openThemesMenu()
    signal openLanguageMenu()
    signal openHelpMenu()

    function toggleMaximized() {
        // from https://github.com/yjg30737/qml-rounded-shadow-framelesswindow
        if (window.visibility === Window.Maximized) {
            window.showNormal();
        } else {
            window.showMaximized();
        }
    }

    background: Rectangle {
        implicitHeight: 48
        color: window.Material.background
        border.width: 1
        border.color: Material.color(
            Material.Grey,
            Material.Shade300
        )

        layer.enabled: toolBar.Material.elevation > 0
        layer.effect: ElevationEffect {
            elevation: toolBar.Material.elevation
            fullWidth: true
        }
    }

    Item {
        anchors.fill: parent
        TapHandler {
            onTapped: if (tapCount === 2) toggleMaximized()
            gesturePolicy: TapHandler.DragThreshold
        }
        DragHandler {
            grabPermissions: TapHandler.CanTakeOverFromAnything
            onActiveChanged: if (active) { window.startSystemMove(); }
        }
    }

    RowLayout {
        anchors.fill: parent
        layoutDirection: Qt.RightToLeft

        RowLayout {
            Layout.alignment: Qt.AlignRight
            spacing: 0
            Button {
                id: minimizeButton
                Material.roundedScale: Material.NotRounded
                Layout.fillHeight: true
                leftPadding: 0
                rightPadding: 0
                topInset: 0
                flat: true
                implicitWidth: 46
                background.implicitWidth: implicitWidth
                text: IconicFontLoader.icon("mdi7.window-minimize")
                font.family: "Material Design Icons"
                font.pixelSize: Qt.application.font.pixelSize * 1.2
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
                flat: true
                implicitWidth: 46
                background.implicitWidth: implicitWidth
                text: window.visibility == Window.Maximized ? IconicFontLoader.icon("mdi7.window-restore") : IconicFontLoader.icon("mdi7.window-maximize")
                font.family: "Material Design Icons"
                font.pixelSize: Qt.application.font.pixelSize * 1.2
                onClicked: toggleMaximized()
            }

            Button {
                id: exitButton
                Material.roundedScale: Material.NotRounded
                Layout.fillHeight: true
                leftPadding: 0
                rightPadding: 0
                topInset: 0
                flat: true
                implicitWidth: 46
                background.implicitWidth: implicitWidth
                text: hovered ? "<font color='white'>" + IconicFontLoader.icon("mdi7.close") + "</font>" : IconicFontLoader.icon("mdi7.close")
                font.family: "Material Design Icons"
                font.pixelSize: Qt.application.font.pixelSize * 1.2
                onClicked: actions.quit.trigger()
                onHoveredChanged: {
                    if (hovered) {
                        exitButton.background.color = Material.color(Material.Red)
                    } else {
                        exitButton.background.color = "transparent"
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

        ToolSeparator {}

        MenuBar {
            id: menus
            spacing: 0
            background : Rectangle {
                implicitHeight: 40
                color: window.Material.background
            }
            menus: [
                Menu {
                    id: convertMenu
                    width: 300
                    title: qsTr("Convert (&C)")
                    IconMenuItem {
                        action: actions.openFile;
                        icon_name: "mdi7.file-import-outline"
                        label: qsTr("Import Projects (Ctrl+O)");
                    }
                    IconMenuItem {
                        id: startConversionMenuItem
                        action: actions.startConversion;
                        icon_name: "mdi7.share-all-outline"
                        label: qsTr("Perform All Tasks (Ctrl+Enter)");
                        enabled: converterPage.startConversionButton.enabled
                    }
                    IconMenuItem {
                        id: clearTasksMenuItem
                        action: actions.clearTasks;
                        icon_name: "mdi7.refresh"
                        label: qsTr("Clear Tasks (Ctrl+R)");
                        enabled: converterPage.taskList.count > 0
                    }
                    MenuSeparator {}
                    IconMenuItem {
                        action: actions.swapInputOutput;
                        icon_name: "mdi7.swap-vertical"
                        label: qsTr("Swap Input and Output (Ctrl+Tab)");
                    }
                },
                Menu {
                    id: formatsMenu
                    width: 200
                    title: qsTr("Formats (&F)")
                    Menu {
                        id: importFormatMenu
                        width: 300
                        title: qsTr("Input Format (&I)")
                        ButtonGroup {
                            id: inputFormatButtonGroup
                        }
                        contentItem: ListView {
                            id: importMenuList
                            model: TaskManager.qget("input_formats")
                            delegate: MenuItem {
                                checkable: true
                                checked: ListView.isCurrentItem
                                ButtonGroup.group: inputFormatButtonGroup
                                onTriggered: {
                                    TaskManager.set_str("input_format", model.value)
                                }
                                text: String(index % 10) + " " + qsTr(model.text)
                            }
                            Connections {
                                target: TaskManager
                                function onInput_format_changed(input_format) {
                                    let new_index = converterPage.inputFormatComboBox.indexOfValue(input_format)
                                    if (new_index != importMenuList.currentIndex) {
                                        importMenuList.currentIndex = new_index
                                    }
                                }
                            }
                            focus: true
                            function navigate(event, key) {
                                if (count >= 10 + key) {
                                    let next_focus = 10 * (Math.floor(currentIndex / 10) + 1)
                                    next_focus = next_focus + key >= count ? key : next_focus + key
                                    itemAtIndex(next_focus).ListView.focus = true
                                    currentIndex = next_focus
                                } else {
                                    itemAtIndex(key).triggered()
                                }
                            }
                            Keys.onDigit0Pressed: (event) => navigate(event, 0)
                            Keys.onDigit1Pressed: (event) => navigate(event, 1)
                            Keys.onDigit2Pressed: (event) => navigate(event, 2)
                            Keys.onDigit3Pressed: (event) => navigate(event, 3)
                            Keys.onDigit4Pressed: (event) => navigate(event, 4)
                            Keys.onDigit5Pressed: (event) => navigate(event, 5)
                            Keys.onDigit6Pressed: (event) => navigate(event, 6)
                            Keys.onDigit7Pressed: (event) => navigate(event, 7)
                            Keys.onDigit8Pressed: (event) => navigate(event, 8)
                            Keys.onDigit9Pressed: (event) => navigate(event, 9)
                        }
                        implicitHeight: importMenuList.contentHeight
                        onClosed: {
                            if (importMenuList.currentIndex != converterPage.inputFormatComboBox.currentIndex) {
                                importMenuList.currentIndex = converterPage.inputFormatComboBox.currentIndex
                            }
                        }
                    }
                    Menu {
                        id: exportFormatMenu
                        width: 300
                        title: qsTr("Output Format (&E)")
                        ButtonGroup {
                            id: exportFormatButtonGroup
                        }
                        contentItem: ListView {
                            id: exportMenuList
                            model: TaskManager.qget("output_formats")
                            delegate: MenuItem {
                                checkable: true
                                checked: ListView.isCurrentItem
                                ButtonGroup.group: exportFormatButtonGroup
                                onTriggered: {
                                    TaskManager.set_str("output_format", model.value)
                                }
                                text: String(index % 10) + " " + qsTr(model.text)
                            }
                            Connections {
                                target: TaskManager
                                function onOutput_format_changed(output_format) {
                                    let new_index = converterPage.outputFormatComboBox.indexOfValue(output_format)
                                    if (new_index != exportMenuList.currentIndex) {
                                        exportMenuList.currentIndex = new_index
                                    }
                                }
                            }
                            focus: true
                            function navigate(event, key) {
                                if (count >= 10 + key) {
                                    let next_focus = 10 * (Math.floor(currentIndex / 10) + 1)
                                    next_focus = next_focus + key >= count ? key : next_focus + key
                                    itemAtIndex(next_focus).ListView.focus = true
                                    currentIndex = next_focus
                                } else {
                                    itemAtIndex(key).triggered()
                                }
                            }
                            Keys.onDigit0Pressed: (event) => navigate(event, 0)
                            Keys.onDigit1Pressed: (event) => navigate(event, 1)
                            Keys.onDigit2Pressed: (event) => navigate(event, 2)
                            Keys.onDigit3Pressed: (event) => navigate(event, 3)
                            Keys.onDigit4Pressed: (event) => navigate(event, 4)
                            Keys.onDigit5Pressed: (event) => navigate(event, 5)
                            Keys.onDigit6Pressed: (event) => navigate(event, 6)
                            Keys.onDigit7Pressed: (event) => navigate(event, 7)
                            Keys.onDigit8Pressed: (event) => navigate(event, 8)
                            Keys.onDigit9Pressed: (event) => navigate(event, 9)
                        }
                        implicitHeight: exportMenuList.contentHeight
                        onClosed: {
                            if (exportMenuList.currentIndex != converterPage.outputFormatComboBox.currentIndex) {
                                exportMenuList.currentIndex = converterPage.outputFormatComboBox.currentIndex
                            }
                        }
                    }
                },
                Menu {
                    id: pluginsMenu
                    title: qsTr("Plugins (&P)")
                    IconMenuItem {
                        action: actions.installPlugin;
                        icon_name: "mdi7.puzzle-plus-outline"
                        label: qsTr("Install a Plugin (Ctrl+I)")
                    }
                    IconMenuItem {
                        icon_name: "mdi7.puzzle-edit-outline"
                        label: qsTr("Manage Plugins")
                        enabled: false
                    }
                    IconMenuItem {
                        icon_name: "mdi7.store-search"
                        label: qsTr("Open Plugin Store")
                        enabled: false
                    }
                },
                Menu {
                    id: settingsMenu
                    title: qsTr("Settings (&S)")
                    MenuItem {
                        text: qsTr("Options (&O)")
                        onTriggered: {
                            actions.openOptions.trigger()
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
                                handleThemeChange("Light")
                            }
                        }
                        MenuItem {
                            id: darkThemeMenuItem
                            checkable: true
                            ButtonGroup.group: themeButtonGroup
                            text: qsTr("Dark")
                            onTriggered: {
                                handleThemeChange("Dark")
                            }
                        }
                        MenuItem {
                            id: systemThemeMenuItem
                            checkable: true
                            ButtonGroup.group: themeButtonGroup
                            text: qsTr("System")
                            onTriggered: {
                                handleThemeChange("System")
                            }
                        }
                        Component.onCompleted: {
                            let currentTheme = ConfigItems.get_theme()
                            if (currentTheme === "Light") {
                                lightThemeMenuItem.checked = true
                            } else if (currentTheme === "Dark") {
                                darkThemeMenuItem.checked = true
                            } else {
                                systemThemeMenuItem.checked = true
                            }
                        }
                    }
                    Menu {
                        id: languageMenu
                        title: qsTr("Language (&L)")
                        ButtonGroup {
                            id: languageButtonGroup
                            onClicked: {
                                dialogs.openDialog.nameFilters[0] = qsTr(converterPage.inputFormatComboBox.currentText) + " (*." + converterPage.inputFormatComboBox.currentValue + ")"
                            }
                        }
                        MenuItem {
                            id: zhCNMenuItem
                            checkable: true
                            ButtonGroup.group: languageButtonGroup
                            text: "简体中文";
                            onTriggered: LocaleSwitcher.switch_language("zh_CN")
                        }
                        MenuItem {
                            id: enUSMenuItem
                            checkable: true
                            ButtonGroup.group: languageButtonGroup
                            text: "English";
                            onTriggered: LocaleSwitcher.switch_language("en_US")
                        }
                        MenuItem {
                            id: jaJPMenuItem
                            checkable: true
                            ButtonGroup.group: languageButtonGroup
                            text: "日本語";
                            onTriggered: LocaleSwitcher.switch_language("ja_JP")
                            enabled: false
                        }
                        Component.onCompleted: {
                            let currentLanguage = LocaleSwitcher.get_language()
                            if (currentLanguage === "zh_CN") {
                                zhCNMenuItem.checked = true
                            } else if (currentLanguage === "en_US") {
                                enUSMenuItem.checked = true
                            } else {
                                jaJPMenuItem.checked = true
                            }
                        }
                    }
                },
                Menu {
                    id: helpMenu
                    title: qsTr("Help (&H)")
                    width: 250
                    IconMenuItem {
                        action: actions.openAbout;
                        icon_name: "mdi7.information-outline"
                        label: qsTr("About (Ctrl+A)");
                    }
                    IconMenuItem {
                        icon_name: "mdi7.progress-upload"
                        label: qsTr("Check for Updates");
                        enabled: true
                        onTriggered: Notifier.check_for_updates()
                    }
                    IconMenuItem {
                        icon_name: "mdi7.text-box-search-outline"
                        label: qsTr("Documentation (F1)");
                        enabled: false
                    }
                }
            ]
        }

        Rectangle {
            width: 48
            height: 48
            color: "transparent"
            Image {
                anchors.centerIn: parent
                source: ConfigItems.icon_data()
                sourceSize.width: 20
                sourceSize.height: 20
            }
        }
    }
    Connections {
        target: toolBar
        function onOpenConvertMenu() {
            convertMenu.open()
        }
        function openFormatsMenu() {
            formatsMenu.open()
        }
        function onOpenImportFormatMenu() {
            if (!formatsMenu.opened) {
                formatsMenu.open()
            }
            importFormatMenu.open()
        }
        function onOpenExportFormatMenu() {
            if (!formatsMenu.opened) {
                formatsMenu.open()
            }
            exportFormatMenu.open()
        }
        function onOpenPluginsMenu() {
            pluginsMenu.open()
        }
        function openSettingsMenu() {
            settingsMenu.open()
        }
        function onOpenThemesMenu() {
            if (!settingsMenu.opened) {
                settingsMenu.open()
            }
            themesMenu.open()
        }
        function onOpenLanguageMenu() {
            if (!settingsMenu.opened) {
                settingsMenu.open()
            }
            languageMenu.open()
        }
        function onOpenHelpMenu() {
            helpMenu.open()
        }
    }
}