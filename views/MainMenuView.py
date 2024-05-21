from PyQt6.QtGui import QMouseEvent
import resources.resources_ui  # Loads in all resource files into ui
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QVBoxLayout
from views.components.MenuButton import MenuButton

class MainMenuView(QFrame):
    def __init__(self, parent, start_game_sp_callback, start_game_mp_callback) -> None:
        super().__init__(parent)
        self.start_sp_game_callback = start_game_sp_callback
        self.start_mp_game_callback = start_game_mp_callback

        uic.loadUi('views/mainmenu_view.ui', self)

        self.insert_menu_buttons()

    def insert_menu_buttons(self) -> None:
        menu_button_vbox = self.findChild(QVBoxLayout, 'menu_button_vbox')
        button_texts = ['1 player', '2 player', 'AI vs AI', 'Player settings', 'Instructions', 'Credits']
        button_functions = [self.start_sp_game_callback, self.start_mp_game_callback, None, None, None, None]

        for text, function in zip(button_texts, button_functions):
            button = MenuButton(text)
            if function:
                button.clicked.connect(function)
            else:
                button.setDisabled(True)
            menu_button_vbox.addWidget(button)