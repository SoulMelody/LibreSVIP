export LIBRESVIP_VERSION=`uv run --locked python -c 'import libresvip;print(libresvip.__version__)'`
export FLET_VERSION=`uv run --locked python -c 'import flet;print(flet.version.version)'`
export FLET_BUILD_COMMAND_PATH=`uv run --locked python -c 'from flet_cli.commands import build_base;print(build_base.__file__)'`
export START_LINE_NUM=`awk "/# requirements/{print NR}" $FLET_BUILD_COMMAND_PATH`
export END_LINE_NUM=`awk "/# site-packages variable/{print NR;exit;}" $FLET_BUILD_COMMAND_PATH`
if [ -n "$START_LINE_NUM" ]; then
    sed -i $START_LINE_NUM','$END_LINE_NUM'd' $FLET_BUILD_COMMAND_PATH
fi
sed -i 's/dev_packages_configured/True/' $FLET_BUILD_COMMAND_PATH
sed -i 's/self.flutter_dependencies = {}/self.flutter_dependencies = {"flet_permission_handler": "any"}/' $FLET_BUILD_COMMAND_PATH
cp  ../libresvip/mobile/__main__.py main.py
uv run flet build apk -v \
    --android-permissions android.permission.READ_EXTERNAL_STORAGE=True android.permission.WRITE_EXTERNAL_STORAGE=True android.permission.MANAGE_EXTERNAL_STORAGE=True \
    --org org.soulmelody \
    --project LibreSVIP \
    --build-version $LIBRESVIP_VERSION \
    --template gh:SoulMelody/flet-build-template \
    --template-ref $FLET_VERSION
