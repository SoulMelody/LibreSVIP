import pathlib

import platformdirs

PACKAGE_NAME = "libresvip"

TICKS_IN_BEAT = 480
DEFAULT_BPM = 120.0
DEFAULT_PHONEME = DEFAULT_ENGLISH_LYRIC = "la"
DEFAULT_CHINESE_LYRIC = "啦"
DEFAULT_JAPANESE_LYRIC = "ラ"
DEFAULT_KOREAN_LYRIC = "라"

app_dir = platformdirs.AppDirs(PACKAGE_NAME)

module = __import__(PACKAGE_NAME)
pkg_dir = pathlib.Path(module.__file__).parent
res_dir = pkg_dir / "res"
