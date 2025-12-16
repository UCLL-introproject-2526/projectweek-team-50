import pygame
from settings import *

class TileMap:
    def __init__(self, map_data, tile_size):
        self.map_data = map_data  # 2D list of integers
        self.tile_size = tile_size
        self.width = len(map_data[0])
        self.height = len(map_data)

    def draw(self, surface):
        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                if tile == 0:
                    continue  # empty tile
                elif tile == 1:  # wall
                    color = (100, 100, 100)
                elif tile == 2:  # special tile
                    color = (200, 100, 50)

                rect = pygame.Rect(
                    x * self.tile_size, y * self.tile_size,
                    self.tile_size, self.tile_size
                )
                pygame.draw.rect(surface, color, rect)

    def is_solid(self, x, y):
        """Return True if the tile at grid position x,y is solid."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.map_data[y][x] == 1
        return False
