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
from nyan_tcg_game.card_preview import generate_previews
from nyan_tcg_game.stats import generate_stats

PACK_FILE = 'pack_data.json'
STATS_FILE = 'pack_stats.txt'
IMAGE_DIR = 'images'
DOWNLOAD_CACHE_DIR = 'downloaded_images'


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('ods_input', type=str, help="ODS sheet of input data")
    parser.add_argument('export_dir', type=str, help="Directory to export json and images to")
    parser.add_argument('pack_name', type=str, help="The name of the pack edition")
    parser.add_argument('--log-level', type=str, default='INFO', help="Sets log level")
    parser.add_argument('--cache-dir', type=str, default='.cache', help='Directory to cache temporary images')
    parser.add_argument('-p', '--preview', action='store_true', help='Preview card frames')
    return parser.parse_args()


def main():
    args = get_args()
    logging.basicConfig(level=args.log_level)
    #logging.getLogger("nyan_tcg_game.crop_gui").setLevel(logging.DEBUG)

    image_directory = os.path.join(args.export_dir, IMAGE_DIR)
    pack_filename = os.path.join(args.export_dir, PACK_FILE)
    stats_filename = os.path.join(args.export_dir, STATS_FILE)
    download_cache_dir = os.path.join(args.cache_dir, DOWNLOAD_CACHE_DIR)

    # Handle card data

    card_data = ods_parser.read_card_data(args.ods_input)
    cards = parse_cards(card_data)
    cards = download_missing_images(cards, download_cache_dir)
    cards = crop_images(cards, image_directory, args.export_dir)

    # Handle bundles
    def parse_bundle_data():
        bundle_data = ods_parser.read_bundle_data(args.ods_input, BundleType.CARD)
        bundle_data.extend(ods_parser.read_bundle_data(args.ods_input, BundleType.CHARACTER))
        bundle_data.extend(ods_parser.read_bundle_data(args.ods_input, BundleType.BUNDLE))
        return parse_bundles(bundle_data, cards)

    bundles = parse_bundle_data()

    nyancards = list(map(NyanCard.from_card, cards))

    pack = Pack(name=args.pack_name, cards=nyancards, bundles=bundles)
    export_pack_json(pack, pack_filename)
    generate_stats(pack, stats_filename)
    
    if args.preview:
        preview_dir = os.path.join(args.export_dir, "previews")
        generate_previews(cards, args.export_dir, preview_dir)





if __name__ == '__main__':
    main()
