import pygame
from pygame.math import Vector2
from character import Character

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