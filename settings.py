# ===============================
# Window (LOGICAL resolution)
# ===============================
SCREEN_WIDTH = 1536
SCREEN_HEIGHT = 960


TITLE = "Team 50 - Tower Defense Shop"

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
    "jester": {
        "cost": 120,
        "range": 55,
        "damage": 30,
        "delay": 1.0,
        "color": (200, 50, 200),
        "stun_duration": 1.0,
    },
    "knight": {
        "cost": 100,
        "range": 60,
        "damage": 40,
        "delay": 1.5,
        "color": (160, 160, 170),
    },
    "archer": {
        "cost": 150,
        "range": 200,
        "damage": 25,
        "delay": 0.8,
        "color": (34, 139, 34),
    },
    "wizard": {
        "cost": 300,
        "range": 180,
        "damage": 65,
        "delay": 1.5,
        "color": (50, 50, 250),
        "slow_duration": 0.5,
    },
    "cannon": {
        "cost": 400,
        "range": 300,
        "damage": 80,
        "delay": 3.5,
        "color": (60, 60, 60),
        "projectile_speed": 8.0,
    },
    "musketeer": {
        "cost": 250,
        "range": 288,
        "damage": 18,
        "delay": 0.7,
        "color": (218, 165, 32),
    },
}
