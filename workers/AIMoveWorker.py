from PyQt6.QtCore import QThread, pyqtSignal

class AIMoveWorker(QThread):
    move_ready = pyqtSignal(object, object)  # card, discarded — no widget

    def __init__(self, player, game_state):
        super().__init__()
        self.player = player
        self.game_state = game_state

    def run(self):
        card, discarded = self.player.take_turn(self.game_state)
        self.move_ready.emit(card, discarded)