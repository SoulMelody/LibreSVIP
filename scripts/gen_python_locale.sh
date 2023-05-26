export PYTHONIOENCODING=utf-8
pybabel extract ../libresvip -o ../libresvip/res/i18n/libresvip_python.pot
if [ ! -f ../libresvip/res/i18n/libresvip_python-zh_CN.po ]; then
    pybabel init -i ../libresvip/res/i18n/libresvip_python.pot -d ../libresvip/res/i18n -l zh_CN
else
    msgmerge -U ../libresvip/res/i18n/libresvip_python-zh_CN.po ../libresvip/res/i18n/libresvip_python.pot
fi