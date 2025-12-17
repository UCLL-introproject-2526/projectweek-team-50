import pygame
import math
from settings import TILE_SIZE, RED, GREEN, BLACK

class Enemy:
    def __init__(self, path_points, health, speed, reward, color_grade=0):
        self.path = path_points
        self.path_index = 0

        # World position (float for smooth movement)
        self.x, self.y = self.path[0]

        self.health = health
        self.max_health = health
        self.speed = speed
        self.reward = reward

        self.finished = False

        self.color = (
            max(50, RED[0] - color_grade * 30),
            RED[1],
            RED[2]
        )

        self.radius = TILE_SIZE // 3

        # ✅ RECT (this fixes your crash)
        size = self.radius * 2
        self.rect = pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            size,
            size
        )

    def update(self, dt):
        if self.finished or self.path_index >= len(self.path) - 1:
            self.finished = True
            return

        target_x, target_y = self.path[self.path_index + 1]

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        if dist < 2:
            self.path_index += 1
        else:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

        # ✅ Update rect position every frame
        self.rect.center = (int(self.x), int(self.y))

        if self.health <= 0:
            self.finished = True

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.x), int(self.y)),
            self.radius
        )

        # Health bar
        bar_width = 30
        bar_height = 5
        x = self.x - bar_width // 2
        y = self.y - self.radius - 10

        pygame.draw.rect(surface, BLACK, (x, y, bar_width, bar_height))

        if self.max_health > 0:
            health_ratio = self.health / self.max_health
            pygame.draw.rect(
                surface,
                GREEN,
                (x, y, bar_width * health_ratio, bar_height)
            )
