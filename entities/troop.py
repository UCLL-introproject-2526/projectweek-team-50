import pygame
from entities.entity import Entity
from entities.projectile import Projectile
from settings import BLUE, TILE_SIZE
from asset_manager import get_tower_sprites
from render_utils import draw_ellipse_shadow

class Troop(Entity):
    def __init__(self, tile_pos, range_radius=160, fire_delay=0.6, damage=20, color=BLUE, slow_duration=0):
        super().__init__(tile_pos)

        self.range = range_radius
        self.fire_delay = fire_delay
        self.damage = damage
        self.color = color
        self.slow_duration = slow_duration  # Duration to slow enemies (0 = no slow)
        
        self.timer = 0.0

        # Sprite/animation state (optional; used if sprite assets exist)
        self.sprite_type = getattr(self, "sprite_type", None)
        self.direction = "right"
        self.attack_timer = 0.0
        self._anim_timer = 0.0
        self._anim_frame = 0
        self._was_attacking = False
        self._idle_frame_time = 0.11
        self._attack_frame_time = 0.07
        st = self._get_sprite_type()
        if st == "goblin":
            self._sprite_draw_size = int(TILE_SIZE * 3)
        elif st == "bloodmage":
            self._sprite_draw_size = int(TILE_SIZE * 3)
        elif st == "wizard":
            self._sprite_draw_size = int(TILE_SIZE * 1.5)
        elif st == "elf":
            self._sprite_draw_size = int(TILE_SIZE * 1.75)
        elif st == "firewarrior":
            self._sprite_draw_size = int(TILE_SIZE * 2.5)
        else:
            self._sprite_draw_size = int(TILE_SIZE * 2)
        if st == "knight":
            self._attack_frame_time = 0.045

    def update(self, dt, enemies, projectiles, coin_manager=None, tilemap=None):
        self.timer += dt
        if self.attack_timer > 0:
            self.attack_timer -= dt

        target = self.find_target(enemies)
        if target:
            dx = target.rect.centerx - self.rect.centerx
            dy = target.rect.centery - self.rect.centery
            self.direction = self._pick_direction(dx, dy)
        elif tilemap is not None:
            self.direction = self._pick_direction_to_path(tilemap)

        if self.timer >= self.fire_delay:
            if target:
                self.attack_target(target, projectiles, coin_manager, tilemap)
                self.timer = 0.0

        attacking = self.attack_timer > 0
        if attacking and not self._was_attacking:
            self._anim_frame = 0
            self._anim_timer = 0.0
        self._was_attacking = attacking

        self._anim_timer += dt
        frame_time = self._attack_frame_time if attacking else self._idle_frame_time
        sprites = get_tower_sprites(self._get_sprite_type(), tower_size=self._sprite_draw_size)
        frames = (sprites.attack if attacking else sprites.idle).get(self.direction, [])
        if frames and self._anim_timer >= frame_time:
            self._anim_timer = 0.0
            self._anim_frame = (self._anim_frame + 1) % len(frames)

    def _get_sprite_type(self) -> str:
        st = getattr(self, "sprite_type", None)
        if st:
            return str(st).lower()
        # Fallback: class name (e.g. FireWarrior -> firewarrior)
        return self.__class__.__name__.lower()

    @staticmethod
    def _pick_direction(dx: float, dy: float) -> str:
        if abs(dx) > abs(dy):
            return "right" if dx >= 0 else "left"
        if abs(dy) > 0:
            return "down" if dy >= 0 else "up"
        return "right"

    def _pick_direction_to_path(self, tilemap) -> str:
        try:
            path = tilemap.get_path_points()
        except Exception:
            return self.direction
        if not path:
            return self.direction

        cx, cy = self.rect.center
        best_i = 0
        best_d2 = float("inf")
        for i, (px, py) in enumerate(path):
            dx = px - cx
            dy = py - cy
            d2 = dx * dx + dy * dy
            if d2 < best_d2:
                best_d2 = d2
                best_i = i

        if best_i < len(path) - 1:
            nx, ny = path[best_i + 1]
        elif best_i > 0:
            nx, ny = path[best_i - 1]
        else:
            return self.direction
        return self._pick_direction(nx - cx, ny - cy)

    def find_target(self, enemies):
        best_target = None
        min_dist = float('inf')
        
        # Simple closest target logic
        for e in enemies:
            dx = e.rect.centerx - self.rect.centerx
            dy = e.rect.centery - self.rect.centery
            dist_sq = dx * dx + dy * dy
            
            if dist_sq <= self.range * self.range:
                if dist_sq < min_dist:
                    min_dist = dist_sq
                    best_target = e
        return best_target

    def attack_target(self, target, projectiles, coin_manager=None, tilemap=None):
        # Default behavior: Shoot Projectile
        self.attack_timer = 0.22
        projectiles.append(
            Projectile(
                self.rect.centerx,
                self.rect.centery,
                target,
                damage=self.damage,
                slow_duration=self.slow_duration,
                source_type=self._get_sprite_type(),
                coin_manager=coin_manager,
                tilemap=tilemap
            )
        )

    def draw(self, surface, offset: tuple[int, int] = (0, 0)):
        ox, oy = offset
        base_rect = self.rect.move(ox, oy)

        sprites = get_tower_sprites(self._get_sprite_type(), tower_size=self._sprite_draw_size)
        attacking = self.attack_timer > 0
        frames = (sprites.attack if attacking else sprites.idle).get(self.direction, [])

        if frames:
            frame = frames[self._anim_frame % len(frames)]
            if not sprites.supports_directions and self.direction == "left":
                frame = pygame.transform.flip(frame, True, False)
            dst = frame.get_rect(center=base_rect.center)

            shadow_w = max(int(self._sprite_draw_size * 0.55), int(TILE_SIZE * 1.1))
            shadow_h = max(6, int(self._sprite_draw_size * 0.10))
            draw_ellipse_shadow(
                surface,
                center=base_rect.midbottom,
                size=(shadow_w, shadow_h),
                alpha=35,
                offset=(0, -2),
            )
            surface.blit(frame, dst)
            return

        pygame.draw.rect(surface, self.color, base_rect)