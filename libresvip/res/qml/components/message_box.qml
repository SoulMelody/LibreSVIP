import QtQuick
import QtQuick.Window
import QtQuick.Dialogs

MessageDialog {
    property var body: ""
    property var message: ""
    property var onOk: null
    property var onCancel: null
    text: body
    informativeText: message
    buttons: {
        let buttons = MessageDialog.NoButton;
        if (onOk) {
            buttons = MessageDialog.Ok | MessageDialog.YesToAll;
            if (onCancel) {
                buttons |= MessageDialog.Cancel | MessageDialog.NoToAll;
            }
        }
        return buttons;
    }
    onButtonClicked: (button, role) => {
        switch (button) {
        case MessageDialog.Ok:
            onOk();
            break;
        case MessageDialog.Cancel:
            {
                onCancel();
                break;
            }
        case MessageDialog.YesToAll:
            {
                onOk();
                window.yesToAll = true;
                break;
            }
        case MessageDialog.NoToAll:
            {
                onCancel();
                window.noToAll = true;
                break;
            }
        }
        destroy();
    }
}
