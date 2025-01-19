from models.Player import Player
from typing import NoReturn, Union, Optional
from pathlib import Path

class AIPlayer(Player):
    def __init__(self, id: int, name: str, preferred_deck_file: Union[str, Path] = 'default_deck.json') -> None:
        super().__init__(id, name, preferred_deck_file)

    def take_turn(self, game_state: dict) -> NoReturn:
        raise NotImplementedError('Subclasses must implement this method')
