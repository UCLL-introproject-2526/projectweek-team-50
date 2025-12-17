import pygame
import math
from settings import YELLOW
from coins import handle_death

# Projectile optionally receives coin_manager and tilemap so it can trigger coin drops

class Projectile:
    def __init__(self, x, y, target, speed=400, damage=20, coin_manager=None, tilemap=None):
        self.x = x
        self.y = y
        self.target = target
        self.speed = speed
        self.damage = damage
        self.alive = True
        self.coin_manager = coin_manager
        self.tilemap = tilemap

    def update(self, dt):
        if not self.target or self.target.finished:
            self.alive = False
            return

        dx = self.target.rect.centerx - self.x
        dy = self.target.rect.centery - self.y
        dist = math.hypot(dx, dy)

        if dist < 5:
            self.target.health -= self.damage
            # If the hit killed the enemy, immediately spawn coins
            if self.target.health <= 0 and self.coin_manager and self.tilemap:
                try:
                    handle_death(self.target, self.coin_manager, self.tilemap)
                except Exception:
                    pass
            self.alive = False
            return

        self.x += (dx / dist) * self.speed * dt
        self.y += (dy / dist) * self.speed * dt

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), 4)
