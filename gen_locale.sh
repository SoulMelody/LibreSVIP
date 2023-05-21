export PATH="$PATH:$(python -c 'import PySide6;print(PySide6.__path__[0])')"
# linguist libresvip/gui/i18n/libresvip_zh-CN.ts
lupdate -I libresvip/gui/components/*.qml -ts libresvip/gui/i18n/libresvip_zh-CN.ts
# lrelease -verbose libresvip/gui/i18n/libresvip.ts -qm libresvip/gui/i18n/libresvip_zh-CN.qm