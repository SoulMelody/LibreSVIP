import pathlib

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401


def open_path(path: pathlib.Path) -> None:
    output_url = QUrl.from_local_file(path)
    QDesktopServices.open_url(output_url)


def open_url(url: str) -> None:
    QDesktopServices.open_url(QUrl(url))
