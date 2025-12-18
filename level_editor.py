import pygame
import os
from settings import *
from level_io import load_level_from_txt, save_level_to_txt

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tile Level Editor")

clock = pygame.time.Clock()

# Tile previews
tileset_dir = os.path.join(os.path.dirname(__file__), "assets", "tiles")
try:
    TILE_IMG_GRASS = pygame.image.load(os.path.join(tileset_dir, "grass.png")).convert_alpha()
    TILE_IMG_PATH = pygame.image.load(os.path.join(tileset_dir, "PATH MAIN.png")).convert_alpha()
except Exception:
    TILE_IMG_GRASS = None
    TILE_IMG_PATH = None

# Grid data
base_dir = os.path.dirname(__file__)
level_path = os.path.join(base_dir, "level.txt")

default_tiles = [
    [TILE_GRASS for _ in range(TILES_X)]
    for _ in range(TILES_Y)
]

tiles = load_level_from_txt(
    level_path,
    fallback=default_tiles,
    expected_width=TILES_X,
    expected_height=TILES_Y,
)

current_tile = TILE_WALL  # default brush
mouse_held = False  # Track if mouse button is held
dirty = False  # Track unsaved changes


def save_level() -> None:
    save_level_to_txt(level_path, tiles)
    print(f"Level saved to {level_path}")

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if dirty:
                save_level()
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                current_tile = TILE_GRASS
            elif event.key == pygame.K_2:
                current_tile = TILE_WALL
            elif event.key == pygame.K_3:
                current_tile = TILE_PATH
            elif event.key == pygame.K_4:
                current_tile = TILE_START
            elif event.key == pygame.K_5:
                current_tile = TILE_FINISH
            elif event.key == pygame.K_6:
                current_tile = TILE_SHOP
            elif event.key == pygame.K_7:
                current_tile = TILE_CASINO

            elif event.key == pygame.K_s:
                save_level()
                dirty = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_held = True  # Start drawing
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_held = False  # Stop drawing

        elif event.type == pygame.MOUSEMOTION:
            if mouse_held:  # Only draw when holding the mouse
                mx, my = pygame.mouse.get_pos()
                tx = mx // TILE_SIZE
                ty = my // TILE_SIZE

                if 0 <= tx < TILES_X and 0 <= ty < TILES_Y:
                    tiles[ty][tx] = current_tile
                    dirty = True

    # Also draw on initial click
    if mouse_held:
        mx, my = pygame.mouse.get_pos()
        tx = mx // TILE_SIZE
        ty = my // TILE_SIZE

        if 0 <= tx < TILES_X and 0 <= ty < TILES_Y:
            tiles[ty][tx] = current_tile
            dirty = True

    # DRAW
    screen.fill((0, 0, 0))

    for y in range(TILES_Y):
        for x in range(TILES_X):
            tid = tiles[y][x]
            # In the editor, show START/FINISH with distinct colors
            if tid == TILE_START:
                color = (0, 255, 255)  # cyan for spawn
                pygame.draw.rect(
                    screen,
                    color,
                    (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                )
            elif tid == TILE_FINISH:
                color = (255, 60, 60)  # red for finish/castle
                pygame.draw.rect(
                    screen,
                    color,
                    (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                )
            elif tid == TILE_SHOP:
                color = (255, 165, 0)  # orange for shop
                pygame.draw.rect(
                    screen,
                    color,
                    (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                )
            elif tid == TILE_CASINO:
                color = (200, 50, 255)  # purple for casino
                pygame.draw.rect(
                    screen,
                    color,
                    (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                )
            else:
                if tid == TILE_GRASS and TILE_IMG_GRASS is not None:
                    screen.blit(TILE_IMG_GRASS, (x * TILE_SIZE, y * TILE_SIZE))
                elif tid == TILE_PATH and TILE_IMG_PATH is not None:
                    screen.blit(TILE_IMG_PATH, (x * TILE_SIZE, y * TILE_SIZE))
                else:
                    color = TILE_COLORS[tid]
                    pygame.draw.rect(
                        screen,
                        color,
                        (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    )

    # Grid
    for x in range(TILES_X + 1):
        pygame.draw.line(screen, (60, 60, 60),
                         (x * TILE_SIZE, 0),
                         (x * TILE_SIZE, SCREEN_HEIGHT), 1)

    for y in range(TILES_Y + 1):
        pygame.draw.line(screen, (60, 60, 60),
                         (0, y * TILE_SIZE),
                         (SCREEN_WIDTH, y * TILE_SIZE), 1)

    pygame.display.flip()

pygame.quit()
