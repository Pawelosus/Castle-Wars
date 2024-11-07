import json
from models.Card import Card
from random import shuffle
from pathlib import Path
from typing import Union

class Deck:
    def __init__(self, deck_file: Union[str, Path] = 'default_deck.json') -> None:
        self.cards = self.init_deck(deck_file)

    def init_deck(self, deck_file: Union[str, Path]) -> list:
        """Init deck with default deck."""
        deck_dir = Path(__file__).parent.parent / 'resources' / 'decks'
        deck_path = deck_dir / deck_file
        
        # Load the deck configuration
        try:
            with open(deck_path) as f:
                deck_dict = json.load(f)
        except FileNotFoundError:
            raise ValueError(f'Deck file "{deck_path}" not found.')
        
        deck = []

        # Load base card info
        cards_path = Path(__file__).parent.parent / 'resources' / 'cards.json'
        try:
            with open(cards_path) as f:
                cards_data = json.load(f)
        except FileNotFoundError:
            raise ValueError(f'Card data file "{cards_path}" not found.')

        # Initialize cards based on deck configuration
        for card_id, count in deck_dict.items():
            material_type, index = card_id.split(':')
            card_info = cards_data[material_type][int(index)]
            for _ in range(count):
                card = Card(
                    card_id,
                    material_type,
                    card_info['cost'],
                    card_info['name'],
                    card_info['effect']
                )
                deck.append(card)

        shuffle(deck)  # Using the built-in random.shuffle function
        return deck

    def get_deck_size(self) -> int:
        return len(self.cards)
    
    def draw_card(self) -> Union[Card, None]:
        if self.cards:
            card = self.cards.pop(0)
            return card
        else:
            return None
