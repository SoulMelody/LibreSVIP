import gettext
from typing import Optional

from qmlease import app, slot
from qtpy.QtCore import QLocale, QObject, QTranslator

from libresvip.core.config import Language, config_path, settings
from libresvip.core.constants import PACKAGE_NAME, res_dir


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


class LocaleSwitcher(QObject):
    def __init__(self) -> None:
        super().__init__()
        self.translator = GettextTranslator(parent=app)
        if not config_path.exists():
            sys_locale = QLocale.system().name()
            settings.language = Language.from_locale(sys_locale)
        self.switch_language(settings.language.to_locale())

    @slot(result=str)
    def get_language(self) -> str:
        return settings.language.to_locale()

    @slot(str)
    def switch_language(self, lang: str) -> None:
        if lang:
            translation_dir = str(res_dir / "locales")
            self.translator.load_translation(lang, translation_dir)
            app.installTranslator(self.translator)
            app.engine.retranslate()
            settings.language = Language.from_locale(lang)
        else:
            app.removeTranslator(self.translator)
            settings.language = Language.ENGLISH
