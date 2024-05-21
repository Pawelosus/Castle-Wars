import json
from models.Card import Card
from random import shuffle
from typing import Union

class Deck:
    def __init__(self) -> None:
        self.cards = self.init_deck()

    def init_deck(self) -> list:
        """Init deck with default deck."""
        with open('resources/decks/default_deck.json') as f:
            deck_dict = json.load(f)
        
        deck = list()
        with open('resources/cards.json') as f:
            cards_data = json.load(f)
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
