from models.Card import Card
from random import shuffle
from typing import Union

class Deck:
    def __init__(self, cards: list) -> None:
        self.cards = cards
        shuffle(self.cards)

    def get_deck_size(self) -> int:
        return len(self.cards)
    
    def draw_card(self) -> Union[Card, None]:
        if self.cards:
            card = self.cards.pop()
            return card
        return None

    def to_state(self) -> dict:
        return {'cards': [card.id for card in self.cards]}

    @classmethod
    def from_state(cls, state: dict) -> 'Deck':
        from DeckManager import DeckManager
        cards = [DeckManager.get_card_by_id(card_id) for card_id in state['cards']]
        shuffle(cards)
        return cls(cards)
