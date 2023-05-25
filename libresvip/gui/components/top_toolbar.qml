import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ToolBar {
    signal openConvertMenu()
    signal openImportFormatMenu()
    signal openExportFormatMenu()
    signal openPluginsMenu()
    signal openThemesMenu()
    signal openLanguageMenu()
    signal openHelpMenu()
    signal themeChanged()

    function toggleMaximized() {
        // from https://github.com/yjg30737/qml-rounded-shadow-framelesswindow
        if (window.visibility === Window.Maximized) {
            window.showNormal();
        } else {
            window.showMaximized();
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
        RowLayout {
            id: menus
            Layout.alignment: Qt.AlignLeft
            spacing: 0
            ToolButton {
                id: convertButton
                Layout.alignment: Qt.AlignLeft
                text: py.qta.icon("mdi6.cached")
                width: 40
                font.family: materialFontLoader.name
                font.pixelSize: Qt.application.font.pixelSize * 1.5
                onClicked: convertMenu.open()
                ToolTip.visible: hovered
                ToolTip.text: qsTr("Convert (&C)")
                Menu {
                    id: convertMenu
                    y: parent.height
                    width: 300
                    IconMenuItem {
                        action: actions.openFile;
                        icon_name: "mdi6.file-import-outline"
                        label: qsTr("Import Projects (Ctrl+O)");
                    }
                    IconMenuItem {
                        id: startConversionMenuItem
                        action: actions.startConversion;
                        icon_name: "mdi6.share-all-outline"
                        label: qsTr("Perform All Tasks (Ctrl+Enter)");
                        enabled: converterPage.startConversionButton.enabled
                    }
                    IconMenuItem {
                        id: clearTasksMenuItem
                        action: actions.clearTasks;
                        icon_name: "mdi6.refresh"
                        label: qsTr("Clear Tasks (Ctrl+R)");
                        enabled: converterPage.taskList.count > 0
                    }
                    MenuSeparator {}
                    IconMenuItem {
                        action: actions.swapInputOutput;
                        icon_name: "mdi6.swap-vertical"
                        label: qsTr("Swap Input and Output (Ctrl+Tab)");
                    }
                }
                Component.onCompleted: {
                    openConvertMenu.connect(convertMenu.open)
                }
            }

            ToolButton {
                id: inputFormatButton
                text: py.qta.icon("mdi6.import")
                width: 40
                font.family: materialFontLoader.name
                font.pixelSize: Qt.application.font.pixelSize * 1.5
                onClicked: importFormatMenu.open()
                ToolTip.visible: hovered
                ToolTip.text: qsTr("Input Format (&F)")
                ButtonGroup {
                    id: inputFormatButtonGroup
                }
                Menu {
                    id: importFormatMenu
                    y: parent.height
                    width: 300
                    contentItem: ListView {
                        id: importMenuList
                        model: py.task_manager.qget("input_formats")
                        delegate: MenuItem {
                            checkable: true
                            checked: ListView.isCurrentItem
                            ButtonGroup.group: inputFormatButtonGroup
                            onTriggered: {
                                py.task_manager.set_str("input_format", model.value)
                            }
                            text: String(index % 10) + " " + model.text
                        }
                        Component.onCompleted: {
                            py.task_manager.input_format_changed.connect((input_format) => {
                                let new_index = converterPage.inputFormatComboBox.indexOfValue(input_format)
                                if (new_index != currentIndex) {
                                    currentIndex = new_index
                                }
                            })
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
                Component.onCompleted: {
                    openImportFormatMenu.connect(importFormatMenu.open)
                }
            }

            ToolButton {
                id: outputFormatButton
                text: py.qta.icon("mdi6.export")
                width: 40
                font.family: materialFontLoader.name
                font.pixelSize: Qt.application.font.pixelSize * 1.5
                onClicked: exportFormatMenu.open()
                ToolTip.visible: hovered
                ToolTip.text: qsTr("Output Format (&E)")
                ButtonGroup {
                    id: exportFormatButtonGroup
                }
                Menu {
                    id: exportFormatMenu
                    y: parent.height
                    width: 300
                    contentItem: ListView {
                        id: exportMenuList
                        model: py.task_manager.qget("output_formats")
                        delegate: MenuItem {
                            checkable: true
                            checked: ListView.isCurrentItem
                            ButtonGroup.group: exportFormatButtonGroup
                            onTriggered: {
                                py.task_manager.set_str("output_format", model.value)
                            }
                            text: String(index % 10) + " " + model.text
                        }
                        Component.onCompleted: {
                            py.task_manager.output_format_changed.connect((output_format) => {
                                let new_index = converterPage.outputFormatComboBox.indexOfValue(output_format)
                                if (new_index != currentIndex) {
                                    currentIndex = new_index
                                }
                            })
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
                Component.onCompleted: {
                    openExportFormatMenu.connect(exportFormatMenu.open)
                }
            }

            ToolSeparator {}

            ToolButton {
                id: pluginsButton
                text: py.qta.icon("mdi6.puzzle-outline")
                width: 40
                font.family: materialFontLoader.name
                font.pixelSize: Qt.application.font.pixelSize * 1.5
                onClicked: pluginsMenu.open()
                ToolTip.visible: hovered
                ToolTip.text: qsTr("Plugins (&P)")
                Menu {
                    id: pluginsMenu
                    y: parent.height
                    IconMenuItem {
                        action: actions.installPlugin;
                        icon_name: "mdi6.puzzle-plus-outline"
                        label: qsTr("Install a Plugin (Ctrl+I)")
                    }
                    IconMenuItem {
                        icon_name: "mdi6.puzzle-edit-outline"
                        label: qsTr("Manage Plugins")
                        enabled: false
                    }
                    IconMenuItem {
                        icon_name: "mdi6.store-search"
                        label: qsTr("Open Plugin Store")
                        enabled: false
                    }
                }
                Component.onCompleted: {
                    openPluginsMenu.connect(pluginsMenu.open)
                }
            }

            ToolButton {
                id: settingsButton
                text: py.qta.icon("mdi6.cog-outline")
                width: 40
                font.family: materialFontLoader.name
                font.pixelSize: Qt.application.font.pixelSize * 1.5
                onClicked: actions.openSettings.trigger()
                ToolTip.visible: hovered
                ToolTip.text: qsTr("Settings (&O)")
            }

            ToolButton {
                id : themesButton
                text: py.qta.icon("mdi6.invert-colors")
                width: 40
                font.family: materialFontLoader.name
                font.pixelSize: Qt.application.font.pixelSize * 1.5
                onClicked: themesMenu.open()
                ToolTip.visible: hovered
                ToolTip.text: qsTr("Themes (&T)")
                Menu {
                    id: themesMenu
                    y: parent.height
                    MenuItem {
                        text: qsTr("Light");
                        onTriggered: {
                            window.Material.theme = Material.Light
                            py.config_items.set_theme("Light")
                            themeChanged()
                        }
                    }
                    MenuItem {
                        text: qsTr("Dark");
                        onTriggered: {
                            window.Material.theme = Material.Dark
                            py.config_items.set_theme("Dark")
                            themeChanged()
                        }
                    }
                    MenuItem {
                        text: qsTr("System");
                        onTriggered: {
                            window.Material.theme = Material.System
                            py.config_items.set_theme("System")
                            themeChanged()
                        }
                    }
                }
                Component.onCompleted: {
                    openThemesMenu.connect(themesMenu.open)
                }
            }

            ToolButton {
                id: languageButton
                text: py.qta.icon("mdi6.translate")
                width: 40
                font.family: materialFontLoader.name
                font.pixelSize: Qt.application.font.pixelSize * 1.5
                onClicked: languageMenu.open()
                ToolTip.visible: hovered
                ToolTip.text: qsTr("Language (&L)")
                Menu {
                    id: languageMenu
                    y: parent.height
                    MenuItem {
                        text: "简体中文";
                        onTriggered: py.locale.switch_language("zh_CN")
                    }
                    MenuItem {
                        text: "English";
                        onTriggered: py.locale.switch_language("en_US")
                    }
                    MenuItem {
                        text: "日本語";
                        onTriggered: py.locale.switch_language("ja_JP")
                        enabled: false
                    }
                }
                Component.onCompleted: {
                    openLanguageMenu.connect(languageMenu.open)
                }
            }

            ToolSeparator {}

            ToolButton {
                id: helpButton
                text: py.qta.icon("mdi6.help-circle-outline")
                width: 40
                font.family: materialFontLoader.name
                font.pixelSize: Qt.application.font.pixelSize * 1.5
                onClicked: helpMenu.open()
                ToolTip.visible: hovered
                ToolTip.text: qsTr("Help (&H)")
                Menu {
                    id: helpMenu
                    y: parent.height
                    width: 250
                    title: qsTr("Help");
                    IconMenuItem {
                        action: actions.openAbout;
                        icon_name: "mdi6.information-outline"
                        label: qsTr("About (Alt+I)");
                    }
                    IconMenuItem {
                        icon_name: "mdi6.progress-upload"
                        label: qsTr("Check for Updates");
                        enabled: false
                        // onTriggered: py.notifier.notify("info", qsTr("Checking for updates..."))
                    }
                    IconMenuItem {
                        icon_name: "mdi6.text-box-search-outline"
                        label: qsTr("Documentation (F1)");
                        enabled: false
                    }
                }
                Component.onCompleted: {
                    openHelpMenu.connect(helpMenu.open)
                }
            }

            ToolSeparator {}

            Label {
                Layout.fillWidth: true
                text: window.title + " - " + qsTr("SVS Projects Converter")
                font.pixelSize: Qt.application.font.pixelSize * 1.2
                elide: Text.ElideRight
            }
        }

        RowLayout {
            Layout.alignment: Qt.AlignRight
            ToolButton {
                id: minimizeButton
                text: py.qta.icon("mdi6.window-minimize")
                width: 40
                font.family: materialFontLoader.name
                font.pixelSize: Qt.application.font.pixelSize * 1.5
                onClicked: window.showMinimized();
            }

            ToolButton {
                id: maximizeButton
                text: window.visibility == Window.Maximized ? py.qta.icon("mdi6.window-restore") : py.qta.icon("mdi6.window-maximize")
                width: 40
                font.family: materialFontLoader.name
                font.pixelSize: Qt.application.font.pixelSize * 1.5
                onClicked: toggleMaximized()
            }

            ToolButton {
                id: exitButton
                text: py.qta.icon("mdi6.close")
                width: 40
                font.family: materialFontLoader.name
                font.pixelSize: Qt.application.font.pixelSize * 1.5
                onClicked: actions.quit.trigger();
            }
        }
    }
}