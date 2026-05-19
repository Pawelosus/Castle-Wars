import random
import math
from typing import Optional, Tuple, Union
from pathlib import Path
from models.AIPlayer import AIPlayer
from models.Card import Card
from Game import Game
from DeckManager import DeckManager

class Node:
    def __init__(self, game_state: dict, parent: Optional["Node"] = None, move: Optional[Tuple] = None):
        self.game_state = game_state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.score = 0

    def is_terminal(self) -> bool:
        """Check if the game state is terminal (game over)."""
        return self.game_state["game_status"] in [1, 2, -1]

    def is_expanded(self) -> bool:
        """Check if Node has been expanded."""
        return len(self.children) > 0

    def ucb1_value(self, exploration_weight: float = 0.1) -> float:
        """Calculate the UCB1 value of this node."""
        assert self.parent is not None

        if self.visits == 0:
            return float('inf')  # Prioritize unvisited nodes

        return (self.score / self.visits) + exploration_weight * math.sqrt(math.log(self.parent.visits) / self.visits)

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
        child_node = DecisionNode(game_state, parent=self, move=move)
        self.children.append(child_node)

    def update(self, result: float) -> None:
        """Update the node's visit count and win count based on the result."""
        self.visits += 1
        self.score += result

    def expand(self) -> None:
        """Expand a node by adding DecisionNodes."""
        game = Game.from_state(self.game_state)
        moves = game.get_possible_moves() 

        for move in moves:
            temp_game = Game.from_state(self.game_state)
            self.apply_move(temp_game, move)
            child_state = temp_game.to_state()
            self.add_child(move, child_state)

    def apply_move(self, game: Game, move: Optional[Tuple[Card, bool]] = None) -> None:
        """Applies a move."""
        current_player = game.current_player
        other_player = game.get_other_player(current_player)
        assert current_player is not None

        if move is not None:
            card, discarded = move
            if not discarded:
                game.use_card_effect(current_player, card)
                current_player.spend_resources(card)
            game.update_resources(other_player)
            game.set_game_status()


class DecisionNode(Node):
    def __init__(self, game_state: dict, parent: Optional["Node"] = None, move: Optional[Tuple] = None):
        super().__init__(game_state, parent, move)

    def add_child(self, move: Tuple, game_state: dict) -> None:
        """Add a child node."""
        child_node = OpponentNode(game_state, parent=self, move=move)
        self.children.append(child_node)

    def expand(self) -> None:
        """
        Sample one draw from the weighted deck distribution and expand
        directly into OpponentNode children.
        """
        temp_game = Game.from_state(self.game_state)
        current_player = temp_game.current_player
        assert current_player is not None
 
        draw_distribution = current_player.deck.get_draw_distribution()
        if not draw_distribution:
            current_player.deck = current_player.init_deck()
            draw_distribution = current_player.deck.get_draw_distribution()
        card_ids, probs = zip(*draw_distribution.items())
        sampled_id = random.choices(card_ids, weights=probs, k=1)[0]
        draw_card = DeckManager.get_card_by_id(sampled_id)

        current_player.draw_card(draw_card)
        temp_game.change_current_player()
        post_draw_state = temp_game.to_state()
 
        legal_moves = temp_game.get_legal_moves()
        plays = [m for m in legal_moves if not m[1]]
        discard = next((m for m in legal_moves if m[1]), None)
        opponent_moves = plays + ([discard] if discard else [])
 
        for move in opponent_moves:
            move_game = Game.from_state(post_draw_state)
            self.apply_move(move_game, move)
            self.add_child(move, move_game.to_state())


class OpponentNode(Node):
    def __init__(self, game_state: dict, parent: Optional["Node"] = None, move: Optional[Tuple] = None):
        super().__init__(game_state, parent, move)


class MCTSAIPlayer(AIPlayer):
    def __init__(self, id: int, name: str, preferred_deck_file: Union[str, Path] = 'default_deck.json', depth_limit: int = 200, iterations: int = 1300):
        super().__init__(id, name, preferred_deck_file)
        self.depth_limit = depth_limit
        self.iterations = iterations

    def take_turn(self, game_state: dict) -> Tuple[Optional[object], bool]:
        """Execute the MCTS logic to determine the best move."""
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

        #self.display_tree(root, max_depth=1)
        #print(best_child.move[0].name, best_child.move[1], best_child.score, best_child.visits)
        return best_child.move if best_child else (None, False)

    def select_node(self, root_node: Node) -> 'Node':
        current_node = root_node

        while True:
            if current_node.is_terminal():
                return current_node
            if not current_node.is_expanded():
                current_node.expand()

            best_child = current_node.best_child()

            if best_child.visits == 0 and isinstance(best_child, DecisionNode):
                return best_child

            current_node = best_child


    def simulate(self, node: Node, depth_limit: int) -> float:
        game = Game.from_state(node.game_state)
        depth = 0

        if not isinstance(node, DecisionNode) or node.is_terminal():
            game_status = game.game_status
            return self.evaluate(game_status)

        current_player = game.current_player

        draw_card = current_player.deck.draw_card()
        if draw_card:
            current_player.draw_card(draw_card)

        game.change_current_player()

        while depth < depth_limit and game.game_status == 0:
            possible_moves = game.get_possible_moves()
            weights = [0.1 if move[1] else 1.0 for move in possible_moves]

            move = random.choices(possible_moves, weights=weights)[0]
            game.apply_move(move)

            depth += 1

        return self.evaluate(game.game_status)


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
        if depth > max_depth:
            return
        
        indent = "  " * depth
        node_type = type(node).__name__
        visits = node.visits
        score = node.score
        ucb1 = node.ucb1_value() if node.parent else "N/A"
        move = node.move[0].name if node.move else "Root"
        print(f"{indent}- [{node_type}] Move: {move}, Visits: {visits}, Score: {score:.2f}, UCB1: {ucb1}")
        
        for child in node.children:
            self.display_tree(child, depth + 1, max_depth)

