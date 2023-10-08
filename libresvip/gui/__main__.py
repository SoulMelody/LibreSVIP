import os
import sys

import qtinter
from qtpy.QtGui import QIcon, QPixmap
from qtpy.QtQuickControls2 import QQuickStyle

if sys.platform == "win32":
    from libresvip.gui.modules.frameless_window_win32 import (
        FramelessWindow,  # noqa: F401
    )
else:
    from libresvip.gui.modules.frameless_window import FramelessWindow  # noqa: F401

from libresvip.core.constants import pkg_dir, res_dir
from libresvip.gui.modules import app, qml_engine


def run() -> None:
    os.environ["QT_QUICK_CONTROLS_MATERIAL_VARIANT"] = "Dense"
    QQuickStyle.setStyle("Material")
    icon_pixmap = QPixmap()
    icon_pixmap.loadFromData((res_dir / "libresvip.ico").read_bytes())
    app.setApplicationName("LibreSVIP")
    app.setOrganizationName("org.soulmelody.libresvip")
    app.setWindowIcon(QIcon(icon_pixmap))
    with qtinter.using_asyncio_from_qt():
        qml_engine.load(
            pkg_dir / "gui" / "main.qml",
        )
        app.exec()


if __name__ == "__main__":
    run()
