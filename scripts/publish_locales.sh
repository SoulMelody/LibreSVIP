mkdir -p ../libresvip/res/locales/zh_CN/LC_MESSAGES
msgcat --use-first -o ../libresvip/res/locales/zh_CN/LC_MESSAGES/libresvip.po ../libresvip/res/i18n/*-zh_CN.po
msgfmt -c -v -o ../libresvip/res/locales/zh_CN/LC_MESSAGES/libresvip.mo ../libresvip/res/locales/zh_CN/LC_MESSAGES/libresvip.po