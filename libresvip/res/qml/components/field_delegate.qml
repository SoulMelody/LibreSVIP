pragma Translator: converter_page

import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ColumnLayout {
    id: root

    property var field: ({})
    property bool showSeparator: true
    signal valueChanged(var value)

    spacing: 0

    function fieldText(target) {
        if (!target || target.value === undefined || target.value === null) {
            return "";
        }
        return String(target.value);
    }

    function emitValue(value) {
        root.valueChanged(value);
    }

    function componentFor(fieldType) {
        switch (fieldType) {
        case "bool":
            return switchItem;
        case "enum":
            return comboBoxItem;
        case "color":
            return colorPickerItem;
        default:
            return textFieldItem;
        }
    }

    IntValidator {
        id: intValidator
    }

    DoubleValidator {
        id: doubleValidator
    }

    Component {
        id: helpButtonItem
        IconButton {
            icon_name: "mdi7.help-circle-outline"
            accessibleName: qsTr("Help")
            cursor_shape: Qt.WhatsThisCursor
            visible: !!(root.field && root.field.description)
            ToolTip {
                y: parent.y - parent.height
                visible: parent.hovered
                text: qsTr((root.field && root.field.description) || "")
            }
        }
    }

    Loader {
        Layout.fillWidth: true
        Layout.minimumHeight: 40
        sourceComponent: root.field ? root.componentFor(root.field.type) : null
    }

    RowLayout {
        Layout.fillWidth: true
        visible: root.showSeparator
        Label {
            text: iconicFontLoader.icon("mdi7.tune-variant")
            font.family: "Material Design Icons"
            font.pixelSize: 12
        }
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 1
            color: Theme.colorBorder
        }
    }

    Component {
        id: textFieldItem
        RowLayout {
            Label {
                text: qsTr((root.field && root.field.title) || "") + "："
                Layout.alignment: Qt.AlignVCenter
                font.pixelSize: 12
                fontSizeMode: Text.Fit
                wrapMode: Text.Wrap
                Layout.preferredWidth: 150
            }
            TextField {
                Layout.fillWidth: true
                text: root.fieldText(root.field)
                validator: {
                    switch (root.field ? root.field.type : "") {
                    case "int":
                        return intValidator;
                    case "float":
                        return doubleValidator;
                    default:
                        return null;
                    }
                }
                onEditingFinished: root.emitValue(text)
            }
            Loader {
                sourceComponent: helpButtonItem
            }
        }
    }

    Component {
        id: switchItem
        RowLayout {
            Label {
                text: qsTr((root.field && root.field.title) || "") + "："
                Layout.alignment: Qt.AlignVCenter
                font.pixelSize: 12
                fontSizeMode: Text.Fit
                wrapMode: Text.Wrap
                Layout.preferredWidth: 150
            }
            Switch {
                checked: !!(root.field && root.field.value)
                onCheckedChanged: root.emitValue(checked)
            }
            Item {
                Layout.fillWidth: true
            }
            Loader {
                sourceComponent: helpButtonItem
            }
        }
    }

    Component {
        id: comboBoxItem
        RowLayout {
            id: comboBoxRow

            function choiceAt(choiceIndex) {
                var choices = root.field && root.field.choices ? root.field.choices : [];
                return choiceIndex >= 0 && choiceIndex < choices.length ? choices[choiceIndex] : null;
            }
            function choiceValue(choice) {
                return choice ? choice.value : null;
            }
            function choiceText(choice) {
                return choice && choice.text ? choice.text : "";
            }
            Label {
                text: qsTr((root.field && root.field.title) || "") + "："
                Layout.alignment: Qt.AlignVCenter
                font.pixelSize: 12
                fontSizeMode: Text.Fit
                wrapMode: Text.Wrap
                Layout.preferredWidth: 150
            }
            ComboBox {
                id: fieldCombo
                Layout.fillWidth: true
                textRole: "text"
                valueRole: "value"
                model: root.field && root.field.choices ? root.field.choices : []
                displayText: qsTr(comboBoxRow.choiceText(comboBoxRow.choiceAt(currentIndex)))
                currentIndex: {
                    var choices = root.field && root.field.choices ? root.field.choices : [];
                    for (var i = 0; i < choices.length; i++) {
                        if (choices[i].value == root.field.value) {
                            return i;
                        }
                    }
                    return -1;
                }
                delegate: MenuItem {
                    width: ListView.view ? ListView.view.width : fieldCombo.width
                    text: qsTr(comboBoxRow.choiceText(modelData))
                    highlighted: fieldCombo.highlightedIndex === index
                    hoverEnabled: fieldCombo.hoverEnabled
                    ToolTip.visible: hovered && !!modelData.desc
                    ToolTip.text: qsTr(modelData.desc || "")
                    ToolTip.delay: 500
                }
                onActivated: index => root.emitValue(parent.choiceValue(parent.choiceAt(index)))
            }
            Loader {
                sourceComponent: helpButtonItem
            }
        }
    }

    Component {
        id: colorPickerItem
        RowLayout {
            Label {
                text: qsTr((root.field && root.field.title) || "") + "："
                Layout.alignment: Qt.AlignVCenter
                font.pixelSize: 12
                fontSizeMode: Text.Fit
                wrapMode: Text.Wrap
                Layout.preferredWidth: 150
            }
            TextField {
                id: colorField
                Layout.fillWidth: true
                text: root.field && root.field.value ? root.field.value : ""
                onEditingFinished: root.emitValue(text)
            }
            IconButton {
                icon_name: "mdi7.eyedropper-variant"
                accessibleName: qsTr("Choose Color")
                onClicked: dialogs.colorDialog.bind_color(colorField.text, color => {
                    colorField.text = color;
                    root.emitValue(color);
                })
            }
            Loader {
                sourceComponent: helpButtonItem
            }
        }
    }
}
