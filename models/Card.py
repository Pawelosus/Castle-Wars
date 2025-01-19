from dataclasses import dataclass
from resources.resource_names import resource_names

@dataclass(frozen=True)
class Card:
    id: int
    material_type: str
    cost: int
    name: str
    effect: str
    
    def is_playable(self, player_resources) -> bool:
        # Ensure material_type is treated as an integer when accessing player_resources
        return player_resources[int(self.material_type)][1] >= self.cost

    def get_effect_value(self, keyword: str) -> int:
        """Parses the card's effect and returns the numeric value for the specified keyword."""
        actions = self.effect.split(';')
        for action in actions:
            action_parts = action.split(' ')
            if keyword in action_parts:
                action_value = action_parts[-1]
                if action_value[0] == '+':
                    return int(action_value[1:])
                elif action_value[0] == '-':
                    return -int(action_value[1:])
                return int(action_value)  # Assume the value is positive if a sign is missing
        return 0

    def to_state(self) -> dict:
        """Convert the Card instance to a dictionary."""
        return self.__dict__

    @classmethod
    def from_state(cls, state: dict) -> 'Card':
        """Create a Card instance from a dictionary."""
        return cls(**state)
