from models.Player import Player
from models.HumanPlayer import HumanPlayer
from models.AIPlayer import AIPlayer
from models.BasicAIPlayer import BasicAIPlayer
from utils.GameLogger import GameLogger
from typing import Union, Tuple, Optional

class Game:     
    def __init__(self):
        self.player1 = None
        self.player2 = None
        self.current_player = None
        self.game_status = 0
        self.game_mode = 0
        self.turn_count = 1

    def setup_game(
        self, mode: str, players: tuple, default_player_names: list,
        player1_deck: str = 'default_deck.json' , player2_deck: str = 'default_deck.json'
    ) -> None:
        self.player1 = players[0](id=1, name=default_player_names[0], preferred_deck_file=player1_deck)
        self.player2 = players[1](id=2, name=default_player_names[1], preferred_deck_file=player2_deck)
        self.current_player = self.player1
        self.game_status = 0
        self.turn_count = 1

        game_modes = {'singleplayer': 1, 'multiplayer': 2, 'cpu_only': 3}
        self.game_mode = game_modes.get(mode, 0)

    def setup_singleplayer(
        self, default_player_names: list,
        player1_type: type = HumanPlayer, player2_type: type = BasicAIPlayer,
        player1_deck: str = 'default_deck.json' , player2_deck: str = 'default_deck.json'
    ) -> None:
        self.setup_game(
            mode='singleplayer',
            players=(player1_type, player2_type),
            default_player_names=default_player_names,
            player1_deck=player1_deck,
            player2_deck=player2_deck
        )

    def setup_multiplayer(
        self, default_player_names: list,
        player1_type: type = HumanPlayer, player2_type: type = HumanPlayer,
        player1_deck: str = 'default_deck.json' , player2_deck: str = 'default_deck.json'
    ) -> None:
        self.setup_game(
            mode='cpu_only',
            players=(player1_type, player2_type),
            default_player_names=default_player_names,
            player1_deck=player1_deck,
            player2_deck=player2_deck
        )

    def setup_cpu_only(
        self, default_player_names: list,
        player1_type: type = BasicAIPlayer, player2_type: type = BasicAIPlayer,
        player1_deck: str = 'default_deck.json' , player2_deck: str = 'default_deck.json'
    ) -> None:
        self.setup_game(
            mode='cpu_only',
            players=(player1_type, player2_type),
            default_player_names=default_player_names,
            player1_deck=player1_deck,
            player2_deck=player2_deck
        )

    def apply_move(self, move: Tuple, logger: Optional[GameLogger] = None) -> None:
        """Apply the given move to the game state."""
        card, discarded = move
        assert self.current_player is not None

        # Apply card effect if not discarded
        if not discarded:
            self.use_card_effect(self.current_player, card)
            self.current_player.spend_resources(card)

        # Discard and draw the card
        self.current_player.discard_card(card)
        self.current_player.draw_card()

        # Update opponent resources (if applicable)
        self.update_resources(self.get_other_player(self.current_player))

        # Set the game status after the move
        self.set_game_status()

        if logger is not None:
            logger.log_move(self, card, discarded)

        if self.game_status == 0:
            self.change_current_player()

    def get_possible_moves(self) -> list:
        """Gets all possible moves that current player can make"""
        assert self.current_player is not None
        playable_cards = self.current_player.get_playable_cards()  # List of Card objects
        possible_moves = [(card, False) for card in playable_cards]  # Play the card
        possible_moves.extend((card, True) for card in self.current_player.hand)  # Discard the card
        return possible_moves

    def update_resources(self, player) -> None:
        for resource in player.resources:
            resource[1] += resource[0]

    def apply_action_to_player(self, target_player, action, action_value) -> None:
        if 'attack' in action:
            target_player.receive_damage(action_value)
        elif 'castle' in action:
            target_player.add_to_castle_hp(action_value)
        elif 'fence' in action:
            target_player.add_to_fence_hp(action_value)
        elif 'stacks' in action:
            target_player.add_to_stacks(action_value)
        elif 'all' in action:
            target_player.add_to_all(action_value)
        else:
            target_player.add_to_resource_based_on_action(action, action_value)

    def get_other_player(self, player) -> Union[HumanPlayer, AIPlayer]:
        if self.player1 is None or self.player2 is None:
            raise ValueError('Player cannot be None')

        return self.player2 if player is self.player1 else self.player1

    def change_current_player(self):
        self.current_player = self.get_other_player(self.current_player)
        self.turn_count += 1

    def get_action_target_player(self, player, action):
        if player is None:
            raise ValueError('Player cannot be None')

        if 'enemy' in action or 'attack' in action:
            return self.get_other_player(player)
        else:
            return player

    def use_card_effect(self, player, card):
        actions = card.effect.split(';')  # Handle multiple actions separately
        for action in actions:
            action_parts = action.split(' ')

            # Get the keyword (e.g., "castle", "attack", "fence")
            keyword = action_parts[0]
            action_value = card.get_effect_value(keyword)
            
            action_target_player = self.get_action_target_player(player, action_parts[:-1])
            
            if 'transfer' in action:
                other_player = self.get_other_player(action_target_player)
                action_target_player.transfer_resources(other_player, action_value)
            else:
                self.apply_action_to_player(action_target_player, action, action_value)

    def set_game_status(self):
        if self.player1 is None or self.player2 is None:
            raise ValueError('Player cannot be None')

        # Draw conditions
        if self.player1.castle_hp <= 0 and self.player2.castle_hp <= 0:
            self.game_status = -1
        elif self.player1.castle_hp >= 100 and self.player2.castle_hp >= 100:
            self.game_status = -1
        # Individual player win conditions
        elif self.player1.castle_hp >= 100:
            self.game_status = 1  # Player 1 wins by reaching 100 castle hp
        elif self.player2.castle_hp >= 100:
            self.game_status = 2  # Player 2 wins by reaching 100 castle hp
        elif self.player1.castle_hp <= 0:
            self.game_status = 2  # Player 2 wins by destroying player 1's castle
        elif self.player2.castle_hp <= 0:
            self.game_status = 1  # Player 1 wins by destroying player 2's castle
        # Card related win conditions
        elif self.player1.has_empty_hand() and self.player2.has_empty_hand():
            self.game_status = -1
        else:
            self.game_status = 0  # No winner yet

    def to_state(self) -> dict:
        if self.player1 is None or self.player2 is None or self.current_player is None:
            raise ValueError("Players or current player have not been initialized properly.")

        return {
            'game_mode': self.game_mode,
            'turn_count': self.turn_count,
            'current_player_id': self.current_player.id,
            'other_player': self.player1 if self.current_player is self.player2 else self.player2,  # required for AI logic
            'player1': self.player1.to_state(),
            'player2': self.player2.to_state(),
            'game_status': self.game_status,
        }

    @classmethod
    def from_state(cls, state: dict):
        game = cls()

        # Set attributes from the state
        game.game_mode = state['game_mode']
        game.turn_count = state['turn_count']
        game.player1 = Player.from_state(state['player1'])
        game.player2 = Player.from_state(state['player2'])
        
        # Link current_player to player1 or player2
        if state['current_player_id'] == game.player1.id:
            game.current_player = game.player1
        elif state['current_player_id'] == game.player2.id:
            game.current_player = game.player2
        else:
            raise ValueError("Invalid current_player ID in state")

        game.game_status = state['game_status']
        return game
