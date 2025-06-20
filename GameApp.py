from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from models.HumanPlayer import HumanPlayer
from models.RuleBasedAIPlayer import RuleBasedAIPlayer
from views.MainMenuView import MainMenuView
from views.GameView import GameView
from views.DeckManagerView import DeckManagerView
from utils.GameLogger import GameLogger
from utils.GameResourcesManager import GameResourcesManager
from Game import Game
from config.config import Config

class GameApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.game_instance = Game()
        self.config = Config()
        self.game_logger = None

        self.setWindowTitle('Castle Wars')
        self.setFixedSize(int(self.config.window_width), int(self.config.window_height))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.current_view = MainMenuView(self, self.start_sp_game, self.start_mp_game, self.start_cpu_game, self.show_deck_manager)
        self.layout.addWidget(self.current_view)
        
    def switch_view(self, new_view, *args, **kwargs) -> None:
        self.layout.removeWidget(self.current_view)
        self.current_view.deleteLater()

        self.current_view = new_view(self, *args, **kwargs)
        self.layout.addWidget(self.current_view)

    def start_game(self) -> None:
        """Starts game and switches view to GameView"""
        if self.game_instance.player1 == None and self.game_instance.player2 == None:
            raise ValueError('Players must be assigned before running the game.')
        else:
            self.switch_view(GameView, self.game_instance, self.card_picked, self.back_to_main_menu)
            if self.config.enable_logs:
                self.game_logger = GameLogger()

    def start_sp_game(self, selected_ai_model_text: str, selected_ai_deck: str, is_player_first: bool) -> None:
        selected_ai_model = GameResourcesManager.resolve_ai_model(selected_ai_model_text)
        default_player_names = [self.config.default_player_name, self.config.default_cpu_name]
        preferred_player_deck = self.config.preferred_deck

        if is_player_first:
            player1_type = HumanPlayer
            player2_type = selected_ai_model
            player1_deck = preferred_player_deck
            player2_deck = selected_ai_deck
        else:
            player1_type = selected_ai_model
            player2_type = HumanPlayer
            player1_deck = selected_ai_deck
            player2_deck = preferred_player_deck

        self.game_instance.setup_singleplayer(default_player_names,
            player1_type=player1_type,
            player2_type=player2_type,
            player1_deck=player1_deck,
            player2_deck=player2_deck
        )
        self.start_game()

    def start_mp_game(self) -> None:
        default_player_names = [self.config.default_player_name + '1', self.config.default_player_name + '2']
        preferred_player_deck = self.config.preferred_deck
        self.game_instance.setup_singleplayer(default_player_names, player1_deck=preferred_player_deck)
        self.start_game()

    def start_cpu_game(self) -> None:
        default_player_names = [self.config.default_cpu_name + '1', self.config.default_cpu_name + '2']
        self.game_instance.setup_cpu_only(default_player_names, player2_type=RuleBasedAIPlayer)
        self.start_game()

    def show_deck_manager(self) -> None:
        self.switch_view(DeckManagerView, self.config, self.back_to_main_menu)

    def card_picked(self, card, card_label, discarded=False) -> None:
        if self.game_instance.current_player is None:
            raise ValueError('Current player cannot be None')
        if not discarded:
            self.game_instance.use_card_effect(self.game_instance.current_player, card)
            self.game_instance.current_player.spend_resources(card)

        self.game_instance.current_player.discard_card(card)

        # Updating resources
        self.game_instance.update_resources(self.game_instance.get_other_player(self.game_instance.current_player))
        self.current_view.update_resource_labels()
        self.current_view.update_structure_levels()
        self.current_view.update_last_played_card_label(card_label)

        self.game_instance.set_game_status()

        if self.game_logger is not None:
            self.game_logger.log_move(self.game_instance, card, discarded)

        self.game_instance.current_player.draw_card()

        self.current_view.handle_game_status(self.game_instance.game_status)

        if self.game_instance.game_status == 0:
            self.game_instance.change_current_player()
            self.current_view.update_current_turn_marker()
            self.current_view.clear_hand_display()
            self.current_view.start_turn()

    def back_to_main_menu(self) -> None:
        self.switch_view(MainMenuView, self.start_sp_game, self.start_mp_game, self.start_cpu_game, self.show_deck_manager)
