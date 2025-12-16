import pygame
from settings import *
from entities.player import Player
from world.tilemap import TileMap


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.tilemap = TileMap()

        self.player = Player(
            position=(100, 300),
            size=(50, 50))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, dt):
        self.player.update(dt)

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.tilemap.draw(self.screen)
        self.player.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            self.update(dt)
            self.draw()
