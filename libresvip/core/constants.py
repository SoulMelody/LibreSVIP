import contextlib
import importlib.resources
import pathlib
import sys
from typing import Final

import platformdirs

PACKAGE_NAME: Final[str] = "libresvip"

KEY_IN_OCTAVE: Final[int] = 12
TICKS_IN_BEAT: Final[int] = 480
DEFAULT_BPM: Final[float] = 120.0
DEFAULT_PHONEME: Final[str] = "la"
DEFAULT_ENGLISH_LYRIC: Final[str] = DEFAULT_PHONEME
DEFAULT_SPANISH_LYRIC: Final[str] = DEFAULT_ENGLISH_LYRIC
DEFAULT_CHINESE_LYRIC: Final[str] = "啦"
DEFAULT_JAPANESE_LYRIC: Final[str] = "ラ"
DEFAULT_KOREAN_LYRIC: Final[str] = "라"

app_dir = platformdirs.AppDirs(PACKAGE_NAME)


if sys.version_info < (3, 10):

    @contextlib.contextmanager
    def resource_path(package: str, rel_path: str) -> pathlib.Path:
        from importlib_resources._adapters import wrap_spec
        from importlib_resources._common import from_package, resolve

        def get_package(package):
            # type: (Package) -> types.ModuleType
            """Take a package name or module object and return the module.

            Raise an exception if the resolved module is not a package.
            """
            resolved = resolve(package)
            if wrap_spec(resolved).submodule_search_locations is None:
                msg = f"{package!r} is not a package"
                raise TypeError(msg)
            return resolved

        yield from_package(get_package(package)) / rel_path

else:
    resource_path = importlib.resources.path

with resource_path(PACKAGE_NAME, ".") as _pkg_dir:
    pkg_dir = _pkg_dir
    res_dir = pkg_dir / "res"
