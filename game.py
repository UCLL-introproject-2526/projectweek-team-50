import pygame
from settings import *
from entities.player import Player
from world.tilemap import TileMap


class Game:
    def __init__(self):
        # Create the actual window FIRST
        self.window = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.RESIZABLE
        )
        pygame.display.set_caption(TITLE)

        # Fixed logical render surface
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Now this is safe
        self.window_size = self.window.get_size()

        self.clock = pygame.time.Clock()
        self.running = True

        self.tilemap = TileMap()

        self.player = Player(
            position=(100, 300),
            size=(50, 50)
        )

        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.VIDEORESIZE:
                self.window = pygame.display.set_mode(
                    (event.w, event.h),
                    pygame.RESIZABLE
                )
                self.window_size = (event.w, event.h)


    def update(self, dt):
        self.player.update(dt)

    def draw(self):
        # Draw EVERYTHING to the logical surface
        self.screen.fill(BG_COLOR)

        self.tilemap.draw(self.screen)
        self.player.draw(self.screen)

        # Scale to window size
        scaled_surface = pygame.transform.scale(
            self.screen,
            self.window_size
        )

        self.window.blit(scaled_surface, (0, 0))
        pygame.display.flip()


    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            self.update(dt)
            self.draw()
