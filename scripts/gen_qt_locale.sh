export PATH="$PATH:$(python -c 'import PySide6;print(PySide6.__path__[0])')"
export PYTHONIOENCODING=utf-8

lupdate -I ../libresvip/gui/components/*.qml -ts ../libresvip/res/i18n/libresvip_gui-zh_CN.ts
# linguist ../libresvip/res/i18n/libresvip-zh_CN.ts
# lrelease -verbose ../libresvip/res/i18n/libresvip-zh_CN.ts -qm ../libresvip/res/i18n/libresvip-zh_CN.qm
ts2po --duplicates=merge ../libresvip/res/i18n/libresvip_gui-zh_CN.ts > ../libresvip/res/i18n/libresvip_gui-zh_CN.po