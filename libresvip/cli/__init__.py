import sys

from libresvip.core.warning_types import warning_logger
from libresvip.utils import translation

warning_logger.add(sys.stderr, format="{message}", level="WARNING")
translation.singleton_translation = translation.get_translation()
translation.singleton_translation.install()
