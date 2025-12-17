import pygame
from settings import *
from shop import Shop
from shopkeeper import Shopkeeper
from coins import CoinManager

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
        self.player.selected_tower = None
        self.player.gold = 100

        # Coin system
        self.coin_manager = CoinManager()

        # Castle
        self.castle_hp = 100
        self.castle_max_hp = 100
        self.game_over = False

        # Wave system
        self.wave_manager = WaveManager(self.tilemap)
        self.current_wave = 0
        self.max_waves = 5
        self.wave_manager.start_wave(self.current_wave)

        # Game state
        self.game_over = False

        # Shop system
        self.shop = Shop(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.shopkeeper = Shopkeeper(tile_pos=(12, 20), tile_size=TILE_SIZE)

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
                    elif self.shop.active:
                        self.shop.toggle()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass  # removed troop placement


    # -----------------------------
    # Update
    # -----------------------------
    def update(self, dt):
        if self.shop.active:
            self.shop.handle_input(self.player)
            return  # pause game logic

        self.player.update(dt, self.tilemap, self.coin_manager, self)

        # Tower placement
        if not self.shop.active:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_p] and self.player.selected_tower:
                tx, ty = self.player.tile_x, self.player.tile_y
                if not self.tilemap.is_blocked(tx, ty) and not self.tilemap.is_path(tx, ty):
                    from entities.tower import Tower
                    self.towers.append(Tower((tx, ty), self.player.selected_tower))
                    self.player.selected_tower = None

        # Enemies
        self.wave_manager.update(dt, self.enemies)

        # Start next wave if current ended
        if not self.wave_manager.wave_active and self.wave_manager.current_wave < self.wave_manager.max_waves:
            self.wave_manager.start_wave(self.wave_manager.current_wave + 1)
        for enemy in self.enemies:
            enemy.update(dt)

        # Check game over
        if self.castle_hp <= 0:
            self.game_over = True

        # Wave progression
        if not self.wave_manager.wave_active and not self.game_over:
            self.current_wave += 1
            if self.current_wave < self.max_waves:
                self.wave_manager.start_wave(self.current_wave)

        # Towers
        for tower in self.towers:
            tower.update(dt, self.enemies, self.projectiles)

        # Projectiles
        for projectile in self.projectiles:
            projectile.update(dt)

        # Handle dead enemies (drop coins) and enemies reaching castle
        for enemy in self.enemies:
            if enemy.finished or enemy.health <= 0:
                if enemy.health > 0:  # reached castle
                    self.castle_hp -= 1
                # Drop coins at enemy's position
                tx = enemy.tile_x
                ty = enemy.tile_y
                # Spawn 2-3 coins, each 5-10 TL, but adjust to reward
                import random
                for _ in range(random.randint(2, 3)):
                    value = min(10, max(5, enemy.reward // 3))  # roughly based on reward
                    self.coin_manager.add_coin_at_tile(tx, ty, value)
                enemy.dead_handled = True

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

        for projectile in self.projectiles:
            projectile.draw(self.screen)
        
        # Draw coins
        self.coin_manager.draw(self.screen)

        self.coin_manager.draw(self.screen)

        self.shopkeeper.draw(self.screen, self.player)

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

        if self.shop.active:
            self.shop.draw(self.screen, self.player)

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
        while self.running and not self.game_over:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            self.update(dt)
            self.draw()
