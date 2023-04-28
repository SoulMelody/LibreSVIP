from qmlease import app, slot
from qtpy.QtCore import QObject, QTranslator

from libresvip.core.config import Language, settings
from libresvip.core.constants import pkg_dir


class LocaleSwitcher(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.translator = QTranslator(app)
        app.engine.retranslate()

    @slot(str)
    def switch_language(self, lang):
        if lang:
            self.translator.load(str(pkg_dir / "/gui/i18n/{lang}.qm"))
            app.installTranslator(self.translator)
            app.engine.retranslate()
            settings.language = Language.from_locale(lang)
        else:
            app.removeTranslator(self.translator)
