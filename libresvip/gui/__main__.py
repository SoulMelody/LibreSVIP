import sys

from PySide6.QtGui import QIcon, QPixmap

from libresvip.core.constants import res_dir
from libresvip.gui.modules import (
    LocaleSwitcher,
    app,
    app_close_event,
    event_loop,
    qml_engine,
)

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401


def startup() -> None:
    qml_engine.load(":/qml/main.qml")
    if not qml_engine.root_objects():
        sys.exit(-1)
    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())


def run() -> None:
    icon_pixmap = QPixmap()
    icon_pixmap.load_from_data((res_dir / "libresvip.ico").read_bytes())
    app.application_name = "LibreSVIP"
    app.organization_name = "org.soulmelody.libresvip"
    app.window_icon = QIcon(icon_pixmap)
    locale_switcher = LocaleSwitcher()
    locale_switcher.translator_initialized.connect(startup)
    locale_switcher.switch_language(locale_switcher.get_language())


if __name__ == "__main__":
    run()
