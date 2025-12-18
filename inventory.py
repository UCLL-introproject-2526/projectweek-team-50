import pygame
from settings import SCREEN_WIDTH, TILE_SIZE, TEXT_COLOR, UI_BG_COLOR, BUTTON_COLOR, BUTTON_SELECTED_COLOR, TROOP_DATA, get_pixel_font


class Inventory:
    """Inventory system for storing towers/troops"""
    MAX_SLOTS = 5
    MAX_QUANTITY = 3
    
    def __init__(self):
        self.slots = [None] * self.MAX_SLOTS  # Fixed 5 slots, each can hold a tower_type
        self.quantities = {}  # {tower_type: quantity}
        self.selected_slot = None  # Currently selected slot index (0-4) or None
        self.font = get_pixel_font(20)
        self.small_font = get_pixel_font(16)
        
    def add_item(self, tower_type):
        """Add a tower to inventory, returns True if successful"""
        # If tower already exists, increment quantity
        for i, slot_tower in enumerate(self.slots):
            if slot_tower == tower_type:
                if self.quantities[tower_type] < self.MAX_QUANTITY:
                    self.quantities[tower_type] += 1
                    return True
                return False
        
        # Tower doesn't exist, find an empty slot
        for i, slot_tower in enumerate(self.slots):
            if slot_tower is None:
                self.slots[i] = tower_type
                self.quantities[tower_type] = 1
                return True
        
        return False  # All slots full
    
    def remove_item(self, tower_type):
        """Remove one tower from inventory"""
        if tower_type not in self.quantities:
            return False
        
        self.quantities[tower_type] -= 1
        if self.quantities[tower_type] <= 0:
            # Remove from quantities and slots only when quantity reaches 0
            del self.quantities[tower_type]
            for i, slot_tower in enumerate(self.slots):
                if slot_tower == tower_type:
                    self.slots[i] = None
                    # If this was the selected slot, clear selection
                    if self.selected_slot == i:
                        self.selected_slot = None
                    break
        return True
        return True
    
    def select_slot(self, slot_number):
        """Select a slot (1-5)"""
        if slot_number < 1 or slot_number > self.MAX_SLOTS:
            return None
        
        slot_index = slot_number - 1
        if self.slots[slot_index] is not None:
            self.selected_slot = slot_index
            return self.slots[slot_index]
        return None
    
    def get_selected_tower(self):
        """Get currently selected tower type"""
        if self.selected_slot is not None:
            return self.slots[self.selected_slot]
        return None
    
    def is_empty(self):
        """Check if inventory is empty"""
        return all(slot is None for slot in self.slots)
    
    def draw(self, surface):
        """Draw inventory bar at the bottom of screen with modern design"""
        # Inventory bar background - gradient effect with border
        bar_height = 90
        bar_y = int(surface.get_height() * 0.82)
        inventory_bg = pygame.Rect(0, bar_y, surface.get_width(), bar_height)
        
        # Modern dark background with subtle gradient
        pygame.draw.rect(surface, (25, 28, 35), inventory_bg)
        pygame.draw.line(surface, (100, 200, 255), (0, bar_y), (surface.get_width(), bar_y), 3)
        pygame.draw.line(surface, (80, 150, 220), (0, bar_y + bar_height - 1), (surface.get_width(), bar_y + bar_height - 1), 1)
        
        # Draw title with glow effect
        title_font = get_pixel_font(20)
        title_text = title_font.render("INVENTORY", True, (100, 200, 255))
        surface.blit(title_text, (15, bar_y + 5))
        
        # Draw gold amount
        gold_font = get_pixel_font(16)
        # Assuming we have access to player gold via a parent reference
        # For now, just show inventory status
        status_text = gold_font.render("Slots:", True, (180, 180, 180))
        surface.blit(status_text, (15, bar_y + 30))
        
        # Draw inventory slots - CENTERED with better styling
        slot_width = 70
        slot_height = 50
        slot_spacing = 8
        total_slots_width = self.MAX_SLOTS * slot_width + (self.MAX_SLOTS - 1) * slot_spacing
        slot_x_start = (surface.get_width() - total_slots_width) // 2
        slot_y = bar_y + 18
        
        for slot_num in range(self.MAX_SLOTS):
            slot_x = slot_x_start + slot_num * (slot_width + slot_spacing)
            tower_type = self.slots[slot_num]
            is_selected = self.selected_slot == slot_num
            
            # Slot background
            slot_rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)
            
            if is_selected and tower_type is not None:
                # Selected slot - bright blue glow
                pygame.draw.rect(surface, (100, 200, 255), slot_rect)
                pygame.draw.rect(surface, (200, 255, 255), slot_rect, 3)
            elif tower_type is not None:
                # Filled slot - dark blue
                pygame.draw.rect(surface, (40, 80, 120), slot_rect)
                pygame.draw.rect(surface, (100, 150, 200), slot_rect, 2)
            else:
                # Empty slot - dark gray
                pygame.draw.rect(surface, (35, 35, 45), slot_rect)
                pygame.draw.rect(surface, (70, 70, 80), slot_rect, 1)
            
            # Draw content
            if tower_type is not None:
                # Tower name
                name_text = self.small_font.render(tower_type.capitalize(), True, (255, 255, 255))
                text_rect = name_text.get_rect(center=(slot_x + slot_width // 2, slot_y + 15))
                surface.blit(name_text, text_rect)
                
                # Quantity
                qty = self.quantities.get(tower_type, 0)
                qty_text = self.small_font.render(f"x{qty}", True, (255, 200, 100))
                qty_rect = qty_text.get_rect(center=(slot_x + slot_width // 2, slot_y + 35))
                surface.blit(qty_text, qty_rect)
            else:
                # Slot number for empty slots
                num_text = self.small_font.render(str(slot_num + 1), True, (100, 100, 120))
                text_rect = num_text.get_rect(center=(slot_x + slot_width // 2, slot_y + 25))
                surface.blit(num_text, text_rect)
