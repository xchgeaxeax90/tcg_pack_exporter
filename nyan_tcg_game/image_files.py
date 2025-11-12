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
    if card.source_uri or (not card.image_fetch_url):
        return card

    logger.debug(f'Attempting to fixup {card}')
    image_filename = card.get_image_filename('.png')
    output_filename = os.path.join(image_dir, image_filename)
    if not os.path.exists(output_filename):
        logger.info(f'Downloading {card.image_fetch_url} as {output_filename}')
        try:
            urllib.request.urlretrieve(card.image_fetch_url, output_filename)
        except Exception as e:
            logger.error(f'Error downloading {card.image_fetch_url}: {e}')
            raise e
    else:
        logger.debug(f'Skipping {output_filename} as it already exists')
    card.source_uri = image_filename
    return card

def copy_existing_filename(card, image_dir):
    """For cards with an image_url (that's the filename) set, this
    fixes the name to the format nyan specifies and copies it into the
    export directory"""
    if not card.source_uri:
        return card
    image_filename = card.get_image_filename('.png')
    output_filename = os.path.join(image_dir, image_filename)
    logger.debug(f'Copying {card.source_uri} to {output_filename}')
    shutil.copy(card.source_uri, output_filename)
    card.image_url = image_filename
    return card
    

def fix_image_files(cards, image_dir):
    os.makedirs(image_dir, exist_ok=True)
    def run(card):
        card = copy_existing_filename(card, image_dir)
        return download_url_for_empty_filename(card, image_dir)

    return list(map(run, cards))
