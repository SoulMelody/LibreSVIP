import QtQuick
import QtQuick.Controls.Material
import QtQuick.Shapes

// adapted from https://github.com/arenasys/sd-tagging-helper/blob/master/qml/DashedRectangle.qml
Shape {
    id: shape
    property var radius: 0
    property var strokeWidth: 4
    property var dashLength: 3
    property var dashOffset: 0

    ShapePath {
        strokeColor: Material.primary
        strokeWidth: shape.strokeWidth
        fillColor: 'transparent'
        strokeStyle: ShapePath.DashLine
        dashPattern: [dashLength, dashLength]
        dashOffset: shape.dashOffset

        startX: radius
        startY: 0
        PathLine {
            x: shape.width
            y: 0
        }
        PathLine {
            x: shape.width
            y: shape.height
        }
        PathLine {
            x: 0
            y: shape.height
        }
        PathLine {
            x: 0
            y: 0
        }
    }
}
