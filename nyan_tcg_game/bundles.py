from dataclasses import dataclass
from collections import defaultdict
import logging
from nyan_tcg_game.schemas import Bundle, BundleType

logger = logging.getLogger(__name__)

@dataclass
class BundleEntry:
    name: str
    variant: str | None
    bundle_name: str

    @classmethod
    def parse_dict(cls, data: dict):
        return cls(
            name=data['Name'],
            variant=data.get('Variant', None),
            bundle_name=data['Group Name'])

    @property
    def card_name(self):
        return f'{self.name} ({self.variant})' if self.variant else self.name

    

def parse_bundles(ods_data: list[dict], bundle_type: BundleType) -> list[Bundle]:
    bundle_entries = map(BundleEntry.parse_dict, ods_data)

    bundle_dict = defaultdict(list)
    for entry in bundle_entries:
        bundle_dict[entry.bundle_name].append(entry)

    
    bundles = []
    for bundle_name, entries in bundle_dict.items():
        cards = []
        sub_bundles = []
        for entry in entries:
            if entry.card_name in bundle_dict and entry.card_name != bundle_name:
                sub_bundles.append(entry.card_name)
            else:
                cards.append(entry.card_name)
        logger.debug(cards)
        bundles.append(Bundle(name=bundle_name,
                              bundle_type=bundle_type,
                              characters=cards,
                              sub_bundles=sub_bundles))
    return bundles
        
            
    
