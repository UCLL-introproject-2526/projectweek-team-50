import random
from typing import Self
from entities.entity import Entity
import pygame

from settings import TILE_SIZE
def handle_death(self, coin_manager, tilemap):
    if self.dead_handled: return
    tx = int(self.x) // TILE_SIZE
    ty = int(self.y) // TILE_SIZE

    # if not grass, search neighbors
    if not tilemap.is_tile_grass(tx, ty):
        found = False
        for r in (1,2):
            for dx in range(-r, r+1):
                for dy in range(-r, r+1):
                    nx, ny = tx+dx, ty+dy
                    if tilemap.is_tile_grass(nx, ny):
                        tx, ty = nx, ny
                        found = True
                        break
                if found: break
            if found: break
        if not found:
            self.dead_handled = True
            return

    # spawn 2-3 coins, each 5-10 TL
    for _ in range(random.randint(2,3)):
        value = random.randint(5, 10)  # Turkish lira
        coin_manager.add_coin_at_tile(tx, ty, value)

    self.dead_handled = True

# CoinManager (simple tile-based)
class CoinManager:
    def __init__(self):
        self.coins = {}  # {(tx, ty): value}
    def add_coin_at_tile(self, tx, ty, value):
        if (tx, ty) not in self.coins:
         self.coins[(tx, ty)] = value
    def collect_at_tile(self, tx, ty):
        return self.coins.pop((tx, ty), 0)
    def draw(self, surface):
        GOLD = (255, 215, 0)
        size = TILE_SIZE // 3

        for (tx, ty), value in self.coins.items():
            x = tx * TILE_SIZE + (TILE_SIZE - size) // 2
            y = ty * TILE_SIZE + (TILE_SIZE - size) // 2
            pygame.draw.rect(
             surface,
             GOLD,
             (x, y, size, size)
         )

class Player(Entity):
    def __init__(self, tile_pos):
        super().__init__(tile_pos)
        self.player_money = 0  # Turkish lira


# in Player.update() after moving / set_tile(...)
collected = CoinManager.collect_at_tile(Self.tile_x, Self.tile_y)
if collected:
    player_money += collected  # add TL