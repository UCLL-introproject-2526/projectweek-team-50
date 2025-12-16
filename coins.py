import pygame
from pygame.math import Vector2

class Coin:
    def __init__(self, position, value=10, radius=8, color=(255, 215, 0)):
        self.position = Vector2(position)
        self.value = value
        self.radius = radius
        self.color = color
        self.collected = False

    def draw(self, screen):
        if not self.collected:
            pygame.draw.circle(
                screen,
                self.color,
                (int(self.position.x), int(self.position.y)),
                self.radius
            )

    def check_collision(self, collector_pos, collector_radius):
        if self.collected:
            return 0

        if (self.position - collector_pos).length() <= self.radius + collector_radius:
            self.collected = True
            return self.value
        return 0


class CoinManager:
    def __init__(self):
        self.coins = []

    def drop_coin(self, position, value=10):
        self.coins.append(Coin(position, value))

    def update(self, collector_pos, collector_radius):
        total = 0
        for coin in self.coins:
            total += coin.check_collision(collector_pos, collector_radius)

        self.coins = [c for c in self.coins if not c.collected]
        return total

    def draw(self, screen):
        for coin in self.coins:
            coin.draw(screen)


class Enemy(Character):
    def __init__(self, path):
        super().__init__(position=path[0], health=50, radius=12)
        self.path = path
        self.path_index = 0
        self.speed = 2

        self.coin_reward = 10
        self.dead_handled = False   # IMPORTANT

# random coin spread from 2 - 5

import random

for _ in range(3):
    offset = Vector2(random.randint(2, 5), random.randint(2, 5))
    coin_manager.drop_coin(enemy.position + offset, 5)

