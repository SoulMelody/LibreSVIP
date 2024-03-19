#!/bin/bash

pyside6-lupdate -I ../libresvip/res/qml/components/*.qml -no-obsolete -ts ../translations/libresvip_gui.ts
ts2po --duplicates=merge -P ../translations/libresvip_gui.ts > ../translations/libresvip_gui.pot
ts2po --duplicates=merge -P ../translations/qt_standard_buttons.ts > ../translations/qt_standard_buttons.pot
