__all__ = [
    "Clipboard",
    "ConfigItems",
    "IconicFontLoader",
    "LocaleSwitcher",
    "TaskManager",
    "app",
    "qml_engine",
]

import platform

from .application import app, qml_engine
from .clipboard import Clipboard
from .config_items import ConfigItems
from .font_loader import IconicFontLoader
from .locale_switcher import LocaleSwitcher
from .task_manager import TaskManager

if platform.python_implementation() == "CPython":
    __all__.append("Notifier")

    from .notifier import Notifier  # noqa: F401
