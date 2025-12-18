import random
import pygame
import math
from settings import TILE_SIZE, get_pixel_font

def handle_death(enemy, coin_manager, tilemap):
    if enemy.dead_handled: 
        return
    
    # Only drop coins if the enemy was actually killed (health <= 0)
    if enemy.health > 0:
        enemy.dead_handled = True
        return
    
    tx = enemy.tile_x
    ty = enemy.tile_y

    # Determine coin drop based on enemy type
    if hasattr(enemy, 'enemy_type') and enemy.enemy_type == "boss":
        # Boss always drops 5-7 coins worth 10 TL each
        num_coins = random.randint(5, 7)
    else:
        # Regular enemies drop 2-3 coins worth 5-10 TL each
        num_coins = random.randint(2, 3)

    # Spawn coins with parabolic animation - each coin gets random value
    for _ in range(num_coins):
        # Randomize value for each coin individually
        if hasattr(enemy, 'enemy_type') and enemy.enemy_type == "boss":
            value = 10  # Boss coins always worth 10
        else:
            value = random.randint(5, 10)  # Regular coins random 5-10
        
        # Random offset within 3-tile radius for landing position
        offset_x = random.randint(-3, 3)
        offset_y = random.randint(-3, 3)
        
        coin_tx = tx + offset_x
        coin_ty = ty + offset_y
        
        # Add animated coin that will drop to the target position
        coin_manager.add_animated_coin(tx, ty, coin_tx, coin_ty, value)

    enemy.dead_handled = True

