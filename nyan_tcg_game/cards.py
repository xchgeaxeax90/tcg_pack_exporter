from dataclasses import dataclass
from enum import Enum
import re

invalid_character_selector = re.compile(r'[()\'\"\[\]\{\}]')


class Rarity(str, Enum):
    COMMON = 'Common'
    RARE = 'Rare'
    SPECIAL_RARE = 'Special Rare'

    @property
    def short_name(self):
        if self == self.COMMON:
            return "C"
        elif self == self.RARE:
            return "R"
        return "SR"

@dataclass
class Card:
    name: str
    variant: str | None
    company: str
    rarity: Rarity
    image_credit: str
    source_url: str | None # Stores the source link for the image - the tweet or webpage it came from
    image_file_uri: str | None # Stores the image file location as a URI
    local_image_path: str | None # Once an image has been fetched from the image file URI, its path is stored here
    resized_uri: str | None # Stores the image path after it has been resized

    @property
    def card_name(self):
        return f'{self.name} ({self.variant})' if self.variant else self.name

    def get_image_filename(self, suffix) -> str:
        filename = f'{self.name}_{self.variant}' if self.variant else self.name
        cleaned_name = invalid_character_selector.sub('', filename)
        cleaned_name = cleaned_name.replace(' ', '_').lower()
        return cleaned_name + suffix

def dict_to_card(data):
    if not data['Rarity']:
        return None
    if data['Variant']:
        name = f"{data['Name']} ({data['Variant']})"
    else:
        name = data['Name']

    return Card(
        name=data['Name'],
        variant=data['Variant'],
        company=data['Company'],
        rarity=Rarity(data['Rarity']),
        image_credit=data['Credit'],
        source_url=data['Source URL'],
        image_file_uri=data['File URI'],
        local_image_path=None,
        resized_uri=None)

def parse_cards(data):
    return filter(None, map(dict_to_card, data))
