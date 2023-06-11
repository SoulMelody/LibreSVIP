#!/bin/bash

export PYTHONIOENCODING=utf-8

pyside6-lupdate -I ../libresvip/gui/components/*.qml -ts ../translations/libresvip_gui-zh_CN.ts
# pyside6-linguist ../translations/libresvip_gui-zh_CN.ts
# pyside6-lrelease -verbose ../translations/libresvip-zh_CN.ts -qm ../translations/libresvip-zh_CN.qm
ts2po --duplicates=merge -P ../translations/libresvip_gui-zh_CN.ts > ../translations/libresvip_gui.pot
if [ ! -f ../translations/libresvip_gui-zh_CN.po ]; then
    # msgconv -i ../translations/libresvip_gui.pot -o ../translations/libresvip_gui-zh_CN.po -t utf-8
    pot2po -i ../translations/libresvip_gui.pot -o ../translations/libresvip_gui-zh_CN.po
else
    msgmerge -U ../translations/libresvip_gui-zh_CN.po ../translations/libresvip_gui.pot
fi
