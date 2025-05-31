import torch
import numpy as np
from typing import Tuple
from ml_utils.feature_constants import FEATURE_STATS

NUM_CARDS = 30

def card_str_to_id(card: str) -> int:
    try:
        card_type, idx = map(int, card.split(":"))
        return card_type * 10 + idx
    except Exception:
        return 0

def card_str_to_one_hot(card: str) -> torch.Tensor:
    card_id = card_str_to_id(card)
    one_hot = torch.zeros(NUM_CARDS, dtype=torch.float32)
    if 0 <= card_id < NUM_CARDS:
        one_hot[card_id] = 1.0
    return one_hot

def encode_hand_to_vector(hand: list[str]) -> list[int]:
    vector = [0] * NUM_CARDS
    for card in hand:
        vector[card_str_to_id(card)] += 1
    return vector

def normalize_resources(res: list[int]) -> list[float]:
    """
    Normalize income (even indices) and stock (odd indices).
    Income (0, 2, 4) is divided by 5.0, stock (1, 3, 5) by 40.0.
    """
    return [
        val / 5.0 if i % 2 == 0 else val / 40.0
        for i, val in enumerate(res)
    ]

def build_feature_tensor(features: dict) -> torch.Tensor:
    vec = [
        features['Turn'] / 60.0,
        features['Player Castle HP'] / 100.0,
        np.log1p(features['Player Fence HP']),
        *encode_hand_to_vector(features['Player Hand']),
        features['Opponent Castle HP'] / 100.0,
        np.log1p(features['Opponent Fence HP']),
        *normalize_resources(features['Player Resources']),
        *normalize_resources(features['Opponent Resources']),
        *card_str_to_one_hot(features['Card Played']),
        float(features['Is discarded']),
    ]
    return torch.tensor(vec, dtype=torch.float32)

def extract_features_from_state(state: dict, move: Tuple) -> dict:
    """
    Converts a nested game state (from to_state()) into a flat dictionary for the value network.
    """
    if state['current_player_id'] == state['player1']['id']:
        current_player = state['player1']
        opponent = state['player2']
    else:
        current_player = state['player2']
        opponent = state['player1']
    
    return {
        'Turn': state['turn_count'],
        'Player Castle HP': current_player['castle_hp'],
        'Player Fence HP': current_player['fence_hp'],
        'Player Hand': current_player['hand'],
        'Opponent Castle HP': opponent['castle_hp'],
        'Opponent Fence HP': opponent['fence_hp'],
        'Player Resources': [val for sublist in current_player['resources'] for val in sublist],
        'Opponent Resources': [val for sublist in opponent['resources'] for val in sublist],
        'Card Played': move[0].id,
        'Is discarded': move[1]
    }
