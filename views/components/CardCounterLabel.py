from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpinBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from views.components.CardLabel import CardLabel

class CardCounterLabel(QWidget):
    count_changed = pyqtSignal(str, int)  # Signal for card ID and count change

    def __init__(self, card, min_count: int = 0, max_count: int = 5) -> None:
        super().__init__()
        self.card = card

        self.init_ui(min_count, max_count)

    def init_ui(self, min_count: int, max_count: int) -> None:
        layout = QVBoxLayout(self)

        # Card art using QLabel
        self.card_label = CardLabel(self.card, interactable=False)

        # Counter using QSpinBox
        self.counter = QSpinBox(self)
        self.counter.setRange(min_count, max_count)
        self.counter.setValue(min_count)
        self.counter.valueChanged.connect(self.on_count_changed)

        # Add widgets to the layout
        layout.addWidget(self.card_label)
        layout.addWidget(self.counter)

    def on_count_changed(self, value: int) -> None:
        self.count_changed.emit(self.card.id, value)
