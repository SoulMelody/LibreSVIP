import os

from lk_utils import relpath
from qmlease import app
from qtpy.QtQuickControls2 import QQuickStyle

from .modules import (
    Clipboard,
    ConfigItems,
    FileOperations,
    FontLoader,
    LocaleSwitcher,
    TaskManager,
)

os.environ["QT_QUICK_CONTROLS_MATERIAL_VARIANT"] = "Dense"
QQuickStyle.setStyle("Material")
app.set_app_name("LibreSVIP")
app.register(Clipboard(), name="clipboard")
app.register(ConfigItems(), name="config_items")
app.register(FileOperations(), name="file_operations")
app.register(FontLoader(), name="qta")
app.register(LocaleSwitcher(), name="locale")
app.register(TaskManager(), name="task_manager")
app.register_qmldir(relpath("components"))
app.run(relpath("main.qml"), debug=True)
