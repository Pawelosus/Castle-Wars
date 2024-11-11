import resources.resources_ui  # Loads in all resource files into ui
from PyQt6 import uic
from PyQt6.QtWidgets import QFrame
from views.components.MenuButton import MenuButton

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

    def show_main_menu(self) -> None:
        """Display the main menu buttons."""
        config = [
            {"text": "1 Player", "callback": "start_game_sp_callback"},
            {"text": "2 Player", "callback": "start_game_mp_callback"},
            {"text": "AI vs AI", "callback": "start_game_cpu_callback"},
            {"text": "Deck Manager", "callback": "display_deck_manager_callback"},
            {"text": "Instructions", "callback": None},
            {"text": "Credits", "callback": None},
        ]
        self.setup_buttons(config)

