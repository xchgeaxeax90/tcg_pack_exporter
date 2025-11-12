import json
import logging
from pydantic.json import pydantic_encoder
logger = logging.getLogger(__name__)

def export_card_json(cards, output_filename):
    logger.debug(cards)
    with open(output_filename, 'w') as f:
        json.dump(cards, f, default=pydantic_encoder, indent=2)
