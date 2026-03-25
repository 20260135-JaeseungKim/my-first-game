import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My First Pygame")

# 🎨 색상
WHITE = (255, 255, 255)  # 배경용 진짜 흰색
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

clock = pygame.time.Clock()
running = True

# 폰트 설정
font = pygame.font.SysFont(None, 30)

# 원 위치
x = 400
y = 300

# 기본 속도
speed = 5

# 원 반지름
radius = 50

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 키 입력 상태 가져오기
    keys = pygame.key.get_pressed()

    # Shift 누르면 속도 2배
    current_speed = speed
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        current_speed = speed * 2

    # WASD + 방향키 이동
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        y -= current_speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        y += current_speed
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        x -= current_speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        x += current_speed

    # 화면 제한
    if x < radius:
        x = radius
    if x > 800 - radius:
        x = 800 - radius
    if y < radius:
        y = radius
    if y > 600 - radius:
        y = 600 - radius

    # 🎨 배경 흰색
    screen.fill(WHITE)

    # 🔵 원 그리기
    pygame.draw.circle(screen, BLUE, (x, y), radius)

    # FPS 표시
    fps = int(clock.get_fps())
    fps_text = font.render(f"FPS: {fps}", True, BLACK)
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()