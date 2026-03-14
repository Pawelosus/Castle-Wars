import torch
from models.MCTSAIPlayer import MCTSAIPlayer, Node, DecisionNode
from models.ValueNet import ValueNet
from ml_utils.feature_processing import build_feature_tensor, extract_features_from_state
from typing import Tuple

class MCTSNNAIPlayer(MCTSAIPlayer):
    def __init__(self, id: int, name: str, 
                 model_path: str = 'value_net.pth',
                 preferred_deck_file: str = 'default_deck.json',
                 iterations: int = 1000,
                 device: str ='cuda'):
        super().__init__(id, name, preferred_deck_file, depth_limit=0, iterations=iterations)

        self.device = torch.device(device)
        self.model = ValueNet().to(self.device)
        state_dict = torch.load(model_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state_dict)
        self.model.eval()

    def state_to_tensor(self, game_state: dict, move: Tuple) -> torch.Tensor:
        features = extract_features_from_state(game_state, move)
        return build_feature_tensor(features).to(self.device)

    def simulate(self, node: Node, depth_limit: int) -> float:
        if type(node) is not DecisionNode or node.is_terminal():
            return self.evaluate(node.game_state['game_status'])

        state_tensor = self.state_to_tensor(node.game_state, node.move)
        with torch.no_grad():
            value = self.model(state_tensor.unsqueeze(0))[0].item()

        return value
