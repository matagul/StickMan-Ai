import pygame
from .player import Player
from .enemy import Enemy
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Stick Man')
    clock = pygame.time.Clock()

    player = Player()
    enemies = []
    enemy_spawn_timer = 0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False

        # Spawn enemy every 2 seconds
        enemy_spawn_timer += dt
        if enemy_spawn_timer >= 2:
            enemies.append(Enemy())
            enemy_spawn_timer = 0

        # Update
        player.update(dt)
        for enemy in enemies[:]:
            enemy.update(dt)
            if enemy.dead:
                enemies.remove(enemy)

        # Draw
        screen.fill((30, 30, 30))
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
