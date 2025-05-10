import pygame
import random
import os
from attribute import hero_attributes, goblin_attributes, ability_effects, item_effects

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Starry Night - Turn-Based Combat")

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
large_font = pygame.font.Font(None, 72)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except pygame.error:
        print(f"Could not load sound: {path}")
        return None

def load_sprite_frames(path, frame_width, frame_height, columns, rows):
    sheet = pygame.image.load(path).convert_alpha()
    frames = []
    for row in range(rows):
        for col in range(columns):
            rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
            if rect.right > sheet.get_width() or rect.bottom > sheet.get_height():
                raise ValueError(f"Frame {rect} is out of bounds for image size {sheet.get_size()}")
            frame = sheet.subsurface(rect)
            frames.append(frame)
    return frames



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
        self.sfx_path = attr.get("sfx", "")
        self.sprite_folder = attr.get("sprite", None)

        self.animations = {}
        if self.sprite_folder:
            idle_path = f"{self.sprite_folder}/idle.png"
            attack_path = f"{self.sprite_folder}/attack.png"
            parry_path = f"{self.sprite_folder}/parry.png"
            fireball_path = f"{self.sprite_folder}/fireball.png"
            heal_path = f"{self.sprite_folder}/heal.png"

            if os.path.exists(idle_path):
                self.animations["idle"] = load_sprite_frames(idle_path, 32, 32, 1, 1)
            if os.path.exists(attack_path):
                self.animations["attack"] = load_sprite_frames(attack_path, 32, 32, 4, 1)
            if os.path.exists(parry_path):
                self.animations["parry"] = load_sprite_frames(parry_path, 32, 32, 4, 1)
            if os.path.exists(fireball_path):
                self.animations["fireball"] = load_sprite_frames(fireball_path, 64, 64, 4, 5)
            if os.path.exists(heal_path):
                self.animations["heal"] = load_sprite_frames(heal_path, 64, 64, 5, 2)

        self.current_animation = "idle"
        self.current_frame = 0
        self.animation_timer = 0
        self.is_animating = False
        self.total_m_dam = 0
        self.total_damage_dealt = 0
        self.total_healing_done = 0
        self.defend_stance = 0
        self.sounds = self.load_sounds()
        self.status_effect_animation = None
        self.status_effect_frame = 0
        self.status_effect_timer = 0

    def load_sounds(self):
        actions = ["attack", "defend", "parry"] + self.abilities + self.items
        sounds = {}
        for name in actions:
            path = f"{self.sfx_path}/{name}.wav"
            if os.path.exists(path):
                sounds[name] = load_sound(path)
        return sounds

    def play_sound(self, action):
        sound = self.sounds.get(action)
        if sound:
            sound.play()

    def start_animation(self, animation):
        if animation in self.animations:
            self.current_animation = animation
            self.current_frame = 0
            self.animation_timer = 0
            self.is_animating = True

    def animate(self):
            # Main animation logic
            if self.is_animating:
                self.animation_timer += 1
                if self.animation_timer >= 5:
                    self.current_frame += 1
                    self.animation_timer = 0

                    # Parry logic for Goblin
                    if self.name == "Goblin" and self.current_animation == "attack":
                        if self.current_frame == 2:
                            battle.parry_window = True
                            battle.parry_timer = pygame.time.get_ticks()
                        elif self.current_frame == 4:
                            battle.parry_window = False

                if self.current_frame >= len(self.animations[self.current_animation]):
                    self.current_frame = 0
                    self.is_animating = False
                    self.current_animation = "idle"

            # Status effect animation logic (e.g. fireball burning on character)
            if self.status_effect_animation:
                self.status_effect_timer += 1
                if self.status_effect_timer >= 5:
                    self.status_effect_timer = 0
                    self.status_effect_frame += 1
                    if self.status_effect_frame >= len(self.animations[self.status_effect_animation]):
                        self.status_effect_animation = None
                        self.status_effect_frame = 0


    def attack(self, target):
        damage = max(1, self.strength - target.defense // 5)
        if target.defend_stance == 1:
            damage //= 2
        p = target.take_damage(damage)
        if p == 1:
            target.play_sound("parry")
            target.start_animation("parry")
            target.total_m_dam += damage
            return "Parried"
        else:
            self.total_damage_dealt += damage
            self.play_sound("attack")
            self.start_animation("attack")
            return f"{self.name} attacks for {damage} damage!"

    def defend(self):
        self.defend_stance = 1
        self.play_sound("defend")
        return f"{self.name} defends!"

    def use_ability(self, ability, target):
        if ability in ability_effects:
            result = ability_effects[ability](self, target)
            self.play_sound(ability)
            if ability == "Fireball":
                self.start_animation("attack")
                target.status_effect_animation = "fireball"
                target.status_effect_frame = 0
                target.status_effect_timer = 0
            if ability == "Heal":
                self.status_effect_animation = "heal"
                self.status_effect_frame = 0
                self.status_effect_timer = 0
            return result
        return "Invalid ability!"

    def use_item(self, item, target):
        if item in item_effects:
            result = item_effects[item](self, target)
            self.play_sound(item)
            return result
        return "Invalid item!"

    def take_damage(self, amount):
        if self.name == "Hero" and battle.parry_success:
            battle.parry_success = False
            battle.parry_window = False
            battle.action_message = "Parry! No damage taken!"
            return 1

        if self.defend_stance == 1:
            self.health -= amount // 2
            self.defend_stance = 0
        else:
            self.health -= amount

    def take_turn(self, opponent):
        move_type = random.choice(["attack"])
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

        # Parry mechanic
        self.parry_window = False
        self.parry_success = False
        self.parry_timer = 0

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
                self.action_message = f"{self.character2.take_turn(self.character1)}"
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
        report += f"{self.character1.name} mitigated {self.character1.total_m_dam} damage.\n"
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

    # Bars
    pygame.draw.rect(screen, RED, (50, 60, 200, 30))
    pygame.draw.rect(screen, GREEN, (50, 60, 200 * (battle.character1.health / battle.character1.max_health), 30))
    pygame.draw.rect(screen, RED, (50, 95, 200, 20))
    pygame.draw.rect(screen, BLUE, (50, 95, 200 * (battle.character1.mana / battle.character1.max_mana), 20))
    pygame.draw.rect(screen, RED, (WIDTH - 250, 60, 200, 30))
    pygame.draw.rect(screen, GREEN, (WIDTH - 250, 60, 200 * (battle.character2.health / battle.character2.max_health), 30))

    screen.blit(font.render(f"{battle.character1.name} HP: {battle.character1.health}", True, BLACK), (50, 30))
    screen.blit(font.render(f"{battle.character2.name} HP: {battle.character2.health}", True, BLACK), (WIDTH - 250, 30))
    screen.blit(font.render(battle.action_message, True, BLACK), (WIDTH // 2 - 200, HEIGHT - 600))

    # Animate and draw characters
    battle.character1.animate()
    battle.character2.animate()

    for i, character in enumerate([battle.character1, battle.character2]):
        frame = character.animations[character.current_animation][character.current_frame]
        pos_x = 100 if i == 0 else WIDTH - 300
        screen.blit(pygame.transform.scale(frame, (200, 200)), (pos_x, HEIGHT // 2 - 100))
        if character.status_effect_animation:
            effect_frame = character.animations[character.status_effect_animation][character.status_effect_frame]
            effect_pos = (pos_x + 50, HEIGHT // 2 - 130)
            screen.blit(pygame.transform.scale(effect_frame, (100, 100)), effect_pos)

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
        for i, ab in enumerate(battle.character1.abilities):
            ab_btn = draw_button(ab, 250 + i * 200, HEIGHT - 200, 180, 60)
            cost = ability_effects[ab].__doc__ if ability_effects.get(ab).__doc__ else ""
            cost_txt = small_font.render(cost, True, BLACK)
            screen.blit(cost_txt, (ab_btn.x + ab_btn.width//2 - cost_txt.get_width()//2, ab_btn.y + 65))
            buttons[f"ability_{i}"] = ab_btn

    if battle.show_items:
        for i, item in enumerate(battle.character1.items):
            item_btn = draw_button(item, 250 + i * 200, HEIGHT - 200, 180, 60)
            effect = item_effects[item].__doc__ if item_effects.get(item).__doc__ else ""
            effect_txt = small_font.render(effect, True, BLACK)
            screen.blit(effect_txt, (item_btn.x + item_btn.width//2 - effect_txt.get_width()//2, item_btn.y + 65))
            buttons[f"item_{i}"] = item_btn

    if battle.game_over:
        screen.fill(WHITE)
        victory_text = "Victory!" if battle.character1.health > 0 else "Defeat!"
        text_rect = large_font.render(victory_text, True, GREEN if battle.character1.health > 0 else RED).get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(large_font.render(victory_text, True, GREEN if battle.character1.health > 0 else RED), text_rect)
        report_text = font.render("Combat Report:", True, BLACK)
        screen.blit(report_text, (50, HEIGHT // 2 - 50))

        lines = battle.battle_report.split("\n")
        for i, line in enumerate(lines):
            screen.blit(small_font.render(line, True, BLACK), (50, HEIGHT // 2 + 10 + i * 30))

        buttons["restart"] = draw_button("Restart", WIDTH // 2 - 200, HEIGHT - 150, 180, 60)
        buttons["quit"] = draw_button("Quit", WIDTH // 2 + 20, HEIGHT - 150, 180, 60)

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
            if event.button == 3:  # Right-click for parry
                if battle.parry_window:
                    battle.parry_success = True
                    print("Parry activated!")  # You can play a sound or animation here
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
                        hero = Character(hero_attributes)
                        enemy = Character(goblin_attributes)
                        battle = Battle(hero, enemy)
                    elif key == "quit":
                        running = False
