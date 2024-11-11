import resources.resources_ui  # Loads in all resource files into UI
from PyQt6 import uic
from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QFileDialog, QMessageBox
from views.components.MenuButton import MenuButton
from views.components.CardCounterLabel import CardCounterLabel
from DeckManager import DeckManager
from typing import Union
from pathlib import Path


class DeckManagerView(QFrame):
    def __init__(self, parent, config, back_to_main_menu_callback) -> None:
        super().__init__(parent)
        self.config = config
        self.back_to_main_menu_callback = back_to_main_menu_callback
        self.current_deck = DeckManager.load_deck(self.config.preferred_deck)
        self.all_cards = DeckManager.load_all_cards()

        uic.loadUi('views/deckmanager_view.ui', self)

        self.card_grid_layout = self.findChild(QGridLayout, 'card_grid_layout')

        self.add_card_widgets()
        self.setup_buttons()
        self.update_card_counts()

    def add_card_widgets(self) -> None:
        for card in self.all_cards:
            card_counter = CardCounterLabel(card)
            row = int(card.material_type)
            column = int(card.id[-1])
            if self.card_grid_layout.itemAtPosition(row, column) is None:
                self.card_grid_layout.addWidget(card_counter, row, column)

    def clear_card_counts(self) -> None:
        for card in self.all_cards:
            row = int(card.material_type)
            column = int(card.id[-1])
            
            layout_item = self.card_grid_layout.itemAtPosition(row, column)
            if layout_item is not None:
                card_widget = layout_item.widget()
                if isinstance(card_widget, CardCounterLabel):
                    card_widget.counter.setValue(0)

    def update_card_counts(self) -> None:
        for card in self.current_deck.cards:
            row = int(card.material_type)
            column = int(card.id[-1])
            
            layout_item = self.card_grid_layout.itemAtPosition(row, column)
            if layout_item is not None:
                card_widget = layout_item.widget()
                if isinstance(card_widget, CardCounterLabel):
                    card_widget.counter.setValue(card_widget.counter.value() + 1)

    def save_deck(self, deck_file: Union[str, Path]) -> None:
        row = 0
        column = 0
        deck_dict = {}

        for row in range(self.card_grid_layout.rowCount()):
            for column in range(self.card_grid_layout.columnCount()):
                layout_item = self.card_grid_layout.itemAtPosition(row, column)
                if layout_item is not None:
                    card_widget = layout_item.widget()
                    if isinstance(card_widget, CardCounterLabel):
                        card = card_widget.card
                        deck_dict[card.id] = card_widget.counter.value()

        DeckManager.save_deck(deck_dict, deck_file)

    def setup_buttons(self) -> None:
        self.import_export_button_vbox = self.findChild(QHBoxLayout, 'import_export_button_vbox')
        self.nav_button_vbox = self.findChild(QHBoxLayout, 'nav_button_vbox')

        import_button = MenuButton('Import')
        export_button = MenuButton('Export')
        use_button = MenuButton('Use')
        default_button = MenuButton('Default')
        back_button = MenuButton('Back')

        # Connect buttons to methods using DeckManager
        import_button.clicked.connect(self.import_deck)
        export_button.clicked.connect(self.export_deck)
        use_button.clicked.connect(self.use_deck)
        default_button.clicked.connect(self.load_default_deck)
        back_button.clicked.connect(self.back_to_main_menu_callback)

        self.import_export_button_vbox.addWidget(import_button)
        self.import_export_button_vbox.addWidget(export_button)
        self.nav_button_vbox.addWidget(use_button)
        self.nav_button_vbox.addWidget(default_button)
        self.nav_button_vbox.addWidget(back_button)

    def import_deck(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Deck", "", "JSON Files (*.json)")
        if file_name:
            try:
                self.current_deck = DeckManager.load_deck(file_name)
                self.clear_card_counts()
                self.update_card_counts()
                QMessageBox.information(self, "Success", "Deck imported successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to import deck: {e}")

    def export_deck(self) -> None:
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Deck", "", "JSON Files (*.json)")
        if file_name:
            try:
                self.save_deck(file_name)
                QMessageBox.information(self, "Success", "Deck exported successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export deck: {e}")

    def use_deck(self) -> None:
        self.config.set('Player', 'PreferredDeck', 'custom_deck.json')
        try:
            self.save_deck('custom_deck.json')
            QMessageBox.information(self, "Success", "Deck set as preferred successfully!")
            self.back_to_main_menu_callback()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to set preferred deck: {e}")

    def load_default_deck(self) -> None:
        self.clear_card_counts()
        self.current_deck = DeckManager.load_deck('default_deck.json')
        self.update_card_counts()
        QMessageBox.information(self, "Default Deck", "Default deck loaded successfully.")

