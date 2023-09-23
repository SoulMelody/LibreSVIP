import csv
import importlib.resources
import io
from gettext import gettext as _


def get_opencpop_dict(dict_name: str, g2p: bool = True) -> dict[str, str]:
    opencpop_dict = {}
    resource_path = importlib.resources(__package__, f"dicts/{dict_name}.txt")
    if (dict_content := resource_path.read_text(encoding="utf-8")) is None:
        msg = _("Cannot find dict.")
        raise FileNotFoundError(msg)
    reader = csv.DictReader(
        io.StringIO(dict_content), delimiter="\t", fieldnames=["pinyin", "phone"]
    )
    for row in reader:
        if g2p:
            opencpop_dict[row["pinyin"]] = row["phone"]
        else:
            opencpop_dict[row["phone"]] = row["pinyin"]
    return opencpop_dict
