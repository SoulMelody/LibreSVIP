from __future__ import annotations

import sys

from cx_Freeze import Executable, setup

include_files = []

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

build_exe_options = {
    "bin_excludes": [],
    # exclude packages that are not really needed
    "excludes": [
        "tkinter",
        "unittest",
        "pydoc",
        "pydoc_data",
        "black",
        "jedi",
        "numpy",
        "ipython",
        "cython",
        "sqlite3",
        "test",
        "pillow",
        "pyside6",
    ],
    "include_files": include_files,
}

executables = [
    Executable(
        "../../libresvip/cli/__main__.py", base=None, target_name="libresvip.cli"
    ),
]

setup(
    name="LibreSVIP",
    version="0.1",
    options={"build_exe": build_exe_options},
    executables=executables,
)
