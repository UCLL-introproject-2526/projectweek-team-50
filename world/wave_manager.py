import pygame
from entities.enemy import Enemy

class WaveManager:
    def __init__(self, tilemap):
        self.tilemap = tilemap
        self.path_points = tilemap.get_path_points()

        self.wave_index = 0
        self.spawn_timer = 0.0
        self.spawn_delay = 1.8  # seconds between enemies

        self.enemies_to_spawn = 0
        self.wave_active = False

    def start_wave(self, enemy_count):
        self.enemies_to_spawn = enemy_count
        self.spawn_timer = 0.0
        self.wave_active = True
        self.wave_index += 1

    def update(self, dt, enemies):
        if not self.wave_active:
            return

        if self.enemies_to_spawn <= 0:
            self.wave_active = False
            return

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_timer = 0.0
            self.spawn_enemy(enemies)
            self.enemies_to_spawn -= 1

    def spawn_enemy(self, enemies):
        enemies.append(
            Enemy(
                path_points=self.path_points,
                health=100 + self.wave_index * 20,
                speed=80,
                reward=10
            )
        )
