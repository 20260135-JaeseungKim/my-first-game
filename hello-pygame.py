import pygame
import sys
import random
import math

pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("My First Pygame")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

clock = pygame.time.Clock()
running = True

game_state = "start"
font = pygame.font.SysFont(None, 40)
big_font = pygame.font.SysFont(None, 70)

# =========================
# 🔥 초기화 함수
# =========================
def reset_game():
    global x, y, hp, monsters, spawn_timer, spawn_delay
    global dash_timer, cooldown_timer, start_time

    x, y = 300, 300
    hp = 3
    monsters = []
    spawn_timer = 0
    spawn_delay = random.randint(30, 120)

    dash_timer = 0
    cooldown_timer = 0

    start_time = pygame.time.get_ticks()

# =========================
# 🔥 플레이어
# =========================
player_radius = 20

# =========================
# 🔥 대쉬
# =========================
dash_speed = 20
dash_duration = 5
dash_timer = 0
dash_cooldown = 30
cooldown_timer = 0

# =========================
# 🔥 몬스터
# =========================
monster_radius = 10

def spawn_monster(px, py):
    while True:
        mx = random.randint(0, 600)
        my = random.randint(0, 600)
        distance = math.hypot(px - mx, py - my)
        if distance > 200:
            speed = random.uniform(0.5, 5)
            return {"x": mx, "y": my, "speed": speed}

# =========================
# 🔥 버튼
# =========================
start_button = pygame.Rect(250, 280, 100, 50)
restart_button = pygame.Rect(220, 350, 160, 60)

# =========================
# 🔥 메인 루프
# =========================
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 시작 화면
        if game_state == "start":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    reset_game()
                    game_state = "play"

            # 🔥 엔터로 시작
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    reset_game()
                    game_state = "play"

        # 게임오버 화면
        elif game_state == "dead":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    reset_game()
                    game_state = "play"

            # 🔥 엔터로 재시작
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    reset_game()
                    game_state = "play"

    screen.fill(WHITE)

    # =========================
    # 🔥 시작 화면
    # =========================
    if game_state == "start":
        title = big_font.render("My Game", True, BLACK)
        screen.blit(title, (200, 200))

        pygame.draw.rect(screen, GRAY, start_button)
        text = font.render("START", True, BLACK)
        screen.blit(text, (255, 290))

    # =========================
    # 🔥 게임 진행
    # =========================
    elif game_state == "play":
        keys = pygame.key.get_pressed()

        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_RIGHT]:
            dx += 1
        if keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_DOWN]:
            dy += 1

        # 대쉬
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and dash_timer == 0 and cooldown_timer == 0:
            if dx != 0 or dy != 0:
                dash_timer = dash_duration
                cooldown_timer = dash_cooldown

        if dash_timer > 0:
            distance = math.hypot(dx, dy)
            if distance != 0:
                x += (dx / distance) * dash_speed
                y += (dy / distance) * dash_speed
            dash_timer -= 1
        else:
            speed = 5
            x += dx * speed
            y += dy * speed

        if cooldown_timer > 0:
            cooldown_timer -= 1

        # 화면 제한
        x = max(player_radius, min(600 - player_radius, x))
        y = max(player_radius, min(600 - player_radius, y))

        # 몬스터 생성
        spawn_timer += 1
        if spawn_timer > spawn_delay:
            monsters.append(spawn_monster(x, y))
            spawn_timer = 0
            spawn_delay = random.randint(30, 120)

        # 몬스터 이동 및 충돌
        for monster in monsters[:]:
            dx_m = x - monster["x"]
            dy_m = y - monster["y"]
            distance = math.hypot(dx_m, dy_m)

            if distance != 0:
                monster["x"] += (dx_m / distance) * monster["speed"]
                monster["y"] += (dy_m / distance) * monster["speed"]

            if distance < player_radius + monster_radius:
                hp -= 1
                monsters.remove(monster)

                if hp <= 0:
                    end_time = pygame.time.get_ticks()
                    survival_time = (end_time - start_time) / 1000
                    game_state = "dead"

        # 그리기
        pygame.draw.circle(screen, BLUE, (int(x), int(y)), player_radius)

        for monster in monsters:
            pygame.draw.circle(screen, RED, (int(monster["x"]), int(monster["y"])), monster_radius)

        # 시간 표시
        current_time = (pygame.time.get_ticks() - start_time) / 1000
        time_text = font.render(f"Time: {int(current_time)}", True, BLACK)
        screen.blit(time_text, (10, 40))

        # HP 표시
        hp_text = font.render(f"HP: {hp}", True, BLACK)
        screen.blit(hp_text, (10, 10))

    # =========================
    # 🔥 게임 오버 화면
    # =========================
    elif game_state == "dead":
        dead_text = big_font.render("DEAD", True, RED)
        screen.blit(dead_text, (220, 200))

        time_text = font.render(f"Time: {int(survival_time)} sec", True, BLACK)
        screen.blit(time_text, (200, 270))

        pygame.draw.rect(screen, GRAY, restart_button)
        text = font.render("RESTART", True, BLACK)
        screen.blit(text, (235, 365))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()