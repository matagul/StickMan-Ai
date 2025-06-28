import pygame
from pygame.math import Vector2
from weapon import DEFAULT_WEAPONS
import time
import math


class Player:
    def __init__(self):
        self.pos = Vector2(400, 300)
        self.speed = 200
        self.color = (200, 200, 200)
        self.radius = 15
        self.health = 100
        self.weapon = DEFAULT_WEAPONS[0]  # Start with Pistol
        self.bullets = []  # List of (pos, direction)
        self.bullet_speed = 400
        self.last_hit_time = 0
        self.hit_cooldown = 1.0  # seconds
        self.angle = 0  # Facing angle in radians
        self.size = (40, 20)  # width, height
        self.last_shot_time = 0
        self.shoot_cooldown = 0.3
        self.rocket_ready = False
        self.velocity = Vector2(0, 0)
        self.acceleration = 600
        self.max_speed = 350
        self.friction = 0.98

    def update(self, dt):
        keys = pygame.key.get_pressed()
        acc = Vector2(0, 0)
        if keys[pygame.K_w]:
            acc.y -= 1
        if keys[pygame.K_s]:
            acc.y += 1
        if keys[pygame.K_a]:
            acc.x -= 1
        if keys[pygame.K_d]:
            acc.x += 1
        if acc.length() > 0:
            acc = acc.normalize() * self.acceleration * dt
            self.velocity += acc
        self.velocity *= self.friction
        if self.velocity.length() > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed
        self.pos += self.velocity * dt
        # Update angle to face mouse
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        self.angle = math.atan2(mouse_pos.y - self.pos.y, mouse_pos.x - self.pos.x)
        # Wrap player position
        if self.pos.x < 0:
            self.pos.x = 800
        elif self.pos.x > 800:
            self.pos.x = 0
        if self.pos.y < 0:
            self.pos.y = 600
        elif self.pos.y > 600:
            self.pos.y = 0
        # Update bullets
        for bullet in self.bullets:
            bullet['pos'] += bullet['dir'] * self.bullet_speed * dt
            # Wrap bullet position
            if bullet['pos'].x < 0:
                bullet['pos'].x = 800
            elif bullet['pos'].x > 800:
                bullet['pos'].x = 0
            if bullet['pos'].y < 0:
                bullet['pos'].y = 600
            elif bullet['pos'].y > 600:
                bullet['pos'].y = 0

    def draw(self, surface):
        # Draw spaceship as rotated rectangle
        rect = pygame.Rect(0, 0, *self.size)
        rect.center = (self.pos.x, self.pos.y)
        ship_surf = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(ship_surf, self.color, (0, 0, *self.size), border_radius=6)
        rotated = pygame.transform.rotate(ship_surf, -math.degrees(self.angle))
        rot_rect = rotated.get_rect(center=(self.pos.x, self.pos.y))
        surface.blit(rotated, rot_rect.topleft)
        # Draw bullets (handled in main for tails)

    def shoot(self, target_pos, rapid=False):
        now = pygame.time.get_ticks()
        cooldown = 0.1 if rapid else self.shoot_cooldown
        if now - self.last_shot_time < cooldown * 1000:
            return
        direction = (target_pos - self.pos)
        if direction.length() > 0:
            direction = direction.normalize()
            if len(self.bullets) >= 20:
                self.bullets.pop(0)
            # Spawn bullet at the front of the ship, in the direction of fire
            bullet_start = self.pos + direction * 28
            self.bullets.append({'pos': bullet_start.copy(), 'dir': direction, 'trail': []})
            self.last_shot_time = now

    def get_forward(self):
        return Vector2(math.cos(self.angle), math.sin(self.angle))

    def get_front_pos(self, dist=40):
        return self.pos + self.get_forward() * dist

    def take_damage(self, amount, shielded=False):
        if shielded:
            return
        now = time.time()
        if now - self.last_hit_time >= self.hit_cooldown:
            self.health -= amount
            if self.health < 0:
                self.health = 0
            self.last_hit_time = now

    def get_powerup_status(self, active_powerups):
        return [ptype for ptype in active_powerups]
