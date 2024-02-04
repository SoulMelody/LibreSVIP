import sys

try:
    import ujson as json
except ImportError:
    import json

if sys.implementation.name == "pypy":
    import zstd
else:
    import zstandard as zstd

__all__ = ["Traversable", "as_file", "json", "package_path", "zstd"]

if sys.version_info < (3, 10):
    from importlib_resources import files as package_path
else:
    from importlib.resources import files as package_path

if sys.version_info < (3, 11):
    from importlib_resources.abc import Traversable
else:
    from importlib.resources.abc import Traversable

if sys.version_info < (3, 12):
    from importlib_resources import as_file
else:
    from importlib.resources import as_file
