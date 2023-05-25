import pathlib

import platformdirs

PACKAGE_NAME = "libresvip"
FRAMEWORK_VERSION = "0.1.0"

TICKS_IN_BEAT = 480
DEFAULT_BPM = 120.0
DEFAULT_PHONEME = "la"
DEFAULT_LYRIC = "啦"

app_dir = platformdirs.AppDirs(PACKAGE_NAME)

module = __import__(PACKAGE_NAME)
pkg_dir = pathlib.Path(module.__file__).parent
res_dir = pkg_dir / "res"
