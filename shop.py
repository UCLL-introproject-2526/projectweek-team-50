import pygame
from settings import GOLD, YELLOW, TILE_COLORS, TILE_PATH, get_pixel_font

class Shop:
    def __init__(self, screen_width, screen_height):
        self.active = False
        self.width = screen_width
        self.height = screen_height
        
        # UI Configuration
        self.font = get_pixel_font(24)
        self.title_font = get_pixel_font(40)
        self.overlay = pygame.Surface((self.width, self.height))
        self.overlay.set_alpha(200)
        self.overlay.fill((0, 0, 0))
        
        # Items for sale
        self.items = [
            {"name": "Goblin", "cost": 60, "id": "goblin", "desc": "MELEE | DMG: 18 | FIRE RATE: 0.50s | RANGE: 55"},
            {"name": "Elf", "cost": 90, "id": "elf", "desc": "MELEE | DMG: 26 | FIRE RATE: 0.55s | RANGE: 65"},
            {"name": "Knight", "cost": 130, "id": "knight", "desc": "MELEE | DMG: 40 | FIRE RATE: 0.85s | RANGE: 80 | ABILITY: Stun (first hit)"},
            {"name": "Archer", "cost": 170, "id": "archer", "desc": "RANGED | DMG: 32 | FIRE RATE: 0.65s | RANGE: 180"},
            {"name": "Wizard", "cost": 260, "id": "wizard", "desc": "RANGED | DMG: 42 | FIRE RATE: 0.80s | RANGE: 260 | ABILITY: Slow 0.5s"},
            {"name": "Fire Warrior", "cost": 350, "id": "firewarrior", "desc": "MELEE | DMG: 60 | FIRE RATE: 0.75s | RANGE: 110"},
            {"name": "Blood Mage", "cost": 500, "id": "bloodmage", "desc": "RANGED | DMG: 85 | FIRE RATE: 0.90s | RANGE: 340"}
        ]
        
        self.selected_index = 0
        self.input_cooldown = 0

    def toggle(self):
        self.active = not self.active
        self.selected_index = 0
        self.input_cooldown = 0

    def handle_input(self, player):
        """Navigation and buying logic"""
        keys = pygame.key.get_pressed()
        
        if self.input_cooldown > 0:
            self.input_cooldown -= 1
            return

        # Navigate
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.selected_index = (self.selected_index - 1) % len(self.items)
            self.input_cooldown = 10
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.selected_index = (self.selected_index + 1) % len(self.items)
            self.input_cooldown = 10

        # Buy
        if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
            self.buy_item(player)
            self.input_cooldown = 20
        
        # Close
        if keys[pygame.K_ESCAPE]:
            self.toggle()
            self.input_cooldown = 20

    def buy_item(self, player):
        item = self.items[self.selected_index]
        if player.gold >= item['cost']:
            # Try to add to inventory
            if player.inventory.add_item(item['id']):
                player.gold -= item['cost']
                self.toggle()  # close shop after buying
                print(f"Bought {item['name']}")
            else:
                print("Inventory full!")
        else:
            print("Not enough gold!")

    def apply_upgrade(self, player, item_id):
        if item_id == "heal":
            player.health = player.max_health
        elif item_id == "speed":
            # Lower move_delay means faster movement
            player.move_delay = max(0.05, player.move_delay - 0.02)
        elif item_id == "max_hp":
            player.max_health += 20
            player.health += 20

    def draw(self, screen, player):
        if not self.active:
            return

        def fit_text(font, text, max_width):
            if font.size(text)[0] <= max_width:
                return text
            ellipsis = "..."
            trimmed = text
            while trimmed and font.size(trimmed + ellipsis)[0] > max_width:
                trimmed = trimmed[:-1]
            return (trimmed + ellipsis) if trimmed else ellipsis

        # Create semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(210)
        overlay.fill((15, 15, 20))
        screen.blit(overlay, (0, 0))

        # Draw decorative border
        border_color = GOLD
        border_thickness = 3
        pygame.draw.rect(screen, border_color, (10, 10, self.width - 20, self.height - 20), border_thickness)
        
        # Inner decorative line
        pygame.draw.rect(screen, TILE_COLORS[TILE_PATH], (13, 13, self.width - 26, self.height - 26), 1)

        # Title
        title = self.title_font.render("⚔ SHOP ⚔", True, GOLD)
        title_rect = title.get_rect(center=(self.width // 2, 35))
        screen.blit(title, title_rect)
        
        # Decorative line under title
        pygame.draw.line(screen, GOLD, (60, 70), (self.width - 60, 70), 2)

        # Gold Display with icon-like styling
        gold_font = get_pixel_font(24)
        gold_text = gold_font.render(f"💰 Gold: {player.gold}", True, (255, 215, 0))
        gold_rect = gold_text.get_rect(center=(self.width // 2, 90))
        screen.blit(gold_text, gold_rect)

        # Instructions at top
        instr_font = get_pixel_font(16)
        instr = instr_font.render("Navigate with UP/DOWN • BUY with SPACE • CLOSE with ESC", True, (200, 190, 120))
        instr_rect = instr.get_rect(center=(self.width // 2, 125))
        screen.blit(instr, instr_rect)
        
        # Decorative separator
        pygame.draw.line(screen, TILE_COLORS[TILE_PATH], (60, 145), (self.width - 60, 145), 1)

        # Items - Card-based layout
        card_width = 350
        card_height = 70
        card_x = (self.width - card_width) // 2
        start_y = 170
        card_spacing = 85
        
        for i, item in enumerate(self.items):
            card_y = start_y + i * card_spacing
            
            is_selected = i == self.selected_index
            
            # Card background
            if is_selected:
                card_color = (50, 120, 180)
                border_color = YELLOW
                border_width = 3
                # Glow effect
                glow_rect = pygame.Rect(card_x - 5, card_y - 5, card_width + 10, card_height + 10)
                pygame.draw.rect(screen, (30, 70, 120), glow_rect, 1)
            else:
                card_color = (35, 45, 65)
                border_color = (80, 120, 160)
                border_width = 2
            
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            pygame.draw.rect(screen, card_color, card_rect)
            pygame.draw.rect(screen, border_color, card_rect, border_width)
            
            # Selection indicator
            if is_selected:
                pygame.draw.polygon(screen, YELLOW, 
                    [(card_x - 10, card_y + card_height // 2 - 5),
                     (card_x - 10, card_y + card_height // 2 + 5),
                     (card_x - 2, card_y + card_height // 2)])
            
            # Item name and cost (left side)
            name_font = get_pixel_font(22)
            color = YELLOW if is_selected else (230, 220, 180)
            name_text = name_font.render(fit_text(name_font, item['name'], card_width - 130), True, color)
            screen.blit(name_text, (card_x + 15, card_y + 8))
            
            # Cost (right side)
            cost_font = get_pixel_font(20)
            cost_color = (255, 215, 0) if player.gold >= item['cost'] else (200, 100, 100)
            cost_text = cost_font.render(f"${item['cost']}", True, cost_color)
            cost_rect = cost_text.get_rect(topright=(card_x + card_width - 15, card_y + 8))
            screen.blit(cost_text, cost_rect)
            
            # Description (bottom of card)
            desc_max_w = card_width - 30
            if is_selected:
                desc_font = get_pixel_font(16)
                desc_text = desc_font.render(fit_text(desc_font, item['desc'], desc_max_w), True, (200, 200, 200))
                screen.blit(desc_text, (card_x + 15, card_y + 38))
            else:
                # Show short info for non-selected
                desc_font = get_pixel_font(14)
                desc_text = desc_font.render(fit_text(desc_font, item['desc'], desc_max_w), True, (150, 150, 150))
                screen.blit(desc_text, (card_x + 15, card_y + 38))
        
        # Bottom instructions
        bottom_y = start_y + len(self.items) * card_spacing + 40
        instructions = [
            "Selected item details shown above",
            "Not enough gold? Defeat enemies to earn coins!"
        ]
        small_font = get_pixel_font(16)
        for i, instr in enumerate(instructions):
            instr_surf = small_font.render(instr, True, (180, 180, 180))
            screen.blit(instr_surf, (self.width // 2 - instr_surf.get_width() // 2, bottom_y + i * 25))