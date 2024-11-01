import resources.resources_ui  # Loads in all resource files into ui
from PyQt6 import uic
from PyQt6.QtWidgets import QLabel, QFrame, QHBoxLayout, QWidget, QPushButton, QApplication
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QEvent, QTimer
from views.components.CardLabel import CardLabel
from views.components.CardDiscardLabel import CardDiscardLabel
from views.components.GhostCardLabel import GhostCardLabel
from views.components.CardbackLabel import CardbackLabel
from utils.ImageHelper import ImageHelper
from models.AIPlayer import AIPlayer
from config.config import Config

class GameView(QFrame):
    def __init__(self, parent, game_instance, card_picked_callback, back_to_main_menu_callback) -> None:
        super().__init__(parent)
        self.game_instance = game_instance
        self.config = Config()
        self.card_picked_callback = card_picked_callback
        self.back_to_main_menu_callback = back_to_main_menu_callback
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Allow the frame to receive keyboard events
        self.ctrl_pressed = False  # Flag variable to track if Ctrl key is pressed

        self.last_played_card = None

        uic.loadUi('views/game_view.ui', self)

        self.findChild(QWidget, 'game_result').setVisible(False)

        self.connect_buttons()
        self.set_player_name_labels()
        self.init_last_played_cards_hbox()
        self.color_player_structures()

        self.update_resource_labels()
        self.update_structure_levels()
        self.update_current_turn_marker()
        self.start_turn()

    def start_turn(self) -> None:
        def _handle_ai_turn():
            card, discarded = self.game_instance.current_player.take_turn()
            card_label = CardLabel(card)
            if discarded:
                discard_label = card_label.findChild(CardDiscardLabel)
                discard_label.setVisible(True)

            self.card_picked_callback(card, card_label, discarded)
        
        self.ctrl_pressed = False
        self.display_hand()
        QApplication.processEvents()

        if isinstance(self.game_instance.current_player, AIPlayer):
            QTimer.singleShot(10, lambda: _handle_ai_turn())

    def init_last_played_cards_hbox(self) -> None:
        def init_card(sprite_path) -> QLabel:
            card = QLabel()
            card.setPixmap(QPixmap(sprite_path))
            card.setScaledContents(True)
            card.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return card

        last_played_cards_layout = self.findChild(QHBoxLayout, 'last_played_cards_hbox')
        cardback = init_card('resources/sprites/cards/cardback.png')
        placeholder = init_card('resources/sprites/cards/last_card_placeholder.png')

        last_played_cards_layout.addWidget(cardback)
        last_played_cards_layout.addWidget(placeholder)

    def update_last_played_card_label(self, card_label) -> None:
        last_played_cards_layout = self.findChild(QHBoxLayout, 'last_played_cards_hbox')
        last_played_card = last_played_cards_layout.itemAt(1).widget()
        last_played_cards_layout.removeWidget(last_played_card)

        card_label.installEventFilter(self)
        last_played_cards_layout.addWidget(card_label)
        
    def connect_buttons(self) -> None:
        game_result_exit_button = self.findChild(QPushButton, 'game_result_exit_button')
        if game_result_exit_button:
            game_result_exit_button.clicked.connect(self.back_to_main_menu_callback)
    
    def color_player_structures(self) -> None:
        players = [self.game_instance.player1, self.game_instance.player2]

        # Setting castle colors
        p1_castle = self.findChild(QLabel, 'p1_castle')
        p2_castle = self.findChild(QLabel, 'p2_castle')
        castles = [p1_castle, p2_castle]
        for idx, castle in enumerate(castles):
            castle_pixmap = castle.pixmap()
            if players[idx].preferred_castle_color is None:
                castle_color = self.config.default_castle_colors[idx]
            else:
                castle_color = players[idx].preferred_castle_color

            castle.setPixmap(ImageHelper.apply_color_filter(castle_pixmap, castle_color))
        
        # Setting fence colors
        p1_fence_base = self.findChild(QLabel, 'p1_fence_base')
        p2_fence_base = self.findChild(QLabel, 'p2_fence_base')
        fences = [p1_fence_base, p2_fence_base]
        for idx, fence in enumerate(fences):
            fence_pixmap = fence.pixmap()
            if players[idx].preferred_fence_color is None:
                fence_color = self.config.default_fence_color
            else:
                fence_color = players[idx].preferred_fence_color

            fence.setPixmap(ImageHelper.apply_color_filter(fence_pixmap, fence_color))

    def set_player_name_labels(self) -> None:
        p1_name_label = self.findChild(QLabel, 'p1_name')
        p2_name_label = self.findChild(QLabel, 'p2_name')

        p1_name_label.setText(self.game_instance.player1.name)
        p2_name_label.setText(self.game_instance.player2.name)

    def display_hand(self) -> None:
        current_player = self.game_instance.current_player
        hand_layout = self.findChild(QHBoxLayout, 'current_player_hand_hbox')
        for card in current_player.hand:
            card_label = None
            if isinstance(current_player, AIPlayer) and self.game_instance.game_mode != 3:
                card_label = CardbackLabel() 
            elif card is None:
                card_label = GhostCardLabel()
            else:
                card_label = CardLabel(card)
                if card.is_playable(current_player.resources):
                    card_label.clicked.connect(self.card_clicked)
                else:
                    card_label.apply_unplayable_filter_effect()

                card_label.ctrl_clicked.connect(self.card_ctrl_clicked)

            hand_layout.addWidget(card_label)
            
    def update_resource_labels(self) -> None:
        players = [self.game_instance.player1, self.game_instance.player2]
        for player_index, player in enumerate(players, 1):
            for resource_index, resources in enumerate(player.resources):
                for sub_resource_index, resource_value in enumerate(resources):
                    label = self.findChild(QLabel, f'p{player_index}_resource_{resource_index}_{sub_resource_index}_value')
                    label.setText(str(resource_value))

            castle_hp_label = self.findChild(QLabel, f'p{player_index}_castle_hp_value')
            fence_hp_label = self.findChild(QLabel, f'p{player_index}_fence_hp_value')
            castle_hp_label.setText(str(player.castle_hp))
            fence_hp_label.setText(str(player.fence_hp))
        
    def handle_card_click(self, card_label, discarded=False) -> None:
        if self.game_instance.game_status != 0 or self.game_instance.game_mode == 3:
            return

        self.card_picked_callback(card_label.card, card_label, discarded)
        if self.ctrl_pressed:
            self.apply_discard_labels()

    def card_clicked(self, card_label) -> None:
        self.handle_card_click(card_label)

    def card_ctrl_clicked(self, card_label) -> None:
        self.handle_card_click(card_label, discarded=True)
    
    def clear_hand_display(self) -> None:
        # Remove all widgets from the hand layout
        hand_layout = self.findChild(QHBoxLayout, 'current_player_hand_hbox')
        for i in reversed(range(hand_layout.count())):
            widget = hand_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
    
    def clear_discard_labels(self) -> None:
        hand_layout = self.findChild(QHBoxLayout, 'current_player_hand_hbox')
        # Iterate over each card label in the hand layout
        for i in range(hand_layout.count()):
            card_label = hand_layout.itemAt(i).widget()
            if isinstance(card_label, GhostCardLabel):
                continue
            discard_label = card_label.findChild(CardDiscardLabel)
            discard_label.setVisible(False)

    def apply_discard_labels(self) -> None:
        hand_layout = self.findChild(QHBoxLayout, 'current_player_hand_hbox')
        # Iterate over each card label in the hand layout
        for i in range(hand_layout.count()):
            card_label = hand_layout.itemAt(i).widget()
            if isinstance(card_label, GhostCardLabel):
                continue
            discard_label = card_label.findChild(CardDiscardLabel)
            discard_label.setVisible(True)
        
    def update_current_turn_marker(self) -> None:
        p1_current_turn_marker = self.findChild(QWidget, 'p1_current_turn_marker')
        p2_current_turn_marker = self.findChild(QWidget, 'p2_current_turn_marker')
        
        if self.game_instance.player1 is self.game_instance.current_player:
            p1_current_turn_marker.setVisible(True)
            p2_current_turn_marker.setVisible(False)
        else:
            p1_current_turn_marker.setVisible(False)
            p2_current_turn_marker.setVisible(True)
    
    def update_structure_levels(self) -> None:
        y_scale_mult = 2  # Defining a rate of how high/low the sprites go per value update
        self.update_castle_levels(y_scale_mult)
        self.update_fence_levels(y_scale_mult)

    def update_castle_levels(self, y_scale_mult=2) -> None:
        p1_castle = self.findChild(QLabel, 'p1_castle')
        p2_castle = self.findChild(QLabel, 'p2_castle')

        p1_castle.move(p1_castle.x(), self.config.base_castle_y_level - self.game_instance.player1.castle_hp * y_scale_mult)
        p2_castle.move(p2_castle.x(), self.config.base_castle_y_level - self.game_instance.player2.castle_hp * y_scale_mult)
    
    def update_fence_levels(self, y_scale_mult=2) -> None:
        p1_fence_base = self.findChild(QLabel, 'p1_fence_base')
        p2_fence_base = self.findChild(QLabel, 'p2_fence_base')
        p1_fence_tip = self.findChild(QLabel, 'p1_fence_tip')
        p2_fence_tip = self.findChild(QLabel, 'p2_fence_tip')

        p1_fence_base.move(p1_fence_base.x(), self.config.base_fence_y_level - self.game_instance.player1.fence_hp * y_scale_mult)
        p2_fence_base.move(p2_fence_base.x(), self.config.base_fence_y_level - self.game_instance.player2.fence_hp * y_scale_mult)
        p1_fence_tip.move(p1_fence_tip.x(), p1_fence_base.y() - p1_fence_tip.height())
        p2_fence_tip.move(p2_fence_tip.x(), p2_fence_base.y() - p2_fence_tip.height())

    def handle_game_status(self, game_status) -> None:
        if game_status == 0:
            return
        
        game_result_widget = self.findChild(QWidget, 'game_result')
        game_result_msg = self.findChild(QLabel, 'game_result_msg')
        message = ''
        if game_status == -1:
            message = 'Draw!'
        elif game_status == 1:
            message = f'{self.game_instance.player1.name} won!'
        elif game_status == 2:
            message = f'{self.game_instance.player2.name} won!'
        
        game_result_msg.setText(message)
        game_result_widget.setVisible(True)
        self.disable_hand_layout()

    def disable_hand_layout(self) -> None:
        hand_layout = self.findChild(QHBoxLayout, 'current_player_hand_hbox')
        for i in range(hand_layout.count()):
            card_label = hand_layout.itemAt(i).widget()
            card_label.setDisabled(True)

    def keyPressEvent(self, event) -> None:
        if self.game_instance.game_status != 0 or isinstance(self.game_instance.current_player, AIPlayer):
            return
        if event.key() == Qt.Key.Key_Control:
            self.ctrl_pressed = True
            self.apply_discard_labels()
        else:
            super().keyPressEvent(event)
        
    def keyReleaseEvent(self, event) -> None:
        if self.game_instance.game_status != 0 or isinstance(self.game_instance.current_player, AIPlayer):
            return
        if event.key() == Qt.Key.Key_Control:
            self.ctrl_pressed = False
            self.clear_discard_labels()
        else:
            super().keyReleaseEvent(event)
    
    def eventFilter(self, obj, event) -> bool:
        # Used to filter any mouse events on last played card hbox
        if event.type() in [QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease, QEvent.Type.MouseButtonDblClick, QEvent.Type.Enter]:
            return True  # Ignore mouse events
        return False
