import argparse
import logging
import os
import nyan_tcg_game.ods_parser as ods_parser
from nyan_tcg_game.cards import parse_cards
from nyan_tcg_game.image_files import fix_image_files
from nyan_tcg_game.json_export import export_card_json


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('ods_input', type=str, help="ODS sheet of input data")
    parser.add_argument('export_dir', type=str, help="Directory to export json and images to")
    parser.add_argument('--log-level', type=str, default='INFO', help="Sets log level")
    parser.add_argument('--image-dir', type=str, default='images', help='Path within  export dir to put images into')
    parser.add_argument('--card-file', type=str, default='card_data.json', help='File to export card data to in export directory')
    return parser.parse_args()


def main():
    args = get_args()
    image_directory = os.path.join(args.export_dir, args.image_dir)
    output_filename = os.path.join(args.export_dir, args.card_file)

    logging.basicConfig(level=args.log_level)
    card_data = ods_parser.read_card_data(args.ods_input)
    cards = parse_cards(card_data)
    cards = fix_image_files(cards, image_directory)
    export_card_json(cards, output_filename)




if __name__ == '__main__':
    main()
