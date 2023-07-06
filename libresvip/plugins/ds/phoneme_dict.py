import csv
import io
import pkgutil


def get_opencpop_dict(dict_name: str, g2p: bool = True) -> dict:
    dict_content = pkgutil.get_data(__package__, f'dicts/{dict_name}.txt')
    opencpop_dict = {}
    reader = csv.DictReader(
        io.BytesIO(dict_content),
        delimiter='\t', fieldnames=['pinyin', 'phone']
    )
    for row in reader:
        if g2p:
            opencpop_dict[row['pinyin']] = row['phone']
        else:
            opencpop_dict[row['phone']] = row['pinyin']
    return opencpop_dict
