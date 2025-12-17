import pygame
from entities.enemy import Enemy

class WaveManager:
    def __init__(self, tilemap):
        self.tilemap = tilemap
        self.path_points = tilemap.get_path_points()

        self.current_wave = 0
        self.max_waves = 5
        self.wave_index = 0
        self.spawn_timer = 0.0
        self.spawn_delay = 1.8  # seconds between enemies

        self.enemies_to_spawn = 0
        self.wave_active = False

    def start_wave(self, wave_num):
        self.current_wave = wave_num
        self.wave_index = wave_num - 1
        enemy_count = 10 + self.wave_index * 5  # 10,15,20,25,30
        self.enemies_to_spawn = enemy_count
        self.spawn_timer = 0.0
        self.wave_active = True

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
        health = 100 + self.wave_index * 30  # 100,130,160,190,220
        speed = 1.0 + self.wave_index * 0.3  # tiles per second: 1.0,1.3,1.6,1.9,2.2
        enemies.append(
            Enemy(
                path_points=self.path_points,
                health=health,
                speed=speed,
                reward=10
            )
        )
