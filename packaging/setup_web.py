from __future__ import annotations

import contextlib
import os
import pathlib
import sys

import nicegui
import shellingham
from cx_Freeze import Executable, setup

sys.path.append(str(pathlib.Path("../").absolute().resolve()))

from bdist_portable import BdistPortable  # noqa: E402

import libresvip  # noqa: E402
from libresvip.core.constants import pkg_dir  # noqa: E402

with contextlib.suppress(Exception):
    if (
        ("conda" in sys.version or "Continuum" in sys.version)
        and shellingham.detect_shell()[0] == "bash"
        and os.name == "nt"
    ):
        os.environ["PATH"] += f"{os.pathsep}{sys.base_prefix}/Library/bin"

include_files = [(pkg_dir / "plugins", pathlib.Path("./lib/libresvip/plugins"))]

base = "Win32GUI" if sys.platform == "win32" else None
nicegui_assets_dir = pathlib.Path(nicegui.__path__[0]) / "elements" / "lib"


build_exe_options = {
    "bin_excludes": [
        asset_path.name
        for lib_name in [
            "aggrid",
            "echarts",
            "mermaid",
            "plotly",
            "three",
            "vanilla-jsoneditor",
        ]
        for asset_path in (nicegui_assets_dir / lib_name).rglob("*")
        if asset_path.is_file()
    ],
    # exclude packages that are not really needed
    "excludes": [
        "aiohttp",
        "attr",
        "black",
        "debugpy",
        "jedi",
        "numpy",
        "matplotlib",
        "IPython",
        "Cython",
        "sqlite3",
        "test",
        "pandas",
        "pep517",
        "PIL",
        "plotly",
        "pydoc",
        "pydoc_data",
        "setuptools",
        "tkinter",
        "wslink",
        "wx",
        "PySide6",
        "qtpy",
        "qtawesome",
        "desktop_notifier",
        "zmq",
    ],
    "include_files": include_files,
    "zip_include_packages": [],
    "packages": [
        "anyio",
        "construct_typed",
        "drawsvg",
        "google.protobuf",
        "jinja2",
        "libresvip",
        "mido_fix",
        "parsimonious",
        "proto",
        "pymediainfo",
        "srt",
        "webview",
        "xsdata",
        "email._header_value_parser",
        "uvicorn.lifespan.on",
        "uvicorn.loops.auto",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets.auto",
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
        "../libresvip/web/__main__.py",
        base=base,
        icon="../libresvip/res/libresvip.ico",
        target_name="libresvip-web",
    ),
]

setup(
    name="LibreSVIP",
    version=libresvip.__version__,
    options={"build_exe": build_exe_options, "bdist_dmg": bdist_dmg_options},
    executables=executables,
    cmdclass={
        "bdist_portable": BdistPortable,
    },
)
