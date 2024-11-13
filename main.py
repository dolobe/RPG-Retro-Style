import random
import json

class GameMainMenu:
    @staticmethod
    def main_menu():
        print("MAIN MENU:")
        print("1. Create New Game")
        print("2. Load Saved Game")
        print("3. About")
        print("4. Exit")

    @staticmethod
    def create_new_game():
        print("Creating New Game")
        name = input("Please Enter your name: ")
        age = input("Enter your age: ")
        print(f"Hello, {name}! Welcome to the game.")
        
        player = Player(name=name, age=age, weapon="Knife", health=100, strength=10, defense=5, xp=0, gold=50)
        Game().start(player)
        player.save_game()
        return player
    
    @staticmethod
    def load_saved_game():
        try:
            with open("savegame.json", "r") as file:
                data = json.load(file)
                player = Player(
                    name=data['name'],
                    age=data['age'],
                    weapon=data['weapon'],
                    health=data['health'],
                    strength=data['strength'],
                    defense=data['defense'],
                    xp=data['xp'],
                    gold=data['gold']
                )
                player.inventory.potions = data['inventory']['potions']
                player.inventory.attack_boost = data['inventory']['attack_boost']
                player.inventory.defense_boost = data['inventory']['defense_boost']
                print(f"Game Loaded! Welcome back, {player.name}.")
                player.inventory.show_inventory()
                return player
        except FileNotFoundError:
            print("No saved game found.")
            return None
        except json.JSONDecodeError:
            print("Error loading saved game. File may be corrupted.")
            return None
        
    @staticmethod
    def main():
        while True:
            GameMainMenu.main_menu()
            choice = input("> ")

            if choice == '1':
                GameMainMenu.create_new_game()
            elif choice == '2':
                player = GameMainMenu.load_saved_game()
                if player:
                    print(f"Loaded {player.name}'s game.")
            elif choice == '3':
                print("About - This is a simple text adventure game.")
            elif choice == '4':
                print("Exiting game. Goodbye!")
                break
            else:
                print("Invalid choice. Please select a valid option.")


class Entity:
    def __init__(self, name, health, strength, defense):
        self.name = name
        self.health = health
        self.strength = strength
        self.defense = defense

class Character:
    def __init__(self, name, attack, defense, health):
        self.name = name
        self.attack = attack
        self.defense = defense
        self.health = health

    def attack(self, target):
        """Effectue une attaque sur la cible (player ou enemy)"""
        chance_to_hit = random.randint(1, 100)

        if chance_to_hit > target.defense:
            damage = max(self.attack - target.defense, 0)
            print(f"{self.name} attaque {target.name} et inflige {damage} de dégâts.")
            target.health -= damage
        else:
            print(f"{self.name} attaque {target.name}, mais l'attaque échoue !")
        
        return target.health
    
