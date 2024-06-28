import asyncio

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from .vendor.qasync import QEventLoop

__all__ = [
    "app",
    "app_close_event",
    "event_loop",
    "qml_engine",
]

app = QGuiApplication()
qml_engine = QQmlApplicationEngine()

event_loop = QEventLoop(app)
asyncio.set_event_loop(event_loop)
app_close_event: asyncio.Event = asyncio.Event()
app.aboutToQuit.connect(app_close_event.set)
qml_engine.quit.connect(app_close_event.set)
