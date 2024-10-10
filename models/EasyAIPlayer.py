from models.AIPlayer import AIPlayer
from models.Card import Card
from numpy.random import randint
from typing import Tuple

class EasyAIPlayer(AIPlayer):
    def __init__(self, name) -> None:
        super().__init__(name)

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
        card = self.hand[
            randint(len(self.hand))
        ]
        return card
