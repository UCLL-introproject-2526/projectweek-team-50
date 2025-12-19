import os
import math
import pygame
from settings import TILE_SIZE, RED, GREEN, BLACK


# Cache loaded animation frames across all Enemy instances.
# Key: (wave_num, enemy_type)
_ANIM_CACHE: dict[tuple[int, str], dict[str, list[pygame.Surface]]] = {}


def _infer_grid_cell_size(w: int, h: int) -> int:
    """Best-effort frame cell size for grid sheets.

    Many provided sheets are multiples of 32px (e.g., 96x128 => 3x4 grid).
    """
    g = math.gcd(w, h)
    # Prefer common pixel-art cell sizes if they divide both.
    for c in (32, 48, 64, 96, 16):
        if w % c == 0 and h % c == 0:
            return c
    return g if g > 0 else min(w, h)


def _split_strip(sheet: pygame.Surface) -> list[pygame.Surface]:
    """Split a horizontal strip where each frame is a square (frame = height x height)."""
    frames: list[pygame.Surface] = []
    w, h = sheet.get_width(), sheet.get_height()
    # Treat only true horizontal strips as strips. Square sheets (w == h)
    # are commonly grids and should not be classified as a 1-frame strip.
    if h <= 0 or w <= h:
        return frames
    if w % h != 0:
        return frames
    count = w // h
    for i in range(count):
        frame = sheet.subsurface(pygame.Rect(i * h, 0, h, h)).copy()
        if pygame.mask.from_surface(frame).count() == 0:
            continue
        frames.append(frame)
    return frames


def _split_vertical_strip(sheet: pygame.Surface) -> list[pygame.Surface]:
    """Split a vertical strip where each frame is a square (frame = width x width)."""
    frames: list[pygame.Surface] = []
    w, h = sheet.get_width(), sheet.get_height()
    if w <= 0 or h <= w:
        return frames
    if h % w != 0:
        return frames
    count = h // w
    for i in range(count):
        frame = sheet.subsurface(pygame.Rect(0, i * w, w, w)).copy()
        if pygame.mask.from_surface(frame).count() == 0:
            continue
        frames.append(frame)
    return frames


def _split_grid(sheet: pygame.Surface, cell: int) -> list[list[pygame.Surface]]:
    """Split a spritesheet into a grid of cell x cell frames (rows x cols)."""
    w, h = sheet.get_width(), sheet.get_height()
    if cell <= 0 or w % cell != 0 or h % cell != 0:
        return []
    cols = w // cell
    rows = h // cell
    grid: list[list[pygame.Surface]] = []
    for r in range(rows):
        row_frames: list[pygame.Surface] = []
        for c in range(cols):
            frame = sheet.subsurface(pygame.Rect(c * cell, r * cell, cell, cell)).copy()
            row_frames.append(frame)
        grid.append(row_frames)
    return grid


def _scale_frames(frames: list[pygame.Surface], size: int) -> list[pygame.Surface]:
    if size <= 0:
        return frames
    out: list[pygame.Surface] = []
    for f in frames:
        try:
            if f.get_width() == size and f.get_height() == size:
                out.append(f)
            else:
                out.append(pygame.transform.scale(f, (size, size)))
        except Exception:
            out.append(f)
    return out


def _pick_wave_root(wave_num: int) -> str:
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
    return os.path.join(assets_dir, "BOSSES AND ENEMIES", f"WAVE {wave_num}")


def _find_first_subdir(parent: str, predicate) -> str | None:
    try:
        for name in os.listdir(parent):
            full = os.path.join(parent, name)
            if os.path.isdir(full) and predicate(name.lower()):
                return full
    except Exception:
        return None
    return None


