import gettext
from typing import Optional

from qtpy.QtCore import QLocale, QObject, QTranslator, Slot
from qtpy.QtGui import QGuiApplication
from qtpy.QtQml import QmlElement, QmlSingleton

from libresvip.core.config import Language, config_path, settings
from libresvip.core.constants import PACKAGE_NAME, res_dir

from .application import qml_engine

QML_IMPORT_NAME = "LibreSVIP"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


class GettextTranslator(QTranslator):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.translation = None

    def load_translation(self, lang: str, translation_dir: str) -> None:
        try:
            self.translation = gettext.translation(
                PACKAGE_NAME, translation_dir, [lang]
            )
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
        n: int = ...,
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
            QGuiApplication.installTranslator(self.translator)
            qml_engine.retranslate()
            settings.language = Language.from_locale(lang)
        else:
            QGuiApplication.removeTranslator(self.translator)
            settings.language = Language.ENGLISH
