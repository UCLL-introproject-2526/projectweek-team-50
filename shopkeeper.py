import pygame
import math
import os
from settings import get_pixel_font

class Shopkeeper:
    def __init__(self, tile_pos, tile_size):
        self.tile_x, self.tile_y = tile_pos
        self.width = tile_size
        self.height = tile_size
        
        # Calculate pixel position based on tile (centered)
        self.x = self.tile_x * tile_size
        self.y = self.tile_y * tile_size
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.interaction_range = 80
        
        # Visuals: building sprite (pixel-perfect)
        self.image = self._load_sprite(tile_size)

    def _load_sprite(self, tile_size: int) -> pygame.Surface:
        asset_path = os.path.join(os.path.dirname(__file__), "assets", "buildings", "shop.png")
        try:
            img = pygame.image.load(asset_path).convert_alpha()
            # Make buildings WAY bigger: ~10 tiles in size (10x compared to the old 1-tile rendering).
            # Do NOT scale 10x from the source image pixels (these are 1024+ px assets).
            target_max = tile_size * 6
            src_w, src_h = img.get_size()
            scale = target_max / max(1, max(src_w, src_h))
            w = max(1, int(src_w * scale))
            h = max(1, int(src_h * scale))
            img = pygame.transform.scale(img, (w, h))
            return img
        except Exception:
            # Fallback (old placeholder)
            image = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            image.fill((0, 0, 255))
            font = get_pixel_font(20)
            text = font.render("S", True, (255, 255, 255))
            image.blit(text, (10, 5))
            return image

    def is_player_close(self, player):
        # Distance formula
        px, py = player.rect.center
        sx, sy = self.rect.center
        dist = math.hypot(px - sx, py - sy)
        return dist <= self.interaction_range

    def draw(self, screen, player, offset: tuple[int, int] = (0, 0)):
        ox, oy = offset
        # Draw Shopkeeper
        # Anchor the sprite to the tile (bottom-center)
        draw_x = self.x + ox + self.width // 2 - self.image.get_width() // 2
        draw_y = self.y + oy + self.height - self.image.get_height()
        screen.blit(self.image, (draw_x, draw_y))
        
        # Draw interaction prompt
        if self.is_player_close(player):
            font = get_pixel_font(16)
            msg = font.render("Press E", True, (255, 255, 255))
            # Draw above head
            rect = self.rect.move(ox, oy)
            bg_rect = pygame.Rect(rect.centerx - 25, rect.top - 25, 50, 20)
            pygame.draw.rect(screen, (50, 50, 50), bg_rect)
            screen.blit(msg, (bg_rect.x + 5, bg_rect.y))