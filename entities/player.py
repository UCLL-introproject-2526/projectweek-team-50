import pygame
import math
from settings import WHITE

class Player:
    def __init__(self, position, size, shape="rect"):
        self.position = pygame.Vector2(position)
        self.shape = shape

        self.speed = 300
        self.velocity = pygame.Vector2(0, 0)

        self.size = size
        self.rect = pygame.Rect(
            self.position.x,
            self.position.y,
            size[0],
            size[1]
        )   

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.velocity.x = 0
        self.velocity.y = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity.x = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity.x = 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.velocity.y = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.velocity.y = 1


        # Normalize to prevent diagonal speed boost
        if self.velocity.length_squared() > 0:
            self.velocity = self.velocity.normalize()



    def update(self, dt):
        self.handle_input()
        self.position += self.velocity * self.speed * dt
        self.rect.topleft = (int(self.position.x), int(self.position.y))


    def draw(self, surface):
        if self.shape == "rect":
            pygame.draw.rect(surface, WHITE, self.rect)
        else:
            pygame.draw.circle(
                surface,
                WHITE,
                self.rect.center,
                self.radius
            )
