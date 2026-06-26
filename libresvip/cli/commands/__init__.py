__all__ = [
    "conf_app",
    "plugin_app",
    "proj_app",
]

import contextlib

from .conf import app as conf_app
from .plugin import app as plugin_app
from .proj import app as proj_app

with contextlib.suppress(ImportError):
    from .rpc import app as rpc_app

    __all__ += ["rpc_app"]
