import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("My First Pygame")

WHITE = (255, 255, 255)
BLUE = (255, 0, 0)

clock = pygame.time.Clock()
running = True

# 🔥 원의 위치 변수
x = 600
y = 400

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 🔥 키 입력 감지
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        x -= 5
    if keys[pygame.K_RIGHT]:
        x += 5
    if keys[pygame.K_UP]:
        y -= 5
    if keys[pygame.K_DOWN]:
        y += 5

    screen.fill(WHITE)

    # 🔥 변경된 좌표로 원 그리기
    pygame.draw.circle(screen, BLUE, (x, y), 50)

    pygame.display.flip()
    clock.tick(60)  # 🔥 부드럽게 움직이게 60FPS

pygame.quit()
sys.exit()