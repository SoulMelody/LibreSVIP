#!/bin/bash

export PYTHONIOENCODING=utf-8

pyside6-lupdate -I ../libresvip/gui/components/*.qml -ts ../libresvip/res/i18n/libresvip_gui-zh_CN.ts
# pyside6-linguist ../libresvip/res/i18n/libresvip_gui-zh_CN.ts
# pyside6-lrelease -verbose ../libresvip/res/i18n/libresvip-zh_CN.ts -qm ../libresvip/res/i18n/libresvip-zh_CN.qm
ts2po --duplicates=merge -P ../libresvip/res/i18n/libresvip_gui-zh_CN.ts > ../libresvip/res/i18n/libresvip_gui.pot
if [ ! -f ../libresvip/res/i18n/libresvip_gui-zh_CN.po ]; then
    # msgconv -i ../libresvip/res/i18n/libresvip_gui.pot -o ../libresvip/res/i18n/libresvip_gui-zh_CN.po -t utf-8
    pot2po -i ../libresvip/res/i18n/libresvip_gui.pot -o ../libresvip/res/i18n/libresvip_gui-zh_CN.po
else
    msgmerge -U ../libresvip/res/i18n/libresvip_gui-zh_CN.po ../libresvip/res/i18n/libresvip_gui.pot
fi
