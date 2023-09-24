import csv
import importlib.resources
import io
from gettext import gettext as _


def get_opencpop_dict(dict_name: str, g2p: bool = True) -> dict[str, str]:
    opencpop_dict = {}
    with importlib.resources.path(__package__, "dicts") as dict_dir:
        if (
            dict_content := (dict_dir / f"{dict_name}.txt").read_text(encoding="utf-8")
        ) is None:
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
