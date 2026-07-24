import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material

Popup {
    id: root

    property string format_type: ""

    y: 45
    x: Math.round((parent.width - width) / 2)
    padding: 16
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent

    function emptyInfo() {
        return {
            "name": "",
            "author": "",
            "website": "",
            "description": "",
            "version": "",
            "file_format": "",
            "suffix": "(*.*)",
            "icon_base64": ""
        };
    }

    contentItem: PluginInfo {
        id: pluginInfo
        info: root.emptyInfo()
    }

    onOpened: {
        pluginInfo.info = taskManager.plugin_info(format_type);
    }

    enter: Transition {
        NumberAnimation {
            property: "opacity"
            from: 0.0
            to: 1.0
            duration: 150
        }
    }

    exit: Transition {
        NumberAnimation {
            property: "opacity"
            from: 1.0
            to: 0.0
            duration: 120
        }
    }
}
