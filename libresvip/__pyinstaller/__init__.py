from libresvip.core.constants import pkg_dir


def get_hook_dirs() -> list[str]:
    return [str(pkg_dir / "__pyinstaller")]
