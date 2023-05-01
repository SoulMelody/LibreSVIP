from __future__ import annotations

import pathlib

from cx_Freeze import Executable, setup

from libresvip.core.constants import pkg_dir

include_files = [
    (pkg_dir / "plugins", pathlib.Path("./lib/libresvip/plugins"))
]

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
        "IPython",
        "Cython",
        "sqlite3",
        "test",
        "PIL",
        "PySide6",
    ],
    "include_files": include_files,
}

executables = [
    Executable(
        "../../libresvip/cli/__main__.py", base=None, target_name="libresvip"
    ),
]

setup(
    name="LibreSVIP",
    version="0.1",
    options={"build_exe": build_exe_options},
    executables=executables,
)
