# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import contextlib
import os
import pathlib
import platform
import sys
sys.modules['FixTk'] = None

import libresvip
import shellingham
from PyInstaller.compat import is_conda, is_win
from PyInstaller.utils.hooks import collect_data_files, collect_entry_point

with contextlib.suppress(Exception):
    if (
        is_conda
        and is_win
        and shellingham.detect_shell()[0] == "bash"
    ):
        os.environ["PATH"] += f"{os.pathsep}{sys.base_prefix}/Library/bin"

here = pathlib.Path(".")

zstd_backends = []
if platform.python_version_tuple() >= ("3", "14"):
    pass
elif is_win and platform.python_compiler().startswith("GCC"):
    zstd_backends.append("zstandard")
else:
    zstd_backends.append("backports.zstd")

cli_collections = []
cli_a = Analysis(
    ['../libresvip/cli/__main__.py'],
    pathex=[
        os.path.join(os.__file__, os.pardir)
    ],
    binaries=[],
    datas=collect_data_files("jyutping") + collect_data_files("xsdata") + collect_entry_point("xsdata.plugins.class_types")[0],
    hiddenimports=[
        *zstd_backends,
        "bidict",
        "construct_typed",
        "Cryptodome.Util.Padding",
        "svg",
        "jinja2",
        "jyutping",
        "ko_pron",
        "tatsu",
        "portion",
        "aristaproto.lib.pydantic.google.protobuf",
        "pypinyin",
        "pysubs2",
        "pyzipper",
        "fsspec.implementations.memory",
        "upath.implementations.memory",
        "wanakana",
        "winloop._noop",
        "xsdata_pydantic.bindings",
        "xsdata_pydantic.fields",
        "xsdata_pydantic.hooks.class_type",
        "ryaml",
        "yaml_ft",
        "yaml",
        "yaml12",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'FixTk', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter', 'sqlite3', 'docutils',
        'pywintypes', 'pythoncom',
        'numpy', "pandas", "pandas.plotting", 'pandas.io.formats.style',
        'jedi', 'IPython', 'parso', 'plotly', 'matplotlib', 'matplotlib.backends', 'PIL', 'PIL.Image', 'zmq',
        "uvicorn", "webview", "clr", 'pythoncom', 'pywintypes',
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtDataVisualization',
        'PySide6.QtGui',
        'PySide6.QtNetwork',
        'PySide6.QtOpenGL',
        'PySide6.QtOpenGLWidgets',
        'PySide6.QtWebChannel',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWidgets',
        'PySide6.QtPositioning',
        'PySide6.QtPrintSupport',
        'PySide6.QtQuick',
        'PySide6.QtQuickWidgets',
        'PySide6.QtQml',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
cli_pyz = PYZ(cli_a.pure, cipher=block_cipher)
cli_exe = EXE(
    cli_pyz,
    cli_a.scripts,
    [],
    exclude_binaries=True,
    name='libresvip-cli',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
cli_collections.extend([
    cli_exe,
    cli_a.binaries,
    cli_a.zipfiles,
    cli_a.datas,
])
coll = COLLECT(
    *cli_collections,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='libresvip-cli',
)
