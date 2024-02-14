#!/bin/bash
if [ -z $LIBRESVIP_LOCALE ]; then
    export LIBRESVIP_LOCALE=zh_CN
fi
mkdir -p ../libresvip/res/locales/"$LIBRESVIP_LOCALE"/LC_MESSAGES
msgcat --use-first -o ../libresvip/res/locales/"$LIBRESVIP_LOCALE"/LC_MESSAGES/libresvip.po ../translations/libresvip_*-"$LIBRESVIP_LOCALE".po ../libresvip/plugins/*/*-"$LIBRESVIP_LOCALE".po
msgfilter -i ../libresvip/res/locales/"$LIBRESVIP_LOCALE"/LC_MESSAGES/libresvip.po -o ../translations/libresvip.po true
msguniq ../translations/libresvip.po -o ../translations/libresvip.po