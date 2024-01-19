import sys

try:
    import ujson as json
except ImportError:
    import json

try:
    import zstandard as zstd
except ImportError:
    import zstd

__all__ = ["json", "package_path", "zstd"]

if sys.version_info < (3, 10):
    from importlib_resources import files as package_path
else:
    from importlib.resources import files as package_path
