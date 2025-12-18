import pygame
import os
from settings import *
from camera import Camera
from shop import Shop
from shopkeeper import Shopkeeper
from casino import Casino
from casino_keeper import CasinoKeeper
from coins import CoinManager, handle_death

from level_io import load_level_from_txt

from entities.player import Player
from entities.troop import Troop
from entities.castle import Castle
from world.tilemap import TileMap
from world.wave_manager import WaveManager


level = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

# If you used the level editor, it saves to `level.txt`. Load it if present,
# otherwise fall back to the hardcoded default above.
_level_txt_path = os.path.join(os.path.dirname(__file__), "level.txt")
level = load_level_from_txt(
    _level_txt_path,
    fallback=level,
    expected_width=TILES_X,
    expected_height=TILES_Y,
)


class Game:
    def __init__(self):
        # Detect display size
        display_info = pygame.display.Info()
        self.display_width = display_info.current_w
        self.display_height = display_info.current_h
        
        # Fullscreen state
        self.fullscreen = False
        
        # Window - start in windowed mode but sized appropriately
        window_scale = 0.85  # Use 85% of screen by default
        window_width = int(self.display_width * window_scale)
        window_height = int(self.display_height * window_scale)
        
        # Keep aspect ratio of game
        game_aspect = SCREEN_WIDTH / SCREEN_HEIGHT
        window_aspect = window_width / window_height
        
        if window_aspect > game_aspect:
            window_width = int(window_height * game_aspect)
        else:
            window_height = int(window_width / game_aspect)
        
        self.window = pygame.display.set_mode(
            (window_width, window_height),
            pygame.RESIZABLE
        )
        pygame.display.set_caption(TITLE)

        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.window_size = self.window.get_size()

        self.clock = pygame.time.Clock()
        self.running = True

        # Font
        self.font = get_pixel_font(24)

        # Font for UI
        self.font = get_pixel_font(24)
        
        # Font for announcements
        self.announcement_font = get_pixel_font(60)

        # World
        self.tilemap = TileMap(level)

        # Camera
        self.camera_enabled = True
        self.camera = Camera(
            world_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
            zoom=1.7,
            follow_speed=6.0,
            shake_max_px=14.0,
            shake_decay=3.0,
        )
        vw, vh = self.camera.view_size
        self._camera_surface = pygame.Surface((vw, vh))

        # Entities
        self.player = Player(tile_pos=(1, 1))
        self.enemies = []
        self.towers = []
        self.projectiles = []
        
        # Coin system
        self.coin_manager = CoinManager()

        # Player
        self.player.gold = 100
        self.player.health = 100
        self.player.max_health = 100

        # Start the camera centered on the player so it follows immediately.
        self.camera.set_target(self.player.rect.center)
        self.camera.pos.update(self.player.rect.center)

        # Castle
        self.castle_hp = 100
        self.castle_max_hp = 100
        self.game_over = False
        self.game_won = False
        self.game_over_timer = 0.0  # For fade and animation effects

        # Wave system
        self.wave_manager = WaveManager(self.tilemap)
        self.current_wave = 0
        self.max_waves = 5
        self.wave_manager.start_wave(self.current_wave + 1)

        # Game state
        self.game_over = False
        
        # Tower placement cooldown
        self.placement_cooldown = 0.0

        # Shop system
        self.shop = Shop(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.shopkeeper = Shopkeeper(tile_pos=(12, 20), tile_size=TILE_SIZE)
        
        # Casino system
        self.casino = Casino(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.casino_keeper = CasinoKeeper(tile_pos=(14, 20), tile_size=TILE_SIZE)
        
        # Startup message - will be activated after first wave announcement
        self.startup_message_timer = 0.0
        self.startup_message_active = False
        self.startup_message_alpha = 255
        
        # Damage flash animation
        self.damage_flash_timer = 0.0

    # -----------------------------
    # Utility
    # -----------------------------
    def screen_to_tile(self, mouse_pos):
        mx, my = mouse_pos
        window_w, window_h = self.window.get_size()

        scale = min(
            window_w / SCREEN_WIDTH,
            window_h / SCREEN_HEIGHT
        )

        scaled_w = SCREEN_WIDTH * scale
        scaled_h = SCREEN_HEIGHT * scale

        x_offset = (window_w - scaled_w) / 2
        y_offset = (window_h - scaled_h) / 2

        # Ignore clicks outside game area
        if (
            mx < x_offset or
            my < y_offset or
            mx > x_offset + scaled_w or
            my > y_offset + scaled_h
        ):
            return None

        # Convert back to logical coordinates
        lx = (mx - x_offset) / scale
        ly = (my - y_offset) / scale

        if self.camera_enabled:
            # Map logical screen coords into the camera view surface coords,
            # then into world coords by adding the camera top-left.
            top_left_x, top_left_y = self.camera.get_top_left()
            world_x = top_left_x + (lx / self.camera.zoom)
            world_y = top_left_y + (ly / self.camera.zoom)
            tile_x = int(world_x // TILE_SIZE)
            tile_y = int(world_y // TILE_SIZE)
        else:
            tile_x = int(lx // TILE_SIZE)
            tile_y = int(ly // TILE_SIZE)

        return tile_x, tile_y

    # -----------------------------
    # Events
    # -----------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.VIDEORESIZE:
                self.window = pygame.display.set_mode(
                    (event.w, event.h),
                    pygame.RESIZABLE
                )
                self.window_size = (event.w, event.h)

            elif event.type == pygame.KEYDOWN:
                # F11 or F for fullscreen toggle
                if event.key == pygame.K_F11 or event.key == pygame.K_f:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.window = pygame.display.set_mode(
                            (self.display_width, self.display_height),
                            pygame.FULLSCREEN
                        )
                    else:
                        # Return to windowed mode with 85% screen size
                        window_scale = 0.85
                        window_width = int(self.display_width * window_scale)
                        window_height = int(self.display_height * window_scale)
                        
                        # Keep aspect ratio
                        game_aspect = SCREEN_WIDTH / SCREEN_HEIGHT
                        window_aspect = window_width / window_height
                        
                        if window_aspect > game_aspect:
                            window_width = int(window_height * game_aspect)
                        else:
                            window_height = int(window_width / game_aspect)
                        
                        self.window = pygame.display.set_mode(
                            (window_width, window_height),
                            pygame.RESIZABLE
                        )
                    self.window_size = self.window.get_size()
                
                # G key to toggle grid
                if event.key == pygame.K_g:
                    import settings
                    settings.SHOW_GRID = not settings.SHOW_GRID

                # C key toggles camera effects (follow/zoom/shake)
                if event.key == pygame.K_c:
                    self.camera_enabled = not self.camera_enabled
                    self.camera.set_enabled(self.camera_enabled, snap=True)
                
                if event.key == pygame.K_e:
                    if self.shopkeeper.is_player_close(self.player):
                        self.shop.toggle()
                    elif self.casino_keeper.is_player_close(self.player):
                        self.casino.toggle()
                    elif self.shop.active:
                        self.shop.toggle()
                    elif self.casino.active:
                        self.casino.toggle()
                
                # Inventory slot selection (1-5) - only if shop/casino not active
                if not self.shop.active and not self.casino.active:
                    if pygame.K_1 <= event.key <= pygame.K_5:
                        slot_num = event.key - pygame.K_1 + 1
                        self.player.inventory.select_slot(slot_num)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass  # removed troop placement


    # -----------------------------
    # Update
    # -----------------------------
    def update(self, dt):
        # Activate startup message after first wave announcement ends
        if not self.startup_message_active and not self.wave_manager.show_announcement and self.current_wave == 0:
            self.startup_message_active = True
            self.startup_message_timer = 5.0
            print("Startup message activated!")  # Debug
        
        # Update startup message timer
        if self.startup_message_active and self.startup_message_timer > 0:
            self.startup_message_timer -= dt
            # Fade out in the last 1 second
            if self.startup_message_timer < 1.0:
                self.startup_message_alpha = int(255 * self.startup_message_timer)
            else:
                self.startup_message_alpha = 255
        
        if self.shop.active:
            self.shop.handle_input(self.player)
            return
        
        if self.casino.active:
            self.casino.handle_input(self.player)
            self.casino.update(dt, self.player)
            return

        # Pause game during wave announcements
        if self.wave_manager.show_announcement:
            self.wave_manager.update(dt, self.enemies)
            return

        self.player.update(dt, self.tilemap, self.coin_manager, self)

        # Camera follow
        if self.camera_enabled:
            self.camera.update(dt, target_pos=self.player.rect.center)
        
        # Update animated coins
        self.coin_manager.update(dt)
        
        # Check collision with enemies for damage
        for enemy in self.enemies:
            dx = self.player.rect.centerx - enemy.rect.centerx
            dy = self.player.rect.centery - enemy.rect.centery
            dist = (dx*dx + dy*dy) ** 0.5
            
            # If player collides with enemy (within combined radius)
            if dist < (self.player.radius + enemy.radius + 10):
                if self.player.damage_cooldown <= 0:
                    # Calculate damage based on wave and enemy strength
                    base_damage = 5 + (self.wave_manager.current_wave - 1) * 3
                    
                    # Enemy type multipliers
                    if enemy.enemy_type == "boss":
                        damage = base_damage * 3
                    elif enemy.enemy_type == "slow_strong":
                        damage = base_damage * 2
                    elif enemy.enemy_type == "fast_weak":
                        damage = base_damage * 0.75
                    else:
                        damage = base_damage
                    
                    self.player.health -= damage
                    self.player.damage_cooldown = 0.5
                    self.damage_flash_timer = 0.3  # Flash for 0.3 seconds

                    if self.camera_enabled:
                        # Mild hit shake
                        self.camera.add_shake(0.22)
                    
                    # Game over if player health reaches 0
                    if self.player.health <= 0:
                        self.game_over = True

                        if self.camera_enabled:
                            # Slightly stronger death shake
                            self.camera.add_shake(0.55)
        
        # Update damage cooldown
        if self.player.damage_cooldown > 0:
            self.player.damage_cooldown -= dt
        
        # Update damage flash timer
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt

        # Update placement cooldown
        if self.placement_cooldown > 0:
            self.placement_cooldown -= dt

        # Tower placement
        if not self.shop.active and self.placement_cooldown <= 0:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_p]:
                selected_tower = self.player.inventory.get_selected_tower()
                if selected_tower:
                    tx, ty = self.player.tile_x, self.player.tile_y
                    if not self.tilemap.is_blocked(tx, ty) and not self.tilemap.is_path(tx, ty):
                        from entities.tower import Tower
                        self.towers.append(Tower((tx, ty), selected_tower))
                        self.player.inventory.remove_item(selected_tower)
                        self.placement_cooldown = 0.2  # 200ms cooldown between placements
                        # Only deselect if the selected slot is now empty
                        if self.player.inventory.get_selected_tower() is None:
                            self.player.inventory.selected_slot = None

        # Enemies
        self.wave_manager.update(dt, self.enemies)
        
        # Check if wave is complete (all enemies dead/reached castle) and start next
        if self.wave_manager.check_wave_complete(self.enemies):
            if self.wave_manager.current_wave < self.wave_manager.max_waves:
                self.wave_manager.start_wave(self.wave_manager.current_wave + 1)
            else:
                # All waves completed - victory!
                self.game_won = True
                self.game_over_timer = 0.0
        
        for enemy in self.enemies:
            enemy.update(dt)

        # Towers
        for tower in self.towers:
            tower.update(dt, self.enemies, self.projectiles, self.coin_manager, self.tilemap)

        # Projectiles
        for projectile in self.projectiles:
            projectile.update(dt)

        # Handle enemies that reached the castle
        for enemy in self.enemies:
            if enemy.finished and enemy.health > 0:
                # enemy reached the castle
                # Boss enemies instantly lose the game
                if enemy.enemy_type == "boss":
                    self.game_over = True
                else:
                    self.castle_hp -= 1

        # Cleanup
        self.projectiles = [p for p in self.projectiles if p.alive]
        
        # Process dead enemies and spawn coins
        alive_enemies = []
        for e in self.enemies:
            if not e.finished and e.health > 0:
                alive_enemies.append(e)
            else:
                # Enemy died, drop coins
                handle_death(e, self.coin_manager, self.tilemap)
        self.enemies = alive_enemies

        # Check game over
        if self.castle_hp <= 0:
            self.game_over = True
            self.game_over_timer = 0.0

    # -----------------------------
    # Draw
    # -----------------------------
    def _draw_world(self, surface: pygame.Surface, *, offset: tuple[int, int] = (0, 0)):
        ox, oy = offset

        surface.fill(BG_COLOR)

        self.tilemap.draw(surface, player_bottom=self.player.rect.bottom, offset=offset)
        self.player.draw(surface, offset=offset)
        # Trees that the player is "behind" should draw on top
        self.tilemap.draw_tree_foreground(surface, player_bottom=self.player.rect.bottom, offset=offset)

        # Draw castle HP bar above finish tile (fallback to default if missing)
        finish_center = self.tilemap.get_finish_center()
        if finish_center:
            castle_x, castle_y = finish_center
        else:
            castle_x = 11 * TILE_SIZE + TILE_SIZE // 2
            castle_y = 6 * TILE_SIZE

        bar_width = 50
        bar_height = 5
        bar_x = castle_x - bar_width // 2 + ox
        bar_y = castle_y - 10 + oy
        pygame.draw.rect(surface, BLACK, (bar_x, bar_y, bar_width, bar_height))
        if self.castle_max_hp > 0:
            hp_ratio = self.castle_hp / self.castle_max_hp
            pygame.draw.rect(surface, GREEN, (bar_x, bar_y, bar_width * hp_ratio, bar_height))

        for tower in self.towers:
            tower.draw(surface, offset=offset)

        for enemy in self.enemies:
            enemy.draw(surface, offset=offset)

            # Draw health indicator above boss enemies
            if enemy.enemy_type == "boss":
                rect = enemy.rect.move(ox, oy)
                # Full health bar for boss
                bar_width = 60
                bar_height = 8
                bar_x = rect.centerx - bar_width // 2
                bar_y = rect.top - 20

                # Background bar
                pygame.draw.rect(surface, BLACK, (bar_x, bar_y, bar_width, bar_height))

                # Health bar
                if enemy.max_health > 0:
                    health_ratio = max(0, enemy.health / enemy.max_health)
                    health_color = (0, 255, 0) if health_ratio > 0.5 else (255, 255, 0) if health_ratio > 0.2 else (255, 0, 0)
                    pygame.draw.rect(surface, health_color, (bar_x, bar_y, bar_width * health_ratio, bar_height))

                # Border
                pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

            # Draw warning indicator for slow enemies
            if enemy.enemy_type == "slow_strong":
                rect = enemy.rect.move(ox, oy)
                # Small warning icon
                pygame.draw.circle(surface, (200, 50, 200), (rect.centerx + 15, rect.centery - 15), 5)
                pygame.draw.circle(surface, (255, 255, 255), (rect.centerx + 15, rect.centery - 15), 5, 1)

        for projectile in self.projectiles:
            projectile.draw(surface, offset=offset)

        # Draw coins
        self.coin_manager.draw(surface, offset=offset)

        self.shopkeeper.draw(surface, self.player, offset=offset)
        self.casino_keeper.draw(surface, self.player, offset=offset)

    def draw(self):
        self.screen.fill(BG_COLOR)

        if self.camera_enabled:
            vw, vh = self.camera.view_size
            if self._camera_surface.get_width() != vw or self._camera_surface.get_height() != vh:
                self._camera_surface = pygame.Surface((vw, vh))

            draw_offset = self.camera.get_draw_offset()
            self._draw_world(self._camera_surface, offset=draw_offset)

            scaled_world = pygame.transform.scale(self._camera_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen.blit(scaled_world, (0, 0))
        else:
            self._draw_world(self.screen, offset=(0, 0))

        # Draw money
        money_text = self.font.render(f"Money: {self.player.gold} TL", True, WHITE)
        self.screen.blit(money_text, (SCREEN_WIDTH//2 - money_text.get_width()//2, 10))
        
        # Draw player health bar
        health_bar_width = 200
        health_bar_height = 15
        health_bar_x = SCREEN_WIDTH // 2 - health_bar_width // 2
        # Place HP bar just above the inventory bar (no overlap)
        inventory_bar_height = 70
        inventory_bar_y = min(int(SCREEN_HEIGHT * 0.90), SCREEN_HEIGHT - inventory_bar_height)
        health_bar_y = inventory_bar_y - health_bar_height - 10
        
        # Background bar
        pygame.draw.rect(self.screen, BLACK, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Health bar with damage flash
        if self.player.max_health > 0:
            health_ratio = max(0, self.player.health / self.player.max_health)
            
            # Determine color: flash red when damaged, otherwise green/yellow/red based on health
            if self.damage_flash_timer > 0:
                health_color = (255, 0, 0)  # Red flash
            else:
                health_color = (0, 255, 0) if health_ratio > 0.5 else (255, 255, 0) if health_ratio > 0.25 else (255, 0, 0)
            
            pygame.draw.rect(self.screen, health_color, (health_bar_x, health_bar_y, health_bar_width * health_ratio, health_bar_height))
        
        # Border
        pygame.draw.rect(self.screen, WHITE, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)
        
        # Health text
        health_text = self.font.render(f"HP: {int(self.player.health)}/{self.player.max_health}", True, WHITE)
        self.screen.blit(health_text, (health_bar_x + health_bar_width + 10, health_bar_y + 2))

        # Draw wave counter
        wave_text = self.font.render(f"Wave: {self.wave_manager.current_wave}", True, WHITE)
        self.screen.blit(wave_text, (10, 40))

        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2))

        # Draw wave
        wave_text = self.font.render(f"Wave: {self.current_wave + 1}/{self.max_waves}", True, WHITE)
        self.screen.blit(wave_text, (10, 30))

        # Game over
        if self.game_over:
            over_text = self.font.render("GAME OVER", True, RED)
            self.screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2))

        # Draw inventory bar at bottom
        self.player.inventory.draw(self.screen)

        if self.shop.active:
            self.shop.draw(self.screen, self.player)
        
        if self.casino.active:
            self.casino.draw(self.screen, self.player)

        # Draw startup message above inventory bar (small, discrete)
        if self.startup_message_active and self.startup_message_timer > 0:
            msg_font = get_pixel_font(32)
            msg_text = "THE GAME HAS STARTED : USE WASD TO NAVIGATE TO THE SHOP TO PROTECT YOUR KINGDOM!"
            
            # Create text surface
            text_surface = msg_font.render(msg_text, True, (255, 255, 0))
            text_surface.set_alpha(self.startup_message_alpha)
            
            # Draw text just above inventory bar
            text_x = SCREEN_WIDTH // 2 - text_surface.get_width() // 2
            text_y = SCREEN_HEIGHT - 130
            self.screen.blit(text_surface, (text_x, text_y))
        
        # Draw damage flash animation (red pulsate and edges)
        if self.damage_flash_timer > 0:
            # Calculate flash intensity (0 to 1)
            flash_intensity = self.damage_flash_timer / 0.3
            
            # Red edge effect
            edge_thickness = int(20 * flash_intensity)
            if edge_thickness > 0:
                pygame.draw.rect(self.screen, (255, 0, 0), (0, 0, SCREEN_WIDTH, edge_thickness))  # Top
                pygame.draw.rect(self.screen, (255, 0, 0), (0, SCREEN_HEIGHT - edge_thickness, SCREEN_WIDTH, edge_thickness))  # Bottom
                pygame.draw.rect(self.screen, (255, 0, 0), (0, 0, edge_thickness, SCREEN_HEIGHT))  # Left
                pygame.draw.rect(self.screen, (255, 0, 0), (SCREEN_WIDTH - edge_thickness, 0, edge_thickness, SCREEN_HEIGHT))  # Right
            
            # Red flash overlay with pulsate effect
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay_alpha = int(100 * flash_intensity)
            overlay.set_alpha(overlay_alpha)
            overlay.fill((255, 0, 0))
            self.screen.blit(overlay, (0, 0))

        # Draw wave announcements
        if self.wave_manager.show_announcement:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Announcement text with countdown
            announcement_font = get_pixel_font(72)
            small_font = get_pixel_font(48)
            
            announcement_text = announcement_font.render(self.wave_manager.announcement_text, True, (255, 255, 0))
            text_rect = announcement_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(announcement_text, text_rect)
            
            # Show countdown numbers with colors
            remaining_time = max(0, self.wave_manager.announcement_duration - self.wave_manager.announcement_timer)
            countdown = int(remaining_time) + 1
            
            if countdown > 0 and countdown <= 3:
                colors = {3: (255, 0, 0), 2: (255, 128, 0), 1: (0, 255, 0)}
                countdown_color = colors.get(countdown, (255, 255, 0))
                countdown_text = small_font.render(str(countdown), True, countdown_color)
                countdown_rect = countdown_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
                self.screen.blit(countdown_text, countdown_rect)

        # Draw game over or victory screen
        if self.game_over or self.game_won:
            self.game_over_timer += 1.0 / 60.0  # Approximate dt
            
            # Fade background to black - gradually increases
            fade_alpha = min(200, int((self.game_over_timer / 3.0) * 200))  # Fade over 3 seconds
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(fade_alpha)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Create slamming animation - scale and bounce
            time_offset = self.game_over_timer * 2  # Speed up the animation
            slam_scale = 1.0 + min(0.3, max(0, 1.0 - time_offset) * 0.3)  # Slam effect
            
            if self.game_over:
                # Game over text - red with slamming animation
                base_font_size = int(100 * slam_scale)
                game_over_font = get_pixel_font(base_font_size)
                game_over_text = game_over_font.render("YOU LOSE!!!!!!!!", True, (255, 0, 0))
                game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                self.screen.blit(game_over_text, game_over_rect)
                
                # Skill issue text - slightly smaller and lower
                skill_font_size = int(70 * slam_scale)
                skill_font = get_pixel_font(skill_font_size)
                skill_text = skill_font.render("SKILL ISSUE!!!!!!!!!", True, (255, 0, 0))
                skill_rect = skill_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
                self.screen.blit(skill_text, skill_rect)
            else:
                # Victory text - green with slamming animation
                base_font_size = int(100 * slam_scale)
                victory_font = get_pixel_font(base_font_size)
                victory_text = victory_font.render("VICTORY!!!!", True, (0, 255, 0))
                victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(victory_text, victory_rect)

        # ===== PROPER SCALING =====
        window_w, window_h = self.window.get_size()
        scale = min(
            window_w / SCREEN_WIDTH,
            window_h / SCREEN_HEIGHT
        )

        scaled_w = int(SCREEN_WIDTH * scale)
        scaled_h = int(SCREEN_HEIGHT * scale)

        scaled_surface = pygame.transform.scale(
            self.screen,
            (scaled_w, scaled_h)
        )

        # Center the game (letterboxing)
        x_offset = (window_w - scaled_w) // 2
        y_offset = (window_h - scaled_h) // 2

        self.window.fill(BLACK)
        self.window.blit(scaled_surface, (x_offset, y_offset))

        pygame.display.flip()

    # -----------------------------
    # Main Loop
    # -----------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            
            # Only update game logic if not game over/won
            if not self.game_over and not self.game_won:
                self.update(dt)
            
            self.draw()
            
            # Exit after 5 seconds of game over/victory animation
            if (self.game_over or self.game_won) and self.game_over_timer > 5.0:
                self.running = False
