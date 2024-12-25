from PyInstaller.utils.hooks import (  # noqa: N999
    collect_data_files,
    collect_submodules,
)

hiddenimports = (
    collect_submodules("libresvip.core")
    + collect_submodules("libresvip.model")
    + collect_submodules("libresvip.utils")
)

datas = (
    collect_data_files("libresvip.middlewares", include_py_files=True, excludes=["**/*.po"])
    + collect_data_files("libresvip.plugins", include_py_files=True, excludes=["**/*.po"])
    + collect_data_files(
        "libresvip.res", excludes=["**/*.po", "**/*.qml", "**/*.qrc", "**/*.ts", "**/qmldir"]
    )
)
