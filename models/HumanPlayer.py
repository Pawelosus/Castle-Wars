from models.Player import Player

class HumanPlayer(Player):
    def __init__(self, name, preferred_deck_file) -> None:
        super().__init__(name, preferred_deck_file)
