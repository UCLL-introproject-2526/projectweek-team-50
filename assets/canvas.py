import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Get parent directory and import settings
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.insert(0, parent_dir)
from settings import get_pixel_font

# Constants
TILE_SIZE_SMALL = 32
GRID_SMALL = 8
SMALL_BOX_SIZE = TILE_SIZE_SMALL * GRID_SMALL  # 256

TILE_SIZE_LARGE = 32
GRID_LARGE = 32
LARGE_CANVAS_SIZE = TILE_SIZE_LARGE * GRID_LARGE  # 1024

WINDOW_WIDTH = SMALL_BOX_SIZE + LARGE_CANVAS_SIZE + 10  # 10px gap
WINDOW_HEIGHT = max(SMALL_BOX_SIZE, LARGE_CANVAS_SIZE)

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Setup window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tile Painter")

# Load image (256x256)
image = pygame.image.load("projectweek-team-50/assets/FieldsTileset.png").convert_alpha()

# Selected tile
selected_tile = None

# Large canvas surface
canvas_surface = pygame.Surface((LARGE_CANVAS_SIZE, LARGE_CANVAS_SIZE))
canvas_surface.fill(WHITE)

# Flags
grid_visible = True
painting = False
zoom_level = 1.0  # 1.0 = 100%

# Font
font = get_pixel_font(24)

# Buttons
def draw_button(rect, text, active=True):
    color = BLUE if active else GRAY
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, WHITE, rect, 2)
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

# Button rects
grid_button_rect = pygame.Rect(10, SMALL_BOX_SIZE + 20, 100, 30)
zoom_in_button_rect = pygame.Rect(120, SMALL_BOX_SIZE + 20, 50, 30)
zoom_out_button_rect = pygame.Rect(180, SMALL_BOX_SIZE + 20, 50, 30)

clock = pygame.time.Clock()

# Main loop
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            # Check buttons
            if grid_button_rect.collidepoint(event.pos):
                grid_visible = not grid_visible
            elif zoom_in_button_rect.collidepoint(event.pos):
                zoom_level = min(4.0, zoom_level + 0.5)
            elif zoom_out_button_rect.collidepoint(event.pos):
                zoom_level = max(0.5, zoom_level - 0.5)

            # Check small tile box
            elif x < SMALL_BOX_SIZE and y < SMALL_BOX_SIZE:
                col = x // TILE_SIZE_SMALL
                row = y // TILE_SIZE_SMALL
                tile_rect = pygame.Rect(col * TILE_SIZE_SMALL, row * TILE_SIZE_SMALL, TILE_SIZE_SMALL, TILE_SIZE_SMALL)
                selected_tile = image.subsurface(tile_rect).copy()

            # Check canvas
            elif x > SMALL_BOX_SIZE + 10:
                painting = True

        elif event.type == pygame.MOUSEBUTTONUP:
            painting = False

    # Drag-to-paint
    if painting and selected_tile:
        x, y = mouse_pos
        if x > SMALL_BOX_SIZE + 10:
            canvas_x = x - (SMALL_BOX_SIZE + 10)
            canvas_y = y
            col = int(canvas_x // (TILE_SIZE_LARGE * zoom_level))
            row = int(canvas_y // (TILE_SIZE_LARGE * zoom_level))
            if 0 <= col < GRID_LARGE and 0 <= row < GRID_LARGE:
                canvas_surface.blit(selected_tile, (col * TILE_SIZE_LARGE, row * TILE_SIZE_LARGE))

    # Draw small tile box
    screen.fill(GRAY, (0, 0, SMALL_BOX_SIZE, SMALL_BOX_SIZE))
    for row in range(GRID_SMALL):
        for col in range(GRID_SMALL):
            tile_rect = pygame.Rect(col * TILE_SIZE_SMALL, row * TILE_SIZE_SMALL, TILE_SIZE_SMALL, TILE_SIZE_SMALL)
            tile_surface = image.subsurface(tile_rect)
            screen.blit(tile_surface, tile_rect.topleft)
            pygame.draw.rect(screen, WHITE, tile_rect, 1)

    # Highlight selected tile
    if selected_tile:
        pygame.draw.rect(screen, RED, (mouse_pos[0] // TILE_SIZE_SMALL * TILE_SIZE_SMALL,
                                       mouse_pos[1] // TILE_SIZE_SMALL * TILE_SIZE_SMALL,
                                       TILE_SIZE_SMALL, TILE_SIZE_SMALL), 3)

    # Draw canvas with zoom
    zoomed_canvas = pygame.transform.scale(canvas_surface, (int(LARGE_CANVAS_SIZE * zoom_level),
                                                            int(LARGE_CANVAS_SIZE * zoom_level)))
    screen.fill(WHITE, (SMALL_BOX_SIZE + 10, 0, int(LARGE_CANVAS_SIZE * zoom_level), int(LARGE_CANVAS_SIZE * zoom_level)))
    screen.blit(zoomed_canvas, (SMALL_BOX_SIZE + 10, 0))

    # Draw grid on canvas
    if grid_visible:
        for i in range(GRID_LARGE + 1):
            pygame.draw.line(screen, GRAY,
                             (SMALL_BOX_SIZE + 10, i * TILE_SIZE_LARGE * zoom_level),
                             (SMALL_BOX_SIZE + 10 + LARGE_CANVAS_SIZE * zoom_level, i * TILE_SIZE_LARGE * zoom_level))
            pygame.draw.line(screen, GRAY,
                             (SMALL_BOX_SIZE + 10 + i * TILE_SIZE_LARGE * zoom_level, 0),
                             (SMALL_BOX_SIZE + 10 + i * TILE_SIZE_LARGE * zoom_level, LARGE_CANVAS_SIZE * zoom_level))

    # Draw buttons
    draw_button(grid_button_rect, "Grid On" if grid_visible else "Grid Off")
    draw_button(zoom_in_button_rect, "+")
    draw_button(zoom_out_button_rect, "-")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
