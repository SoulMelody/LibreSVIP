from typing import Final

import platformdirs

from libresvip.core.compat import package_path

PACKAGE_NAME: Final[str] = "libresvip"

# lyric related constants
DEFAULT_PHONEME: Final[str] = "la"
DEFAULT_ENGLISH_LYRIC: Final[str] = DEFAULT_PHONEME
DEFAULT_SPANISH_LYRIC: Final[str] = DEFAULT_ENGLISH_LYRIC
DEFAULT_CHINESE_LYRIC: Final[str] = "啦"
DEFAULT_JAPANESE_LYRIC: Final[str] = "ラ"
DEFAULT_KOREAN_LYRIC: Final[str] = "라"

# midi related constants
DEFAULT_BPM: Final[float] = 120.0
KEY_IN_OCTAVE: Final[int] = 12
TICKS_IN_BEAT: Final[int] = 480
MIN_BREAK_LENGTH_BETWEEN_PITCH_SECTIONS: Final[int] = TICKS_IN_BEAT
DEFAULT_PITCH_BEND_SENSITIVITY: Final[int] = 2
MAX_PITCH_BEND_SENSITIVITY: Final[int] = 24
PITCH_MAX_VALUE: Final[int] = 8191

app_dir = platformdirs.AppDirs(PACKAGE_NAME)

pkg_dir = package_path(PACKAGE_NAME)
res_dir = pkg_dir / "res"
