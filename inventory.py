import pygame
from settings import SCREEN_WIDTH, TILE_SIZE, TEXT_COLOR, UI_BG_COLOR, BUTTON_COLOR, BUTTON_SELECTED_COLOR, TROOP_DATA


class Inventory:
    """Inventory system for storing towers/troops"""
    MAX_SLOTS = 5
    MAX_QUANTITY = 3
    
    def __init__(self):
        self.items = {}  # {tower_type: quantity}
        self.selected_slot = None  # Currently selected tower type (1-5 or None)
        self.font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 16)
        
    def add_item(self, tower_type):
        """Add a tower to inventory, returns True if successful"""
        if len(self.items) >= self.MAX_SLOTS and tower_type not in self.items:
            return False  # Inventory full
        
        if tower_type not in self.items:
            self.items[tower_type] = 0
        
        if self.items[tower_type] < self.MAX_QUANTITY:
            self.items[tower_type] += 1
            return True
        return False
    
    def remove_item(self, tower_type):
        """Remove one tower from inventory"""
        if tower_type in self.items:
            self.items[tower_type] -= 1
            if self.items[tower_type] <= 0:
                del self.items[tower_type]
                if self.selected_slot == tower_type:
                    self.selected_slot = None
            return True
        return False
    
    def select_slot(self, slot_number):
        """Select a slot (1-5)"""
        if slot_number < 1 or slot_number > self.MAX_SLOTS:
            return None
        
        # Get the slot_number-th tower type
        tower_types = list(self.items.keys())
        if slot_number - 1 < len(tower_types):
            self.selected_slot = tower_types[slot_number - 1]
            return self.selected_slot
        return None
    
    def get_selected_tower(self):
        """Get currently selected tower type"""
        return self.selected_slot
    
    def is_empty(self):
        """Check if inventory is empty"""
        return len(self.items) == 0
    
    def draw(self, surface):
        """Draw inventory bar at the bottom of screen"""
        # Inventory bar background
        bar_height = 75
        bar_y = surface.get_height() - bar_height - 80
        inventory_bg = pygame.Rect(0, bar_y, surface.get_width(), bar_height)
        pygame.draw.rect(surface, UI_BG_COLOR, inventory_bg)
        pygame.draw.line(surface, (100, 100, 100), (0, bar_y), (surface.get_width(), bar_y), 2)
        
        # Draw title
        title_text = self.font.render("INVENTORY", True, TEXT_COLOR)
        surface.blit(title_text, (10, bar_y + 5))
        
        # Draw inventory slots - CENTERED
        slot_width = 110
        slot_height = 55
        total_slots_width = self.MAX_SLOTS * slot_width + (self.MAX_SLOTS - 1) * 5
        slot_x_start = (surface.get_width() - total_slots_width) // 2
        slot_y = bar_y + 15
        
        tower_types = list(self.items.keys())
        
        for slot_num in range(1, self.MAX_SLOTS + 1):
            slot_x = slot_x_start + (slot_num - 1) * (slot_width + 5)
            
            if slot_num - 1 < len(tower_types):
                tower_type = tower_types[slot_num - 1]
                quantity = self.items[tower_type]
                
                # Highlight selected slot
                if self.selected_slot == tower_type:
                    slot_color = BUTTON_SELECTED_COLOR
                else:
                    slot_color = BUTTON_COLOR
                
                # Draw slot background
                slot_rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)
                pygame.draw.rect(surface, slot_color, slot_rect)
                pygame.draw.rect(surface, TEXT_COLOR, slot_rect, 2)
                
                # Get tower data for color indicator
                tower_data = TROOP_DATA.get(tower_type, {})
                tower_color = tower_data.get("color", (200, 200, 200))
                
                # Draw color indicator
                color_box = pygame.Rect(slot_x + 5, slot_y + 5, 12, 12)
                pygame.draw.rect(surface, tower_color, color_box)
                
                # Draw tower name
                name_text = self.small_font.render(tower_type.capitalize(), True, TEXT_COLOR)
                surface.blit(name_text, (slot_x + 20, slot_y + 3))
                
                # Draw quantity
                qty_font = pygame.font.SysFont('Arial', 14)
                qty_text = qty_font.render(f"x{quantity}", True, TEXT_COLOR)
                surface.blit(qty_text, (slot_x + 20, slot_y + 20))
                
                # Draw key hint
                key_text = self.small_font.render(f"[{slot_num}]", True, (150, 150, 150))
                surface.blit(key_text, (slot_x + slot_width - 28, slot_y + slot_height - 16))
            else:
                # Empty slot
                slot_rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)
                pygame.draw.rect(surface, (40, 40, 50), slot_rect)
                pygame.draw.rect(surface, (80, 80, 80), slot_rect, 2)
                
                # Draw key hint
                key_text = self.small_font.render(f"[{slot_num}]", True, (80, 80, 80))
                surface.blit(key_text, (slot_x + slot_width - 28, slot_y + slot_height - 16))
        
        # Draw place hint
        if self.selected_slot:
            place_text = self.small_font.render("Press P to place", True, (100, 255, 100))
            surface.blit(place_text, (surface.get_width() - 180, bar_y + 52))
