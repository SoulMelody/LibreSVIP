import gettext
from typing import Optional

from PySide6.QtCore import QLocale, QObject, QTranslator, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QmlElement, QmlSingleton

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

from libresvip.core.config import Language, config_path, settings
from libresvip.core.constants import PACKAGE_NAME, res_dir

from .application import qml_engine

QML_IMPORT_NAME = "LibreSVIP"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


class GettextTranslator(QTranslator):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.translation: Optional[gettext.NullTranslations] = None

    def load_translation(self, lang: str, translation_dir: str) -> None:
        try:
            self.translation = gettext.translation(PACKAGE_NAME, translation_dir, [lang])
            gettext.textdomain(PACKAGE_NAME)
            gettext.bindtextdomain(PACKAGE_NAME, translation_dir)
        except OSError:
            self.translation = gettext.NullTranslations()
            gettext.textdomain("messages")
        self.translation.install(names=["gettext", "ngettext"])

    def translate(
        self,
        context: str,
        source_text: str,
        disambiguation: Optional[bytes] = None,
        n: int = 0,
    ) -> str:
        if self.translation and source_text.strip():
            return self.translation.gettext(source_text)
        return source_text


@QmlElement
@QmlSingleton
class LocaleSwitcher(QObject):
    def __init__(self) -> None:
        super().__init__()
        self.translator = GettextTranslator()
        if not config_path.exists():
            sys_locale = QLocale.system().name()
            settings.language = Language.from_locale(sys_locale)
        self.switch_language(settings.language.to_locale())

    @Slot(result=str)
    def get_language(self) -> str:
        return settings.language.to_locale()

    @Slot(str)
    def switch_language(self, lang: str) -> None:
        if lang:
            translation_dir = str(res_dir / "locales")
            self.translator.load_translation(lang, translation_dir)
            QGuiApplication.install_translator(self.translator)
            qml_engine.retranslate()
            settings.language = Language.from_locale(lang)
        else:
            QGuiApplication.remove_translator(self.translator)
            settings.language = Language.ENGLISH
