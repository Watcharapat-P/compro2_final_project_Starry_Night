import pygame
import random
import os
import attribute as atr
import csv
import sys

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
        self.moveset = []

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
            if self.is_animating:
                self.animation_timer += 1
                if self.animation_timer >= 5:
                    self.current_frame += 1
                    self.animation_timer = 0

                    if (self.name == "Goblin" or self.name == "Skeleton") and self.current_animation == "attack":
                        if self.current_frame == 2:
                            battle.parry_window = True
                            battle.parry_timer = pygame.time.get_ticks()
                        elif self.current_frame == 4:
                            battle.parry_window = False


                if self.current_frame >= len(self.animations[self.current_animation]):
                    self.current_frame = 0
                    self.is_animating = False
                    self.current_animation = "idle"

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
            target.moveset.append("parry")
            return "Parried"
        else:
            self.total_damage_dealt += damage
            self.play_sound("attack")
            self.start_animation("attack")
            self.moveset.append("attack")
            return f"{self.name} attacks for {damage} damage!"

    def defend(self):
        self.defend_stance = 1
        self.play_sound("defend")
        self.moveset.append("defend")
        return f"{self.name} defends!"

    def use_ability(self, ability, target):
        if ability in atr.ability_effects:
            result = atr.ability_effects[ability](self, target)
            self.play_sound(ability)
            self.moveset.append(ability)
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
        if item in atr.item_effects:
            result = atr.item_effects[item](self, target)
            self.play_sound(item)
            self.moveset.append("item")
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
            self.save_combat_report_to_csv()
        elif self.character2.health <= 0:
            self.action_message = "You win!"
            self.game_over = True
            self.battle_report = self.generate_combat_report()
            self.save_combat_report_to_csv()

    def generate_combat_report(self):
        report = f"{self.character1.name} dealt {self.character1.total_damage_dealt} damage.\n"
        report += f"{self.character1.name} healed {self.character1.total_healing_done} HP.\n"
        report += f"{self.character1.name} mitigated {self.character1.total_m_dam} damage.\n"
        report += f"{self.character2.name} dealt {self.character2.total_damage_dealt} damage.\n"
        report += f"{self.character2.name} healed {self.character2.total_healing_done} HP.\n"
        return report

    def save_combat_report_to_csv(self, filename="combat_log.csv"):
        file_exists = os.path.isfile(filename)
        with open(filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Name", "Damage Dealt", "Healing Done", "Damage Mitigated", "Movesets"])
            writer.writerow([
                self.character1.name,
                self.character1.total_damage_dealt,
                self.character1.total_healing_done,
                self.character1.total_m_dam,
                self.character1.moveset
            ])
            writer.writerow([
                self.character2.name,
                self.character2.total_damage_dealt,
                self.character2.total_healing_done,
                self.character2.total_m_dam,
                self.character2.moveset
            ])
            writer.writerow([])

class GameInstance:
    def __init__(self, hero_atr, enemy_atr):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1280, 720
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Starry Night - Turn-Based Combat")

        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 72)

        self.colors = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255)
        }
        global battle
        self.hero = Character(hero_atr)
        self.enemy = Character(enemy_atr)
        self.battle = Battle(self.hero, self.enemy)
        battle = self.battle
        self.clock = pygame.time.Clock()
        self.buttons = {}

    def draw_button(self, text, x, y, w, h, color=None):
        color = color or self.colors["blue"]
        rect = pygame.draw.rect(self.screen, color, (x, y, w, h))
        label = self.font.render(text, True, self.colors["white"])
        self.screen.blit(label, (x + w // 2 - label.get_width() // 2, y + h // 2 - label.get_height() // 2))
        return rect

    def draw_battle_screen(self):
        self.screen.fill(self.colors["white"])
        battle = self.battle

        pygame.draw.rect(self.screen, self.colors["red"], (50, 60, 200, 30))
        pygame.draw.rect(self.screen, self.colors["green"], (50, 60, 200 * (battle.character1.health / battle.character1.max_health), 30))
        pygame.draw.rect(self.screen, self.colors["red"], (50, 95, 200, 20))
        pygame.draw.rect(self.screen, self.colors["blue"], (50, 95, 200 * (battle.character1.mana / battle.character1.max_mana), 20))
        pygame.draw.rect(self.screen, self.colors["red"], (self.WIDTH - 250, 60, 200, 30))
        pygame.draw.rect(self.screen, self.colors["green"], (self.WIDTH - 250, 60, 200 * (battle.character2.health / battle.character2.max_health), 30))

        self.screen.blit(self.font.render(f"{battle.character1.name} HP: {battle.character1.health}", True, self.colors["black"]), (50, 30))
        self.screen.blit(self.font.render(f"{battle.character2.name} HP: {battle.character2.health}", True, self.colors["black"]), (self.WIDTH - 250, 30))
        self.screen.blit(self.font.render(battle.action_message, True, self.colors["black"]), (self.WIDTH // 2 - 200, self.HEIGHT - 600))

        battle.character1.animate()
        battle.character2.animate()
        for i, character in enumerate([battle.character1, battle.character2]):
            frame = character.animations[character.current_animation][character.current_frame]
            pos_x = 100 if i == 0 else self.WIDTH - 300
            self.screen.blit(pygame.transform.scale(frame, (200, 200)), (pos_x, self.HEIGHT // 2 - 100))
            if character.status_effect_animation:
                effect_frame = character.animations[character.status_effect_animation][character.status_effect_frame]
                effect_pos = (pos_x + 50, self.HEIGHT // 2 - 130)
                self.screen.blit(pygame.transform.scale(effect_frame, (100, 100)), effect_pos)

        self.buttons.clear()
        if not battle.game_over and battle.is_character1_turn:
            bw, bh = 180, 60
            start_x = (self.WIDTH - (4 * bw + 3 * 20)) / 2
            y_pos = self.HEIGHT - 100
            self.buttons["attack"] = self.draw_button("Attack", start_x, y_pos, bw, bh)
            self.buttons["defend"] = self.draw_button("Defend", start_x + bw + 20, y_pos, bw, bh)
            self.buttons["ability"] = self.draw_button("Ability", start_x + 2 * (bw + 20), y_pos, bw, bh)
            self.buttons["item"] = self.draw_button("Item", start_x + 3 * (bw + 20), y_pos, bw, bh)

        if battle.show_abilities:
            for i, ab in enumerate(battle.character1.abilities):
                ab_btn = self.draw_button(ab, 250 + i * 200, self.HEIGHT - 200, 180, 60)
                cost = atr.ability_effects[ab].__doc__ or ""
                cost_txt = self.small_font.render(cost, True, self.colors["black"])
                self.screen.blit(cost_txt, (ab_btn.x + ab_btn.width // 2 - cost_txt.get_width() // 2, ab_btn.y + 65))
                self.buttons[f"ability_{i}"] = ab_btn

        if battle.show_items:
            for i, item in enumerate(battle.character1.items):
                item_btn = self.draw_button(item, 250 + i * 200, self.HEIGHT - 200, 180, 60)
                effect = atr.item_effects[item].__doc__ or ""
                effect_txt = self.small_font.render(effect, True, self.colors["black"])
                self.screen.blit(effect_txt, (item_btn.x + item_btn.width // 2 - effect_txt.get_width() // 2, item_btn.y + 65))
                self.buttons[f"item_{i}"] = item_btn

        if battle.game_over:
            screen.fill(WHITE)
            victory_text = "Victory!" if battle.character1.health > 0 else "Defeat!"
            text_rect = large_font.render(victory_text, True, GREEN if battle.character1.health > 0 else RED).get_rect(
                center=(WIDTH // 2, HEIGHT // 4))
            screen.blit(large_font.render(victory_text, True, GREEN if battle.character1.health > 0 else RED),
                        text_rect)
            report_text = font.render("Combat Report:", True, BLACK)
            screen.blit(report_text, (50, HEIGHT // 2 - 50))

            lines = battle.battle_report.split("\n")
            for i, line in enumerate(lines):
                screen.blit(small_font.render(line, True, BLACK), (50, HEIGHT // 2 + 10 + i * 30))

            self.buttons["stage"] = self.draw_button("Back", WIDTH // 2 - 200, HEIGHT - 150, 180, 60)
            self.buttons["quit"] = self.draw_button("Quit", WIDTH // 2 + 20, HEIGHT - 150, 180, 60)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if event.button == 3:
                if self.battle.parry_window:
                    self.battle.parry_success = True
                    print("Parry activated!")
            for key, btn in self.buttons.items():
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
                    elif key == "quit":
                        self.running = False
                    elif key == "stage":
                        self.running = False
                        pygame.quit()


    def run(self):
        self.running = True
        while self.running:
            self.clock.tick(60)
            self.battle.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.handle_input(event)
            self.draw_battle_screen()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    level = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    if level == 1:
        enemy_attributes = atr.goblin_attributes
    elif level == 2:
        enemy_attributes = atr.skeleton_attributes
    else:
        print(f"Warning: Level {level} not defined, defaulting to Goblin.")
        enemy_attributes = atr.goblin_attributes

    game = GameInstance(atr.hero_attributes, enemy_attributes)
    game.run()
    print(level)

