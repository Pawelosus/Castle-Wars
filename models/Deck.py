from models.Card import Card
from random import shuffle
from typing import Union

class Deck:
    def __init__(self, cards: list) -> None:
        self.cards = cards

    def get_deck_size(self) -> int:
        return len(self.cards)
    
    def draw_card(self) -> Union[Card, None]:
        if self.cards:
            return self.cards.pop(0)
        return None

    def shuffle(self) -> None:
        shuffle(self.cards)
