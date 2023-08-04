#!/bin/bash
if [ -z $LIBRESVIP_LOCALE ]; then
    export LIBRESVIP_LOCALE=zh_CN
fi
mkdir -p ../libresvip/res/locales/"$LIBRESVIP_LOCALE"/LC_MESSAGES
msgcat --use-first -o ../translations/libresvip-"$LIBRESVIP_LOCALE".po ../translations/*-"$LIBRESVIP_LOCALE".po ../libresvip/plugins/*/*-"$LIBRESVIP_LOCALE".po
msgfmt -c -v -o ../libresvip/res/locales/"$LIBRESVIP_LOCALE"/LC_MESSAGES/libresvip.mo ../translations/libresvip-"$LIBRESVIP_LOCALE".po