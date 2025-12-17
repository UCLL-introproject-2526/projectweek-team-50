import pygame
from settings import TILE_SIZE

class Entity:
    def __init__(self, tile_pos):
        self.tile_x, self.tile_y = tile_pos

        self.target_x = self.tile_x * TILE_SIZE
        self.target_y = self.tile_y * TILE_SIZE

        self.pos_x = self.target_x
        self.pos_y = self.target_y

        self.rect = pygame.Rect(
            self.pos_x,
            self.pos_y,
            TILE_SIZE,
            TILE_SIZE
        )

        self.lerp_speed = 12.0

    def set_tile(self, tx, ty):
        self.tile_x = tx
        self.tile_y = ty
        self.target_x = tx * TILE_SIZE
        self.target_y = ty * TILE_SIZE

    def lerp(self, dt):
        self.pos_x += (self.target_x - self.pos_x) * min(self.lerp_speed * dt, 1)
        self.pos_y += (self.target_y - self.pos_y) * min(self.lerp_speed * dt, 1)
        self.rect.topleft = (self.pos_x, self.pos_y)

    def update(self, dt):
        self.lerp(dt)

    def draw(self, surface):
        raise NotImplementedError
