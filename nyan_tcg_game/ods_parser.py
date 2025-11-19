from pyexcel_ods import get_data
import itertools
import logging

from nyan_tcg_game.schemas import BundleType

logger = logging.getLogger(__name__)

def read_sheet(filename, sheet_name):
    data = get_data(filename)
    try:
        return data[sheet_name]
    except KeyError:
        logger.warn(f"Could not find \"{sheet_name}\" in spreadsheet, returning empty list")
        return []

def convert_to_row_dict(data):
    if data:
        header_row = data[0]
        def cleanup_row(row):
            return map(lambda x: None if x == '' else x, row)
        return [dict(itertools.zip_longest(header_row, cleanup_row(row), fillvalue=None)) for row in data[1:]]
    return []

def read_card_data(filename):
    return convert_to_row_dict(read_sheet(filename, 'Cards'))

def read_bundle_data(filename, bundle_type: BundleType):
    if bundle_type == BundleType.CHARACTER:
        data = read_sheet(filename, 'Character Groups')
    elif bundle_type == BundleType.CARD:
        data = read_sheet(filename, 'Card Groups')
    elif bundle_type == BundleType.BUNDLE:
        data = read_sheet(filename, 'Bundle Groups')
    else:
        return None
    data = convert_to_row_dict(data)
    data = [{'bundle_type': bundle_type, **d} for d in data]
    return data
