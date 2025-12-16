import pygame
from settings import *

class TileMap:
    def __init__(self, tile_data=None):
        if tile_data:
            self.tiles = tile_data
        else:
            self.tiles = [
                [TILE_GRASS for _ in range(TILES_X)]
                for _ in range(TILES_Y)
            ]

    def is_blocked(self, tx, ty):
        if tx < 0 or ty < 0 or tx >= TILES_X or ty >= TILES_Y:
            return True
        return self.tiles[ty][tx] == TILE_WALL

    def is_path(self, tx, ty):
        return self.tiles[ty][tx] == TILE_PATH

    def draw(self, surface):
        for y in range(TILES_Y):
            for x in range(TILES_X):
                tile_id = self.tiles[y][x]
                color = TILE_COLORS[tile_id]

                pygame.draw.rect(
                    surface,
                    color,
                    (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                )

        # Grid overlay
        for x in range(TILES_X + 1):
            pygame.draw.line(
                surface, (60, 60, 60),
                (x * TILE_SIZE, 0),
                (x * TILE_SIZE, SCREEN_HEIGHT), 1
            )

        for y in range(TILES_Y + 1):
            pygame.draw.line(
                surface, (60, 60, 60),
                (0, y * TILE_SIZE),
                (SCREEN_WIDTH, y * TILE_SIZE), 1
            )
