import pygame
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

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
BLUE = (50, 120, 220)
RED = (220, 50, 50)
YELLOW = (240, 200, 0)
ORANGE = (240, 140, 0)
GREEN = (50, 200, 50)

BLOCK_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout")
clock = pygame.time.Clock()
font = get_korean_font(36)
font_big = get_korean_font(72)

# --- 레벨 설정 ---
LEVELS = [
    {"rows": 3, "ball_speed": 5, "label": "Lv.1"},
    {"rows": 5, "ball_speed": 6, "label": "Lv.2"},
    {"rows": 7, "ball_speed": 8, "label": "Lv.3"},
]

# --- 사운드 자리 ---
# hit_block_sound  = pygame.mixer.Sound("hit_block.wav")
# hit_wall_sound   = pygame.mixer.Sound("hit_wall.wav")
# miss_sound       = pygame.mixer.Sound("miss.wav")
# clear_sound      = pygame.mixer.Sound("clear.wav")

PAD_W, PAD_H = 100, 12
BALL_R = 8
BLOCK_W, BLOCK_H = 72, 22
BLOCK_COLS = 10
BLOCK_MARGIN = 5
BLOCK_TOP = 60


def make_blocks(rows):
    blocks = []
    for r in range(rows):
        for c in range(BLOCK_COLS):
            x = BLOCK_MARGIN + c * (BLOCK_W + BLOCK_MARGIN)
            y = BLOCK_TOP + r * (BLOCK_H + BLOCK_MARGIN)
            color = BLOCK_COLORS[r % len(BLOCK_COLORS)]
            blocks.append(
                {"rect": pygame.Rect(x, y, BLOCK_W, BLOCK_H), "color": color, "hp": 1}
            )
    return blocks


def draw_hud(score, lives, level_cfg):
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Lives: {'♥ ' * lives}", True, RED), (WIDTH - 180, 10))
    screen.blit(font.render(level_cfg["label"], True, YELLOW), (WIDTH // 2 - 25, 10))


def message_screen(title, color, score):
    screen.fill(GRAY)
    screen.blit(font_big.render(title, True, color), (WIDTH // 2 - 180, 220))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (350, 310))
    screen.blit(font.render("R: Restart   Q: Quit", True, WHITE), (270, 360))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return True
                if e.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


def main():
    level_idx = 0
    level_cfg = LEVELS[level_idx]

    pad = pygame.Rect(WIDTH // 2 - PAD_W // 2, HEIGHT - 40, PAD_W, PAD_H)
    ball = pygame.Rect(WIDTH // 2 - BALL_R, HEIGHT // 2, BALL_R * 2, BALL_R * 2)
    bx, by = level_cfg["ball_speed"], -level_cfg["ball_speed"]
    blocks = make_blocks(level_cfg["rows"])
    score = 0
    lives = 3
    launched = False

    while True:
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                launched = True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and pad.left > 0:
            pad.x -= 7
        if keys[pygame.K_RIGHT] and pad.right < WIDTH:
            pad.x += 7

        if not launched:
            ball.centerx = pad.centerx
            screen.fill(GRAY)
            for b in blocks:
                pygame.draw.rect(screen, b["color"], b["rect"])
            pygame.draw.rect(screen, WHITE, pad)
            pygame.draw.ellipse(screen, WHITE, ball)
            draw_hud(score, lives, level_cfg)
            text_surf = font.render("SPACE to launch", True, YELLOW)
            screen.blit(
                text_surf, (WIDTH // 2 - text_surf.get_width() // 2, HEIGHT // 2 + 40)
            )
            pygame.display.flip()
            continue

        ball.x += bx
        ball.y += by

        if ball.left <= 0 or ball.right >= WIDTH:
            # hit_wall_sound.play()
            bx = -bx
        if ball.top <= 0:
            # hit_wall_sound.play()
            by = -by

        if ball.colliderect(pad) and by > 0:
            # hit_wall_sound.play()
            offset = (ball.centerx - pad.centerx) / (PAD_W / 2)
            bx = int(offset * level_cfg["ball_speed"]) or bx
            by = -abs(by)

        hit_block = None
        for b in blocks:
            if ball.colliderect(b["rect"]):
                hit_block = b
                break
        if hit_block:
            # hit_block_sound.play()
            hit_block["hp"] -= 1
            if hit_block["hp"] <= 0:
                blocks.remove(hit_block)
                score += 10
            by = -by

        if ball.bottom >= HEIGHT:
            # miss_sound.play()
            lives -= 1
            launched = False
            ball.center = (WIDTH // 2, HEIGHT // 2)
            if lives <= 0:
                if message_screen("GAME OVER", RED, score):
                    main()
                return

        if not blocks:
            # clear_sound.play()
            level_idx += 1
            if level_idx >= len(LEVELS):
                if message_screen("CLEAR!", YELLOW, score):
                    main()
                return
            level_cfg = LEVELS[level_idx]
            blocks = make_blocks(level_cfg["rows"])
            launched = False
            ball.center = (WIDTH // 2, HEIGHT // 2)
            bx, by = level_cfg["ball_speed"], -level_cfg["ball_speed"]

        screen.fill(GRAY)
        for b in blocks:
            pygame.draw.rect(screen, b["color"], b["rect"])
        pygame.draw.rect(screen, WHITE, pad)
        pygame.draw.ellipse(screen, WHITE, ball)
        draw_hud(score, lives, level_cfg)
        pygame.display.flip()


main()