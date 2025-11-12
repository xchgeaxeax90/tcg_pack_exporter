from pydantic import BaseModel, Field
from enum import Enum

class Rarity(str, Enum):
    COMMON = 'Common'
    RARE = 'Rare'
    SPECIAL_RARE = 'SpecialRare'
   

class Card(BaseModel):
    name: str
    subtext: str
    character: str
    image_url: str
    image_credit: str
    image_source: str
    rarity: Rarity


class BundleType(str, Enum):
    CHARACTER = 'character'
    CARD = 'card'

class Bundle(BaseModel):
    name: str
    bundle_type: BundleType = Field(..., alias='type')
    characters: list[str]
    sub_bundles: list[str]
