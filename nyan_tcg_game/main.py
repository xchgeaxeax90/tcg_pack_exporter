import argparse
import logging
import os
import nyan_tcg_game.ods_parser as ods_parser
from nyan_tcg_game.cards import parse_cards
from nyan_tcg_game.image_files import fix_image_files, download_missing_images
from nyan_tcg_game.json_export import export_pack_json
from nyan_tcg_game.crop_gui import crop_images
from nyan_tcg_game.bundles import parse_bundles
from nyan_tcg_game.schemas import BundleType, Pack, NyanCard

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('ods_input', type=str, help="ODS sheet of input data")
    parser.add_argument('export_dir', type=str, help="Directory to export json and images to")
    parser.add_argument('pack_name', type=str, help="The name of the pack edition")
    parser.add_argument('--log-level', type=str, default='INFO', help="Sets log level")
    parser.add_argument('--image-dir', type=str, default='images', help='Path within  export dir to put images into')
    parser.add_argument('--pack-file', type=str, default='pack_data.json', help='File to export card data to in export directory')
    parser.add_argument('--cache-dir', type=str, default='.cache', help='Directory to cache temporary images')
    return parser.parse_args()


def main():
    args = get_args()
    logging.basicConfig(level=args.log_level)

    image_directory = os.path.join(args.export_dir, args.image_dir)
    pack_filename = os.path.join(args.export_dir, args.pack_file)
    download_cache_dir = os.path.join(args.cache_dir, 'downloaded_images')

    # Handle card data

    card_data = ods_parser.read_card_data(args.ods_input)
    cards = parse_cards(card_data)
    cards = download_missing_images(cards, download_cache_dir)
    cards = crop_images(cards, image_directory, args.export_dir)

    # Handle bundles
    def parse_bundle_data():
        bundle_data = ods_parser.read_bundle_data(args.ods_input, BundleType.CARD)
        bundle_data.extend(ods_parser.read_bundle_data(args.ods_input, BundleType.CHARACTER))
        return parse_bundles(bundle_data, cards)

    bundles = parse_bundle_data()

    nyancards = list(map(NyanCard.from_card, cards))

    pack = Pack(name=args.pack_name, cards=nyancards, bundles=bundles)
    export_pack_json(pack, pack_filename)
    





if __name__ == '__main__':
    main()
