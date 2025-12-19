import os
import pygame
from collections import deque
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
        self._castle_surface = self._load_castle_surface()
        self._castle_shadow_surface = self._build_castle_shadow(self._castle_surface)
        self._deco_grass_path_variants = self._build_deco_grass_path_variants(self._tile_surfaces.get("grass"))
        self._aesthetic_path_levels: dict[tuple[int, int], int] = {}
        # Precompute distance-to-path for visual grass shading (darker farther away)
        self._dist_to_path = self._compute_distance_to_path()
        self._grass_shades = self._build_grass_shades(self._tile_surfaces)
        self._decor = self._generate_decorations()
        # Needs decor to exist so we can start these trails from the nearby tree groves.
        self._aesthetic_path_levels = self._compute_aesthetic_paths_from_decor()

    def _build_castle_shadow(self, img: pygame.Surface | None) -> pygame.Surface | None:
        """Create a cheap silhouette shadow to draw "behind" the castle."""
        if img is None:
            return None
        try:
            shadow = img.copy()
            # Multiply RGB by 0 to make black; reduce alpha slightly.
            shadow.fill((0, 0, 0, 170), special_flags=pygame.BLEND_RGBA_MULT)
            return shadow
        except Exception:
            return None

    def _build_deco_grass_path_variants(self, grass: pygame.Surface | None) -> list[pygame.Surface] | None:
        """Create a few darker/lighter grass tiles for fading aesthetic paths."""
        if grass is None:
            return None
        try:
            variants: list[pygame.Surface] = []
            # 0 = darkest (near trees), higher = lighter (towards main path)
            factors = [0.72, 0.78, 0.84, 0.90, 0.96]
            for f in factors:
                img = grass.copy()
                img.fill((int(255 * f), int(255 * f), int(255 * f), 255), special_flags=pygame.BLEND_RGBA_MULT)
                # Slight noise-free overlay for readability
                overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 35))
                img.blit(overlay, (0, 0))
                variants.append(img)
            return variants
        except Exception:
            return None

    def _compute_aesthetic_paths_from_decor(self) -> dict[tuple[int, int], int]:
        """Compute visual-only paths from shop/casino to the nearby forest.

        Important: these trails must NOT connect to the enemy route (core path tiles).
        Returns a mapping tile -> fade level index.
        """
        core_path_ids = {TILE_PATH, TILE_START, TILE_FINISH, TILE_CASTLE}
        targets: list[tuple[int, int]] = []

        s = self.get_shop_tile()
        c = self.get_casino_tile()
        if s is not None:
            targets.append(s)
        if c is not None:
            targets.append(c)

        if not targets:
            return {}

        def in_bounds(x: int, y: int) -> bool:
            return 0 <= x < TILES_X and 0 <= y < TILES_Y

        def passable(x: int, y: int) -> bool:
            return self.tiles[y][x] != TILE_WALL

        # Approximate tree "forest" tiles from placed tree bases.
        forest_tiles: set[tuple[int, int]] = set()
        for t in self._decor.get("trees", []):
            try:
                tx = int(t.get("base_x", 0)) // TILE_SIZE
                ty = int(t.get("base_y", 0)) // TILE_SIZE
                if 0 <= tx < TILES_X and 0 <= ty < TILES_Y:
                    forest_tiles.add((tx, ty))
            except Exception:
                continue

        if not forest_tiles:
            return {}

        def nearest_forest_tile_to(target: tuple[int, int]) -> tuple[int, int]:
            tx, ty = target
            best = None
            best_d = 9999
            for fx, fy in forest_tiles:
                d = abs(fx - tx) + abs(fy - ty)
                if d < best_d:
                    best_d = d
                    best = (fx, fy)
            return best if best is not None else target

        out_levels: dict[tuple[int, int], int] = {}
        for target in targets:
            # Connect the building to the nearest forest tile, while avoiding the enemy route.
            start = target
            goal = nearest_forest_tile_to(target)

            # BFS from building to forest, forbidding the core path tiles.
            q = deque([start])
            parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
            found: tuple[int, int] | None = None
            while q and found is None:
                x, y = q.popleft()
                if (x, y) == goal:
                    found = (x, y)
                    break
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if not in_bounds(nx, ny) or not passable(nx, ny):
                        continue
                    # Never run this aesthetic path onto the enemy route.
                    if self.tiles[ny][nx] in core_path_ids:
                        continue
                    if (nx, ny) in parent:
                        continue
                    parent[(nx, ny)] = (x, y)
                    q.append((nx, ny))

            if found is None:
                continue

            # Reconstruct ordered path from building -> forest
            ordered: list[tuple[int, int]] = []
            cur = found
            while cur is not None:
                ordered.append(cur)
                cur = parent.get(cur)

            ordered.reverse()

            # Assign fade levels: darker near forest end, lighter near the building.
            levels = 5
            n = max(1, len(ordered))
            for i, (x, y) in enumerate(ordered):
                if self.tiles[y][x] not in (TILE_GRASS, TILE_SHOP, TILE_CASINO):
                    continue
                # i=0 near building => lightest, i=end near forest => darkest
                t = i / max(1, n - 1)
                lvl = int((1.0 - t) * (levels - 1))
                lvl = max(0, min(levels - 1, lvl))
                out_levels[(x, y)] = max(out_levels.get((x, y), 0), lvl)

        return out_levels

    def _load_castle_surface(self) -> pygame.Surface | None:
        """Load and scale the finish-point castle sprite (assets/CASTLE.png)."""
        try:
            assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
            path = os.path.join(assets_dir, "CASTLE.png")
            img = pygame.image.load(path).convert_alpha()

            # The source is extremely large; scale it to a few tiles so it fits the map.
            # Keep square aspect (the source is square).
            target_px = int(TILE_SIZE * 8)
            if target_px <= 0:
                return img
            if img.get_width() != target_px or img.get_height() != target_px:
                img = pygame.transform.smoothscale(img, (target_px, target_px))
            return img
        except Exception:
            return None

    def _get_finish_castle_rect(self, *, offset: tuple[int, int] = (0, 0)) -> pygame.Rect | None:
        """Compute the on-screen rect for the finish castle sprite.

        Returns a rect in *screen coordinates* (offset applied) or None.
        """
        if self._castle_surface is None:
            return None

        finish = self.get_finish_tile()
        if finish is None:
            return None

        ox, oy = offset
        fx, fy = finish

        # Find the adjacent path tile so we know how the path approaches the finish.
        core_path_ids = {TILE_PATH, TILE_START, TILE_FINISH, TILE_CASTLE}
        neighbor = None
        for nx, ny in ((fx - 1, fy), (fx + 1, fy), (fx, fy - 1), (fx, fy + 1)):
            if 0 <= nx < TILES_X and 0 <= ny < TILES_Y and self.tiles[ny][nx] in core_path_ids:
                if (nx, ny) != (fx, fy):
                    neighbor = (nx, ny)
                    break

        # Build the base rect in WORLD coordinates first, then add the draw offset.
        base_world = self._castle_surface.get_rect()
        base_world.midbottom = (
            fx * TILE_SIZE + TILE_SIZE // 2,
            (fy + 1) * TILE_SIZE,
        )

        # Preferred direction: place the castle "past" the finish tile away from the
        # incoming path segment. If that would push it off-map (common when finish is
        # on an edge), automatically flip to the opposite side to maximize visibility.
        pref_dx, pref_dy = (0, 0)
        if neighbor is not None:
            nx, ny = neighbor
            pref_dx = fx - nx
            pref_dy = fy - ny

        shift = TILE_SIZE * 2
        candidates: list[pygame.Rect] = []
        # preferred, flipped, and centered (fallback)
        candidates.append(base_world.move(pref_dx * shift, pref_dy * shift))
        candidates.append(base_world.move(-pref_dx * shift, -pref_dy * shift))
        candidates.append(base_world.copy())

        world_bounds = pygame.Rect(0, 0, TILES_X * TILE_SIZE, TILES_Y * TILE_SIZE)

        def visible_area(r: pygame.Rect) -> int:
            inter = r.clip(world_bounds)
            return max(0, inter.width) * max(0, inter.height)

        # Pick the candidate with the most on-map area.
        best = max(candidates, key=visible_area)
        if visible_area(best) == 0:
            # As a last resort, clamp the base rect into bounds.
            best = base_world.copy()
            best.clamp_ip(world_bounds)

        # User-tuned placement: drop the castle slightly lower.
        best.move_ip(0, TILE_SIZE * 3)
        return best.move(ox, oy)

    def _draw_castle_shadow(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self._castle_shadow_surface is None:
            return
        # Small offset to read as a "back" shadow.
        surface.blit(self._castle_shadow_surface, (rect.x + 10, rect.y + 10))

    def _draw_finish_castle(self, surface: pygame.Surface, *, offset: tuple[int, int] = (0, 0)) -> None:
        rect = self._get_finish_castle_rect(offset=offset)
        if rect is None:
            return
        surface.blit(self._castle_surface, rect.topleft)

    def _compute_distance_to_path(self) -> list[list[int]]:
        """Manhattan distance in tiles to the nearest core path tile.

        Used only for visuals (grass shading), so it can be approximate but stable.
        """
        core_path_ids = {TILE_PATH, TILE_START, TILE_FINISH, TILE_CASTLE}

        dist = [[9999 for _ in range(TILES_X)] for _ in range(TILES_Y)]
        q: deque[tuple[int, int]] = deque()

        for y in range(TILES_Y):
            for x in range(TILES_X):
                if self.tiles[y][x] in core_path_ids:
                    dist[y][x] = 0
                    q.append((x, y))

        # Multi-source BFS on the grid
        while q:
            x, y = q.popleft()
            d = dist[y][x] + 1
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if nx < 0 or ny < 0 or nx >= TILES_X or ny >= TILES_Y:
                    continue
                if d < dist[ny][nx]:
                    dist[ny][nx] = d
                    q.append((nx, ny))

        return dist

    def _build_grass_shades(self, surfaces: dict) -> dict[str, list[pygame.Surface] | None]:
        """Prebuild a small set of shaded variants for grass + grass edge tiles.

        Returns a dict with keys matching _tile_surfaces (grass + edge_*), each value is a
        list of surfaces for shade levels 0..N-1.
        """
        def shade_variants(img: pygame.Surface | None) -> list[pygame.Surface] | None:
            if img is None:
                return None
            variants: list[pygame.Surface] = []

            # 0 = normal, higher = darker. Keep subtle so it reads like atmosphere.
            # Tuned for 32x32 tiles.
            factors = [1.00, 0.92, 0.85, 0.78, 0.70]
            for f in factors:
                v = img.copy()
                # Multiply RGB by factor (keep alpha)
                v.fill((int(255 * f), int(255 * f), int(255 * f), 255), special_flags=pygame.BLEND_RGBA_MULT)
                variants.append(v)
            return variants

        return {
            "grass": shade_variants(surfaces.get("grass")),
            "edge_left": shade_variants(surfaces.get("edge_left")),
            "edge_right": shade_variants(surfaces.get("edge_right")),
            "edge_up": shade_variants(surfaces.get("edge_up")),
            "edge_down": shade_variants(surfaces.get("edge_down")),
        }
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

    def _load_pngs_with_names_from_dir(self, folder_path):
        items = []
        try:
            for name in os.listdir(folder_path):
                if not name.lower().endswith(".png"):
                    continue
                path = os.path.join(folder_path, name)
                try:
                    img = pygame.image.load(path).convert_alpha()
                    items.append((name, img))
                except Exception:
                    continue
        except Exception:
            return []
        return items

    def _generate_decorations(self):
        """Generate natural-looking, non-blocking decorative sprites.

        Decorations are placed only on grass tiles, away from the core path and
        away from shop/casino tiles. Path width is purely visual; path logic stays 1 tile.

        Trees support a simple z-layer: when the player is "behind" a tree (above its base),
        the tree is drawn in the foreground.
        """
        assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
        decor_root = os.path.join(assets_dir, "decoration")

        # Keep a clear area for the finish landmark (castle) so it stays visible.
        castle_keepout: pygame.Rect | None = None
        try:
            r = self._get_finish_castle_rect(offset=(0, 0))
            if r is not None:
                # Inflate a bit to avoid trunks/shadows sitting directly on the castle.
                castle_keepout = r.inflate(TILE_SIZE * 4, TILE_SIZE * 4)
        except Exception:
            castle_keepout = None

        # Set-piece assets
        campfire_img = None
        try:
            campfire_sheet = pygame.image.load(os.path.join(assets_dir, "campfire-sheet.png")).convert_alpha()
            # First frame of a 4-frame 64x64 strip (256x64)
            if campfire_sheet.get_height() > 0:
                fw = campfire_sheet.get_height()
                campfire_img = campfire_sheet.subsurface(pygame.Rect(0, 0, fw, fw)).copy()
        except Exception:
            campfire_img = None

        grass_patches = self._load_pngs_from_dir(os.path.join(decor_root, "5 Grass"))
        flowers = self._load_pngs_from_dir(os.path.join(decor_root, "6 Flower"))
        bushes = self._load_pngs_from_dir(os.path.join(decor_root, "9 Bush"))

        stones = self._load_pngs_from_dir(os.path.join(decor_root, "4 Stone"))
        stones_named = self._load_pngs_with_names_from_dir(os.path.join(decor_root, "4 Stone"))
        camp = self._load_pngs_from_dir(os.path.join(decor_root, "8 Camp"))
        camp_named = self._load_pngs_with_names_from_dir(os.path.join(decor_root, "8 Camp"))

        decor_misc_folder = os.path.join(decor_root, "7 Decor")
        decor_misc = self._load_pngs_with_names_from_dir(decor_misc_folder)

        # Split misc decor into trees vs smaller props.
        # IMPORTANT: treat files named like "Tree1.png" / "Tree2.png" as trees regardless of size.
        trees: list[pygame.Surface] = []
        tree1: list[pygame.Surface] = []
        tree2: list[pygame.Surface] = []
        logs: list[pygame.Surface] = []
        lamps: list[pygame.Surface] = []
        props: list[pygame.Surface] = []
        for name, s in decor_misc:
            if s is None:
                continue
            lower = name.lower()
            if "log" in lower:
                logs.append(s)
                props.append(s)
                continue
            if lower.startswith("lamp"):
                lamps.append(s)
                props.append(s)
                continue
            if "tree" in lower:
                if "tree1" in lower:
                    tree1.append(s)
                    trees.append(s)
                elif "tree2" in lower:
                    # Keep Tree2 separate: only allowed right next to the path.
                    tree2.append(s)
                else:
                    trees.append(s)
                continue

            # Heuristic: taller sprites read as trees/large plants.
            if s.get_height() >= int(TILE_SIZE * 2.6):
                trees.append(s)
            else:
                props.append(s)

        shadows = self._load_pngs_from_dir(os.path.join(decor_root, "1 Shadow"))

        # Visual scale: make trees 20% larger.
        if trees or tree2:
            def _scale_120(images: list[pygame.Surface]) -> list[pygame.Surface]:
                scaled = []
                for img in images:
                    try:
                        w = max(1, int(img.get_width() * 1.2))
                        h = max(1, int(img.get_height() * 1.2))
                        scaled.append(pygame.transform.scale(img, (w, h)))
                    except Exception:
                        scaled.append(img)
                return scaled

            trees = _scale_120(trees) if trees else []
            tree1 = _scale_120(tree1) if tree1 else []
            tree2 = _scale_120(tree2) if tree2 else []

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

        # Keep a clear buffer around shop/casino so tall sprites (trees) don't overlap.
        SHOP_TREE_BUFFER = 3

        # Deterministic randomness so the map looks stable.
        rng = __import__("random").Random(1337)

        small = []  # patches/flowers/bushes/rocks/props, always behind player
        tree_list = []  # trees with base_y for simple z-layer
        tree_tiles = []

        # Make the decor look more "natural" by clustering trees/undergrowth in a few
        # forest zones instead of spreading them evenly.
        candidate_grass = []
        for y in range(TILES_Y):
            for x in range(TILES_X):
                if self.tiles[y][x] != TILE_GRASS:
                    continue
                if near_core_path(x, y, radius=1):
                    continue
                if near_special(x, y, radius=SHOP_TREE_BUFFER):
                    continue
                candidate_grass.append((x, y))

        forest_centers = []
        if candidate_grass:
            def pick_from_region(predicate):
                region = [p for p in candidate_grass if predicate(p[0], p[1])]
                if not region:
                    return None
                return rng.choice(region)

            # Always seed clusters in the areas the user cares about.
            ul_region_pred = lambda tx, ty: tx < int(TILES_X * 0.35) and ty < int(TILES_Y * 0.35)
            ul = pick_from_region(ul_region_pred)
            # Extra UL forest centers so it reads like a forest, not scattered trees.
            ul2 = pick_from_region(ul_region_pred)
            ul3 = pick_from_region(ul_region_pred)
            center = pick_from_region(
                lambda tx, ty: abs(tx - (TILES_X // 2)) <= int(TILES_X * 0.18)
                and abs(ty - (TILES_Y // 2)) <= int(TILES_Y * 0.18)
            )
            lower = pick_from_region(lambda tx, ty: ty > int(TILES_Y * 0.65))

            for c in (ul, ul2, ul3, center, lower):
                if c is not None:
                    forest_centers.append(c)

            # Additional clusters to keep the map feeling alive.
            for _ in range(min(10, max(4, len(candidate_grass) // 140))):
                forest_centers.append(rng.choice(candidate_grass))

        def region_tree_boost(tx: int, ty: int) -> float:
            # Extra trees specifically in: upper-left, center, and lower part.
            boost = 1.0

            # upper-left
            if tx < int(TILES_X * 0.35) and ty < int(TILES_Y * 0.35):
                boost *= 1.8

            # center
            if abs(tx - (TILES_X // 2)) <= int(TILES_X * 0.18) and abs(ty - (TILES_Y // 2)) <= int(TILES_Y * 0.18):
                boost *= 1.6

            # lower part (lower third)
            if ty > int(TILES_Y * 0.65):
                boost *= 1.7

            return boost

        def ul_forest_strength(tx: int, ty: int) -> float:
            """0..1 strength for how deep into the upper-left forest core we are."""
            if not (tx < int(TILES_X * 0.35) and ty < int(TILES_Y * 0.35)):
                return 0.0
            if ul is None:
                return 0.35
            cx, cy = ul
            d = abs(cx - tx) + abs(cy - ty)
            if d <= 2:
                return 1.0
            if d <= 4:
                return 0.85
            if d <= 6:
                return 0.6
            if d <= 8:
                return 0.35
            return 0.2

        def forest_factor(tx: int, ty: int) -> float:
            if not forest_centers:
                return 1.0
            best = 999
            for cx, cy in forest_centers:
                d = abs(cx - tx) + abs(cy - ty)
                if d < best:
                    best = d
            # Simple falloff (tile distance): tight clusters with soft edges.
            if best <= 2:
                return 1.0
            if best <= 4:
                return 0.65
            if best <= 6:
                return 0.35
            return 0.15

        # Very sparse "set pieces" like camp items should not clump.
        camp_tiles = []

        # Pick specific stone variants requested (7.png, 8.png, 11.png)
        stones_7_8_11: list[pygame.Surface] = []
        for n, s in stones_named:
            if s is None:
                continue
            if n in ("7.png", "8.png", "11.png"):
                stones_7_8_11.append(s)

        # Camp 1 (1.png)
        camp_1 = None
        for n, s in camp_named:
            if n == "1.png":
                camp_1 = s
                break

        def _place_tree_at(tx: int, ty: int, *, prefer_tree1: bool = True):
            if tx < 0 or ty < 0 or tx >= TILES_X or ty >= TILES_Y:
                return
            if self.tiles[ty][tx] != TILE_GRASS:
                return
            if near_core_path(tx, ty, radius=1):
                return
            if near_special(tx, ty, radius=SHOP_TREE_BUFFER):
                return
            if prefer_tree1 and tree1:
                img = rng.choice(tree1)
            elif trees:
                img = rng.choice(trees)
            else:
                return

            jitter_x = rng.randint(-6, 6)
            jitter_y = rng.randint(-2, 2)
            base_x = tx * TILE_SIZE + TILE_SIZE // 2 + jitter_x
            base_y = ty * TILE_SIZE + TILE_SIZE + jitter_y

            if castle_keepout is not None and castle_keepout.collidepoint(base_x, base_y):
                return

            shadow = rng.choice(shadows) if shadows else None
            tree_list.append({
                "img": img,
                "shadow": shadow,
                "base_x": base_x,
                "base_y": base_y,
            })
            tree_tiles.append((tx, ty))

        def _place_castle_forest_tree_at(tx: int, ty: int):
            """Place a tree intended to overlap the bottom of the castle.

            This bypasses the castle keepout so we can intentionally overlap.
            """
            if tx < 0 or ty < 0 or tx >= TILES_X or ty >= TILES_Y:
                return
            if self.tiles[ty][tx] != TILE_GRASS:
                return
            # Never place these on the actual path tiles.
            if self.tiles[ty][tx] in (TILE_PATH, TILE_START, TILE_FINISH, TILE_CASTLE):
                return
            if near_core_path(tx, ty, radius=0):
                return
            if near_special(tx, ty, radius=SHOP_TREE_BUFFER):
                return
            if tree1:
                img = rng.choice(tree1)
            elif trees:
                img = rng.choice(trees)
            else:
                return

            jitter_x = rng.randint(-8, 8)
            jitter_y = rng.randint(-4, 2)
            base_x = tx * TILE_SIZE + TILE_SIZE // 2 + jitter_x
            base_y = ty * TILE_SIZE + TILE_SIZE + jitter_y
            shadow = rng.choice(shadows) if shadows else None
            tree_list.append({
                "img": img,
                "shadow": shadow,
                "base_x": base_x,
                "base_y": base_y,
            })

        def _place_small_at(tx: int, ty: int, img: pygame.Surface, *, dx: int = 0, dy: int = 0, anchor_ground: bool = True):
            if img is None:
                return
            if tx < 0 or ty < 0 or tx >= TILES_X or ty >= TILES_Y:
                return
            if self.tiles[ty][tx] != TILE_GRASS:
                return
            if near_core_path(tx, ty, radius=1):
                return
            if near_special(tx, ty, radius=1):
                return

            if anchor_ground:
                px = tx * TILE_SIZE + TILE_SIZE // 2 - img.get_width() // 2 + dx
                py = ty * TILE_SIZE + TILE_SIZE - img.get_height() + dy
            else:
                px = tx * TILE_SIZE + dx
                py = ty * TILE_SIZE + dy
            small.append({"img": img, "x": px, "y": py})

        for y in range(TILES_Y):
            for x in range(TILES_X):
                if self.tiles[y][x] != TILE_GRASS:
                    continue
                if near_core_path(x, y, radius=1):
                    continue
                # Keep trees away from shop/casino by several tiles; other small decor can be closer.
                if near_special(x, y, radius=1):
                    continue

                roll = rng.random()

                ff = forest_factor(x, y)
                ul_strength = ul_forest_strength(x, y)

                # Camp props: very rare, spaced out
                if camp and roll < (0.0007 * ff):
                    too_close = False
                    for cx, cy in camp_tiles:
                        if abs(cx - x) + abs(cy - y) <= 6:
                            too_close = True
                            break
                    if not too_close:
                        img = rng.choice(camp)
                        jitter_x = rng.randint(-6, 6)
                        jitter_y = rng.randint(-6, 6)
                        px = x * TILE_SIZE + jitter_x
                        py = y * TILE_SIZE + jitter_y
                        small.append({"img": img, "x": px, "y": py})
                        camp_tiles.append((x, y))
                    continue

                # Trees (including Tree1.png): boosted in specific map regions.
                # Upper-left gets a dense "forest" look (more trees, closer spacing).
                tree_prob = 0.040 * ff * region_tree_boost(x, y)
                if ul_strength > 0:
                    # Stronger upper-left boost so it clearly becomes a forest.
                    tree_prob = max(tree_prob, 0.13 * (0.35 + 0.65 * ul_strength))

                if trees and roll < tree_prob:
                    # Extra buffer so trees don't overlap shops/casinos.
                    if near_special(x, y, radius=SHOP_TREE_BUFFER):
                        continue
                    too_close = False
                    # Allow very tight packing deep in the UL forest.
                    if ul_strength >= 0.85:
                        min_dist = 0
                    elif ul_strength >= 0.6:
                        min_dist = 1
                    else:
                        min_dist = 2
                    for tx, ty in tree_tiles:
                        if abs(tx - x) + abs(ty - y) <= min_dist:
                            too_close = True
                            break
                    if not too_close:
                        # Replace Tree2 with Tree1 everywhere, except *right next to the path*.
                        # (Current generation avoids path-adjacent tiles, but keep this rule for future levels.)
                        adjacent_to_path = near_core_path(x, y, radius=1)

                        if adjacent_to_path and tree2:
                            img = rng.choice(tree2)
                        else:
                            # Bias UL forest to use Tree1 most of the time.
                            if ul_strength >= 0.6 and tree1 and rng.random() < 0.85:
                                img = rng.choice(tree1)
                            else:
                                img = rng.choice(trees)
                        jitter_x = rng.randint(-6, 6)
                        jitter_y = rng.randint(-2, 2)
                        base_x = x * TILE_SIZE + TILE_SIZE // 2 + jitter_x
                        base_y = y * TILE_SIZE + TILE_SIZE + jitter_y

                        # Shadow (under tree, on ground)
                        # Always give trees a shadow. If shadow art is missing, auto-shadow will be used.
                        shadow = rng.choice(shadows) if shadows else None
                        tree_list.append({
                            "img": img,
                            "shadow": shadow,
                            "base_x": base_x,
                            "base_y": base_y,
                        })
                        tree_tiles.append((x, y))
                    continue

                # Stones / rocks (a bit more common)
                if stones and roll < (0.028 * (0.35 + 0.65 * ff)):
                    img = rng.choice(stones)
                    jitter_x = rng.randint(-6, 6)
                    jitter_y = rng.randint(-6, 6)
                    px = x * TILE_SIZE + jitter_x
                    py = y * TILE_SIZE + jitter_y
                    small.append({"img": img, "x": px, "y": py})
                    continue

                # Misc small props
                if props and roll < (0.010 * (0.25 + 0.75 * ff)):
                    img = rng.choice(props)
                    jitter_x = rng.randint(-6, 6)
                    jitter_y = rng.randint(-6, 6)
                    px = x * TILE_SIZE + jitter_x
                    py = y * TILE_SIZE + jitter_y
                    small.append({"img": img, "x": px, "y": py})
                    continue

                # Bushes (more throughout the map)
                if bushes and roll < (0.055 * (0.40 + 0.60 * ff)):
                    img = rng.choice(bushes)
                    jitter_x = rng.randint(-6, 6)
                    jitter_y = rng.randint(-4, 4)
                    px = x * TILE_SIZE + jitter_x
                    py = y * TILE_SIZE + jitter_y
                    small.append({"img": img, "x": px, "y": py})
                    continue

                # Flowers (more common)
                if flowers and roll < (0.095 * (0.35 + 0.65 * ff)):
                    img = rng.choice(flowers)
                    jitter_x = rng.randint(-6, 6)
                    jitter_y = rng.randint(-6, 6)
                    px = x * TILE_SIZE + jitter_x
                    py = y * TILE_SIZE + jitter_y
                    small.append({"img": img, "x": px, "y": py})
                    continue

                # Grass patches (most common, slightly denser)
                if grass_patches and roll < (0.22 * (0.55 + 0.45 * ff)):
                    img = rng.choice(grass_patches)
                    jitter_x = rng.randint(-6, 6)
                    jitter_y = rng.randint(-6, 6)
                    px = x * TILE_SIZE + jitter_x
                    py = y * TILE_SIZE + jitter_y
                    small.append({"img": img, "x": px, "y": py})
                    continue

        # ------------------------------------------------------------------
        # Corner set pieces (world-space):
        # - Bottom-left: campfire + some logs + dense Tree1 forest
        # - Bottom-right: more Tree1 (with shadows) + stones and nature props
        # ------------------------------------------------------------------
        bl_x0, bl_x1 = 0, max(1, int(TILES_X * 0.28))
        bl_y0, bl_y1 = max(0, int(TILES_Y * 0.70)), TILES_Y - 1
        br_x0, br_x1 = max(0, int(TILES_X * 0.72)), TILES_X - 1
        br_y0, br_y1 = max(0, int(TILES_Y * 0.70)), TILES_Y - 1

        def _find_grass_in_box(x0: int, x1: int, y0: int, y1: int):
            for ty in range(y1, y0 - 1, -1):
                for tx in range(x0, x1 + 1):
                    if tx < 0 or ty < 0 or tx >= TILES_X or ty >= TILES_Y:
                        continue
                    if self.tiles[ty][tx] != TILE_GRASS:
                        continue
                    if near_core_path(tx, ty, radius=1):
                        continue
                    if near_special(tx, ty, radius=1):
                        continue
                    return (tx, ty)
            return None

        # Bottom-left campfire set-piece
        camp_tile = _find_grass_in_box(bl_x0 + 1, bl_x1 - 1, bl_y0 + 1, bl_y1 - 1)
        if camp_tile and campfire_img is not None:
            cx, cy = camp_tile
            _place_small_at(cx, cy, campfire_img, dy=4, anchor_ground=True)
            if logs:
                # A few logs around the fire
                _place_small_at(cx - 1, cy, rng.choice(logs), dx=-10, dy=10, anchor_ground=True)
                _place_small_at(cx + 1, cy, rng.choice(logs), dx=10, dy=10, anchor_ground=True)
                _place_small_at(cx, cy + 1, rng.choice(logs), dx=0, dy=14, anchor_ground=True)

            # Dense Tree1 forest around the campfire
            if tree1:
                added = 0
                for ty in range(bl_y0, bl_y1 + 1):
                    for tx in range(bl_x0, bl_x1 + 1):
                        if added >= 60:
                            break
                        if abs(tx - cx) + abs(ty - cy) <= 1:
                            continue
                        if rng.random() < 0.55:
                            _place_tree_at(tx, ty, prefer_tree1=True)
                            added += 1
                    if added >= 60:
                        break

        # Bottom-right: extra Tree1 + stones + nature
        if tree1:
            added = 0
            for ty in range(br_y0, br_y1 + 1):
                for tx in range(br_x0, br_x1 + 1):
                    if added >= 45:
                        break
                    # Slight spacing so it reads like a grove, not a solid wall.
                    if (tx + ty) % 2 == 0 and rng.random() < 0.42:
                        _place_tree_at(tx, ty, prefer_tree1=True)
                        added += 1
                if added >= 45:
                    break

        # Extra stones and greenery in the bottom-right corner
        added_small = 0
        for ty in range(br_y0, br_y1 + 1):
            for tx in range(br_x0, br_x1 + 1):
                if added_small >= 90:
                    break
                if self.tiles[ty][tx] != TILE_GRASS:
                    continue
                if near_core_path(tx, ty, radius=1) or near_special(tx, ty, radius=1):
                    continue

                r = rng.random()
                if stones and r < 0.22:
                    _place_small_at(tx, ty, rng.choice(stones), dx=rng.randint(-6, 6), dy=rng.randint(-4, 8), anchor_ground=True)
                    added_small += 1
                elif bushes and r < 0.34:
                    _place_small_at(tx, ty, rng.choice(bushes), dx=rng.randint(-6, 6), dy=rng.randint(-4, 6), anchor_ground=True)
                    added_small += 1
                elif flowers and r < 0.48:
                    _place_small_at(tx, ty, rng.choice(flowers), dx=rng.randint(-6, 6), dy=rng.randint(-4, 6), anchor_ground=True)
                    added_small += 1
                elif grass_patches and r < 0.70:
                    _place_small_at(tx, ty, rng.choice(grass_patches), dx=rng.randint(-6, 6), dy=rng.randint(-4, 6), anchor_ground=True)
                    added_small += 1
            if added_small >= 90:
                break

        # ------------------------------------------------------------------
        # Path-adjacent dressing: stones (7/8/11), more flowers, lamp1/lamp2, logs.
        # Also add more trees with shadows near shop/casino.
        # ------------------------------------------------------------------
        def adjacent_to_core_path(tx: int, ty: int) -> bool:
            if self.tiles[ty][tx] != TILE_GRASS:
                return False
            # Only immediate adjacency for "around the path"
            return near_core_path(tx, ty, radius=1)

        # Collect grass tiles that border the path (but are not special tiles)
        path_edge_grass: list[tuple[int, int]] = []
        for ty in range(TILES_Y):
            for tx in range(TILES_X):
                if adjacent_to_core_path(tx, ty) and not near_special(tx, ty, radius=1):
                    path_edge_grass.append((tx, ty))

        rng.shuffle(path_edge_grass)

        # Place a limited number so it doesn't clutter everything.
        placed = 0
        for (tx, ty) in path_edge_grass:
            if placed >= 140:
                break
            r = rng.random()

            # stones 7/8/11
            if stones_7_8_11 and r < 0.28:
                _place_small_at(tx, ty, rng.choice(stones_7_8_11), dx=rng.randint(-6, 6), dy=rng.randint(-4, 8), anchor_ground=True)
                placed += 1
                continue

            # flowers
            if flowers and r < 0.52:
                _place_small_at(tx, ty, rng.choice(flowers), dx=rng.randint(-6, 6), dy=rng.randint(-6, 6), anchor_ground=True)
                placed += 1
                continue

            # lamp1 / lamp2 (from 7 Decor)
            if lamps and r < 0.60:
                # Lamps are taller, anchor to ground
                _place_small_at(tx, ty, rng.choice(lamps), dx=rng.randint(-4, 4), dy=rng.randint(-2, 2), anchor_ground=True)
                placed += 1
                continue

            # log 1/2/4 (logs list already filtered to Log*.png)
            if logs and r < 0.72:
                _place_small_at(tx, ty, rng.choice(logs), dx=rng.randint(-8, 8), dy=rng.randint(6, 14), anchor_ground=True)
                placed += 1
                continue

            # extra bushes
            if bushes and r < 0.88:
                _place_small_at(tx, ty, rng.choice(bushes), dx=rng.randint(-6, 6), dy=rng.randint(-4, 6), anchor_ground=True)
                placed += 1
                continue

        # Trees near shop/casino with shadows (but keep a clear 3-tile buffer)
        special_tiles: list[tuple[int, int]] = []
        for ty in range(TILES_Y):
            for tx in range(TILES_X):
                if self.tiles[ty][tx] in (TILE_SHOP, TILE_CASINO):
                    special_tiles.append((tx, ty))

        for sx, sy in special_tiles:
            # Place trees OUTSIDE the buffer so they feel "near" but never overlap.
            for ty in range(max(0, sy - (SHOP_TREE_BUFFER + 3)), min(TILES_Y, sy + (SHOP_TREE_BUFFER + 4))):
                for tx in range(max(0, sx - (SHOP_TREE_BUFFER + 3)), min(TILES_X, sx + (SHOP_TREE_BUFFER + 4))):
                    if self.tiles[ty][tx] != TILE_GRASS:
                        continue
                    if near_core_path(tx, ty, radius=1):
                        continue
                    d = abs(tx - sx) + abs(ty - sy)
                    if d <= SHOP_TREE_BUFFER:
                        continue
                    # Light density so it reads like a grove around the building.
                    if rng.random() < 0.22:
                        _place_tree_at(tx, ty, prefer_tree1=True)

        # Camp 1 + campfire + logs set-piece somewhere near the path (but on grass)
        if camp_1 is not None and campfire_img is not None:
            # Prefer a path-adjacent grass tile in the lower half so the player sees it.
            candidate = next(((tx, ty) for (tx, ty) in path_edge_grass if ty > int(TILES_Y * 0.55)), None)
            if candidate is not None:
                cx, cy = candidate
                _place_small_at(cx, cy, camp_1, dy=6, anchor_ground=True)
                _place_small_at(cx + 1, cy, campfire_img, dy=4, anchor_ground=True)
                if logs:
                    _place_small_at(cx, cy + 1, rng.choice(logs), dx=-6, dy=12, anchor_ground=True)
                    _place_small_at(cx + 1, cy + 1, rng.choice(logs), dx=8, dy=12, anchor_ground=True)
                    _place_small_at(cx - 1, cy, rng.choice(logs), dx=-10, dy=10, anchor_ground=True)

        # Add a small "forest" in the upper-left of the screen near the castle,
        # and let the castle overlap it so mainly leaves peek out.
        try:
            if self._castle_surface is not None:
                castle_rect = self._get_finish_castle_rect(offset=(0, 0))
            else:
                castle_rect = None
        except Exception:
            castle_rect = None

        if castle_rect is not None:
            # Put it clearly in the upper-left of the screen relative to the castle.
            ul_left_tx = max(0, min(TILES_X - 1, (castle_rect.left // TILE_SIZE) - 3))
            ul_right_tx = min(TILES_X - 1, ul_left_tx + 7)
            ul_top_ty = max(0, min(TILES_Y - 1, (castle_rect.top // TILE_SIZE) - 4))
            ul_bottom_ty = min(TILES_Y - 1, ul_top_ty + 6)

            for ty in range(ul_top_ty, ul_bottom_ty + 1):
                for tx in range(ul_left_tx, ul_right_tx + 1):
                    if self.tiles[ty][tx] != TILE_GRASS:
                        continue
                    if near_core_path(tx, ty, radius=1):
                        continue
                    # Slightly denser near the castle edge.
                    d = abs(tx - ul_right_tx) + abs(ty - ul_bottom_ty)
                    p = 0.72 if d <= 3 else 0.45
                    if rng.random() < p:
                        _place_castle_forest_tree_at(tx, ty)

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

    def _shade_level_for_tile(self, tx: int, ty: int) -> int:
        """0..4 shade level for grass-like tiles based on distance to path."""
        try:
            d = self._dist_to_path[ty][tx]
        except Exception:
            return 0

        # Dist buckets: quickly fades after you leave the path, then levels off.
        # 0-1: normal/near path, 2-3: slightly darker, 4-5: darker, 6-8: darkest.
        if d <= 1:
            return 0
        if d <= 3:
            return 1
        if d <= 5:
            return 2
        if d <= 8:
            return 3
        return 4

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

    def _find_first_tile(self, tile_id: int):
        for y in range(TILES_Y):
            for x in range(TILES_X):
                if self.tiles[y][x] == tile_id:
                    return (x, y)
        return None

    def get_shop_tile(self):
        return self._find_first_tile(TILE_SHOP)

    def get_casino_tile(self):
        return self._find_first_tile(TILE_CASINO)

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
                    shade_level = self._shade_level_for_tile(x, y)
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
                            shaded = (self._grass_shades.get("edge_left") or [])
                        elif side == "left":
                            edge = self._tile_surfaces.get("edge_right")
                            shaded = (self._grass_shades.get("edge_right") or [])
                        elif side == "down":
                            edge = self._tile_surfaces.get("edge_up")
                            shaded = (self._grass_shades.get("edge_up") or [])
                        else:  # up
                            edge = self._tile_surfaces.get("edge_down")
                            shaded = (self._grass_shades.get("edge_down") or [])

                        if edge is not None:
                            if shaded and 0 <= shade_level < len(shaded):
                                surface.blit(shaded[shade_level], (px, py))
                            else:
                                surface.blit(edge, (px, py))
                        else:
                            shaded_grass = (self._grass_shades.get("grass") or [])
                            if shaded_grass and 0 <= shade_level < len(shaded_grass):
                                surface.blit(shaded_grass[shade_level], (px, py))
                            else:
                                surface.blit(grass_img, (px, py))
                    elif len(touching) > 1 and path_main_img is not None:
                        # At corners/junctions, fill with main path to avoid incorrect edge orientation.
                        surface.blit(path_main_img, (px, py))
                    else:
                        shaded_grass = (self._grass_shades.get("grass") or [])
                        if shaded_grass and 0 <= shade_level < len(shaded_grass):
                            surface.blit(shaded_grass[shade_level], (px, py))
                        else:
                            surface.blit(grass_img, (px, py))

                    # Visual-only fading grass path for shop/casino access.
                    if self._deco_grass_path_variants is not None:
                        lvl = self._aesthetic_path_levels.get((x, y))
                        if lvl is not None:
                            lvl = max(0, min(len(self._deco_grass_path_variants) - 1, int(lvl)))
                            surface.blit(self._deco_grass_path_variants[lvl], (px, py))

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
                # Fallback: ellipse shadow sized to the tree.
                auto = t.get("_auto_shadow")
                if auto is None:
                    img = t.get("img")
                    tree_w = img.get_width() if img is not None else TILE_SIZE * 2

                    sw = max(TILE_SIZE, int(tree_w * 0.55))
                    sh = max(8, int(TILE_SIZE * 0.55))
                    auto = pygame.Surface((sw, sh), pygame.SRCALPHA)
                    pygame.draw.ellipse(auto, (0, 0, 0, 95), auto.get_rect())
                    t["_auto_shadow"] = auto

                sx = int(t["base_x"] - auto.get_width() // 2) + ox
                sy = int(t["base_y"] - auto.get_height() // 2) + oy
                surface.blit(auto, (sx, sy))
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

        # Finish landmark (castle) should participate in depth ordering:
        # - Trees with a smaller base_y ("upper" trees) are drawn first, so the castle covers them.
        # - Trees with a larger base_y ("lower" trees) are drawn after, so they cover the castle.
        castle_rect = self._get_finish_castle_rect(offset=offset)
        castle_base_y_world = None
        if castle_rect is not None:
            castle_base_y_world = int(castle_rect.bottom - oy)

        # Trees behind player (or all trees if player_bottom not provided): PART 1 (behind castle)
        for t in self._decor.get("trees", []):
            base_y = int(t["base_y"])
            if player_bottom is not None and player_bottom < base_y:
                continue
            if castle_base_y_world is not None and base_y > castle_base_y_world:
                continue
            img = t.get("img")
            if img is None:
                continue
            x = int(t["base_x"] - img.get_width() // 2) + ox
            y = int(t["base_y"] - img.get_height()) + oy
            surface.blit(img, (x, y))

        # Castle
        if castle_rect is not None and self._castle_surface is not None:
            self._draw_castle_shadow(surface, castle_rect)
            surface.blit(self._castle_surface, castle_rect.topleft)

        # Trees behind player: PART 2 (in front of castle)
        for t in self._decor.get("trees", []):
            base_y = int(t["base_y"])
            if player_bottom is not None and player_bottom < base_y:
                continue
            if castle_base_y_world is None or base_y <= castle_base_y_world:
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
