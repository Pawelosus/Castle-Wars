from PyQt6.QtWidgets import QLabel, QGraphicsOpacityEffect, QHBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from views.components.CardDiscardLabel import CardDiscardLabel

class CardLabel(QLabel):
    clicked = pyqtSignal('QWidget')
    ctrl_clicked = pyqtSignal('QWidget')

    def __init__(self, card, interactable: bool = True) -> None:
        super().__init__()
        self.card = card
        self.interactable = interactable

        self.init_label()

    def init_label(self):
        self.card_id_filename = self.convert_card_id_to_file_name(self.card.id)
        pixmap = QPixmap(f'resources/sprites/cards/{self.card_id_filename}.png')
        if not pixmap.isNull():
            layout = QHBoxLayout(self)
            self.setPixmap(pixmap)
            self.setScaledContents(True)
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)

            discard_label = CardDiscardLabel()
            discard_label.setVisible(False)
            layout.addWidget(discard_label)

        else:
            print(f'Error loading image for card ID {self.card.id}')
        
    def apply_unplayable_filter_effect(self) -> None:
        opacity_effect = QGraphicsOpacityEffect(self)
        opacity_effect.setOpacity(0.5)  # Adjust opacity as needed
        self.setGraphicsEffect(opacity_effect)

    def mousePressEvent(self, event) -> None:
        if not self.interactable:
            return  # Ignore the event if not interactable
        if event.button() == Qt.MouseButton.LeftButton:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.ctrl_clicked.emit(self)
            else:
                self.clicked.emit(self)
        
    def clear_layout(self) -> None:
        if self.layout is not None:
            while self.layout.count():
                item = self.layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        
    def enterEvent(self, event) -> None:
        if not self.interactable:
            return
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def leaveEvent(self, event) -> None:
        if not self.interactable:
            return
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def convert_card_id_to_file_name(self, card_id) -> str:
        return card_id.replace(':', '')
