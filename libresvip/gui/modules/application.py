from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

__all__ = [
    "app",
    "qml_engine",
]

app = QGuiApplication()
qml_engine = QQmlApplicationEngine()
