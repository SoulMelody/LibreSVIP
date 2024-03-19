from bidict import bidict

from libresvip.core.compat import json, package_path

singer_data_path = package_path("libresvip.plugins.svip3") / "singers.json"
singers_data = bidict(json.loads(singer_data_path.read_text(encoding="utf-8")))
