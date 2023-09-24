# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import contextlib
import os
import sys
sys.modules['FixTk'] = None

import qmlease
import shellingham
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

from libresvip.core.constants import pkg_dir

with contextlib.suppress(Exception):
    if (
        ("conda" in sys.version or "Continuum" in sys.version)
        and shellingham.detect_shell()[0] == "bash"
        and os.name == "nt"
    ):
        os.environ["PATH"] += f"{os.pathsep}{sys.base_prefix}/Library/bin"


a = Analysis(
    ['../libresvip/gui/__main__.py'],
    pathex=[
        os.path.join(os.__file__, os.pardir),
        os.path.join(qmlease.__path__[0], os.pardir)
    ],
    binaries=[],
    datas=[
        (str(pkg_dir / "plugins"), "libresvip/plugins"),
    ] + copy_metadata("libresvip") + collect_data_files("libresvip") + collect_data_files("desktop_notifier") + collect_data_files("qmlease") + collect_data_files("xsdata"),
    hiddenimports=[
        "construct_typed",
        "drawsvg",
        "jinja2",
        "libresvip",
        "mido_fix",
        "portion",
        "pure_protobuf.annotations",
        "pypinyin",
        "srt",
        "textx",
        "fsspec.implementations.memory",
        "upath.implementations.memory",
        "wanakana",
        "xsdata.formats.dataclass.parsers",
        "xsdata.formats.dataclass.serializers",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'FixTk', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter', 'sqlite3', 'docutils',
        'numpy', "pandas", "pandas.plotting", 'pandas.io.formats.style',
        'jedi', 'IPython', 'parso', 'plotly', 'matplotlib', 'matplotlib.backends', 'PIL', 'PIL.Image',
        "uvicorn", "webview", "clr",
        'PySide6.QtDataVisualization',
        'PySide6.QtWebChannel',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtPositioning',
        'PySide6.QtPrintSupport',
        'PySide6.QtQuickWidgets',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
to_keep = []
to_exclude = [
    "libQt6WebEngineCore.so.6",
    "QtWebEngineCore",
    "Qt6WebEngineCore.dll",
]

for (dest, source, kind) in a.binaries:
    # Skip anything we don't need.
    if os.path.split(dest)[1] in to_exclude:
        continue
    to_keep.append((dest, source, kind))

# Replace list of data files with filtered one.
a.binaries = to_keep
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='libresvip-gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['../libresvip/res/libresvip.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='libresvip-gui',
)
