from PySide6 import QtCore

from libresvip.core.compat import as_file
from libresvip.core.constants import res_dir


def init_resources() -> None:
    with as_file(res_dir / "resources.rcc") as rcc_file:
        QtCore.QResource.registerResource(str(rcc_file))


def cleanup_resources() -> None:
    with as_file(res_dir / "resources.rcc") as rcc_file:
        QtCore.QResource.unregisterResource(str(rcc_file))


init_resources()
