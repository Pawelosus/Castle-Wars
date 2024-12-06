import random
from typing import List, Tuple, Union
from models.Card import Card
from models.Player import Player
from models.AIPlayer import AIPlayer
from Game import Game
from pathlib import Path


class Node:
    def __init__(self, parent: 'Node', move: Union[Card, None], is_discard: bool, player: AIPlayer, opponent: Player):
        self.parent = parent
        self.move = move
        self.is_discard = is_discard
        self.player = player  # Current AI player
        self.opponent = opponent  # Opponent player
        self.children = []
        self.visits = 0
        self.value = 0  # The evaluation of this node's game state

    def is_fully_expanded(self) -> bool:
        # Check if all possible child nodes (moves) have been explored
        return len(self.children) > 0

    def best_child(self) -> 'Node':
        # Select the child node with the best value
        return max(self.children, key=lambda child: child.value / (child.visits + 1e-5))


class MonteCarloAIPlayer(AIPlayer):
    def __init__(self, name: str, preferred_deck_file: Union[str, Path] = 'default_deck.json') -> None:
        super().__init__(name, preferred_deck_file)
        self.simulation_count = 3  # Number of simulations to run

    def take_turn(self, opponent: Player, game: Game) -> Tuple[Card, bool]:
        # Start MCTS to select the best move given the current game state
        best_move = self.mcts(game, opponent)
        return best_move

    def mcts(self, game: Game, opponent: Player) -> Tuple[Card, bool]:
        # Root node is the current game state
        root_node = Node(parent=None, move=None, is_discard=False, player=self, opponent=opponent)

        for _ in range(self.simulation_count):
            # Perform simulations to explore possible outcomes
            node_to_explore = self.selection(root_node)
            simulation_result = self.simulation(node_to_explore)
            self.backpropagation(node_to_explore, simulation_result)

        # After simulations, select the best move from the root node's children
        best_node = root_node.best_child()
        return best_node.move, best_node.is_discard

    def selection(self, root_node: Node) -> Node:
        # Traverse down the tree to find a node to simulate (select based on best value)
        current_node = root_node
        while current_node.is_fully_expanded():
            current_node = current_node.best_child()  # Pick the best child based on value
        return current_node

    def simulation(self, node: Node) -> int:
        # Simulate the game from this node's state
        simulated_game = node.player.simulate_game(node.move, node.is_discard, node.opponent)  # Simulate the result after the move
        # Determine the outcome of the simulation (win/loss)
        outcome = simulated_game.get_winner()  # 1 for win, -1 for loss
        return outcome

    def backpropagation(self, node: Node, result: int) -> None:
        # Backpropagate the result of the simulation up to the root
        current_node = node
        while current_node is not None:
            current_node.visits += 1
            current_node.value += result
            current_node = current_node.parent

