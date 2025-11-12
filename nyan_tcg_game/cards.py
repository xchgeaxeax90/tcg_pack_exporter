from nyan_tcg_game.schemas import Card, Rarity

def dict_to_card(data):
    if not data['Rarity']:
        return None
    if data['Variant']:
        name = f"{data['Name']} ({data['Variant']})"
    else:
        name = data['Name']

    subtext = data['Company']
    character = data['Name']
    rarity = Rarity(data['Rarity'])
    image_url = data['Filename']
    image_credit = data['Credit']
    image_source = data['URL']
    

    return Card(name=name,
                subtext=subtext,
                character=character,
                rarity=rarity,
                image_url=image_url,
                image_credit=image_credit,
                image_source=image_source)

def parse_cards(data):
    return filter(None, map(dict_to_card, data))
