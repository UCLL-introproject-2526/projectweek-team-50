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

        # Consider the projectile hitting the target if it's within a small
        # distance or the projectile point lies within the target rect.
        hit = False
        if dist < max(5, getattr(self.target, 'radius', 8)):
            hit = True
        else:
            try:
                if self.target.rect.collidepoint(int(self.x), int(self.y)):
                    hit = True
            except Exception:
                pass

        if hit:
            self.target.health -= self.damage
            # If the hit killed the enemy, mark finished and spawn coins
            if self.target.health <= 0:
                self.target.finished = True
                if self.coin_manager and self.tilemap:
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
