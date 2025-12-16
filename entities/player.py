import pygame
from settings import TILE_SIZE, WHITE

class Player:
    def __init__(self, tile_pos):
        self.tile_x, self.tile_y = tile_pos
        self.target_x, self.target_y = tile_pos  # Where we are moving to

        self.move_delay = 0.15  # seconds per tile
        self.timer = 0.0

        # Current position for smooth movement
        self.pos_x = self.tile_x * TILE_SIZE
        self.pos_y = self.tile_y * TILE_SIZE

        self.rect = pygame.Rect(self.pos_x, self.pos_y, TILE_SIZE, TILE_SIZE)
        self.lerp_speed = 12.0  # Higher = faster interpolation

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
        if self.timer >= self.move_delay:
            dx, dy = self.handle_input()
            if dx != 0 or dy != 0:
                nx = self.tile_x + dx
                ny = self.tile_y + dy
                if not tilemap.is_blocked(nx, ny):
                    self.tile_x = nx
                    self.tile_y = ny
                    self.target_x = nx * TILE_SIZE
                    self.target_y = ny * TILE_SIZE
            self.timer = 0.0

        # Smoothly interpolate position toward target
        self.pos_x += (self.target_x - self.pos_x) * min(self.lerp_speed * dt, 1)
        self.pos_y += (self.target_y - self.pos_y) * min(self.lerp_speed * dt, 1)

        self.rect.topleft = (self.pos_x, self.pos_y)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)
