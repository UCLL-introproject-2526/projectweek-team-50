import pygame
from settings import WHITE
from entities.entity import Entity

class Player(Entity):
    def __init__(self, tile_pos):
        super().__init__(tile_pos)

        self.move_delay = 0.15
        self.timer = 0.0
        self.gold = 0

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
                if not tilemap.is_blocked(nx, ny):
                    self.set_tile(nx, ny)
                    # Collect coins after moving
                    collected = coin_manager.collect_at_tile(self.tile_x, self.tile_y)
                    if collected:
                        self.gold += collected
            self.timer = 0.0

        super().update(dt)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)
