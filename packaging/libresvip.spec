# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import contextlib
import os
import pathlib
import platform
import sys
sys.modules['FixTk'] = None

import libresvip
import PySide6
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

here = pathlib.Path(".")

cli_collections = []
if platform.machine() != "ARM64":
    cli_a = Analysis(
        ['../libresvip/cli/__main__.py'],
        pathex=[
            os.path.join(os.__file__, os.pardir)
        ],
        binaries=[],
        datas=collect_data_files("xsdata") + collect_entry_point("xsdata.plugins.class_types")[0],
        hiddenimports=[
            "bidict",
            "construct_typed",
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


pyside6_dir = pathlib.Path(PySide6.__path__[0])
gui_a = Analysis(
    ['../libresvip/gui/__main__.py'],
    pathex=[
        os.path.join(os.__file__, os.pardir),
        os.path.join(PySide6.__path__[0], os.pardir)
    ],
    binaries=[],
    datas=collect_data_files("desktop_notifier") + collect_data_files("fonticon_mdi7") + collect_data_files("xsdata") + collect_entry_point("xsdata.plugins.class_types")[0],
    hiddenimports=[
        "bidict",
        "construct_typed",
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
        'FixTk', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter', 'sqlite3', 'docutils',
        'pywintypes', 'pythoncom',
        'numpy', "pandas", "pandas.plotting", 'pandas.io.formats.style',
        'jedi', 'IPython', 'parso', 'plotly', 'matplotlib', 'matplotlib.backends', 'PIL', 'PIL.Image', 'zmq',
        "uvicorn", "webview", "clr", 'pythoncom', 'pywintypes',
        'PySide6.QtDataVisualization',
        'PySide6.QtWebChannel',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineQuick',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtPositioning',
        'PySide6.QtPrintSupport',
        'PySide6.QtQuick3D',
        'PySide6.QtQuickWidgets',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

gui_binaries = []

def platform_libs_for_qtmodule(module: str) -> list[str]:
    return [
        f"libQt6{module}.so.6",  # Linux
        f"Qt{module}",  # MacOS
        f"Qt6{module}.dll",  # Windows
    ]

binaries_exclude = sum(
    (platform_libs_for_qtmodule(module)
    for module in (
        "Charts",
        "ChartsQml",
        "Concurrent",
        "DataVisualization",
        "DataVisualizationQml",
        "Graphs",
        "Location",
        "Multimedia",
        "MultimediaQuick",
        "Pdf",
        "PdfQuick",
        "Positioning",
        "PositioningQuick",
        "Quick3D",
        "Quick3DAssetImport",
        "Quick3DAssetUtils",
        "Quick3DEffects",
        "Quick3DHelpers",
        "Quick3DHelpersImpl",
        "Quick3DParticleEffects",
        "Quick3DParticles",
        "Quick3DRuntimeRender",
        "Quick3DSpatialAudio",
        "Quick3DUtils",
        "Quick3DXr",
        "QuickTest",
        "QuickTimeline",
        "QuickTimelineBlendTrees",
        "QuickWidget",
        "RemoteObjects",
        "RemoteObjectsQml",
        "Scxml",
        "ScxmlQml",
        "Sensors",
        "SensorsQuick",
        "ShaderTools",
        "SpatialAudio",
        "Sql",
        "StateMachine",
        "StateMachineQml",
        "Test",
        "TextToSpeech",
        "VirtualKeyboard",
        "VirtualKeyboardSettings",
        "WebChannel",
        "WebChannelQuick",
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
    )),
    [str(dbg_lib) for dbg_lib in pyside6_dir.rglob("**/qmldbg*")]
)

for (dest, source, kind) in gui_a.binaries:
    # Skip anything we don't need.
    if os.path.split(dest)[1] in binaries_exclude:
        continue
    gui_binaries.append((dest, source, kind))

# Replace list of data files with filtered one.
gui_a.binaries = gui_binaries
gui_pyz = PYZ(gui_a.pure, cipher=block_cipher)

gui_exe = EXE(
    gui_pyz,
    gui_a.scripts,
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
    entitlements_file=str(here / "macos-entitlements.plist"),
    icon=['../libresvip/res/libresvip.ico'],
)
coll = COLLECT(
    *cli_collections,
    gui_exe,
    gui_a.binaries,
    gui_a.zipfiles,
    gui_a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='libresvip',
)


if platform.system() == "Darwin":
    app = BUNDLE(
        coll,
        name="LibreSVIP.app",
        icon=pathlib.Path("../libresvip/res/libresvip.ico"),
        bundle_identifier="org.soulmelody.LibreSVIP",
        version=libresvip.__version__,
        info_plist={
            "NSPrincipalClass": "NSApplication",
            "CFBundleExecutable": "MacOS/libresvip-gui",
            "CFBundleIconFile": "logo.icns",
            "NSAppleEventsUsageDescription": "Please grant access to use Apple Events",
            "CFBundleVersion": libresvip.__version__,
        },
    )