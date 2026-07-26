from importlib.resources import files

from libresvip.core.constants import PACKAGE_NAME


def get_hook_dirs() -> list[str]:
    return [str(files(PACKAGE_NAME) / "__pyinstaller")]