def _load_directional_folder(folder: str, prefer_keyword: str) -> dict[str, list[pygame.Surface]]:
    """Load direction sheets like D_Run.png / U_Run.png / S_Run.png.

    - D_ => down
    - U_ => up
    - L_ => left
    - R_ => right
    - S_ => side (used for right; left uses inverted if present or a flip)
    """
    result: dict[str, list[pygame.Surface]] = {"down": [], "up": [], "left": [], "right": []}
    if not os.path.isdir(folder):
        return result

    files = []
    try:
        for n in os.listdir(folder):
            if n.lower().endswith(".png"):
                files.append(n)
    except Exception:
        return result

    # Prefer Run/Fly depending on the folder.
    candidates = [n for n in files if prefer_keyword in n.lower()]
    if not candidates:
        candidates = files

    def load(name: str) -> pygame.Surface | None:
        try:
            return pygame.image.load(os.path.join(folder, name)).convert_alpha()
        except Exception:
            return None

    side = None
    side_inv = None

    for n in candidates:
        lower = n.lower()
        img = load(n)
        if img is None:
            continue

        # strip split
        frames = _split_strip(img)
        if not frames:
            frames = _split_vertical_strip(img)
        if not frames:
            frames = [img]

        if lower.startswith("d_"):
            result["down"] = frames
        elif lower.startswith("u_"):
            result["up"] = frames
        elif lower.startswith("l_"):
            result["left"] = frames
        elif lower.startswith("r_"):
            result["right"] = frames
        elif lower.startswith("s_"):
            if "invert" in lower:
                side_inv = frames
            else:
                side = frames

    # Side handling:
    # These asset packs commonly provide S_ as the LEFT-facing side walk.
    # If an *_inverted variant exists, treat it as the RIGHT-facing version.
    # Otherwise, derive the missing side by flipping.
    if side and side_inv:
        if not result["left"]:
            result["left"] = side
        if not result["right"]:
            result["right"] = side_inv
    elif side:
        if not result["left"]:
            result["left"] = side
        if not result["right"]:
            result["right"] = [pygame.transform.flip(f, True, False) for f in side]
    elif side_inv:
        if not result["right"]:
            result["right"] = side_inv
        if not result["left"]:
            result["left"] = [pygame.transform.flip(f, True, False) for f in side_inv]

    # Fallbacks: if some directions missing, copy from others.
    any_frames = next((v for v in result.values() if v), [])
    for k in ("down", "up", "left", "right"):
        if not result[k] and any_frames:
            result[k] = any_frames

    return result


def _load_integrated_sheet(path: str, *, layout: str = "default") -> dict[str, list[pygame.Surface]]:
    """Load a single sheet that contains multiple directions.

    Supports common grid layout: rows represent directions, cols represent frames.
    For 4+ rows: uses a direction order depending on `layout`:
    - layout="default": Down, Left, Right, Up
    - layout="boss": Down, Up, Left, Right
    - layout="fast_weak": Down, Right, Up, Left  (left animation is last row)
    Extra rows (like a 5th) are ignored.
    """
    result: dict[str, list[pygame.Surface]] = {"down": [], "up": [], "left": [], "right": []}
    try:
        sheet = pygame.image.load(path).convert_alpha()
    except Exception:
        return result

    # Try strip first (only if it actually has multiple frames)
    strip = _split_strip(sheet)
    if len(strip) > 1:
        for k in result:
            result[k] = strip
        return result

    w, h = sheet.get_width(), sheet.get_height()
    cell = _infer_grid_cell_size(w, h)
    grid = _split_grid(sheet, cell)
    if not grid:
        # final fallback: single image
        for k in result:
            result[k] = [sheet]
        return result

    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    if rows >= 4 and cols >= 2:
        if layout == "boss":
            # Boss sheets are commonly ordered: Down, Up, Left, Right.
            down = grid[0]
            up = grid[1]
            left = grid[2]
            right = grid[3]
        elif layout == "fast_weak":
            # Waves 3-5 fast-weak integrated sheets: left animation is on the LAST row.
            down = grid[0]
            right = grid[1]
            up = grid[2]
            left = grid[3]
        else:
            # Default: Down, Left, Right, Up
            down = grid[0]
            left = grid[1]
            right = grid[2]
            up = grid[3]

        result["down"] = down
        result["left"] = left
        result["right"] = right
        result["up"] = up
        return result

    # Common 3-row layout where animations are arranged vertically per direction
    # (e.g., 96x96 = 3 cols (directions) x 3 rows (frames) @ 32px).
    # Assumes column order: Down, Left, Right, (optional Up). If Up is missing,
    # fall back to Down.
    if rows == 3 and cols >= 3:
        def col_frames(col: int) -> list[pygame.Surface]:
            return [grid[r][col] for r in range(rows)]

        # 3-row sheets (e.g., 96x96 at 32px) can be arranged with directions in columns.
        # Default is: Down, Left, Right, (optional Up).
        result["down"] = col_frames(0)
        result["left"] = col_frames(1)
        result["right"] = col_frames(2)
        result["up"] = col_frames(3) if cols >= 4 else result["down"]
        return result

    # If it's not a 4-row grid, treat the first row as a looping anim.
    loop = [f for f in grid[0] if f is not None] if rows else [sheet]
    for k in result:
        result[k] = loop
    return result


