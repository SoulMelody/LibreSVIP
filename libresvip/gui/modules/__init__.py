__all__ = [
    "Clipboard",
    "ConfigItems",
    "FramelessHelper",
    "IconicFontLoader",
    "LocaleSwitcher",
    "TaskManager",
    "app",
    "app_close_event",
    "event_loop",
    "qml_engine",
]

import platform

from .application import app, app_close_event, event_loop, qml_engine
from .clipboard import Clipboard
from .font_loader import IconicFontLoader
from .frameless_helper import FramelessHelper
from .log_handler import enable_log_handler


def __getattr__(name: str) -> type:
    if name == "ConfigItems":
        from .config_items import ConfigItems

        return ConfigItems
    if name == "LocaleSwitcher":
        from .locale_switcher import LocaleSwitcher

        return LocaleSwitcher
    if name == "TaskManager":
        from .task_manager import TaskManager

        return TaskManager
    if name == "Notifier":
        from .notifier import Notifier

        return Notifier
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)


enable_log_handler()
if platform.python_implementation() == "CPython":
    __all__ += ["Notifier"]
