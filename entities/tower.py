import os
import pygame
from entities.entity import Entity
from entities.projectile import Projectile
from settings import RED, GREEN, BLUE, TILE_SIZE
from asset_manager import get_tower_sprites
from render_utils import draw_ellipse_shadow


_SFX_CACHE: dict[str, pygame.mixer.Sound | None] = {}


def _get_sfx(filename: str, *, volume: float) -> pygame.mixer.Sound | None:
    """Load a wav from assets/sounds once and reuse it."""
    key = f"{filename}|{volume:.3f}"
    if key in _SFX_CACHE:
        return _SFX_CACHE[key]

    try:
        if not pygame.mixer.get_init():
            _SFX_CACHE[key] = None
            return None
    except Exception:
        _SFX_CACHE[key] = None
        return None

    try:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "sounds"))
        path = os.path.join(base, filename)
        if not os.path.exists(path):
            _SFX_CACHE[key] = None
            return None
        s = pygame.mixer.Sound(path)
        s.set_volume(max(0.0, min(1.0, float(volume))))
        _SFX_CACHE[key] = s
        return s
    except Exception:
        _SFX_CACHE[key] = None
        return None


def _play_sfx(filename: str, *, volume: float) -> None:
    s = _get_sfx(filename, volume=volume)
    if s is None:
        return
    try:
        s.play()
    except Exception:
        pass

