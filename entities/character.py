import pygame
from pygame.math import Vector2


class Character:
    def __init__(self, position, health, radius):
        self.position = Vector2(position)
        self.max_health = health
        self.health = health
        self.radius = radius
        self.alive = True

    def take_damage(self, amount):
        if not self.alive:
            return

        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.alive = False

    def draw_health_bar(self, screen):
        bar_width = 40
        bar_height = 6
        ratio = self.health / self.max_health

        x = self.position.x - bar_width // 2
        y = self.position.y - self.radius - 12

        # Background (red)
        pygame.draw.rect(
            screen,
            (120, 0, 0),
            (x, y, bar_width, bar_height)
        )

        # Health (green)
        pygame.draw.rect(
            screen,
            (0, 200, 0),
            (x, y, bar_width * ratio, bar_height)
        )

    def draw(self, screen):
        # Intended to be overridden by subclasses
        pass
