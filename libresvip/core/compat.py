import sys

try:
    import ujson as json
except ImportError:
    import json

try:
    import pyzstd as zstd
except ImportError:
    try:
        import numcodecs.zstd as zstd
    except ImportError:
        import zstandard as zstd

__all__ = ["Traversable", "as_file", "files", "json", "zstd"]

if sys.version_info < (3, 10):
    from importlib_resources import as_file, files
else:
    from importlib.resources import as_file, files

if sys.version_info < (3, 11):
    from importlib_resources.abc import Traversable
else:
    from importlib.resources.abc import Traversable
