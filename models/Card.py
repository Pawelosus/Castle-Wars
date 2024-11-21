from resources.resource_names import resource_names

class Card:
    def __init__(self, id, material_type, cost, name, effect) -> None:
        self.id = id
        self.material_type = int(material_type)
        self.cost = cost
        self.name = name
        self.effect = effect
    
    def __str__(self) -> str:
        return f'{self.name}: {self.effect}\n\tCost: {self.cost} {resource_names[str(self.material_type)][1]}'

    def is_playable(self, player_resources) -> bool:
        return player_resources[self.material_type][1] >= self.cost

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
