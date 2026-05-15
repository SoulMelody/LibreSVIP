import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Controls.Material.impl

ComboBox {
    id: combo
    property string hint
    property var choices
    property string suffixesRole: "suffixes"
    property string currentSuffixes: ""
    property var currentSuffixValues: []

    height: 40
    model: choices
    textRole: "text"
    valueRole: "value"
    displayText: qsTr(currentText) + (currentSuffixes ? " (" + currentSuffixes + ")" : "")

    onCurrentIndexChanged: updateSuffixes()
    onModelChanged: updateSuffixes()
    Component.onCompleted: updateSuffixes()

    function updateSuffixes() {
        if (model && currentIndex >= 0) {
            var item = typeof model.get === "function" ? model.get(currentIndex) : model[currentIndex];
            currentSuffixes = item && item[suffixesRole] ? item[suffixesRole] : "";
            currentSuffixValues = item && item["suffix_values"] ? item["suffix_values"] : [];
        } else {
            currentSuffixes = "";
            currentSuffixValues = [];
        }
    }

    delegate: MenuItem {
        width: ListView.view.width
        contentItem: Label {
            text: qsTr(model[combo.textRole]) + (model[combo.suffixesRole] ? " (" + model[combo.suffixesRole] + ")" : "")
            color: combo.highlightedIndex === index ? Material.accentColor : window.Material.foreground
        }
        highlighted: combo.highlightedIndex === index
        hoverEnabled: combo.hoverEnabled
    }

    background: Rectangle {
        color: "transparent"
    }

    contentItem: TextField {
        padding: 6
        leftPadding: combo.mirrored ? 0 : 12
        rightPadding: combo.mirrored ? 12 : 0

        text: combo.displayText

        enabled: true
        autoScroll: combo.editable
        readOnly: true
        inputMethodHints: Qt.ImhNone
        validator: combo.validator
        selectByMouse: false

        color: combo.enabled ? combo.Material.foreground : combo.Material.hintTextColor
        selectionColor: combo.Material.accentColor
        selectedTextColor: combo.Material.primaryHighlightedTextColor
        verticalAlignment: Text.AlignVCenter
        placeholderText: hint

        cursorDelegate: CursorDelegate {}

        MouseArea {
            anchors.fill: parent
            onClicked: mouse => {
                if (combo.popup.opened) {
                    combo.popup.close();
                } else {
                    parent.forceActiveFocus();
                    combo.popup.open();
                }
                mouse.accepted = false;
            }
        }
    }

    indicator: Label {
        anchors.right: parent.right
        anchors.rightMargin: 20
        y: parent.height / 2 - 8
        text: iconicFontLoader.icon("mdi7.menu-down")
        font.family: "Material Design Icons"
        font.pixelSize: (parent.height - 16) / 2
    }

    popup: Popup {
        y: combo.height
        width: combo.contentItem.width
        implicitHeight: 400
        padding: 1

        contentItem: ListView {
            clip: true
            implicitHeight: contentHeight
            model: combo.popup.visible ? combo.delegateModel : null
            currentIndex: combo.highlightedIndex

            ScrollIndicator.vertical: ScrollIndicator {}
        }

        onAboutToShow: {
            combo.indicator.text = iconicFontLoader.icon("mdi7.menu-up");
        }

        onAboutToHide: {
            combo.indicator.text = iconicFontLoader.icon("mdi7.menu-down");
        }
    }
}
