import csv
import pathlib


def get_opencpop_dict(dict_name: str) -> dict:
    dict_path = pathlib.Path(__file__).parent / 'dicts' / f'{dict_name}.txt'
    with open(dict_path) as f:
        opencpop_dict = {}
        reader = csv.DictReader(f, delimiter='\t', fieldnames=['pinyin', 'phone'])
        for row in reader:
            opencpop_dict[row['phone']] = row['pinyin']
        return opencpop_dict