class Player(Entity, Character):
    def __init__(self, name, age, weapon, health, strength, defense, xp, gold):
        super().__init__(name, health, strength, defense)
        self.age = age
        self.weapon = weapon
        self.xp = xp
        self.level = 1
        self.inventory = Inventory(potions=20, attack_boost=5, defense_boost=5)
        self.buy_inventory = BuyInventory()
        self.gold = gold

    def choose_inventory(self):
        print("Choose the items for your inventory:")

        while True:
            print("\n1. Use inventory\n2. Buy inventory items\n3. Exit")
            choice = input("> ")

            if choice == '1':
                print("1. Use a potion\n2. Use an attack boost\n3. Use a defense boost\n4. Exit")
                choice = input("> ")

                if choice == '1':
                    self.inventory.use_potion()
                elif choice == '2':
                    if self.inventory.attack_boost > 0:
                        self.inventory.use_attack_boost(self)
                    else:
                        print("No more attack boosts! Would you like to buy one for 50 gold? (y/n)")
                        if input("> ").lower() == 'y' and self.gold >= 50:
                            self.buy_inventory.buy_attack_boost(1, self.gold)
                        else:
                            print("Not enough gold or purchase cancelled.")
                elif choice == '3':
                    if self.inventory.defense_boost > 0:
                        self.inventory.use_defense_boost(self)
                    else:
                        print("No more defense boosts! Would you like to buy one for 50 gold? (y/n)")
                        if input("> ").lower() == 'y' and self.gold >= 50:
                            self.buy_inventory.buy_defense_boost(1, self.gold)
                        else:
                            print("Not enough gold or purchase cancelled.")
                elif choice == '4':
                    print("Exiting inventory use selection.")
                break

            elif choice == '2':
                print("1. Buy a potion\n2. Buy an attack boost\n3. Buy a defense boost\n4. Exit")
                purchase_choice = input("> ")

                if purchase_choice == '1':
                    amount = int(input("How many potions would you like to buy? "))
                    self.gold = self.buy_inventory.buy_potions(amount, self.gold)
                elif purchase_choice == '2':
                    amount = int(input("How many attack boosts would you like to buy? "))
                    self.gold = self.buy_inventory.buy_attack_boost(amount, self.gold)
                elif purchase_choice == '3':
                    amount = int(input("How many defense boosts would you like to buy? "))
                    self.gold = self.buy_inventory.buy_defense_boost(amount, self.gold)
                elif purchase_choice == '4':
                    print("Exiting purchase selection.")
                else:
                    print("Invalid choice.")
                
            elif choice == '3':
                print("Exiting inventory selection.")
                break

            else:
                print("Invalid choice. Please select a valid option.")

    def attack(self, enemy):
        base_damage = max(0, self.strength - enemy.defense)

        attack_success = random.random() < 0.9

        if attack_success:
            print(f"{self.name} attacks {enemy.name} with {self.weapon} and causes {base_damage} damage.")
            return base_damage
        else:
            print(f"{self.name}'s attack on {enemy.name} failed!")
            return 0
    
    def take_damage(self, damage):
        damage_after_defense = max(0, damage - self.defense)
        self.health -= damage_after_defense
        if self.health <= 0:
            print(f"{self.name} has been defeated.")
            return False
        return True
    
    def gain_xp(self, amount):
        self.xp += amount
        print(f"{self.name} gained {amount} XP.")
        self.level_up()
        
    def save_game(self):
        data = {
            'name': self.name,
            'age': self.age,
            'weapon': self.weapon,
            'health': self.health,
            'strength': self.strength,
            'defense': self.defense,
            'xp': self.xp,
            'gold': self.gold,
            'inventory': {
                'potions': self.inventory.potions,
                'attack_boost': self.inventory.attack_boost,
                'defense_boost': self.inventory.defense_boost
            }
        }
        with open("savegame.json", "w") as file:
            json.dump(data, file)
        print("Game saved successfully.")


class Enemy(Entity, Character):
    def __init__(self, name, level, health, strength, defense):
        super().__init__(name, health, strength, defense)
        self.level = level

    def attack(self, player):
        base_damage = max(0, self.strength - player.defense)
        
        attack_success = random.random() < 0.9

        if attack_success:
            print(f"{self.name} attacks {player.name} and causes {base_damage} damage.")
            return base_damage
        else:
            print(f"{self.name}'s attack on {player.name} failed!")
            return 0


class Inventory:
    def __init__(self, potions=0, attack_boost=0, defense_boost=0):
        self.potions = potions
        self.attack_boost = attack_boost
        self.defense_boost = defense_boost

    def use_potion(self):
        if self.potions > 0:
            self.potions -= 1
            print(f"Used a potion. Remaining potions: {self.potions}")
        else:
            print("No potions left!")

    def show_inventory(self):
        print(f"Inventory:\nPotions: {self.potions}\nAttack Boosts: {self.attack_boost}\nDefense Boosts: {self.defense_boost}")
        

class UseInventory(Inventory):
    def __init__(self, potions=0, attack_boost=0, defense_boost=0):
        super().__init__(potions, attack_boost, defense_boost)
        
    def use_potion(self):
        super().use_potion()
    
    def use_attack_boost(self, player):
        if self.attack_boost > 0:
            player.strength += 5
            self.attack_boost -= 1
            print(f"Your strength increased by 5. Current strength: {player.strength}")
        else:
            print("No attack boosts left!")
        
    def use_defense_boost(self, player):
        if self.defense_boost > 0:
            player.defense += 5
            self.defense_boost -= 1
            print(f"Your defense increased by 5. Current defense: {player.defense}")
        else:
            print("No defense boosts left!")

