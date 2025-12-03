import re
import os
import shutil
import logging
import urllib.request

invalid_character_selector = re.compile(r'[()\'\"\[\]\{\}]')

logger = logging.getLogger(__name__)


def download_url_for_empty_filename(card, image_dir):
    """For cards with an empty image_url, this function downloads the
    image at the card's image_source url as the card's image data"""
    if not card.image_file_uri:
        logger.error(f"Cannot find image file for card {card}")
        return card

    logger.debug(f'Attempting to fixup {card}')
    image_filename = card.get_image_filename('.png')
    output_filename = os.path.join(image_dir, image_filename)
    if not os.path.exists(output_filename):
        logger.info(f'Downloading {card.image_file_uri} as {output_filename}')
        if 'pximg' in card.image_file_uri or 'pixiv' in card.image_file_uri:
            logger.info(f"Adding pixiv specific headers the request for {output_filename}")
            opener = urllib.request.build_opener()
            opener.addheaders = [('referer', 'https://www.pixiv.net/')]
            urllib.request.install_opener(opener)
        else:
            urllib.request.install_opener(None)

        try:
            urllib.request.urlretrieve(card.image_file_uri, output_filename)
        except Exception as e:
            logger.error(f'Error downloading {card.image_file_uri}: {e}')
            raise e
    else:
        logger.debug(f'Skipping {output_filename} as it already exists')
    card.local_image_path = output_filename
    return card

def download_missing_images(cards, download_dir):
    os.makedirs(download_dir, exist_ok=True)
    return list(map(lambda c: download_url_for_empty_filename(c, download_dir), cards))

def fix_image_files(cards, image_dir):
    os.makedirs(image_dir, exist_ok=True)
    def run(card):
        return download_url_for_empty_filename(card, image_dir)

    return list(map(run, cards))
