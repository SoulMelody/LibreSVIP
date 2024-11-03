import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import LibreSVIP

Item {
    property QtObject openFile: Action {
        shortcut: "Ctrl+O"
        onTriggered: {
            if (!taskManager.busy) {
                dialogs.openDialog.open();
            }
        }
    }
    property QtObject chooseSavePath: Action {
        shortcut: "Ctrl+Shift+S"
        onTriggered: dialogs.saveDialog.open()
    }
    property QtObject swapInputOutput: Action {
        shortcut: "Ctrl+Tab"
        onTriggered: {
            converterPage.swapInputOutputButton.clicked();
        }
    }
    property QtObject clearTasks: Action {
        shortcut: "Ctrl+R"
        onTriggered: {
            if (!taskManager.busy) {
                converterPage.taskList.model.clear();
            } else {
                let message_box = messageBox.createObject(window, {
                    body: qsTr("Alert"),
                    message: qsTr("Cannot restore task list while conversion is in progress."),
                    onOk: () => {}
                });
                message_box.open();
            }
        }
    }
    property QtObject openAbout: Action {
        shortcut: "Ctrl+A"
        onTriggered: dialogs.aboutDialog.open()
    }
    property QtObject openOptions: Action {
        shortcut: "Alt+O"
        onTriggered: dialogs.settingsDialog.open()
    }
    property QtObject openConvertMenu: Action {
        shortcut: "Alt+C"
        onTriggered: toolbar.openConvertMenu()
    }
    property QtObject openImportFormatMenu: Action {
        shortcut: "Alt+I"
        onTriggered: {
            if (!taskManager.busy) {
                toolbar.openImportFormatMenu();
            }
        }
    }
    property QtObject openExportFormatMenu: Action {
        shortcut: "Alt+E"
        onTriggered: {
            if (!taskManager.busy) {
                toolbar.openExportFormatMenu();
            }
        }
    }
    property QtObject openHelpMenu: Action {
        shortcut: "Alt+H"
        onTriggered: toolbar.openHelpMenu()
    }
    property QtObject openLanguageMenu: Action {
        shortcut: "Alt+L"
        onTriggered: toolbar.openLanguageMenu()
    }
    property QtObject openThemesMenu: Action {
        shortcut: "Alt+T"
        onTriggered: toolbar.openThemesMenu()
    }
    property QtObject startConversion: Action {
        shortcut: "Ctrl+Enter"
        onTriggered: {
            if (converterPage.startConversionButton.enabled) {
                taskManager.start_conversion();
            }
        }
    }
    property QtObject openDocumentation: Action {
        shortcut: "F1"
        onTriggered: notifier.open_link("https://soulmelody.github.io/LibreSVIP")
    }
    property QtObject quit: Action {
        shortcut: "Ctrl+Q"
        onTriggered: Qt.quit()
    }
}
