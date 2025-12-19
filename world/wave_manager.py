import pygame
from entities.enemy import Enemy

class WaveManager:
    def __init__(self, tilemap):
        self.tilemap = tilemap
        self.path_points = tilemap.get_path_points()

        self.current_wave = 0
        # Assets exist for waves 1-5.
        self.max_waves = 5
        self.wave_index = 0
        self.spawn_timer = 0.0
        self.spawn_delay = 1.8  # seconds between enemies

        self.enemies_to_spawn = 0
        self.spawning = False  # Are we currently spawning enemies?
        self.wave_finished = False  # Has wave ended (all enemies dead/reached castle)?
        
        # Announcement system
        self.show_announcement = False
        self.announcement_timer = 0.0
        self.announcement_duration = 3.0  # seconds to show announcement
        self.announcement_text = ""

    def start_wave(self, wave_num):
        self.current_wave = wave_num
        self.wave_index = wave_num - 1
        
        # Increase difficulty per wave and vary based on wave type
        if wave_num == 1:
            enemy_count = 20  # Wave 1: 10 standard enemies
        else:
            enemy_count = 25 + self.wave_index * 5  # Waves 2-5: 17, 22, 27, 32
        
        # Add 1 for the boss at the end
        self.enemies_to_spawn = enemy_count + 1
        self.spawn_timer = 0.0
        self.spawning = True
        self.wave_finished = False
        self.show_announcement = True
        self.announcement_timer = 0.0
        
        # Set announcement text
        if wave_num == 1:
            self.announcement_text = "WAVE 1 - GET READY!"
        else:
            self.announcement_text = f"WAVE {wave_num} - INCOMING!"

    def update(self, dt, enemies):
        # Update announcement
        if self.show_announcement:
            self.announcement_timer += dt
            if self.announcement_timer >= self.announcement_duration:
                self.show_announcement = False
        
        # Spawn enemies
        if self.spawning:
            if self.enemies_to_spawn <= 0:
                self.spawning = False
                return

            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_delay:
                self.spawn_timer = 0.0
                self.spawn_enemy(enemies)
                self.enemies_to_spawn -= 1
    
    def check_wave_complete(self, enemies):
        """Check if wave is complete: all enemies spawned, and either all died or reached castle"""
        if not self.spawning and len(enemies) == 0:
            self.wave_finished = True
            return True
        return False
    
    @property
    def wave_active(self):
        """Returns True if announcement is showing or wave is still spawning/active"""
        return self.show_announcement or self.spawning

    def spawn_enemy(self, enemies):
        # Check if this is the last enemy to spawn (the boss)
        is_boss = (self.enemies_to_spawn == 1)
        
        if is_boss:
            # Spawn boss enemy
            # Boss gets progressively stronger with each wave
            wave_num = self.current_wave
            
            # Base stats for boss
            health = 500 + (wave_num - 1) * 300  # 500, 800, 1100, 1400, 1700
            # Nerf specific bosses that are currently too tanky.
            if wave_num == 1:
                health = 350
            elif wave_num == 4:
                health = 1000
            reward = 100 + (wave_num - 1) * 50  # 100, 150, 200, 250, 300
            speed = 0.5  # Base speed
            
            # Last 2 waves (waves 4 and 5) have faster bosses
            if wave_num >= 4:
                speed = 1.2 + (wave_num - 4) * 0.3  # 1.2, 1.5
            
            enemies.append(
                Enemy(
                    path_points=self.path_points,
                    health=health,
                    speed=speed,
                    reward=reward,
                    enemy_type="boss",
                    wave_num=self.current_wave,
                )
            )
        elif self.current_wave == 1:
            # Wave 1: Standard enemies
            health = 100
            speed = 1.0
            reward = 10
            enemy_type = "standard"
            enemies.append(
                Enemy(
                    path_points=self.path_points,
                    health=health,
                    speed=speed,
                    reward=reward,
                    enemy_type=enemy_type,
                    wave_num=self.current_wave,
                )
            )
        else:
            # Waves 2-5: Mix of fast weak and slow strong enemies
            enemy_index = (len(enemies) - (self.enemies_to_spawn - 1)) % 3
            
            if enemy_index == 0:
                # Fast weak enemies (1 out of 3)
                health = 60 + self.wave_index * 10  # 70,80,90,100
                speed = 2.0 + self.wave_index * 0.4  # 2.4,2.8,3.2,3.6 (faster)
                reward = 15
                enemy_type = "fast_weak"
            else:
                # Slow strong enemies (2 out of 3)
                health = 150 + self.wave_index * 50  # 200,250,300,350
                speed = 0.6 + self.wave_index * 0.1  # 0.7,0.8,0.9,1.0 (slower)
                reward = 20
                enemy_type = "slow_strong"
            
            enemies.append(
                Enemy(
                    path_points=self.path_points,
                    health=health,
                    speed=speed,
                    reward=reward,
                    enemy_type=enemy_type,
                    wave_num=self.current_wave,
                )
            )
