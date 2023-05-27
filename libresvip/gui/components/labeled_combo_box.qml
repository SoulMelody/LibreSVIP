import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Controls.Material.impl

ComboBox {
    property string hint
    property var choices
    id: combo

    height: 40
    model: choices
    textRole: "text"
    valueRole: "value"
    hoverEnabled: true
    displayText: qsTr(currentText)

    delegate: ItemDelegate {
        width: combo.width
        contentItem: Label {
            text: combo.textRole
                ? qsTr(Array.isArray(combo.model) ? modelData[combo.textRole] : model[combo.textRole])
                : qsTr(modelData)
            font: combo.font
            elide: Text.ElideRight
            verticalAlignment: Text.AlignVCenter
            color: index == combo.highlightedIndex ? Material.accentColor : window.Material.foreground
        }
    }

    background: Rectangle {
        color: "transparent"
    }

    contentItem: TextField {
        z: 1
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
        focus: combo.popup.opened

        color: combo.enabled ? combo.Material.foreground : combo.Material.hintTextColor
        selectionColor: combo.Material.accentColor
        selectedTextColor: combo.Material.primaryHighlightedTextColor
        verticalAlignment: Text.AlignVCenter
        placeholderText: hint

        cursorDelegate: CursorDelegate { }

        MouseArea {
            anchors.fill: parent
            onClicked: (mouse) => {
                if (combo.popup.opened){
                    combo.popup.close()
                } else {
                    parent.forceActiveFocus()
                    combo.popup.open()
                }
                mouse.accepted = false
            }
        }
    }

    indicator: Label {
        anchors.right: parent.right
        anchors.rightMargin: 20
        y: parent.height / 2 - 5
        text: py.qta.icon("mdi6.menu-down")
        font.family: materialFontLoader.name
        font.pixelSize: (parent.height - 10) / 2
    }

    popup: Popup {
        y: combo.height - 1
        width: combo.contentItem.width
        implicitHeight: 400
        padding: 1

        contentItem: ListView {
            clip: true
            implicitHeight: contentHeight
            model: combo.popup.visible ? combo.delegateModel : null
            currentIndex: combo.highlightedIndex

            ScrollIndicator.vertical: ScrollIndicator { }
        }

        onAboutToShow: {
            combo.indicator.text = py.qta.icon("mdi6.menu-up")
        }

        onAboutToHide: {
            combo.indicator.text = py.qta.icon("mdi6.menu-down")
        }
    }
}