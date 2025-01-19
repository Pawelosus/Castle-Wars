from models.Player import Player

class HumanPlayer(Player):
    def __init__(self, id: int, name: str, preferred_deck_file) -> None:
        super().__init__(id, name, preferred_deck_file)