def _load_enemy_frames(wave_num: int, enemy_type: str) -> dict[str, list[pygame.Surface]]:
    """Load frames for (wave_num, enemy_type) from assets/BOSSES AND ENEMIES."""
    root = _pick_wave_root(wave_num)
    enemy_type = enemy_type.lower()

    if not os.path.isdir(root):
        return {"down": [], "up": [], "left": [], "right": []}

    # Boss is stored as a png in the wave folder.
    if enemy_type == "boss":
        preferred = os.path.join(root, f"boss wave {wave_num}.png")
        if os.path.exists(preferred):
            return _load_integrated_sheet(preferred, layout="boss")
        # Fallback: any boss*.png in that wave.
        try:
            for n in os.listdir(root):
                if n.lower().startswith("boss") and n.lower().endswith(".png"):
                    return _load_integrated_sheet(os.path.join(root, n), layout="boss")
        except Exception:
            pass
        return {"down": [], "up": [], "left": [], "right": []}

    # Standard (wave 1): folder like "STANDARD rat" with D_Run/S_Run/U_Run.
    if enemy_type == "standard":
        folder = _find_first_subdir(root, lambda s: "standard" in s)
        if folder:
            return _load_directional_folder(folder, prefer_keyword="run")
        return {"down": [], "up": [], "left": [], "right": []}

    # Fast weak: wave 2 uses a directional folder; waves 3-5 provide a combined sheet.
    if enemy_type == "fast_weak":
        folder = _find_first_subdir(root, lambda s: "fast" in s and "weak" in s)
        if folder:
            return _load_directional_folder(folder, prefer_keyword="run")
        # Try wave-root file "fast weak.png"
        combined = os.path.join(root, "fast weak.png")
        if os.path.exists(combined):
            return _load_integrated_sheet(combined, layout="fast_weak")
        return {"down": [], "up": [], "left": [], "right": []}

    # Slow strong: wave 2-4 horse soldier; wave 5 flying wizard with Fly.
    if enemy_type == "slow_strong":
        folder = _find_first_subdir(root, lambda s: "slow" in s and "strong" in s)
        if folder:
            # Prefer Fly if present, else Run.
            prefer = "fly" if any("fly" in n.lower() for n in os.listdir(folder) if n.lower().endswith(".png")) else "run"
            return _load_directional_folder(folder, prefer_keyword=prefer)
        return {"down": [], "up": [], "left": [], "right": []}

    return {"down": [], "up": [], "left": [], "right": []}

