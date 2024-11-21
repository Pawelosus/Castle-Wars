from pathlib import Path
from typing import Union
from numpy.random import randint

from DeckManager import DeckManager
from models.Card import Card
from models.Deck import Deck
from resources.resource_names import resource_names

class Player:
    def __init__(self, name: str, preferred_deck_file: Union[str, Path] = 'default_deck.json') -> None:
        self.name = name
        self.preferred_deck_file = preferred_deck_file
        
        self.deck = self.init_deck()
        self.hand = self.init_hand()
        self.castle_hp = 30
        self.fence_hp = 10
        self.resources = [
            [2, 5],
            [2, 5],
            [2, 5]
        ]
        self.preferred_castle_color = None
        self.preferred_fence_color = None

    # === Init methods === 

    def init_hand(self) -> list:
        hand = []
        count = 8
        for _ in range(count):
            card = self.deck.draw_card()
            hand.append(card)        
        return hand

    def init_deck(self) -> Deck:
        return DeckManager.load_deck(self.preferred_deck_file)

    # === Card filtering methods ===

    def get_playable_cards(self) -> list:
        playable_cards = [card for card in self.hand if card is not None and card.is_playable(self.resources)]
        return playable_cards

    def get_random_playable_card(self) -> Union[Card, None]:
        playable_cards = self.get_playable_cards()
        if not playable_cards:
            return None
        return playable_cards[randint(len(playable_cards))]

    def get_random_card(self) -> Union[Card, None]:
        valid_cards = [card for card in self.hand if card is not None]
        if not valid_cards:
            return None
        return valid_cards[randint(len(valid_cards))]

    def get_cards_by_keywords(self, keywords: list[str]) -> list[Card]:
        """Returns a list of cards whose effects contain any of the specified keywords."""
        return [
            card for card in self.get_playable_cards()
            if any(keyword in card.effect for keyword in keywords)
        ]

    def get_attack_type_cards(self):
        return self.get_cards_by_keywords(["attack", "enemy castle"])

    def get_defense_type_cards(self):
        return self.get_cards_by_keywords(["fence", "castle"])

    def get_resource_type_cards(self):
        return self.get_cards_by_keywords(["bricks", "crystals", "weapons", "builders", "soldiers", "magic"])

    def get_utility_type_cards(self):
        return self.get_cards_by_keywords(["all"])

    def get_disrupt_type_cards(self):
        """Returns a list of cards that reduce the opponent's resources or affect the opponent's stacks."""
        return self.get_cards_by_keywords(["enemy bricks", "enemy crystals", "enemy weapons", "enemy stacks", "transfer"])

    def get_highest_cost_card(self):
        """Returns the card with the highest cost from the hand."""
        return max(self.hand, key=lambda card: card.cost, default=None)

    def get_lowest_cost_card(self):
        """Returns the card with the lowest cost from the hand."""
        return min(self.hand, key=lambda card: card.cost, default=None)
    
    # === Gameplay methods ===

    def has_empty_hand(self) -> bool:
        """Returns True if the player's hand consists only of None cards"""
        return all(card is None for card in self.hand)

    def draw_card(self) -> Union[Card, None]:
        for i, card in enumerate(self.hand):
            if card is None:
                new_card = self.deck.draw_card()
                if new_card:
                    self.hand[i] = new_card
                    return new_card
                else:
                    # If deck runs out of cards, refill the deck and attempt to draw again
                    self.deck = self.init_deck()
                    return self.draw_card() 
        return None  # Hand is full
    
    def discard_card(self, card) -> None:
        if card in self.hand:
            idx = self.hand.index(card)
            self.hand[idx] = None
        else:
            raise ValueError('Card not found in hand')
    
    def transfer_resources(self, other_player, transfer_amount) -> None:
        """Transfer resources between players with the specified amount"""
        resource_type_count = len(resource_names)
        for resource_type in range(resource_type_count):
            actual_amount = min(self.resources[resource_type][1], transfer_amount)
            self.resources[resource_type][1] -= actual_amount
            other_player.resources[resource_type][1] +=  actual_amount
    
    def receive_damage(self, incoming_damage) -> None:
        fence_damage = min(self.fence_hp, incoming_damage)
        self.fence_hp -= fence_damage
        self.castle_hp -= incoming_damage - fence_damage
        self.fence_hp = max(0, self.fence_hp)
        self.castle_hp = max(0, self.castle_hp)
        
    def add_to_castle_hp(self, value) -> None:
        self.castle_hp = max(0, self.castle_hp + value)
    
    def add_to_fence_hp(self, value) -> None:
        self.fence_hp = max(0, self.fence_hp + value)
    
    def add_to_stacks(self, value) -> None:
        """Adds value to bricks, weapons and magic resources"""
        for resource_type in range(len(self.resources)):
            self.resources[int(resource_type)][1] = max(0, self.resources[int(resource_type)][1] + value)
        
    def add_to_all(self, value) -> None:
        self.add_to_castle_hp(value)
        self.add_to_fence_hp(value)
        for resource_type in self.resources:
            for idx in range(len(resource_type)):
                resource_type[idx] = max(1, resource_type[idx] + value)
    
    def add_to_resource_based_on_action(self, action, value) -> None:
        for resource_type, resource_info in resource_names.items():
            for idx, resource_name in enumerate(resource_info):
                if resource_name in action:
                    self.resources[int(resource_type)][idx] = max(0, self.resources[int(resource_type)][idx] + value)
                    return
        raise ValueError(f'Invalid action "{action}" not found in resource names: {list(resource_names.keys())}')

    def spend_resources(self, card) -> None:
        self.resources[card.material_type][1] -= card.cost
