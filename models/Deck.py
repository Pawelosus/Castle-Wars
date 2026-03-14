from models.Card import Card
from random import shuffle
from collections import Counter
from typing import Union, Optional

class Deck:
    def __init__(self, cards: list) -> None:
        self.cards = cards
        shuffle(self.cards)

    def get_deck_size(self) -> int:
        return len(self.cards)
    
    def draw_card(self, specific_card: Optional[Card] = None) -> Union[Card, None]:
        if self.cards:
            if specific_card:
                card = self.cards.remove(specific_card)
            else:
                card = self.cards.pop()
            return card
        return None

    def get_draw_distribution(self) -> dict[str, float]:
        """Return a probability distribution over card IDs in the deck."""
        card_counts = Counter(card.id for card in self.cards)
        total = len(self.cards)
        return {card_id: count / total for card_id, count in card_counts.items()}

    def to_state(self) -> dict:
        return {'cards': [card.id for card in self.cards]}

    @classmethod
    def from_state(cls, state: dict) -> 'Deck':
        from DeckManager import DeckManager
        cards = [DeckManager.get_card_by_id(card_id) for card_id in state['cards']]
        shuffle(cards)
        return cls(cards)
