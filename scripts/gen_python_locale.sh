#!/bin/bash

export PYTHONIOENCODING=utf-8

if [ -z $LIBRESVIP_LOCALE ]; then
    export LIBRESVIP_LOCALE=zh_CN
fi
pybabel extract ../libresvip/cli ../libresvip/core ../libresvip/extension ../libresvip/gui ../libresvip/model ../libresvip/web  -o ../translations/libresvip_python.pot
if [ ! -f ../translations/libresvip_python-"$LIBRESVIP_LOCALE".po ]; then
    pybabel init -i ../translations/libresvip_python.pot -d ../translations -l $LIBRESVIP_LOCALE
else
    pybabel update -l $LIBRESVIP_LOCALE --ignore-obsolete --init-missing -N -i ../translations/libresvip_python.pot -o ../translations/libresvip_python-zh_CN.po
fi