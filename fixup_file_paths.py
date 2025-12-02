import pyexcel
import argparse
from urllib.parse import urlparse
from pathlib import Path
import os
import shutil

parser = argparse.ArgumentParser('fixup_file_paths')
parser.add_argument('input_sheet')
parser.add_argument('output_sheet')
parser.add_argument('export_directory')

args = parser.parse_args()

books = pyexcel.get_book(file_name=args.input_sheet)

def fixup_filename(filename, export_dir):
    uri = urlparse(filename)
    if uri.scheme == 'file':
        p = Path(uri.path)
        if p.is_relative_to(export_dir):
            return filename
        new_filename = Path(export_dir) / p.name
        shutil.copy(p, new_filename)
        return uri._replace(path=str(new_filename)).geturl()

    return filename
    

def fixup_files(sheet, export_dir):
    os.makedirs(export_dir, exist_ok=True)
    sheet.name_columns_by_row(0)
    idx = sheet.colnames.index("File URI")
    file_col = sheet.column[idx]

    fixed_file_col = [fixup_filename(f, export_dir) for f in file_col]
    sheet.column[idx] = fixed_file_col

fixup_files(books.Cards, args.export_directory)
books.save_as(args.output_sheet)
    
