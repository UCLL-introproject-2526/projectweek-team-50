import pygame
from game import Game

pygame.init()
try:
    game = Game()
    # perform one update/draw cycle
    game.handle_events()
    game.update(1/60)
    game.draw()
    print('SMOKE_OK')
finally:
    pygame.quit()
