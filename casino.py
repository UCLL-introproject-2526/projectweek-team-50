import pygame
import random
import math
from settings import GOLD, YELLOW, get_pixel_font

class Casino:
    def __init__(self, screen_width, screen_height):
        self.active = False
        self.width = screen_width
        self.height = screen_height
        self.fee = 150
        
        # UI Configuration
        self.font = get_pixel_font(24)
        self.title_font = get_pixel_font(40)
        self.overlay = pygame.Surface((self.width, self.height))
        self.overlay.set_alpha(200)
        self.overlay.fill((0, 0, 0))
        
        # Available troops to win
        self.available_troops = ["goblin", "elf", "knight", "archer", "wizard", "firewarrior", "bloodmage"]
        
        # Animation state
        self.animating = False
        self.animation_timer = 0.0
        self.animation_duration = 2.0  # 2 seconds for spin animation
        self.won_troop = None
        self.show_win = False
        self.win_timer = 0.0
        
        self.input_cooldown = 0

    def toggle(self):
        self.active = not self.active
        self.input_cooldown = 0
        self.animating = False
        self.animation_timer = 0.0
        self.show_win = False
        self.win_timer = 0.0

    def handle_input(self, player):
        """Play casino logic"""
        keys = pygame.key.get_pressed()
        
        if self.input_cooldown > 0:
            self.input_cooldown -= 1
            return

        # Play (spin)
        if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
            if not self.animating:
                self.play(player)
                self.input_cooldown = 20
        
        # Close
        if keys[pygame.K_ESCAPE]:
            self.toggle()
            self.input_cooldown = 20

    def play(self, player):
        """Pay fee and spin"""
        if player.gold >= self.fee:
            player.gold -= self.fee
            self.animating = True
            self.animation_timer = 0.0
            self.show_win = False
            self.win_timer = 0.0
            # Pick a random troop
            self.won_troop = random.choice(self.available_troops)
        else:
            print("Not enough gold!")

    def update(self, dt, player):
        """Update animation state"""
        if self.animating:
            self.animation_timer += dt
            
            # Animation finished
            if self.animation_timer >= self.animation_duration:
                self.animating = False
                self.show_win = True
                self.win_timer = 0.0
                
                # Add troop to inventory
                if self.won_troop and player:
                    player.inventory.add_item(self.won_troop)
        
        # Win display timer
        if self.show_win:
            self.win_timer += dt
            if self.win_timer >= 2.0:  # Show win message for 2 seconds
                self.show_win = False

    def draw(self, screen, player):
        if not self.active:
            return

        # Background
        screen.blit(self.overlay, (0, 0))

        # Title
        title = self.title_font.render("CASINO", True, (255, 215, 0))
        screen.blit(title, (self.width//2 - title.get_width()//2, 50))

        # Gold Display
        gold_text = self.font.render(f"Gold: {player.gold}", True, (255, 255, 0))
        screen.blit(gold_text, (self.width//2 - gold_text.get_width()//2, 120))

        # Fee Display
        fee_text = self.font.render(f"Entry Fee: {self.fee} Gold", True, (255, 0, 0))
        screen.blit(fee_text, (self.width//2 - fee_text.get_width()//2, 160))

        if self.animating:
            # Spinning animation
            progress = self.animation_timer / self.animation_duration
            
            # Randomly cycling through troops
            cycle_index = int((progress * 10) % len(self.available_troops))
            display_troop = self.available_troops[cycle_index]
            
            # Big spinning text
            spin_font = get_pixel_font(80)
            scale = 1.0 + abs(0.2 * (progress - 0.5))  # Pulsing effect
            spin_font = get_pixel_font(int(80 * scale))
            
            colors = [
                (255, 0, 0),
                (0, 255, 0),
                GOLD,
                YELLOW,
                (255, 0, 255)
            ]
            color = colors[int((progress * 5) % len(colors))]
            
            spin_text = spin_font.render(display_troop.upper(), True, color)
            screen.blit(spin_text, (self.width//2 - spin_text.get_width()//2, self.height//2 - 100))
            
            # Spinning indicator
            indicator_font = get_pixel_font(40)
            spinner = ["◐", "◓", "◑", "◒"][int((progress * 4) % 4)]
            spinner_text = indicator_font.render(spinner, True, (255, 255, 255))
            screen.blit(spinner_text, (self.width//2 - spinner_text.get_width()//2, self.height//2 + 50))

        elif self.show_win:
            # Win animation
            progress = self.win_timer / 2.0
            
            # Scale up animation
            scale = 1.0 + (1.0 - progress) * 0.5  # Grows then shrinks
            win_font = get_pixel_font(int(60 * scale))
            
            # Color animation (golden yellow)
            color_intensity = int(200 + 55 * (1.0 - progress))
            win_text = win_font.render(f"YOU WON: {self.won_troop.upper()}!", True, 
                                       (255, color_intensity, 0))
            screen.blit(win_text, (self.width//2 - win_text.get_width()//2, self.height//2 - 100))
            
            # Confetti effect (stars)
            for i in range(10):
                angle = (i / 10.0) * 6.28 + (progress * 2)
                x = self.width//2 + 300 * abs((1.0 - progress)) * math.cos(angle)
                y = self.height//2 + 200 * abs((1.0 - progress)) * math.sin(angle)
                pygame.draw.circle(screen, (255, 215, 0), (int(x), int(y)), 5)

        else:
            # Normal state
            play_text = self.font.render("Press SPACE to Play (Costs 150 Gold)", True, (0, 255, 0))
            screen.blit(play_text, (self.width//2 - play_text.get_width()//2, self.height//2 - 50))
            
            # Available troops display
            troops_text = self.font.render("Available Prizes:", True, (255, 255, 255))
            screen.blit(troops_text, (self.width//2 - troops_text.get_width()//2, self.height//2 + 50))
            
            troops_list = ", ".join([t.capitalize() for t in self.available_troops])
            troops_display = get_pixel_font(20).render(troops_list, True, (200, 200, 200))
            screen.blit(troops_display, (self.width//2 - troops_display.get_width()//2, self.height//2 + 100))

        # Instructions
        instructions = [
            "Press SPACE or ENTER to play (or spin again if already won)",
            "Press ESC to close casino"
        ]
        instr_font = get_pixel_font(18)
        instr_y = self.height - 100
        for instr in instructions:
            instr_surf = instr_font.render(instr, True, (255, 255, 255))
            screen.blit(instr_surf, (self.width//2 - instr_surf.get_width()//2, instr_y))
            instr_y += 25
