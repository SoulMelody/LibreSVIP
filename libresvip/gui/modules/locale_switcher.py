import gettext
from typing import Optional

from qmlease import app, slot
from qtpy.QtCore import QObject, QTranslator

from libresvip.core.config import Language, settings
from libresvip.core.constants import PACKAGE_NAME, res_dir


class GettextTranslator(QTranslator):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.translation = None

    def load_translation(self, lang, translation_dir):
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
        disambiguation: Optional[bytes] = ...,
        n: int = ...,
    ) -> str:
        if self.translation and source_text.strip():
            return self.translation.gettext(source_text)
        return source_text


class LocaleSwitcher(QObject):
    def __init__(self):
        super().__init__()
        self.translator = GettextTranslator(
            parent=app,
        )
        self.switch_language(settings.language.to_locale())

    @slot(str)
    def switch_language(self, lang):
        if lang:
            translation_dir = str(res_dir / "locales")
            self.translator.load_translation(lang, translation_dir)
            app.installTranslator(self.translator)
            app.engine.retranslate()
            settings.language = Language.from_locale(lang)
        else:
            app.removeTranslator(self.translator)
            settings.language = Language.ENGLISH
