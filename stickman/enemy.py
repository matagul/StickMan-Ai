import pygame
from pygame.math import Vector2
import random


class Enemy:
    def __init__(self, pos=None, stage=0):
        self.pos = Vector2(pos or (random.randint(50, 750), random.randint(50, 550)))
        self.stage = stage  # 0 original, 1 first split, 2 second split
        self.speed = 120 + 20 * stage
        self.radius = max(5, 20 - stage * 5)
        self.color = (200, 50, 50)
        self.time_alive = 0
        self.dead = False

    def update(self, dt):
        self.time_alive += dt
        direction = Vector2(400, 300) - self.pos
        if direction.length() > 1:
            direction = direction.normalize()
        self.pos += direction * self.speed * dt

        new_enemies = []
        if self.time_alive >= 3 and self.stage < 2:
            self.dead = True
            if self.stage == 0:
                new_enemies = [
                    Enemy(self.pos + (10, 0), 1),
                    Enemy(self.pos - (10, 0), 1),
                ]
            elif self.stage == 1:
                new_enemies = [
                    Enemy(self.pos + (10, 0), 2),
                    Enemy(self.pos - (10, 0), 2),
                    Enemy(self.pos + (0, 10), 2),
                    Enemy(self.pos - (0, 10), 2),
                ]
        return new_enemies

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.pos, self.radius)
