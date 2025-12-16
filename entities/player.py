import pygame
from settings import TILE_SIZE, WHITE

class Player:
    def __init__(self, tile_pos):
        self.tile_x, self.tile_y = tile_pos

        self.move_delay = 0.15  # seconds per tile
        self.timer = 0.0

        self.rect = pygame.Rect(
            self.tile_x * TILE_SIZE,
            self.tile_y * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
        elif keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1

        return dx, dy

    def update(self, dt, tilemap):
        self.timer += dt
        if self.timer < self.move_delay:
            return

        dx, dy = self.handle_input()
        if dx == 0 and dy == 0:
            return

        nx = self.tile_x + dx
        ny = self.tile_y + dy

        if not tilemap.is_blocked(nx, ny):
            self.tile_x = nx
            self.tile_y = ny

        self.rect.topleft = (
            self.tile_x * TILE_SIZE,
            self.tile_y * TILE_SIZE
        )

        self.timer = 0.0

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)
