from PyQt6.QtWidgets import QApplication
from GameApp import GameApp

def run_game_app() -> None:
    app = QApplication([])
    game_app = GameApp()
    game_app.show()
    app.exec()

if __name__ == "__main__":
    run_game_app()