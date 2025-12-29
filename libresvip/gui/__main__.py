import sys
from typing import TYPE_CHECKING

from PySide6.QtGui import QIcon, QPixmap

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

from libresvip.core.constants import res_dir
from libresvip.gui.modules import (
    Clipboard,
    ConfigItems,
    IconicFontLoader,
    LocaleSwitcher,
    TaskManager,
    app,
    app_close_event,
    event_loop,
    qml_engine,
)

if TYPE_CHECKING:
    from PySide6.QtCore import QObject


def startup() -> None:
    qml_engine.load(":/qml/main.qml")
    if not qml_engine.root_objects():
        sys.exit(-1)
    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())


def run() -> None:
    locale_switcher = LocaleSwitcher()
    initial_properties: dict[str, QObject] = {
        "clipboard": Clipboard(),
        "configItems": ConfigItems(),
        "iconicFontLoader": IconicFontLoader(),
        "localeSwitcher": locale_switcher,
        "taskManager": TaskManager(),
    }
    try:
        from libresvip.gui.modules import Notifier

        initial_properties["notifier"] = Notifier()
    except ImportError:
        pass
    icon_pixmap = QPixmap()
    icon_pixmap.load_from_data((res_dir / "libresvip.ico").read_bytes())
    app.application_name = "LibreSVIP"
    app.organization_name = "org.soulmelody.libresvip"
    app.window_icon = QIcon(icon_pixmap)
    qml_engine.set_initial_properties(initial_properties)
    locale_switcher.translator_initialized.connect(startup)
    locale_switcher.switch_language(locale_switcher.get_language())


if __name__ == "__main__":
    run()
