hero_attributes = {
    "name": "Hero",
    "health": 100,
    "mana": 50,
    "strength": 15,
    "defense": 5,
    "abilities": ["Fireball", "Heal", "Bash", "Shield"],
    "items": ["Potion", "Elixir"],
    "sfx": "sfx/hero",
    "sprite": "sprites/hero"
}

goblin_attributes = {
    "name": "Goblin",
    "health": 60,
    "mana": 50,
    "strength": 10,
    "defense": 5,
    "abilities": ["Swipe", "Kick"],
    "items": ["Potion"],
    "sfx": "sfx/hero",
    "sprite": "sprites/goblin"
}
def fireball(char1, char2):
    """Deal 25+str magic damage, costs 10 mana"""
    dmg_for = 25 + char1.strength
    if char1.mana >= 10:
        if char2.defend_stance == 1:
            damage = dmg_for // 2
        else:
            damage = dmg_for

        # Apply damage and check for parry
        p = char2.take_damage(damage)
        char1.mana -= 10

        if p == 1:
            char2.play_sound("parry")
            char2.start_animation("parry")
            char2.total_m_dam += damage
            return "Parried"
        else:
            char1.total_damage_dealt += damage
            char1.play_sound("fireball")
            return f"{char1.name} casts Fireball for {damage} damage!"
    return "Not enough mana for Fireball!"

def heal(char1, char2):
    """Heals 30 HP"""
    if char1.mana >= 5:
        heal_amount = 30
        if char1.health + heal_amount > char1.max_health:
            heal_amount = char1.max_health - char1.health
            char1.health = char1.max_health
        else:
            char1.health = char1.health + heal_amount
        char1.mana -= 5
        char1.total_healing_done += heal_amount
        return f"{char1.name} heals for {heal_amount} HP!"
    return "Not enough mana for Heal!"

def bash(char1, char2):
    """Deal 15+str Damages"""
    dmg_for = (15 + char1.strength)
    if char2.defend_stance == 1:
        damage = dmg_for//2
    else:
        damage = dmg_for
    char2.health -= damage
    char1.total_damage_dealt += damage
    return f"{char1.name} bashes {char2.name} for {damage} damage!"

def shield(char1, char2):
    """+10 def"""
    char1.defense += 10
    return f"{char1.name} shields, increasing defense by 10!"

def swipe(char1, char2):
    """Basic attack: 10 + str damage"""
    dmg_for = 10 + char2.strength
    if char2.defend_stance == 1:
        damage = dmg_for//2
    else:
        damage = dmg_for
    char2.health -= damage
    char1.total_damage_dealt += damage
    return f"{char1.name} swipes for {damage} damage!"

def kick(char1, char2):
    """Stronger attack: 15 + str damage"""
    dmg_for = 15 + char2.strength
    if char2.defend_stance == 1:
        damage = dmg_for // 2
    else:
        damage = dmg_for
    char2.health -= damage
    char1.total_damage_dealt += damage
    return f"{char1.name} kicks for {damage} damage!"

def potion(char1, char2):
    """Heals 20 HP"""
    heal_amount = 20
    if char1.health + heal_amount > char1.max_health:
        heal_amount = char1.max_health - char1.health
        char1.health = char1.max_health
    else:
        char1.health = char1.health + heal_amount
    char1.total_healing_done += heal_amount
    return f"{char1.name} uses a potion to restore {heal_amount} HP!"

def elixir(char1, char2):
    """Heals 30 MP"""
    char1.mana = min(char1.max_mana, char1.mana + 30)
    return f"{char1.name} uses an elixir to restore 30 mana!"


ability_effects = {
    "Fireball": fireball,
    "Heal": heal,
    "Bash": bash,
    "Shield": shield,
    "Swipe": swipe,
    "Kick": kick
}

item_effects = {
    "Potion": potion,
    "Elixir": elixir
}

sound_effects = {
    "attack": "hero_attack.wav",
    "defend": "hero_defend.wav",
    "Fireball": "fireball.wav",
    "Heal": "heal.wav",
    "Bash": "bash.wav",
    "Shield": "shield.wav",
    "Potion": "potion.wav",
    "Elixir": "elixir.wav"
}
