import pygame
import random
import sys

pygame.init()


def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0:
            return font
    return pygame.font.SysFont(None, size)


WIDTH, HEIGHT = 800, 600
FPS = 60

WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
GRAY    = (20,  20,  40)
BLUE    = (50,  150, 255)
RED     = (220, 50,  50)
YELLOW  = (240, 220, 0)
GREEN   = (50,  220, 80)
ORANGE  = (240, 140, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()
font = get_korean_font(36)
font_big = get_korean_font(72)

# --- 레벨 설정 ---
LEVELS = [
    {"enemy_speed": 2, "spawn": 60, "label": "Lv.1"},
    {"enemy_speed": 3, "spawn": 40, "label": "Lv.2"},
    {"enemy_speed": 5, "spawn": 25, "label": "Lv.3"},
]

# --- 사운드 자리 ---
# shoot_sound    = pygame.mixer.Sound("shoot.wav")
# explosion_sound= pygame.mixer.Sound("explosion.wav")
# hit_sound      = pygame.mixer.Sound("hit.wav")

PLAYER_W, PLAYER_H = 40, 40
ENEMY_W,  ENEMY_H  = 36, 36
BULLET_W, BULLET_H = 6,  14

def draw_player(surf, rect):
    cx = rect.centerx
    pygame.draw.polygon(surf, BLUE, [
        (cx, rect.top),
        (rect.left, rect.bottom),
        (cx, rect.bottom - 8),
        (rect.right, rect.bottom),
    ])
    pygame.draw.rect(surf, YELLOW, (cx - 4, rect.bottom - 10, 8, 10))

def draw_enemy(surf, rect):
    cx = rect.centerx
    pygame.draw.polygon(surf, RED, [
        (cx, rect.bottom),
        (rect.left, rect.top),
        (cx, rect.top + 8),
        (rect.right, rect.top),
    ])

def spawn_enemy(level_cfg):
    x = random.randint(0, WIDTH - ENEMY_W)
    return pygame.Rect(x, -ENEMY_H, ENEMY_W, ENEMY_H)

def draw_stars(stars):
    for s in stars:
        pygame.draw.circle(screen, WHITE, (s[0], s[1]), s[2])

def draw_hud(score, lives, level_cfg):
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Lives: {'♥ ' * lives}", True, RED), (WIDTH - 180, 10))
    screen.blit(font.render(level_cfg["label"], True, YELLOW), (WIDTH // 2 - 25, 10))

def game_over_screen(score):
    screen.fill((10, 10, 30))
    screen.blit(font_big.render("GAME OVER", True, RED), (220, 220))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (350, 310))
    screen.blit(font.render("R: Restart   Q: Quit", True, WHITE), (270, 360))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key == pygame.K_q: pygame.quit(); sys.exit()

def main():
    player = pygame.Rect(WIDTH // 2 - PLAYER_W // 2, HEIGHT - 70, PLAYER_W, PLAYER_H)
    bullets  = []
    enemies  = []
    score    = 0
    lives    = 3
    shoot_cd = 0
    spawn_timer = 0
    level_idx = 0
    level_cfg = LEVELS[level_idx]
    invincible = 0

    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 2))
             for _ in range(80)]

    while True:
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  and player.left  > 0:      player.x -= 6
        if keys[pygame.K_RIGHT] and player.right < WIDTH:   player.x += 6
        if keys[pygame.K_UP]    and player.top   > 0:      player.y -= 6
        if keys[pygame.K_DOWN]  and player.bottom < HEIGHT: player.y += 6

        shoot_cd -= 1
        if keys[pygame.K_SPACE] and shoot_cd <= 0:
            # shoot_sound.play()
            b = pygame.Rect(player.centerx - BULLET_W // 2, player.top, BULLET_W, BULLET_H)
            bullets.append(b)
            shoot_cd = 15

        bullets = [b for b in bullets if b.bottom > 0]
        for b in bullets:
            b.y -= 10

        spawn_timer += 1
        if spawn_timer >= level_cfg["spawn"]:
            spawn_timer = 0
            enemies.append(spawn_enemy(level_cfg))

        alive_enemies = []
        for en in enemies:
            en.y += level_cfg["enemy_speed"]
            if en.top < HEIGHT:
                alive_enemies.append(en)
        enemies = alive_enemies

        hit_bullets = set()
        hit_enemies = set()
        for bi, b in enumerate(bullets):
            for ei, en in enumerate(enemies):
                if b.colliderect(en):
                    # explosion_sound.play()
                    hit_bullets.add(bi)
                    hit_enemies.add(ei)
                    score += 10
        bullets  = [b  for i, b  in enumerate(bullets)  if i not in hit_bullets]
        enemies  = [en for i, en in enumerate(enemies)   if i not in hit_enemies]

        level_idx = min(score // 50, len(LEVELS) - 1)
        level_cfg = LEVELS[level_idx]

        if invincible > 0:
            invincible -= 1
        else:
            for en in enemies:
                if player.colliderect(en):
                    # hit_sound.play()
                    lives -= 1
                    invincible = 90
                    enemies.clear()
                    if lives <= 0:
                        if game_over_screen(score):
                            main()
                        return
                    break

        for s in stars:
            s = list(s)

        screen.fill(GRAY)
        draw_stars(stars)

        for b in bullets:
            pygame.draw.rect(screen, YELLOW, b)

        for en in enemies:
            draw_enemy(screen, en)

        blink = (invincible // 10) % 2 == 0
        if blink:
            draw_player(screen, player)

        draw_hud(score, lives, level_cfg)
        pygame.display.flip()

main()