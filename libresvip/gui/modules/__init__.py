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
from .config_items import ConfigItems
from .font_loader import IconicFontLoader
from .frameless_helper import FramelessHelper
from .locale_switcher import LocaleSwitcher
from .log_handler import enable_log_handler
from .task_manager import TaskManager

enable_log_handler()
if platform.python_implementation() == "CPython":
    __all__ += ["Notifier"]

    from .notifier import Notifier
