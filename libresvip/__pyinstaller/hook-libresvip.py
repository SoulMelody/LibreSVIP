from PyInstaller.utils.hooks import (  # noqa: N999
    collect_data_files,
    collect_submodules,
)

from libresvip.core.constants import pkg_dir

hiddenimports = (
    collect_submodules("libresvip.core")
    + collect_submodules("libresvip.model")
    + collect_submodules("libresvip.utils")
)

datas = [
    (str(pkg_dir / "middlewares"), "libresvip/middlewares"),
    (str(pkg_dir / "plugins"), "libresvip/plugins"),
    *collect_data_files("libresvip", excludes=["__pyinstaller"]),
]
