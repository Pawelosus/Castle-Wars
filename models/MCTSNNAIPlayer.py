import torch
from models.MCTSAIPlayer import MCTSAIPlayer, Node, DecisionNode
from models.ValueNet import ValueNet
from ml_utils.feature_processing import build_feature_tensor, extract_features_from_state
from typing import Tuple

class MCTSNNAIPlayer(MCTSAIPlayer):
    def __init__(self, id: int, name: str, 
                 model_path: str = 'value_net_best.pth',
                 preferred_deck_file: str = 'default_deck.json',
                 iterations: int = 2000,
                 device: str = 'cuda',
                 greedy: bool = True,
                 discard_penalty: float = 0.0):
        super().__init__(id, name, preferred_deck_file, depth_limit=0, iterations=iterations)
        self.greedy = greedy
        self.discard_penalty = discard_penalty
        self.device = torch.device(device)
        self.model = ValueNet().to(self.device)
        state_dict = torch.load(model_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state_dict)
        self.model.eval()

    def take_turn(self, game_state: dict) -> Tuple:
        if self.greedy:
            return self.greedy_take_turn(game_state)
        return super().take_turn(game_state)

    def greedy_take_turn(self, game_state: dict) -> Tuple:
        from Game import Game
        game = Game.from_state(game_state)
        moves = game.get_possible_moves()
        
        best_move = None
        best_value = float('-inf')
        
        for move in moves:
            temp_game = Game.from_state(game_state)
            temp_game.apply_move(move, finish_turn=False)

            state_tensor = self.state_to_tensor(temp_game.to_state(), move)
            with torch.no_grad():
                value = self.model(state_tensor.unsqueeze(0))[0].item()
            if move[1]:
                value -= self.discard_penalty  # Penalize discards slightly to encourage playing cards
            #print(f"{move[0].name} {'discard' if move[1] else 'play'}: {value:.4f}")
            if value > best_value:
                best_value = value
                best_move = move
        
        #print(f"Best: {best_move[0].name} {'discard' if best_move[1] else 'play'} = {best_value:.4f}")
        return best_move

    def state_to_tensor(self, game_state: dict, move: Tuple) -> torch.Tensor:
        features = extract_features_from_state(game_state, move)
        return build_feature_tensor(features).to(self.device)

    def simulate(self, node: Node, depth_limit: int) -> float:
        if node.is_terminal():
            return self.evaluate(node.game_state['game_status'])

        if isinstance(node, DecisionNode):
            state_tensor = self.state_to_tensor(node.game_state, node.move)
            with torch.no_grad():
                value = self.model(state_tensor.unsqueeze(0))[0].item()
            return value

        # OpponentNode that isn't terminal shouldn't be evaluated
        return node.parent.score
