#!/bin/bash

export PYTHONIOENCODING=utf-8
pybabel extract ../libresvip/cli ../libresvip/core ../libresvip/extension ../libresvip/gui ../libresvip/model ../libresvip/web  -o ../translations/libresvip_python.pot
if [ ! -f ../translations/libresvip_python-zh_CN.po ]; then
    pybabel init -i ../translations/libresvip_python.pot -d ../translations -l zh_CN
else
    msgmerge -U ../translations/libresvip_python-zh_CN.po ../translations/libresvip_python.pot
fi