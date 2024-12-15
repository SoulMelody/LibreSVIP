export LIBRESVIP_VERSION=`python -c 'import libresvip;print(libresvip.__version__)'`
flet build apk \
    --android-permissions android.permission.READ_EXTERNAL_STORAGE=True android.permission.WRITE_EXTERNAL_STORAGE=True android.permission.MANAGE_EXTERNAL_STORAGE=True \
    --arch arm64-v8a \
    --include-packages flet_permission_handler \
    --org org.soulmelody.libresvip \
    --project LibreSVIP \
    --build-version $LIBRESVIP_VERSION \
    --skip-flutter-doctor