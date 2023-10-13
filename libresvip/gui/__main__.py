import os
import sys

import qtinter
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtQuickControls2 import QQuickStyle

from libresvip.core.constants import pkg_dir, res_dir
from libresvip.gui.modules import app, qml_engine

if sys.platform == "win32":
    from libresvip.gui.modules.frameless_window_win32 import (
        FramelessWindow,  # noqa: F401
    )
else:
    from libresvip.gui.modules.frameless_window import FramelessWindow  # noqa: F401

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401


def run() -> None:
    os.environ["QT_QUICK_CONTROLS_MATERIAL_VARIANT"] = "Dense"
    QQuickStyle.set_style("Material")
    icon_pixmap = QPixmap()
    icon_pixmap.load_from_data((res_dir / "libresvip.ico").read_bytes())
    app.application_name = "LibreSVIP"
    app.organization_name = "org.soulmelody.libresvip"
    app.window_icon = QIcon(icon_pixmap)
    with qtinter.using_asyncio_from_qt():
        qml_engine.load(
            pkg_dir / "gui" / "main.qml",
        )
        if not qml_engine.root_objects():
            sys.exit(-1)
        app.exec()


if __name__ == "__main__":
    run()
