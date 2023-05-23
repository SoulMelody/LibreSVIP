import os

from qmlease import app
from qtpy.QtQuickControls2 import QQuickStyle

from libresvip.core.constants import pkg_dir
from libresvip.gui.modules import (
    Clipboard,
    ConfigItems,
    FontLoader,
    LocaleSwitcher,
    Notifier,
    TaskManager,
)

os.environ["QT_QUICK_CONTROLS_MATERIAL_VARIANT"] = "Dense"
QQuickStyle.setStyle("Material")
app.set_app_name("LibreSVIP")
app.set_app_icon(str((pkg_dir / "libresvip.ico").resolve()))
config_items = ConfigItems()
task_manager = TaskManager()
config_items.auto_set_output_extension_changed.connect(task_manager.reset_output_ext)
app.register(Clipboard(), name="clipboard")
app.register(config_items, name="config_items")
app.register(FontLoader(), name="qta")
app.register(LocaleSwitcher(), name="locale")
app.register(Notifier(), name="notifier")
app.register(task_manager, name="task_manager")
app.register_qmldir(
    pkg_dir / "gui" / "components",
)
app.run(
    pkg_dir / "gui" / "main.qml",
    # debug=True
)
