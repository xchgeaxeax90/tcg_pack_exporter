import sqlite3
from nyan_tcg_game.schemas import Pack
from prettytable import PrettyTable

db = sqlite3.connect(":memory:")
#db = sqlite3.connect("stats.db")

def create_db():
    db.execute('CREATE TABLE cards (name text, character text, subtext text, rarity text);')
    db.execute('CREATE TABLE bundles (bundle_name text PRIMARY KEY);')
    db.execute('''CREATE TABLE card_bundles (bundle_name text, card_name text,
    FOREIGN KEY(bundle_name) REFERENCES bundles(bundle_name),
    FOREIGN KEY(card_name) REFERENCES cards(name));''')
    db.execute('''CREATE TABLE character_bundles (bundle_name text, character_name text,
    FOREIGN KEY(bundle_name) REFERENCES bundles(bundle_name),
    FOREIGN KEY(character_name) REFERENCES cards(character));''')
    db.execute('CREATE VIEW characters(character) AS SELECT DISTINCT(character) FROM cards;')
def populate_db(pack: Pack):
    with db:
        db.executemany('INSERT INTO cards (name, character, subtext, rarity) VALUES (?, ?, ?, ?);',
                    [(card.name, card.character, card.subtext, card.rarity) for card in pack.cards])
        for bundle in pack.bundles:
            db.execute('INSERT INTO bundles (bundle_name) VALUES (?);', (bundle.name, ))
            db.executemany('INSERT INTO card_bundles (bundle_name, card_name) VALUES (?, ?);',
                        [(bundle.name, card) for card in bundle.cards])
            db.executemany('INSERT INTO character_bundles (bundle_name, character_name) VALUES (?, ?);',
                        [(bundle.name, character) for character in bundle.characters])
    

def print_bundle_membership(stats_fp):
    results = db.execute('''
    SELECT characters.character as character,
       COUNT(DISTINCT character_bundles.bundle_name) + COUNT(DISTINCT card_bundles.bundle_name) as total_bundles,
       COUNT(DISTINCT character_bundles.bundle_name) as num_character_bundles,
       COUNT(DISTINCT card_bundles.bundle_name) as num_card_bundles
    FROM characters
        LEFT JOIN character_bundles ON characters.character = character_bundles.character_name
        LEFT JOIN cards ON cards.character = characters.character
        LEFT JOIN card_bundles ON cards.name = card_bundles.card_name
    WHERE cards.character IS NOT NULL
    GROUP BY characters.character ;
    ''').fetchall()
    stats_fp.write('Number of bundles per character:\n')
    table = PrettyTable()
    table.field_names = ["Character Name", "Total", "Char", "Card"]
    for row in results:
        table.add_row(row)
    stats_fp.write(str(table))
    stats_fp.write('\n')

def print_character_rarities(stats_fp):
    results = db.execute('''
    SELECT ch.character,
    SUM(CASE WHEN ca.rarity = 'Common' THEN 1 ELSE 0 END) as common_count,
    SUM(CASE WHEN ca.rarity = 'Rare' THEN 1 ELSE 0 END) as rare_count,
    SUM(CASE WHEN ca.rarity = 'Special Rare' THEN 1 ELSE 0 END) as special_rare_count
    FROM characters ch
    LEFT JOIN cards ca ON ca.character = ch.character
    WHERE ch.character IS NOT NULL
    GROUP BY ch.character ORDER BY ch.character''').fetchall()
    stats_fp.write('Rarities per character:\n')
    table = PrettyTable()
    table.field_names = ["Character Name", "C", "R", "SR"]
    for row in results:
        table.add_row(row)
    stats_fp.write(str(table))
    stats_fp.write('\n')
    
def print_subtexts(stats_fp):
    results = db.execute('''
    SELECT cards.subtext, COUNT(DISTINCT cards.character), COUNT(*) FROM cards
    WHERE cards.subtext IS NOT NULL
    GROUP BY cards.subtext;
    ''').fetchall()
    stats_fp.write('Subtext/Company counts:\n')
    table = PrettyTable()
    table.field_names = ["Subtext", "Characters", "Cards"]
    for row in results:
        table.add_row(row)
    stats_fp.write(str(table))
    stats_fp.write('\n')

def print_totals(stats_fp):
    results = db.execute('''
    SELECT COUNT(*), COUNT(DISTINCT cards.character) FROM cards;''').fetchone()
    bundle_results = db.execute('''
    SELECT COUNT(*) FROM bundles;''').fetchone()

    stats_fp.write("Totals:\n")
    table = PrettyTable()
    table.field_names = ["Item", "Total"]
    table.add_row(["Cards", results[0]])
    table.add_row(["Characters", results[1]])
    table.add_row(["Bundles", bundle_results[0]])
    stats_fp.write(str(table))
    stats_fp.write("\n")
    

def generate_stats(pack: Pack, stats_file: str):
    create_db()
    populate_db(pack)
    with open(stats_file, 'w') as f:
        print_bundle_membership(f)
        f.write('\n\n')
        print_character_rarities(f)
        f.write('\n\n')
        print_subtexts(f)
        f.write('\n\n')
        print_totals(f)
