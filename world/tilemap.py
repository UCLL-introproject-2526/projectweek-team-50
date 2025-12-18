import os
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

        self._tile_surfaces = self._load_tile_surfaces()
        self._decor = self._generate_decorations()

    def _load_pngs_from_dir(self, folder_path):
        surfaces = []
        try:
            for name in os.listdir(folder_path):
                if not name.lower().endswith(".png"):
                    continue
                path = os.path.join(folder_path, name)
                try:
                    img = pygame.image.load(path).convert_alpha()
                    surfaces.append(img)
                except Exception:
                    continue
        except Exception:
            return []
        return surfaces

    def _generate_decorations(self):
        """Generate natural-looking, non-blocking decorative sprites.

        Decorations are placed only on grass tiles, away from the core path and
        away from shop/casino tiles. Path width is purely visual; path logic stays 1 tile.

        Trees support a simple z-layer: when the player is "behind" a tree (above its base),
        the tree is drawn in the foreground.
        """
        assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
        decor_root = os.path.join(assets_dir, "decoration")

        grass_patches = self._load_pngs_from_dir(os.path.join(decor_root, "5 Grass"))
        flowers = self._load_pngs_from_dir(os.path.join(decor_root, "6 Flower"))
        bushes = self._load_pngs_from_dir(os.path.join(decor_root, "9 Bush"))

        decor_misc = self._load_pngs_from_dir(os.path.join(decor_root, "7 Decor"))
        trees = [s for s in decor_misc if s and s.get_width() >= TILE_SIZE * 2 or s.get_height() >= TILE_SIZE * 2]
        if not trees:
            # Fallback: filter by filename pattern if sizes are small
            try:
                folder = os.path.join(decor_root, "7 Decor")
                trees = []
                for name in os.listdir(folder):
                    if name.lower().startswith("tree") and name.lower().endswith(".png"):
                        try:
                            trees.append(pygame.image.load(os.path.join(folder, name)).convert_alpha())
                        except Exception:
                            pass
            except Exception:
                trees = []

        shadows = self._load_pngs_from_dir(os.path.join(decor_root, "1 Shadow"))

        # Visual scale: make trees 20% larger.
        if trees:
            scaled_trees = []
            for img in trees:
                try:
                    w = max(1, int(img.get_width() * 1.2))
                    h = max(1, int(img.get_height() * 1.2))
                    scaled_trees.append(pygame.transform.scale(img, (w, h)))
                except Exception:
                    scaled_trees.append(img)
            trees = scaled_trees

        core_path_ids = {TILE_PATH, TILE_START, TILE_FINISH, TILE_CASTLE}

        def is_core_path(tx, ty):
            if tx < 0 or ty < 0 or tx >= TILES_X or ty >= TILES_Y:
                return False
            return self.tiles[ty][tx] in core_path_ids

        def near_core_path(tx, ty, radius=1):
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if abs(dx) + abs(dy) > radius:
                        continue
                    if is_core_path(tx + dx, ty + dy):
                        return True
            return False

        def near_special(tx, ty, radius=1):
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    nx = tx + dx
                    ny = ty + dy
                    if nx < 0 or ny < 0 or nx >= TILES_X or ny >= TILES_Y:
                        continue
                    if self.tiles[ny][nx] in (TILE_SHOP, TILE_CASINO, TILE_START, TILE_FINISH, TILE_CASTLE):
                        return True
            return False

        # Deterministic randomness so the map looks stable.
        rng = __import__("random").Random(1337)

        small = []  # patches/flowers/bushes, always behind player
        tree_list = []  # trees with base_y for simple z-layer
        tree_tiles = []

        for y in range(TILES_Y):
            for x in range(TILES_X):
                if self.tiles[y][x] != TILE_GRASS:
                    continue
                if near_core_path(x, y, radius=1):
                    continue
                if near_special(x, y, radius=1):
                    continue

                roll = rng.random()

                # Trees: rare + spacing
                if trees and roll < 0.006:
                    too_close = False
                    for tx, ty in tree_tiles:
                        if abs(tx - x) + abs(ty - y) <= 3:
                            too_close = True
                            break
                    if not too_close:
                        img = rng.choice(trees)
                        jitter_x = rng.randint(-6, 6)
                        jitter_y = rng.randint(-2, 2)
                        base_x = x * TILE_SIZE + TILE_SIZE // 2 + jitter_x
                        base_y = y * TILE_SIZE + TILE_SIZE + jitter_y

                        # Shadow (under tree, on ground)
                        shadow = rng.choice(shadows) if shadows else None
                        tree_list.append({
                            "img": img,
                            "shadow": shadow,
                            "base_x": base_x,
                            "base_y": base_y,
                        })
                        tree_tiles.append((x, y))
                    continue

                # Bushes
                if bushes and roll < 0.020:
                    img = rng.choice(bushes)
                    jitter_x = rng.randint(-6, 6)
                    jitter_y = rng.randint(-4, 4)
                    px = x * TILE_SIZE + jitter_x
                    py = y * TILE_SIZE + jitter_y
                    small.append({"img": img, "x": px, "y": py})
                    continue

                # Flowers
                if flowers and roll < 0.045:
                    img = rng.choice(flowers)
                    jitter_x = rng.randint(-6, 6)
                    jitter_y = rng.randint(-6, 6)
                    px = x * TILE_SIZE + jitter_x
                    py = y * TILE_SIZE + jitter_y
                    small.append({"img": img, "x": px, "y": py})
                    continue

                # Grass patches (most common)
                if grass_patches and roll < 0.10:
                    img = rng.choice(grass_patches)
                    jitter_x = rng.randint(-6, 6)
                    jitter_y = rng.randint(-6, 6)
                    px = x * TILE_SIZE + jitter_x
                    py = y * TILE_SIZE + jitter_y
                    small.append({"img": img, "x": px, "y": py})
                    continue

        return {"small": small, "trees": tree_list}

    def draw_tree_foreground(self, surface, *, player_bottom: int, offset: tuple[int, int] = (0, 0)):
        """Draw trees that should appear in front of the player (player is behind the tree)."""
        ox, oy = offset
        for t in self._decor.get("trees", []):
            base_y = int(t["base_y"])
            if player_bottom < base_y:
                img = t["img"]
                x = int(t["base_x"] - img.get_width() // 2) + ox
                y = int(t["base_y"] - img.get_height()) + oy
                surface.blit(img, (x, y))

    def _load_tile_surfaces(self):
        """Load 32x32 tile images from assets/tiles.

        Expected filenames (as provided):
        - grass.png
        - PATH MAIN.png
        - PATH EDGE LEFT.png / RIGHT / UP / DOWN
        """
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "tiles"))
        names = {
            "grass": "grass.png",
            "path_main": "PATH MAIN.png",
            "edge_left": "PATH EDGE LEFT.png",
            "edge_right": "PATH EDGE RIGHT.png",
            "edge_up": "PATH EDGE UP.png",
            "edge_down": "PATH EDGE DOWN.png",
        }

        surfaces = {}
        for key, filename in names.items():
            path = os.path.join(base_dir, filename)
            try:
                img = pygame.image.load(path).convert_alpha()
                if img.get_width() != TILE_SIZE or img.get_height() != TILE_SIZE:
                    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                surfaces[key] = img
            except Exception:
                surfaces[key] = None

        return surfaces

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


    def draw(self, surface, *, player_bottom: int | None = None, offset: tuple[int, int] = (0, 0)):
        ox, oy = offset
        # Core path tiles (walkable). We will only widen visually by drawing
        # edge tiles onto adjacent grass, without changing the actual grid.
        core_path_ids = {TILE_PATH, TILE_START, TILE_FINISH, TILE_CASTLE}

        def is_core_path(tx, ty):
            if tx < 0 or ty < 0 or tx >= TILES_X or ty >= TILES_Y:
                return False
            return self.tiles[ty][tx] in core_path_ids

        grass_img = self._tile_surfaces.get("grass")
        path_main_img = self._tile_surfaces.get("path_main")

        for y in range(TILES_Y):
            for x in range(TILES_X):
                tile_id = self.tiles[y][x]
                px = x * TILE_SIZE + ox
                py = y * TILE_SIZE + oy

                # Base tile rendering
                if tile_id in (TILE_GRASS, TILE_SHOP, TILE_CASINO) and grass_img is not None:
                    # Visual widening: if a grass tile touches the core path, draw an edge tile.
                    neighbors = {
                        "right": is_core_path(x + 1, y),
                        "left": is_core_path(x - 1, y),
                        "down": is_core_path(x, y + 1),
                        "up": is_core_path(x, y - 1),
                    }
                    touching = [k for k, v in neighbors.items() if v]

                    if len(touching) == 1:
                        side = touching[0]
                        # Edge images are named by where the GRASS is.
                        # Example: if core path is on the right, we need grass on the left -> EDGE LEFT.
                        if side == "right":
                            edge = self._tile_surfaces.get("edge_left")
                        elif side == "left":
                            edge = self._tile_surfaces.get("edge_right")
                        elif side == "down":
                            edge = self._tile_surfaces.get("edge_up")
                        else:  # up
                            edge = self._tile_surfaces.get("edge_down")

                        if edge is not None:
                            surface.blit(edge, (px, py))
                        else:
                            surface.blit(grass_img, (px, py))
                    elif len(touching) > 1 and path_main_img is not None:
                        # At corners/junctions, fill with main path to avoid incorrect edge orientation.
                        surface.blit(path_main_img, (px, py))
                    else:
                        surface.blit(grass_img, (px, py))

                elif tile_id in (TILE_PATH, TILE_START, TILE_FINISH) and path_main_img is not None:
                    surface.blit(path_main_img, (px, py))

                else:
                    # Fallback: existing solid-color tiles (castle/walls/etc.)
                    color = TILE_COLORS[tile_id]
                    pygame.draw.rect(surface, color, (px, py, TILE_SIZE, TILE_SIZE))

        # Decorations (always behind player)
        for d in self._decor.get("small", []):
            img = d.get("img")
            if img is None:
                continue
            surface.blit(img, (d.get("x", 0) + ox, d.get("y", 0) + oy))

        # Tree shadows (always on ground, behind player)
        for t in self._decor.get("trees", []):
            shadow = t.get("shadow")
            if shadow is None:
                # Fallback: simple ellipse shadow
                shadow_surf = pygame.Surface((TILE_SIZE, TILE_SIZE // 2), pygame.SRCALPHA)
                pygame.draw.ellipse(shadow_surf, (0, 0, 0, 90), shadow_surf.get_rect())
                sx = int(t["base_x"] - shadow_surf.get_width() // 2) + ox
                sy = int(t["base_y"] - shadow_surf.get_height() // 2) + oy
                surface.blit(shadow_surf, (sx, sy))
                continue

            # Scale shadow a bit based on tree size
            scale_w = max(TILE_SIZE, int(shadow.get_width() * 1.0))
            scale_h = max(8, int(shadow.get_height() * 1.0))
            sh = shadow
            if sh.get_width() != scale_w or sh.get_height() != scale_h:
                sh = pygame.transform.scale(sh, (scale_w, scale_h))
            sx = int(t["base_x"] - sh.get_width() // 2) + ox
            sy = int(t["base_y"] - sh.get_height() // 2) + oy
            surface.blit(sh, (sx, sy))

        # Trees behind player (or all trees if player_bottom not provided)
        for t in self._decor.get("trees", []):
            base_y = int(t["base_y"])
            if player_bottom is not None and player_bottom < base_y:
                continue
            img = t.get("img")
            if img is None:
                continue
            x = int(t["base_x"] - img.get_width() // 2) + ox
            y = int(t["base_y"] - img.get_height()) + oy
            surface.blit(img, (x, y))

        # Grid overlay - only draw if SHOW_GRID is enabled
        import settings
        if settings.SHOW_GRID:
            for x in range(TILES_X + 1):
                pygame.draw.line(
                    surface, (60, 60, 60),
                    (x * TILE_SIZE + ox, 0 + oy),
                    (x * TILE_SIZE + ox, SCREEN_HEIGHT + oy), 1
                )

            for y in range(TILES_Y + 1):
                pygame.draw.line(
                    surface, (60, 60, 60),
                    (0 + ox, y * TILE_SIZE + oy),
                    (SCREEN_WIDTH + ox, y * TILE_SIZE + oy), 1
                )
