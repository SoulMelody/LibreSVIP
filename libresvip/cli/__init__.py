import sys

from libresvip.core.warning_types import warning_logger
from libresvip.extension.manager import get_translation
from libresvip.utils import translation

warning_logger.add(sys.stderr, format="{message}", level="WARNING")
translation.singleton_translation = get_translation()
