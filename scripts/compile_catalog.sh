#!/bin/bash
if [ -z $LIBRESVIP_LOCALE ]; then
    export LIBRESVIP_LOCALE=zh_CN
fi
msgfmt -c -v -o ../libresvip/res/locales/"$LIBRESVIP_LOCALE"/LC_MESSAGES/libresvip.mo ../libresvip/res/locales/"$LIBRESVIP_LOCALE"/LC_MESSAGES/libresvip.po
