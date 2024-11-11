from models.AIPlayer import AIPlayer
from models.Card import Card
from numpy.random import randint
from typing import Tuple, Union
from pathlib import Path

class BasicAIPlayer(AIPlayer):
    def __init__(self, name: str, preferred_deck_file: Union[str, Path] = 'default_deck.json') -> None:
        super().__init__(name, preferred_deck_file)

    def take_turn(self) -> Tuple[Card, bool]:
        playable_cards = self.get_playable_cards()
        if len(playable_cards) > 0:
            card = self.get_random_playable_card()
            is_discarded = False
        else:
            card = self.get_random_card()
            is_discarded = True

        return card, is_discarded

    def get_random_playable_card(self) -> Card:
        playable_cards = self.get_playable_cards()
        card = playable_cards[
            randint(len(playable_cards))
        ]
        return card

    def get_random_card(self) -> Card:
        valid_cards = [card for card in self.hand if card is not None]  # Hand does contain None values
        return valid_cards[randint(len(valid_cards))]
