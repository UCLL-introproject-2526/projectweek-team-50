from entities.troop import Troop

class Goblin(Troop):
    def __init__(self, tile_pos):
        # Melee (weakest)
        super().__init__(tile_pos, range_radius=55, fire_delay=0.50, damage=18)
        self.name = "Goblin"
        self.sprite_type = "goblin"


class Elf(Troop):
    def __init__(self, tile_pos):
        # Melee
        super().__init__(tile_pos, range_radius=65, fire_delay=0.55, damage=26)
        self.name = "Elf"
        self.sprite_type = "elf"


class Knight(Troop):
    def __init__(self, tile_pos):
        # Melee (stronger)
        super().__init__(tile_pos, range_radius=80, fire_delay=0.85, damage=40)
        self.name = "Knight"
        self.sprite_type = "knight"


class Archer(Troop):
    def __init__(self, tile_pos):
        # Medium ranged
        super().__init__(tile_pos, range_radius=180, fire_delay=0.65, damage=32)
        self.name = "Archer"
        self.sprite_type = "archer"


class Wizard(Troop):
    def __init__(self, tile_pos):
        # High range with slow
        super().__init__(tile_pos, range_radius=260, fire_delay=0.80, damage=42, slow_duration=0.5)
        self.name = "Wizard"
        self.sprite_type = "wizard"


class FireWarrior(Troop):
    def __init__(self, tile_pos):
        # Melee but bigger range
        super().__init__(tile_pos, range_radius=110, fire_delay=0.75, damage=60)
        self.name = "Fire Warrior"
        self.sprite_type = "firewarrior"


class BloodMage(Troop):
    def __init__(self, tile_pos):
        # Strongest: very high range
        super().__init__(tile_pos, range_radius=340, fire_delay=0.90, damage=85)
        self.name = "Blood Mage"
        self.sprite_type = "bloodmage"