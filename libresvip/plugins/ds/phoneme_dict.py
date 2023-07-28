import csv
import io
import pkgutil
from gettext import gettext as _


def get_opencpop_dict(dict_name: str, g2p: bool = True) -> dict[str, str]:
    opencpop_dict = {}
    if (dict_content := pkgutil.get_data(__package__, f'dicts/{dict_name}.txt')) is None:
        msg = _('Cannot find dict.')
        raise FileNotFoundError(msg)
    reader = csv.DictReader(
        io.StringIO(dict_content.decode('utf-8')),
        delimiter='\t', fieldnames=['pinyin', 'phone']
    )
    for row in reader:
        if g2p:
            opencpop_dict[row['pinyin']] = row['phone']
        else:
            opencpop_dict[row['phone']] = row['pinyin']
    return opencpop_dict