class Enemy:
    def __init__(self, path_points, health, speed, reward, color_grade=0, enemy_type="standard", wave_num: int | None = None):
        self.path = path_points
        # Index of the current path point we have reached. Next target is path_index + 1.
        self.path_index = 0
        self.enemy_type = enemy_type  # "standard", "fast_weak", "slow_strong", or "boss"
        self.wave_num = int(wave_num) if wave_num is not None else 1

        # Animation state
        self.direction = "down"  # up/down/left/right
        self._anim_timer = 0.0
        self._anim_frame = 0
        self._anim_speed = 0.12

        # Continuous position (pixels, at path centers)
        start_x, start_y = self.path[0]
        self.pos_x = float(start_x)
        self.pos_y = float(start_y)

        # Tile position (integers) kept for other systems (e.g., coin drops)
        self.tile_x = int(self.pos_x // TILE_SIZE)
        self.tile_y = int(self.pos_y // TILE_SIZE)

        # Movement speed in tiles/second; keep the existing "3x faster" tuning.
        self.speed = float(speed) * 3.0
        self.base_speed = self.speed

        self.health = health
        self.max_health = health
        self.reward = reward
        self.finished = False
        self.dead_handled = False
        self.killed_by_tower = False
        self.slow_timer = 0
        self.stun_timer = 0
        self.has_been_stunned = False

        # Set color and size based on enemy type
        if enemy_type == "fast_weak":
            # Fast weak enemies: yellow/lime color (small circles)
            self.color = (200, 255, 0)  # Yellow-green
            self.radius = TILE_SIZE // 5  # Smaller
        elif enemy_type == "slow_strong":
            # Slow strong enemies: purple/magenta color (larger squares)
            self.color = (200, 50, 200)  # Purple
            self.radius = TILE_SIZE // 2  # Much larger
        elif enemy_type == "boss":
            # Boss enemies: golden/orange color (very large)
            self.color = (255, 165, 0)  # Orange-gold
            self.radius = TILE_SIZE  # Very large (2x TILE_SIZE diameter)
        else:
            # Standard enemies: red
            self.color = (
                max(50, RED[0] - color_grade * 30),
                RED[1],
                RED[2]
            )
            self.radius = TILE_SIZE // 3
        

        # Rect for collisions
        size = self.radius * 2
        self.rect = pygame.Rect(
            int(self.pos_x) - self.radius,
            int(self.pos_y) - self.radius,
            size,
            size
        )

        # Load animation frames for this wave/type (cached)
        key = (self.wave_num, self.enemy_type.lower())
        if key not in _ANIM_CACHE:
            _ANIM_CACHE[key] = _load_enemy_frames(self.wave_num, self.enemy_type)
        # IMPORTANT: don't mutate the global cache with per-enemy scaling.
        raw = _ANIM_CACHE[key]
        self._frames_by_dir = {
            "down": list(raw.get("down", [])),
            "up": list(raw.get("up", [])),
            "left": list(raw.get("left", [])),
            "right": list(raw.get("right", [])),
        }

        # Pre-scale frames to an appropriate draw size for this enemy.
        # User request: rats + horse soldiers should be ~4x bigger.
        if self.enemy_type == "fast_weak":
            # Make fast-weak clearly smaller than the others.
            self._sprite_draw_size = int(TILE_SIZE * 2)
        elif self.enemy_type in ("standard", "slow_strong"):
            self._sprite_draw_size = int(TILE_SIZE * 4)
        else:
            self._sprite_draw_size = max(TILE_SIZE, int(self.radius * 3.0))
        for d in ("down", "up", "left", "right"):
            if self._frames_by_dir.get(d):
                self._frames_by_dir[d] = _scale_frames(self._frames_by_dir[d], self._sprite_draw_size)

    def update(self, dt):
        if self.finished or self.path_index >= len(self.path) - 1:
            self.finished = True
            return

        # Update stun timer
        if self.stun_timer > 0:
            self.stun_timer -= dt
            # Don't move while stunned
            self.rect.center = (int(self.pos_x), int(self.pos_y))
            return

        # Update slow timer
        if self.slow_timer > 0:
            self.slow_timer -= dt
            self.speed = self.base_speed * 0.6
        else:
            self.speed = self.base_speed

        # Smooth continuous movement along the path.
        # Convert tiles/sec -> pixels/sec.
        pixels_per_sec = max(0.0, self.speed) * TILE_SIZE
        remaining = pixels_per_sec * max(0.0, dt)

        while remaining > 0.0 and self.path_index < len(self.path) - 1:
            tx, ty = self.path[self.path_index + 1]
            dx = float(tx) - self.pos_x
            dy = float(ty) - self.pos_y
            dist = math.hypot(dx, dy)

            # Update direction based on where we're heading.
            if abs(dx) > abs(dy):
                self.direction = "right" if dx > 0 else "left"
            elif abs(dy) > 0:
                self.direction = "down" if dy > 0 else "up"

            if dist <= 1e-6:
                self.path_index += 1
                continue

            if dist <= remaining:
                self.pos_x = float(tx)
                self.pos_y = float(ty)
                self.path_index += 1
                remaining -= dist
            else:
                step = remaining / dist
                self.pos_x += dx * step
                self.pos_y += dy * step
                remaining = 0.0

        # Update rect and tile coords
        self.rect.center = (int(self.pos_x), int(self.pos_y))
        self.tile_x = int(self.pos_x // TILE_SIZE)
        self.tile_y = int(self.pos_y // TILE_SIZE)

        # Update animation
        self._anim_timer += dt
        # Slightly speed up animation for faster enemies
        speed_factor = max(0.6, min(2.0, self.speed / 3.0))
        frame_time = max(0.06, self._anim_speed / speed_factor)
        frames = self._frames_by_dir.get(self.direction, []) if hasattr(self, "_frames_by_dir") else []
        if frames and self._anim_timer >= frame_time:
            self._anim_timer = 0.0
            self._anim_frame = (self._anim_frame + 1) % len(frames)

        if self.health <= 0:
            self.finished = True

    def draw(self, surface, offset: tuple[int, int] = (0, 0)):
        ox, oy = offset
        rect = self.rect.move(ox, oy)
        drew_sprite = False
        frames = self._frames_by_dir.get(self.direction, []) if hasattr(self, "_frames_by_dir") else []
        if frames:
            frame = frames[self._anim_frame % len(frames)]
            if frame is not None:
                dst = frame.get_rect(center=rect.center)
                surface.blit(frame, dst)
                drew_sprite = True

        # Fallback to old shapes if sprite assets are missing.
        if not drew_sprite:
            if self.enemy_type == "fast_weak":
                pygame.draw.circle(surface, self.color, rect.center, self.radius)
            elif self.enemy_type == "slow_strong":
                size = self.radius * 2
                r2 = pygame.Rect(rect.centerx - self.radius, rect.centery - self.radius, size, size)
                pygame.draw.rect(surface, self.color, r2)
            elif self.enemy_type == "boss":
                size = self.radius * 2
                r2 = pygame.Rect(rect.centerx - self.radius, rect.centery - self.radius, size, size)
                pygame.draw.rect(surface, self.color, r2)
                pygame.draw.rect(surface, (255, 255, 0), r2, 3)
            else:
                pygame.draw.circle(surface, self.color, rect.center, self.radius)

        # Health bar
        bar_width = 30
        if self.enemy_type == "boss":
            bar_width = 60  # Larger health bar for boss
        
        bar_height = 5
        x = rect.centerx - bar_width // 2
        y = rect.top - 10

        pygame.draw.rect(surface, BLACK, (x, y, bar_width, bar_height))

        if self.max_health > 0:
            health_ratio = self.health / self.max_health
            pygame.draw.rect(
                surface,
                GREEN,
                (x, y, bar_width * health_ratio, bar_height)
            )

        # Draw stun indicator (stars above enemy)
        if self.stun_timer > 0:
            star_size = 6
            star_y = rect.top - 20
            # Draw stars indicating stun
            for i in range(2):
                star_x = rect.centerx - 10 + i * 20
                pygame.draw.circle(surface, (255, 255, 100), (star_x, star_y), star_size)
                pygame.draw.circle(surface, (255, 255, 255), (star_x, star_y), star_size - 2)
