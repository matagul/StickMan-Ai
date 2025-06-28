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
        if self.stage == 0:
            self.health = 80
        else:
            self.health = 40

    def update(self, dt, player_pos=None):
        self.time_alive += dt
        # Follow player if player_pos is given, else go to center
        target = player_pos if player_pos is not None else Vector2(400, 300)
        direction = target - self.pos
        if direction.length() > 1:
            direction = direction.normalize()
        self.pos += direction * self.speed * dt
        # Wrap enemy position
        if self.pos.x < 0:
            self.pos.x = 800
        elif self.pos.x > 800:
            self.pos.x = 0
        if self.pos.y < 0:
            self.pos.y = 600
        elif self.pos.y > 600:
            self.pos.y = 0
        new_enemies = []
        if self.time_alive >= 3 and self.stage < 2:
            # Only split if not dead
            if not self.dead:
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
        # Draw shadow
        shadow_surf = pygame.Surface((self.radius*2, self.radius), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0,0,0,70), (0, 0, self.radius*2, self.radius))
        shadow_rect = shadow_surf.get_rect(center=(int(self.pos.x), int(self.pos.y + self.radius)))
        surface.blit(shadow_surf, shadow_rect.topleft)
        # Draw 3D shaded sphere
        enemy_surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        for r in range(int(self.radius), 0, -1):
            shade = int(200 * (r/self.radius)**1.5)
            pygame.draw.circle(enemy_surf, (shade, 50, 50), (int(self.radius), int(self.radius)), r)
        # Highlight
        pygame.draw.circle(enemy_surf, (255, 180, 180, 90), (int(self.radius*0.7), int(self.radius*0.7)), int(self.radius*0.5))
        surface.blit(enemy_surf, (self.pos.x-self.radius, self.pos.y-self.radius))

    def check_attack(self, player):
        # If colliding with player, deal 10 damage
        if (self.pos - player.pos).length() < (self.radius + player.radius):
            player.take_damage(10)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.dead = True
        else:
            self.hit_timer = 1.0
