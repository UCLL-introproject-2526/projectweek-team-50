import pygame
from entities.entity import Entity
from entities.projectile import Projectile
from settings import RED, GREEN, BLUE

class Tower(Entity):
    def __init__(self, tile_pos, tower_type):
        super().__init__(tile_pos)
        self.type = tower_type
        if tower_type == 'knight':
            self.range = 60  # very short range (melee)
            self.damage = 50  # much stronger damage
            self.fire_delay = 0.6  # faster attack
            self.color = RED
        elif tower_type == 'archer':
            self.range = 160  # medium
            self.damage = 20
            self.fire_delay = 0.6
            self.color = GREEN
        elif tower_type == 'wizard':
            self.range = 240  # high
            self.damage = 15
            self.fire_delay = 0.5
            self.color = BLUE
        elif tower_type == 'musketeer':
            self.range = 280  # longest range
            self.damage = 12  # less than wizard
            self.fire_delay = 0.7
            self.color = (218, 165, 32)  # goldenrod
        
        self.timer = 0.0
        self.attack_timer = 0.0  # For melee animation

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
        if self.type == 'knight':
            # Knight uses instant melee attack instead of projectile
            target.health -= self.damage
            target.killed_by_tower = True
            self.attack_timer = 0.2  # Animation duration
            
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
            # Archer and Wizard use projectiles
            projectiles.append(
                Projectile(
                    self.rect.centerx,
                    self.rect.centery,
                    target,
                    damage=self.damage,
                    coin_manager=coin_manager,
                    tilemap=tilemap
                )
            )

    def draw(self, surface):
        if self.type == 'knight' and self.attack_timer > 0:
            # Knight attack animation: expand during attack
            expansion = int(20 * (1 - self.attack_timer / 0.2))
            expanded_rect = self.rect.inflate(expansion * 2, expansion * 2)
            pygame.draw.rect(surface, self.color, expanded_rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)