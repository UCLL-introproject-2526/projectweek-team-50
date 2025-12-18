import pygame
from settings import WHITE, TILES_X, TILES_Y, TILE_SIZE, get_pixel_font
from entities.entity import Entity
from inventory import Inventory

class Player(Entity):
    def __init__(self, tile_pos):
        super().__init__(tile_pos)

        self.move_delay = 0.10  # Faster movement
        self.timer = 0.0
        self.gold = 0
        self.inventory = Inventory()
        self.selected_tower = None
        
        # Player health system
        self.health = 100
        self.max_health = 100
        self.damage_cooldown = 0.0
        self.radius = TILE_SIZE // 2  # Collision radius

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
        elif keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1

        return dx, dy

    def update(self, dt, tilemap, coin_manager, game):
        self.timer += dt
        if self.timer >= self.move_delay:
            dx, dy = self.handle_input()
            if dx or dy:
                nx = self.tile_x + dx
                ny = self.tile_y + dy
                
                # Check boundaries and blocked tiles
                if 0 <= nx < TILES_X and 0 <= ny < TILES_Y and not tilemap.is_blocked(nx, ny):
                    self.set_tile(nx, ny)
                    # Collect coins after moving (within 1 tile)
                    collected = coin_manager.collect_nearby(self.tile_x, self.tile_y, radius=1)
                    if collected:
                        self.gold += collected
            self.timer = 0.0

        super().update(dt)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)
        
        # Draw happy ASCII face
        font = get_pixel_font(16)
        face = font.render(":)", True, (0, 0, 0))  # Black on white
        face_rect = face.get_rect(center=self.rect.center)
        surface.blit(face, face_rect)
