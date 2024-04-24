import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import LibreSVIP

ColumnLayout {
    required property string mode
    required property string pattern_prefix
    required property string pattern_main
    required property string pattern_suffix
    required property string replacement
    required property int flags
}