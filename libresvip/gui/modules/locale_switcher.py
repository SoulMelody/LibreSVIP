import gettext
from typing import Optional

from loguru import logger
from qmlease import app, slot
from qtpy.QtCore import QObject, QTranslator

from libresvip.core.config import Language, settings
from libresvip.core.constants import res_dir


class GettextTranslator(QTranslator):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.translation = None

    def load_translation(self, lang, translation_dir):
        try:
            self.translation = gettext.translation("libresvip", translation_dir, [lang])
        except FileNotFoundError:
            logger.warning(f"Translation file for {lang} not found.")
            self.translation = None

    def translate(
        self,
        context: str,
        sourceText: str,
        disambiguation: Optional[bytes] = ...,
        n: int = ...,
    ) -> str:
        if self.translation and sourceText.strip():
            return self.translation.gettext(sourceText)
        return sourceText


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
