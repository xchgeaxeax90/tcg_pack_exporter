import re
import os
import logging
import urllib.request

invalid_character_selector = re.compile(r'[()\'\"\[\]\{\}]')

logger = logging.getLogger(__name__)

def get_card_filename(card):
    cleaned_name = invalid_character_selector.sub('', card.name)
    logger.debug(cleaned_name)
    filename_prefix = cleaned_name.replace(' ', '_').lower()
    extension = os.path.splitext(card.image_source)[1]
    return filename_prefix + extension


def download_url_for_empty_filename(card, image_dir):
    """For cards with an empty image_url, this function downloads the
    image at the card's image_source url as the card's image data"""
    if card.image_url or (not card.image_source):
        return card

    logger.debug(f'Attempting to fixup {card}')
    image_filename = get_card_filename(card)
    output_filename = os.path.join(image_dir, image_filename)
    if not os.path.exists(output_filename):
        urllib.request.urlretrieve(card.image_source, output_filename)
        logger.info(f'Downloading {card.image_source} as {output_filename}')
    else:
        logger.debug(f'Skipping {output_filename} as it already exists')
    card.image_url = image_filename
    return card

def fix_image_files(cards, image_dir):
    os.makedirs(image_dir, exist_ok=True)
    def run(card):
        return download_url_for_empty_filename(card, image_dir)

    return list(map(run, cards))
