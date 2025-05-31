import torch
from models.MCTSAIPlayer import MCTSAIPlayer, Node
from models.ValueNet import ValueNet
from ml_utils.feature_processing import build_feature_tensor, extract_features_from_state
from typing import Tuple

class MCTSNNAIPlayer(MCTSAIPlayer):
    def __init__(self, id: int, name: str, 
                 model_path: str = 'value_net.pth',
                 preferred_deck_file: str = 'default_deck.json',
                 iterations: int = 2000,
                 device: str ='cpu'):
        super().__init__(id, name, preferred_deck_file, depth_limit=0, iterations=iterations)

        self.device = torch.device(device)
        self.model = ValueNet().to(self.device)
        state_dict = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model.eval()

    def state_to_tensor(self, game_state: dict, move: Tuple) -> torch.Tensor:
        features = extract_features_from_state(game_state, move)
        return build_feature_tensor(features).to(self.device)

    def simulate(self, node: Node, depth_limit: int) -> float:
        if node.is_terminal() or node.game_state['current_player_id'] != self.id:
            return self.evaluate(node.game_state['game_status'])

        state_tensor = self.state_to_tensor(node.game_state, node.move)
        with torch.no_grad():
            value = self.model(state_tensor.unsqueeze(0))[0].item()

        return value
