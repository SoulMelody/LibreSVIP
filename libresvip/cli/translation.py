import gettext

from libresvip.core.config import settings
from libresvip.core.constants import PACKAGE_NAME, res_dir


def init_i18n():
    locale_name = settings.language.to_locale()
    if (res_dir / "locales" / locale_name).exists():
        gettext.install(PACKAGE_NAME, res_dir / "locales", names=["gettext", "ngettext"])
        gettext.textdomain(PACKAGE_NAME)
        gettext.bindtextdomain(PACKAGE_NAME, res_dir / "locales")
