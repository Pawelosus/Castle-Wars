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