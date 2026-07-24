import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material

ComboBox {
    id: root

    implicitHeight: Math.max(Theme.minClickSize, 40)
    textRole: "text"
    valueRole: "value"
    model: [
        {
            value: "Overwrite",
            text: qsTr("Overwrite")
        },
        {
            value: "Skip",
            text: qsTr("Skip")
        },
        {
            value: "Prompt",
            text: qsTr("Prompt")
        }
    ]
    currentIndex: indexOfValue(configItems.conflict_policy)
    Component.onCompleted: {
        // The initial currentIndex binding can run before the array model has roles.
        root.currentIndex = root.indexOfValue(configItems.conflict_policy);
    }
    onActivated: index => {
        configItems.conflict_policy = valueAt(index);
    }
    Connections {
        target: configItems
        function onConflict_policy_changed(value) {
            root.currentIndex = root.indexOfValue(value);
        }
    }
}
