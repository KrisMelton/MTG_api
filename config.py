API_URL = "https://api.scryfall.com/bulk-data"
CSV_DIRECTORY = 'resources\Deck_List'
OUTPUT_EXCEL_FILE = 'static\merged_cards_with_totals.xlsx'
COLUMNS_TO_DROP = [
    "id", 'oracle_id', 'multiverse_ids', 'arena_id', 'lang', 'released_at', 'uri', 'scryfall_uri', 'layout', 
    'highres_image', 'image_status', 'image_uris', 'all_parts', 'legalities', 'games', 'reserved', 'foil', 
    'nonfoil', 'oversized', 'promo', 'reprint', 'variation', 'set', 'set_name', 'set_type', 'set_uri', 
    'set_search_uri', 'scryfall_set_uri', 'rulings_uri', 'prints_search_uri', 'collector_number', 'digital', 
    'rarity', 'watermark', 'flavor_text', 'illustration_id', 'card_back_id', 'artist', 'border_color', 'frame', 
    'full_art', 'textless', 'booster', 'story_spotlight', 'edhrec_rank', 'penny_rank', 'related_uris', 
    'purchase_uris'
]
POSTGRESQL = {
    'user': 'postgres',
    'password': 'Fucksql',
    'host': 'localhost',
    'port': '5432',
    'database': 'MTG_db'
}
