import pygame
from settings import TILE_SIZE, RED, GREEN, BLACK

class Enemy:
    def __init__(self, path_points, health, speed, reward, color_grade=0, enemy_type="standard"):
        self.path = path_points
        self.path_index = 0
        self.enemy_type = enemy_type  # "standard", "fast_weak", or "slow_strong"

        # Tile position (integers)
        self.tile_x = self.path[0][0] // TILE_SIZE
        self.tile_y = self.path[0][1] // TILE_SIZE

        # Movement speed: make enemies three times faster than the base `speed`
        # and convert tiles-per-second to seconds-per-tile
        self.speed = speed * 3
        if self.speed <= 0:
            self.move_delay = 0.7
        else:
            self.move_delay = 1.0 / self.speed
        self.timer = 0.0

        self.health = health
        self.max_health = health
        self.reward = reward
        self.finished = False
        self.dead_handled = False
        self.killed_by_tower = False  # Track if killed by tower (for coin drops)

        # Set color and size based on enemy type
        if enemy_type == "fast_weak":
            # Fast weak enemies: yellow/lime color (small circles)
            self.color = (200, 255, 0)  # Yellow-green
            self.radius = TILE_SIZE // 5  # Smaller
        elif enemy_type == "slow_strong":
            # Slow strong enemies: purple/magenta color (larger squares)
            self.color = (200, 50, 200)  # Purple
            self.radius = TILE_SIZE // 2  # Much larger
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
            self.tile_x * TILE_SIZE + TILE_SIZE//2 - self.radius,
            self.tile_y * TILE_SIZE + TILE_SIZE//2 - self.radius,
            size,
            size
        )

        # Lerp positions (pixels)
        self.lerp_x = self.rect.centerx
        self.lerp_y = self.rect.centery

        # Lerp speed factor (0 < factor <= 1)
        self.lerp_factor = 0.4  # very fast lerp; increase for faster, decrease for smoother

    def update(self, dt):
        if self.finished or self.path_index >= len(self.path) - 1:
            self.finished = True
            return

        self.timer += dt
        if self.timer >= self.move_delay:
            # Move to next path tile
            self.path_index += 1
            target_px, target_py = self.path[self.path_index]
            self.tile_x = target_px // TILE_SIZE
            self.tile_y = target_py // TILE_SIZE

            # Reset timer
            self.timer = 0.0

        # Fast lerp toward tile center
        self._lerp_to_tile()

        # Update rect
        self.rect.center = (int(self.lerp_x), int(self.lerp_y))

        if self.health <= 0:
            self.finished = True

    def _lerp_to_tile(self):
        """Very fast lerp toward current tile center."""
        target_center_x = self.tile_x * TILE_SIZE + TILE_SIZE // 2
        target_center_y = self.tile_y * TILE_SIZE + TILE_SIZE // 2

        self.lerp_x += (target_center_x - self.lerp_x) * self.lerp_factor
        self.lerp_y += (target_center_y - self.lerp_y) * self.lerp_factor

    def draw(self, surface):
        if self.enemy_type == "fast_weak":
            # Draw as small circle (yellow-green)
            pygame.draw.circle(
                surface,
                self.color,
                self.rect.center,
                self.radius
            )
        elif self.enemy_type == "slow_strong":
            # Draw as large square (purple)
            size = self.radius * 2
            rect = pygame.Rect(
                self.rect.centerx - self.radius,
                self.rect.centery - self.radius,
                size,
                size
            )
            pygame.draw.rect(
                surface,
                self.color,
                rect
            )
        else:
            # Standard: red circle
            pygame.draw.circle(
                surface,
                self.color,
                self.rect.center,
                self.radius
            )

        # Health bar
        bar_width = 30
        bar_height = 5
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 10

        pygame.draw.rect(surface, BLACK, (x, y, bar_width, bar_height))

        if self.max_health > 0:
            health_ratio = self.health / self.max_health
            pygame.draw.rect(
                surface,
                GREEN,
                (x, y, bar_width * health_ratio, bar_height)
            )
