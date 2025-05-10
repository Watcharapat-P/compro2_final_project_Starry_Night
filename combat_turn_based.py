import pygame
import random
import sys
from attribute import hero_attributes, goblin_attributes, ability_effects, item_effects

pygame.init()


WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Starry Night - Turn-Based Combat")

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
large_font = pygame.font.Font(None, 72) # Added a larger font


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Character:
    def __init__(self, attr):
        self.name = attr["name"]
        self.health = attr["health"]
        self.max_health = attr["health"]
        self.mana = attr["mana"]
        self.max_mana = attr["mana"]
        self.strength = attr["strength"]
        self.defense = attr["defense"]
        self.abilities = attr["abilities"]
        self.items = attr["items"]
        self.total_damage_dealt = 0
        self.total_healing_done = 0
        self.defend_stance = 0

    def attack(self, target):
        if target.defend_stance == 1:
            damage = max(1, self.strength - target.defense // 5) // 2
        else:
            damage = max(1, self.strength - target.defense // 5)
        target.take_damage(damage)
        self.total_damage_dealt += damage
        return f"{self.name} attacks for {damage} damage!"

    def defend(self):
        self.defend_stance = 1
        return f"{self.name} defends!"

    def use_ability(self, ability, target):
        if ability in ability_effects:
            result = ability_effects[ability](self, target)
            return result
        return "Invalid ability!"

    def use_item(self, item, target):
        if item in item_effects:
            result = item_effects[item](self, target)
            return result
        return "Invalid item!"

    def take_damage(self, amount):
        if self.defend_stance == 1:
            self.health -= amount // 2
            self.defend_stance = 0
        else:
            self.health -= amount

    def take_turn(self, opponent):
        move_type = random.choice(["attack", "defend", "ability", "item"])

        if move_type == "attack":
            return self.attack(opponent)

        elif move_type == "defend":
            return self.defend()

        elif move_type == "ability" and self.abilities:
            ability = random.choice(self.abilities)
            return self.use_ability(ability, opponent)

        elif move_type == "item" and self.items:
            item = random.choice(self.items)
            return self.use_item(item, opponent)

class Battle:
    def __init__(self, character1, character2):
        self.character1 = character1
        self.character2 = character2
        self.is_character1_turn = True
        self.game_over = False
        self.action_message = "Choose your action!"
        self.show_abilities = False
        self.show_items = False
        self.battle_report = ""
        self.waiting_for_enemy = False
        self.enemy_turn_time = None

    def process_action(self, action, ability_choice=None, item_choice=None):

        if self.game_over or not self.is_character1_turn:
            return

        if action == "attack":
            self.action_message = self.character1.attack(self.character2)
        elif action == "defend":
            self.action_message = self.character1.defend()
        elif action == "item":
            if item_choice:
                self.action_message = self.character1.use_item(item_choice, self.character2)
                self.show_items = False
            else:
                self.show_items = not self.show_items
                return
        elif action == "ability":
            if ability_choice:
                self.action_message = self.character1.use_ability(ability_choice, self.character2)
                self.show_abilities = False
            else:
                self.show_abilities = not self.show_abilities
                return

        self.is_character1_turn = False
        self.waiting_for_enemy = True
        self.enemy_turn_time = pygame.time.get_ticks() + 1000
        self.check_win()

    def update(self):
        if self.waiting_for_enemy and pygame.time.get_ticks() >= self.enemy_turn_time:
            if not self.game_over:
                self.action_message = f" {self.character2.take_turn(self.character1)}"
                self.check_win()
            self.is_character1_turn = True
            self.waiting_for_enemy = False

    def check_win(self):
        if self.character1.health <= 0:
            self.action_message = "You lose!"
            self.game_over = True
            self.battle_report = self.generate_combat_report()
        elif self.character2.health <= 0:
            self.action_message = "You win!"
            self.game_over = True
            self.battle_report = self.generate_combat_report()

    def generate_combat_report(self):
        report = f"{self.character1.name} dealt {self.character1.total_damage_dealt} damage.\n"
        report += f"{self.character1.name} healed {self.character1.total_healing_done} HP.\n"
        report += f"{self.character2.name} dealt {self.character2.total_damage_dealt} damage.\n"
        report += f"{self.character2.name} healed {self.character2.total_healing_done} HP.\n"
        return report



hero = Character(hero_attributes)
enemy = Character(goblin_attributes)
battle = Battle(hero, enemy)

def draw_button(text, x, y, w, h, color=BLUE):
    rect = pygame.draw.rect(screen, color, (x, y, w, h))
    label = font.render(text, True, WHITE)
    screen.blit(label, (x + w//2 - label.get_width()//2, y + h//2 - label.get_height()//2))
    return rect

def draw_battle_screen():
    screen.fill(WHITE)

    pygame.draw.rect(screen, RED, (50, 60, 200, 30))
    pygame.draw.rect(screen, GREEN, (50, 60, 200 * (battle.character1.health / battle.character1.max_health), 30))
    pygame.draw.rect(screen, RED, (50, 95, 200, 20))
    pygame.draw.rect(screen, BLUE, (50, 95, 200 * (battle.character1.mana / battle.character1.max_mana), 20))
    pygame.draw.rect(screen, RED, (WIDTH - 250, 60, 200, 30))
    pygame.draw.rect(screen, GREEN, (WIDTH - 250, 60, 200 * (battle.character2.health / battle.character2.max_health), 30))

    screen.blit(font.render(f"{battle.character1.name} HP: {battle.character1.health}", True, BLACK), (50, 30))
    screen.blit(font.render(f"{battle.character2.name} HP: {battle.character2.health}", True, BLACK), (WIDTH - 250, 30))
    screen.blit(font.render(battle.action_message, True, BLACK), (WIDTH // 2 - 200, HEIGHT - 180))

    buttons = {}

    if not battle.game_over and battle.is_character1_turn:
        button_width = 180
        button_height = 60
        start_x = (WIDTH - (4 * button_width + 3 * 20)) / 2
        y_position = HEIGHT - 100
        buttons["attack"] = draw_button("Attack", start_x, y_position, button_width, button_height)
        buttons["defend"] = draw_button("Defend", start_x + button_width + 20, y_position, button_width, button_height)
        buttons["ability"] = draw_button("Ability", start_x + 2 * (button_width + 20), y_position, button_width, button_height)
        buttons["item"] = draw_button("Item", start_x + 3 * (button_width + 20), y_position, button_width, button_height)

    if battle.show_abilities:
        ability_button_width = 180
        ability_button_height = 60
        ability_start_x = (WIDTH - (len(battle.character1.abilities) * ability_button_width + (len(battle.character1.abilities) -1) * 20)) / 2
        ability_y_position = HEIGHT // 2 + 100
        for i, ab in enumerate(battle.character1.abilities):
            ab_btn = draw_button(ab, ability_start_x + i * (ability_button_width + 20), ability_y_position, ability_button_width, ability_button_height)
            cost = ability_effects[ab].__doc__ if ability_effects.get(ab).__doc__ else ""
            cost_txt = small_font.render(cost, True, BLACK)
            screen.blit(cost_txt, (ab_btn.x + ab_btn.width//2 - cost_txt.get_width()//2, ab_btn.y + ability_button_height + 5))
            buttons[f"ability_{i}"] = ab_btn

    if battle.show_items:
        item_button_width = 180
        item_button_height = 60
        item_start_x = (WIDTH - (len(battle.character1.items) * item_button_width + (len(battle.character1.items) -1) * 20)) / 2
        item_y_position = HEIGHT // 2 + 100
        for i, item in enumerate(battle.character1.items):
            item_btn = draw_button(item, item_start_x + i * (item_button_width + 20), item_y_position, item_button_width, item_button_height)
            effect = item_effects[item].__doc__ if item_effects.get(item).__doc__ else ""
            effect_txt = small_font.render(effect, True, BLACK)
            screen.blit(effect_txt, (item_btn.x + item_btn.width//2 - effect_txt.get_width()//2, item_btn.y + item_button_height + 5))
            buttons[f"item_{i}"] = item_btn

    if battle.game_over:
        screen.fill(WHITE)
        victory_text = "Victory!" if battle.character1.health > 0 else "Defeat!"
        text_rect = large_font.render(victory_text, True, GREEN if battle.character1.health > 0 else RED).get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(large_font.render(victory_text, True, GREEN if battle.character1.health > 0 else RED), text_rect)
        report_text = font.render("Combat Report:", True, BLACK)
        report_x = 50
        report_y = HEIGHT // 2 - 50
        screen.blit(report_text, (report_x, report_y))

        lines = battle.battle_report.split("\n")
        y_offset = report_y + 40
        for line in lines:
            screen.blit(small_font.render(line, True, BLACK), (report_x, y_offset))
            y_offset += 30
        restart_button_width = 180
        restart_button_height = 60
        restart_x = WIDTH // 2 - (restart_button_width + 20) // 2
        quit_x = WIDTH // 2 + (restart_button_width + 20) // 2
        buttons["restart"] = draw_button("Restart", restart_x, HEIGHT - 150, restart_button_width, restart_button_height)
        buttons["quit"] = draw_button("Quit", quit_x, HEIGHT - 150, restart_button_width, restart_button_height)

    pygame.display.flip()
    return buttons



running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)
    battle.update()
    buttons = draw_battle_screen()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for key, btn in buttons.items():
                if btn.collidepoint(mx, my):
                    if key == "attack":
                        battle.process_action("attack")
                    elif key == "defend":
                        battle.process_action("defend")
                    elif key == "item":
                        battle.process_action("item")
                    elif key == "ability":
                        battle.process_action("ability")
                    elif key.startswith("ability_"):
                        idx = int(key.split("_")[1])
                        battle.process_action("ability", ability_choice=battle.character1.abilities[idx])
                    elif key.startswith("item_"):
                        idx = int(key.split("_")[1])
                        battle.process_action("item", item_choice=battle.character1.items[idx])
                    elif key == "restart":
                        character1 = Character(hero_attributes)
                        character2 = Character(goblin_attributes)
                        battle = Battle(character1, character2)
                    elif key == "quit":
                        running = False
