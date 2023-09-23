import os
import sys

import qtinter
from qmlease import app
from qtpy.QtGui import QPixmap
from qtpy.QtQml import qmlRegisterType
from qtpy.QtQuickControls2 import QQuickStyle

from libresvip.core.constants import pkg_dir, res_dir
from libresvip.gui.modules import (
    Clipboard,
    ConfigItems,
    FontLoader,
    LocaleSwitcher,
    Notifier,
    TaskManager,
)


def run() -> None:
    os.environ["QT_QUICK_CONTROLS_MATERIAL_VARIANT"] = "Dense"
    app._register_backend = lambda: None
    QQuickStyle.setStyle("Material")
    icon_pixmap = QPixmap()
    icon_pixmap.loadFromData((res_dir / "libresvip.ico").read_bytes())
    app.set_app_name("LibreSVIP")
    app.set_app_icon(icon_pixmap)
    if sys.platform == "win32":
        from libresvip.gui.modules.frameless_window_win32 import Win32FramelessWindow

        qmlRegisterType(
            Win32FramelessWindow, "FramelessWindow", 1, 0, "FramelessWindow"
        )
    else:
        from libresvip.gui.modules.frameless_window import FramelessWindow

        qmlRegisterType(FramelessWindow, "FramelessWindow", 1, 0, "FramelessWindow")
    config_items = ConfigItems()
    task_manager = TaskManager()
    config_items.auto_set_output_extension_changed.connect(
        task_manager.reset_output_ext
    )
    app.register(Clipboard(), name="clipboard")
    app.register(config_items, name="config_items")
    app.register(FontLoader(), name="qta")
    app.register(LocaleSwitcher(), name="locale")
    app.register(task_manager, name="task_manager")
    app.register_qmldir(
        pkg_dir / "gui" / "components",
    )
    with qtinter.using_asyncio_from_qt():
        app.register(Notifier(), name="notifier")
        app.run(
            pkg_dir / "gui" / "main.qml",
            # debug=True
        )


if __name__ == "__main__":
    run()
