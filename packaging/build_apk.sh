export LIBRESVIP_VERSION=`uv run python -c 'import libresvip;print(libresvip.__version__)'`
export FLET_VERSION=`uv run python -c 'import flet;print(flet.version.version)'`
cp  ../libresvip/mobile/__main__.py main.py
uv run flet build apk \
    --android-permissions android.permission.READ_EXTERNAL_STORAGE=True android.permission.WRITE_EXTERNAL_STORAGE=True android.permission.MANAGE_EXTERNAL_STORAGE=True \
    --include-packages flet_permission_handler \
    --org org.soulmelody \
    --project LibreSVIP \
    --build-version $LIBRESVIP_VERSION \
    --template gh:SoulMelody/flet-build-template \
    --template-ref $FLET_VERSION