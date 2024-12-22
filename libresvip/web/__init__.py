import os
from multiprocessing import freeze_support

freeze_support()

from libresvip.core.constants import app_dir  # noqa: E402

os.environ.setdefault("NICEGUI_STORAGE_PATH", str(app_dir.user_config_path / ".nicegui"))
