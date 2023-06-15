from __future__ import annotations

import pathlib
import sys

import PySide6
from cx_Freeze import Executable, setup

sys.path.append(str(pathlib.Path("../../").absolute().resolve()))

from libresvip.core.constants import pkg_dir
from libresvip.utils import download_and_setup_ffmpeg

download_and_setup_ffmpeg()

try:
    from cx_Freeze.hooks import get_qt_plugins_paths
except ImportError:
    get_qt_plugins_paths = None

pyside6_dir = pathlib.Path(PySide6.__file__).parent
include_files = [(pkg_dir / "plugins", pathlib.Path("./lib/libresvip/plugins"))]
qml_dirs = ["Qt", "QtCore", "QtQml", "QtQuick"]
qml_base_dir = None
if (pyside6_dir / "qml").exists():
    qml_base_dir = "qml"
elif (pyside6_dir / "Qt/qml").exists():
    qml_base_dir = "Qt/qml"

if qml_base_dir:
    for qml_dir in qml_dirs:
        include_files.append(
            (
                pyside6_dir / qml_base_dir / qml_dir,
                pathlib.Path(f"./lib/PySide6/{qml_base_dir}/{qml_dir}"),
            )
        )

if get_qt_plugins_paths:
    # Inclusion of extra plugins (since cx_Freeze 6.8b2)
    # cx_Freeze imports automatically the following plugins depending of the
    # use of some modules:
    # imageformats, platforms, platformthemes, styles - QtGui
    # mediaservice - QtMultimedia
    # printsupport - QtPrintSupport
    for plugin_name in (
        "xcbglintegrations",
        "egldeviceintegrations",
        "wayland-decoration-client",
        "wayland-graphics-integration-client",
        "wayland-shell-integration",
    ):
        include_files += get_qt_plugins_paths("PySide6", plugin_name)

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None


def platform_libs_for_qtmodule(module: str) -> list[str]:
    return [
        f"libQt6{module}.so.6",  # Linux
        f"Qt{module}",  # MacOS
        f"Qt6{module}.dll",  # Windows
    ]


build_exe_options = {
    "bin_excludes": sum(
        (
            platform_libs_for_qtmodule(module)
            for module in (
                "Charts",
                "ChartsQml",
                "Concurrent",
                "DataVisualization",
                "DataVisualizationQml",
                "Location",
                "Multimedia",
                "MultimediaQuick",
                "Pdf",
                "Positioning",
                "PositioningQuick",
                "Quick3D",
                "RemoteObjects",
                "RemoteObjectsQml",
                "Scxml",
                "ScxmlQml",
                "Sensors",
                "SensorsQuick",
                "ShaderTools",
                "Sql",
                "StateMachine",
                "StateMachineQml",
                "Svg",
                "Test",
                "TextToSpeech",
                "VirtualKeyboard",
                "WebChannel",
                "WebEngineCore",
                "WebEngineQuick",
                "WebEngineQuickDelegatesQml",
                "WebSockets",
                "3DAnimation",
                "3DCore",
                "3DExtras",
                "3DInput",
                "3DLogic",
                "3DQuick",
                "3DQuickAnimation",
                "3DQuickExtras",
                "3DQuickInput",
                "3DQuickRender",
                "3DQuickScene2D",
                "3DRender",
            )
        ),
        [],
    ),
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
    "packages": ["qmlease", "libresvip", "PySide6.QtQuick", "PySide6.QtOpenGLWidgets", "xsdata_pydantic"],
}

executables = [
    Executable(
        "../../libresvip/cli/__main__.py",
        base=None,
        target_name="libresvip",
    ),
    Executable(
        "../../libresvip/gui/__main__.py",
        base=base,
        icon="../../libresvip/res/libresvip.ico",
        target_name="libresvip-gui",
    ),
]

setup(
    name="LibreSVIP",
    version="0.1",
    options={"build_exe": build_exe_options},
    executables=executables,
)
