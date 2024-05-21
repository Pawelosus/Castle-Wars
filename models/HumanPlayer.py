from models.Player import Player

class HumanPlayer(Player):
    def __init__(self, name) -> None:
        super().__init__(name)