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


class Enemy(Character):
    def __init__(self, path):
        super().__init__(
            position=path[0],
            health=50,
            radius=12
        )

        self.path = path
        self.path_index = 0
        self.speed = 2

    def move(self):
        if not self.alive:
            return

        if self.path_index >= len(self.path) - 1:
            return

        target = Vector2(self.path[self.path_index + 1])
        direction = target - self.position

        if direction.length() <= self.speed:
            self.position = target
            self.path_index += 1
        else:
            self.position += direction.normalize() * self.speed

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            (200, 60, 60),
            self.position,
            self.radius
        )
        self.draw_health_bar(screen)
