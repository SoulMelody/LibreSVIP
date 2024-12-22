from bidict import bidict

from libresvip.core.compat import files, json

singer_data_path = files("libresvip.plugins.svip3") / "singers.json"
singers_data = bidict(json.loads(singer_data_path.read_text(encoding="utf-8")))
