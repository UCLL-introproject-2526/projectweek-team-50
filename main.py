import os
import pygame
from game import Game

def main():
    pygame.init()

    
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        music_path = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "Dark Fantasy Tiktok Song (slowed  reverb) Yamaha - Dorian concept.mp3",
        )
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.65)
        pygame.mixer.music.play(-1)
    except Exception:
        
        pass

    game = Game()
    game.run()
    pygame.quit()

if __name__ == "__main__":
    main()
