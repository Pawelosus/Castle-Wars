from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from config.config import Config

class MenuButton(QPushButton):
    clicked = pyqtSignal()

    def __init__(self, text) -> None:
        super().__init__()
        self.text = text
        self.config = Config()

        self.init_button()

    def init_button(self) -> None:
        self.setFixedSize(self.config.button_width, self.config.button_height)
        self.setText(self.text)
        self.setStyleSheet(
            """
            QPushButton {
                background-color: lightgrey;
                font-weight: bold;
                font-size: 14px;
            }
            """
        )
    
    def mousePressEvent(self, event) -> None:
        self.clicked.emit()
        super().mousePressEvent(event)
