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
# Colors (ALL COMMON COLORS)
# ===============================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)

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

# Tile IDs
TILE_GRASS = 0
TILE_WALL = 1
TILE_PATH = 2

# Tile colors
TILE_COLORS = {
    TILE_GRASS: (40, 120, 40),
    TILE_WALL:  (80, 80, 80),
    TILE_PATH:  (150, 120, 60),
}

# ===============================
# Troop Stats
# ===============================
TROOP_DATA = {
    "jester": {
        "cost": 50,
        "range": 50,
        "damage": 15,
        "delay": 0.4,
        "color": (200, 50, 200),
    },
    "knight": {
        "cost": 100,
        "range": 60,
        "damage": 40,
        "delay": 1.2,
        "color": (160, 160, 170),
    },
    "archer": {
        "cost": 150,
        "range": 200,
        "damage": 20,
        "delay": 0.8,
        "color": (34, 139, 34),
    },
    "wizard": {
        "cost": 300,
        "range": 180,
        "damage": 60,
        "delay": 1.5,
        "color": (50, 50, 250),
    },
    "cannon": {
        "cost": 500,
        "range": 350,
        "damage": 120,
        "delay": 3.0,
        "color": (20, 20, 20),
    },
}
