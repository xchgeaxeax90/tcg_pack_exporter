from pyexcel_ods import get_data
from nyan_tcg_game.schemas import BundleType
import itertools

def read_sheet(filename, sheet_name):
    data = get_data(filename)
    return data[sheet_name]

def convert_to_row_dict(data):
    header_row = data[0]
    def cleanup_row(row):
        return map(lambda x: None if x == '' else x, row)
    return [dict(itertools.zip_longest(header_row, cleanup_row(row), fillvalue=None)) for row in data[1:]]

def read_card_data(filename):
    return convert_to_row_dict(read_sheet(filename, 'Cards'))

def read_bundle_data(filename, bundle_type: BundleType):
    if bundle_type == BundleType.CHARACTER:
        return convert_to_row_dict(read_sheet(filename, 'Character Groups'))
    elif bundle_type == BundleType.CARD:
        return convert_to_row_dict(read_sheet(filename, 'Card Groups'))
    return None
