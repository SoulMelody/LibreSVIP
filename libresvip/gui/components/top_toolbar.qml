import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ToolBar {
    signal openConvertMenu()
    signal openPluginsMenu()
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

    RowLayout{
        anchors.left: parent.left
        ToolButton {
            id: convertButton
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
                    action: actions.startConversion;
                    icon_name: "mdi6.share-all-outline"
                    label: qsTr("Perform All Tasks (Ctrl+Enter)");
                    enabled: converterPage.taskList.count > 0
                    Component.onCompleted: {
                        py.task_manager.tasks_size_changed.connect(function() {
                            enabled = converterPage.taskList.count > 0
                        })
                    }
                }
                IconMenuItem {
                    action: actions.clearTasks;
                    icon_name: "mdi6.refresh"
                    label: qsTr("Clear Tasks (Ctrl+R)");
                    enabled: converterPage.taskList.count > 0
                    Component.onCompleted: {
                        py.task_manager.tasks_size_changed.connect(function() {
                            enabled = converterPage.taskList.count > 0
                        })
                    }
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

        ToolSeparator {}

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
                MenuItem{
                    text: qsTr("Light");
                    onTriggered: {
                        window.Material.theme = Material.Light
                        py.config_items.set_theme("Light")
                    }
                }
                MenuItem{
                    text: qsTr("Dark");
                    onTriggered: {
                        window.Material.theme = Material.Dark
                        py.config_items.set_theme("Dark")
                    }
                }
                MenuItem{
                    text: qsTr("System");
                    onTriggered: {
                        window.Material.theme = Material.System
                        py.config_items.set_theme("System")
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
                MenuItem{
                    text: "简体中文";
                    onTriggered: py.locale.switch_language("zh-CN")
                }
                MenuItem{
                    text: "English";
                    onTriggered: py.locale.switch_language("en-US")
                }
                MenuItem{
                    text: "日本語";
                    onTriggered: py.locale.switch_language("ja-JP")
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
    }

    Label {
        text: window.title + " - " + qsTr("SVS Projects Converter")
        anchors.centerIn: parent
        font.pixelSize: Qt.application.font.pixelSize * 1.2
    }

    RowLayout {
        anchors.right: parent.right
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