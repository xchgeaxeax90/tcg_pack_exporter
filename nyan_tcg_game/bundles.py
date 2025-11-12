from dataclasses import dataclass
from collections import defaultdict
import logging
from nyan_tcg_game.schemas import Bundle, BundleType
from nyan_tcg_game.cards import Card

logger = logging.getLogger(__name__)

@dataclass
class BundleEntry:
    name: str
    variant: str | None
    bundle_name: str
    bundle_type: BundleType

    @classmethod
    def parse_dict(cls, data: dict):
        return cls(
            name=data['Name'],
            variant=data.get('Variant', None),
            bundle_name=data['Group Name'],
            bundle_type=data['bundle_type'])

    @property
    def card_name(self):
        return f'{self.name} ({self.variant})' if self.variant else self.name

    

def parse_bundles(ods_data: list[dict],
                  cards: list[Card]) -> list[Bundle]:
    bundle_entries = map(BundleEntry.parse_dict, ods_data)

    bundle_dict = defaultdict(list)
    for entry in bundle_entries:
        bundle_dict[entry.bundle_name].append(entry)

    valid_characters = set(map(lambda x: x.name, cards))
    valid_cards = set(map(lambda x: x.card_name, cards))

    
    bundles = []
    for bundle_name, entries in bundle_dict.items():
        cards = []
        characters = []
        sub_bundles = []
        for entry in entries:
            if entry.bundle_type == BundleType.CARD and entry.card_name in valid_cards:
                cards.append(entry.card_name)
            elif entry.bundle_type == BundleType.CHARACTER and entry.name in valid_characters:
                characters.append(entry.card_name)
        logger.debug(cards)
        if cards or characters or sub_bundles:
            bundles.append(Bundle(name=bundle_name,
                                #bundle_type=BundleType.CHARACTER,
                                characters=characters,
                                cards=cards,
                                sub_bundles=sub_bundles))
    return bundles
        
            
    
