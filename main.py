import json

class Game:
    def __init__(self):
        self.default_deck = None
        pass
    
    def show_menu(self):
        print("Castle Wars: Python Edition")
        print("===========================")
        print("1. Singleplayer")
        print("2. Multiplayer")
        print("3. Create deck")
        print("4. Import deck")
        print("0. Exit")

    def play():
        pass

    def start(self):
        on = True
        while on:
            self.show_menu()
            option = input()
            if option == "1":
                pass
            elif option == "2":
                pass
            elif option == "3":
                pass
            elif option == "4":
                pass
            elif option == "0":
                on = False
            
        
class Player:
    def __init__(self):
        self.deck = Deck()

class Deck:
    def __init__(self):
        self.cards = self.init_cards()
        self.deck = self.init_deck()
        self.deck_size = self.get_deck_size()

    def init_cards(self):
        with open('cards.json') as f:
            return json.load(f)
    
    def init_deck(self):
        """Init deck with default deck."""
        self.deck_size = 0
        with open('default_deck.json') as f:
            return json.load(f)
    
    def get_deck_size(self):
        current_deck_size = 0
        for value in self.deck.values():
            current_deck_size += value
        
        return current_deck_size
        


game = Game()
deck = Deck()

print(deck.deck_size)