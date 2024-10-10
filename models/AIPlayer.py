from models.Player import Player

class AIPlayer(Player):
    def __init__(self, name) -> None:
        super().__init__(name)

    def take_turn(self) -> None:
        raise NotImplementedError('Subclasses must implement this method')
