import pygame
from pygame.math import Vector2


class Player:
    def __init__(self):
        self.pos = Vector2(400, 300)
        self.speed = 200
        self.color = (200, 200, 200)
        self.radius = 15
        self.health = 100

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.pos.y -= self.speed * dt
        if keys[pygame.K_s]:
            self.pos.y += self.speed * dt
        if keys[pygame.K_a]:
            self.pos.x -= self.speed * dt
        if keys[pygame.K_d]:
            self.pos.x += self.speed * dt

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.pos, self.radius)
