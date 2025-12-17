import pygame
import math
from settings import YELLOW

class Projectile:
    def __init__(self, x, y, target, speed=400, damage=20):
        self.x = x
        self.y = y
        self.target = target
        self.speed = speed
        self.damage = damage
        self.alive = True

    def update(self, dt):
        if not self.target or self.target.finished:
            self.alive = False
            return

        dx = self.target.rect.centerx - self.x
        dy = self.target.rect.centery - self.y
        dist = math.hypot(dx, dy)

        if dist < 5:
            self.target.health -= self.damage
            self.alive = False
            return

        self.x += (dx / dist) * self.speed * dt
        self.y += (dy / dist) * self.speed * dt

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), 4)