# Coin with parabolic animation
class AnimatedCoin:
    def __init__(self, start_tx, start_ty, end_tx, end_ty, value):
        self.start_tx = start_tx
        self.start_ty = start_ty
        self.end_tx = end_tx
        self.end_ty = end_ty
        self.value = value
        
        # Animation parameters
        self.duration = 0.6  # Duration in seconds
        self.elapsed = 0.0
        self.completed = False
        
        # Current position
        self.x = start_tx * TILE_SIZE + TILE_SIZE // 2
        self.y = start_ty * TILE_SIZE + TILE_SIZE // 2
        
        # Target position in pixels
        self.target_x = end_tx * TILE_SIZE + TILE_SIZE // 2
        self.target_y = end_ty * TILE_SIZE + TILE_SIZE // 2
    
    def update(self, dt):
        if self.completed:
            return
        
        self.elapsed += dt
        progress = min(1.0, self.elapsed / self.duration)
        
        if progress >= 1.0:
            self.completed = True
            self.x = self.target_x
            self.y = self.target_y
            return
        
        # Parabolic trajectory
        # Horizontal: linear interpolation
        self.x = self.start_tx * TILE_SIZE + TILE_SIZE // 2
        self.x += (self.target_x - (self.start_tx * TILE_SIZE + TILE_SIZE // 2)) * progress
        
        # Vertical: parabolic (goes up then down)
        # Peak is at progress = 0.5
        self.y = self.start_ty * TILE_SIZE + TILE_SIZE // 2
        vertical_distance = self.target_y - (self.start_ty * TILE_SIZE + TILE_SIZE // 2)
        
        # Parabolic formula: creates arc upward then downward
        arc_height = -80  # How high the coin goes
        vertical_offset = arc_height * (4 * progress * (1 - progress))
        
        self.y += vertical_distance * progress + vertical_offset
    
    def draw(self, surface, offset: tuple[int, int] = (0, 0)):
        GOLD = (255, 215, 0)
        DARK_GOLD = (184, 134, 11)
        size = TILE_SIZE // 3
        ox, oy = offset
        
        # Draw coin as circle
        pygame.draw.circle(surface, GOLD, (int(self.x) + ox, int(self.y) + oy), size // 2)
        pygame.draw.circle(surface, DARK_GOLD, (int(self.x) + ox, int(self.y) + oy), size // 2, 2)
        
        # Draw value text if landed
        if self.completed:
            font = get_pixel_font(16)
            text = font.render(str(self.value), True, GOLD)
            surface.blit(text, (int(self.x) + ox - 8, int(self.y) + oy - 8))

# Floating text that drifts upward and fades
class FloatingText:
    def __init__(self, tx, ty, value):
        self.x = tx * TILE_SIZE + TILE_SIZE // 2
        self.y = ty * TILE_SIZE + TILE_SIZE // 2
        self.value = value
        
        # Animation parameters
        self.duration = 1.0  # seconds to drift and fade
        self.elapsed = 0.0
        self.completed = False
        self.drift_speed = 30  # pixels per second upward
    
    def update(self, dt):
        if self.completed:
            return
        
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.completed = True
            return
        
        # Drift upward
        self.y -= self.drift_speed * dt
    
    def draw(self, surface):
        if self.completed:
            return
        
        # Calculate opacity (fade out)
        progress = self.elapsed / self.duration
        alpha = int(255 * (1 - progress))  # Fade from 255 to 0
        
        # Create text surface with fade
        font = get_pixel_font(16)
        text_surface = font.render(str(self.value), True, (255, 215, 0))  # Gold
        text_surface.set_alpha(alpha)
        
        # Draw at current position
        surface.blit(text_surface, (int(self.x) - 8, int(self.y) - 8))

# CoinManager with animation support
class CoinManager:
    def __init__(self):
        self.coins = {}  # {(tx, ty): value} - static coins
        self.animated_coins = []  # List of AnimatedCoin objects
        self.floating_texts = []  # List of FloatingText objects
    
    def add_coin_at_tile(self, tx, ty, value):
        """Add a static coin at a tile"""
        if (tx, ty) not in self.coins:
            self.coins[(tx, ty)] = value
    
    def add_animated_coin(self, start_tx, start_ty, end_tx, end_ty, value):
        """Add a coin with parabolic animation"""
        coin = AnimatedCoin(start_tx, start_ty, end_tx, end_ty, value)
        self.animated_coins.append(coin)
    
    def update(self, dt):
        """Update all animated coins and floating text"""
        for coin in self.animated_coins:
            coin.update(dt)
        
        # Update floating text
        for text in self.floating_texts:
            text.update(dt)
        
        # Move completed coins to static coins
        completed = []
        for i, coin in enumerate(self.animated_coins):
            if coin.completed:
                self.coins[(coin.end_tx, coin.end_ty)] = coin.value
                completed.append(i)
        
        # Remove completed animated coins (in reverse order to maintain indices)
        for i in reversed(completed):
            self.animated_coins.pop(i)
        
        # Remove completed floating text
        self.floating_texts = [t for t in self.floating_texts if not t.completed]
    
    def collect_at_tile(self, tx, ty):
        value = self.coins.pop((tx, ty), 0)
        if value > 0:
            # Spawn floating text at collection point
            self.floating_texts.append(FloatingText(tx, ty, value))
        return value

    def collect_nearby(self, tx, ty, radius=1):
        """Collect and remove all coins within Chebyshev distance `radius` of (tx,ty).
        Returns the total value collected."""
        total = 0
        # gather keys to remove to avoid modifying dict during iteration
        to_remove = []
        for (cx, cy), val in list(self.coins.items()):
            if max(abs(cx - tx), abs(cy - ty)) <= radius:
                total += val
                to_remove.append((cx, cy))
                # Spawn floating text for each collected coin
                self.floating_texts.append(FloatingText(cx, cy, val))

        for k in to_remove:
            self.coins.pop(k, None)

        return total
    
    def draw(self, surface, offset: tuple[int, int] = (0, 0)):
        GOLD = (255, 215, 0)
        size = TILE_SIZE // 3
        ox, oy = offset
        
        # Draw static coins
        for (tx, ty), value in self.coins.items():
            x = tx * TILE_SIZE + (TILE_SIZE - size) // 2 + ox
            y = ty * TILE_SIZE + (TILE_SIZE - size) // 2 + oy
            pygame.draw.rect(surface, GOLD, (x, y, size, size))
            pygame.draw.rect(surface, (184, 134, 11), (x, y, size, size), 1)
        
        # Draw animated coins
        for coin in self.animated_coins:
            coin.draw(surface, offset=offset)
        
        # Draw floating text
        for text in self.floating_texts:
            text.draw(surface)

