from models.Player import Player
from typing import NoReturn

class AIPlayer(Player):
    def __init__(self, name) -> None:
        super().__init__(name)

    def take_turn(self) -> NoReturn:
        raise NotImplementedError('Subclasses must implement this method')
