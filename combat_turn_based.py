import pygame
import random
import sys
from attribute import hero_attributes, enemy_attributes, ability_effects, item_effects

pygame.init()


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Starry Night - Turn-Based Combat")

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Hero:
    def __init__(self, attr):
        self.name = attr["name"]
        self.health = attr["health"]
        self.max_health = attr["health"]
        self.mana = attr["mana"]
        self.strength = attr["strength"]
        self.defense = attr["defense"]
        self.abilities = attr["abilities"]
        self.items = attr["items"]
        self.total_damage_dealt = 0
        self.total_healing_done = 0

    def attack(self, enemy):
        damage = max(1, self.strength - enemy.strength // 5)
        enemy.take_damage(damage)
        self.total_damage_dealt += damage
        return f"{self.name} attacks for {damage} damage!"

    def defend(self):
        self.defense += 5
        return f"{self.name} defends and increases defense!"

    def use_ability(self, ability, enemy):
        if ability in ability_effects:
            result = ability_effects[ability](self, enemy)
            return result
        return "Invalid ability!"

    def use_item(self, item, enemy):
        if item in item_effects:
            result = item_effects[item](self, enemy)
            return result
        return "Invalid item!"

    def take_damage(self, amount):
        self.health -= amount

class Enemy:
    def __init__(self, attr):
        self.name = attr["name"]
        self.health = attr["health"]
        self.max_health = attr["health"]
        self.strength = attr["strength"]
        self.abilities = attr["abilities"]

    def attack(self, hero):
        move = random.choice(self.abilities)
        damage = max(1, self.strength - hero.defense // 4)
        hero.take_damage(damage)
        return f"{self.name} uses {move} and deals {damage} damage!"

    def take_damage(self, amount):
        self.health -= amount

class Battle:
    def __init__(self, hero, enemy):
        self.hero = hero
        self.enemy = enemy
        self.is_hero_turn = True
        self.game_over = False
        self.action_message = "Choose your action!"
        self.show_abilities = False
        self.show_items = False
        self.battle_report = ""
        self.waiting_for_enemy = False
        self.enemy_turn_time = None

    def process_action(self, action, ability_choice=None, item_choice=None):

        if self.game_over or not self.is_hero_turn:
            return

        if action == "attack":
            self.action_message = self.hero.attack(self.enemy)
        elif action == "defend":
            self.action_message = self.hero.defend()
        elif action == "item":
            if item_choice:
                self.action_message = self.hero.use_item(item_choice, self.enemy)
                self.show_items = False
            else:
                self.show_items = not self.show_items
                return
        elif action == "ability":
            if ability_choice:
                self.action_message = self.hero.use_ability(ability_choice, self.enemy)
                self.show_abilities = False
            else:
                self.show_abilities = not self.show_abilities
                return

        self.is_hero_turn = False
        self.waiting_for_enemy = True
        self.enemy_turn_time = pygame.time.get_ticks() + 1000
        self.check_win()

    def update(self):
        if self.waiting_for_enemy and pygame.time.get_ticks() >= self.enemy_turn_time:
            if not self.game_over:
                self.action_message += f" {self.enemy.attack(self.hero)}"
                self.check_win()
            self.is_hero_turn = True
            self.waiting_for_enemy = False

    def check_win(self):
        if self.hero.health <= 0:
            self.action_message = "You lose!"
            self.game_over = True
            self.battle_report = self.generate_combat_report()
        elif self.enemy.health <= 0:
            self.action_message = "You win!"
            self.game_over = True
            self.battle_report = self.generate_combat_report()

    def generate_combat_report(self):
        report = f"{self.hero.name} dealt {self.hero.total_damage_dealt} damage.\n"
        report += f"{self.hero.name} healed {self.hero.total_healing_done} HP.\n"
        report += f"{self.enemy.name} dealt {self.hero.total_damage_dealt} damage.\n"
        return report



hero = Hero(hero_attributes)
enemy = Enemy(enemy_attributes)
battle = Battle(hero, enemy)

def draw_button(text, x, y, w, h, color=BLUE):
    rect = pygame.draw.rect(screen, color, (x, y, w, h))
    label = font.render(text, True, WHITE)
    screen.blit(label, (x + w//2 - label.get_width()//2, y + h//2 - label.get_height()//2))
    return rect

def draw_battle_screen():
    screen.fill(WHITE)

    pygame.draw.rect(screen, RED, (50, 50, 200, 30))
    pygame.draw.rect(screen, GREEN, (50, 50, 200 * (hero.health / hero.max_health), 30))
    pygame.draw.rect(screen, RED, (WIDTH - 250, 50, 200, 30))
    pygame.draw.rect(screen, GREEN, (WIDTH - 250, 50, 200 * (enemy.health / enemy.max_health), 30))

    screen.blit(font.render(f"{hero.name} HP: {hero.health}", True, BLACK), (50, 90))
    screen.blit(font.render(f"{enemy.name} HP: {enemy.health}", True, BLACK), (WIDTH - 250, 90))
    screen.blit(font.render(battle.action_message, True, BLACK), (WIDTH // 2 - 200, HEIGHT - 60))

    buttons = {}

    if not battle.game_over and battle.is_hero_turn:
        buttons["attack"] = draw_button("Attack", 50, HEIGHT - 150, 150, 50)
        buttons["defend"] = draw_button("Defend", 250, HEIGHT - 150, 150, 50)
        buttons["ability"] = draw_button("Ability", 450, HEIGHT - 150, 150, 50)
        buttons["item"] = draw_button("Item", 650, HEIGHT - 150, 100, 50)

    if battle.show_abilities:
        for i, ab in enumerate(hero.abilities):
            ab_btn = draw_button(ab, 100 + i * 170, HEIGHT // 2 - 50, 150, 50)
            cost = ability_effects[ab].__doc__ if ability_effects.get(ab).__doc__ else ""
            cost_txt = small_font.render(cost, True, BLACK)
            screen.blit(cost_txt, (ab_btn.x + ab_btn.width//2 - cost_txt.get_width()//2, ab_btn.y + 55))
            buttons[f"ability_{i}"] = ab_btn

    if battle.show_items:
        for i, item in enumerate(hero.items):
            item_btn = draw_button(item, 100 + i * 170, HEIGHT // 2 - 50, 150, 50)
            effect = item_effects[item].__doc__ if item_effects.get(item).__doc__ else ""
            effect_txt = small_font.render(effect, True, BLACK)
            screen.blit(effect_txt, (item_btn.x + item_btn.width//2 - effect_txt.get_width()//2, item_btn.y + 55))
            buttons[f"item_{i}"] = item_btn

    if battle.game_over:
        screen.fill(WHITE)
        victory_text = "Victory!" if battle.hero.health > 0 else "Defeat!"
        screen.blit(font.render(victory_text, True, GREEN if battle.hero.health > 0 else RED), (WIDTH // 2 - 100, HEIGHT // 4))
        report_text = font.render("Combat Report:", True, BLACK)
        screen.blit(report_text, (50, HEIGHT // 2))

        lines = battle.battle_report.split("\n")
        y_offset = HEIGHT // 2 + 40
        for line in lines:
            screen.blit(small_font.render(line, True, BLACK), (50, y_offset))
            y_offset += 30

        buttons["restart"] = draw_button("Restart", WIDTH // 2 - 75, HEIGHT - 150, 150, 50)
        buttons["quit"] = draw_button("Quit", WIDTH // 2 - 75, HEIGHT - 90, 150, 50)

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
                        battle.process_action("ability", ability_choice=hero.abilities[idx])
                    elif key.startswith("item_"):
                        idx = int(key.split("_")[1])
                        battle.process_action("item", item_choice=hero.items[idx])
                    elif key == "restart":
                        hero = Hero(hero_attributes)
                        enemy = Enemy(enemy_attributes)
                        battle = Battle(hero, enemy)
                    elif key == "quit":
                        running = False
