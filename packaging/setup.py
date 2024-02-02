from __future__ import annotations

import contextlib
import os
import pathlib
import sys

import PySide6
import shellingham
import shiboken6
from cx_Freeze import Executable, setup

sys.path.append(str(pathlib.Path("../").absolute().resolve()))

from bdist_portable import BdistPortable  # noqa: E402

import libresvip  # noqa: E402
from libresvip.core.constants import pkg_dir  # noqa: E402

bin_includes = []
bin_path_includes = [shiboken6.__path__[0]]
with contextlib.suppress(Exception):
    if (
        ("conda" in sys.version or "Continuum" in sys.version)
        and shellingham.detect_shell()[0] == "bash"
        and os.name == "nt"
    ):
        bin_path_includes.append(f"{sys.base_prefix}/Library/bin")

try:
    from cx_Freeze.hooks import get_qt_plugins_paths
except ImportError:
    get_qt_plugins_paths = None

pyside6_dir = pathlib.Path(PySide6.__path__[0])
include_files = [(pkg_dir / "plugins", pathlib.Path("./lib/libresvip/plugins"))]
qml_dirs = ["Qt", "QtCore", "QtQml", "QtQuick"]
qml_base_dir = None
if (pyside6_dir / "qml").exists():
    qml_base_dir = "qml"
elif (pyside6_dir / "Qt/qml").exists():
    qml_base_dir = "Qt/qml"
    xcb_soname = "Qt/lib/libQt6XcbQpa.so.6"
    if (pyside6_dir / xcb_soname).exists():
        bin_includes.append(pyside6_dir / xcb_soname)

if qml_base_dir:
    include_files.extend(
        (
            pyside6_dir / qml_base_dir / qml_dir,
            pathlib.Path(f"./lib/PySide6/{qml_base_dir}/{qml_dir}"),
        )
        for qml_dir in qml_dirs
    )
    if qml_lib := next(pyside6_dir.glob("*pyside6qml*"), None):
        bin_includes.append(qml_lib)

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
                "PdfQuick",
                "Positioning",
                "PositioningQuick",
                "Quick3D",
                "Quick3DUtils",
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
    "bin_includes": bin_includes,
    "bin_path_includes": bin_path_includes,
    # exclude packages that are not really needed
    "excludes": [
        "attr",
        "black",
        "cryptography",
        "jedi",
        "nicegui",
        "numpy",
        "matplotlib",
        "IPython",
        "Cython",
        "sqlite3",
        "test",
        "pep517",
        "PIL",
        "pydoc",
        "pydoc_data",
        "pythonnet",
        "setuptools",
        "startlette",
        "tkinter",
        "uvicorn",
        "webview",
        "wx",
    ],
    "include_files": include_files,
    "zip_include_packages": ["PySide6"],
    "packages": [
        "anyio",
        "bidict",
        "construct_typed",
        "drawsvg",
        "google.protobuf",
        "jinja2",
        "libresvip",
        "mido_fix",
        "parsimonious",
        "proto",
        "pymediainfo",
        "PySide6.QtQuick",
        "PySide6.QtOpenGL",
        "srt",
        "xsdata",
        "fsspec.implementations.memory",
        "upath.implementations.memory",
        "zstandard",
    ],
}

bdist_dmg_options = {
    "volume_label": "LibreSVIP",
    "applications_shortcut": True,
}

executables = [
    Executable(
        "../libresvip/cli/__main__.py",
        base=None,
        target_name="libresvip",
    ),
    Executable(
        "../libresvip/gui/__main__.py",
        base=base,
        icon="../libresvip/res/libresvip.ico",
        target_name="libresvip-gui",
    ),
]

setup(
    name="LibreSVIP",
    version=libresvip.__version__,
    options={
        "build_exe": build_exe_options,
        "bdist_dmg": bdist_dmg_options,
    },
    executables=executables,
    cmdclass={
        "bdist_portable": BdistPortable,
    },
)
