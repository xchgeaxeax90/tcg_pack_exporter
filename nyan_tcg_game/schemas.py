from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from nyan_tcg_game.cards import Card, Rarity
   

class NyanCard(BaseModel):
    name: str
    subtext: str
    character: str
    image_url: str | None
    image_credit: str | None
    image_source: str | None
    rarity: Rarity

    @classmethod
    def from_card(cls, card):
        return cls(
            name=card.get_card_name(),
            subtext=card.company,
            character=card.name,
            rarity=card.rarity,
            image_url=card.resized_uri,
            image_credit=card.image_credit,
            image_source=card.image_fetch_url)


class BundleType(str, Enum):
    CHARACTER = 'character'
    CARD = 'card'

class Bundle(BaseModel):
    name: str
    bundle_type: BundleType = Field(..., alias='type')
    characters: list[str]
    sub_bundles: list[str]
    model_config = ConfigDict(populate_by_name=True)
