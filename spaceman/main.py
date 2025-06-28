import pygame
from player import Player
from enemy import Enemy
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, MOUSEBUTTONDOWN
import math
import random
import numpy as np
import os


def main():
    pygame.init()
    pygame.mixer.init()
    mixer_info = pygame.mixer.get_init()
    if mixer_info:
        mixer_channels = mixer_info[1]
    else:
        mixer_channels = 1
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('MTC Space Man')
    clock = pygame.time.Clock()

    player = Player()
    enemies = []
    enemy_spawn_timer = 0
    wave = 1
    level = 1
    player_name = "MTC"
    score = 0
    high_score = 0
    powerups = []
    powerup_timer = 0
    paused = False
    game_over = False
    powerup_types = ['rapid', 'shield', 'health']
    active_powerups = {}
    auto_target = False
    auto_target_text = 'OFF'
    rocket_ready = False
    rocket_cooldown = 3
    quitting = False

    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 20)

    # --- Cyberpunk space background setup ---
    # Multi-layer parallax stars
    star_layers = [
        [
            {'pos': [random.randint(0, 800), random.randint(0, 600)], 'speed': random.uniform(10 + 30*i, 30 + 60*i), 'color': (random.randint(100,255), random.randint(100,255), 255)}
            for _ in range(30 + 20*i)
        ] for i in range(3)
    ]
    # Animated gradient (vertical and horizontal)
    gradient_surface = pygame.Surface((800, 600))
    gradient_offset = 0
    # Neon moving shapes (add velocity for movement)
    neon_circles = [
        {
            'center': [random.randint(0, 800), random.randint(0, 600)],
            'radius': random.randint(40, 120),
            'color': (0, random.randint(100,255), 255, 128),
            'speed': random.uniform(10, 30),
            'vel': [random.uniform(-30, 30), random.uniform(-30, 30)],
            'angle': random.uniform(0, 2*math.pi),
            'gradient_phase': random.uniform(0, 2*math.pi)
        }
        for _ in range(4)
    ]
    # Neon lines (REMOVED VERTICAL LINES)
    # neon_lines = [
    #     {'x': random.randint(0, 800), 'color': (0, random.randint(100,255), 255, 80), 'width': random.randint(2, 5)}
    #     for _ in range(10)
    # ]

    # --- Music and SFX ---
    pygame.mixer.music.load('spaceman/assets/music/bgm.mp3')
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
    
    sfx_enabled = True
    music_enabled = True
    sfx_volume = 0.5
    music_volume = 0.2
    # --- Achievements ---
    achievements = {'score_1000': False, 'wave_10': False, 'powerup_10': False}
    achievement_texts = {'score_1000': 'Score 1000!', 'wave_10': 'Reach Wave 10!', 'powerup_10': 'Collect 10 Powerups!'}
    powerups_collected = 0
    # --- Start screen ---
    show_start = True
    start_anim = 0

    # --- Sound effects ---
    # (Removed for simplicity)

    # --- Load images ---
    try:
        spaceship_img = pygame.image.load('spaceman/assets/img/spaceship.png').convert_alpha()
    except:
        spaceship_img = None
    try:
        enemy_img = pygame.image.load('spaceman/assets/img/enemy.png').convert_alpha()
    except:
        enemy_img = None
    try:
        bullet_img = pygame.image.load('spaceman/assets/img/bullet.png').convert_alpha()
    except:
        bullet_img = None
    bg_imgs = []
    for i in range(1, 6):
        try:
            bg_imgs.append(pygame.image.load(f'spaceman/assets/img/bg{i}.jpg').convert())
        except:
            pass

    camera_offset = [0, 0]
    camera_shake = 0
    camera_shake_timer = 0
    camera_shake_decay = 0.92
    camera_env_phase = 0

    running = True
    while running and not quitting:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == QUIT:
                quitting = True
            if event.type == KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if paused or show_start or game_over:
                        quitting = True
                    else:
                        paused = True
                if show_start and event.key == pygame.K_SPACE:
                    show_start = False
                if not show_start and event.key == pygame.K_t:
                    auto_target = not auto_target
                    auto_target_text = 'ON' if auto_target else 'OFF'
                if event.key == pygame.K_r and game_over:
                    # Restart
                    player = Player()
                    enemies = []
                    enemy_spawn_timer = 0
                    wave = 1
                    level = 1
                    score = 0
                    powerups = []
                    powerup_timer = 0
                    active_powerups = {}
                    game_over = False
                if (paused or game_over) and event.key == pygame.K_q:
                    quitting = True
                if paused and not show_start:
                    if event.key == pygame.K_m:
                        music_enabled = not music_enabled
                        if music_enabled:
                            pygame.mixer.music.set_volume(music_volume)
                        else:
                            pygame.mixer.music.set_volume(0)
                    if event.key == pygame.K_s:
                        sfx_enabled = not sfx_enabled
                    if event.key == pygame.K_UP:
                        music_volume = min(1.0, music_volume + 0.1)
                        pygame.mixer.music.set_volume(music_volume if music_enabled else 0)
                    if event.key == pygame.K_DOWN:
                        music_volume = max(0.0, music_volume - 0.1)
                        pygame.mixer.music.set_volume(music_volume if music_enabled else 0)
        mouse_held = pygame.mouse.get_pressed()[0]
        keys = pygame.key.get_pressed()
        if not paused and not game_over and not show_start:
            if (mouse_held or (auto_target and keys[pygame.K_SPACE])):
                if auto_target and enemies:
                    closest = min(enemies, key=lambda e: (e.pos - player.pos).length())
                    player.shoot(closest.pos, rapid='rapid' in active_powerups)
                elif mouse_held:
                    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                    player.shoot(mouse_pos, rapid='rapid' in active_powerups)
            # Rocket fire
            if rocket_ready and keys[pygame.K_SPACE]:
                if enemies:
                    target = min(enemies, key=lambda e: (e.pos - player.pos).length())
                    for enemy in enemies[:]:
                        if (enemy.pos - target.pos).length() < 80:
                            enemy.take_damage(200)
                    rocket_ready = False
                    rocket_cooldown = pygame.time.get_ticks()
        # Power-up spawn
        powerup_timer += dt
        if powerup_timer > 8:
            powerup_timer = 0
            if len(powerups) < 2:
                ptype = random.choices(['rapid', 'shield', 'health', 'rocket'], weights=[4,3,3,1])[0]
                pos = pygame.Vector2(random.randint(40, 760), random.randint(40, 560))
                powerups.append({'type': ptype, 'pos': pos, 'timer': 0})
        # Power-up collection
        for p in powerups[:]:
            if (player.pos - p['pos']).length() < 30:
                active_powerups[p['type']] = pygame.time.get_ticks()
                if p['type'] == 'health':
                    player.health = min(player.health + 30, 100)
                if p['type'] == 'rocket':
                    rocket_ready = True
                if p['type'] == 'rapid':
                    camera_shake = 30  # Trigger camera shake on boost
                powerups_collected += 1
                powerups.remove(p)
                # Glow at bullet head
                if 'flash_timer' not in locals():
                    flash_timer = 0
                flash_timer = 1.0
        # Rocket cooldown
        if not rocket_ready and rocket_cooldown and pygame.time.get_ticks() - rocket_cooldown > 8000:
            rocket_ready = True
            rocket_cooldown = 0
        # Power-up effects
        now = pygame.time.get_ticks()
        if 'rapid' in active_powerups and now - active_powerups['rapid'] > 5000:
            del active_powerups['rapid']
        if 'shield' in active_powerups and now - active_powerups['shield'] > 5000:
            del active_powerups['shield']
        # Spawn enemy every 2 seconds, increase wave every 10 enemies killed
        enemy_spawn_timer += dt
        if enemy_spawn_timer >= 2:
            enemies.append(Enemy())
            enemy_spawn_timer = 0
        # Wave/level logic (simple: every 10 kills, next wave)
        if len(enemies) == 0:
            wave += 1
            for _ in range(wave * 3):
                enemies.append(Enemy())
            if wave % 5 == 0:
                level += 1
        # Update
        player.update(dt)
        for enemy in enemies[:]:
            new_enemies = enemy.update(dt, player.pos)
            enemy.check_attack(player)
            if enemy.dead:
                # Score by enemy type
                if enemy.stage == 0:
                    score += 100
                elif enemy.stage == 1:
                    score += 200
                else:
                    score += 300
                enemies.remove(enemy)
                enemies.extend(new_enemies)
        # Bullet-enemy collision
        for bullet in player.bullets[:]:
            for enemy in enemies[:]:
                if (bullet['pos'] - enemy.pos).length() < enemy.radius:
                    enemy.take_damage(40)
                    if bullet in player.bullets:
                        player.bullets.remove(bullet)
                    break
        # Update bullet trails and remove old bullets
        for bullet in player.bullets[:]:
            bullet['trail'].append(bullet['pos'].copy())
            if len(bullet['trail']) < 2:
                bullet['trail'].insert(0, bullet['pos'].copy() - bullet['dir'] * 10)
            if 'spawn_time' not in bullet:
                bullet['spawn_time'] = pygame.time.get_ticks()
            if pygame.time.get_ticks() - bullet['spawn_time'] > 2000:
                player.bullets.remove(bullet)
                continue
            if len(bullet['trail']) > 10:
                bullet['trail'].pop(0)
            for i in range(len(bullet['trail'])-1, 0, -1):
                alpha = int(120 * (i / len(bullet['trail']))**1.2)
                color = (255, 255, 120, alpha)
                pygame.draw.line(screen, color, bullet['trail'][i], bullet['trail'][i-1], 7)
            # Always draw a solid, bright bullet on top
            pygame.draw.circle(screen, (255,255,80), (int(bullet['pos'].x), int(bullet['pos'].y)), 8)
            pygame.draw.circle(screen, (255,255,255), (int(bullet['pos'].x), int(bullet['pos'].y)), 4)
            if bullet_img:
                rect = bullet_img.get_rect(center=(int(bullet['pos'].x), int(bullet['pos'].y)))
                screen.blit(bullet_img, rect.topleft)
            else:
                for g in range(4, 0, -1):
                    alpha = int(40 * g)
                    pygame.draw.circle(screen, (255,255,180,alpha), (int(bullet['pos'].x), int(bullet['pos'].y)), 6+g*2)
                pygame.draw.circle(screen, (255,255,180), (int(bullet['pos'].x), int(bullet['pos'].y)), 3)
        # Camera shake effect
        if camera_shake > 0.1:
            camera_shake *= camera_shake_decay
            camera_shake_timer += dt
            angle = random.uniform(0, 2*math.pi)
            mag = camera_shake * random.uniform(0.5, 1.0)
            camera_offset[0] = int(math.cos(angle) * mag)
            camera_offset[1] = int(math.sin(angle) * mag)
        else:
            camera_shake = 0
            camera_offset = [0, 0]
        # Subtle camera movement for lively environment
        camera_env_phase += dt * 0.5
        camera_offset[0] += int(8 * math.sin(camera_env_phase))
        camera_offset[1] += int(6 * math.cos(camera_env_phase * 0.7))
        # Draw background image for current wave if available
        if bg_imgs:
            bg_idx = min((wave-1)//2, len(bg_imgs)-1)
            screen.blit(bg_imgs[bg_idx], (camera_offset[0], camera_offset[1]))
        else:
            gradient_offset = (gradient_offset + 20 * dt) % 600
            for y in range(600):
                color = (
                    int(20 + 80 * ((y + gradient_offset) % 600) / 600),
                    int(10 + 40 * ((y + gradient_offset) % 600) / 600),
                    int(60 + 180 * ((y + gradient_offset) % 600) / 600)
                )
                pygame.draw.line(gradient_surface, color, (0, y), (800, y))
            screen.blit(gradient_surface, (camera_offset[0], camera_offset[1]))
        # Parallax stars
        for i, layer in enumerate(star_layers):
            for star in layer:
                star['pos'][1] += star['speed'] * dt * (0.5 + 0.5*i)
                if star['pos'][1] > 600:
                    star['pos'][0] = random.randint(0, 800)
                    star['pos'][1] = 0
                pygame.draw.circle(screen, star['color'], (int(star['pos'][0] + camera_offset[0]*0.2), int(star['pos'][1] + camera_offset[1]*0.2)), 2 + i)
        # Neon moving circles (live moving gradient)
        for circle in neon_circles:
            # Move
            circle['center'][0] += circle['vel'][0] * dt
            circle['center'][1] += circle['vel'][1] * dt
            # Bounce off edges
            if circle['center'][0] < circle['radius']:
                circle['center'][0] = circle['radius']
                circle['vel'][0] *= -1
            elif circle['center'][0] > 800 - circle['radius']:
                circle['center'][0] = 800 - circle['radius']
                circle['vel'][0] *= -1
            if circle['center'][1] < circle['radius']:
                circle['center'][1] = circle['radius']
                circle['vel'][1] *= -1
            elif circle['center'][1] > 600 - circle['radius']:
                circle['center'][1] = 600 - circle['radius']
                circle['vel'][1] *= -1
            # Animate gradient phase
            circle['gradient_phase'] += dt * 0.7
            grad_surf = pygame.Surface((circle['radius']*2, circle['radius']*2), pygame.SRCALPHA)
            for r in range(circle['radius'], 0, -1):
                phase = circle['gradient_phase'] + r * 0.08
                color = (
                    int(40 + 80 * (0.5 + 0.5 * math.sin(phase))),
                    int(100 + 120 * (0.5 + 0.5 * math.cos(phase + 1))),
                    255,
                    int(128 * (r / circle['radius']))
                )
                pygame.draw.circle(grad_surf, color, (circle['radius'], circle['radius']), r)
            screen.blit(grad_surf, (int(circle['center'][0] - circle['radius'] + camera_offset[0]), int(circle['center'][1] - circle['radius'] + camera_offset[1])))
        # Neon lines (REMOVED)
        # for line in neon_lines:
        #     pygame.draw.line(screen, line['color'], (line['x'], 0), (line['x'], 600), line['width'])
        # Draw power-ups (no glow)
        for p in powerups:
            color = (0,255,255) if p['type']=='rapid' else (255,255,0) if p['type']=='shield' else (0,255,0) if p['type']=='health' else (255,80,80)
            pygame.draw.circle(screen, color, (int(p['pos'].x), int(p['pos'].y)), 18)
            pygame.draw.circle(screen, (255,255,255), (int(p['pos'].x), int(p['pos'].y)), 18, 2)
            icon = small_font.render(p['type'][0].upper(), True, (0,0,0))
            screen.blit(icon, (int(p['pos'].x)-6, int(p['pos'].y)-10))
        # Draw player (spaceship) as image if available
        if spaceship_img:
            rotated = pygame.transform.rotate(spaceship_img, -math.degrees(player.angle))
            rect = rotated.get_rect(center=(player.pos.x, player.pos.y))
            screen.blit(rotated, rect.topleft)
        else:
            player.draw(screen)
        # Draw thruster flame effect (opposite of movement direction)
        if player.velocity.length() > 10:
            v = player.velocity.normalize()
            base_angle = math.atan2(-v.y, -v.x)  # Opposite of movement
            for f in range(3):
                flame_len = 18 + random.randint(-2,2)
                flame_angle = base_angle + random.uniform(-0.18,0.18)
                fx = player.pos.x + math.cos(flame_angle) * (player.radius + 18 + f*2)
                fy = player.pos.y + math.sin(flame_angle) * (player.radius + 8 + f*2)
                flame_color = (255, 180, 60, 180 - f*40)
                pygame.draw.polygon(screen, flame_color, [
                    (fx, fy),
                    (fx + math.cos(flame_angle+0.25)*6, fy + math.sin(flame_angle+0.25)*6),
                    (fx + math.cos(flame_angle-0.25)*6, fy + math.sin(flame_angle-0.25)*6)
                ])
        # Draw enemies as images if available
        for enemy in enemies:
            if enemy_img:
                rect = enemy_img.get_rect(center=(enemy.pos.x, enemy.pos.y))
                screen.blit(enemy_img, rect.topleft)
                # Draw healthbar/circle inside PNG bounds
                bar_width = rect.width * 0.7
                bar_height = 6
                health_ratio = max(enemy.health, 0) / (80 if enemy.stage == 0 else 40)
                bar_x = int(enemy.pos.x - bar_width // 2)
                bar_y = int(enemy.pos.y + rect.height//2 - 18)
                pygame.draw.rect(screen, (60,60,60), (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(screen, (0,200,0), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
            else:
                enemy.draw(screen)
                # Draw healthbar as before
                bar_width = 40
                bar_height = 6
                health_ratio = max(enemy.health, 0) / (80 if enemy.stage == 0 else 40)
                bar_x = int(enemy.pos.x - bar_width // 2)
                bar_y = int(enemy.pos.y - enemy.radius - 12)
                pygame.draw.rect(screen, (60,60,60), (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(screen, (0,200,0), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
        # Enjoyable polish: screen flash on powerup, enemy hit effect, player engine glow
        # (Screen flash)
        if 'flash_timer' not in locals():
            flash_timer = 0
        if flash_timer > 0:
            flash_surf = pygame.Surface((800,600), pygame.SRCALPHA)
            flash_surf.fill((255,255,255,int(120*flash_timer)))
            screen.blit(flash_surf, (0,0))
            flash_timer -= dt * 2
        # On powerup collection, trigger flash
        for p in powerups[:]:
            if (player.pos - p['pos']).length() < 30:
                flash_timer = 1.0
        # Enemy hit effect (draw red overlay on hit)
        for enemy in enemies:
            if hasattr(enemy, 'hit_timer') and enemy.hit_timer > 0:
                hit_surf = pygame.Surface((40,40), pygame.SRCALPHA)
                pygame.draw.circle(hit_surf, (255,0,0,int(120*enemy.hit_timer)), (20,20), 20)
                screen.blit(hit_surf, (int(enemy.pos.x-20), int(enemy.pos.y-20)))
                enemy.hit_timer -= dt * 2
        # Subtle player engine glow
        engine_glow = pygame.Surface((60, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(engine_glow, (0,255,255,80), (0, 10, 60, 10))
        engine_rect = engine_glow.get_rect(center=(int(player.pos.x - 20*math.cos(player.angle)), int(player.pos.y - 10*math.sin(player.angle))))
        screen.blit(engine_glow, engine_rect.topleft)
        # --- Draw bullets ON TOP of everything else ---
        for bullet in player.bullets[:]:
            for i in range(len(bullet['trail'])-1, 0, -1):
                alpha = int(120 * (i / len(bullet['trail']))**1.2)
                color = (255, 255, 120, alpha)
                pygame.draw.line(screen, color, bullet['trail'][i], bullet['trail'][i-1], 7)
            pygame.draw.circle(screen, (255,255,80), (int(bullet['pos'].x), int(bullet['pos'].y)), 8)
            pygame.draw.circle(screen, (255,255,255), (int(bullet['pos'].x), int(bullet['pos'].y)), 4)
            if bullet_img:
                rect = bullet_img.get_rect(center=(int(bullet['pos'].x), int(bullet['pos'].y)))
                screen.blit(bullet_img, rect.topleft)
        # --- Start screen ---
        if show_start:
            start_anim += dt
            screen.fill((10, 10, 30))
            title_font = pygame.font.SysFont('Orbitron', 80)
            title = title_font.render('CYBER SPACESHIP', True, (0,255,255))
            glow = pygame.Surface((800, 200), pygame.SRCALPHA)
            for i in range(10):
                pygame.draw.rect(glow, (0,255,255,20-i*2), (100-i*8, 60-i*8, 600+i*16, 80+i*16), border_radius=40)
            screen.blit(glow, (0,0))
            screen.blit(title, (120, 80))
            press_text = font.render('Press SPACE to Start', True, (255,255,255))
            screen.blit(press_text, (250, 300 + int(10*math.sin(start_anim*2))))
            menu_text = small_font.render('T: Toggle Auto-Target  ESC/Q: Quit  SPACE: Start', True, (0,255,255))
            screen.blit(menu_text, (180, 400))
            pygame.display.flip()
            continue
        # --- Pause menu ---
        if paused:
            overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            screen.blit(overlay, (0,0))
            pause_text = font.render('PAUSED', True, (255,255,255))
            screen.blit(pause_text, (320, 250))
            info_text = small_font.render('ESC/Q: Quit  T: Toggle Auto-Target  M: Music  S: SFX  UP/DOWN: Volume', True, (200,200,200))
            screen.blit(info_text, (80, 300))
            pygame.display.flip()
            continue
        # --- Game Over screen polish ---
        if game_over:
            overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            screen.blit(overlay, (0,0))
            over_text = font.render('GAME OVER', True, (255,80,80))
            screen.blit(over_text, (300, 200))
            score_text = font.render(f'Score: {score}', True, (255,255,255))
            screen.blit(score_text, (320, 260))
            high_text = font.render(f'High Score: {high_score}', True, (255,255,0))
            screen.blit(high_text, (320, 300))
            y = 350
            for key, unlocked in achievements.items():
                if unlocked:
                    ach_text = small_font.render(f'Achievement: {achievement_texts[key]}', True, (0,255,255))
                    screen.blit(ach_text, (250, y))
                    y += 30
            info_text = small_font.render('R: Restart  ESC/Q: Quit', True, (200,200,200))
            screen.blit(info_text, (320, y+20))
            pygame.display.flip()
            continue
        # --- Achievements check ---
        if score >= 1000:
            achievements['score_1000'] = True
        if wave >= 10:
            achievements['wave_10'] = True
        if powerups_collected >= 10:
            achievements['powerup_10'] = True
        # --- Draw HUD (stylish panel, icons, larger fonts) ---
        hud_bg = pygame.Surface((800, 60), pygame.SRCALPHA)
        hud_bg.fill((20, 20, 40, 220))
        screen.blit(hud_bg, (0, 0))
        health_icon = pygame.Surface((32,32), pygame.SRCALPHA)
        pygame.draw.circle(health_icon, (0,255,0), (16,16), 16)
        screen.blit(health_icon, (10, 10))
        health_text = font.render(f'{player.health}', True, (255,255,255))
        screen.blit(health_text, (50, 15))
        # Bonuses (power-ups and rocket)
        bonus_x = 120
        for ptype in active_powerups:
            icon = small_font.render(ptype[0].upper(), True, (255,255,0))
            screen.blit(icon, (bonus_x, 15))
            bonus_x += 30
        if rocket_ready:
            rocket_icon = small_font.render('R', True, (255,255,0))
            screen.blit(rocket_icon, (bonus_x, 15))
            bonus_x += 30
        enemy_text = font.render(f'Enemies: {len(enemies)}', True, (255,255,255))
        screen.blit(enemy_text, (bonus_x, 15))
        wave_text = font.render(f'Wave: {wave}', True, (255,255,255))
        screen.blit(wave_text, (bonus_x+160, 15))
        level_text = font.render(f'Level: {level}', True, (255,255,255))
        screen.blit(level_text, (bonus_x+290, 15))
        name_text = font.render(f'Player: {player_name}', True, (255,255,255))
        screen.blit(name_text, (620, 15))
        score_text = font.render(f'Score: {score}', True, (255,255,0))
        screen.blit(score_text, (10, 35))
        high_text = font.render(f'High: {high_score}', True, (255,255,0))
        screen.blit(high_text, (180, 35))
        # Auto-target status
        auto_text = small_font.render(f'Auto-Target: {auto_target_text}', True, (0,255,255))
        screen.blit(auto_text, (620, 35))
        pygame.display.flip()
        # End game if player is dead
        if player.health <= 0:
            game_over = True
            if score > high_score:
                high_score = score
        # Explosion particles for dead enemies
        if 'explosions' not in locals():
            explosions = []
        for enemy in enemies[:]:
            if hasattr(enemy, 'exploding') and enemy.exploding:
                for part in enemy.exploding:
                    part['pos'][0] += part['vel'][0] * dt
                    part['pos'][1] += part['vel'][1] * dt
                    part['life'] -= dt
                    if part['life'] > 0:
                        pygame.draw.circle(screen, part['color'], (int(part['pos'][0]), int(part['pos'][1])), int(part['size']*part['life']))
                enemy.exploding = [p for p in enemy.exploding if p['life'] > 0]
                if not enemy.exploding:
                    enemies.remove(enemy)
        # When enemy dies, spawn explosion
        for enemy in enemies[:]:
            if enemy.dead and not hasattr(enemy, 'exploding'):
                enemy.exploding = []
                for _ in range(18):
                    angle = random.uniform(0, 2*math.pi)
                    speed = random.uniform(80, 200)
                    enemy.exploding.append({
                        'pos': [enemy.pos.x, enemy.pos.y],
                        'vel': [math.cos(angle)*speed, math.sin(angle)*speed],
                        'life': random.uniform(0.4, 0.8),
                        'size': random.uniform(3, 7),
                        'color': random.choice([(255,200,80),(255,80,40),(255,255,255)])
                    })

    pygame.quit()


if __name__ == '__main__':
    main()
