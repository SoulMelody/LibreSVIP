export LIBRESVIP_VERSION=`python -c 'import libresvip;print(libresvip.__version__)'`
export FLET_VERSION=`python -c 'import flet;print(flet.version.version)'`
flet build apk \
    --android-permissions android.permission.READ_EXTERNAL_STORAGE=True android.permission.WRITE_EXTERNAL_STORAGE=True android.permission.MANAGE_EXTERNAL_STORAGE=True \
    --arch arm64-v8a \
    --include-packages flet_permission_handler \
    --org org.soulmelody \
    --project LibreSVIP \
    --build-version $LIBRESVIP_VERSION \
    --template gh:SoulMelody/flet-build-template \
    --template-ref $FLET_VERSION \
    --module-name ../libresvip/mobile/__main__.py