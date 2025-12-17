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
    

    def is_buildable(self, x, y):
        if x < 0 or y < 0 or y >= self.height or x >= self.width:
            return False
        return self.grid[y][x] == 0  # grass

    def get_path_points(self):
        # Find all PATH tiles
        path_tiles = set()
        for y in range(TILES_Y):
            for x in range(TILES_X):
                if self.tiles[y][x] == TILE_PATH:
                    path_tiles.add((x, y))

        if not path_tiles:
            return []

        # Helper to get PATH neighbors
        def neighbors(tx, ty):
            dirs = [(1,0), (-1,0), (0,1), (0,-1)]
            result = []
            for dx, dy in dirs:
                n = (tx + dx, ty + dy)
                if n in path_tiles:
                    result.append(n)
            return result

        # Find start tile (only one PATH neighbor)
        start = None
        for tile in path_tiles:
            if len(neighbors(*tile)) == 1:
                start = tile
                break

        if start is None:
            raise ValueError("Path has no valid start tile")

        # Walk the path
        ordered_tiles = [start]
        visited = {start}

        current = start
        while True:
            next_tiles = [
                n for n in neighbors(*current)
                if n not in visited
            ]

            if not next_tiles:
                break

            current = next_tiles[0]
            ordered_tiles.append(current)
            visited.add(current)

        # Convert tiles → pixel centers
        path_points = []
        for tx, ty in ordered_tiles:
            px = tx * TILE_SIZE + TILE_SIZE // 2
            py = ty * TILE_SIZE + TILE_SIZE // 2
            path_points.append((px, py))

        return path_points


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
