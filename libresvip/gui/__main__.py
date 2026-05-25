import contextlib
import gettext
import sys
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QSplashScreen

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

from libresvip.core.config import Language, config_path, settings
from libresvip.core.constants import res_dir
from libresvip.gui.modules import (
    app,
    app_close_event,
    event_loop,
    qml_engine,
)

if TYPE_CHECKING:
    from PySide6.QtCore import QObject


splash_screen: QSplashScreen | None = None
splash_translation: gettext.NullTranslations | None = None


def _(text: str) -> str:
    return text


def _load_splash_translation(lang: str) -> gettext.NullTranslations:
    msg_dir = res_dir / "locales" / lang / "LC_MESSAGES"
    if not msg_dir.is_dir():
        return gettext.NullTranslations()
    for child_file in msg_dir.iterdir():
        if child_file.name.endswith(".mo"):
            with child_file.open("rb") as fp:
                return gettext.GNUTranslations(fp)
    return gettext.NullTranslations()


def _build_splash_pixmap(icon_pixmap: QPixmap) -> QPixmap:
    splash_pixmap = QPixmap(520, 300)
    splash_pixmap.fill(QColor("#f3f4f6"))
    painter = QPainter(splash_pixmap)
    painter.set_render_hint(QPainter.RenderHint.Antialiasing)
    painter.set_pen(Qt.PenStyle.NoPen)
    painter.set_brush(QColor("#ffffff"))
    painter.draw_rounded_rect(20, 20, 480, 260, 24, 24)
    painter.set_brush(QColor("#ff6a3d"))
    painter.draw_rounded_rect(50, 50, 96, 96, 24, 24)
    scaled_icon = icon_pixmap.scaled(
        64,
        64,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    painter.draw_pixmap(66, 66, scaled_icon)
    painter.set_pen(QColor("#111827"))
    title_font = QFont()
    title_font.point_size = 24
    title_font.bold = True
    painter.set_font(title_font)
    painter.draw_text(176, 92, _translate_splash(_("LibreSVIP")))
    subtitle_font = QFont()
    subtitle_font.point_size = 10
    painter.set_font(subtitle_font)
    painter.set_pen(QColor("#6b7280"))
    painter.draw_text(176, 122, _translate_splash(_("Preparing plugins and interface")))
    painter.end()
    return splash_pixmap


def _set_splash_message(message: str) -> None:
    if splash_screen is None:
        return
    splash_screen.show_message(
        _translate_splash(message),
        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
        QColor("#4b5563"),
    )
    app.process_events()


def _translate_splash(message: str) -> str:
    if splash_translation is None:
        return message
    return splash_translation.gettext(message)


def startup() -> None:
    global splash_screen, splash_translation
    qml_engine.load(":/qml/main.qml")
    if not qml_engine.root_objects():
        sys.exit(-1)
    _set_splash_message(_("Loading translations..."))
    locale_switcher.load_plugin_translations()
    if splash_screen is not None:
        app.process_events()
        splash_screen.close()
        splash_screen = None
        splash_translation = None
    with contextlib.suppress(RuntimeError), event_loop:
        event_loop.run_until_complete(app_close_event.wait())


def run() -> None:
    global locale_switcher, splash_screen, splash_translation
    icon_pixmap = QPixmap()
    icon_pixmap.load_from_data((res_dir / "libresvip.ico").read_bytes())
    app.application_name = "LibreSVIP"
    app.organization_name = "org.soulmelody.libresvip"
    app.window_icon = QIcon(icon_pixmap)
    app.set_attribute(Qt.ApplicationAttribute.AA_DontUseNativeMenuBar, True)
    if not config_path.exists():
        settings.language = Language.auto()
    splash_translation = _load_splash_translation(settings.language.value)
    splash_screen = QSplashScreen(_build_splash_pixmap(icon_pixmap))
    splash_screen.show()
    splash_screen.raise_()
    _set_splash_message(_("Loading format providers..."))

    from libresvip.gui.modules import (
        Clipboard,
        ConfigItems,
        IconicFontLoader,
        LocaleSwitcher,
        TaskManager,
    )

    locale_switcher = LocaleSwitcher()

    config_items = ConfigItems()
    task_manager = TaskManager()
    _set_splash_message(_("Building interface..."))

    initial_properties: dict[str, QObject] = {
        "clipboard": Clipboard(),
        "configItems": config_items,
        "iconicFontLoader": IconicFontLoader(),
        "localeSwitcher": locale_switcher,
        "taskManager": task_manager,
    }
    with contextlib.suppress(ImportError):
        from libresvip.gui.modules import Notifier

        initial_properties["notifier"] = Notifier()  # pyrefly: ignore[not-callable]
    qml_engine.set_initial_properties(initial_properties)
    locale_switcher.translator_initialized.connect(startup)
    _set_splash_message(_("Opening window..."))
    locale_switcher.initialize()


if __name__ == "__main__":
    run()
