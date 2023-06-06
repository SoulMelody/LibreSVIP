#!/bin/bash

export PYTHONIOENCODING=utf-8

pyside6-lupdate -I ../libresvip/gui/components/*.qml -ts ../libresvip/res/i18n/libresvip_gui-zh_CN.ts
# pyside6-linguist ../libresvip/res/i18n/libresvip-zh_CN.ts
# pyside6-lrelease -verbose ../libresvip/res/i18n/libresvip-zh_CN.ts -qm ../libresvip/res/i18n/libresvip-zh_CN.qm
ts2po --duplicates=merge ../libresvip/res/i18n/libresvip_gui-zh_CN.ts > ../libresvip/res/i18n/libresvip_gui-zh_CN.po