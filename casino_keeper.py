import pygame
import math

class CasinoKeeper:
    def __init__(self, tile_pos, tile_size):
        self.tile_x, self.tile_y = tile_pos
        self.width = tile_size
        self.height = tile_size
        
        # Calculate pixel position based on tile (centered)
        self.x = self.tile_x * tile_size
        self.y = self.tile_y * tile_size
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.interaction_range = 80
        
        # Visuals (Purple square with 'C' for Casino)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((200, 50, 200))  # Purple
        font = pygame.font.SysFont('Arial', 20, bold=True)
        text = font.render("C", True, (255, 255, 255))
        self.image.blit(text, (10, 5))

    def is_player_close(self, player):
        # Distance formula
        px, py = player.rect.center
        sx, sy = self.rect.center
        dist = math.hypot(px - sx, py - sy)
        return dist <= self.interaction_range

    def draw(self, screen, player):
        # Draw Casino Keeper
        screen.blit(self.image, (self.x, self.y))
        
        # Draw interaction prompt
        if self.is_player_close(player):
            font = pygame.font.SysFont('Arial', 16)
            msg = font.render("Press E", True, (255, 255, 255))
            # Draw above head
            bg_rect = pygame.Rect(self.rect.centerx - 25, self.rect.top - 25, 50, 20)
            pygame.draw.rect(screen, (50, 50, 50), bg_rect)
            screen.blit(msg, (bg_rect.x + 5, bg_rect.y))
