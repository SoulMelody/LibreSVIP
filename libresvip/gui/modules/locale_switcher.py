import gettext
from typing import Optional

from PySide6.QtCore import QLocale, QObject, QTranslator, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QmlElement, QmlSingleton

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

from libresvip.core.config import Language, config_path, settings
from libresvip.core.constants import PACKAGE_NAME
from libresvip.utils import translation

from .application import qml_engine

QML_IMPORT_NAME = "LibreSVIP"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


class GettextTranslator(QTranslator):
    def load_translation(self, lang: str) -> None:
        try:
            translation.singleton_translation = translation.get_translation(PACKAGE_NAME, lang)
        except OSError:
            translation.singleton_translation = gettext.NullTranslations()

    def translate(
        self,
        context: str,
        source_text: str,
        disambiguation: Optional[bytes] = None,
        n: int = 0,
    ) -> str:
        if translation.singleton_translation is not None and source_text.strip():
            return translation.singleton_translation.gettext(source_text)
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
            self.translator.load_translation(lang)
            QGuiApplication.install_translator(self.translator)
            qml_engine.retranslate()
            settings.language = Language.from_locale(lang)
        else:
            QGuiApplication.remove_translator(self.translator)
            settings.language = Language.ENGLISH
