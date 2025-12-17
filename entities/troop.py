import pygame
from entities.entity import Entity
from entities.projectile import Projectile
from settings import BLUE

class Troop(Entity):
    def __init__(self, tile_pos, range_radius=160, fire_delay=0.6, damage=20, color=BLUE):
        super().__init__(tile_pos)

        self.range = range_radius
        self.fire_delay = fire_delay
        self.damage = damage
        self.color = color
        
        self.timer = 0.0

    def update(self, dt, enemies, projectiles, coin_manager=None, tilemap=None):
        self.timer += dt
        if self.timer >= self.fire_delay:
            target = self.find_target(enemies)
            if target:
                self.attack_target(target, projectiles, coin_manager, tilemap)
                self.timer = 0.0

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
        pygame.draw.rect(surface, self.color, self.rect)