import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material

ComboBox {
    property string hint
    property var choices
    id: combo

    clip: true
    height: 40
    model: choices
    textRole: "text"
    valueRole: "value"
    hoverEnabled: true
    displayText: qsTr(currentText)

    Label {
        id: hintLabel
        text: hint
        y: 0
        x: 15
        font.pixelSize: 10
    }

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

    background: Canvas {
        anchors.fill: parent
        onPaint: {
            var context = getContext("2d");
            context.clearRect(0, 0, parent.width, parent.height);
            context.beginPath();
            context.moveTo(15, 10);
            context.lineTo(2, 10);
            context.lineTo(2, parent.height - 2);
            context.lineTo(parent.width - 2, parent.height - 2);
            context.lineTo(parent.width - 2, 10);
            context.lineTo(15 + hintLabel.width - 2, 10);
            context.strokeStyle = hintLabel.color;
            context.lineWidth = combo.hovered ? 2 : 1;
            context.stroke();
        }
    }

    indicator: Label {
        anchors.right: parent.right
        anchors.rightMargin: 10
        y: parent.height / 2 - 5
        text: py.qta.icon("mdi6.menu-down")
        font.family: materialFontLoader.name
        font.pixelSize: (parent.height - 10) / 2
    }

    popup: Popup {
        y: combo.height - 1
        width: combo.width
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
            hintLabel.color = Material.accentColor
            combo.background.requestPaint()
        }

        onAboutToHide: {
            combo.indicator.text = py.qta.icon("mdi6.menu-down")
            hintLabel.color = window.Material.foreground
            combo.background.requestPaint()
        }
    }

    onHoveredChanged: {
        if (!popup.opened) {
            hintLabel.color = window.Material.foreground
        }
        background.requestPaint()
    }

    Connections {
        target: toolbar
        function onThemeChanged() {
            if (popup.opened) {
                hintLabel.color = Material.accentColor
            } else {
                hintLabel.color = window.Material.foreground
            }
            background.requestPaint()
        }
    }
}