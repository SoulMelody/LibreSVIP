import pathlib

from qtpy.QtCore import QUrl
from qtpy.QtGui import QDesktopServices


def open_path(path: pathlib.Path):
    output_url = QUrl.fromLocalFile(path)
    QDesktopServices.openUrl(output_url)


def open_url(url: str):
    QDesktopServices.openUrl(QUrl(url))
