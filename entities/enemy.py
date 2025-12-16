import pygame
import math
from settings import RED, GREEN, BLACK

class Enemy:
    def __init__(self, path_points, health, speed, reward, color_grade=0):
        self.path = path_points
        self.x, self.y = self.path[0]

        self.health = health
        self.max_health = health
        self.speed = speed
        self.reward = reward

        self.path_index = 0
        self.finished = False

        self.color = (
            max(50, RED[0] - color_grade * 30),
            RED[1],
            RED[2]
        )
        self.radius = 12

    def update(self, dt):
        if self.finished or self.path_index >= len(self.path) - 1:
            self.finished = True
            return

        target_x, target_y = self.path[self.path_index + 1]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        if dist < 1:
            self.path_index += 1
        else:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.x), int(self.y)),
            self.radius
        )

        # Health bar
        pygame.draw.rect(surface, BLACK, (self.x - 15, self.y - 20, 30, 5))
        if self.max_health > 0:
            health_perc = self.health / self.max_health
            pygame.draw.rect(
                surface,
                GREEN,
                (self.x - 15, self.y - 20, 30 * health_perc, 5)
            )
