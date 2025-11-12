import json
import logging
from pydantic.json import pydantic_encoder
from pydantic import TypeAdapter
from nyan_tcg_game.schemas import NyanCard, Bundle, Pack
logger = logging.getLogger(__name__)


card_adapter = TypeAdapter(list[NyanCard])

def export_card_json(cards, output_filename):
    nyancards = list(map(NyanCard.from_card, cards))
    logger.debug(cards)
    with open(output_filename, 'wb') as f:
        f.write(card_adapter.dump_json(nyancards, indent=2, by_alias=True))


bundle_adapter = TypeAdapter(list[Bundle])

def export_bundle_json(bundles, output_filename):
    logger.debug(bundles)
    with open(output_filename, 'wb') as f:
        f.write(bundle_adapter.dump_json(bundles, indent=2, by_alias=True))


def export_pack_json(pack: Pack, output_filename: str):
    with open(output_filename, 'w') as f:
        f.write(pack.model_dump_json(indent=2, by_alias=True))
