import random
import math
from typing import Optional, Tuple, Union
from pathlib import Path
from models.AIPlayer import AIPlayer
from models.Card import Card
from Game import Game

class Node:
    def __init__(self, game_state: dict, parent: Optional["Node"] = None, move: Optional[Tuple] = None, is_agent_turn_next: bool = True):
        self.game_state = game_state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.score = 0
        self.is_agent_turn_next = is_agent_turn_next

    def is_terminal(self) -> bool:
        """Check if the game state is terminal (game over)."""
        return self.game_state["game_status"] in [1, 2, -1]

    def is_fully_expanded(self) -> bool:
        """Check if all possible moves have been explored."""
        game = Game.from_state(self.game_state)
        current_player = game.current_player
        assert current_player is not None

        if self.is_agent_turn_next:
            moves = game.get_possible_moves()  # For the current player
        else:
            moves = [move for move in game.get_legal_moves() if not move[1]] + [[move for move in game.get_legal_moves() if move[1]][0]]  # For the opponent

        return len(self.children) == len(moves)

    def ucb1_value(self, exploration_weight: float = 2.5) -> float:
        """Calculate the UCB1 value of this node."""
        assert self.parent is not None
        parent_visits = self.parent.visits

        if self.visits == 0:
            return float('inf')  # Prioritize unvisited nodes

        return (self.score / self.visits) + exploration_weight * math.sqrt(math.log(parent_visits) / self.visits)

    def best_child(self) -> 'Node':
        """Return the child node with the highest UCB1 value."""
        if not self.children:
            raise ValueError('Root node has no children')

        best_value = -float('inf')
        for child in self.children:
            ucb1_val = child.ucb1_value()
            if ucb1_val > best_value:
                best_value = ucb1_val
                best_node = child
        
        return best_node

    def add_child(self, move: Tuple, game_state: dict) -> None:
        """Add a child node."""
        new_state = game_state
        child_node = Node(new_state, parent=self, move=move, is_agent_turn_next=not self.is_agent_turn_next)
        self.children.append(child_node)

    def update(self, result: float) -> None:
        """Update the node's visit count and win count based on the result."""
        self.visits += 1
        self.score += result

class MCTSAIPlayer(AIPlayer):
    def __init__(self, id: int, name: str, preferred_deck_file: Union[str, Path] = 'default_deck.json', depth_limit: int = 200, iterations: int = 3000):
        super().__init__(id, name, preferred_deck_file)
        self.depth_limit = depth_limit
        self.iterations = iterations
    
    def take_turn(self, game_state: dict) -> Tuple[Optional[object], bool]:
        """Executes the MCTS logic to determine the best move."""
        best_move = self.mcts(game_state)
        return best_move
    
    def mcts(self, game_state: dict) -> Tuple[Optional[object], bool]:
        # Root node creation
        root = Node(game_state, parent=None, move=None)

        for _ in range(self.iterations):
            node = self.select_node(root)
            simulation_result = self.simulate(node, self.depth_limit)
            self.backpropagate(node, simulation_result)

        best_child = max(
            root.children,
            key=lambda child: (child.score / child.visits if child.visits > 0 else float('-inf'), child.visits)
        )
        
        # self.display_tree(root)
        
        print(best_child.move[0].name, best_child.move[1], best_child.score, best_child.visits)
        return best_child.move if best_child else (None, False)

    def select_node(self, root_node: Node) -> 'Node':
        current_node = root_node

        while True:
            if current_node.is_terminal():
                return current_node
            if not current_node.is_fully_expanded():
                self.expand(current_node)
            
            # Select the best child using UCB1
            best_child = current_node.best_child()

            if best_child.visits == 0:
                return best_child

            current_node = best_child

    def expand(self, node: Node) -> None:
        """Expand a node by adding a child for an unexplored move."""
        game = Game.from_state(node.game_state)
        current_player = game.current_player

        assert current_player is not None
        if self.is_current_player(current_player.id):
            moves = game.get_possible_moves()  # For the current player
        else:
            moves = [move for move in game.get_legal_moves() if not move[1]] + [[move for move in game.get_legal_moves() if move[1]][0]]  # For the opponent
        
        for move in moves:
            temp_game = Game.from_state(node.game_state)
            self._apply_move(temp_game, move)
            child_state = temp_game.to_state()
            node.add_child(move, child_state)

    def simulate(self, node: Node, depth_limit: int) -> float:
        game = Game.from_state(node.game_state)
        depth = 0
        total_score = 0

        if node.is_terminal():
            game_status = game.game_status
            return self.evaluate(game_status)

        while depth < depth_limit and game.game_status == 0:
            possible_moves = game.get_possible_moves()
            weights = [0.5 if move[1] else 1.0 for move in possible_moves]
            move = random.choices(possible_moves, weights=weights)[0]

            self._apply_move(game, move)

            game_status = game.game_status
            total_score += self.evaluate(game_status)
            depth += 1

        return total_score

    def _apply_move(self, game: Game, move: Tuple[Card, bool]) -> None:
        """
        Applies a move.

        If it's the current player's turn, normal game rules apply.
        If it's the opponent's turn, the move is played without accessing his hand. Card draw and discards don't take effect.
        Args:
            game (Game): The current game instance.
            move (Tuple[Card, bool]): A tuple representing the move (card, discarded).
        """
        assert game.current_player is not None

        if self.is_current_player(game.current_player.id):
            game.apply_move(move)
            return

        card, discarded = move
        if not discarded:
            game.use_card_effect(game.current_player, card)
            game.current_player.spend_resources(card)

        game.update_resources(game.get_other_player(game.current_player))
        game.set_game_status()

        if game.game_status == 0:
            game.change_current_player()

    def backpropagate(self, node: Node, result: float) -> None:
        """Backpropagate the simulation result through the tree."""
        while node is not None:
            node.update(result)
            node = node.parent

    def evaluate(self, game_status: int) -> float:
        """Evaluates the game state for a win/loss perspective of the AI."""
        score = 0
        if game_status == self.id:  # Win
            score += 1
        elif game_status == 0:  # Ongoing
            score += 0
        elif game_status == -1:  # Draw
            score += 0.2
        else:  # Loss
            score += -1

        return score

    def display_tree(self, node, depth=0, max_depth=3):
        """
        Recursively print the MCTS tree structure, limiting the depth to just the root's children.

        Args:
            node (Node): The root node to display.
            depth (int): Current depth in the tree, used for indentation.
            max_depth (int): The maximum depth to display.
        """
        if depth > max_depth:  # Stop recursion if we exceed the max depth
            return
            
        indent = "  " * depth  # Indentation to represent tree depth
        move = node.move[0].name if node.move else "Root"
        visits = node.visits
        score = node.score
        ucb1 = node.ucb1_value() if node.parent else "N/A"
        print(f'{indent}- Move: {move}, Visits: {visits}, Score: {score:.2f}, UCB1: {ucb1}')
        
        for child in node.children:
            self.display_tree(child, depth + 1, max_depth)

