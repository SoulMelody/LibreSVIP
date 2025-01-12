from __future__ import annotations

import contextlib
import itertools
import os
import pathlib
import sys

import nicegui
import shellingham
from cx_Freeze import Executable, setup

sys.path.append(str(pathlib.Path("../").absolute().resolve()))

from bdist_portable import BdistPortable

import libresvip

with contextlib.suppress(Exception):
    if (
        ("conda" in sys.version or "Continuum" in sys.version)
        and shellingham.detect_shell()[0] == "bash"
        and os.name == "nt"
    ):
        os.environ["PATH"] += f"{os.pathsep}{sys.base_prefix}/Library/bin"

base = "Win32GUI" if sys.platform == "win32" else None
nicegui_assets_dir = pathlib.Path(nicegui.__path__[0]) / "elements" / "lib"
zip_includes: list[tuple[str, str]] = [
    ("../libresvip/res", "libresvip/res"),
]
zip_includes.extend(
    (
        str(resource_file),
        str(resource_file.as_posix())[3:],
    )
    for resource_file in pathlib.Path("../res").rglob("**/*.*")
    if resource_file.is_file() and resource_file.suffix not in [".po", ".qml"]
)
zip_includes.extend(
    (
        str(plugin_info),
        str(plugin_info.as_posix())[3:],
    )
    for plugin_info in itertools.chain(
        pathlib.Path("../libresvip/middlewares").rglob("**/*.*"),
        pathlib.Path("../libresvip/plugins").rglob("**/*.*"),
    )
    if plugin_info.is_file() and plugin_info.suffix not in [".py", ".pyc"]
)


build_exe_options = {
    "bin_excludes": [
        asset_path.name
        for lib_name in [
            "aggrid",
            "echarts",
            "echarts-gl",
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
        "libresvip.gui",
        "libresvip.tui",
        "matplotlib",
        "numpy",
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
        "wx",
        "PySide6",
        "qtpy",
        "qtawesome",
        "desktop_notifier",
        "zmq",
    ],
    "include_files": [],
    "zip_includes": zip_includes,
    "zip_include_packages": [
        "libresvip.cli",
        "libresvip.core",
        "libresvip.middlewares",
        "libresvip.model",
        "libresvip.plugins",
        "libresvip.web",
    ],
    "packages": [
        "anyio",
        "construct_typed",
        "drawsvg",
        "google.protobuf",
        "jinja2",
        "libresvip.cli",
        "libresvip.core",
        "libresvip.middlewares",
        "libresvip.model",
        "libresvip.plugins",
        "libresvip.web",
        "mido_fix",
        "parsimonious",
        "proto",
        "pymediainfo",
        "pysubs2",
        "pyzipper",
        "webview",
        "xsdata_pydantic",
        "email._header_value_parser",
        "nicegui.functions.clipboard",
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
