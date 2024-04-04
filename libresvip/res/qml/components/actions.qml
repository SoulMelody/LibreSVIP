import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import LibreSVIP

Item {
    property QtObject openFile: Action {
        text: qsTr("&Open")
        shortcut: "Ctrl+O"
        onTriggered: {   
            if (!TaskManager.busy) {
                dialogs.openDialog.open()
            }
        }
    }
    property QtObject chooseSavePath: Action {
        text: qsTr("&Choose Save Path")
        shortcut: "Ctrl+Shift+S"
        onTriggered: dialogs.saveDialog.open()
    }
    property QtObject swapInputOutput: Action {
        text: qsTr("&Swap Input/Output")
        shortcut: "Ctrl+Tab"
        onTriggered: {
            converterPage.swapInputOutputButton.clicked()
        }
    }
    property QtObject clearTasks: Action {
        text: qsTr("&Restore Task List")
        shortcut: "Ctrl+R"
        onTriggered: {
            if (!TaskManager.busy) {
                converterPage.taskList.model.clear()
            } else {
                let message_box = messageBox.createObject(
                    window,
                    {
                        body: qsTr("Alert"),
                        message: qsTr("Cannot restore task list while conversion is in progress."),
                        onOk: () => {}
                    }
                )
                message_box.open()
            }
        }
    }
    property QtObject openAbout: Action {
        text: qsTr("&About")
        shortcut: "Ctrl+A"
        onTriggered: dialogs.aboutDialog.open()
    }
    property QtObject openOptions: Action {
        text: qsTr("&Options")
        shortcut: "Alt+O"
        onTriggered: dialogs.settingsDialog.open()
    }
    property QtObject openConvertMenu: Action {
        text: qsTr("&Convert")
        shortcut: "Alt+C"
        onTriggered: toolbar.openConvertMenu()
    }
    property QtObject openImportFormatMenu: Action {
        text: qsTr("&Import From")
        shortcut: "Alt+I"
        onTriggered: {   
            if (!TaskManager.busy) {
                toolbar.openImportFormatMenu()
            }
        }
    }
    property QtObject openExportFormatMenu: Action {
        text: qsTr("&Export To")
        shortcut: "Alt+E"
        onTriggered: {   
            if (!TaskManager.busy) {
                toolbar.openExportFormatMenu()
            }
        }
    }
    property QtObject openHelpMenu: Action {
        text: qsTr("&Help")
        shortcut: "Alt+H"
        onTriggered: toolbar.openHelpMenu()
    }
    property QtObject openLanguageMenu: Action {
        text: qsTr("&Language")
        shortcut: "Alt+L"
        onTriggered: toolbar.openLanguageMenu()
    }
    property QtObject openThemesMenu: Action {
        text: qsTr("&Themes")
        shortcut: "Alt+T"
        onTriggered: toolbar.openThemesMenu()
    }
    property QtObject startConversion: Action {
        text: qsTr("&Start Conversion")
        shortcut: "Ctrl+Enter"
        onTriggered: {
            if (converterPage.startConversionButton.enabled) {
                TaskManager.start_conversion()
            }
        }
    }
    property QtObject openDocumentation: Action {
        text: qsTr("&Documentation")
        shortcut: "F1"
        onTriggered: Notifier.open_link("https://soulmelody.github.io/LibreSVIP")
    }
    property QtObject quit: Action {
        text: qsTr("&Quit")
        shortcut: "Ctrl+Q"
        onTriggered: Qt.quit()
    }
}