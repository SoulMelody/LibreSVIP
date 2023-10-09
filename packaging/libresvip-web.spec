# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import contextlib
import os
import sys
sys.modules['FixTk'] = None

import nicegui
import shellingham
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

from libresvip.core.constants import pkg_dir

with contextlib.suppress(Exception):
    if (
        ("conda" in sys.version or "Continuum" in sys.version)
        and shellingham.detect_shell()[0] == "bash"
        and os.name == "nt"
    ):
        os.environ["PATH"] += f"{os.pathsep}{sys.base_prefix}/Library/bin"


a = Analysis(
    ['../libresvip/web/pages.py'],
    pathex=[
        os.path.join(os.__file__, os.pardir),
        os.path.join(nicegui.__path__[0], os.pardir)
    ],
    binaries=[],
    datas=[
        (str(pkg_dir / "plugins"), "libresvip/plugins"),
    ] + copy_metadata("libresvip") + collect_data_files("libresvip") + collect_data_files("nicegui") + collect_data_files("xsdata"),
    hiddenimports=[
        "construct_typed",
        "drawsvg",
        "google.protobuf.any_pb2",
        "jinja2",
        "mido_fix",
        "portion",
        "proto",
        "pypinyin",
        "srt",
        "textx",
        "fsspec.implementations.memory",
        "upath.implementations.memory",
        "wanakana",
        "xsdata.formats.dataclass.parsers",
        "xsdata.formats.dataclass.serializers",
        "zstd",
    ] + collect_submodules("libresvip.core") + collect_submodules("libresvip.model"),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'FixTk', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter', 'sqlite3', 'docutils',
        'numpy', "pandas", "pandas.plotting", 'pandas.io.formats.style',
        'jedi', 'IPython', 'parso', 'plotly', 'matplotlib', 'matplotlib.backends', 'PIL', 'PIL.Image',
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
to_keep = []
js_lib_prefix = os.path.join("nicegui", "elements", "lib")
to_exclude = [
    os.path.join(js_lib_prefix, "echarts"),
    os.path.join(js_lib_prefix, "highcharts"),
    os.path.join(js_lib_prefix, "mermaid"),
    os.path.join(js_lib_prefix, "plotly"),
    os.path.join(js_lib_prefix, "vanilla-jsoneditor"),
]

for (dest, source, kind) in a.datas:
    # Skip anything we don't need.
    if any(dest.startswith(exclude_dir) for exclude_dir in to_exclude):
        continue
    to_keep.append((dest, source, kind))

# Replace list of data files with filtered one.
a.datas = to_keep
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='libresvip-web',
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
    name='libresvip-web',
)