class Tower(Entity):
    def __init__(self, tile_pos, tower_type):
        super().__init__(tile_pos)
        self.type = tower_type
        # Default fields
        self.slow_duration = 0
        self.stun_duration = 0
        self.projectile_speed = 4.0

        if tower_type == 'goblin':
            # Melee (weakest)
            self.range = 55
            self.damage = 18
            self.fire_delay = 0.50
            self.color = (40, 170, 60)
        elif tower_type == 'elf':
            # Melee
            self.range = 65
            self.damage = 26
            self.fire_delay = 0.55
            self.color = (120, 220, 120)
        elif tower_type == 'knight':
            # Melee with small stun on first hit
            self.range = 80
            self.damage = 40
            self.fire_delay = 0.85
            self.color = RED
            self.stun_duration = 0.4
        elif tower_type == 'archer':
            # Medium ranged
            self.range = 180
            self.damage = 32
            self.fire_delay = 0.65
            self.color = GREEN
        elif tower_type == 'wizard':
            # High range with slow
            self.range = 260
            self.damage = 42
            self.fire_delay = 0.80
            self.color = BLUE
            self.slow_duration = 0.5
        elif tower_type == 'firewarrior':
            # Melee but bigger range
            self.range = 110
            self.damage = 60
            self.fire_delay = 0.75
            self.color = (220, 80, 40)
        elif tower_type == 'bloodmage':
            # Strongest: very high range
            self.range = 340
            self.damage = 85
            self.fire_delay = 0.90
            self.color = (150, 40, 200)
            self.projectile_speed = 5.5
        else:
            # Safety fallback: treat unknown tower IDs as a basic goblin.
            self.type = 'goblin'
            self.range = 55
            self.damage = 18
            self.fire_delay = 0.50
            self.color = (40, 170, 60)
        
        self.timer = 0.0
        self.attack_timer = 0.0

        # Sprite/animation state
        self.direction = "right"  # up/down/left/right
        self._anim_timer = 0.0
        self._anim_frame = 0
        self._was_attacking = False
        # Slightly slower idle, snappier attack
        self._idle_frame_time = 0.11
        self._attack_frame_time = 0.07
        if self.type == "knight":
            # Knight attack should feel fast/snappy.
            self._attack_frame_time = 0.045
        # Towers render larger than a single tile. Goblin sheets are larger and
        # look too small if forced into a 64px height.
        # Also tune a few classes to match their art proportions.
        if self.type == "goblin":
            self._sprite_draw_size = int(TILE_SIZE * 3)      # bigger
        elif self.type == "bloodmage":
            self._sprite_draw_size = int(TILE_SIZE * 3)      # bigger
        elif self.type == "wizard":
            self._sprite_draw_size = int(TILE_SIZE * 1.5)    # smaller
        elif self.type == "elf":
            self._sprite_draw_size = int(TILE_SIZE * 1.75)   # a bit smaller
        elif self.type == "firewarrior":
            self._sprite_draw_size = int(TILE_SIZE * 2.5)    # bigger
        else:
            self._sprite_draw_size = int(TILE_SIZE * 2)

        # Lock an idle-facing direction to avoid jittering flips when no target.
        self._path_facing_locked = False

    def update(self, dt, enemies, projectiles, coin_manager=None, tilemap=None):
        self.timer += dt
        if self.attack_timer > 0:
            self.attack_timer -= dt

        # Facing:
        # - Only goblin has true directional POV assets.
        # - For other towers, keep a stable "faces the path" direction so sprites
        #   don't flip back/forth as targets move.
        target = self.find_target(enemies)
        attacking = self.attack_timer > 0
        if self.type == "goblin" and target:
            dx = target.rect.centerx - self.rect.centerx
            dy = target.rect.centery - self.rect.centery
            self.direction = self._pick_direction(dx, dy)
            self._path_facing_locked = False
        elif (not self._path_facing_locked) and tilemap is not None:
            self.direction = self._pick_direction_to_path(tilemap)
            self._path_facing_locked = True
        
        if self.timer >= self.fire_delay:
            if target:
                self.attack_target(target, projectiles, coin_manager, tilemap)
                self.timer = 0.0

        # Update animation (idle during cooldown; attack only while attack_timer > 0)
        attacking = self.attack_timer > 0
        if attacking and not self._was_attacking:
            self._anim_frame = 0
            self._anim_timer = 0.0
        self._was_attacking = attacking

        self._anim_timer += dt
        frame_time = self._attack_frame_time if attacking else self._idle_frame_time
        sprites = get_tower_sprites(self.type, tower_size=self._sprite_draw_size)
        frames = (sprites.attack if attacking else sprites.idle).get(self.direction, [])
        if frames and self._anim_timer >= frame_time:
            self._anim_timer = 0.0
            self._anim_frame = (self._anim_frame + 1) % len(frames)

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

        # Look along the path direction at the nearest point.
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
        melee_types = {'goblin', 'elf', 'knight', 'firewarrior'}

        # Decide how long to display attack animation.
        sprites = get_tower_sprites(self.type, tower_size=self._sprite_draw_size)
        attack_frames = sprites.attack.get(self.direction, [])
        min_show = 0.22
        if attack_frames:
            min_show = max(min_show, len(attack_frames) * self._attack_frame_time)

        if self.type in melee_types:
            # Melee towers use instant attack instead of projectile
            target.health -= self.damage
            target.killed_by_tower = True
            self.attack_timer = min_show

            # Melee hit SFX
            if self.type == 'knight':
                _play_sfx("07_human_atk_sword_2.wav", volume=0.22)
            elif self.type == 'elf':
                _play_sfx("26_sword_hit_1.wav", volume=0.20)
            elif self.type == 'firewarrior':
                _play_sfx("10_human_special_atk_1.wav", volume=0.22)

            # Extra boss damage feedback
            if getattr(target, 'enemy_type', '').lower() == 'boss':
                _play_sfx("21_orc_damage_3.wav", volume=0.14)
            
            # Knight stuns the enemy only on first hit
            if self.type == 'knight' and not target.has_been_stunned:
                target.stun_timer = self.stun_duration
                target.has_been_stunned = True
            
            # If enemy dies, handle it
            if target.health <= 0:
                target.finished = True
                if coin_manager and tilemap:
                    try:
                        from coins import handle_death
                        handle_death(target, coin_manager, tilemap)
                    except Exception:
                        pass
        else:
            # Other towers use projectiles
            self.attack_timer = min_show

            # Fire SFX per ranged tower
            if self.type == 'archer':
                _play_sfx("Retro Weapon Arrow 02.wav", volume=0.22)
            elif self.type == 'wizard':
                _play_sfx("Retro Blop 07.wav", volume=0.18)
            elif self.type == 'bloodmage':
                # Use an electric shot SFX.
                _play_sfx("Retro Weapon Electric 05.wav", volume=0.20)

            projectiles.append(
                Projectile(
                    self.rect.centerx,
                    self.rect.centery,
                    target,
                    damage=self.damage,
                    slow_duration=self.slow_duration,
                    projectile_speed=self.projectile_speed,
                    source_type=self.type,
                    coin_manager=coin_manager,
                    tilemap=tilemap
                )
            )

    def draw(self, surface, offset: tuple[int, int] = (0, 0)):
        ox, oy = offset
        base_rect = self.rect.move(ox, oy)

        sprites = get_tower_sprites(self.type, tower_size=self._sprite_draw_size)
        attacking = self.attack_timer > 0
        frames = (sprites.attack if attacking else sprites.idle).get(self.direction, [])

        if frames:
            frame = frames[self._anim_frame % len(frames)]
            # Only flip when the asset set truly supports directional POVs.
            # (For non-directional towers we keep a stable path-facing direction.)
            if sprites.supports_directions and self.direction == "left":
                frame = pygame.transform.flip(frame, True, False)

            # Anchor by bottom-center so width differences don't look like movement.
            dst = frame.get_rect(midbottom=base_rect.midbottom)

            # Very subtle ground shadow under tower.
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

        # Fallback: old colored rects if sprites missing
        if self.type in {'goblin', 'elf', 'knight', 'firewarrior'} and self.attack_timer > 0:
            expansion = int(20 * (1 - self.attack_timer / 0.22))
            expanded_rect = base_rect.inflate(expansion * 2, expansion * 2)
            pygame.draw.rect(surface, self.color, expanded_rect)
        else:
            pygame.draw.rect(surface, self.color, base_rect)