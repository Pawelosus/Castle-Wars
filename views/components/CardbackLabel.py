from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap

class CardbackLabel(QLabel):
    def __init__(self) -> None:
        super().__init__()

        self.init_label()
    
    def init_label(self) -> None:
        pixmap = QPixmap(f'resources/sprites/cards/cardback.png')
        if not pixmap.isNull():
            self.setPixmap(pixmap)
        

