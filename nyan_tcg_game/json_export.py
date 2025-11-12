import json
import logging
from pydantic.json import pydantic_encoder
from nyan_tcg_game.schemas import NyanCard, Bundle
logger = logging.getLogger(__name__)




def export_card_json(cards, output_filename):
    nyancards = list(map(NyanCard.from_card, cards))
    logger.debug(cards)
    with open(output_filename, 'w') as f:
        json.dump(nyancards, f, default=pydantic_encoder, indent=2)


def export_bundle_json(bundles, output_filename):
    logger.debug(bundles)
    with open(output_filename, 'w') as f:
        json.dump(bundles, f, default=pydantic_encoder, indent=2)
