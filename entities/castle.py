import pygame
from settings import TILE_SIZE, RED, GREEN, BLACK

class Castle:
    def __init__(self, tile_pos):
        self.tile_x, self.tile_y = tile_pos
        self.hp = 10 # Lose when 10 enemies reach
        self.max_hp = 10

        # Rect for the 3x3 area
        self.rect = pygame.Rect(
            self.tile_x * TILE_SIZE,
            self.tile_y * TILE_SIZE,
            TILE_SIZE * 3,
            TILE_SIZE * 3
        )

    def take_damage(self, damage=5):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            # Game over logic can be handled in game.py

    def draw(self, surface):
        # Draw the castle as a blue square or something
        pygame.draw.rect(surface, (100, 100, 150), self.rect)

        # HP bar
        bar_width = 60
        bar_height = 8
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 15

        pygame.draw.rect(surface, BLACK, (x, y, bar_width, bar_height))

        if self.max_hp > 0:
            health_ratio = self.hp / self.max_hp
            pygame.draw.rect(
                surface,
                GREEN if health_ratio > 0.5 else RED,
                (x, y, bar_width * health_ratio, bar_height)
            )