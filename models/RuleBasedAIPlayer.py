from models.Player import Player
from models.AIPlayer import AIPlayer
from models.Card import Card
from typing import Tuple, Union
from pathlib import Path

class RuleBasedAIPlayer(AIPlayer):
    def __init__(self, name: str, preferred_deck_file: Union[str, Path] = 'default_deck.json') -> None:
        super().__init__(name, preferred_deck_file)

    def _get_first_playable_card(self, card_getter_func) -> Union[Card, None]:
        """Helper function to get the first playable card from a specific category."""
        return next(iter(card_getter_func()), None)

    def take_turn(self, opponent: Player) -> Tuple[Card, bool]:
        is_discarded = False

        # === Winning Move Priority ===
        # Rule 1: Play any castle-building card if it guarantees a win
        for defense_card in self.get_defense_type_cards():
            if self.castle_hp + defense_card.get_effect_value(keyword='castle') >= 100:
                return defense_card, is_discarded

        # Rule 2: Play any strong attack card if it guarantees a win
        for attack_card in self.get_attack_type_cards():
            if attack_card.get_effect_value(keyword='attack') >= opponent.castle_hp + opponent.fence_hp:
                return attack_card, is_discarded

        # === Other Strategic Moves ===
        # Rule 3: Play "Curse" if the opponent has high production in one resource and low in others
        if opponent.resources:
            max_producer = max(res[0] for res in opponent.resources)
            min_producer = min(res[0] for res in opponent.resources)
            if max_producer >= 4 and min_producer <= 2:
                utility_card = self._get_first_playable_card(self.get_utility_type_cards)
                if utility_card and utility_card.name == "Curse":
                    return utility_card, is_discarded

        # Fallback: Play a random card if no strong rules apply
        random_card = self.get_random_playable_card()
        if random_card:
            return random_card, is_discarded

        # Rule 4: Discard the lowest-cost card if no cards can be played
        lowest_cost_card = self.get_lowest_cost_card()
        if not lowest_cost_card:
            raise ValueError('No card to discard')
        is_discarded = True
        return lowest_cost_card, is_discarded

