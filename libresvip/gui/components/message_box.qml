import QtQuick
import QtQuick.Window
import QtQuick.Dialogs

MessageDialog {
    property var body: "";
    property var message: "";
    property var onOk: null;
    property var onCancel: null;
    text: body
    informativeText: message
    buttons: {
        let buttons = MessageDialog.NoButton
        if (onOk) {
            buttons = MessageDialog.Ok
            if (onCancel) {
                buttons |= MessageDialog.Cancel
            }
        }
        else if (onCancel) {
            buttons = MessageDialog.Cancel
        }
        return buttons
    }
    onButtonClicked: (button, role) => {
        switch (button) {
            case MessageDialog.Ok:
                onOk()
                break;
            case MessageDialog.Cancel: {
                onCancel()
                break;
            }
        }
        destroy()
    }
}