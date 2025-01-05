from models.Player import Player
from models.AIPlayer import AIPlayer
from models.Card import Card
from typing import Tuple, Union
from pathlib import Path

class BasicAIPlayer(AIPlayer):
    def __init__(self, id: int, name: str, preferred_deck_file: Union[str, Path] = 'default_deck.json') -> None:
        super().__init__(id, name, preferred_deck_file)

    def take_turn(self, opponent: Player) -> Tuple[Card, bool]:
        playable_cards = self.get_playable_cards()
        if len(playable_cards) > 0:
            card = self.get_random_playable_card()
            is_discarded = False
        else:
            card = self.get_random_card()
            is_discarded = True

        assert card is not None, "Unexpected None card in AI take_turn"
        return card, is_discarded

