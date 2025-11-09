import asyncio
import os
import platform

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

from .vendor.qasync import QEventLoop

__all__ = [
    "app",
    "app_close_event",
    "event_loop",
    "qml_engine",
]

if platform.system() == "Windows":
    os.environ["QT_QPA_PLATFORM"] = "windows:nodirectwrite"
os.environ["QT_QUICK_CONTROLS_MATERIAL_VARIANT"] = "Dense"
app = QGuiApplication()
qml_engine = QQmlApplicationEngine()
QQuickStyle.setStyle("Material")

event_loop = QEventLoop(app)
asyncio.set_event_loop(event_loop)
app_close_event: asyncio.Event = asyncio.Event()


def set_close_event() -> None:
    if not app_close_event.is_set():
        app_close_event.set()


app.aboutToQuit.connect(set_close_event)
qml_engine.quit.connect(set_close_event)
