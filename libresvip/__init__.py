import importlib.metadata
import os

from libresvip.core.constants import PACKAGE_NAME

__version__ = importlib.metadata.version(PACKAGE_NAME)
os.environ.setdefault("LOGURU_AUTOINIT", "false")
