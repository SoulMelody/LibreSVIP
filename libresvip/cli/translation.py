import gettext

from libresvip.core.config import settings
from libresvip.core.constants import PACKAGE_NAME, res_dir


def init_i18n():
    gettext.install(
        PACKAGE_NAME, res_dir / "locales", names=[settings.language.to_locale()]
    )
    gettext.textdomain(PACKAGE_NAME)
    gettext.bindtextdomain(PACKAGE_NAME, res_dir / "locales")
