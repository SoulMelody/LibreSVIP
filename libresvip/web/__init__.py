import os

from libresvip.core.constants import app_dir

os.environ.setdefault("NICEGUI_STORAGE_PATH", str(app_dir.user_config_path / ".nicegui"))
