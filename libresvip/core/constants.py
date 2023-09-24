import importlib.resources

import platformdirs

PACKAGE_NAME = "libresvip"

KEY_IN_OCTAVE = 12
TICKS_IN_BEAT = 480
DEFAULT_BPM = 120.0
DEFAULT_PHONEME = DEFAULT_ENGLISH_LYRIC = "la"
DEFAULT_CHINESE_LYRIC = "啦"
DEFAULT_JAPANESE_LYRIC = "ラ"
DEFAULT_KOREAN_LYRIC = "라"

app_dir = platformdirs.AppDirs(PACKAGE_NAME)

with importlib.resources.path(PACKAGE_NAME, ".") as _pkg_dir:
    pkg_dir = _pkg_dir
    res_dir = pkg_dir / "res"
