#!/bin/bash
mkdir -p ../libresvip/res/locales/zh_CN/LC_MESSAGES
msgcat --use-first -o ../libresvip/res/locales/zh_CN/LC_MESSAGES/libresvip.po ../translations/*-zh_CN.po ../libresvip/plugins/*/*-zh_CN.po
msgfmt -c -v -o ../libresvip/res/locales/zh_CN/LC_MESSAGES/libresvip.mo ../libresvip/res/locales/zh_CN/LC_MESSAGES/libresvip.po