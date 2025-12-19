# ===============================
# Window (LOGICAL resolution)
# ===============================
SCREEN_WIDTH = 1536
SCREEN_HEIGHT = 960


TITLE = "No Way Through"

# ===============================
# Timing
# ===============================
FPS = 60

# ===============================
# Pixel Art Font
# ===============================
import pygame
import os

# Path to the pixel art font
PIXEL_FONT_PATH = os.path.join(os.path.dirname(__file__), "assets", "pixel_font.ttf")

def get_pixel_font(size, bold=False):
    """
    Get a pixel art font with the specified size.
    Note: TTF fonts don't support bold parameter, so it's ignored.
    """
    try:
        return pygame.font.Font(PIXEL_FONT_PATH, size)
    except:
        # Fallback to system font if pixel font is not found
        return pygame.font.Font(None, size)

# ===============================
# Colors (ALL COMMON COLORS)
# ===============================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)

BG_COLOR = (30, 30, 30)
GRID_COLOR = (60, 60, 60)
WALL_COLOR = (80, 80, 80)

# ===============================
# Shop / UI Colors
# ===============================
UI_BG_COLOR = (45, 45, 55)
BUTTON_COLOR = (70, 70, 80)
BUTTON_HOVER_COLOR = (100, 100, 110)
BUTTON_SELECTED_COLOR = (100, 200, 100)
TEXT_COLOR = (240, 240, 240)

# ===============================
# Tiles
# ===============================
TILE_SIZE = 32
TILES_X = SCREEN_WIDTH // TILE_SIZE
TILES_Y = SCREEN_HEIGHT // TILE_SIZE

# ===============================
# Player
# ===============================
# Visual-only sprite draw scale (collision remains TILE_SIZE).
# Previously 1.5; make avatar 20% bigger.
PLAYER_SPRITE_SCALE = 1.8

# Grid visibility (can be toggled with G key in game)
SHOW_GRID = True

# Tile IDs
TILE_GRASS = 0
TILE_WALL = 1
TILE_PATH = 2
TILE_CASTLE = 3
TILE_START = 4
TILE_FINISH = 5
TILE_SHOP = 6
TILE_CASINO = 7

# Tile colors
TILE_COLORS = {
    TILE_GRASS: (40, 120, 40),
    TILE_WALL:  (80, 80, 80),
    TILE_PATH:  (150, 120, 60),
    TILE_CASTLE: (100, 100, 100),  # Grey castle
    # In the game, render start/finish as normal path tiles
    TILE_START: (150, 120, 60),
    TILE_FINISH: (150, 120, 60),
    TILE_SHOP: (40, 120, 40),  # Grass in game
    TILE_CASINO: (40, 120, 40),  # Grass in game
}

# ===============================
# Troop Stats
# ===============================
TROOP_DATA = {
    # Definitive tower roster (ordered by strength):
    "goblin": {
        "cost": 60,
        "range": 55,
        "damage": 18,
        "delay": 0.50,
        "color": (40, 170, 60),
    },
    "elf": {
        "cost": 90,
        "range": 65,
        "damage": 26,
        "delay": 0.55,
        "color": (120, 220, 120),
    },
    "knight": {
        "cost": 130,
        "range": 80,
        "damage": 40,
        "delay": 0.85,
        "color": (255, 0, 0),
        "stun_duration": 0.4,
    },
    "archer": {
        "cost": 170,
        "range": 180,
        "damage": 32,
        "delay": 0.65,
        "color": (0, 200, 0),
    },
    "wizard": {
        "cost": 260,
        "range": 260,
        "damage": 42,
        "delay": 0.80,
        "color": (0, 120, 255),
        "slow_duration": 0.5,
    },
    "firewarrior": {
        "cost": 350,
        "range": 110,
        "damage": 60,
        "delay": 0.75,
        "color": (220, 80, 40),
    },
    "bloodmage": {
        "cost": 500,
        "range": 340,
        "damage": 85,
        "delay": 0.90,
        "color": (150, 40, 200),
        "projectile_speed": 5.5,
    },
}
