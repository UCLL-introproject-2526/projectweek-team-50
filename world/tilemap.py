import pygame
from settings import TILE_SIZE, TILES_X, TILES_Y, SCREEN_WIDTH, SCREEN_HEIGHT

class TileMap:
    def __init__(self):
        pass  # later: load map data here

    def draw(self, surface):
        # Vertical grid lines
        for x in range(TILES_X + 1):
            pygame.draw.line(
                surface,
                (60, 60, 60),
                (x * TILE_SIZE, 0),
                (x * TILE_SIZE, SCREEN_HEIGHT),
                1
            )

        # Horizontal grid lines
        for y in range(TILES_Y + 1):
            pygame.draw.line(
                surface,
                (60, 60, 60),
                (0, y * TILE_SIZE),
                (SCREEN_WIDTH, y * TILE_SIZE),
                1
            )
