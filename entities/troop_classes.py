from entities.troop import Troop

class Jester(Troop):
    def __init__(self, tile_pos):
        # Melee unit: Short range, fast attack?
        super().__init__(tile_pos, range_radius=60, fire_delay=0.5)
        self.name = "Jester"

class Knight(Troop):
    def __init__(self, tile_pos):
        # Melee unit: Short range, tanky?
        super().__init__(tile_pos, range_radius=50, fire_delay=1.5)
        self.name = "Knight"

class Archer(Troop):
    def __init__(self, tile_pos):
        # Standard ranged unit
        super().__init__(tile_pos, range_radius=200, fire_delay=0.8)
        self.name = "Archer"

class Wizard(Troop):
    def __init__(self, tile_pos):
        # Long range or AOE with slow effect?
        super().__init__(tile_pos, range_radius=180, fire_delay=1.5, slow_duration=0.5)
        self.name = "Wizard"

class Cannon(Troop):
    def __init__(self, tile_pos):
        # Very long range, slow fire
        super().__init__(tile_pos, range_radius=300, fire_delay=2.5)
        self.name = "Cannon"