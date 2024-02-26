__all__ = [
    "Clipboard",
    "ConfigItems",
    "FramelessWindow",
    "IconicFontLoader",
    "LocaleSwitcher",
    "TaskManager",
    "app",
    "app_close_event",
    "event_loop",
    "qml_engine",
]

import platform
import sys

from .application import app, app_close_event, event_loop, qml_engine
from .clipboard import Clipboard
from .config_items import ConfigItems
from .font_loader import IconicFontLoader
from .locale_switcher import LocaleSwitcher
from .task_manager import TaskManager

if sys.platform == "win32":
    from libresvip.gui.modules.frameless_window_win32 import FramelessWindow
else:
    from libresvip.gui.modules.frameless_window import FramelessWindow

if platform.python_implementation() == "CPython":
    __all__ += ["Notifier"]

    from .notifier import Notifier  # noqa: F401
