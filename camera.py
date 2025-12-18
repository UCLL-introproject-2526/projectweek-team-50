import math
import random

import pygame


class Camera:
    def __init__(
        self,
        *,
        world_size: tuple[int, int],
        screen_size: tuple[int, int],
        zoom: float = 2,
        follow_speed: float = 6.0,
        shake_max_px: float = 100.0,
        shake_decay: float = 3.0,
    ):
        self.world_w, self.world_h = world_size
        self.screen_w, self.screen_h = screen_size

        self.zoom = float(zoom)
        self.follow_speed = float(follow_speed)

        self.enabled = True

        self.pos = pygame.Vector2(self.world_w / 2, self.world_h / 2)  # camera center in world coords
        self._target = pygame.Vector2(self.pos)

        # Shake (trauma-based)
        self.trauma = 0.0
        self.shake_max_px = float(shake_max_px)
        self.shake_decay = float(shake_decay)
        self._shake_offset = pygame.Vector2(0, 0)

    @property
    def view_size(self) -> tuple[int, int]:
        # zoom > 1.0 means zoom IN (smaller view window that will be scaled up)
        z = max(0.05, float(self.zoom))
        vw = max(1, int(self.screen_w / z))
        vh = max(1, int(self.screen_h / z))
        return vw, vh

    def set_enabled(self, enabled: bool, *, snap: bool = True):
        enabled = bool(enabled)
        if enabled and not self.enabled and snap:
            self.pos.update(self._target)
            self.trauma = 0.0
            self._shake_offset.update(0, 0)
        self.enabled = enabled

    def set_target(self, target_pos: tuple[float, float] | pygame.Vector2):
        self._target = pygame.Vector2(target_pos)

    def add_shake(self, amount: float):
        """Add a subtle shake impulse.

        amount is in [0..1], higher = stronger/longer.
        """
        self.trauma = max(0.0, min(1.0, self.trauma + float(amount)))

    def update(self, dt: float, target_pos: tuple[float, float] | pygame.Vector2 | None = None):
        if target_pos is not None:
            self.set_target(target_pos)

        if not self.enabled:
            self._shake_offset.update(0, 0)
            self.trauma = 0.0
            return

        # Smooth follow
        alpha = min(self.follow_speed * max(0.0, float(dt)), 1.0)
        self.pos += (self._target - self.pos) * alpha

        # Decay shake trauma
        if self.trauma > 0.0:
            self.trauma = max(0.0, self.trauma - self.shake_decay * max(0.0, float(dt)))

        # New shake offset each frame (subtle)
        if self.trauma > 0.0:
            t = self.trauma * self.trauma
            angle = random.random() * math.tau
            mag = random.random() * t * self.shake_max_px
            self._shake_offset.update(math.cos(angle) * mag, math.sin(angle) * mag)
        else:
            self._shake_offset.update(0, 0)

    def _clamp_top_left(self, top_left: pygame.Vector2) -> pygame.Vector2:
        vw, vh = self.view_size

        # If the view is larger than the world, center the world in the view.
        if vw >= self.world_w:
            top_left.x = (self.world_w - vw) / 2
        else:
            top_left.x = max(0.0, min(top_left.x, self.world_w - vw))

        if vh >= self.world_h:
            top_left.y = (self.world_h - vh) / 2
        else:
            top_left.y = max(0.0, min(top_left.y, self.world_h - vh))

        return top_left

    def get_top_left(self) -> tuple[float, float]:
        vw, vh = self.view_size
        top_left = pygame.Vector2(self.pos.x - vw / 2, self.pos.y - vh / 2)
        top_left += self._shake_offset
        top_left = self._clamp_top_left(top_left)
        return float(top_left.x), float(top_left.y)

    def get_draw_offset(self) -> tuple[int, int]:
        """Offset to add to world coordinates when drawing to the camera view surface."""
        tx, ty = self.get_top_left()
        return int(-tx), int(-ty)
