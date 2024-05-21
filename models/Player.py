from models.Deck import Deck
from models.Card import Card
from resources.resource_names import resource_names
from typing import Union

class Player:
    def __init__(self, name) -> None:
        self.deck = Deck()
        self.name = name
        self.hand = self.init_hand()
        self.playable_cards = []
        self.castle_hp = 30
        self.fence_hp = 10
        self.resources = [
            [2, 5],
            [2, 5],
            [2, 5]
        ]
        self.preferred_castle_color = None
        self.preferred_fence_color = None

    def init_hand(self) -> list:
        hand = []
        count = 8
        for _ in range(count):
            card = self.deck.draw_card()
            hand.append(card)        
        return hand
    
    def has_empty_hand(self) -> bool:
        """Returns whether Player's hand consists of only None type cards"""
        for card in self.hand:
            if card is not None:
                return False
        return True

    def draw_card(self) -> Union[Card, None]:
        for i, card in enumerate(self.hand):
            if card is None:
                new_card = self.deck.draw_card()
                if new_card:
                    self.hand[i] = new_card
                    return new_card
                else:
                    return None  # Deck is empty; TODO: Make a check to not attempt drawing a card if empty.
        return None  # Hand is full; TODO: I dont like this.
    
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
        raise ValueError(f'Invalid action {action}')

    def spend_resources(self, card) -> None:
        if card.is_playable(self.resources):
            self.resources[card.material_type][1] -= card.cost
        else:
            raise ValueError('Card cost is higher than the player resource value')