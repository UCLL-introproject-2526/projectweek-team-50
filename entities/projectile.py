import pygame
import math
from settings import YELLOW
from coins import handle_death
from settings import TILE_SIZE
from asset_manager import get_projectile_frames

# Projectile optionally receives coin_manager and tilemap so it can trigger coin drops

class Projectile:
    def __init__(
        self,
        x,
        y,
        target,
        speed=400,
        damage=20,
        slow_duration=0,
        projectile_speed=4.0,
        source_type: str | None = None,
        coin_manager=None,
        tilemap=None,
    ):
        self.x = x
        self.y = y
        self.target = target
        self.speed = speed * projectile_speed  # Multiply base speed by projectile_speed factor
        self.damage = damage
        self.slow_duration = slow_duration
        self.alive = True
        self.coin_manager = coin_manager
        self.tilemap = tilemap

        self.source_type = (source_type or "").lower()
        self._anim_timer = 0.0
        self._anim_frame = 0
        self._frame_time = 0.07
        self._last_dx = 1.0
        self._last_dy = 0.0
        self._sprite_size = max(12, int(TILE_SIZE * 0.9))
        self._frames = get_projectile_frames(self.source_type, projectile_size=self._sprite_size)

    def update(self, dt):
        if not self.target or self.target.finished:
            self.alive = False
            return

        dx = self.target.rect.centerx - self.x
        dy = self.target.rect.centery - self.y
        dist = math.hypot(dx, dy)

        if dist > 1e-6:
            self._last_dx, self._last_dy = dx, dy

        # Consider the projectile hitting the target if it's within a small
        # distance or the projectile point lies within the target rect.
        hit = False
        if dist < max(5, getattr(self.target, 'radius', 8)):
            hit = True
        else:
            try:
                if self.target.rect.collidepoint(int(self.x), int(self.y)):
                    hit = True
            except Exception:
                pass

        if hit:
            self.target.health -= self.damage
            self.target.killed_by_tower = True  # Mark as killed by tower for coin drops
            
            # Apply slow effect if wizard
            if self.slow_duration > 0:
                if not hasattr(self.target, 'slow_timer'):
                    self.target.slow_timer = 0
                self.target.slow_timer = self.slow_duration
            
            # If the hit killed the enemy, mark finished and spawn coins
            if self.target.health <= 0:
                self.target.finished = True
                if self.coin_manager and self.tilemap:
                    try:
                        handle_death(self.target, self.coin_manager, self.tilemap)
                    except Exception:
                        pass
            self.alive = False
            return

        self.x += (dx / dist) * self.speed * dt
        self.y += (dy / dist) * self.speed * dt

        # Advance animation
        if self._frames:
            self._anim_timer += dt
            if self._anim_timer >= self._frame_time:
                self._anim_timer = 0.0
                self._anim_frame = (self._anim_frame + 1) % len(self._frames)

    def draw(self, surface, offset: tuple[int, int] = (0, 0)):
        ox, oy = offset

        if self._frames:
            frame = self._frames[self._anim_frame % len(self._frames)]
            # Face travel direction: if mostly horizontal, use flip.
            # If diagonal/vertical, do a gentle rotate.
            dx, dy = self._last_dx, self._last_dy
            if abs(dx) >= abs(dy):
                if dx < 0:
                    frame = pygame.transform.flip(frame, True, False)
            else:
                angle = -math.degrees(math.atan2(dy, dx))
                try:
                    frame = pygame.transform.rotate(frame, angle)
                except Exception:
                    pass

            dst = frame.get_rect(center=(int(self.x) + ox, int(self.y) + oy))
            surface.blit(frame, dst)
            return

        pygame.draw.circle(surface, YELLOW, (int(self.x) + ox, int(self.y) + oy), 4)
