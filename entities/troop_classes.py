import pygame
from entities.troop import Troop
from settings import TROOP_DATA

class Jester(Troop):
    def __init__(self, tile_pos):
        stats = TROOP_DATA["jester"]
        super().__init__(
            tile_pos, 
            range_radius=stats["range"], 
            fire_delay=stats["delay"], 
            damage=stats["damage"],
            color=stats["color"]
        )

    def attack_target(self, target, projectiles):
        # Melee: Direct Hit
        target.health -= self.damage

class Knight(Troop):
    def __init__(self, tile_pos):
        stats = TROOP_DATA["knight"]
        super().__init__(
            tile_pos, 
            range_radius=stats["range"], 
            fire_delay=stats["delay"], 
            damage=stats["damage"],
            color=stats["color"]
        )

    def attack_target(self, target, projectiles):
        # Melee: Strong Direct Hit
        target.health -= self.damage

class Archer(Troop):
    def __init__(self, tile_pos):
        stats = TROOP_DATA["archer"]
        super().__init__(
            tile_pos, 
            range_radius=stats["range"], 
            fire_delay=stats["delay"], 
            damage=stats["damage"],
            color=stats["color"]
        )
    # Uses default ranged projectile attack

class Wizard(Troop):
    def __init__(self, tile_pos):
        stats = TROOP_DATA["wizard"]
        super().__init__(
            tile_pos, 
            range_radius=stats["range"], 
            fire_delay=stats["delay"], 
            damage=stats["damage"],
            color=stats["color"]
        )
    # Uses default ranged projectile attack (Visuals can be upgraded later)

class Cannon(Troop):
    def __init__(self, tile_pos):
        stats = TROOP_DATA["cannon"]
        super().__init__(
            tile_pos, 
            range_radius=stats["range"], 
            fire_delay=stats["delay"], 
            damage=stats["damage"],
            color=stats["color"]
        )
    # Uses default ranged projectile attack