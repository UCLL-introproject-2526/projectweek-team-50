import pygame
from entities.entity import Entity
from entities.projectile import Projectile
from settings import BLUE

class Troop(Entity):
    def __init__(self, tile_pos, range_radius=160, fire_delay=0.6):
        super().__init__(tile_pos)

        self.range = range_radius
        self.fire_delay = fire_delay
        self.timer = 0.0

    def update(self, dt, enemies, projectiles):
        self.timer += dt
        if self.timer >= self.fire_delay:
            target = self.find_target(enemies)
            if target:
                projectiles.append(
                    Projectile(
                        self.rect.centerx,
                        self.rect.centery,
                        target
                    )
                )
                self.timer = 0.0

    def find_target(self, enemies):
        for e in enemies:
            dx = e.rect.centerx - self.rect.centerx
            dy = e.rect.centery - self.rect.centery
            if dx * dx + dy * dy <= self.range * self.range:
                return e
        return None

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect)
