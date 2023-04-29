import os

from lk_utils import relpath
from qmlease import app
from qtpy.QtQuickControls2 import QQuickStyle

from .modules import (
    Clipboard,
    ConfigItems,
    FontLoader,
    LocaleSwitcher,
    TaskManager,
)

os.environ["QT_QUICK_CONTROLS_MATERIAL_VARIANT"] = "Dense"
QQuickStyle.setStyle("Material")
app.set_app_name("LibreSVIP")
# app.set_app_icon
config_items = ConfigItems()
task_manager = TaskManager()
config_items.auto_set_output_extension_changed.connect(task_manager.reset_output_ext)
app.register(Clipboard(), name="clipboard")
app.register(config_items, name="config_items")
app.register(FontLoader(), name="qta")
app.register(LocaleSwitcher(), name="locale")
app.register(task_manager, name="task_manager")
app.register_qmldir(relpath("components"))
app.run(relpath("main.qml"), debug=True)
