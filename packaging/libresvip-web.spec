# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import contextlib
import os
import platform
import sys
sys.modules['FixTk'] = None

import nicegui
import shellingham
from PyInstaller.utils.hooks import collect_data_files, collect_entry_point
from PyInstaller.utils.misc import is_win

with contextlib.suppress(Exception):
    if (
        ("conda" in sys.version or "Continuum" in sys.version)
        and shellingham.detect_shell()[0] == "bash"
        and os.name == "nt"
    ):
        os.environ["PATH"] += f"{os.pathsep}{sys.base_prefix}/Library/bin"


a = Analysis(
    ['../libresvip/web/__main__.py'],
    pathex=[
        os.path.join(os.__file__, os.pardir),
        os.path.join(nicegui.__path__[0], os.pardir)
    ],
    binaries=[],
    datas=collect_data_files("nicegui") + collect_data_files("xsdata") + collect_entry_point("xsdata.plugins.class_types")[0],
    hiddenimports=[
        "bidict",
        "construct_typed",
        "docutils",
        "drawsvg",
        "google.protobuf.any_pb2",
        "jinja2",
        "mido_fix",
        "parsimonious",
        "portion",
        "proto",
        "pypinyin",
        "pysubs2",
        "pyzipper",
        "fsspec.implementations.memory",
        "upath.implementations.memory",
        "wanakana",
        "xsdata_pydantic.bindings",
        "xsdata_pydantic.fields",
        "xsdata_pydantic.hooks.class_type",
        "zstandard",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'FixTk', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter', 'sqlite3',
        'pywintypes', 'pythoncom',
        'numpy', "pandas", "pandas.plotting", 'pandas.io.formats.style',
        'jedi', 'IPython', 'parso', 'plotly', 'matplotlib', 'matplotlib.backends', 'PIL', 'PIL.Image', 'zmq',
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
    os.path.join(js_lib_prefix, "aggrid"),
    os.path.join(js_lib_prefix, "codemirror"),
    os.path.join(js_lib_prefix, "echarts"),
    os.path.join(js_lib_prefix, "echarts-gl"),
    os.path.join(js_lib_prefix, "leaflet"),
    os.path.join(js_lib_prefix, "mermaid"),
    os.path.join(js_lib_prefix, "plotly"),
    os.path.join(js_lib_prefix, "three"),
    os.path.join(js_lib_prefix, "vanilla-jsoneditor"),
]
if is_win and platform.machine() != "ARM64":
    to_exclude.append(os.path.join("webview", "lib", "runtimes", "win-arm", "native", "WebView2Loader.dll"))

for (dest, source, kind) in a.datas:
    # Skip anything we don't need.
    if any(dest.startswith(exclude_dir) for exclude_dir in to_exclude):
        continue
    to_keep.append((dest, source, kind))

# Replace list of data files with filtered one.
a.datas = to_keep
pyz = PYZ(a.pure, cipher=block_cipher)

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
