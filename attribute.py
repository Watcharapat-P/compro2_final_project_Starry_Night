

hero_attributes = {
    "name": "Hero",
    "health": 100,
    "mana": 50,
    "strength": 15,
    "defense": 5,
    "abilities": ["Fireball", "Heal", "Bash", "Shield"],
    "items": ["Potion", "Elixir"]
}

enemy_attributes = {
    "name": "Goblin",
    "health": 60,
    "strength": 10,
    "abilities": ["Swipe", "Kick"]
}
def fireball(hero, enemy):
    """Deal 40 Damages"""
    if hero.mana >= 10:
        damage = 25 + hero.strength
        enemy.health -= damage
        hero.mana -= 10
        hero.total_damage_dealt += damage
        return f"{hero.name} casts Fireball for {damage} damage!"
    return "Not enough mana for Fireball!"

def heal(hero, enemy):
    """Heals 30 HP"""
    if hero.mana >= 5:
        heal_amount = 30
        if hero.health + heal_amount > hero.max_health:
            heal_amount = hero.max_health - hero.health
            hero.health = hero.max_health
        else:
            hero.health = hero.health + heal_amount
        hero.mana -= 5
        hero.total_healing_done += heal_amount
        return f"{hero.name} heals for {heal_amount} HP!"
    return "Not enough mana for Heal!"

def bash(hero, enemy):
    """Deal 15+str Damages"""
    damage = 15 + hero.strength
    enemy.health -= damage
    hero.total_damage_dealt += damage
    return f"{hero.name} bashes {enemy.name} for {damage} damage!"

def shield(hero, enemy):
    """+10 def"""
    hero.defense += 10
    return f"{hero.name} shields, increasing defense by 10!"


def potion(hero, enemy):
    """Heals 20 HP"""
    heal_amount = 20
    if hero.health + heal_amount > hero.max_health:
        heal_amount = hero.max_health - hero.health
        hero.health = hero.max_health
    else:
        hero.health = hero.health + heal_amount
    hero.total_healing_done += heal_amount
    return f"{hero.name} uses a potion to restore {heal_amount} HP!"

def elixir(hero, enemy):
    """Heals 30 MP"""
    hero.mana = min(hero.max_mana, hero.mana + 30)
    return f"{hero.name} uses an elixir to restore 30 mana!"


ability_effects = {
    "Fireball": fireball,
    "Heal": heal,
    "Bash": bash,
    "Shield": shield
}

item_effects = {
    "Potion": potion,
    "Elixir": elixir
}
