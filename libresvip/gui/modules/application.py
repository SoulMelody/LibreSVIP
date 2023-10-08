from qtpy.QtGui import QGuiApplication
from qtpy.QtQml import QQmlApplicationEngine

__all__ = [
    "app",
    "qml_engine",
]

app = QGuiApplication()
qml_engine = QQmlApplicationEngine()
