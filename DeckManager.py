import json
from pathlib import Path
from typing import Union, Dict, Optional
from models.Deck import Deck
from models.Card import Card

class DeckManager:
    _card_cache: Optional[list[Card]] = None
    _card_lookup: dict[str, Card] = {}

    @staticmethod
    def _load_json(file_path: Path) -> Dict:
        """Helper function to load JSON data from a file."""
        try:
            with open(file_path) as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f'File "{file_path}" not found.')

    @staticmethod
    def _get_cards_data() -> Dict:
        """Loads the base card data from cards.json."""
        cards_path = Path(__file__).parent / 'resources' / 'cards.json'
        return DeckManager._load_json(cards_path)

    @staticmethod
    def _create_card(card_id: str, card_info: Dict) -> Card:
        """Helper function to create a Card object from card ID and card information."""
        material_type, index = card_id.split(':')
        return Card(
            card_id,
            material_type,
            card_info['cost'],
            card_info['name'],
            card_info['effect']
        )

    @staticmethod
    def get_card_by_id(card_id: str) -> Card:
        """Fetches a Card object using its ID from the base card data."""
        if DeckManager._card_cache is None:
            DeckManager.load_all_cards()
        return DeckManager._card_lookup[card_id]

    @staticmethod
    def load_all_cards() -> list[Card]:
        """Loads all cards from cards.json and returns a list of Card objects."""
        if DeckManager._card_cache is not None:
            return DeckManager._card_cache

        cards_data = DeckManager._get_cards_data()
        all_cards = []

        for material_type, card_list in cards_data.items():
            for index, card_info in enumerate(card_list):
                card_id = f"{material_type}:{index}"
                card = DeckManager._create_card(card_id, card_info)
                all_cards.append(card)
                DeckManager._card_lookup[card_id] = card

        DeckManager._card_cache = all_cards
        return all_cards

    @staticmethod
    def load_deck(deck_file: Union[str, Path]) -> Deck:
        """Loads a deck from a file and returns a Deck object."""
        deck_dir = Path(__file__).parent / 'resources' / 'decks'
        deck_path = deck_dir / deck_file

        # Check if the deck file exists, fallback to default_deck.json if not
        if not deck_path.exists():
            print(f"Warning: Deck file '{deck_file}' not found. Using 'default_deck.json' instead.")
            deck_path = deck_dir / 'default_deck.json'

        # Load the deck configuration
        deck_dict = DeckManager._load_json(deck_path)
        cards_data = DeckManager._get_cards_data()

        deck = []

        # Initialize cards based on deck configuration
        for card_id, count in deck_dict.items():
            card_info = cards_data[card_id.split(':')[0]][int(card_id.split(':')[1])]
            for _ in range(count):
                card = DeckManager._create_card(card_id, card_info)
                deck.append(card)

        deck_obj = Deck(deck)
        return deck_obj

    @staticmethod
    def save_deck(deck_dict: dict, deck_file: Union[str, Path]) -> None:
        """Saves the deck configuration to a file."""
        deck_dir = Path(__file__).parent / 'resources' / 'decks'
        deck_path = deck_dir / deck_file

        # Save the dictionary to a JSON file
        try:
            with open(deck_path, 'w') as f:
                json.dump(deck_dict, f, indent=4)
            print(f'Deck successfully saved to "{deck_path}".')
        except Exception as e:
            print(f'Error saving deck: {e}')
