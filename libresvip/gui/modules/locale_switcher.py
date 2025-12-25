import gettext

from PySide6.QtCore import QLocale, QObject, QTranslator, Signal, Slot

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

from libresvip.core.config import Language, config_path, settings
from libresvip.extension.manager import get_translation
from libresvip.utils import translation

from .application import app, qml_engine


class GettextTranslator(QTranslator):
    def load_translation(self, lang: str) -> None:
        try:
            translation.singleton_translation = get_translation(lang=lang)
        except OSError:
            translation.singleton_translation = gettext.NullTranslations()

    def translate(
        self,
        context: str,
        source_text: str,
        disambiguation: bytes | None = None,
        n: int = 0,
    ) -> str:
        if translation.singleton_translation is not None and source_text.strip():
            if (
                contextual_text := translation.singleton_translation.pgettext(context, source_text)
            ) != source_text:
                return contextual_text
            return translation.singleton_translation.gettext(source_text)
        return source_text


class LocaleSwitcher(QObject):
    translator_initialized = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._translator_initialized = False
        self.translator = GettextTranslator()
        if not config_path.exists():
            sys_locale = QLocale.system().name()
            settings.language = Language.from_locale(sys_locale)

    @Slot(result=str)
    def get_language(self) -> str:
        return settings.language.value

    @Slot(str)
    def switch_language(self, lang: str) -> None:
        if lang:
            self.translator.load_translation(lang)
            app.install_translator(self.translator)
            qml_engine.retranslate()
            settings.language = Language.from_locale(lang)
        else:
            app.remove_translator(self.translator)
            settings.language = Language.ENGLISH
        if not self._translator_initialized:
            self._translator_initialized = True
            self.translator_initialized.emit()
