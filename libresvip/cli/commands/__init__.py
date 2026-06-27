__all__ = [
    "conf_app",
    "plugin_app",
    "proj_app",
    "rpc_app",
]

from .conf import app as conf_app
from .plugin import app as plugin_app
from .proj import app as proj_app
from .rpc import app as rpc_app
