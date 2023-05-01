from __future__ import annotations

import pathlib
import sys

import PySide6
from cx_Freeze import Executable, setup

from libresvip.core.constants import pkg_dir

try:
    from cx_Freeze.hooks import get_qt_plugins_paths
except ImportError:
    get_qt_plugins_paths = None

pyside6_dir = pathlib.Path(PySide6.__file__).parent
include_files = [(pkg_dir / "plugins", pathlib.Path("./lib/libresvip/plugins"))]
if (pyside6_dir / "qml").exists():
    include_files.append((pyside6_dir / "qml", pathlib.Path("./lib/PySide6/qml")))
elif (pyside6_dir / "Qt/qml").exists():
    include_files.append((pyside6_dir / "Qt/qml", pathlib.Path("./lib/PySide6/Qt/qml")))
if get_qt_plugins_paths:
    # Inclusion of extra plugins (since cx_Freeze 6.8b2)
    # cx_Freeze imports automatically the following plugins depending of the
    # use of some modules:
    # imageformats, platforms, platformthemes, styles - QtGui
    # mediaservice - QtMultimedia
    # printsupport - QtPrintSupport
    for plugin_name in (
        # "accessible",
        # "iconengines",
        # "platforminputcontexts",
        "xcbglintegrations",
        "egldeviceintegrations",
        "wayland-decoration-client",
        "wayland-graphics-integration-client",
        # "wayland-graphics-integration-server",
        "wayland-shell-integration",
    ):
        include_files += get_qt_plugins_paths("PySide6", plugin_name)

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

build_exe_options = {
    "bin_excludes": [
        "QtWebEngineCore",
        "Qt6WebEngineCore.dll",
        "libQt6WebEngineCore.so",
        "Python.Runtime.dll",
    ],
    # exclude packages that are not really needed
    "excludes": [
        "tkinter",
        "unittest",
        "pydoc",
        "pydoc_data",
        "pep517",
        "black",
        "jedi",
        "numpy",
        "IPython",
        "Cython",
        "sqlite3",
        "test",
        "PIL",
        "trame",
        "trame_client",
        "trame_router",
        "trame_server",
        "wslink",
        "webview",
        "aiohttp",
        "pythonnet",
    ],
    "include_files": include_files,
    "zip_include_packages": ["PySide6"],
    "packages": ["qmlease", "libresvip", "PySide6.QtQuick"],
}

executables = [
    Executable(
        "../../libresvip/gui/__main__.py",
        base=base,
        target_name="libresvip-gui",
    ),
]

setup(
    name="LibreSVIP",
    version="0.1",
    options={"build_exe": build_exe_options},
    executables=executables,
)
