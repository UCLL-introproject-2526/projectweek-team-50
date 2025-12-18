import pygame
from entities.entity import Entity
from entities.projectile import Projectile
from settings import RED, GREEN, BLUE

class Tower(Entity):
    def __init__(self, tile_pos, tower_type):
        super().__init__(tile_pos)
        self.type = tower_type
        if tower_type == 'knight':
            self.range = 60
            self.damage = 50
            self.fire_delay = 0.6
            self.color = RED
            self.slow_duration = 0
            self.stun_duration = 0
            self.projectile_speed = 4.0
        elif tower_type == 'jester':
            self.range = 55
            self.damage = 30
            self.fire_delay = 1.0
            self.color = (200, 50, 200)
            self.slow_duration = 0
            self.stun_duration = 1.0
            self.projectile_speed = 4.0
        elif tower_type == 'archer':
            self.range = 160
            self.damage = 20
            self.fire_delay = 0.6
            self.color = GREEN
            self.slow_duration = 0
            self.stun_duration = 0
            self.projectile_speed = 4.0
        elif tower_type == 'wizard':
            self.range = 240
            self.damage = 15
            self.fire_delay = 0.5
            self.color = BLUE
            self.slow_duration = 0.5
            self.stun_duration = 0
            self.projectile_speed = 4.0
        elif tower_type == 'cannon':
            self.range = 300
            self.damage = 80
            self.fire_delay = 3.5
            self.color = (60, 60, 60)
            self.slow_duration = 0
            self.stun_duration = 0
            self.projectile_speed = 8.0
        elif tower_type == 'musketeer':
            self.range = 280
            self.damage = 18
            self.fire_delay = 0.7
            self.color = (218, 165, 32)
            self.slow_duration = 0
            self.stun_duration = 0
            self.projectile_speed = 4.0
        
        self.timer = 0.0
        self.attack_timer = 0.0

    def update(self, dt, enemies, projectiles, coin_manager=None, tilemap=None):
        self.timer += dt
        if self.attack_timer > 0:
            self.attack_timer -= dt
        
        if self.timer >= self.fire_delay:
            target = self.find_target(enemies)
            if target:
                self.attack_target(target, projectiles, coin_manager, tilemap)
                self.timer = 0.0

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
        if self.type == 'knight' or self.type == 'jester':
            # Knight and Jester use instant melee attack instead of projectile
            target.health -= self.damage
            target.killed_by_tower = True
            self.attack_timer = 0.2
            
            # Jester stuns the enemy only on first hit
            if self.type == 'jester' and not target.has_been_stunned:
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
            projectiles.append(
                Projectile(
                    self.rect.centerx,
                    self.rect.centery,
                    target,
                    damage=self.damage,
                    slow_duration=self.slow_duration,
                    projectile_speed=self.projectile_speed,
                    coin_manager=coin_manager,
                    tilemap=tilemap
                )
            )

    def draw(self, surface):
        if (self.type == 'knight' or self.type == 'jester') and self.attack_timer > 0:
            # Melee attack animation: expand during attack
            expansion = int(20 * (1 - self.attack_timer / 0.2))
            expanded_rect = self.rect.inflate(expansion * 2, expansion * 2)
            pygame.draw.rect(surface, self.color, expanded_rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)