class BuyInventory(Inventory):
    def buy_potions(self, amount, gold):
        cost = 10
        total_cost = amount * cost

        if total_cost <= gold:
            self.potions += amount
            gold -= total_cost
            print(f"Bought {amount} potions for {total_cost} gold.")
        else:
            print("Not enough gold!")
        return gold

    def buy_attack_boost(self, amount, gold):
        cost = 50
        total_cost = amount * cost

        if total_cost <= gold:
            self.attack_boost += amount
            gold -= total_cost
            print(f"Bought {amount} attack boosts for {total_cost} gold.")
        else:
            print("Not enough gold!")
        return gold

    def buy_defense_boost(self, amount, gold):
        cost = 50
        total_cost = amount * cost

        if total_cost <= gold:
            self.defense_boost += amount
            gold -= total_cost
            print(f"Bought {amount} defense boosts for {total_cost} gold.")
        else:
            print("Not enough gold!")
        return gold

class Game:
    def start(self, player):
        while True:
            print(f"\nWelcome, {player.name}! What would you like to do?")
            print("1. Explore")
            print("2. View Inventory")
            print("3. View Stats")
            print("4. Save and Exit")

            choice = input("> ")

            if choice == '1':
                self.explore(player)
                print("Exploring the world...")
                enemy = Enemy(name="Goblin", level=1, health=30, strength=5, defense=3)
                print(f"A wild {enemy.name} appears!")
                while enemy.health > 0 and player.health > 0:
                    print(f"\n{player.name}'s health: {player.health}, {enemy.name}'s health: {enemy.health}")
                    print("1. Attack\n2. Use Item")
                    action = input("> ")

                    if action == '1':
                        damage = player.attack(enemy)
                        enemy.health -= damage
                        if enemy.health <= 0:
                            print(f"{enemy.name} has been defeated!")
                            player.gain_xp(50)
                            player.gold += 20
                            print(f"{player.name} earned 20 gold!")
                            break
                    elif action == '2':
                        player.choose_inventory()
                    else:
                        print("Invalid choice.")
                    
                    if enemy.health > 0:
                        damage = enemy.attack(player)
                        if not player.take_damage(damage):
                            break

            elif choice == '2':
                player.inventory.show_inventory()

            elif choice == '3':
                print(f"\n{player.name}'s Stats:")
                print(f"Level: {player.level}")
                print(f"Health: {player.health}")
                print(f"Strength: {player.strength}")
                print(f"Defense: {player.defense}")
                print(f"XP: {player.xp}")
                print(f"Gold: {player.gold}")
            
            elif choice == '4':
                player.save_game()
                print("Exiting the game.")
                break

            else:
                print("Invalid choice.")
                
    def explore(self, player):
        print("\nYou are standing in an open field. Where would you like to go?")
        print("1. Go North (N)")
        print("2. Go South (S)")
        print("3. Go East (E)")
        print("4. Go West (W)")
        print("5. Return to Menu")

        choice = input("> ").upper()

        if choice == 'North' or choice == 'N':
            self.explore_direction(player, "North")
        elif choice == 'South' or choice == 'S':
            self.explore_direction(player, "South")
        elif choice == 'East' or choice == 'E':
            self.explore_direction(player, "East")
        elif choice == 'West' or choice == 'W':
            self.explore_direction(player, "West")
        elif choice == '5':
            print("Returning to main menu.")
            return
        else:
            print("Invalid choice.")
            self.explore(player)

    def explore_direction(self, player, direction):
        print(f"\nYou head {direction}.")
        event = random.choice(["nothing", "enemy", "treasure"])

        if event == "nothing":
            print(f"Nothing happens as you travel {direction}.")
        elif event == "enemy":
            enemy = Enemy(name="Goblin", level=1, health=30, strength=5, defense=3)
            print(f"A wild {enemy.name} appears!")
            self.battle(player, enemy)
        elif event == "treasure":
            print(f"You found some treasure on the road to {direction}!")
            player.gold += 10
            print(f"Your current gold: {player.gold}")
    
    def battle(self, player, enemy):
        while enemy.health > 0 and player.health > 0:
            print(f"\n{player.name}'s health: {player.health}, {enemy.name}'s health: {enemy.health}")
            print("1. Attack\n2. Use Item")
            action = input("> ")

            if action == '1':
                damage = player.attack(enemy)
                enemy.health -= damage
                if enemy.health <= 0:
                    print(f"{enemy.name} has been defeated!")
                    player.gain_xp(50)
                    player.gold += 20
                    print(f"{player.name} earned 20 gold!")
                    break
            elif action == '2':
                player.choose_inventory()
            else:
                print("Invalid choice.")

            if enemy.health > 0:
                damage = enemy.attack(player)
                if not player.take_damage(damage):
                    break

if __name__ == "__main__":
    GameMainMenu.main()
