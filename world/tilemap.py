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
        tile = self.tiles[ty][tx]
        return tile in (TILE_PATH, TILE_START, TILE_FINISH, TILE_CASTLE)
    

    def is_buildable(self, x, y):
        # Use TILES_X and TILES_Y instead of self.width / self.height
        if x < 0 or y < 0 or x >= TILES_X or y >= TILES_Y:
            return False
        # Use self.tiles instead of self.grid
        return self.tiles[y][x] == TILE_GRASS  # grass is buildable


    def get_start_tile(self):
        for y in range(TILES_Y):
            for x in range(TILES_X):
                if self.tiles[y][x] == TILE_START:
                    return (x, y)
        return None

    def get_finish_tile(self):
        for y in range(TILES_Y):
            for x in range(TILES_X):
                if self.tiles[y][x] == TILE_FINISH:
                    return (x, y)
        # Fallback to castle if finish not explicitly set
        for y in range(TILES_Y):
            for x in range(TILES_X):
                if self.tiles[y][x] == TILE_CASTLE:
                    return (x, y)
        return None

    def get_finish_center(self):
        finish = self.get_finish_tile()
        if finish:
            fx, fy = finish
            return (fx * TILE_SIZE + TILE_SIZE // 2, fy * TILE_SIZE + TILE_SIZE // 2)
        return None

    def get_path_points(self):
        # Collect path-like tiles (PATH + FINISH; allow CASTLE as fallback)
        path_tiles = set()
        for y in range(TILES_Y):
            for x in range(TILES_X):
                tid = self.tiles[y][x]
                if tid in (TILE_PATH, TILE_FINISH, TILE_CASTLE):
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

        # Prefer explicit start tile; else infer start by degree==1
        start = self.get_start_tile()
        if start is None:
            for tile in path_tiles:
                if len(neighbors(*tile)) == 1:
                    start = tile
                    break
        if start is None:
            raise ValueError("Path has no valid start tile")

        # Walk the path until finish (if present)
        ordered_tiles = [start]
        visited = {start}
        finish = self.get_finish_tile()
        current = start
        while True:
            if finish is not None and current == finish:
                break
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

        # Grid overlay - only draw if SHOW_GRID is enabled
        import settings
        if settings.SHOW_GRID:
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
