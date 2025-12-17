import random

import pygame

from settings import TILE_SIZE

# Player money starts at 0
player_money = 0

def handle_death(enemy, coin_manager, tilemap):
    if enemy.dead_handled: 
        return
    
    tx = enemy.tile_x
    ty = enemy.tile_y

    # spawn 2-3 coins, each 5-10 TL, spread randomly within 2-tile radius
    for _ in range(random.randint(2,3)):
        value = random.randint(5, 10)  # Turkish lira
        
        # Random offset within 2-tile radius
        offset_x = random.randint(-2, 2)
        offset_y = random.randint(-2, 2)
        
        coin_tx = tx + offset_x
        coin_ty = ty + offset_y
        
        coin_manager.add_coin_at_tile(coin_tx, coin_ty, value)

    enemy.dead_handled = True

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