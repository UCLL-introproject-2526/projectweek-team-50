import pygame

class Shop:
    def __init__(self, screen_width, screen_height):
        self.active = False
        self.width = screen_width
        self.height = screen_height
        
        # UI Configuration
        self.font = pygame.font.SysFont('Arial', 24)
        self.title_font = pygame.font.SysFont('Arial', 40, bold=True)
        self.overlay = pygame.Surface((self.width, self.height))
        self.overlay.set_alpha(200)
        self.overlay.fill((0, 0, 0))
        
        # Items for sale
        self.items = [
            {"name": "Knight Tower", "cost": 50,  "id": "knight", "desc": "Melee tower, small range"},
            {"name": "Archer Tower", "cost": 100, "id": "archer", "desc": "Ranged tower, medium range"},
            {"name": "Wizard Tower", "cost": 200, "id": "wizard", "desc": "Magic tower, high range"},
            {"name": "Musketeer Tower", "cost": 250, "id": "musketeer", "desc": "Longest range, lower damage"}
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

        # Background
        screen.blit(self.overlay, (0, 0))

        # Title
        title = self.title_font.render("SHOP", True, (255, 215, 0))
        screen.blit(title, (self.width//2 - title.get_width()//2, 50))

        # Gold Display
        gold_text = self.font.render(f"Gold: {player.gold}", True, (255, 255, 0))
        screen.blit(gold_text, (self.width//2 - gold_text.get_width()//2, 100))

        # Items
        start_y = 180
        for i, item in enumerate(self.items):
            color = (255, 255, 255)
            prefix = "   "
            if i == self.selected_index:
                color = (0, 255, 0)
                prefix = " > "
            
            # Item Text
            text_str = f"{prefix}{item['name']}  [${item['cost']}]"
            text_surf = self.font.render(text_str, True, color)
            screen.blit(text_surf, (self.width//2 - text_surf.get_width()//2, start_y + i * 60))
            
            # Description
            if i == self.selected_index:
                desc_surf = pygame.font.SysFont('Arial', 20).render(item['desc'], True, (200, 200, 200))
                screen.blit(desc_surf, (self.width//2 - desc_surf.get_width()//2, start_y + i * 60 + 30))
        
        # Instructions
        instructions = [
            "Use UP/DOWN arrows or W/S to navigate",
            "Press SPACE or ENTER to buy selected item",
            "Press ESC to close shop"
        ]
        instr_font = pygame.font.SysFont('Arial', 18)
        instr_y = start_y + len(self.items) * 60 + 50
        for instr in instructions:
            instr_surf = instr_font.render(instr, True, (255, 255, 255))
            screen.blit(instr_surf, (self.width//2 - instr_surf.get_width()//2, instr_y))
            instr_y += 25