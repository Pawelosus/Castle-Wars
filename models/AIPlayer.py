from models.Player import Player
from typing import NoReturn, Union
from pathlib import Path

class AIPlayer(Player):
    def __init__(self, name: str, preferred_deck_file: Union[str, Path] = 'default_deck.json') -> None:
        super().__init__(name, preferred_deck_file)

    def take_turn(self) -> NoReturn:
        raise NotImplementedError('Subclasses must implement this method')
