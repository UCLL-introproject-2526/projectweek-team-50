import pygame
import os
from settings import WHITE, TILES_X, TILES_Y, TILE_SIZE, PLAYER_SPRITE_SCALE
from entities.entity import Entity
from inventory import Inventory
from render_utils import draw_ellipse_shadow

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
        
        # Spritesheet and animation
        self.direction = "down"  # down, up, left, right
        self.is_moving = False
        self.animation_frame = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.25  # seconds per frame

        # Draw the player slightly larger than a single tile (visual-only).
        # Movement/collision still use the base TILE_SIZE rect.
        self.sprite_draw_size = int(TILE_SIZE * PLAYER_SPRITE_SCALE)
        self.last_drawn_sprite = None
        
        # Load spritesheets
        self.idle_sprites = {}
        self.run_sprites = {}
        self.load_spritesheets()
        
        # Current sprite for rendering
        self.current_sprite = None

    def load_spritesheets(self):
        """Load spritesheet images from assets/IDLE and assets/RUN folders."""
        asset_path = os.path.join(os.path.dirname(__file__), "..", "assets")
        
        # Load IDLE spritesheets
        directions = ["down", "up", "left", "right"]
        for direction in directions:
            idle_file = os.path.join(asset_path, "IDLE", f"idle_{direction}.png")
            if os.path.exists(idle_file):
                spritesheet = pygame.image.load(idle_file).convert_alpha()
                frames = self._split_spritesheet(spritesheet)
                self.idle_sprites[direction] = frames
        
        # Load RUN spritesheets
        for direction in directions:
            run_file = os.path.join(asset_path, "RUN", f"run_{direction}.png")
            if os.path.exists(run_file):
                spritesheet = pygame.image.load(run_file).convert_alpha()
                frames = self._split_spritesheet(spritesheet)
                self.run_sprites[direction] = frames
    
    def _split_spritesheet(self, spritesheet):
        """Split a spritesheet into animation frames.

        Your player sheets are 768x80 and are arranged as TWO 32x40 rows
        that must be stacked to form ONE 32x80 frame (top + bottom).
        We compose those into a single frame, then scale to TILE_SIZE x TILE_SIZE.
        """
        frames: list[pygame.Surface] = []

        sheet_w = spritesheet.get_width()
        sheet_h = spritesheet.get_height()
        frame_w = TILE_SIZE

        cols = max(1, sheet_w // frame_w)

        # Special-case: 2-row stacked layout (e.g. 80px tall => 40px top + 40px bottom)
        if sheet_h % 2 == 0 and (sheet_h // 2) >= 1:
            half_h = sheet_h // 2
            for col in range(cols):
                x = col * frame_w
                if x + frame_w > sheet_w:
                    continue

                top = spritesheet.subsurface(pygame.Rect(x, 0, frame_w, half_h)).copy()
                bottom = spritesheet.subsurface(pygame.Rect(x, half_h, frame_w, half_h)).copy()

                combined = pygame.Surface((frame_w, sheet_h), pygame.SRCALPHA)
                combined.blit(top, (0, 0))
                combined.blit(bottom, (0, half_h))

                # Skip fully transparent columns
                if pygame.mask.from_surface(combined).count() == 0:
                    continue

                combined = self._zoom_frame(combined)
                frames.append(combined)

        # Fallback: treat as a single-row strip with full height
        if not frames:
            for col in range(cols):
                x = col * frame_w
                if x + frame_w > sheet_w:
                    continue

                frame = spritesheet.subsurface(pygame.Rect(x, 0, frame_w, sheet_h)).copy()
                if pygame.mask.from_surface(frame).count() == 0:
                    continue
                frame = self._zoom_frame(frame)
                frames.append(frame)

        if not frames:
            # Absolute fallback: 1 visible square
            frame = pygame.Surface((self.sprite_draw_size, self.sprite_draw_size), pygame.SRCALPHA)
            pygame.draw.rect(frame, WHITE, (0, 0, self.sprite_draw_size, self.sprite_draw_size))
            frames = [frame]

        return frames

    def _zoom_frame(self, frame: pygame.Surface) -> pygame.Surface:
        """Trim transparent borders and scale into a larger square.

        This keeps animations unchanged (same frames/order), but makes the
        warrior occupy more of the drawn area (less empty background).
        """
        mask = pygame.mask.from_surface(frame)
        rects = mask.get_bounding_rects()
        if not rects:
            return pygame.transform.scale(frame, (self.sprite_draw_size, self.sprite_draw_size))

        # Union all bounding rects
        bbox = rects[0].copy()
        for r in rects[1:]:
            bbox.union_ip(r)

        # Small padding so we don't crop outline pixels
        pad = 1
        bbox.x = max(0, bbox.x - pad)
        bbox.y = max(0, bbox.y - pad)
        bbox.w = min(frame.get_width() - bbox.x, bbox.w + pad * 2)
        bbox.h = min(frame.get_height() - bbox.y, bbox.h + pad * 2)

        cropped = frame.subsurface(bbox).copy()

        # Preserve aspect ratio: scale to fit inside a square, then center.
        target = pygame.Surface((self.sprite_draw_size, self.sprite_draw_size), pygame.SRCALPHA)
        cw, ch = cropped.get_size()
        if cw <= 0 or ch <= 0:
            return target

        scale = min(self.sprite_draw_size / cw, self.sprite_draw_size / ch)
        sw = max(1, int(cw * scale))
        sh = max(1, int(ch * scale))
        scaled = pygame.transform.scale(cropped, (sw, sh))
        target.blit(scaled, scaled.get_rect(center=(self.sprite_draw_size // 2, self.sprite_draw_size // 2)))
        return target

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
            self.direction = "left"
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
            self.direction = "right"
        elif keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
            self.direction = "up"
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
            self.direction = "down"

        return dx, dy

    def update(self, dt, tilemap, coin_manager, game):
        self.timer += dt
        self.animation_timer += dt
        
        # Check if moving
        dx, dy = self.handle_input()
        was_moving = self.is_moving
        self.is_moving = (dx != 0 or dy != 0)
        
        if self.timer >= self.move_delay:
            if self.is_moving:
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
        
        # Update animation frame
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0.0
            # Always increment animation frame
            sprite_dict = self.run_sprites if self.is_moving else self.idle_sprites
            if self.direction in sprite_dict:
                num_frames = len(sprite_dict[self.direction])
                if num_frames > 0:
                    self.animation_frame = (self.animation_frame + 1) % num_frames
        
        # Reset animation when state changes
        if was_moving != self.is_moving:
            self.animation_frame = 0
            self.animation_timer = 0.0

        super().update(dt)

    def draw(self, surface, offset: tuple[int, int] = (0, 0)):
        """Draw the player centered on the tile."""
        ox, oy = offset
        sprite_dict = self.run_sprites if self.is_moving else self.idle_sprites
        sprite_rect = pygame.Rect(0, 0, self.sprite_draw_size, self.sprite_draw_size)
        sprite_rect.center = (self.rect.centerx + ox, self.rect.centery + oy)

        # Ground shadow (draw first so the sprite appears above it)
        shadow_center = (sprite_rect.centerx, sprite_rect.bottom - int(sprite_rect.height * 0.18))
        shadow_size = (int(sprite_rect.width * 0.55), max(6, int(sprite_rect.height * 0.18)))
        draw_ellipse_shadow(surface, center=shadow_center, size=shadow_size, alpha=85, offset=(0, 2))

        if self.direction in sprite_dict and sprite_dict[self.direction]:
            frames = sprite_dict[self.direction]
            if frames:
                frame_index = self.animation_frame % len(frames)
                sprite = frames[frame_index]
                if sprite:
                    self.last_drawn_sprite = sprite
                    surface.blit(sprite, sprite_rect)
                    return

        if "down" in self.idle_sprites and self.idle_sprites["down"]:
            sprite = self.idle_sprites["down"][0]
            if sprite:
                self.last_drawn_sprite = sprite
                surface.blit(sprite, sprite_rect)
                return

        if self.last_drawn_sprite:
            surface.blit(self.last_drawn_sprite, sprite_rect)
            return

        pygame.draw.rect(surface, WHITE, sprite_rect)
        pygame.draw.rect(surface, (0, 0, 0), sprite_rect, 2)
