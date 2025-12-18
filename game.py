import pygame
from settings import *
from shop import Shop
from shopkeeper import Shopkeeper
from casino import Casino
from casino_keeper import CasinoKeeper
from coins import CoinManager, handle_death

from entities.player import Player
from entities.troop import Troop
from entities.castle import Castle
from world.tilemap import TileMap
from world.wave_manager import WaveManager


level = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]


class Game:
    def __init__(self):
        # Window
        self.window = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.RESIZABLE
        )
        pygame.display.set_caption(TITLE)

        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.window_size = self.window.get_size()

        self.clock = pygame.time.Clock()
        self.running = True

        # Font
        self.font = pygame.font.SysFont(None, 24)

        # Font for UI
        self.font = pygame.font.SysFont(None, 24)
        
        # Font for announcements
        self.announcement_font = pygame.font.SysFont(None, 60)

        # World
        self.tilemap = TileMap(level)

        # Entities
        self.player = Player(tile_pos=(1, 1))
        self.enemies = []
        self.towers = []
        self.projectiles = []
        
        # Coin system
        self.coin_manager = CoinManager()

        # Player
        self.player.gold = 100

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
    def draw(self):
        self.screen.fill(BG_COLOR)

        self.tilemap.draw(self.screen)
        self.player.draw(self.screen)

        # Draw castle HP bar
        castle_x = 11 * TILE_SIZE + TILE_SIZE // 2
        castle_y = 6 * TILE_SIZE
        bar_width = 50
        bar_height = 5
        bar_x = castle_x - bar_width // 2
        bar_y = castle_y - 10
        pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
        if self.castle_max_hp > 0:
            hp_ratio = self.castle_hp / self.castle_max_hp
            pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, bar_width * hp_ratio, bar_height))

        for tower in self.towers:
            tower.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)
            
            # Draw health indicator above boss enemies
            if enemy.enemy_type == "boss":
                # Full health bar for boss
                bar_width = 60
                bar_height = 8
                bar_x = enemy.rect.centerx - bar_width // 2
                bar_y = enemy.rect.top - 20
                
                # Background bar
                pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
                
                # Health bar
                if enemy.max_health > 0:
                    health_ratio = max(0, enemy.health / enemy.max_health)
                    health_color = (0, 255, 0) if health_ratio > 0.5 else (255, 255, 0) if health_ratio > 0.2 else (255, 0, 0)
                    pygame.draw.rect(self.screen, health_color, (bar_x, bar_y, bar_width * health_ratio, bar_height))
                
                # Border
                pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
            
            # Draw warning indicator for slow enemies
            if enemy.enemy_type == "slow_strong":
                # Small warning icon
                pygame.draw.circle(self.screen, (200, 50, 200), (enemy.rect.centerx + 15, enemy.rect.centery - 15), 5)
                pygame.draw.circle(self.screen, (255, 255, 255), (enemy.rect.centerx + 15, enemy.rect.centery - 15), 5, 1)

        for projectile in self.projectiles:
            projectile.draw(self.screen)
        
        # Draw coins
        self.coin_manager.draw(self.screen)

        self.coin_manager.draw(self.screen)

        self.shopkeeper.draw(self.screen, self.player)
        self.casino_keeper.draw(self.screen, self.player)

        # Draw money
        money_text = self.font.render(f"Money: {self.player.gold} TL", True, WHITE)
        self.screen.blit(money_text, (SCREEN_WIDTH//2 - money_text.get_width()//2, 10))

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
            msg_font = pygame.font.Font(None, 32)
            msg_text = "THE GAME HAS STARTED : USE WASD TO NAVIGATE TO THE SHOP TO PROTECT YOUR KINGDOM!"
            
            # Create text surface
            text_surface = msg_font.render(msg_text, True, (255, 255, 0))
            text_surface.set_alpha(self.startup_message_alpha)
            
            # Draw text just above inventory bar
            text_x = SCREEN_WIDTH // 2 - text_surface.get_width() // 2
            text_y = SCREEN_HEIGHT - 130
            self.screen.blit(text_surface, (text_x, text_y))

        # Draw wave announcements
        if self.wave_manager.show_announcement:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Announcement text with countdown
            announcement_font = pygame.font.Font(None, 72)
            small_font = pygame.font.Font(None, 48)
            
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
                game_over_font = pygame.font.Font(None, base_font_size)
                game_over_text = game_over_font.render("YOU LOSE!!!!!!!!", True, (255, 0, 0))
                game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                self.screen.blit(game_over_text, game_over_rect)
                
                # Skill issue text - slightly smaller and lower
                skill_font_size = int(70 * slam_scale)
                skill_font = pygame.font.Font(None, skill_font_size)
                skill_text = skill_font.render("SKILL ISSUE!!!!!!!!!", True, (255, 0, 0))
                skill_rect = skill_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
                self.screen.blit(skill_text, skill_rect)
            else:
                # Victory text - green with slamming animation
                base_font_size = int(100 * slam_scale)
                victory_font = pygame.font.Font(None, base_font_size)
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
