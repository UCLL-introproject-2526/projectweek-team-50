# Window
SCREEN_WIDTH = 1536
MAP_HEIGHT = 960         # The height of the gameplay area (30 tiles)
UI_HEIGHT = 120          # Extra space at the bottom for the shop
SCREEN_HEIGHT = MAP_HEIGHT + UI_HEIGHT
TITLE = "Team 50 - Tower Defense Shop"

# Timing
FPS = 60

# Colors
BG_COLOR = (30, 30, 30)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (220, 60, 60)
GREEN = (60, 200, 60)
BLUE  = (60, 120, 220)
YELLOW = (240, 220, 70)
GRID_COLOR = (60, 60, 60)
WALL_COLOR = (80, 80, 80)

# Shop Colors
UI_BG_COLOR = (45, 45, 55)
BUTTON_COLOR = (70, 70, 80)
BUTTON_HOVER_COLOR = (100, 100, 110)
BUTTON_SELECTED_COLOR = (100, 200, 100)
TEXT_COLOR = (240, 240, 240)

# Tiles
TILE_SIZE = 32
TILES_X = SCREEN_WIDTH // TILE_SIZE
TILES_Y = MAP_HEIGHT // TILE_SIZE  # Use MAP_HEIGHT so the grid doesn't overlap UI

# Tile IDs
TILE_GRASS = 0
TILE_WALL = 1
TILE_PATH = 2

TILE_COLORS = {
    TILE_GRASS: (40, 120, 40),   # green
    TILE_WALL:  (80, 80, 80),    # gray
    TILE_PATH:  (150, 120, 60),  # brown
}

# Troop Stats & Costs
# Format: Cost, Range (pixels), Damage, Fire Delay (seconds), Color
TROOP_DATA = {
    "jester": {
        "cost": 50,
        "range": 50,
        "damage": 15,
        "delay": 0.4,
        "color": (200, 50, 200) # Purple
    },
    "knight": {
        "cost": 100,
        "range": 60,
        "damage": 40,
        "delay": 1.2,
        "color": (160, 160, 170) # Steel
    },
    "archer": {
        "cost": 150,
        "range": 200,
        "damage": 20,
        "delay": 0.8,
        "color": (34, 139, 34)   # Forest Green
    },
    "wizard": {
        "cost": 300,
        "range": 180,
        "damage": 60,
        "delay": 1.5,
        "color": (50, 50, 250)   # Blue Magic
    },
    "cannon": {
        "cost": 500,
        "range": 350,
        "damage": 120,
        "delay": 3.0,
        "color": (20, 20, 20)    # Black
    }
}