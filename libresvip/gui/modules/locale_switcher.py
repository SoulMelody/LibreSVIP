import gettext

from PySide6.QtCore import QLocale, QObject, QTranslator, Signal, Slot

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

from libresvip.core.config import Language, config_path, settings
from libresvip.extension.manager import get_translation
from libresvip.utils import translation

from .application import app, qml_engine


class GettextTranslator(QTranslator):
    def load_translation(self, lang: str, *, include_plugins: bool = True) -> None:
        try:
            translation.singleton_translation = get_translation(
                lang=lang,
                include_plugins=include_plugins,
            )
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
    plugin_translations_loaded = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._translator_initialized = False
        self._plugin_translations_loaded = False
        self.translator = GettextTranslator()
        if not config_path.exists():
            sys_locale = QLocale.system().name()
            settings.language = Language.from_locale(sys_locale)

    @Slot(result=str)
    def get_language(self) -> str:
        return settings.language

    def _apply_language(self, lang: str, *, include_plugins: bool) -> None:
        if lang:
            self.translator.load_translation(lang, include_plugins=include_plugins)
            app.install_translator(self.translator)
            qml_engine.retranslate()
            settings.language = Language.from_locale(lang)
        else:
            app.remove_translator(self.translator)
            settings.language = Language.ENGLISH

    def initialize(self) -> None:
        self._plugin_translations_loaded = False
        self._apply_language(self.get_language(), include_plugins=False)
        if not self._translator_initialized:
            self._translator_initialized = True
            self.translator_initialized.emit()

    @Slot(str)
    def switch_language(self, lang: str) -> None:
        self._plugin_translations_loaded = False
        self._apply_language(lang, include_plugins=True)
        self._plugin_translations_loaded = True
        self.plugin_translations_loaded.emit()
        if not self._translator_initialized:
            self._translator_initialized = True
            self.translator_initialized.emit()

    @Slot()
    def load_plugin_translations(self) -> None:
        if self._plugin_translations_loaded:
            return
        self._apply_language(self.get_language(), include_plugins=True)
        self._plugin_translations_loaded = True
        self.plugin_translations_loaded.emit()
