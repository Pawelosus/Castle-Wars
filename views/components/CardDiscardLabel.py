from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

class CardDiscardLabel(QLabel):
    def __init__(self) -> None:
        super().__init__()

        self.setText('DISCARD')
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            """
            QLabel {
                background-color: rgba(255, 0, 0, 128);
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            """
        )