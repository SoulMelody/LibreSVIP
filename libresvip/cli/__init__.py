import sys

from libresvip.core.warning_types import warning_logger
from libresvip.extension.manager import get_translation
from libresvip.utils import translation

if sys.platform == "win32":
    import ctypes

    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleOutputCP(65001)
    kernel32.SetConsoleCP(65001)

warning_logger.add(sys.stderr, format="{message}", level="WARNING")
translation.singleton_translation = get_translation()
