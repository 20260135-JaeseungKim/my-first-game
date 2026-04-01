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
CELL = 20
FPS = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
DARK = (30, 150, 30)
RED = (220, 50, 50)
GRAY = (40, 40, 40)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()
font = get_korean_font(36)
font_big = get_korean_font(72)

# --- 레벨 설정 ---
LEVELS = {
    1: {"speed": 8, "label": "Easy"},
    2: {"speed": 12, "label": "Normal"},
    3: {"speed": 18, "label": "Hard"},
}
level = 1

# --- 사운드 자리 ---
# eat_sound = pygame.mixer.Sound("eat.wav")
# die_sound = pygame.mixer.Sound("die.wav")


def new_food(snake):
    while True:
        pos = (
            random.randrange(0, WIDTH // CELL) * CELL,
            random.randrange(0, HEIGHT // CELL) * CELL,
        )
        if pos not in snake:
            return pos


def draw_grid():
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, (20, 20, 20), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, (20, 20, 20), (0, y), (WIDTH, y))


def draw_snake(snake):
    for i, seg in enumerate(snake):
        color = DARK if i == 0 else GREEN
        pygame.draw.rect(screen, color, (*seg, CELL, CELL))
        pygame.draw.rect(screen, BLACK, (*seg, CELL, CELL), 1)


def draw_hud(score, level):
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Level: {LEVELS[level]['label']}", True, WHITE), (10, 40))


def game_over_screen(score):
    screen.fill(GRAY)
    screen.blit(font_big.render("GAME OVER", True, RED), (220, 220))
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


def level_select_screen():
    screen.fill(GRAY)
    screen.blit(font_big.render("SNAKE", True, GREEN), (310, 160))
    for lv, info in LEVELS.items():
        screen.blit(
            font.render(f"{lv}: {info['label']}", True, WHITE), (340, 250 + lv * 40)
        )
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    return int(e.unicode)


def main():
    global level
    level = level_select_screen()

    snake = [(WIDTH // 2, HEIGHT // 2)]
    direction = (CELL, 0)
    food = new_food(snake)
    score = 0
    speed = LEVELS[level]["speed"]

    while True:
        clock.tick(speed)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP and direction != (0, CELL):
                    direction = (0, -CELL)
                if e.key == pygame.K_DOWN and direction != (0, -CELL):
                    direction = (0, CELL)
                if e.key == pygame.K_LEFT and direction != (CELL, 0):
                    direction = (-CELL, 0)
                if e.key == pygame.K_RIGHT and direction != (-CELL, 0):
                    direction = (CELL, 0)

        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        if (
            head[0] < 0
            or head[0] >= WIDTH
            or head[1] < 0
            or head[1] >= HEIGHT
            or head in snake
        ):
            # die_sound.play()
            if game_over_screen(score):
                main()
            return

        snake.insert(0, head)

        if head == food:
            # eat_sound.play()
            score += 10
            food = new_food(snake)
            if score % 50 == 0 and level < 3:
                level = min(level + 1, 3)
                speed = LEVELS[level]["speed"]
        else:
            snake.pop()

        screen.fill(GRAY)
        draw_grid()
        pygame.draw.rect(screen, RED, (*food, CELL, CELL))
        draw_snake(snake)
        draw_hud(score, level)
        pygame.display.flip()


main()