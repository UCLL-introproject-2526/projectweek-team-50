import pygame
from settings import *

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tile Level Editor")

clock = pygame.time.Clock()

# Grid data
tiles = [
    [TILE_GRASS for _ in range(TILES_X)]
    for _ in range(TILES_Y)
]

current_tile = TILE_WALL  # default brush
mouse_held = False  # Track if mouse button is held

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                current_tile = TILE_GRASS
            elif event.key == pygame.K_2:
                current_tile = TILE_WALL
            elif event.key == pygame.K_3:
                current_tile = TILE_PATH

            elif event.key == pygame.K_s:
                # SAVE TO TEXT FILE
                with open("level.txt", "w") as f:
                    f.write("level = [\n")
                    for row in tiles:
                        f.write(f"    {row},\n")
                    f.write("]\n")

                print("Level saved to level.txt")

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

    # Also draw on initial click
    if mouse_held:
        mx, my = pygame.mouse.get_pos()
        tx = mx // TILE_SIZE
        ty = my // TILE_SIZE

        if 0 <= tx < TILES_X and 0 <= ty < TILES_Y:
            tiles[ty][tx] = current_tile

    # DRAW
    screen.fill((0, 0, 0))

    for y in range(TILES_Y):
        for x in range(TILES_X):
            pygame.draw.rect(
                screen,
                TILE_COLORS[tiles[y][x]],
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
