#!/bin/bash

export PYTHONIOENCODING=utf-8

if [ -z $LIBRESVIP_LOCALE ]; then
    export LIBRESVIP_LOCALE=zh_CN
fi
pyside6-lupdate -I ../libresvip/res/qml/components/*.qml ../libresvip/gui/modules/*.py -no-obsolete -ts ../translations/libresvip_gui-"$LIBRESVIP_LOCALE".ts
# pyside6-linguist ../translations/libresvip_gui-"$LIBRESVIP_LOCALE".ts
# pyside6-lrelease -verbose ../translations/libresvip-"$LIBRESVIP_LOCALE".ts -qm ../translations/libresvip-"$LIBRESVIP_LOCALE".qm
ts2po --duplicates=merge -P ../translations/libresvip_gui-"$LIBRESVIP_LOCALE".ts > ../translations/libresvip_gui.pot
if [ ! -f ../translations/libresvip_gui-"$LIBRESVIP_LOCALE".po ]; then
    # msgconv -i ../translations/libresvip_gui.pot -o ../translations/libresvip_gui-"$LIBRESVIP_LOCALE".po -t utf-8
    pot2po -i ../translations/libresvip_gui.pot -o ../translations/libresvip_gui-"$LIBRESVIP_LOCALE".po
else
    msgmerge -U -N --no-location ../translations/libresvip_gui-"$LIBRESVIP_LOCALE".po ../translations/libresvip_gui.pot
fi
