export PYTHONIOENCODING=utf-8
pybabel extract ../libresvip -o ../libresvip/res/i18n/libresvip_python.pot
pot2po -i ../libresvip/res/i18n/libresvip_python.pot -o ../libresvip/res/i18n/libresvip_python-zh_CN.po