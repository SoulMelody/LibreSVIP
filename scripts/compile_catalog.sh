#!/bin/bash
dir="../libresvip/res/locales/"
ls $dir | while read line
do
    locale_dir=$dir$line
    mkdir -p $locale_dir/LC_MESSAGES
    msgfmt -c -v -o $locale_dir/LC_MESSAGES/libresvip.mo $locale_dir/LC_MESSAGES/libresvip.po
done
