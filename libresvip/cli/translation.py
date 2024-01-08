import gettext
import locale

from libresvip.core.config import Language, config_path, save_settings, settings
from libresvip.core.constants import PACKAGE_NAME, res_dir


def init_i18n() -> None:
    if not config_path.exists():
        sys_locale = locale.getdefaultlocale()[0]
        settings.language = Language.from_locale(sys_locale or "en_US")
        save_settings()
    locale_name = settings.language.to_locale()
    if (res_dir / "locales" / locale_name).exists():
        gettext.install(PACKAGE_NAME, res_dir / "locales", names=["gettext", "ngettext"])
        gettext.textdomain(PACKAGE_NAME)
        gettext.bindtextdomain(PACKAGE_NAME, res_dir / "locales")
