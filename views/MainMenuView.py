import resources.resources_ui  # Loads in all resource files into UI
from PyQt6 import uic
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QComboBox, QPushButton, QRadioButton, QButtonGroup, QLabel
from PyQt6.QtCore import Qt
from pathlib import Path
from views.components.MenuButton import MenuButton
from utils.GameResourcesManager import GameResourcesManager

class MainMenuView(QFrame):
    def __init__(self, parent, start_game_sp_callback, start_game_mp_callback, start_game_cpu_callback, display_deck_manager_callback) -> None:
        super().__init__(parent)
        self.start_game_sp_callback = start_game_sp_callback
        self.start_game_mp_callback = start_game_mp_callback
        self.start_game_cpu_callback = start_game_cpu_callback
        self.display_deck_manager_callback = display_deck_manager_callback

        uic.loadUi('views/mainmenu_view.ui', self)

        self.show_main_menu()

    def clear_buttons(self) -> None:
        """Remove all existing buttons from the layout."""
        while self.menu_button_vbox.count():
            button = self.menu_button_vbox.takeAt(0).widget()
            if button:
                button.deleteLater()

    def setup_buttons(self, config) -> None:
        """Create buttons based on provided configuration."""
        self.clear_buttons()
        for item in config:
            button = MenuButton(item["text"])
            callback_name = item.get("callback")
            if callback_name and hasattr(self, callback_name):
                button.clicked.connect(getattr(self, callback_name))
            else:
                button.setDisabled(True)
            self.menu_button_vbox.addWidget(button)

    def load_ai_model_combo_box(self) -> None:
        """Set up the AI model selection combo box using available AI models."""
        ai_label = QLabel("Select AI Model:")
        ai_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.menu_button_vbox.addWidget(ai_label)

        self.ai_model_combo = QComboBox()
        ai_models = GameResourcesManager.load_ai_models()
        self.ai_model_combo.addItems(ai_models)
        self.menu_button_vbox.addWidget(self.ai_model_combo)

    def load_deck_combo_box(self) -> None:
        """Set up the deck selection combo box using available deck files."""
        deck_label = QLabel("Select Deck:")
        deck_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.menu_button_vbox.addWidget(deck_label)

        self.deck_combo = QComboBox()
        decks = GameResourcesManager.load_decks()
        self.deck_combo.addItems(decks)
        self.menu_button_vbox.addWidget(self.deck_combo)
    
    def show_main_menu(self) -> None:
        """Display the main menu buttons."""
        config = [
            {"text": "1 Player", "callback": "show_sp_config_menu"},
            {"text": "2 Player", "callback": "start_game_mp_callback"},
            {"text": "AI vs AI", "callback": "start_game_cpu_callback"},
            {"text": "Deck Manager", "callback": "display_deck_manager_callback"},
            {"text": "Instructions", "callback": None},
            {"text": "Credits", "callback": None},
        ]
        self.setup_buttons(config)

    def show_sp_config_menu(self) -> None:
        """Display Singleplayer configuration menu using the existing menu_button_vbox layout."""
        self.clear_buttons()

        # AI Model Selection
        ai_label = QLabel("Select AI Model:")
        ai_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.menu_button_vbox.addWidget(ai_label)

        self.ai_model_combo = QComboBox()
        ai_models = GameResourcesManager.load_ai_models()
        self.ai_model_combo.addItems(ai_models)
        self.menu_button_vbox.addWidget(self.ai_model_combo)

        # Deck Selection
        deck_label = QLabel("Select AI Deck:")
        deck_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.menu_button_vbox.addWidget(deck_label)

        self.deck_combo = QComboBox()
        decks = GameResourcesManager.load_decks()
        self.deck_combo.addItems(decks)
        self.menu_button_vbox.addWidget(self.deck_combo)

        # First or Second Player Choice
        player_order_label = QLabel("Choose Player Order:")
        player_order_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.menu_button_vbox.addWidget(player_order_label)

        self.first_player_radio = QRadioButton("Start First")
        self.second_player_radio = QRadioButton("Start Second")
        self.first_player_radio.setChecked(True)

        self.player_order_group = QButtonGroup()
        self.player_order_group.addButton(self.first_player_radio)
        self.player_order_group.addButton(self.second_player_radio)

        self.menu_button_vbox.addWidget(self.first_player_radio)
        self.menu_button_vbox.addWidget(self.second_player_radio)

        # Start Game Button
        start_button = MenuButton("Start Game")
        start_button.clicked.connect(self.start_singleplayer_game)
        self.menu_button_vbox.addWidget(start_button)

        # Back Button
        back_button = MenuButton("Back")
        back_button.clicked.connect(self.show_main_menu)
        self.menu_button_vbox.addWidget(back_button)

    def start_singleplayer_game(self) -> None:
        """Callback to start the singleplayer game with the selected options."""
        selected_ai_model = self.ai_model_combo.currentText()
        selected_deck = self.deck_combo.currentText()
        is_player_first = self.first_player_radio.isChecked()

        selected_deck += '.json'

        # Pass the selected options to the start game callback
        self.start_game_sp_callback(selected_ai_model, selected_deck, is_player_first)

