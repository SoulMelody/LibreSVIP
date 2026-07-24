pragma Singleton

import QtQml
import QtQuick

QtObject {
    property bool darkMode: false

    property color colorBorderLight: "#E0E0E0"
    property color colorBorderDark: "#424242"
    property color colorBorder: darkMode ? colorBorderDark : colorBorderLight
    property color colorMutedTextLight: "#757575"
    property color colorMutedTextDark: "#BDBDBD"
    property color colorMutedText: darkMode ? colorMutedTextDark : colorMutedTextLight

    property color colorSuccess: "#4CAF50"
    property color colorSuccessLight: "#81C784"
    property color colorSuccessDark: "#2E7D32"
    property color colorWarning: "#FF9800"
    property color colorWarningLight: "#FFB74D"
    property color colorWarningDark: "#E65100"
    property color colorError: "#F44336"
    property color colorErrorLight: "#E57373"
    property color colorErrorDark: "#C62828"
    property color colorInfo: "#2196F3"
    property color colorInfoLight: "#64B5F6"
    property color colorInfoDark: "#1565C0"
    property color colorFocusBorderLight: "#FF3F51B5"
    property color colorFocusBorderDark: "#FFFFD54F"
    property color colorFocusBorder: darkMode ? colorFocusBorderDark : colorFocusBorderLight

    property int spacingXS: 8
    property int spacingS: 12
    property int spacingM: 16
    property int spacingL: 24
    property int minClickSize: 32
}
