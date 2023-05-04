from qmlease import app, slot
from qtpy.QtCore import QObject, QTranslator

from libresvip.core.config import Language, settings
from libresvip.core.constants import pkg_dir


class LocaleSwitcher(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.translator = QTranslator(app)
        self.switch_language(settings.language.to_locale())

    @slot(str)
    def switch_language(self, lang):
        if lang:
            translation_dir = str(pkg_dir / "gui/i18n")
            locale_filename = f"libresvip_{lang}.qm"
            self.translator.load(locale_filename, translation_dir)
            app.installTranslator(self.translator)
            app.engine.retranslate()
            settings.language = Language.from_locale(lang)
        else:
            app.removeTranslator(self.translator)
